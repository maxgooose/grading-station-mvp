# Lighting Strategy — Current Decision & Plan

**Date:** 2026-04-15 · **Updated:** 2026-06-08 (purchase decision locked)
**Status:** Eyeball test **PASSED 2026-05-09** (inside the wooden-plank shell). Lighting for v1 is **plug-and-play, manually switched** — the 12 V / MOSFET / PSU rig described below is **superseded** (kept only as the optional auto-switch upgrade). Buy list locked; see [`../hardware/v1-parts-order.html`](../hardware/v1-parts-order.html).

---

## Current state of the lightbox

- **What it was:** A typical Amazon photo tent (diffused fabric walls, LED strips, soft uniform fill from multiple sides). Purchased 2026-04-14 to fix the Grad-CAM background shortcut, then later returned.
- **What it does well:** Uniform **bright-field** illumination. Excellent for paint wear, dents, cracks, chips, stains, edge damage, logos, labels, and reading screen content.
- **What it does badly:** Scratches. A diffused tent lights the device from every angle at once, so there is no "dark zone" for the camera to sit in. Scratches have near-zero contrast against the bright screen surface.
- **Decision update:** The lightbox has already been returned. Replace it with another diffused bright-field source while still adding dark-field for scratch visibility.

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

Two captures per device per face, same fixture, same position. The bright-field → dark-field switch is mechanically free at each face — only the LED bank changes.

- **MVP v1:** operator manually flips the device between the front-face and back-face capture pairs.
- **MVP v2 (deferred):** the U-cradle handles the 180° flip without the operator touching the device. See [`../hardware/README.md`](../hardware/README.md).

| Capture | Lighting | Purpose | Defect classes detected |
|---|---|---|---|
| **A — Bright-field** | Replacement diffused bright-field source | Bulk cosmetic grading | Paint wear, dents, cracks, chips, stains, edge damage, logos |
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

## Hardware to buy — LOCKED 2026-06-08 (plug-and-play, manual switching)

Two off-the-shelf lights, each with its own plug + dimmer. **No MOSFET, no PSU, no wiring for v1** — the operator switches bright-field ↔ dark-field by hand between the two shots (they're already opening the door to flip the phone). Full buy list + links: [`../hardware/v1-parts-order.html`](../hardware/v1-parts-order.html). Canonical geometry: [`../hardware/shell-v1-lighting-camera-3d.html`](../hardware/shell-v1-lighting-camera-3d.html).

- **Bright-field** — 2× 12" under-cabinet LED bar, 5000 K, **CRI 90+, flicker-free**, linkable (e.g. Amazon `B0FX521RMC`), ~$20–30. The two bars **flank the central ⌀2" lens hole** so the screen-mirror reflection lands beside the lens, not in it.
- **Dark-field** — one **12 V DC** white LED strip, cut into **3 segments → back + left + right walls**, mounted **bare** (no diffuser) on small black-foam blocks, ~5 mm above the screen plane, 3–6 cm from the device edge, tilted **12–15° grazing**. All three on together. Budget consumer kit ~$20, or the vision-grade Waveform FilmGrade flicker-free system ~$60–80. Prefer 12 V DC (not 5 V USB) so a later ~$10 USB relay can auto-switch it.

> **Flicker is the #1 machine-vision risk.** The ELP 4K is rolling-shutter — PWM *dimming* causes rolling-bar banding. Run the LEDs **undimmed at full brightness on a clean DC supply and set brightness with the camera's exposure**; only dim with a **flicker-free** dimmer; always confirm with a test capture.

**Optional auto-switch upgrade (v1.5/v2):** a 4-channel MOSFET + GPIO (~$10) on a 12 V supply replaces the manual switch. This is the only surviving piece of the old MOSFET plan.

---

## Lighting for the 5-camera layout

5 cameras (1 overhead + 4 corner-mounted edge cams, lens center ~0.75" up — corner layout confirmed 2026-06-11, see [`../hardware/README.md`](../hardware/README.md)) split the lighting into **three states**:

| State | Lights | Captures |
|---|---|---|
| A — Bright-field | Roof bars | Top camera (flat face) |
| B — Edge bright-field | Wall strips, diffused | 4 side cams (edges + corners) |
| C — Dark-field | Wall strips, bare grazing | Top camera only (scratches) |

Key points: **dark-field is top-camera-only** (its geometry is defined for the overhead lens), and the side cams need state **B** because a top-down bright-field underlights the vertical sidewalls. The corner cams sit **low (lens ~0.75")** — the same band as the grazing strips — so strips are placed **after** the cameras are mounted, out of all 5 camera FOVs (the old "strips low, cams high ~4" — no collision" note belonged to the superseded mid-wall layout). All switching stays manual for v1.

---

## ZERO-COST EYEBALL TEST — ✅ PASSED 2026-05-09

**Done.** Bright-field + dark-field were verified inside the wooden-plank shell (see the hardware/README progress log): bright-field uniform across the load position; dark-field grazing strips give clean shadows with no spill into the camera FOV → the dual-capture theory holds for our device set. The procedure below is kept as the historical record **and** as the re-test recipe once the real purchased lights are mounted — now with an added flicker/banding check (see the verification step in the parts order).

1. Find the worst-scratched device in the current dataset.
2. Turn off all room lights except one lamp.
3. Hold the device under the lamp and tilt slowly through angles.
4. At one specific angle, **every scratch will suddenly glow bright white** on a dark screen. Dramatic and unmistakable.
5. Take two photos:
   - One in any temporary diffused bright-field setup (bright-field baseline).
   - One at the magic dark-field angle from step 4 (phone flashlight or lamp + hand-held camera is fine).
6. Compare side by side.

**Pass condition:** scratches visible to the human eye in the dark-field photo but invisible in the bright-field photo → proceed with the dual-capture plan.
**Fail condition:** scratches are not meaningfully more visible in dark-field → the theory doesn't apply to our device set; revisit with different optics or give up on scratch detection as a separate channel.

---

## Open questions for next session

1. ~~**Run the eyeball test**~~ ✅ **Done 2026-05-09 (PASSED).** Re-run with the real purchased lights once mounted — add a flicker/banding check — and save both images to `software/grading-model/data/lighting-test/`.
2. **Confirm the device set's scratch distribution** — are scratches on the front glass, back glass, or both? Dark-field needs to be applied to whichever surface has them.
3. **Decide on labeling schema for segmentation.** `scratch`, `crack`, `dent`, `paint_wear`, `chip`, `stain` — finalized list before any labeling starts (relabeling is expensive, schema changes late are painful).
4. **Decide whether to keep cross-polarization anywhere in the station.** It suppresses scratch scatter; it should NOT be on the dark-field capture. If it's on the bright-field capture for glare rejection, that's fine.
5. **Budget the labeling effort.** ~300 existing images × polygon masks ≈ 20–40 hours in Roboflow/CVAT. Decide whether to relabel all or start fresh with replacement-bright-field captures.

---

## What the models look like under this plan

- **Current EfficientNet-B0 binary classifier** → retired. Replaced by two segmentation models + rules.
- **Bright-field defect segmenter** — multi-class instance segmentation on diffused bright-field captures. Candidates: YOLOv8-seg (fast baseline), U-Net (better for thin cracks), SegFormer-B0 (modern alternative).
- **Dark-field scratch segmenter** — single-class segmentation on dark-field captures. Candidates: U-Net or SegFormer preferred over YOLOv8-seg, because scratches are thin linear features that YOLO's mask prototypes handle poorly (see `rotberg-yolov8-repo-analysis.md`).
- **Grading head** — pure Python rules over the combined instance list from both models. Not a neural network.
