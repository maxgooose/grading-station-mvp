# Lighting Strategy — Current Decision & Plan

**Date:** 2026-04-15
**Status:** Plan agreed, eyeball test pending before any hardware change.

---

## Current state of the lightbox

- **What it is:** A typical Amazon photo tent (diffused fabric walls, LED strips, soft uniform fill from multiple sides). Purchased 2026-04-14 to fix the Grad-CAM background shortcut.
- **What it does well:** Uniform **bright-field** illumination. Excellent for paint wear, dents, cracks, chips, stains, edge damage, logos, labels, and reading screen content.
- **What it does badly:** Scratches. A diffused tent lights the device from every angle at once, so there is no "dark zone" for the camera to sit in. Scratches have near-zero contrast against the bright screen surface.
- **Decision: KEEP the lightbox. Do not return it.** It solves a real problem (bulk defect capture + background shortcut fix). It just does not solve the scratch problem.

---

## Core concept: bright-field vs dark-field

A phone screen is a mirror. A scratch is a rough groove that scatters light in every direction instead of bouncing it cleanly.

**Bright-field (what the Amazon tent does):**
- Camera sits in the specular bounce path. Intact screen is bright. Scratches appear as faint dark lines.
- Contrast for scratches: **tiny.** This is why the current approach fails on them.
- Contrast for dents, cracks, paint wear: **good.** Soft shadows from any surface irregularity.

**Dark-field (what OFH built, what we need to add):**
- Camera sits *outside* the specular bounce path. Intact screen is **black** (bounce goes elsewhere). Scratches appear as **bright lines** (scatter reaches the camera from every angle).
- Contrast for scratches: **huge.** Pops like stars on a night sky.
- Contrast for dents, paint wear, colors: **zero.** The whole background is black — you can't see anything except the scratches.

Neither regime is "better". They capture different defects. A real grading station needs both.

---

## The dual-capture plan

Two captures per device, same fixture, same position. Mechanically free because the device is stationary in the sandwich-flip.

| Capture | Lighting | Purpose | Defect classes detected |
|---|---|---|---|
| **A — Bright-field** | Current Amazon lightbox | Bulk cosmetic grading | Paint wear, dents, cracks, chips, stains, edge damage, logos |
| **B — Dark-field** | New grazing-angle LED + black enclosure (to build) | Scratch-only grading | Scratches, hairline cracks, fine abrasion |

**Grading head:** rule-based combiner, human-readable, no retraining needed to change thresholds.

```
if any(darkfield.scratch.length > 10mm): C
elif brightfield.crack.count > 0: C
elif brightfield.paint_wear.area_pct > 15: C
elif darkfield.scratch.count > 3: C
else: B
```

Each model solves one problem it is good at. The grading rule stays legible and disputable.

---

## Hardware to add (dark-field rig)

Cheap. Can prototype under $40. Can also prototype **free** by just draping black fabric inside the existing lightbox for the dark-field pass.

- 1× LED strip (~$10) — same kind as the existing lightbox
- Black matte liner or small separate enclosure (~$15) — black felt or black foamboard
- LED positioned **grazing angle above the device** so specular bounce misses the lens
- Independent LED switching (MOSFET + GPIO, ~$10) to toggle between bright-field and dark-field passes
- Optional: separate small enclosure instead of re-lining the existing tent

---

## ZERO-COST EYEBALL TEST (run before any hardware change)

This is the single most important next step. It takes 15 minutes and definitively answers "does dark-field even work for our device set" before spending a dollar.

1. Find the worst-scratched device in the current dataset.
2. Turn off all room lights except one lamp.
3. Hold the device under the lamp and tilt slowly through angles.
4. At one specific angle, **every scratch will suddenly glow bright white** on a dark screen. Dramatic and unmistakable.
5. Take two photos:
   - One in the current Amazon lightbox (bright-field baseline).
   - One at the magic dark-field angle from step 4 (phone flashlight or lamp + hand-held camera is fine).
6. Compare side by side.

**Pass condition:** scratches visible to the human eye in the dark-field photo but invisible in the bright-field photo → proceed with the dual-capture plan.
**Fail condition:** scratches are not meaningfully more visible in dark-field → the theory doesn't apply to our device set; revisit with different optics or give up on scratch detection as a separate channel.

---

## Open questions for next session

1. **Run the eyeball test** and save both images to `data/lighting-test/` for reference.
2. **Confirm the device set's scratch distribution** — are scratches on the front glass, back glass, or both? Dark-field needs to be applied to whichever surface has them.
3. **Decide on labeling schema for segmentation.** `scratch`, `crack`, `dent`, `paint_wear`, `chip`, `stain` — finalized list before any labeling starts (relabeling is expensive, schema changes late are painful).
4. **Decide whether to keep cross-polarization anywhere in the station.** It suppresses scratch scatter; it should NOT be on the dark-field capture. If it's on the bright-field capture for glare rejection, that's fine.
5. **Budget the labeling effort.** ~300 existing images × polygon masks ≈ 20–40 hours in Roboflow/CVAT. Decide whether to relabel all or start fresh with lightbox-only captures.

---

## What the models look like under this plan

- **Current EfficientNet-B0 binary classifier** → retired. Replaced by two segmentation models + rules.
- **Bright-field defect segmenter** — multi-class instance segmentation on lightbox captures. Candidates: YOLOv8-seg (fast baseline), U-Net (better for thin cracks), SegFormer-B0 (modern alternative).
- **Dark-field scratch segmenter** — single-class segmentation on dark-field captures. Candidates: U-Net or SegFormer preferred over YOLOv8-seg, because scratches are thin linear features that YOLO's mask prototypes handle poorly (see `rotberg-yolov8-repo-analysis.md`).
- **Grading head** — pure Python rules over the combined instance list from both models. Not a neural network.
