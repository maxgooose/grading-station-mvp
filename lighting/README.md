# Lighting

How the device is illuminated during capture. This is the most under-valued and most defect-determining component of the whole station.

**Status:** Dual-capture plan (bright-field + dark-field) confirmed — **eyeball test PASSED 2026-05-09** inside the wooden-plank shell. **Buy decision locked 2026-06-08:** plug-and-play, manually switched (no MOSFET/PSU for v1). Next action: **purchase → install → re-test capture**. Buy list: [`../hardware/v1-parts-order.html`](../hardware/v1-parts-order.html).

---

## What's here

| File | What it is |
|---|---|
| [`lighting-decision-and-plan.md`](lighting-decision-and-plan.md) | **Start here.** Current decision (lightbox was returned; replace bright-field source + add dark-field rig), the dual-capture plan, the zero-cost eyeball test, open questions. |
| [`optics-for-hire-scratch-detection.md`](optics-for-hire-scratch-detection.md) | Full technical breakdown of the Optics for Hire blog post — the source of the dark-field idea. Hardware, illumination principle, pipeline, transferable lessons. |

---

## The core insight

**Scratch detection is an optics problem, not a model problem.**

A phone screen is a mirror. An intact surface bounces light in one direction (specular); a scratch scatters it in all directions (diffuse). The lighting regime decides whether the scratch reaches the camera or not. If the geometry is wrong, no model will save you. If the geometry is right, even classical contour detection would work.

---

## Bright-field vs dark-field

| Regime | Camera position | Intact screen looks | Scratch looks | Dents / cracks / paint wear | Our rig |
|---|---|---|---|---|---|
| **Bright-field** | In the specular bounce path | Bright | Faint dark line (tiny contrast) | Visible as soft shadows | 2× 12" under-cabinet LED bar (5000 K, CRI 90+, flicker-free), flanking the lens |
| **Dark-field** | Outside the specular bounce path | Black (bounce goes elsewhere) | Bright line (huge contrast — "pops like stars") | Invisible (black background) | 3× bare 12 V LED strips (back/left/right walls), grazing 12–15° |

Neither is better. **They capture different defects.** A real grading station needs both.

---

## The dual-capture plan

Two captures per device, same fixture, same position — bright-field then dark-field, with the LEDs switching between exposures.

- **MVP v1:** the operator flips the device manually between the front-face and back-face capture pairs. Each pair (BF + DF on one face) is mechanically free — same position, lighting just switches.
- **MVP v2 (deferred):** the U-cradle holds the device stationary through an automated 180° flip. Both pairs are then mechanically free with no operator intervention. See [`../hardware/README.md`](../hardware/README.md).

```
same device, same position
  │
  ├──► capture A: bright-field (replacement diffused source) ──► bright-field defect segmenter
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

## Lightbox status update

- The Amazon lightbox was purchased on 2026-04-14 and later returned.
- The project still needs a uniform bright-field source because that lighting condition reduces background shortcut risk in the classifier pipeline.
- Next action: source a replacement diffused bright-field panel/tent and pair it with the planned dark-field rig.

---

## Lighting hardware to buy — LOCKED 2026-06-08 (plug-and-play)

Two off-the-shelf lights, each with its own plug + dimmer. **No MOSFET, no PSU, no custom wiring for v1** — switch bright-field ↔ dark-field by hand between the two shots. Specific products, links, and the flicker caveat live in the canonical buy list: [`../hardware/v1-parts-order.html`](../hardware/v1-parts-order.html). Geometry: [`../hardware/shell-v1-lighting-camera-3d.html`](../hardware/shell-v1-lighting-camera-3d.html).

| Part | Spec | Est. cost |
|---|---|---|
| Bright-field bar ×2 | 12" under-cabinet LED, 5000 K, CRI 90+, flicker-free, linkable; flank the lens | $20–30 |
| Dark-field strip ×1 kit | 12 V DC white strip, cut into 3 wall segments, bare, grazing 12–15° | $20 (or ~$60–80 Waveform FilmGrade flicker-free) |
| Black foam blocks / brackets | set + lock the grazing angle | ~$5 |
| **Total** | | **~$45–115** |

Key geometry: each dark-field strip is positioned so its specular bounce off the screen **misses the camera lens** — only scattered light (from scratches) reaches the sensor. **Flicker:** the ELP 4K is rolling-shutter; PWM dimming bands the image. Run undimmed on DC and set brightness via camera exposure, or use a flicker-free dimmer. Auto-switching is an optional later add (~$10 USB relay or 4-channel MOSFET).

---

## The zero-cost eyeball test — ✅ PASSED 2026-05-09

**Done** — verified inside the wooden-plank shell (hardware/README progress log): dark-field made scratches pop on a black screen, bright-field stayed uniform. The dual-capture plan is confirmed for our device set. Procedure kept below as the re-test recipe for when the real purchased lights are mounted (add a flicker/banding check then).

1. Find the worst-scratched device in the dataset.
2. Turn off all room lights except one lamp.
3. Hold the device under the lamp and tilt slowly through angles.
4. At one specific angle, **every scratch will suddenly glow bright white** on a dark screen. Dramatic and unmistakable.
5. Take two photos:
   - One with any temporary diffused bright-field setup (bright-field baseline).
   - One at the magic dark-field angle from step 4 (phone flashlight or lamp + any camera is fine).
6. Compare side by side. Save both to `software/grading-model/data/lighting-test/`.

**Pass:** scratches visible in the dark-field photo but invisible in the bright-field photo → proceed with dual-capture plan.
**Fail:** scratches are not meaningfully more visible in dark-field → theory doesn't apply to our device set. Revisit with different optics, or drop scratch detection as a separate channel.

---

## Open questions

1. ~~**Run the eyeball test**~~ ✅ **Done 2026-05-09 (PASSED).** Now: buy the locked lights, install, and re-test the capture (with a flicker check).
2. **Scratch distribution on our device set** — front glass only, back glass only, or both? Dark-field applies to whichever surface has them.
3. **Label schema finalization** — `scratch`, `crack`, `dent`, `paint_wear`, `chip`, `stain`. Lock before any labeling. Relabeling is expensive.
4. **Cross-polarization** — suppresses scratch scatter. Must **NOT** go on dark-field capture. OK on bright-field for glare rejection if needed.
5. **Labeling budget** — ~300 existing images × polygon masks ≈ 20-40 hours in Roboflow/CVAT. Relabel all, or start fresh with lightbox-only captures?
