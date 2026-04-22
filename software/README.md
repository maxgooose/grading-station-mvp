# Software

The ML/CV pipeline that turns captured images into a grade (B / C today, Universal + Blueberry scales next).

**Status:** POC classifier exists and works on paper, but has a known Grad-CAM background-shortcut problem. Being replaced by a dual-capture segmentation pipeline.

---

## What's here

### `grading-model/` — current POC code

| Script | Purpose |
|---|---|
| `scripts/train.py` | Partial-unfreeze EfficientNet-B0, binary B/C classifier, temperature + threshold calibration saved at end of training. |
| `scripts/predict.py` | Inference on a single image or a folder; applies saved calibration. |
| `scripts/gradcam.py` | Grad-CAM visualizations — the tool that surfaced the background-shortcut issue. |
| `scripts/check_memorization.py` | Sanity check: does the model generalize or just memorize train-set images? |
| `scripts/simulate_device.py` | Simulate multi-photo inference (OR-aggregation across same-device shots). |
| `scripts/app.py` | Minimal local app for trying the model on ad-hoc captures. |
| `scripts/generate_questions_pdf.py` | Produces a PDF of model questions / test cases. |
| `data/` | Training data (gitignored — stored externally). POC uses `B/` and `C/` folders. |
| `runs/` | Training artifacts (gitignored). |

### Current model recipe (POC)

- EfficientNet-B0, last two MBConv blocks unfrozen, differential LR AdamW.
- Class-weighted cross-entropy biased toward B (real distribution is skewed).
- Strong augmentation including RandomErasing.
- Save best on val_loss. Fit temperature + threshold at end of training for calibrated OR-aggregated inference downstream.

---

## Target architecture (next)

Replacing the binary classifier with a **dual-capture segmentation pipeline**, driven by the lighting decision in [`../lighting/`](../lighting/README.md).

```
bright-field image ──► bright-field seg model ──┐
                                                ├──► rule-based grading head ──► grade
dark-field image  ──► dark-field seg model   ──┘
```

| Model | Input | Detects |
|---|---|---|
| Bright-field defect segmenter | Lightbox capture | Paint wear, dents, cracks, chips, stains, edge damage. |
| Dark-field scratch segmenter | Grazing-angle capture | Scratches, hairline cracks, fine abrasion. |
| Grading head | Per-class instance list from both | B / C (POC), Universal + Blueberry (prod). Plain Python rules, human-readable, retrain-free. |

Candidates: YOLOv8-seg for bright-field (fast baseline), U-Net or SegFormer-B0 for dark-field (thin linear features — YOLO mask prototypes handle these poorly, see [`../research/rotberg-yolov8-repo-analysis.md`](../research/rotberg-yolov8-repo-analysis.md)).

---

## Grading scales

The model must output one of the real customer scales — not the POC's B/C. Full definitions live in [`../grading-criteria/README.md`](../grading-criteria/README.md).

- **Universal (primary):** A, B, C(amz), C, D. Five classes, A is rare.
- **Blueberry (later):** Excellent, Good, Acceptable.

Key implication for model design: this is **per-surface, per-defect instance segmentation**, not whole-device classification. The grading head applies the "one deep scratch = D" rule as an OR gate over the combined instance list from bright-field + dark-field captures.

---

## Known issues with current POC

1. **Grad-CAM background shortcut** — model latches onto background cues from the original (no-lightbox) captures. Amazon lightbox purchased 2026-04-14 to fix capture conditions; retraining pending.
2. **Binary output** — B/C only. Doesn't produce the multi-class defect taxonomy needed for Universal/Blueberry grading.
3. **No scratch signal** — bright-field captures lose scratches to near-zero contrast. Dark-field pipeline is the fix.

---

## Immediate next steps

1. Run the zero-cost eyeball test in [`../lighting/lighting-decision-and-plan.md`](../lighting/lighting-decision-and-plan.md) → decides whether dark-field is viable on our device set.
2. Finalize the per-defect label schema (`scratch`, `crack`, `dent`, `paint_wear`, `chip`, `stain`, …). Relabeling is expensive; lock this before CVAT/Roboflow work begins.
3. Pilot-label ~20 bright-field + dark-field image pairs.
4. Train YOLOv8-seg bright-field baseline; train U-Net dark-field baseline; compare.
5. Write the grading head (Python rules over instance lists).
