# Grading Station — Integration Spec

How every previously-designed piece (U-cradle, dark-field lighting, camera, bright-field lightbox, controller) fits into one physical station. This is the doc you read before ordering parts.

**Status:** First integration pass. Individual components are specced; integration decisions are flagged as **DECIDED** (locked), **RECOMMENDED** (my call, easy to flip), or **OPEN** (needs your input).

---

## The station, at a glance

A light-tight enclosure (~45 × 45 × 55 cm inside dimensions) containing:

- **U-cradle** at the center, holding the device stationary through a 180° flip
- **Camera** mounted directly above the device, pointing straight down
- **4 LED strips** at screen-plane height on all 4 sides for dark-field
- **Bright-field light panel** on the inner top surface (diffused, reused from Amazon tent)
- **MOSFET + MCU** in a separate electronics compartment, controlling lighting + optional cradle motor + camera trigger
- **Operator loading door** on the front

One device in → 4 captures (bright-field + dark-field at 0° and 180°) → grade out.

---

## Unified BOM (target: **~$500 total**)

Pulled from `cradle-build-spec.md` + `lighting/README.md` + additions for the enclosure and control.

| Subsystem | Line items | Est. cost |
|---|---|---|
| **U-cradle** (from `cradle-build-spec.md`) | 2020 extrusion, bearings, axle, waterjet arm plates, spring kit, silicone pads, handle | **~$200** |
| **Enclosure** | 2020 extrusion frame + black-painted foamboard panels + hinges + magnetic door latch | **~$70** |
| **Dark-field lighting** | 4× LED strips, 4× diffusion-free mounts, matte-black felt liner, 4-channel MOSFET driver | **~$50** |
| **Bright-field lighting** | Reuse Amazon lightbox LEDs (already have), mount into top of enclosure | **~$0** |
| **Camera + lens** | USB machine-vision camera (Arducam / ELP) + 6 mm or 8 mm M12 lens | **~$80** |
| **Control** | ESP32 (or Arduino Uno), 12 V / 24 V PSU, wiring, small OLED status display, start button, door interlock switch | **~$50** |
| **(optional) Motorized cradle** | NEMA 17 stepper + TMC2209 driver + shaft coupling + mount bracket | **~$50** |
| **Total (manual cradle)** | | **~$450** |
| **Total (motorized cradle)** | | **~$500** |

---

## Physical layout

Coordinate system: **origin at the center of the device when loaded**, **Z up**, **X along the device long axis**, **Y along the device short axis**.

### Top-down view (operator looking into the open door)

```
                    back of enclosure
       ┌─────────────────────────────────────┐
       │                                     │
       │     [N LED strip]                   │
       │     ─────────────                   │
       │                                     │
  W    │  │                        │   camera on mount   │    E
       │  │  U-cradle arms hold    │     (above device,  │
       │  │  the device screen-up  │      pointing down) │
       │  │                        │                     │
       │                                     │
       │     ─────────────                   │
       │     [S LED strip]                   │
       │                                     │
       └─────────────────────────────────────┘
                    door (operator side)
```

### Side view (cross-section)

```
        ┌────────────────────────────────────┐
        │  [bright-field diffused panel]     │ ← inner top, diffused LEDs
        │             │                       │
        │             ▼  camera               │
        │             □                       │
        │                                     │
        │    LED ▶ ─────────── ◀ LED          │ ← 4 grazing-angle LED strips
        │         device in U-cradle          │
        │                                     │
        │    cradle axle through posts        │
        │    — manual handle exits side panel │
        │                                     │
        └────────────────────────────────────┘
           matte black everywhere
```

### Key dimensions (DECIDED)

| Dimension | Value | Why |
|---|---|---|
| Inside width × depth | 45 × 45 cm | Clearance for 12.9" iPad Pro + cradle arms + 4 LED strips |
| Inside height | 55 cm | Camera working distance (25–35 cm) + cradle + base clearance |
| Camera height above device | 28 cm | Matches 6–8 mm M12 lens FOV for whole-device frame |
| LED strip height above device surface | ~5 mm | At screen plane; grazing 10–15° angle |
| LED strip distance from device edge | 4 cm | Bright scatter without appearing in frame |

---

## Capture cycle (the full choreography)

| Step | Time | What happens |
|---|---|---|
| 1 | — | Operator opens door, places device in U-cradle (spring clamps it), closes door |
| 2 | 0.2 s | Door interlock confirms closure; MCU starts sequence |
| 3 | 1 s  | Cradle already at 0° (rotation stop); **bright-field LEDs ON**, camera captures frame `A0` |
| 4 | 0.3 s | Bright-field OFF, **dark-field LEDs ON**, camera captures frame `B0` |
| 5 | 1 s  | Cradle rotates 180° (manual handle or stepper); settles at stop |
| 6 | 0.3 s | **Bright-field LEDs ON**, camera captures `A180` |
| 7 | 0.3 s | Dark-field LEDs ON, camera captures `B180` |
| 8 | 2 s  | Host inference: 4 images → model → grade |
| 9 | —   | Grade displayed on OLED; operator opens door, removes device |

**Total cycle: ~5 s automated + operator load/unload.** Well under the 57 s budget in the original architecture.

---

## Electrical / control

**Single MCU (ESP32 recommended).** Handles:

- 4-channel MOSFET driver for LED banks (bright-field, dark-field × N, independent)
- Camera trigger (GPIO pulse if camera supports hardware trigger; otherwise USB command from host PC)
- Door interlock switch (GPIO, fail-safe: no capture if door open)
- Start button + small OLED status display
- (Optional) stepper driver for motorized cradle — TMC2209 with 200-step/rev NEMA 17

**Power:** single 24 V / 5 A bench PSU, buck-converted to 12 V for LEDs and 5 V for MCU. Camera powered over USB.

**Host PC or Raspberry Pi** runs:
- Camera capture (USB)
- Model inference
- Grade display

MCU and host PC communicate over serial (USB CDC on the ESP32). MCU orchestrates the *physical* sequence, host handles *image processing*.

---

## Integration decisions

### DECIDED (locked)

- **Architecture:** fixed camera + U-cradle with 180° flip. Not robot-arm, not conveyor.
- **Dual-capture:** bright-field + dark-field per device, per side.
- **Black everything inside** the enclosure. Mandatory for dark-field contrast.
- **Operator loads manually** (not an autonomous feeder). V1 scope is "remove the man from the grading step," not "remove the man from the loading step."

### RECOMMENDED (my call, flip if you want)

| Decision | Recommendation | Why |
|---|---|---|
| **Cradle drive** | Manual handle for V1 | Simpler; spec already exists. Motorize later — same axle, same stops. ~$50 swap. |
| **Camera** | Arducam / ELP USB 1080p with M12 lens | Enough resolution for whole-device frame (~150 µm/px on a 6" phone at 28 cm). Industrial cameras are overkill until we know the pipeline works. |
| **Lens** | 6 mm M12 | Covers 12.9" iPad at 28 cm. |
| **Number of dark-field LEDs** | 4 (all 4 sides) | Covers all scratch orientations. ~$20 more than 2, worth it. |
| **Bright-field source** | Reuse Amazon lightbox LED strip panel | Already own it. Mount as diffused panel inside the enclosure top. |
| **Enclosure build** | 2020 extrusion frame + black foamboard panels | Cheap, modifiable, light-tight with felt gaskets |
| **MCU** | ESP32 dev board | WiFi for debugging, 3.3 V, plenty of GPIO |
| **Host** | Laptop (dev) → Raspberry Pi 5 (production) | USB camera + basic inference; no GPU needed for a small classifier |

### OPEN (need your input before ordering)

1. **Motorize the cradle or keep manual for V1?** Manual is faster to build and sufficient for prototyping; motorized is necessary before "fully automated." My vote: **manual first**.

2. **Budget envelope.** I'm quoting ~$500 total. Is that within the target, or do we need to push closer to $300? Costs that can come down: camera ($80 → $30 webcam), enclosure ($70 → $25 cardboard-and-fabric prototype).

3. **Device variety on day 1.** Are we optimizing for phones only, or does day-1 need to handle tablets too? Affects enclosure size, camera lens choice, cradle pad groove.

4. **Bright-field inside the dark-field enclosure** — can we really reuse the Amazon tent LEDs in this form factor, or do we need to buy a dedicated diffused panel? Depends on how much we can disassemble the tent. ~$25 risk.

5. **Grade feedback UI.** Just show a letter on an OLED? Or a full screen with the annotated image? Full screen = ~$40 extra, better UX, more wiring.

---

## Build order (once parts are ordered)

Minimum-risk sequence — build one subsystem at a time, verify it works before moving on.

1. **Enclosure skeleton** — 2020 frame, no panels yet. Bare frame to mount everything.
2. **U-cradle build** — follow `cradle-build-spec.md` to the letter. Tune clamp force with fish scale. Tune rotation stops.
3. **Mount cradle inside enclosure** — verify the manual handle exits through a side panel cleanly.
4. **Camera + lens mount** — centered above device, adjustable height. Verify whole device fits frame at both 0° and 180° positions.
5. **Panels + light-tight sealing** — black foamboard, felt gaskets on the door.
6. **Bright-field lighting** — reuse Amazon tent LEDs on top inner surface, diffused.
7. **Dark-field lighting** — 4 LED strips at grazing angle on 4 sides. **Run the eyeball test inside the enclosure** before wiring MOSFETs.
8. **Electrical / MCU** — wire LEDs through MOSFETs, test each channel independently, then integrate sequence firmware.
9. **Host software** — capture 4 frames, save with timestamps, feed to inference.
10. **End-to-end test** — one device, full cycle, manual inspection of output grade.

---

## What this does NOT include (yet)

- **Autonomous device feeder / unloader.** Operator loads manually. V1 scope.
- **Reject / sort bins** post-grading. Operator hand-sorts based on the displayed grade. V1 scope.
- **Production enclosure aesthetics.** V1 looks homemade. Industrial design comes after the pipeline is validated.
- **Cloud sync / grading logs / audit trail.** Local JSON log for now; cloud later.

---

## Related docs

- [`cradle-build-spec.md`](cradle-build-spec.md) — the flip-mechanism detail
- [`../lighting/README.md`](../lighting/README.md) — lighting theory + eyeball test
- [`../lighting/dark-field-setup.html`](../lighting/dark-field-setup.html) — lighting visualization
- [`../grading-criteria/README.md`](../grading-criteria/README.md) — what the station is grading against
- [`../software/README.md`](../software/README.md) — what runs on the host
