# Hardware

The physical grading station: enclosure, cameras, lighting, a feeding mechanism that gets devices in and out, and (eventually) an automated flip mechanism so a device can be captured on both faces without the operator touching it during the capture pass.

## MVP scope

| Phase | What's in | Feeding | Flip mechanism |
|---|---|---|---|
| **MVP v1 (current focus)** | Enclosure, camera + lens mount, dual-capture lighting integration, control electronics, **feeding mechanism (device in → device out)**. | **Feeding mechanism — design being finalized today** (mechanism TBD: conveyor / tray / drawer / ?). Handles entry to the load position and exit afterward. | **Operator manually flips** the device between the front-face and back-face capture passes. |
| **MVP v2 (deferred — slight consideration only)** | Adds the automated pivoting U-cradle so the device is clamped once and rotated 180° between captures with no hands on the device. | (Same v1 feeding mechanism — feeding stays decoupled from the flip mechanism.) | **Pivoting U-cradle (specced, not being built now).** Kept on the radar so v1 enclosure / lighting / camera mount choices stay compatible with dropping the cradle in later. |

> The U-cradle spec below is **archival / forward-looking**. It is **not** a v1 build target. Do not order parts for it. The detail is preserved so MVP v2 is a parts-order-and-build job, not a redesign.

**Status:** U-cradle architectural spec exists. All parts are off-the-shelf, ~$150–250 BOM, buildable in a single afternoon plus tuning **when v2 starts**.

---

## What's here

| File | What it is |
|---|---|
| **`cradle-build-spec.md`** *(MVP v2 — currently absent from working tree)* | Canonical flip-mechanism spec. Full build doc for the pivoting U-cradle: concept, axle stackup, BOM, tools, 4-phase build sequence, critical details, tuning targets, gotchas. To be reinstated when MVP v2 starts. |
| `cradle_build_spec.docx` *(MVP v2 — currently absent from working tree)* | Original Word source (contains Figures 1 and 2, referenced from the markdown). |
| [`station-integration.md`](station-integration.md) | How the enclosure, camera, lighting, control, and (eventually) the cradle fit together. v1-vs-v2 split called out inline. |
| [`station-visualization.html`](station-visualization.html) | Step-by-step animated visualization of the full grading station cycle. **Visualizes the MVP v2 end-state** (with the automated flip mechanism). Open in a browser. |
| [`universal-cellular-3d.html`](universal-cellular-3d.html) | 3D prototype view of the Universal Cellular grading station (turntable + manual operator flip — closer to the MVP v1 capture flow). Open in a browser. |

---

## The design: pivoting U-cradle *(MVP v2 — deferred)*

> Everything from here through "Open questions" describes the **MVP v2 flip mechanism**. It is not being built in v1. Read it as the target architecture, not the current build target.

Two arms grip the device by its **edges** (not its faces). The arm pair rotates on a single horizontal axle:

- **0°** → cameras capture one side
- **180°** → cameras capture the other side

One arm is locked to the axle. The other rides on a linear bushing, spring-loaded toward the fixed arm. To load: pull the sliding arm outward, drop the device in, release — spring clamps it.

Because the arms grip edges only, **both faces stay fully exposed** to the cameras. No clamp-open-rotate-clamp-close cycle needed between front and back captures.

---

## Architecture at a glance

**Fixed cameras + stationary device with one 180° flip.** Chosen over the two competing competitor architectures (robot arm presenting all 6 sides; conveyor with photometric scan) because it is simpler, cheaper, and handles any device form factor without re-tooling.

**MVP v1 flow** (what we are actually building):

```
Device fed in via feeding mechanism (mechanism TBD — finalize today)
  │
  ▼
Device arrives at load position, screen-up
  │
  ├─► Bright-field capture (front)
  ├─► Dark-field capture   (front)   — same position, lighting switches
  │
  ▼
Operator opens door, manually flips the device, closes door
  │
  ├─► Bright-field capture (back)
  ├─► Dark-field capture   (back)
  │
  ▼
Grade decided
  │
  ▼
Device fed out via feeding mechanism (to operator / sort area)
```

**MVP v2 flow** (deferred — what the U-cradle below enables):

```
Load (operator drops device into U-cradle, spring clamps it)
  │
  ├─► Bright-field capture @ 0°   (full face + edges visible)
  ├─► Dark-field capture @ 0°     (same position — lighting switches, see lighting/)
  │
  ▼
Cradle rotates 180° (~1 s), hard mechanical stop — no human hands
  │
  ├─► Bright-field capture @ 180°
  ├─► Dark-field capture @ 180°
  │
  ▼
Unload
```

Rotation speed: ~1 s per 180°. Cycle time budget: 57 s. In v2 the bottleneck is image capture + model inference, not the mechanism. In v1 the bottleneck is the operator's hand.

---

## Key parameters (at a glance) *(MVP v2 — deferred)*

Full detail in `cradle-build-spec.md` (to be reinstated when v2 starts).

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

## Non-negotiable build rules *(MVP v2 — deferred)*

These will kill the U-cradle build if skipped (relevant only when v2 starts):

1. **Drill both post bores in a single pass** with the posts clamped together — the only way to guarantee coaxial bearings.
2. **File axle flats** wherever a set screw lands. Set screws on round shafts slip under torque.
3. **Hard rotation stops at 0° and 180°.** Without them, camera registration drifts pass-to-pass.
4. **Matte black everywhere visible.** Gloss reflects into polarized captures.
5. **No oil on bushing or bearings** — attracts dust, dust lands in images. Silicone grease, sparingly.
6. **Threadlocker on the handle knob** — it will unscrew itself under repeated rotation otherwise.

---

## Immediate next steps

### MVP v1 (now)

1. **Finalize the feeding mechanism today.** Pick the in / out path (conveyor, tray, drawer, slide, or other), the hand-off geometry to the load position, and the trigger that says "device is in place, start capture." This decision sets the enclosure footprint and door geometry, so it has to happen before the enclosure is built — see [`station-integration.md`](station-integration.md).
2. Build the **enclosure** (2020 frame + black foamboard panels) — sized to fit the chosen feeding path. See [`station-integration.md`](station-integration.md).
3. Build the **feeding mechanism** per the finalized design.
4. Mount the **camera + lens** centered above the load position. Verify the whole device fits in frame for the largest form factor we care about on day 1.
5. Wire **bright-field + dark-field lighting** with independent MOSFET switching. Run the eyeball test inside the enclosure ([`../lighting/`](../lighting/README.md)).
6. Wire the full **capture cycle**: feed in → device-present sensor → BF shot → DF shot → prompt operator to flip → door interlock → BF shot → DF shot → grade → feed out.
7. **Make the load position v2-ready.** Leave physical clearance and mounting points for the U-cradle's axle posts so v2 is a drop-in upgrade, not a rebuild.

### MVP v2 (deferred — do not start)

1. ~~Order the BOM (~$150–250, all off-the-shelf).~~
2. ~~Send arm-plate DXF to SendCutSend (180 × 40 × 4 mm, 6061 aluminum, waterjet).~~
3. ~~Build in the 4-phase sequence from `cradle-build-spec.md`. Plan a full afternoon — the build is faster than the tuning.~~
4. ~~Tune clamp force to 15–20 N with a fish scale; load-test with a 12.9" iPad Pro inverted.~~
5. ~~Integrate with lighting — the U-cradle holds the device stationary between bright-field and dark-field captures at each angle.~~
6. ~~Camera registration check — 50 cycles at 0° ↔ 180°, target a few pixels of drift or less.~~

---

## Open questions *(MVP v2 — deferred)*

- **Motorized rotation or manual handle?** Spec is manual (handle knob). For full automation ("remove the man"), the handle becomes a stepper + encoder. Trivial swap — same axle, same stops — but not specced yet.
- **Device-edge thickness variation** — the groove is cut for a specific edge thickness + 0.5 mm. Do we need swap-in pads for different form-factor classes (phone / foldable / tablet), or does one groove width + spring range cover everything?
- **Cradle orientation at rest** — which face is up at 0°? Screen-up is operator-natural and gets photographed before anything touches it.
