"""
Check if the model memorized the training set.

Reproduces the exact 80/20 stratified split used in train.py (same seed=42),
runs TTA inference on train vs val images separately, and reports per-image
accuracy for each subset. A large gap between train and val accuracy means
the model is memorizing; a small gap means it's generalizing.
"""

import os
import sys
import ssl
from pathlib import Path

sys.stdout.reconfigure(line_buffering=True)

import certifi
os.environ.setdefault("SSL_CERT_FILE", certifi.where())
ssl._create_default_https_context = ssl.create_default_context

import numpy as np
from sklearn.model_selection import train_test_split

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

ROOT = Path(__file__).resolve().parent.parent
CACHE_DIR = ROOT / "data" / ".cache"

SEED = 42
VAL_FRAC = 0.2


def collect_samples():
    samples = []
    for label_idx, cls in enumerate(CLASSES):
        cls_dir = CACHE_DIR / cls
        for p in sorted(cls_dir.glob("*.jpg")):
            samples.append((p, label_idx))
    return samples


def evaluate(model, samples, T, threshold, name):
    b_correct = 0
    b_total = 0
    c_correct = 0
    c_total = 0
    for path, true_label in samples:
        probs = predict_with_tta(model, path, temperature=T, tta_passes=DEFAULT_TTA_PASSES)
        pred = label_from_probs(probs, threshold)
        if true_label == 0:  # B
            b_total += 1
            if pred == "B":
                b_correct += 1
        else:  # C
            c_total += 1
            if pred == "C":
                c_correct += 1
    b_acc = b_correct / b_total if b_total > 0 else 0.0
    c_acc = c_correct / c_total if c_total > 0 else 0.0
    total_acc = (b_correct + c_correct) / (b_total + c_total)
    print(f"  {name}: total={b_total + c_total}  "
          f"B {b_correct}/{b_total} ({b_acc:.1%})  "
          f"C {c_correct}/{c_total} ({c_acc:.1%})  "
          f"overall {total_acc:.1%}")
    return {
        "b_correct": b_correct, "b_total": b_total, "b_acc": b_acc,
        "c_correct": c_correct, "c_total": c_total, "c_acc": c_acc,
        "overall": total_acc,
    }


def main():
    run_dir = latest_run()
    print(f"[run] {run_dir}")
    print(f"[device] {DEVICE}")

    model = load_model(run_dir)
    T = load_temperature(run_dir)
    threshold = load_threshold(run_dir)
    print(f"[calibration] T={T:.4f}  c_threshold={threshold:.2f}")

    samples = collect_samples()
    labels = [lbl for _, lbl in samples]
    print(f"[pool] total={len(samples)}  B={labels.count(0)}  C={labels.count(1)}")

    # Reproduce the exact same split as train.py
    train_idx, val_idx = train_test_split(
        range(len(samples)), test_size=VAL_FRAC, stratify=labels, random_state=SEED
    )
    train_samples = [samples[i] for i in train_idx]
    val_samples = [samples[i] for i in val_idx]
    print(f"[split] train={len(train_samples)}  val={len(val_samples)}")

    print()
    print("=== Per-image accuracy by split ===")
    train_metrics = evaluate(model, train_samples, T, threshold, "TRAIN (model saw these)")
    val_metrics = evaluate(model, val_samples, T, threshold, "VAL   (HELD OUT — honest test)")

    print()
    print("=== Diagnosis ===")
    overall_gap = train_metrics["overall"] - val_metrics["overall"]
    b_gap = train_metrics["b_acc"] - val_metrics["b_acc"]
    c_gap = train_metrics["c_acc"] - val_metrics["c_acc"]
    print(f"  overall gap (train - val): {overall_gap:+.1%}")
    print(f"  B-acc gap (train - val):   {b_gap:+.1%}")
    print(f"  C-acc gap (train - val):   {c_gap:+.1%}")

    if overall_gap > 0.25:
        verdict = "HEAVY MEMORIZATION — train >> val"
    elif overall_gap > 0.15:
        verdict = "MODERATE memorization — visible gap but val still useful"
    elif overall_gap > 0.08:
        verdict = "MILD gap — some overfit, mostly generalizing"
    else:
        verdict = "GENERALIZING — small train/val gap"
    print(f"  verdict: {verdict}")
    print()
    print("The VAL numbers are the honest ones — that's what you should trust.")


if __name__ == "__main__":
    main()
