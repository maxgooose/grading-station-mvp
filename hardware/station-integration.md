# Grading Station — Integration Spec

How every previously-designed piece (dark-field lighting, camera, bright-field lightbox, controller, **feeding mechanism**, and — eventually — the U-cradle) fits into one physical station. This is the doc you read before ordering parts.

**MVP scope:** v1 = enclosure + camera + lighting + control + **feeding mechanism (device in → device out)** with **operator-driven manual flip** in the middle. v2 (deferred) = drop the U-cradle into the same enclosure to remove the operator from the capture loop. Items below are tagged `[v1]`, `[v2]`, or `[v1+v2]`.

> **Hot item — finalize today:** the feeding mechanism (in / out). Mechanism choice (conveyor / tray / drawer / slide / other) drives enclosure footprint and door geometry, so it must be locked before the enclosure is built. See the OPEN section below.

**Status:** First integration pass. Individual components are specced; integration decisions are flagged as **DECIDED** (locked), **RECOMMENDED** (my call, easy to flip), or **OPEN** (needs your input).

---

## The station, at a glance

A light-tight enclosure (~45 × 45 × 55 cm inside dimensions) containing:

- **Feeding mechanism** that transports the device in to the load position and out to the operator / sort area when grading is done. `[v1+v2]` **Mechanism TBD — finalize today.** Candidates: short bidirectional conveyor (in and out through the same opening), pull-out drawer / sliding tray, gravity slide with stop. Includes a **device-present sensor** (IR break-beam or microswitch) that tells the MCU the device has arrived at the load position.
- **Device load position** at the center.
  - `[v1]` Device sits on a flat, padded rest plate at the end of the feeding path. After the front-face capture pair, the operator opens the door, manually flips the device, closes the door, second capture pair runs.
  - `[v2 — deferred]` **U-cradle** holds the device stationary through an automated 180° flip. Same enclosure, same camera/lighting layout — drops in where the v1 rest plate sits. (Feeding mechanism is unchanged from v1.)
- **Camera** mounted directly above the device, pointing straight down. `[v1+v2]`
- **4 LED strips** at screen-plane height on all 4 sides for dark-field. `[v1+v2]`
- **Bright-field light panel** on the inner top surface (diffused, reused from Amazon tent). `[v1+v2]`
- **MOSFET + MCU** in a separate electronics compartment, controlling lighting + camera trigger + feeding mechanism actuator + device-present sensor (+ cradle motor in v2). `[v1+v2]`
- **Operator loading door** on the front (still needed in v1 for the manual mid-cycle flip). `[v1+v2]`

One device in → 4 captures (bright-field + dark-field on each face) → grade out. In v1 the operator flips the device between the two pairs; in v2 the cradle does it. The feeding mechanism handles the entry and exit in both phases.

---

## Unified BOM

Pulled from `lighting/README.md` + additions for the enclosure and control. **MVP v1** target is **~$250 total**; **MVP v2** adds the cradle and (optionally) its motor on top.

| Subsystem | Phase | Line items | Est. cost |
|---|---|---|---|
| **Enclosure** | v1 | 2020 extrusion frame + black-painted foamboard panels + hinges + magnetic door latch + flat rest plate for the device | **~$70** |
| **Feeding mechanism** *(finalize today)* | v1 | TBD until mechanism is chosen. Range: ~$20 (gravity slide + microswitch) → ~$60 (pull-out drawer with linear rail + microswitch) → ~$120 (small bidirectional belt conveyor + DC motor + driver + IR break-beam sensor). | **~$20–120** |
| **Dark-field lighting** | v1 | 4× LED strips, 4× diffusion-free mounts, matte-black felt liner, 4-channel MOSFET driver | **~$50** |
| **Bright-field lighting** | v1 | Reuse Amazon lightbox LEDs (already have), mount into top of enclosure | **~$0** |
| **Camera + lens** | v1 | USB machine-vision camera (Arducam / ELP) + 6 mm or 8 mm M12 lens | **~$80** |
| **Control** | v1 | ESP32 (or Arduino Uno), 12 V / 24 V PSU, wiring, small OLED status display, start button, door interlock switch | **~$50** |
| **U-cradle** *(deferred)* | v2 | 2020 extrusion, bearings, axle, waterjet arm plates, spring kit, silicone pads, handle | **~$200** |
| **Motorized cradle** *(deferred, optional within v2)* | v2 | NEMA 17 stepper + TMC2209 driver + shaft coupling + mount bracket | **~$50** |
| **Total — MVP v1 (operator manual flip + feeding)** | | | **~$270–370** |
| **Total — MVP v2 (manual cradle)** | | | **~$470–570** |
| **Total — MVP v2 (motorized cradle)** | | | **~$520–620** |

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
       │  │  v1: device on rest    │     (above device,  │
       │  │  plate, screen-up      │      pointing down) │
       │  │  v2 (deferred): U-cradle arms                │
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
        │         device on rest plate (v1)   │
        │         device in U-cradle (v2)     │
        │                                     │
        │    [v2] cradle axle through posts   │
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

### MVP v1 — operator manually flips between passes

| Step | Time | What happens |
|---|---|---|
| 1 | — | Operator places device on the **feeding mechanism** input (screen-up), presses Start |
| 2 | TBD | **Feed in.** Feeding mechanism transports the device to the load position. Device-present sensor fires → MCU confirms "device in place" |
| 3 | 0.2 s | Door interlock confirms closure; MCU starts pass A |
| 4 | 1 s  | **Bright-field LEDs ON**, camera captures frame `A_front` |
| 5 | 0.3 s | Bright-field OFF, **dark-field LEDs ON**, camera captures frame `B_front` |
| 6 | — | OLED prompts "FLIP DEVICE". Operator opens door, manually flips device to screen-down, closes door |
| 7 | 0.2 s | Door interlock confirms closure; MCU starts pass B |
| 8 | 0.3 s | **Bright-field LEDs ON**, camera captures `A_back` |
| 9 | 0.3 s | Dark-field LEDs ON, camera captures `B_back` |
| 10 | 2 s  | Host inference: 4 images → model → grade |
| 11 | — | Grade displayed on OLED |
| 12 | TBD | **Feed out.** Feeding mechanism transports the device to the operator / sort area. Device-present sensor clears → MCU returns to idle, ready for next device |

**Total: ~4 s automated capture + feed-in + feed-out + however long the operator takes to flip.** Throughput is operator-bound in v1 — that's deliberate. v1 is "remove the man from the *grading*", not from the loading or flipping.

### MVP v2 — cradle flips, no human hands during capture *(deferred)*

| Step | Time | What happens |
|---|---|---|
| 1 | — | Operator places device on the **feeding mechanism** input, presses Start |
| 2 | TBD | **Feed in.** Feeding mechanism transports the device into the U-cradle (or hands it off to the cradle's load position). Spring clamps it; device-present sensor fires |
| 3 | 0.2 s | Door interlock confirms closure; MCU starts sequence |
| 4 | 1 s  | Cradle already at 0° (rotation stop); **bright-field LEDs ON**, camera captures frame `A0` |
| 5 | 0.3 s | Bright-field OFF, **dark-field LEDs ON**, camera captures frame `B0` |
| 6 | 1 s  | Cradle rotates 180° (manual handle or stepper); settles at stop |
| 7 | 0.3 s | **Bright-field LEDs ON**, camera captures `A180` |
| 8 | 0.3 s | Dark-field LEDs ON, camera captures `B180` |
| 9 | 2 s  | Host inference: 4 images → model → grade |
| 10 | — | Grade displayed on OLED |
| 11 | TBD | **Feed out.** Cradle releases (or hands device back to feeding path); feeding mechanism transports the device to the operator / sort area |

**Total cycle: ~5 s automated capture + feed-in + feed-out + operator load (no flip).** Well under the 57 s budget in the original architecture.

---

## Electrical / control

**Single MCU (ESP32 recommended).** Handles:

- 4-channel MOSFET driver for LED banks (bright-field, dark-field × N, independent) `[v1+v2]`
- Camera trigger (GPIO pulse if camera supports hardware trigger; otherwise USB command from host PC) `[v1+v2]`
- Door interlock switch (GPIO, fail-safe: no capture if door open) `[v1+v2]`
- Start button + small OLED status display (also drives the "FLIP DEVICE" prompt in v1) `[v1+v2]`
- **Feeding mechanism** actuator + device-present sensor `[v1+v2]` — driver depends on the chosen mechanism (DC motor + H-bridge for a conveyor; stepper + driver for a drawer; nothing for a passive gravity slide). Sensor is an IR break-beam or microswitch on the GPIO.
- Stepper driver for motorized cradle — TMC2209 with 200-step/rev NEMA 17 `[v2 — deferred, optional within v2]`

**Power:** single 24 V / 5 A bench PSU, buck-converted to 12 V for LEDs and 5 V for MCU. Camera powered over USB.

**Host PC or Raspberry Pi** runs:
- Camera capture (USB)
- Model inference
- Grade display

MCU and host PC communicate over serial (USB CDC on the ESP32). MCU orchestrates the *physical* sequence, host handles *image processing*.

---

## Integration decisions

### DECIDED (locked)

- **Architecture:** fixed camera + dual-capture lighting + feeding mechanism + (eventually) U-cradle with 180° flip. Not robot-arm.
- **MVP split:** v1 ships **without** the U-cradle — operator manually flips between the two capture passes — but **with** a feeding mechanism (device in / device out). v2 drops the cradle into the same enclosure.
- **Feeding mechanism is in v1 scope.** Specific mechanism is being finalized today (see OPEN below).
- **Dual-capture:** bright-field + dark-field per device, per side.
- **Black everything inside** the enclosure. Mandatory for dark-field contrast.
- **Operator places device on the feeder; does not reach into the enclosure to load.** V1 still requires the operator to open the door for the mid-cycle manual flip — that's the only hands-in-enclosure step.

### RECOMMENDED (my call, flip if you want)

| Decision | Recommendation | Why |
|---|---|---|
| **Flip mechanism** | **Operator manual flip in v1**, U-cradle in v2 (deferred) | v1 ships in days, not weeks. Cradle is a known-good upgrade — design v1 around its eventual footprint. |
| **Cradle drive** *(v2)* | Manual handle when v2 starts | Simpler; spec already exists. Motorize later — same axle, same stops. ~$50 swap. |
| **Camera** | Arducam / ELP USB 1080p with M12 lens | Enough resolution for whole-device frame (~150 µm/px on a 6" phone at 28 cm). Industrial cameras are overkill until we know the pipeline works. |
| **Lens** | 6 mm M12 | Covers 12.9" iPad at 28 cm. |
| **Number of dark-field LEDs** | 4 (all 4 sides) | Covers all scratch orientations. ~$20 more than 2, worth it. |
| **Bright-field source** | Reuse Amazon lightbox LED strip panel | Already own it. Mount as diffused panel inside the enclosure top. |
| **Enclosure build** | 2020 extrusion frame + black foamboard panels | Cheap, modifiable, light-tight with felt gaskets. **Leave clear airspace and mounting points where the v2 cradle posts will go.** |
| **MCU** | ESP32 dev board | WiFi for debugging, 3.3 V, plenty of GPIO. Same board carries forward into v2. |
| **Host** | Laptop (dev) → Raspberry Pi 5 (production) | USB camera + basic inference; no GPU needed for a small classifier |

### OPEN (need your input before ordering)

1. **Feeding mechanism — finalize today.** Pick one and lock it; everything else (enclosure size, door geometry, MCU pin map, BOM) keys off this. Options to weigh:

   | Option | Approx. cost | Pros | Cons |
   |---|---|---|---|
   | **Gravity slide + microswitch stop** | ~$20 | Cheapest, no actuator, no power | Manual reset for "feed out"; only works one direction; tilt geometry intrudes into enclosure |
   | **Pull-out drawer / tray on linear rail** | ~$60 | Operator loads outside the enclosure, slides drawer in; positive stop; trivial to seal light-tight | Operator still pushes/pulls; not actuated unless we add a stepper |
   | **Bidirectional belt conveyor (in + out same opening)** | ~$120 | Closest to the universal-cellular-3d.html visualization; fully actuated; matches future production aesthetic | Most complex; needs DC motor + H-bridge + IR break-beam; light-tightness around belt opening is non-trivial |
   | **Other (your idea)** | — | — | — |

   Sub-decisions that follow from the choice: in/out path (same opening or opposite ends), device-present sensor (microswitch vs IR break-beam), how light-tightness is preserved at the feed opening.

2. ~~**Motorize the cradle or keep manual for V1?**~~ **Resolved by MVP split:** no cradle in v1. Decide manual-vs-motorized when v2 starts.

3. **Budget envelope.** v1 lands at ~$270–370 depending on feeding mechanism. v2 adds the cradle for another ~$200–250. Does that match the target?

4. **Device variety on day 1.** Are we optimizing for phones only, or does day-1 need to handle tablets too? Affects enclosure size, camera lens choice, feeding mechanism width, and (later) cradle pad groove.

5. **Bright-field inside the dark-field enclosure** — can we really reuse the Amazon tent LEDs in this form factor, or do we need to buy a dedicated diffused panel? Depends on how much we can disassemble the tent. ~$25 risk.

6. **Grade feedback UI.** Just show a letter on an OLED? Or a full screen with the annotated image? Full screen = ~$40 extra, better UX, more wiring. (In v1 the same display also drives the "FLIP DEVICE" prompt.)

---

## Build order (once parts are ordered)

Minimum-risk sequence — build one subsystem at a time, verify it works before moving on.

### MVP v1

0. **Finalize the feeding mechanism design** (gates everything below — see OPEN #1).
1. **Enclosure skeleton** — 2020 frame, no panels yet. Bare frame to mount everything. **Reserve the central footprint and side-panel pass-throughs the v2 cradle will need** (axle posts, handle exit slot). **Cut the feed-in / feed-out opening(s)** based on the chosen mechanism's geometry.
2. **Feeding mechanism** — build per the finalized design. Mount the device-present sensor at the load position. Verify the device arrives consistently (same X/Y, same orientation) across 50 trials before moving on.
3. **Device rest plate** at the end of the feeding path — flat black-silicone-padded plate at the load position. Sized for the largest day-1 form factor. (Replaced by the U-cradle in v2.)
4. **Camera + lens mount** — centered above the rest plate, adjustable height. Verify whole device fits frame in both screen-up and screen-down orientations.
5. **Panels + light-tight sealing** — black foamboard, felt gaskets on the door **and around the feed openings**.
6. **Bright-field lighting** — reuse Amazon tent LEDs on top inner surface, diffused.
7. **Dark-field lighting** — 4 LED strips at grazing angle on 4 sides. **Run the eyeball test inside the enclosure** before wiring MOSFETs.
8. **Electrical / MCU** — wire LEDs through MOSFETs, wire the feeding mechanism actuator + device-present sensor, test each channel independently, then integrate sequence firmware (including the operator "FLIP DEVICE" prompt and the feed-in / feed-out steps).
9. **Host software** — capture 4 frames across two operator-flipped passes, save with timestamps, feed to inference.
10. **End-to-end test** — one device, full cycle (feed in → captures → manual flip → captures → grade → feed out), manual inspection of output grade.

### MVP v2 *(deferred)*

1. **U-cradle build** — follow `cradle-build-spec.md` to the letter (to be reinstated). Tune clamp force with fish scale. Tune rotation stops.
2. **Mount cradle inside enclosure** — replaces the v1 rest plate. Verify the manual handle exits through the pre-cut side-panel slot cleanly.
3. **Camera registration check** — 50 cycles at 0° ↔ 180°, target a few pixels of drift or less.
4. **Update firmware** — drop the "FLIP DEVICE" prompt; insert the cradle-rotate step. Same lighting / camera / inference path.

---

## What this does NOT include

### Out of MVP v1 (and explicitly v2 scope or later)

- **Automated flip mechanism (U-cradle).** v2.
- **Motorized cradle drive.** v2 (and optional even within v2 — manual handle ships first).

### Out of both MVP v1 and v2

- **Autonomous device feeder magazine / hopper.** v1 feeding mechanism is single-device per cycle — operator places one device on the feeder per cycle. A multi-device hopper that auto-loads the feeder is out of scope.
- **Active reject / sort bins** post-grading. The feeding mechanism delivers every device to the same exit; operator hand-sorts based on the displayed grade. Powered sort gates are out of scope.
- **Production enclosure aesthetics.** Looks homemade. Industrial design comes after the pipeline is validated.
- **Cloud sync / grading logs / audit trail.** Local JSON log for now; cloud later.

---

## Related docs

- `cradle-build-spec.md` — the flip-mechanism detail (MVP v2; currently absent from working tree, to be reinstated when v2 starts)
- [`../lighting/README.md`](../lighting/README.md) — lighting theory + eyeball test
- [`../lighting/dark-field-setup.html`](../lighting/dark-field-setup.html) — lighting visualization
- [`../grading-criteria/README.md`](../grading-criteria/README.md) — what the station is grading against
- [`../software/README.md`](../software/README.md) — what runs on the host
