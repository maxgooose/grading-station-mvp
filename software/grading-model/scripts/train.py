"""
POC: binary grade classifier (B vs C) on same-device photos.

Surgical recipe: partial-unfreeze EfficientNet-B0 (last 2 MBConv blocks),
differential LR AdamW, class-weighted CE biased toward B, stronger aug
including RandomErasing, save best on val_loss, fit temperature + threshold
at end of training to support calibrated OR-aggregated inference downstream.
"""

import os
import sys
import json
import time
import ssl
from pathlib import Path
from datetime import datetime

sys.stdout.reconfigure(line_buffering=True)

import certifi
os.environ.setdefault("SSL_CERT_FILE", certifi.where())
ssl._create_default_https_context = ssl.create_default_context

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms
from torchvision.models import efficientnet_b0, EfficientNet_B0_Weights
from PIL import Image
import pillow_heif
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, classification_report
import matplotlib.pyplot as plt
import numpy as np

pillow_heif.register_heif_opener()

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
CACHE_DIR = DATA_DIR / ".cache"
RUNS_DIR = ROOT / "runs"
CACHE_SIZE = 512

CLASSES = ["B", "C"]
IMG_SIZE = 224
BATCH_SIZE = 16
EPOCHS = 40
PATIENCE = 8
LR_HEAD = 1e-3
LR_BACKBONE = 1e-4
WD_HEAD = 1e-4
WD_BACKBONE = 1e-5
UNFREEZE_BLOCKS = 2
SEED = 42
VAL_FRAC = 0.2

CLASS_WEIGHTS = [1.3, 0.7]
LABEL_SMOOTHING = 0.05

TARGET_C_PRECISION = 0.95
FALLBACK_MIN_C_RECALL = 0.50
FALLBACK_THRESHOLD = 0.80

DEVICE = torch.device("mps" if torch.backends.mps.is_available() else "cpu")


class GradingDataset(Dataset):
    def __init__(self, samples, transform):
        self.samples = samples
        self.transform = transform

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, i):
        path, label = self.samples[i]
        img = Image.open(path).convert("RGB")
        return self.transform(img), label


IMG_EXTS = {".heic", ".heif", ".jpg", ".jpeg", ".png"}


def build_cache_if_needed():
    needs_build = False
    for cls in CLASSES:
        src = DATA_DIR / cls
        dst = CACHE_DIR / cls
        src_files = [p for p in sorted(src.iterdir()) if p.suffix.lower() in IMG_EXTS]
        if not dst.exists():
            needs_build = True
            break
        dst_files = list(dst.glob("*.jpg"))
        if len(dst_files) != len(src_files):
            needs_build = True
            break
    if not needs_build:
        print(f"[cache] already built at {CACHE_DIR}")
        return
    print(f"[cache] building at {CACHE_DIR} (resize to {CACHE_SIZE}px, JPEG q=95)")
    for cls in CLASSES:
        src = DATA_DIR / cls
        dst = CACHE_DIR / cls
        dst.mkdir(parents=True, exist_ok=True)
        src_files = [p for p in sorted(src.iterdir()) if p.suffix.lower() in IMG_EXTS]
        t0 = time.time()
        for i, p in enumerate(src_files, 1):
            out = dst / (p.stem + ".jpg")
            if out.exists():
                continue
            img = Image.open(p).convert("RGB")
            w, h = img.size
            scale = CACHE_SIZE / min(w, h)
            img = img.resize((int(round(w * scale)), int(round(h * scale))), Image.LANCZOS)
            img.save(out, "JPEG", quality=95)
            if i % 25 == 0 or i == len(src_files):
                print(f"  {cls}: {i}/{len(src_files)}  ({time.time() - t0:.1f}s)")
    print("[cache] done")


def collect_samples():
    samples = []
    for label_idx, cls in enumerate(CLASSES):
        cls_dir = CACHE_DIR / cls
        for p in sorted(cls_dir.glob("*.jpg")):
            samples.append((p, label_idx))
    return samples


def build_model(unfreeze_blocks: int = UNFREEZE_BLOCKS):
    weights = EfficientNet_B0_Weights.IMAGENET1K_V1
    model = efficientnet_b0(weights=weights)

    # Freeze everything first.
    for p in model.parameters():
        p.requires_grad = False

    # EfficientNet-B0 features: 9 stages (0..8). Unfreeze the last `unfreeze_blocks` + the final Conv+BN (index 8).
    n_stages = len(model.features)
    start = max(1, n_stages - unfreeze_blocks - 1)  # keep early stages frozen
    for i in range(start, n_stages):
        for p in model.features[i].parameters():
            p.requires_grad = True

    # Replace the classification head with a fresh 2-class Linear (auto requires_grad=True).
    in_features = model.classifier[1].in_features
    model.classifier = nn.Sequential(
        nn.Dropout(p=0.3, inplace=True),
        nn.Linear(in_features, len(CLASSES)),
    )

    return model, start


def freeze_bn_stats(model: nn.Module):
    """Keep BatchNorm layers in eval mode so running stats don't drift on small batches,
    while still allowing their learned affine weights to update."""
    for m in model.modules():
        if isinstance(m, nn.BatchNorm2d):
            m.eval()


def build_optimizer(model: nn.Module):
    head_params = []
    backbone_params = []
    for name, p in model.named_parameters():
        if not p.requires_grad:
            continue
        if name.startswith("classifier"):
            head_params.append(p)
        else:
            backbone_params.append(p)
    param_groups = [
        {"params": head_params, "lr": LR_HEAD, "weight_decay": WD_HEAD},
    ]
    if backbone_params:
        param_groups.append(
            {"params": backbone_params, "lr": LR_BACKBONE, "weight_decay": WD_BACKBONE}
        )
    optimizer = torch.optim.AdamW(param_groups)
    return optimizer, len(head_params), len(backbone_params)


def run_epoch(model, loader, criterion, optimizer, train, collect_logits=False):
    if train:
        model.train()
        freeze_bn_stats(model)  # critical for small-batch fine-tuning
    else:
        model.eval()

    total_loss, correct, total = 0.0, 0, 0
    all_preds, all_labels, all_logits = [], [], []
    ctx = torch.enable_grad() if train else torch.no_grad()
    with ctx:
        for imgs, labels in loader:
            imgs, labels = imgs.to(DEVICE), labels.to(DEVICE)
            logits = model(imgs)
            loss = criterion(logits, labels)
            if train:
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
            total_loss += loss.item() * imgs.size(0)
            preds = logits.argmax(1)
            correct += (preds == labels).sum().item()
            total += imgs.size(0)
            all_preds.extend(preds.cpu().tolist())
            all_labels.extend(labels.cpu().tolist())
            if collect_logits:
                all_logits.append(logits.detach().cpu())
    logits_tensor = torch.cat(all_logits, dim=0) if collect_logits else None
    return total_loss / total, correct / total, all_preds, all_labels, logits_tensor


def fit_temperature(logits: torch.Tensor, labels: torch.Tensor, max_iter: int = 200) -> float:
    """Fit a single scalar temperature T minimizing NLL on (logits/T) vs labels."""
    logits = logits.detach().float()
    labels = labels.long()
    T = torch.nn.Parameter(torch.ones(1) * 1.0)
    optimizer = torch.optim.LBFGS([T], lr=0.1, max_iter=max_iter, line_search_fn="strong_wolfe")
    nll = nn.CrossEntropyLoss()

    def closure():
        optimizer.zero_grad()
        loss = nll(logits / T.clamp(min=1e-3), labels)
        loss.backward()
        return loss

    optimizer.step(closure)
    return float(T.detach().clamp(min=1e-3).item())


def threshold_sweep(probs_c: np.ndarray, labels: np.ndarray):
    """Sweep thresholds from 0.05 to 0.99 and compute C-precision, C-recall, B-recall."""
    thresholds = np.arange(0.05, 1.00, 0.01)
    n_true_c = int((labels == 1).sum())
    n_true_b = int((labels == 0).sum())
    rows = []
    for t in thresholds:
        pred_c = probs_c >= t
        tp = int(((labels == 1) & pred_c).sum())
        fp = int(((labels == 0) & pred_c).sum())
        fn = n_true_c - tp
        tn = n_true_b - fp
        c_prec = tp / (tp + fp) if (tp + fp) > 0 else 1.0
        c_rec = tp / n_true_c if n_true_c > 0 else 0.0
        b_rec = tn / n_true_b if n_true_b > 0 else 0.0
        rows.append((float(t), c_prec, c_rec, b_rec, tp, fp, fn, tn))
    return rows


def pick_threshold(rows):
    # Find smallest threshold that hits target C-precision.
    target_rows = [r for r in rows if r[1] >= TARGET_C_PRECISION]
    if target_rows:
        # smallest threshold among those that hit precision
        chosen = min(target_rows, key=lambda r: r[0])
        return chosen, f"precision>={TARGET_C_PRECISION:.2f}"
    # Fallback: maximize precision subject to recall >= FALLBACK_MIN_C_RECALL
    feasible = [r for r in rows if r[2] >= FALLBACK_MIN_C_RECALL]
    if feasible:
        chosen = max(feasible, key=lambda r: r[1])
        return chosen, f"max_precision@recall>={FALLBACK_MIN_C_RECALL:.2f}"
    # Last resort: hard default
    for r in rows:
        if abs(r[0] - FALLBACK_THRESHOLD) < 1e-6:
            return r, f"fallback={FALLBACK_THRESHOLD:.2f}"
    return rows[len(rows) // 2], "midpoint"


def save_threshold_sweep(rows, chosen, out_path):
    ts = [r[0] for r in rows]
    cp = [r[1] for r in rows]
    cr = [r[2] for r in rows]
    br = [r[3] for r in rows]
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.plot(ts, cp, label="C precision", color="#2b8cbe")
    ax.plot(ts, cr, label="C recall", color="#e34a33")
    ax.plot(ts, br, label="B recall", color="#31a354")
    ax.axvline(chosen[0], color="#636363", linestyle="--", alpha=0.7, label=f"chosen t={chosen[0]:.2f}")
    ax.axhline(TARGET_C_PRECISION, color="#2b8cbe", linestyle=":", alpha=0.5)
    ax.set_xlabel("threshold on P(C)")
    ax.set_ylabel("value")
    ax.set_ylim(0, 1.02)
    ax.set_title("Threshold sweep (val split, calibrated)")
    ax.legend(loc="lower left", fontsize=9)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)


def save_confusion_matrix(y_true, y_pred, out_path, title="Validation confusion matrix"):
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    fig, ax = plt.subplots(figsize=(4, 4))
    im = ax.imshow(cm, cmap="Blues")
    ax.set_xticks([0, 1], CLASSES)
    ax.set_yticks([0, 1], CLASSES)
    ax.set_xlabel("Predicted")
    ax.set_ylabel("True")
    ax.set_title(title)
    for i in range(2):
        for j in range(2):
            ax.text(j, i, cm[i, j], ha="center", va="center",
                    color="white" if cm[i, j] > cm.max() / 2 else "black")
    fig.colorbar(im, ax=ax)
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)


def save_curves(history, out_path):
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    axes[0].plot(history["train_loss"], label="train")
    axes[0].plot(history["val_loss"], label="val")
    axes[0].set_title("Loss")
    axes[0].set_xlabel("epoch")
    axes[0].legend()
    axes[0].grid(alpha=0.3)
    axes[1].plot(history["train_acc"], label="train")
    axes[1].plot(history["val_acc"], label="val")
    axes[1].set_title("Accuracy")
    axes[1].set_xlabel("epoch")
    axes[1].legend()
    axes[1].grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)


def main():
    torch.manual_seed(SEED)
    np.random.seed(SEED)

    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = RUNS_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    print(f"[run] {run_dir}")
    print(f"[device] {DEVICE}")

    build_cache_if_needed()
    samples = collect_samples()
    labels = [lbl for _, lbl in samples]
    print(f"[data] total={len(samples)}  B={labels.count(0)}  C={labels.count(1)}")

    train_idx, val_idx = train_test_split(
        range(len(samples)), test_size=VAL_FRAC, stratify=labels, random_state=SEED
    )

    train_tf = transforms.Compose([
        transforms.Resize((IMG_SIZE + 32, IMG_SIZE + 32)),
        transforms.RandomResizedCrop(IMG_SIZE, scale=(0.75, 1.0), ratio=(0.85, 1.18)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomAffine(degrees=15, translate=(0.08, 0.08), scale=(0.90, 1.10), shear=5),
        transforms.RandomPerspective(distortion_scale=0.2, p=0.3),
        transforms.ColorJitter(brightness=0.3, contrast=0.3, saturation=0.25, hue=0.05),
        transforms.RandomApply([transforms.GaussianBlur(kernel_size=3, sigma=(0.1, 1.5))], p=0.2),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        transforms.RandomErasing(p=0.35, scale=(0.02, 0.15), ratio=(0.3, 3.3), value="random"),
    ])
    val_tf = transforms.Compose([
        transforms.Resize(IMG_SIZE + 32),
        transforms.CenterCrop(IMG_SIZE),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    train_samples = [samples[i] for i in train_idx]
    val_samples = [samples[i] for i in val_idx]
    train_ds = GradingDataset(train_samples, train_tf)
    val_ds = GradingDataset(val_samples, val_tf)
    train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True, num_workers=2, persistent_workers=True)
    val_loader = DataLoader(val_ds, batch_size=BATCH_SIZE, shuffle=False, num_workers=2, persistent_workers=True)

    print(f"[split] train={len(train_ds)}  val={len(val_ds)}")

    model, unfreeze_start = build_model(unfreeze_blocks=UNFREEZE_BLOCKS)
    model.to(DEVICE)
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total = sum(p.numel() for p in model.parameters())
    print(f"[model] unfrozen_from_stage={unfreeze_start}  trainable={trainable:,}  total={total:,}")

    class_weight_tensor = torch.tensor(CLASS_WEIGHTS, dtype=torch.float32, device=DEVICE)
    criterion = nn.CrossEntropyLoss(weight=class_weight_tensor, label_smoothing=LABEL_SMOOTHING)
    print(f"[loss] weighted CE weights={CLASS_WEIGHTS}  label_smoothing={LABEL_SMOOTHING}")

    optimizer, n_head, n_backbone = build_optimizer(model)
    print(f"[optim] AdamW head_params={n_head}  backbone_params={n_backbone}  "
          f"lr_head={LR_HEAD}  lr_backbone={LR_BACKBONE}")
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=EPOCHS)

    history = {"train_loss": [], "val_loss": [], "train_acc": [], "val_acc": []}
    best_val_loss = float("inf")
    best_val_acc_at_best_loss = 0.0
    best_state = None
    best_epoch = 0
    epochs_since_improvement = 0

    for epoch in range(1, EPOCHS + 1):
        t0 = time.time()
        tr_loss, tr_acc, _, _, _ = run_epoch(model, train_loader, criterion, optimizer, train=True)
        val_loss, val_acc, _, _, _ = run_epoch(model, val_loader, criterion, optimizer, train=False)
        scheduler.step()
        history["train_loss"].append(tr_loss)
        history["val_loss"].append(val_loss)
        history["train_acc"].append(tr_acc)
        history["val_acc"].append(val_acc)
        dt = time.time() - t0

        improved = val_loss < best_val_loss - 1e-4
        marker = "*" if improved else " "
        print(f"epoch {epoch:02d}/{EPOCHS}{marker} "
              f"train {tr_loss:.4f}/{tr_acc:.3f}  "
              f"val {val_loss:.4f}/{val_acc:.3f}  "
              f"lr={optimizer.param_groups[0]['lr']:.2e}  ({dt:.1f}s)")

        if improved:
            best_val_loss = val_loss
            best_val_acc_at_best_loss = val_acc
            best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
            best_epoch = epoch
            epochs_since_improvement = 0
        else:
            epochs_since_improvement += 1
            if epochs_since_improvement >= PATIENCE:
                print(f"[early_stop] no val_loss improvement for {PATIENCE} epochs (best epoch={best_epoch})")
                break

    assert best_state is not None
    torch.save(best_state, run_dir / "best_model.pt")
    save_curves(history, run_dir / "curves.png")

    # Reload best weights for calibration/threshold fitting.
    model.load_state_dict(best_state)
    _, _, best_preds, best_labels_list, best_logits = run_epoch(
        model, val_loader, criterion, optimizer, train=False, collect_logits=True
    )
    save_confusion_matrix(
        best_labels_list, best_preds, run_dir / "confusion.png",
        title=f"Val confusion (argmax @ epoch {best_epoch})",
    )
    report = classification_report(
        best_labels_list, best_preds, target_names=CLASSES, digits=3, zero_division=0
    )
    print("\n--- argmax @ 0.5 on val split ---")
    print(report)

    # Fit temperature on best val logits.
    labels_tensor = torch.tensor(best_labels_list, dtype=torch.long)
    temperature = fit_temperature(best_logits, labels_tensor)
    print(f"[calibration] fitted temperature T={temperature:.4f}")

    # Apply temperature, get calibrated probs.
    calibrated_probs = torch.softmax(best_logits / max(temperature, 1e-3), dim=1).numpy()
    probs_c = calibrated_probs[:, 1]
    labels_arr = np.array(best_labels_list, dtype=np.int64)

    # Threshold sweep on calibrated probs.
    sweep = threshold_sweep(probs_c, labels_arr)
    chosen, reason = pick_threshold(sweep)
    c_threshold, c_prec, c_rec, b_rec, tp, fp, fn, tn = chosen
    print(f"[threshold] chosen t={c_threshold:.2f}  "
          f"C-precision={c_prec:.3f}  C-recall={c_rec:.3f}  B-recall={b_rec:.3f}  "
          f"(rule={reason})")

    save_threshold_sweep(sweep, chosen, run_dir / "threshold_sweep.png")

    # Confusion matrix at chosen threshold.
    thresholded_preds = (probs_c >= c_threshold).astype(int).tolist()
    save_confusion_matrix(
        best_labels_list, thresholded_preds, run_dir / "confusion_thresholded.png",
        title=f"Val confusion (t={c_threshold:.2f})",
    )

    # Save per-run artifacts.
    with open(run_dir / "temperature.json", "w") as f:
        json.dump({"temperature": temperature}, f, indent=2)

    with open(run_dir / "threshold.json", "w") as f:
        json.dump(
            {
                "c_threshold": c_threshold,
                "rule": reason,
                "target_c_precision": TARGET_C_PRECISION,
                "val_c_precision": c_prec,
                "val_c_recall": c_rec,
                "val_b_recall": b_rec,
                "val_tp": tp,
                "val_fp": fp,
                "val_fn": fn,
                "val_tn": tn,
            },
            f,
            indent=2,
        )

    with open(run_dir / "classification_report.txt", "w") as f:
        f.write(report)

    metrics = {
        "best_epoch": best_epoch,
        "best_val_loss": best_val_loss,
        "best_val_acc_at_best_loss": best_val_acc_at_best_loss,
        "temperature": temperature,
        "c_threshold": c_threshold,
        "val_c_precision": c_prec,
        "val_c_recall": c_rec,
        "val_b_recall": b_rec,
        "history": history,
        "train_size": len(train_ds),
        "val_size": len(val_ds),
        "classes": CLASSES,
        "epochs_planned": EPOCHS,
        "patience": PATIENCE,
        "lr_head": LR_HEAD,
        "lr_backbone": LR_BACKBONE,
        "wd_head": WD_HEAD,
        "wd_backbone": WD_BACKBONE,
        "unfreeze_blocks": UNFREEZE_BLOCKS,
        "class_weights": CLASS_WEIGHTS,
        "label_smoothing": LABEL_SMOOTHING,
        "batch_size": BATCH_SIZE,
        "img_size": IMG_SIZE,
        "device": str(DEVICE),
        "seed": SEED,
    }
    with open(run_dir / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"\n[done] best_val_loss={best_val_loss:.4f}  best_epoch={best_epoch}  "
          f"C-precision={c_prec:.3f} @ t={c_threshold:.2f}")
    print(f"[artifacts] {run_dir}")


if __name__ == "__main__":
    main()
