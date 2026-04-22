# Lighting

How the device is illuminated during capture. This is the most under-valued and most defect-determining component of the whole station.

**Status:** Dual-capture plan (bright-field + dark-field) agreed on paper. Blocking next step: **zero-cost eyeball test** before any hardware change. Decision date: 2026-04-15.

---

## What's here

| File | What it is |
|---|---|
| [`lighting-decision-and-plan.md`](lighting-decision-and-plan.md) | **Start here.** Current decision (keep Amazon lightbox, add dark-field rig), the dual-capture plan, the zero-cost eyeball test, open questions. |
| [`optics-for-hire-scratch-detection.md`](optics-for-hire-scratch-detection.md) | Full technical breakdown of the Optics for Hire blog post — the source of the dark-field idea. Hardware, illumination principle, pipeline, transferable lessons. |

---

## The core insight

**Scratch detection is an optics problem, not a model problem.**

A phone screen is a mirror. An intact surface bounces light in one direction (specular); a scratch scatters it in all directions (diffuse). The lighting regime decides whether the scratch reaches the camera or not. If the geometry is wrong, no model will save you. If the geometry is right, even classical contour detection would work.

---

## Bright-field vs dark-field

| Regime | Camera position | Intact screen looks | Scratch looks | Dents / cracks / paint wear | Our rig |
|---|---|---|---|---|---|
| **Bright-field** | In the specular bounce path | Bright | Faint dark line (tiny contrast) | Visible as soft shadows | Amazon photo tent (purchased 2026-04-14) |
| **Dark-field** | Outside the specular bounce path | Black (bounce goes elsewhere) | Bright line (huge contrast — "pops like stars") | Invisible (black background) | To build — grazing-angle LED + black enclosure |

Neither is better. **They capture different defects.** A real grading station needs both.

---

## The dual-capture plan

Two captures per device, same fixture, same position. Mechanically free — the U-cradle holds the device stationary at each rotation angle.

```
same device, same position
  │
  ├──► capture A: bright-field (current lightbox) ──► bright-field defect segmenter
  │
  └──► capture B: dark-field (new rig)            ──► dark-field scratch segmenter
                                                      │
                                                      ▼
                                                  grading head (rule-based combiner)
                                                      │
                                                      ▼
                                                  B / C (today) or Universal + Blueberry (prod)
```

| Capture | Purpose | Defects detected |
|---|---|---|
| A — Bright-field | Bulk cosmetic grading | Paint wear, dents, cracks, chips, stains, edge damage, logos |
| B — Dark-field | Scratch-only grading | Scratches, hairline cracks, fine abrasion |

---

## Why keep the Amazon lightbox

- Solves a real problem: uniform bright-field illumination fixed the Grad-CAM background-shortcut issue in the POC classifier.
- Excellent for every defect *except* scratches: paint wear, dents, cracks, chips, stains, edge damage, logos, labels, and screen-content legibility.
- It just doesn't solve the scratch problem. Scratches need dark-field. Don't return the tent — augment it.

---

## Dark-field rig — hardware to add

Cheap. Prototype-able under $40, or for **free** by draping black fabric inside the existing lightbox during the dark-field pass.

| Part | Est. cost |
|---|---|
| 1× LED strip (grazing-angle placement above device) | $10 |
| Black matte liner (felt or foamboard) or small separate enclosure | $15 |
| MOSFET + GPIO for independent LED switching between captures | $10 |
| **Total** | **~$35** |

Key geometry: the LED is positioned so its specular bounce off the screen **misses the camera lens**. Only scattered light (from scratches) reaches the sensor.

---

## The zero-cost eyeball test (run before spending a dollar)

This is the **single most important next step**. 15 minutes. Definitively answers "does dark-field even work for our device set" before any hardware purchase or model work.

1. Find the worst-scratched device in the dataset.
2. Turn off all room lights except one lamp.
3. Hold the device under the lamp and tilt slowly through angles.
4. At one specific angle, **every scratch will suddenly glow bright white** on a dark screen. Dramatic and unmistakable.
5. Take two photos:
   - One in the Amazon lightbox (bright-field baseline).
   - One at the magic dark-field angle from step 4 (phone flashlight or lamp + any camera is fine).
6. Compare side by side. Save both to `software/grading-model/data/lighting-test/`.

**Pass:** scratches visible in the dark-field photo but invisible in the bright-field photo → proceed with dual-capture plan.
**Fail:** scratches are not meaningfully more visible in dark-field → theory doesn't apply to our device set. Revisit with different optics, or drop scratch detection as a separate channel.

---

## Open questions

1. **Run the eyeball test** — gating everything downstream.
2. **Scratch distribution on our device set** — front glass only, back glass only, or both? Dark-field applies to whichever surface has them.
3. **Label schema finalization** — `scratch`, `crack`, `dent`, `paint_wear`, `chip`, `stain`. Lock before any labeling. Relabeling is expensive.
4. **Cross-polarization** — suppresses scratch scatter. Must **NOT** go on dark-field capture. OK on bright-field for glare rejection if needed.
5. **Labeling budget** — ~300 existing images × polygon masks ≈ 20-40 hours in Roboflow/CVAT. Relabel all, or start fresh with lightbox-only captures?
