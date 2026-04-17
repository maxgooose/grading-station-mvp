# Rotberg YOLOv8 Repo — Analysis & Fit Assessment

**Repo:** https://github.com/AryehRotberg/Mobile-Phone-Defect-Segmentation-YOLOv8
**Cloned to:** `references/Mobile-Phone-Defect-Segmentation-YOLOv8/`
**Relationship to OFH:** None. Independent indie project, no lightbox, different architecture. See `optics-for-hire-scratch-detection.md`.

---

## What the repo actually is

A **thin wrapper around Ultralytics YOLOv8-seg** for single-class scratch segmentation on phone screens. Total hand-written code: ~150 lines across 6 files. The ML work is one call: `YOLO('yolov8s-seg.pt').train(...)`.

### Code map

| File | Lines | Purpose |
|------|-------|---------|
| `src/components/model_trainer.py` | 45 | Wraps `YOLO.train()` + Optuna over `{optimizer, patience}` |
| `src/components/data_ingestion.py` | 27 | Downloads a Roboflow zip, extracts it |
| `src/components/model_evaluation.py` | 17 | Wraps `YOLO.val()` for test-split metrics |
| `src/components/utils.py` | 23 | Reads/writes config.yaml, defines Optuna search space |
| `src/pipelines/pipeline.py` | 34 | Main: ingest → tune → evaluate |
| `app.py` | 29 | Streamlit: upload image → show mask + count |
| `api.py` | 30 | FastAPI `/predict` endpoint |
| `camera_utils.py` | 54 | OpenCV webcam loop + live YOLO inference |

That's the entire repo. No custom model, no custom loss, no custom augmentation, no preprocessing, no calibration, no threshold selection, no metrics logging, no hardware integration.

### Training recipe (from `model_trainer.py`)

```python
YOLO('models/yolov8s-seg.pt').train(
    data=data_config_file,   # Roboflow yolov8-format dataset
    epochs=100,
    imgsz=640,
    optimizer=trial.suggest_categorical('optimizer', ['auto', 'NAdam', 'AdamW', 'RMSProp']),
    patience=trial.suggest_categorical('patience', [10, 25, 50]),
)
```

12 Optuna trials over optimizer × patience. Everything else is Ultralytics defaults.

### Dataset

```yaml
data_ingestion:
  data_download_url: https://app.roboflow.com/ds/0SEyfjIH2b?key=sSYdeFAoCa
```

A Roboflow-hosted dataset named `"Mobile Phone Defect Segmentation.v1i.yolov8.zip"`. Single version, no description, no size, no license, no split documentation. Single class: `scratch` (inferred from `app.py`: `results[0].boxes.cls.tolist().count(0)` — class 0 is the only one used).

### Inference output

```python
num_scratches = results[0].boxes.cls.tolist().count(0)
if num_scratches == 0: "No scratches detected."
else: f"Detected {num_scratches} scratches."
```

That's the whole grading logic: **count of detected scratch instances**. No severity, no size, no area, no pass/fail threshold, no confidence gating.

### Production weights included

`models/production/best.pt` is committed in the repo. Trained on the Roboflow dataset above. Almost certainly will not transfer to our lightbox captures without fine-tuning — different optics, different lighting, different device positioning, different scratch morphology under dark-field vs ambient.

---

## Is this a good approach for our station?

### The architectural decomposition (yes)

**Moving from whole-image classification → per-scratch instance segmentation is the right direction.** Every problem we have with the current EfficientNet-B0 classifier goes away:

| Current (EfficientNet B/C) | Instance segmentation |
|---|---|
| Grad-CAM shows background shortcut | Pixel-level scratch masks — can't cheat |
| Opaque "C" with 57% val acc | Per-scratch coordinates, length, area |
| No explanation for operator | Highlighted mask + count for QA |
| Single image-level label per device | Supervision on every defect pixel |
| Grading logic baked into softmax | Rule-based: `if longest_scratch > X or count > Y → C` |
| Can't generalize to new grade cutoffs | Thresholds tunable without retraining |

This is the same decomposition OFH used (segment screen + detect scratches), just collapsed into one network. It also aligns with the canonical MSD dataset and the FDSNeT paper workflow.

### The specific choice of YOLOv8-seg (mixed)

**Arguments for YOLOv8-seg:**
- Trivial to stand up. This repo proves it — ~150 LoC for a full train/serve pipeline.
- Mature, well-supported, fast inference (~10 ms per frame on an M-series GPU).
- Single-shot — simpler than two-stage U-Net-segment-then-detect.
- Already Apple Silicon friendly via PyTorch MPS.
- Strong instance separation (one mask per detected scratch, not one blob per image).

**Arguments against YOLOv8-seg for scratches specifically:**
- YOLO was designed for **compact, roughly-square, closed-contour objects** (people, cars, dogs). Scratches are the opposite: thin (1–5 px wide), long, highly anisotropic, open-contoured, often broken into segments.
- **Anchor/box assignment struggles with thin long objects.** A 2 px × 400 px scratch has an almost-zero box area and crazy aspect ratio. YOLO's IoU-based matcher penalizes these.
- **Mask prototypes are 1/4 resolution.** YOLOv8-seg outputs masks at imgsz/4 (so 160×160 for the default 640 input). That's too coarse for 1–2 px wide scratches — entire scratches disappear into single mask pixels.
- The scratch-detection literature on thin features (surface inspection, metal, OLED panels) almost universally uses **U-Net variants** or **transformer segmentation** (SegFormer, Mask2Former), not YOLO. FDSNeT, MSDD-UNet, and the OFH post all chose U-Net for a reason.
- Single-class only in this repo. Our station needs multi-class (scratch, crack, dent, paint wear, screen burn) — not hard to extend, but this repo doesn't show the way.

**Net verdict on YOLOv8-seg:** it's a reasonable *first baseline*, not the endpoint. If YOLOv8-seg saturates at ~70% mask-mAP on our data, that's the ceiling of this architecture on thin features; U-Net or SegFormer is where to go next. But starting with YOLOv8-seg gets us to a working end-to-end instance segmenter faster than any alternative.

### The repo itself as a reference (low value)

- **Code quality is thin.** Glue around Ultralytics. Copying the file layout gains us very little — we already have `train.py`, `predict.py`, `app.py` in our own repo.
- **No training recipe we can learn from.** Ultralytics defaults + 12-trial Optuna sweep is not a meaningful contribution.
- **No hardware guidance.** Zero lightbox, illumination, or capture details. All the interesting engineering from the OFH post is missing.
- **Production weights are useless to us.** Trained on Roboflow street-captured scratch images, no lightbox, different distribution.

What *is* useful: confirming that Ultralytics can go from zero to deployed with ~150 LoC, so if we decide to try YOLOv8-seg, the barrier is a weekend not a month.

---

## What we'd actually need to adopt this approach

1. **Pixel-level scratch masks, not B/C labels.** This is the big cost. Every image in `data/B` and `data/C` needs polygon annotations for every scratch. Realistic effort: 20–40 hours of labeling for ~300 images using Roboflow / CVAT / Label Studio.
2. **Multi-class label schema.** `scratch`, `crack`, `dent`, `paint_wear`, `screen_burn`, `edge_chip` — whatever the grading rubric actually cares about. Defined once, hard to change later, so worth a meeting.
3. **Instance-level → device-level grading rule.** A function `(detected_instances) → B | C` that encodes the actual grading standard. This replaces the current softmax. Example: `C if any(scratch.length > 10mm) or count(scratch) > 3 else B`. The advantage: the rule is human-readable and disputable.
4. **Training data from the lightbox only.** Do not mix pre-lightbox captures with lightbox captures — the Grad-CAM shortcut lesson applies here too. The model will learn whichever distribution dominates.
5. **Baseline against U-Net.** Once YOLOv8-seg is working, run the same data through a small U-Net (or SegFormer-B0) to see whether architecture matters. Decide data-driven.

---

## Recommendation

**Adopt the decomposition (instance segmentation), not the repo.** The direction is right and unblocks every current failure mode. But:

- Don't use Rotberg's weights or code directly — the data distribution is wrong and the code is too thin to be worth importing.
- Use this repo as a **speed-of-standup reference**: "Ultralytics + Roboflow + 150 LoC gets you a serving endpoint" is the useful takeaway.
- Plan for the real cost, which is **labeling**, not modeling.
- Keep YOLOv8-seg as the *first* baseline, but expect to compare against U-Net/SegFormer for thin-feature performance.
- Before any of this, validate that scratches are **visible in raw lightbox captures** (OFH lesson). If they aren't, no segmentation model will recover them.

### Suggested order of operations

1. Capture 10 devices in the new lightbox. Eyeball: are scratches clearly visible?
2. If no → fix lightbox geometry (dark-field angle, diffusion, no specular into lens) before any ML work.
3. If yes → label 20 images in Roboflow with polygon scratch masks. Train YOLOv8s-seg for 50 epochs as a baseline. Look at `val_batch*_pred.jpg` outputs.
4. If baseline is promising (>50% mask-mAP) → full relabel + full train + rule-based grading head.
5. If baseline is weak → switch to U-Net / SegFormer and rerun step 3.
