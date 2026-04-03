# Flip Mechanism MVP — Final Spec

## The Design: Sandwich Flip

Device sits screen-up on a soft silicone pad. A matching top pad descends, sandwiches the device, the whole thing rotates 180°, top pad lifts. Done.

## Why Sandwich

- Works for every device size without adjustment — pads are bigger than the biggest device
- No adaptive-width mechanism needed (side-clamp requires one)
- Camera bumps sink into the soft silicone — device sits flat
- Cracked screens, foldables, tablets — all handled by the same pads, same force, same rotation

## Orientation

Screen up. Always. Operator loads it naturally, screen gets photographed first before anything touches it, camera bump sinks into the bottom pad.

## Capture Sequence

1. Device enters, sits screen-up on bottom pad
2. Top camera shoots front face (through aperture hole in top diffuser)
3. 4 edge cameras shoot all edges simultaneously (through aperture holes in side/back diffusers)
4. Top pad descends, sandwiches device (~20N force via spring)
5. Rotate 180° over ~1.5 seconds
6. Upper pad lifts (original bottom pad, now on top after flip)
7. Top camera shoots back face
8. Device exits to sorting

~10 seconds per cycle. Budget is 57 seconds. Plenty of margin.

## Pads

- Material: Silicone, Shore 20-30A (soft phone case softness)
- Thickness: 8-10mm
- Size: 300 x 230mm (covers iPad Pro 12.9" with margin)
- Backed by 6mm aluminum plate
- Both pads identical and swappable

## Rotation

- Horizontal center axis, parallel to device long edge
- NEMA 23 stepper + 5:1 planetary gearbox
- Trapezoidal velocity profile (smooth accel/decel)
- Rotary encoder confirms 0 and 180 positions
- Sweep radius at 90°: ~117mm (well within 32" box interior)

## Top Pad Actuator

- Lead screw or pneumatic cylinder
- 50mm travel (handles 6mm thin iPad to 16mm folded Z Flip)
- Spring between actuator and pad — provides consistent 20N regardless of device thickness

## Physics Check

Worst case: iPad Pro 682g at 90° rotation.
- Gravity pulling sideways: 6.7N
- Friction from two silicone pads at 20N clamp: ~20N
- 3x safety margin. It holds.

---

## Enclosure: Takerers LB12 Lightbox (Prototype Phase)

32" × 32" × 32" (813mm cube) fabric tent lightbox. Used for prototype and data collection. Final production station will use a custom rigid enclosure with the same internal layout.

**Specs:**
- 3 LED bar panels (70 LEDs each, 210 total), 5600K, CRI 95+
- 10-100% stepless dimming, 360° rotatable bars
- Interior: silver reflective fabric
- Front face: open shooting window (device entry/exit)
- Included: 1 fabric diffuser, 5 backdrops, brightness dimmer

**The lightbox is just a light-controlled tent.** It cannot support motors, bearings, or steel shafts. All mechanical hardware mounts to an internal rigid subframe.

## Internal Rigid Subframe

- **Material:** 2020 aluminum extrusion + T-nuts/brackets
- **Purpose:** structural skeleton inside the lightbox — holds shaft bearings, cameras, diffuser panels, actuator
- **Shape:** rectangular frame sitting on lightbox floor
- **Mounting points:** pillow block bearings (left/right), camera brackets (5 positions), diffuser panel standoffs (3 panels)
- The subframe is entirely matte black (anodized or painted) to minimize reflections

## Anti-Reflection: Cameras Behind Diffuser Panels

**Problem:** Dark phone screens are mirrors. Any visible hardware (cameras, brackets, motor) reflects off the screen and appears in photos. The AI model would train on camera reflections — corrupting grading accuracy.

**Solution:** All 5 cameras mount BEHIND frosted acrylic diffuser panels, shooting through small aperture holes (~18mm diameter). From the device's perspective:
- It sees uniform white light from the diffuser surface
- The camera lens is a tiny dark dot surrounded by bright uniform light
- Cross-polarization (CPL on lens, crossed 90° to polar film) kills the residual specular reflection of even that dot
- **Result: zero hardware reflections in photos**

**Camera space:** Pi HQ module (38×38×20mm) + 6mm lens (~30mm) = ~50mm depth behind diffuser. Cameras sit between the LED bars and the diffuser panel.

## Lighting Stack (per wall: left, right, top)

Order matters — polarize AFTER diffusion, not before:

```
FABRIC WALL
  │
  ├── LED bar (velcro to fabric, ~15mm)
  │
  ├── AIR GAP (~35mm) ← cameras mount here, behind diffuser
  │
  ├── DIFFUSER PANEL (frosted acrylic, 3-5mm)
  │
  ├── POLARIZING FILM (0.19mm, on outer face of diffuser)
  │
  └── → INTERIOR (device is here)
```

Total wall stack depth: ~55-60mm per side.
Effective interior between left/right diffusers: 813mm - 2×60mm ≈ **690mm (27")**

**Why this order:**
- LED → diffuser: point-source LEDs spread into uniform wash
- Diffuser → polar film: light is already uniform, then gets linearly polarized
- If polar film were before diffuser: diffusion would randomize polarization direction → cross-polar setup fails

## Polarizing Film

- 3 sheets, 20 × 30cm each (7.8" × 11.8"), 0.19mm thick
- Linear polarizer, >99.9% efficiency, 400-700nm
- Non-adhesive — held to diffuser face by clips or tape at edges
- Total coverage: 1,800 cm²
- Required coverage: ~20×30cm zone on each of 3 diffuser panels = 1,800 cm² (just enough if placed strategically in the center zones facing the device)
- If full panel coverage needed: order 1-2 additional sheets

## Diffuser Panels

- **Material:** frosted/opal acrylic, 3mm thick
- **Size:** ~30 × 30cm per wall (3 panels: left, right, top)
- **Purpose:** spread LED point sources into uniform light wash
- **Camera apertures:** ~18mm holes drilled at camera positions
- **Mounting:** standoffs from subframe, ~55mm offset from fabric wall

## Camera Positions (5 cameras)

All cameras behind diffuser panels, all shooting through aperture holes.

| Camera | Diffuser | Direction | Notes |
|--------|----------|-----------|-------|
| Top | Ceiling panel | Straight down | Primary camera — shoots front face and back face |
| Left edge | Left wall panel | Inward at device left edge | Sees left side (buttons, SIM tray) |
| Right edge | Right wall panel | Inward at device right edge | Sees right side (buttons) |
| Top edge | Back wall panel (upper) | Forward-down at device top edge | Sees top edge |
| Bottom edge | Back wall panel (lower) | Forward-down at device bottom edge | Sees charging port, speakers |

## Clearance Math (Real Dimensions)

- Box interior: 813mm cube
- Wall stack per side: 60mm
- Interior between left/right diffusers: ~690mm
- Interior below top diffuser: ~750mm
- Flip sweep radius: ~117mm (pad 230mm/2 = 115mm + sandwich thickness)
- Clearance from flip to left/right diffuser: 690/2 - 117 = **228mm** ✓
- Clearance from flip to top diffuser: 750/2 - 117 = **258mm** ✓ (if axis centered)
- No bottom diffuser — only left, right, top walls have lighting

## Frame

- 2020 aluminum extrusion subframe (matte black)
- 12mm steel shaft through sealed pillow block bearings
- Bearings mount to vertical extrusion uprights
- Naturally balanced (symmetric pads)
- All visible metal: matte black anodized or painted

## Devices Covered

| Device | Why it works |
|--------|-------------|
| Standard phones | Camera bump sinks into pad, flip holds easily |
| Large tablets | Pads sized for iPad Pro, force margin is fine |
| Foldables (folded) | Extra thickness handled by actuator travel range |
| Foldables (unfolded) | Soft pad conforms to hinge crease |
| Curved-edge screens | Pad contacts flat center, curves hang free |
| Cracked/broken devices | Friction-based hold, not vacuum — doesn't care |

## BOM (Flip Mechanism + Station Interior)

| Part | Est. Cost |
|------|-----------|
| 2× silicone pad sheet (cut to size) | $30 |
| 2× aluminum backing plate 300×230×6mm | $40 |
| NEMA 23 stepper + 5:1 gearbox | $65 |
| Stepper driver (TMC2209 or similar) | $15 |
| Lead screw actuator (top pad, 50mm stroke) | $35 |
| 12mm steel shaft + 2× pillow block bearings | $25 |
| Rotary encoder | $15 |
| 2020 aluminum extrusion subframe + brackets | $60 |
| 3× frosted acrylic diffuser panels (30×30cm) | $20 |
| Compression spring (force control) | $5 |
| Matte black paint / anodizing | $10 |
| **Total** | **~$320** |
