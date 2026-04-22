# Pivoting U-Cradle — Build Spec

**Internal build reference — AI grading station.** Canonical flip-mechanism spec. Source: `cradle_build_spec.docx` (kept alongside this file).

Figure references (*Figure 1 — front view, gray = fixed frame, colored = rotating assembly; Figure 2 — order of parts along the axle, left-bearing to handle*) are in the docx.

---

## Concept

Two arms grip the device by its **edges** (not its faces). The arm pair rotates on a single axle — 0° captures one side, 180° captures the other. One arm is locked to the axle, the other rides a linear bushing and is spring-loaded toward the fixed arm. To load: pull the sliding arm outward, drop the device in, release — spring clamps it.

Because the arms grip edges only, both faces stay fully exposed to the cameras. No open-close cycle needed between front and back captures.

---

## Axle stackup

The non-obvious part is the sliding arm. One arm is locked to the axle with a set screw (fixed). The other arm rides on a linear bushing (LM8UU) and slides freely along the axle. A compression spring between the sliding arm and a set-screwed stop collar pushes the sliding arm toward the fixed arm, clamping the phone.

**Order along the axle (left-bearing → handle):**
E-clip → fixed arm (set-screw onto flat) → sliding arm on bushing → spring → stop collar (set-screw onto second flat) → E-clip → far bearing → handle knob.

---

## Bill of materials

All off-the-shelf. Total **~$150–250** before tax / shipping. No machining required if arms are waterjet.

| Qty | Part | Spec | Source | ~Cost |
|---|---|---|---|---|
| 1 | Aluminum extrusion (base) | 2020, 500 mm | Amazon / Misumi | $8 |
| 2 | Aluminum extrusion (posts) | 2020, 250 mm | Same | $10 |
| 1 | Aluminum extrusion (cross-brace) | 2020, 300 mm, optional | Same | $6 |
| 6 | 2020 inside corner brackets | Standard with M5 hardware | Amazon | $12 |
| ~20 | M5 T-slot nuts + bolts | For 2020 extrusion | Amazon | $10 |
| 2 | Pillow-block bearing | KP08 or UCFL001, 8 mm bore | VXB / Amazon | $12 |
| 1 | Linear bushing | LM8UU, 8 mm ID (for sliding arm) | Amazon | $3 |
| 1 | Axle shaft | 8 mm stainless, 300 mm, h6 tolerance | McMaster 1346K18 | $10 |
| 1 | Arm-plate pair | 180 × 40 × 4 mm, aluminum 6061, waterjet | SendCutSend (your DXF) | $30 |
| 1 | Compression-spring kit | 6 mm ID, rates 500 / 750 / 1000 N/m | McMaster 1692K kit | $15 |
| 2 | Shaft collar, set-screw | 8 mm bore, steel | Amazon | $6 |
| 2 | E-clip / retaining ring | For 8 mm shaft | Amazon | $3 |
| 1 | Silicone rubber sheet | 3 mm thick, 70 A shore, **black** | Amazon / McMaster | $12 |
| 1 | Contact cement | Small tube (DAP Weldwood or equiv.) | Hardware store | $5 |
| 1 | Handle knob | M6 thread, ~40 mm diameter, rubber | Amazon | $8 |
| misc | M3 screws + set screws | For arm-to-axle lock, collar set screws | On hand | — |

---

## Tools

- **Drill press (required — for coaxial bearing bores).** Hand-drilled bores will not be coaxial and the build will fail.
- M3 tap + handle
- Hacksaw or band saw for extrusion
- Dremel with cut-off wheel for axle flats
- Allen keys 2 / 2.5 / 3 / 4 mm
- Digital calipers
- Fish scale or 0–30 N force gauge (for tuning clamp force)

---

## Build sequence

### Phase 1 — Frame

- Cut extrusion to length on the saw. Debur cut ends with a file.
- **Critical:** clamp the two posts face-to-face so their top ends align exactly. Drill the bearing clearance hole through **both posts in a single pass** on the drill press. This is how you guarantee the bearings end up coaxial. Separate drilling always fails.
- Assemble frame: base + 2 posts with corner brackets. Add cross-brace between posts if rigidity is lacking. Check posts are parallel and vertical with a square.
- Press-fit bearings into post bores. Tap home with a soft mallet and a wood block. Do not force them — if they won't go, the bore is undersized; ream 0.05 mm and retry.

### Phase 2 — Rotating assembly

- **Prepare the axle.** Measure 30 mm in from each end, then measure the position where each set screw will land (fixed-arm center and stop-collar center). File a flat about 10 mm long at each of those two positions using a Dremel cut-off wheel followed by a bastard file until the flat is mirror-flat. Set screws MUST bite on a flat, not a round surface, or they slip under torque.
- **Drill arm plates.** 8 mm center bore for axle. 90° to that: M3 through-hole, tapped, positioned to intersect the axle flat when assembled (fixed arm only). For the sliding arm, instead of a tapped hole, press-fit the LM8UU bushing into an enlarged center bore (typically 15 mm).
- **Cut rubber pads** to size (roughly 80 × 15 mm strips). Contact-cement to the inner face of each arm. Let cure 30 minutes. Press a retention groove into each pad with a heated metal edge (e.g., a heated flat screwdriver tip) — groove width = device edge thickness + 0.5 mm, depth ~2 mm.
- **Paint both arm plates matte black** and bake at 80 °C for 30 minutes. Any gloss kicks specular highlights in polarized imaging.
- **Dry-assemble on the axle:** E-clip → fixed arm (set-screw onto flat) → sliding arm on bushing → spring → stop collar (set-screw onto second flat) → E-clip. Push the sliding arm in and release; it should slide back freely under spring force.

### Phase 3 — Integration

- Slide the fully-assembled axle through both bearings from one side. Goes in with the sliding-arm subassembly first; the fixed arm goes on last once the axle is through.
- Thread the handle knob onto the far axle end. Use blue threadlocker. Knob must be finger-tight without tools.
- **Add rotation stops:** a short dowel pin or bolt in the axle that hits a fixed tab on the post face at 0° and at 180°. Without this, the operator never lands at the same angle twice and your camera registration drifts.

### Phase 4 — Tune and verify

- **Measure clamp force.** Hook a fish scale on the sliding arm and pull outward until it just separates from the phone. Target **15–20 N**. Adjust by moving the stop collar (more inward = more preload).
- **Load test:** 12.9" iPad Pro, cradle inverted, hold 60 s, bang the bench, tilt the whole station 15–20°. iPad must not move. If it slips, go stiffer spring or deeper groove.
- **Integrate with the imaging station.** Set camera frame on the cradle in both 0° and 180° positions. Verify registration repeatability within a few pixels over 50 cycles.

---

## Critical details that will kill the build if wrong

- **Coaxial bearing bores.** Drill both posts clamped together. Never separately.
- **Axle flats.** Flats must align with set screws when arms/collar are installed. Mark flat orientations before torquing.
- **Sliding arm must not bind.** After assembly, push the arm inward against the spring and release. It has to return smoothly without stick-slip. If it binds, the bushing is not coaxial with the bearings — open the bushing bore 0.1 mm or shim the bearings.
- **Rotation stops.** Mandatory. Without repeatable hard stops the camera will not register consistently pass to pass.
- **Matte black everywhere.** Arms, handle, visible hardware. Black pads, black arms, black frame if reachable. Gloss destroys cross-polarized imaging.
- **Do not use oil on the bushing or bearings.** Oil attracts dust and dust ends up in imaging. Silicone grease, sparingly.

---

## Tuning targets

| Parameter | Target |
|---|---|
| Clamp force | **15–20 N** measured at the pad (use a fish scale on the sliding arm) |
| Spring rate | Start at **750 N/m**. Go to 1000 N/m if iPad slips, 500 N/m if phones are pinched too hard. |
| Preload compression | **20–30 mm** at the loaded position (adjust by moving the stop collar) |
| Pad material | **Black silicone, 70 A shore, 3 mm sheet**, contact-cemented to arm inner face |
| Pad groove | **2 mm deep × device-edge-thickness + 0.5 mm wide**, press with hot metal edge |
| Rotation speed | **~1 s per 180°**, no reason to go faster |
| Rotation stops | Hard mechanical stops at 0° and 180° — mandatory for camera registration |

---

## Gotchas

- Set screw on a round shaft will slip — **file the flat first**, always.
- Don't overcompress the spring. Check solid height in the spring spec; leave at least **3 mm free travel** at max compression or the coils bind and destroy the spring.
- Spring should be a close fit around the axle — **6 mm ID on 8 mm shaft is wrong**; use ~8.5 mm ID. Too loose and it migrates sideways and jams.
- **Knob threadlocker is non-negotiable.** It will walk off under repeated rotation otherwise.
- Budget a **full afternoon for tuning**. The build takes less time than getting spring rate, preload, and groove depth right on the first device-class swap.
- **Keep one spare spring of each rate.** You will want to swap during tuning.
