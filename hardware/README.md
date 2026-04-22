# Hardware

The physical grading station: how a device enters, gets clamped into a pivoting U-cradle, rotates 180° between captures, and exits — fully automated, no operator hands on the device during capture.

**Status:** U-cradle build spec finalized. All parts are off-the-shelf, ~$150–250 BOM, buildable in a single afternoon plus tuning.

---

## What's here

| File | What it is |
|---|---|
| **[`cradle-build-spec.md`](cradle-build-spec.md)** | **Canonical flip-mechanism spec.** Full build doc for the pivoting U-cradle: concept, axle stackup, BOM, tools, 4-phase build sequence, critical details, tuning targets, gotchas. |
| [`cradle_build_spec.docx`](cradle_build_spec.docx) | Original Word source (contains Figures 1 and 2, referenced from the markdown). |
| [`station-visualization.html`](station-visualization.html) | Step-by-step animated visualization of the full grading station cycle. Open in a browser. |
| [`universal-cellular-3d.html`](universal-cellular-3d.html) | 3D prototype view of the Universal Cellular grading station. Open in a browser. |

---

## The design: pivoting U-cradle

Two arms grip the device by its **edges** (not its faces). The arm pair rotates on a single horizontal axle:

- **0°** → cameras capture one side
- **180°** → cameras capture the other side

One arm is locked to the axle. The other rides on a linear bushing, spring-loaded toward the fixed arm. To load: pull the sliding arm outward, drop the device in, release — spring clamps it.

Because the arms grip edges only, **both faces stay fully exposed** to the cameras. No clamp-open-rotate-clamp-close cycle needed between front and back captures.

---

## Architecture at a glance

**Fixed cameras + stationary device with one 180° flip.** Chosen over the two competing competitor architectures (robot arm presenting all 6 sides; conveyor with photometric scan) because it is simpler, cheaper, and handles any device form factor without re-tooling.

```
Load (operator drops device into U-cradle, spring clamps it)
  │
  ├─► Bright-field capture @ 0°   (full face + edges visible)
  ├─► Dark-field capture @ 0°     (same position — lighting switches, see lighting/)
  │
  ▼
Rotate 180° (~1 s), hard mechanical stop
  │
  ├─► Bright-field capture @ 180°
  ├─► Dark-field capture @ 180°
  │
  ▼
Unload
```

Rotation speed: ~1 s per 180°. Cycle time budget: 57 s. The bottleneck is image capture + model inference, not the mechanism.

---

## Key parameters (at a glance)

Full detail in [`cradle-build-spec.md`](cradle-build-spec.md).

| Parameter | Target |
|---|---|
| Clamp force | 15–20 N at the pad |
| Spring rate (starting) | 750 N/m (kit includes 500 / 750 / 1000 — swap as needed) |
| Pad material | Black silicone, 70 A shore, 3 mm |
| Pad retention groove | 2 mm deep × (device edge + 0.5 mm) wide |
| Rotation stops | Hard mechanical stops at 0° and 180° — **mandatory** |
| Rotation speed | ~1 s per 180° |
| Axle | 8 mm stainless, 300 mm, h6 tolerance |
| Bearings | Pillow-block (KP08 or UCFL001) — bores drilled through both posts in a single pass (coaxial) |
| Finish | Matte black everything (arms, frame, hardware) — gloss destroys cross-polarized imaging |

---

## Non-negotiable build rules

These will kill the build if skipped:

1. **Drill both post bores in a single pass** with the posts clamped together — the only way to guarantee coaxial bearings.
2. **File axle flats** wherever a set screw lands. Set screws on round shafts slip under torque.
3. **Hard rotation stops at 0° and 180°.** Without them, camera registration drifts pass-to-pass.
4. **Matte black everywhere visible.** Gloss reflects into polarized captures.
5. **No oil on bushing or bearings** — attracts dust, dust lands in images. Silicone grease, sparingly.
6. **Threadlocker on the handle knob** — it will unscrew itself under repeated rotation otherwise.

---

## Immediate next steps

1. **Order the BOM** (~$150–250, all off-the-shelf).
2. **Send arm-plate DXF to SendCutSend** (180 × 40 × 4 mm, 6061 aluminum, waterjet).
3. **Build in the 4-phase sequence** from [`cradle-build-spec.md`](cradle-build-spec.md). Plan a full afternoon — the build is faster than the tuning.
4. **Tune clamp force** to 15–20 N with a fish scale; load-test with a 12.9" iPad Pro inverted.
5. **Integrate with lighting** — the U-cradle holds the device stationary between bright-field and dark-field captures at each angle. See [`../lighting/`](../lighting/README.md).
6. **Camera registration check** — 50 cycles at 0° ↔ 180°, target a few pixels of drift or less.

---

## Open questions

- **Motorized rotation or manual handle?** Current spec is manual (handle knob). For full automation ("remove the man"), the handle becomes a stepper + encoder. Trivial swap — same axle, same stops — but not specced yet.
- **Device-edge thickness variation** — the groove is cut for a specific edge thickness + 0.5 mm. Do we need swap-in pads for different form-factor classes (phone / foldable / tablet), or does one groove width + spring range cover everything?
- **Cradle orientation at rest** — which face is up at 0°? Screen-up is operator-natural and gets photographed before anything touches it.
