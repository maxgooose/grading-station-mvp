"""
Grad-CAM visualization for the grading model.
Shows where the model looks when it predicts a given class.

Usage:
    python3 scripts/gradcam.py path/to/image.heic
    python3 scripts/gradcam.py --class C --count 12 --montage
    python3 scripts/gradcam.py --run runs/20260413_151726 data/C/IMG_1437.HEIC
"""

import os
import sys
import ssl
import math
import argparse
from pathlib import Path

sys.stdout.reconfigure(line_buffering=True)

import certifi
os.environ.setdefault("SSL_CERT_FILE", certifi.where())
ssl._create_default_https_context = ssl.create_default_context

import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import transforms
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import pillow_heif

sys.path.insert(0, str(Path(__file__).resolve().parent))
from predict import (
    CLASSES,
    DEVICE,
    latest_run,
    load_model,
    load_temperature,
    load_threshold,
)

pillow_heif.register_heif_opener()

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
IMG_SIZE = 224

NORMALIZE = transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
PREP = transforms.Compose([
    transforms.Resize(IMG_SIZE + 32),
    transforms.CenterCrop(IMG_SIZE),
    transforms.ToTensor(),
    NORMALIZE,
])


class GradCAM:
    """Basic Grad-CAM on the last feature map of EfficientNet-B0."""

    def __init__(self, model, target_layer):
        self.model = model
        self.target_layer = target_layer
        self.activations = None
        self.gradients = None
        self._fwd_handle = target_layer.register_forward_hook(self._save_activation)
        self._bwd_handle = target_layer.register_full_backward_hook(self._save_gradient)

    def _save_activation(self, module, inp, out):
        self.activations = out.detach()

    def _save_gradient(self, module, grad_in, grad_out):
        self.gradients = grad_out[0].detach()

    def __call__(self, input_tensor, target_class):
        self.model.zero_grad()
        logits = self.model(input_tensor)
        score = logits[0, target_class]
        score.backward(retain_graph=False)

        # Weights: global-avg of gradients per channel
        weights = self.gradients.mean(dim=(2, 3), keepdim=True)  # [1, C, 1, 1]
        cam = (weights * self.activations).sum(dim=1, keepdim=True)  # [1, 1, h, w]
        cam = F.relu(cam)

        # Normalize to [0, 1]
        cam_max = cam.amax(dim=(2, 3), keepdim=True)
        cam = cam / (cam_max + 1e-8)

        # Upsample to input image size
        cam = F.interpolate(cam, size=(IMG_SIZE, IMG_SIZE), mode="bilinear", align_corners=False)
        return cam[0, 0].cpu().numpy(), torch.softmax(logits, dim=1)[0].detach().cpu().tolist()

    def close(self):
        self._fwd_handle.remove()
        self._bwd_handle.remove()


def load_pil(path: Path) -> Image.Image:
    return Image.open(path).convert("RGB")


def to_tensor(pil: Image.Image) -> torch.Tensor:
    return PREP(pil).unsqueeze(0).to(DEVICE)


def overlay(pil_224: Image.Image, heatmap: np.ndarray, alpha: float = 0.5) -> np.ndarray:
    base = np.array(pil_224).astype(np.float32) / 255.0  # [H, W, 3] in [0,1]
    cmap = cm.get_cmap("jet")
    heat_rgb = cmap(heatmap)[..., :3]  # drop alpha
    mixed = (1 - alpha) * base + alpha * heat_rgb
    mixed = np.clip(mixed, 0, 1)
    return mixed


def display_pil_224(pil: Image.Image) -> Image.Image:
    return transforms.Compose([
        transforms.Resize(IMG_SIZE + 32),
        transforms.CenterCrop(IMG_SIZE),
    ])(pil)


def run_one(cam, path: Path, target_class: int):
    pil = load_pil(path)
    pil_display = display_pil_224(pil)
    x = to_tensor(pil)
    heatmap, probs = cam(x, target_class=target_class)
    mixed = overlay(pil_display, heatmap)
    return pil_display, heatmap, mixed, probs


def save_pair(pil_display: Image.Image, mixed: np.ndarray, probs, title: str, out_path: Path):
    fig, axes = plt.subplots(1, 2, figsize=(7, 3.6))
    axes[0].imshow(pil_display)
    axes[0].set_title("input")
    axes[0].axis("off")
    axes[1].imshow(mixed)
    axes[1].set_title(f"Grad-CAM (C)   P_B={probs[0]:.2f}  P_C={probs[1]:.2f}")
    axes[1].axis("off")
    fig.suptitle(title, fontsize=10)
    fig.tight_layout()
    fig.savefig(out_path, dpi=130, bbox_inches="tight")
    plt.close(fig)


def save_montage(items, out_path: Path, cols: int = 4, title: str = ""):
    n = len(items)
    rows = math.ceil(n / cols)
    fig, axes = plt.subplots(rows, cols, figsize=(cols * 3.0, rows * 3.2))
    if rows == 1:
        axes = axes.reshape(1, -1)
    for i, (path, pil_display, mixed, probs) in enumerate(items):
        r, c = i // cols, i % cols
        ax = axes[r, c]
        ax.imshow(mixed)
        ax.set_title(f"{path.name}\nP_C={probs[1]:.2f}", fontsize=7)
        ax.axis("off")
    for j in range(n, rows * cols):
        r, c = j // cols, j % cols
        axes[r, c].axis("off")
    if title:
        fig.suptitle(title, fontsize=12, y=0.99)
    fig.tight_layout()
    fig.savefig(out_path, dpi=140, bbox_inches="tight")
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("images", nargs="*", type=Path)
    ap.add_argument("--run", type=Path, default=None)
    ap.add_argument("--class", dest="target_class", type=str, default="C", choices=CLASSES,
                    help="Target class to visualize (which class are we asking 'why C?' for)")
    ap.add_argument("--montage", action="store_true",
                    help="Build a 4-column grid of B and C samples")
    ap.add_argument("--count", type=int, default=8, help="Per-class count for --montage")
    args = ap.parse_args()

    run_dir = args.run if args.run else latest_run()
    out_dir = run_dir / "gradcam"
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"[run] {run_dir}")
    print(f"[device] {DEVICE}")

    model = load_model(run_dir)
    model.eval()
    for p in model.parameters():
        p.requires_grad = True  # Grad-CAM needs grads even in eval

    # Target the last feature map (spatial) before adaptive avgpool.
    target_layer = model.features[-1]
    cam = GradCAM(model, target_layer)

    target_idx = CLASSES.index(args.target_class)

    if args.montage:
        samples = []
        for cls in CLASSES:
            paths = sorted((DATA_DIR / cls).iterdir())
            paths = [p for p in paths if p.suffix.lower() in {".heic", ".heif", ".jpg", ".jpeg", ".png"}]
            # Pick evenly spaced samples across the folder to avoid all-from-start bias
            step = max(1, len(paths) // args.count)
            picks = paths[::step][:args.count]
            for path in picks:
                pil_display, heatmap, mixed, probs = run_one(cam, path, target_idx)
                samples.append((path, pil_display, mixed, probs))

        b_samples = samples[:args.count]
        c_samples = samples[args.count:]
        save_montage(b_samples, out_dir / "montage_B.png", cols=4,
                     title=f"Grad-CAM on B images (showing 'why {args.target_class}?')")
        save_montage(c_samples, out_dir / "montage_C.png", cols=4,
                     title=f"Grad-CAM on C images (showing 'why {args.target_class}?')")
        print(f"[saved] {out_dir / 'montage_B.png'}")
        print(f"[saved] {out_dir / 'montage_C.png'}")
    else:
        if not args.images:
            raise SystemExit("Provide image paths or use --montage")
        for path in args.images:
            pil_display, heatmap, mixed, probs = run_one(cam, path, target_idx)
            out = out_dir / f"{path.stem}_gradcam.png"
            save_pair(pil_display, mixed, probs,
                      f"{path.name}  (why {args.target_class}?)",
                      out)
            print(f"[saved] {out}")

    cam.close()


if __name__ == "__main__":
    main()
