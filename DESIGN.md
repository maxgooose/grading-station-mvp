# Automated Device Cosmetic Grading Station — Design Document

> This is the source of truth for the station design. If you're a new agent picking up this project, read this file first.

## What This Is

A station that photographs used phones and tablets from all angles, then uses an AI model to grade them A/B/C cosmetically. Replaces manual human inspection at Universal Cellular Inc. (~500 devices/day).

**The person's only job**: load devices onto a tray. Everything else is automated.

## How It Works — The Full Cycle (~12 seconds)

```
1. Device slides in through front opening → rests on fixed support rails
2. C-bracket is retracted to the side — nothing blocks the cameras
3. Top camera shoots the front screen (through aperture in ceiling diffuser)
4. 4 edge cameras fire simultaneously (left, right, top edge, bottom edge)
5. C-bracket slides to center, pads clamp the device (~20N)
6. Entire C-bracket rotates 180° — device is now face-down
7. C-bracket opens and retracts to the side again
8. Top camera shoots the back panel
9. Device slides back out the same front opening → sorted into A/B/C bin
```

Single opening. Same mechanism every cycle. No alternating parts.

---

## The Station — Physical Layout

### Enclosure

**Prototype phase:** Takerers LB12 lightbox — 32"×32"×32" (813mm cube) fabric tent.
- 3 LED bar panels (210 LEDs total), 5600K, CRI 95+, stepless dimming
- Fabric walls with silver reflective interior
- Front face has shooting window (our device entry/exit point)
- The lightbox is just a light-controlled tent — it holds no mechanical load

**Production phase:** Custom rigid enclosure (aluminum extrusion or sheet metal) with the same internal layout.

### Internal Rigid Subframe

The fabric lightbox can't support motors or shafts. Everything mechanical mounts to:

- **Material:** 2020 aluminum extrusion + T-nuts/corner brackets
- **Shape:** rectangular frame sitting on the lightbox floor
- **Matte black** (anodized or painted) to eliminate reflections
- **Mounts:** pillow block bearings, camera brackets, diffuser panel standoffs

### Fixed Support Rails

Two thin metal rods spanning the subframe horizontally, at the center height. The device rests on these rails during photography — **not on the pads**. This is critical: the pads are only for clamping during the flip. The rails keep the device in position while the C-bracket is retracted.

---

## The C-Bracket Flip Mechanism

This is the core mechanical innovation. A C-shaped bracket carries both the top and bottom pads as one unit.

### Why a C-Bracket

The top camera shoots straight down at the device. Any pad above the device blocks that shot. A single retractable top pad creates an alternating problem after the flip (the new top pad has no retraction mechanism). The C-bracket solves this:

- Both pads are on one bracket
- The entire bracket slides sideways along a rail to fully clear the camera's field of view
- After flipping, the bracket retracts the same way — works identically regardless of orientation
- No alternating parts, no asymmetric mechanisms

### C-Bracket Structure

```
Side view (bracket centered):

      LEAD SCREW
          │
       [SPRING]
          │
    ┌── TOP PAD (silicone + aluminum) ──┐
    │                                    │  ← C-bracket arms
    │         [device clamped]           │     (steel or aluminum)
    │                                    │
    └── BOTTOM PAD (silicone + aluminum)─┘
```

- **Arms:** two vertical members connecting top and bottom pad mounting plates
- **Top pad:** adjustable height via lead screw (closes the gap to sandwich the device)
- **Bottom pad:** fixed to the bracket base
- **Slide rail:** horizontal, parallel to the rotation shaft axis. Bracket slides along this to retract/center.

### Pads

- **Material:** Silicone, Shore 20-30A (soft phone case softness)
- **Thickness:** 8-10mm
- **Size:** 310 × 230mm (covers iPad Pro 12.9" with margin)
- **Backing:** 6mm aluminum plate behind each pad
- **Both pads identical and swappable**
- Camera bumps sink into the soft silicone — device sits flat

### Lead Screw Actuator (Gap Adjustment)

- Mounted on the C-bracket, drives the top pad up/down
- **50mm travel** — handles 6mm thin iPad to 16mm folded Z Flip
- Compression spring between screw and pad provides consistent **~20N** clamping force regardless of device thickness

### Rotation

- **Axis:** horizontal, at center of the C-bracket, parallel to device long edge
- **Motor:** NEMA 23 stepper + 5:1 planetary gearbox
- **Profile:** trapezoidal velocity (smooth accel/decel)
- **Confirmation:** rotary encoder at 0° and 180°
- **Shaft:** 12mm steel through sealed pillow block bearings mounted to subframe uprights
- **Sweep radius at 90°:** ~117mm
- **Clearance to nearest diffuser panel:** 228mm (plenty)

### Physics Check

Worst case: iPad Pro (682g) at 90° rotation.
- Gravity pulling sideways: 6.7N
- Friction from two silicone pads at 20N clamp: ~20N
- **3× safety margin. It holds.**

---

## Lighting System

### The Problem

Glass-backed devices (iPhone 8+, Galaxy S series) create glare that hides scratches. Different device colors change how damage looks. We need consistent, glare-free illumination.

### Cross-Polarized Setup

Two polarizers crossed at 90°:
1. **Polarizing film** on the light source (outer face of diffuser panels)
2. **CPL filter** on each camera lens, rotated 90° to the film

Effect: kills specular reflections (glare) while preserving diffuse reflections (scratches, dents, scuffs). The camera sees surface damage, not mirror reflections.

### Lighting Stack (per wall: left, right, top ceiling)

Order matters — **polarize AFTER diffusion**:

```
FABRIC WALL (lightbox)
  │
  ├── LED bar (velcro to fabric, ~15mm thick)
  │       70 LEDs per bar, 5600K, CRI 95+
  │
  ├── AIR GAP (~35mm)
  │       ← cameras mount here, behind the diffuser
  │
  ├── DIFFUSER PANEL (frosted/opal acrylic, 3-5mm)
  │       Spreads point-source LEDs into uniform wash
  │
  ├── POLARIZING FILM (0.19mm, on outer face of diffuser)
  │       Linear polarizer, >99.9% efficiency, 400-700nm
  │
  └── → INTERIOR (device is here)
```

**Total stack depth:** ~55-60mm per wall
**Effective interior:** 813mm - 2×60mm ≈ **690mm (27")**

**Why this order:** If polarizing film goes before the diffuser, diffusion randomizes the polarization direction and cross-polar setup fails. Film must be after diffusion.

### Diffuser Panels

- **Material:** frosted/opal acrylic, 3mm thick
- **Size:** ~30×30cm per panel (3 panels: left, right, top)
- **Camera apertures:** ~18mm holes drilled at each camera position
- **Mounting:** standoffs from subframe, ~55mm offset from fabric wall

### Polarizing Film

- 3 sheets, 20×30cm each (7.8"×11.8"), 0.19mm thick
- Linear polarizer, >99.9% efficiency, 400-700nm, non-adhesive
- Held to diffuser face by clips or tape at edges
- Total coverage: 1,800 cm² — just enough for center zones of 3 panels
- May need 1-2 additional sheets for full coverage

---

## Camera System

### Anti-Reflection Design

**Problem:** dark phone screens are mirrors. Any visible camera, bracket, or motor reflects off the screen and appears in photos. The AI model would train on those reflections — corrupting grading accuracy.

**Solution:** all 5 cameras mount **behind** frosted acrylic diffuser panels, shooting through small aperture holes (~18mm). From the device's perspective:
- It sees only uniform white light from the diffuser surface
- The lens is a tiny dark dot surrounded by bright light
- The CPL filter on the lens kills even that residual dot's specular reflection
- **Result: zero hardware reflections in photos**

### Camera Hardware

- **5× Raspberry Pi HQ Camera Modules** (12.3MP, Sony IMX477, CS-mount)
- **5× 6mm CS-mount wide angle lenses** — wide angle for close-range capture
- **5× Raspberry Pi 4 Model B (1GB)** — one per camera, 1GB sufficient for capture only
- **5× CPL (Circular Polarizer) filters** — mounted on each lens
- **1× 8-port gigabit ethernet switch** — connects all Pis to main workstation

### Camera Positions

All behind diffuser panels. All shooting through ~18mm aperture holes.

| Camera | Behind | Direction | What it captures |
|--------|--------|-----------|-----------------|
| **Top** | Ceiling diffuser | Straight down | Front screen (step 3) and back panel (step 8) |
| **Left edge** | Left wall diffuser | Inward | Left side — volume buttons, SIM tray |
| **Right edge** | Right wall diffuser | Inward | Right side — power button |
| **Top edge** | Back wall diffuser (upper) | Forward-down | Top edge of device |
| **Bottom edge** | Back wall diffuser (lower) | Forward-down | Charging port, speakers, mic |

### Camera Space

Pi HQ module (38×38×20mm) + 6mm lens (~30mm) = ~50mm depth. Cameras sit in the air gap between LED bars and diffuser panels.

---

## AI Model

- **Architecture:** EfficientNet-B0, fine-tuned on captured dataset
- **Parameters:** 5.3M — small enough for fast inference, accurate enough for 3-class
- **Input:** 224×224 resized images
- **Inference:** each of the 6 images classified independently, then aggregated via confidence-weighted voting
- **Output:** Grade (A, B, or C) + confidence score
- **Low-confidence:** devices below threshold flagged for human review
- **Speed:** ~2 seconds per device on GPU, ~15 seconds on CPU
- **Training data:** 20,000 pre-labeled devices × 6 images each = ~120K training images
- **Target accuracy:** 90%+ on validation set

---

## Grading Criteria

| Grade | Description |
|-------|-------------|
| **A (Excellent)** | No visible scratches, dents, or wear. Screen flawless. Appears new/like-new. |
| **B (Good)** | Minor cosmetic wear — light scratches on back/edges, small scuffs. Screen good, no cracks. |
| **C (Fair)** | Visible scratches, dents, or chips on body and/or screen. Noticeable damage but functional. |

---

## Devices Supported

| Device | How it's handled |
|--------|-----------------|
| Standard phones | Camera bump sinks into silicone pad |
| iPads (up to 13" Pro) | Pads sized to cover with margin |
| Samsung Galaxy phones | Glass backs work well with cross-polarization |
| Foldables (folded) | Extra thickness handled by 50mm actuator travel |
| Foldables (unfolded) | Soft pad conforms to hinge crease |
| Curved-edge screens | Pad contacts flat center, curves hang free |
| Cracked/broken devices | Friction-based hold — doesn't care about surface condition |
| Mixed colors | Cross-polarization + exposure normalization handles all colors |

---

## Throughput

| Step | Time |
|------|------|
| Device enters onto rails | ~2s |
| Front + edge capture | ~2s |
| C-bracket slide in + clamp | ~1.5s |
| 180° flip | ~1.5s |
| C-bracket open + retract | ~1.5s |
| Back capture | ~1s |
| Device exits to sort bin | ~2s |
| AI inference (parallel) | ~2s |
| **Total per device** | **~12s** |
| **500 devices** | **~1.7 hours** |

Budget was 57 seconds per device. We're at 12. Plenty of margin.

---

## Clearance Math

- Box interior: 813mm cube
- Wall stack per side: ~60mm
- Interior between left/right diffusers: ~690mm
- C-bracket pads width: 310mm
- Flip sweep radius at 90°: ~117mm
- **Clearance from flip to left/right diffuser: 690/2 - 117 = 228mm** ✓
- **Clearance from flip to top diffuser: ~258mm** ✓
- No bottom diffuser — only left, right, top walls have lighting

---

## BOM

### Flip Mechanism + Station Interior

| Part | Est. Cost |
|------|-----------|
| 2× silicone pad sheet (cut to size) | $30 |
| 2× aluminum backing plate 310×230×6mm | $40 |
| C-bracket arms + slide rail hardware | $45 |
| NEMA 23 stepper + 5:1 planetary gearbox | $65 |
| Stepper driver (TMC2209 or similar) | $15 |
| Lead screw actuator (50mm stroke) | $35 |
| 12mm steel shaft + 2× pillow block bearings | $25 |
| Rotary encoder | $15 |
| 2020 aluminum extrusion subframe + brackets | $60 |
| 3× frosted acrylic diffuser panels (30×30cm) | $20 |
| Compression spring | $5 |
| Matte black paint / anodizing | $10 |
| Fixed support rails + mounting hardware | $15 |
| **Mechanism subtotal** | **~$380** |

### Camera + Lighting (Phase 1)

| Part | Est. Cost |
|------|-----------|
| Takerers 32" lightbox (LEDs included) | $65 |
| Polarizing film sheets (3-pack) | $15 |
| 5× Raspberry Pi HQ Camera Module | $250 |
| 5× 6mm CS-mount lens | $125 |
| 5× Raspberry Pi 4 (1GB) | $175 |
| 5× USB-C power supply | $50 |
| 5× 32GB MicroSD cards | $40 |
| 5× CSI ribbon cables | $25 |
| 5× CPL filters | $60 |
| 8-port gigabit ethernet switch | $20 |
| 6× Cat6 cables (1m) | $18 |
| **Camera subtotal** | **~$843** |

### **Estimated total: ~$1,223**
### With 15% buffer: ~$1,400

---

## Software Pipeline (Not Yet Built)

1. **Capture service** — triggers all 5 cameras simultaneously, saves images with device ID
2. **Preprocessing** — auto-crop, exposure normalization, white balance, resize to 224×224
3. **Inference server** — runs EfficientNet-B0 on GPU, returns grade + confidence
4. **Operator dashboard** — real-time grade result, daily throughput, grade distribution, flagged-for-review rate
5. **API integration** — pushes grade + images to WholeCellIO (existing inventory system)
6. **Image archival** — stores all images with metadata for retraining

---

## Key Design Decisions (and why)

| Decision | Rationale |
|----------|-----------|
| C-bracket (not single retractable pad) | After flip, the new top pad also needs to retract. C-bracket moves both pads as one unit — same mechanism every cycle. |
| Device on fixed rails (not on pads) | Pads must fully retract to clear camera view. Device needs to stay in place during photography. |
| Cameras behind diffusers | Dark screens are mirrors. Any visible hardware corrupts training data. |
| Polarize after diffusion | Diffusing after polarization randomizes polarization direction — defeats cross-polar setup. |
| Cross-polarization (not standard diffused light) | Glass-backed devices create glare that hides scratches. Cross-polar kills glare. |
| Single front opening (not in/out on opposite sides) | One hole in the lightbox is simpler than two. Same slot for entry and exit. |
| EfficientNet-B0 (not heavier model) | 5.3M params is enough for 3-class grading. Fast inference, cheap to retrain. |
| 6 photos (not 10+) | Front, back, 4 edges covers everything that affects grade. More angles add complexity without improving accuracy. |
| Silicone pads (not vacuum or clamps) | Works for every device shape/condition. Camera bumps sink in. Cracked screens don't matter. |
| Lightbox for prototype, custom enclosure for production | Validates lighting and capture before investing in custom metalwork. |

---

## Open / Not Yet Designed

- [ ] Feed mechanism — how devices get loaded onto rails (spring pusher, gravity slide, or small conveyor)
- [ ] Sort mechanism — how devices route to A/B/C bins after exiting
- [ ] Software pipeline — capture, preprocessing, inference, dashboard
- [ ] API integration spec with WholeCellIO
- [ ] C-bracket slide rail motor/actuator selection (stepper, servo, or pneumatic)
- [ ] Exact support rail dimensions and device centering mechanism

---

## Files in This Repo

| File | Purpose |
|------|---------|
| `DESIGN.md` | This file — full system design, the source of truth |
| `flip-mechanism-mvp.md` | Earlier flip mechanism spec (partially outdated — DESIGN.md supersedes for the C-bracket design) |
| `station-visualization.html` | Interactive animated visualization of the full capture sequence |
