"""
Simulate device-level OR-aggregation by drawing N random k-image bags from
each class folder, running TTA inference on each image, and applying the
calibrated threshold + OR rule.

Usage:
    python3 scripts/simulate_device.py
    python3 scripts/simulate_device.py --bags 500 --k 12
"""

import os
import sys
import ssl
import json
import argparse
import random
from pathlib import Path

sys.stdout.reconfigure(line_buffering=True)

import certifi
os.environ.setdefault("SSL_CERT_FILE", certifi.where())
ssl._create_default_https_context = ssl.create_default_context

import torch
from PIL import Image
import pillow_heif

sys.path.insert(0, str(Path(__file__).resolve().parent))
from predict import (
    CLASSES,
    DEVICE,
    DEFAULT_TTA_PASSES,
    latest_run,
    load_model,
    load_temperature,
    load_threshold,
    predict_with_tta,
    label_from_probs,
)

pillow_heif.register_heif_opener()

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
IMG_EXTS = {".heic", ".heif", ".jpg", ".jpeg", ".png"}


def collect_paths(cls: str):
    return [p for p in sorted((DATA_DIR / cls).iterdir()) if p.suffix.lower() in IMG_EXTS]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bags", type=int, default=200, help="Number of simulated devices per class")
    ap.add_argument("--k", type=int, default=12, help="Images per simulated device")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    random.seed(args.seed)
    run_dir = latest_run()
    print(f"[run] {run_dir}")
    print(f"[device] {DEVICE}")

    model = load_model(run_dir)
    T = load_temperature(run_dir)
    c_threshold = load_threshold(run_dir)
    print(f"[calibration] T={T:.4f}  c_threshold={c_threshold:.2f}")

    paths_b = collect_paths("B")
    paths_c = collect_paths("C")
    print(f"[pool] B={len(paths_b)}  C={len(paths_c)}")

    # Cache per-image calibrated P(C) so we don't re-run TTA per bag
    def per_image_probs(paths):
        out = {}
        for i, p in enumerate(paths, 1):
            probs = predict_with_tta(model, p, temperature=T, tta_passes=DEFAULT_TTA_PASSES)
            out[p] = probs
            if i % 25 == 0 or i == len(paths):
                print(f"  inference {i}/{len(paths)}")
        return out

    print("[inference] running TTA on B pool ...")
    probs_b = per_image_probs(paths_b)
    print("[inference] running TTA on C pool ...")
    probs_c = per_image_probs(paths_c)

    # Per-image stats at chosen threshold
    def per_image_metrics(probs_map, true_class):
        n_c = sum(1 for p, pr in probs_map.items() if label_from_probs(pr, c_threshold) == "C")
        n_b = len(probs_map) - n_c
        if true_class == "B":
            return {"B": n_b, "C": n_c, "B-accuracy": n_b / len(probs_map)}
        else:
            return {"B": n_b, "C": n_c, "C-accuracy": n_c / len(probs_map)}

    print()
    print("--- Per-image metrics on the full training folders ---")
    b_img = per_image_metrics(probs_b, "B")
    c_img = per_image_metrics(probs_c, "C")
    print(f"B pool ({len(paths_b)} imgs): labeled B={b_img['B']}  C={b_img['C']}  "
          f"B-accuracy={b_img['B-accuracy']:.3f}")
    print(f"C pool ({len(paths_c)} imgs): labeled B={c_img['B']}  C={c_img['C']}  "
          f"C-accuracy={c_img['C-accuracy']:.3f}")

    # Device-level OR simulation
    def simulate(probs_map, paths, bags, k):
        device_c_flags = 0
        for _ in range(bags):
            bag = random.sample(paths, k)
            any_c = any(label_from_probs(probs_map[p], c_threshold) == "C" for p in bag)
            if any_c:
                device_c_flags += 1
        return device_c_flags

    bags = args.bags
    k = args.k
    print()
    print(f"--- Device-level OR simulation (bags={bags}, k={k}) ---")

    b_as_c = simulate(probs_b, paths_b, bags, k)
    c_as_c = simulate(probs_c, paths_c, bags, k)
    print(f"B devices flagged as C (false positive): {b_as_c}/{bags} = {b_as_c / bags:.3f}")
    print(f"C devices flagged as C (true positive ):  {c_as_c}/{bags} = {c_as_c / bags:.3f}")

    summary = {
        "run": str(run_dir),
        "c_threshold": c_threshold,
        "temperature": T,
        "bags": bags,
        "k": k,
        "pool_B": len(paths_b),
        "pool_C": len(paths_c),
        "per_image_B_accuracy": b_img["B-accuracy"],
        "per_image_C_accuracy": c_img["C-accuracy"],
        "device_level_B_as_C": b_as_c / bags,
        "device_level_C_as_C": c_as_c / bags,
    }
    out_path = run_dir / "device_simulation.json"
    with open(out_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\n[saved] {out_path}")


if __name__ == "__main__":
    main()
