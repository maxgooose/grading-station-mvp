"""
Run the trained grading model on one or more images, with TTA + calibrated threshold.

Usage:
    python3 scripts/predict.py path/to/image.heic [path/to/image2.jpg ...]
    python3 scripts/predict.py --run runs/20260413_125250 path/to/image.heic
    python3 scripts/predict.py --threshold 0.7 path/to/image.heic
    python3 scripts/predict.py --no-tta path/to/image.heic
"""

import os
import sys
import ssl
import json
import argparse
from pathlib import Path

sys.stdout.reconfigure(line_buffering=True)

import certifi
os.environ.setdefault("SSL_CERT_FILE", certifi.where())
ssl._create_default_https_context = ssl.create_default_context

import torch
import torch.nn as nn
from torchvision import transforms
from torchvision import transforms as T
from torchvision.models import efficientnet_b0
from PIL import Image
import pillow_heif

pillow_heif.register_heif_opener()

ROOT = Path(__file__).resolve().parent.parent
RUNS_DIR = ROOT / "runs"
CLASSES = ["B", "C"]
IMG_SIZE = 224
DEFAULT_TTA_PASSES = 8
DEFAULT_THRESHOLD = 0.5

DEVICE = torch.device("mps" if torch.backends.mps.is_available() else "cpu")

NORMALIZE = transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])


def latest_run():
    runs = sorted([p for p in RUNS_DIR.iterdir() if p.is_dir() and (p / "best_model.pt").exists()])
    if not runs:
        raise SystemExit(f"No runs with best_model.pt found under {RUNS_DIR}")
    return runs[-1]


def build_model():
    model = efficientnet_b0(weights=None)
    in_features = model.classifier[1].in_features
    model.classifier = nn.Sequential(
        nn.Dropout(p=0.3, inplace=True),
        nn.Linear(in_features, len(CLASSES)),
    )
    return model


def load_model(run_dir: Path):
    ckpt = run_dir / "best_model.pt"
    state = torch.load(ckpt, map_location=DEVICE)
    model = build_model()
    try:
        model.load_state_dict(state)
    except RuntimeError:
        # Fallback for older checkpoints that used the original single-Linear head.
        legacy = efficientnet_b0(weights=None)
        in_features = legacy.classifier[1].in_features
        legacy.classifier[1] = nn.Linear(in_features, len(CLASSES))
        legacy.load_state_dict(state)
        model = legacy
        print("[warn] loaded legacy checkpoint with single-Linear head")
    model.to(DEVICE).eval()
    return model


def load_temperature(run_dir: Path) -> float:
    p = run_dir / "temperature.json"
    if not p.exists():
        print("[warn] no temperature.json — using T=1.0 (uncalibrated)")
        return 1.0
    return float(json.loads(p.read_text())["temperature"])


def load_threshold(run_dir: Path) -> float:
    p = run_dir / "threshold.json"
    if not p.exists():
        print(f"[warn] no threshold.json — using default {DEFAULT_THRESHOLD}")
        return DEFAULT_THRESHOLD
    return float(json.loads(p.read_text())["c_threshold"])


def _to_tensor_and_norm(pil_img) -> torch.Tensor:
    return NORMALIZE(T.ToTensor()(pil_img))


def _tta_transforms(pil_img, size=IMG_SIZE):
    """Return a list of 8 pre-processed tensors: identity, hflip, 4 corner crops + center crop,
    and 2 small rotations. All share the same normalization."""
    resized = T.Resize(size + 32)(pil_img)  # short-side resize
    w, h = resized.size
    cx, cy = w // 2, h // 2
    half = size // 2

    # center crop for identity and hflip
    center = resized.crop((cx - half, cy - half, cx + half, cy + half))
    center_hflip = T.RandomHorizontalFlip(p=1.0)(center)

    # 4 corner crops
    top_left = resized.crop((0, 0, size, size)) if w >= size and h >= size else center
    top_right = resized.crop((w - size, 0, w, size)) if w >= size and h >= size else center
    bot_left = resized.crop((0, h - size, size, h)) if w >= size and h >= size else center
    bot_right = resized.crop((w - size, h - size, w, h)) if w >= size and h >= size else center

    # small rotations
    rot_pos = T.functional.rotate(center, 8)
    rot_neg = T.functional.rotate(center, -8)

    views = [center, center_hflip, top_left, top_right, bot_left, bot_right, rot_pos, rot_neg]
    tensors = [_to_tensor_and_norm(v) for v in views]
    return torch.stack(tensors, dim=0)


def predict_with_tta(model, image, temperature: float = 1.0, tta_passes: int = DEFAULT_TTA_PASSES):
    """Return calibrated (P_B, P_C) averaged over TTA views.
    `image` can be a path (str or Path) or an open PIL.Image.
    tta_passes=1 disables TTA (single center crop)."""
    if not isinstance(image, Image.Image):
        image = Image.open(image).convert("RGB")
    else:
        image = image.convert("RGB")

    if tta_passes <= 1:
        x = T.Compose([
            T.Resize(IMG_SIZE + 32),
            T.CenterCrop(IMG_SIZE),
            T.ToTensor(),
            NORMALIZE,
        ])(image).unsqueeze(0).to(DEVICE)
    else:
        x = _tta_transforms(image).to(DEVICE)

    with torch.no_grad():
        logits = model(x)
        probs = torch.softmax(logits / max(temperature, 1e-3), dim=1)
        mean_probs = probs.mean(dim=0).cpu().tolist()
    return mean_probs  # [P_B, P_C]


def label_from_probs(probs, c_threshold: float) -> str:
    return "C" if probs[1] >= c_threshold else "B"


def predict_one(model, image_path, temperature: float = 1.0):
    """Single-pass (no TTA) prediction — thin wrapper for quick debugging."""
    probs = predict_with_tta(model, image_path, temperature=temperature, tta_passes=1)
    return probs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("images", nargs="+", type=Path)
    ap.add_argument("--run", type=Path, default=None)
    ap.add_argument("--threshold", type=float, default=None,
                    help="Override calibrated c_threshold from threshold.json")
    ap.add_argument("--no-tta", action="store_true", help="Disable test-time augmentation")
    args = ap.parse_args()

    run_dir = args.run if args.run else latest_run()
    print(f"[run] {run_dir}")
    print(f"[device] {DEVICE}")

    model = load_model(run_dir)
    temperature = load_temperature(run_dir)
    c_threshold = args.threshold if args.threshold is not None else load_threshold(run_dir)
    tta_passes = 1 if args.no_tta else DEFAULT_TTA_PASSES

    print(f"[calibration] T={temperature:.4f}  c_threshold={c_threshold:.2f}  tta_passes={tta_passes}")
    print()
    print(f"{'image':<44} {'label':<6} {'B%':>8} {'C%':>8}")
    print("-" * 72)

    b_labels, c_labels = 0, 0
    for p in args.images:
        if not p.exists():
            print(f"{p.name[:44]:<44} NOT FOUND")
            continue
        probs = predict_with_tta(model, p, temperature=temperature, tta_passes=tta_passes)
        label = label_from_probs(probs, c_threshold)
        if label == "B":
            b_labels += 1
        else:
            c_labels += 1
        print(f"{p.name[:44]:<44} {label:<6} {probs[0] * 100:>7.1f}% {probs[1] * 100:>7.1f}%")

    print("-" * 72)
    print(f"Summary: {b_labels} B  /  {c_labels} C  (threshold={c_threshold:.2f})")


if __name__ == "__main__":
    main()
