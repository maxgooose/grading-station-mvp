# Camera Placement — 5-Camera Layout (MVP v1)

**Date:** 2026-06-08 · **Status:** ⚠️ **Mount scheme SUPERSEDED 2026-06-11** — kept for the FOV math and capture-state definitions.

> **Superseded (2026-06-11):** this paper spec (side cams mid-panel ~4" up, tilted ~40–50° down) and the corner-mount work were done in parallel sessions. The **build plan is corner mounts**: ELP-USBFHD06H-L36 boards on blocks bridging each corner at ~45°, lens center 0.75" up, aimed level at the stage crosshair, ~7.3" working distance, barrel refocused to ~5.5" — see the 2026-06-10/11 entries in [`README.md`](README.md). The Step-1 FOV math below was independently confirmed (~73–74° HFOV; the boards are ELP-USBFHD06H-L36, not generic IMX323 modules). The mid-wall mount table (Steps 2–4) and the diagrams are historical. Note the corner plan also changes the lighting interaction: the corner cams sit **low (lens ~0.75")**, in the same band as the grazing strips, so the "cams high / strips low, no collision" separation below no longer holds — strips get placed after the cameras, out of their FOVs.

How the five cameras are positioned inside the 12" cube and why. This **supersedes the "single camera mounted directly above" description** in [`station-integration.md`](station-integration.md) — that doc predates the side-camera decision.

---

## The five cameras

| # | Camera | Sensor / lens | Role | Mount |
|---|---|---|---|---|
| 1 | **ELP 4K** (top) | varifocal, CS-mount | Flat-face capture (screen / back) + corner tops | **Lens only** through the ⌀2" roof hole; body sits on the roof |
| 2–5 | **4× ELP IMX323** | 1/2.9", **fixed 3.6 mm** | The 4 device **edges** (sidewalls) + corners | **Inside** the box, mid-panel on each wall, angled down |

Only the top camera's lens enters the box from above; the four IMX323 bodies live **inside** the cube, so their placement is constrained by both optics *and* by not colliding with / shadowing the lighting.

---

## Assumptions (correct these if the build differs)

- Interior ≈ **11" (285 mm)** → **142 mm** from center to each inner wall.
- Worst-case device: phone **160 × 78 mm** (Pro-Max class). **Tablets are out of scope for the side cameras** — a 12.9" iPad edge cannot be framed from inside a 285 mm box; tablets are top-camera + flip only.
- Screen plane ≈ **12 mm** above the interior floor (rest-plate height).
- Device centered, long axis along X.

Derived gaps (wall inner face → nearest device edge):
- Wall → **near long edge** = 142 − 39 = **104 mm** (the N/S cameras).
- Wall → **near short edge** = 142 − 80 = **62 mm** (the E/W cameras).

---

## Step 1 — IMX323 + 3.6 mm field of view

Active silicon = 1920×1080 at 2.8 µm = **5.38 × 3.02 mm** (6.17 mm diag). With `FOV = 2·atan(size / 2f)`, f = 3.6 mm:

| | Value |
|---|---|
| **Horizontal FOV** | **≈ 73°** |
| **Vertical FOV** | **≈ 46°** |
| Diagonal FOV | ≈ 81° |

(The listing doesn't print a FOV; this is computed from sensor + focal length, which is more trustworthy than the marketing number.)

---

## Step 2 — the binding constraint: long-edge cameras

The **N/S cameras** must span the **160 mm** long edge across only a **104 mm** gap. Mounted *at edge height looking horizontally*, that needs `2·atan(80/104) = 75°` HFOV — **more than the 73° the lens has** → both corners clip at the frame edge. (This is the "some corners aren't caught" effect.)

Fix: **mount higher and tilt down.** More height → longer slant distance → smaller HFOV needed → corners pulled inside the frame.

| Cam height above screen | Slant dist | Down-tilt | HFOV needed (have 73°) | Corner in-frame? |
|---|---|---|---|---|
| 0 mm (at edge) | 104 mm | 0° | 75° ❌ | clipped |
| 50 mm (~2") | 115 mm | 26° | 70° | 95% out — tight |
| **90 mm (~3.5")** | **137 mm** | **41°** | **61° (12° margin)** | **82% out — comfortable** ✅ |

**Long-edge (N/S) cameras → mid-panel, ~3.5–4" up the wall (~90–100 mm above the screen plane ≈ 4" above the floor), tilted ~40° down, sensor landscape (long axis along the edge).**

---

## Step 3 — short-edge cameras (easy)

78 mm across a 62 mm gap needs only ~44° HFOV — huge margin. Mount the **E/W cameras at the same ~4" height** for symmetry; geometry puts them at a steeper **~50°** down-tilt (slant ≈ 109 mm, corner only ~20° off-axis → very comfortable).

---

## Step 4 — are the corners caught?

Each corner is seen by **three** views:

- its **short-edge camera** — corner ~20° off-axis → clean;
- its **long-edge camera** — corner ~30° off-axis → fine *if* mounted per Step 2;
- the **top camera** — straight down on the corner.

Corners only drop out when the long-edge pair is mounted **too low**. Remedies, cheapest first: **raise the N/S pair to ~4"**, then optionally **toe each in ~5°** for extra corner margin. No new hardware.

---

## Resolution & calibration

- ~**0.1 mm/px** on the edge — good for chips, dents, edge wear. **Not** for hairline scratches; those stay the **top camera's dark-field** job.
- The 3.6 mm lens has mild barrel distortion → **calibrate each side camera** (OpenCV checkerboard) before measuring geometry off it.

---

## Layout diagrams

**Top-down (plan view).** Side cams mid-panel; DF strips low on the walls; top cam straight down at center.

```
                       BACK wall (N)
        ┌──────────────[ Cam N ]──────────────┐
        │         (down-tilt, sees N long edge) │
        │      · · · DF strip (low, grazing) · · ·
        │            ┌─────────────────┐         │
 LEFT   │ [ Cam W ]► │  PHONE 160×78    │ ◄[ Cam E ]   RIGHT
 (W)    │            │  screen up       │         │   (E)
        │            └─────────────────┘         │
        │      · · · DF strip (low, grazing) · · ·
        │                                        │
        └──────────────[ Cam S ]────────────────┘
                  FRONT wall (door side)
            Top camera (ELP 4K) ⊙ looks straight down from roof center.
```

**Cross-section (looking along the long edge).** Note the vertical separation: side cams high, grazing strips low.

```
 ROOF ═══[ BF bar ]══( top-cam lens ⊙ )══[ BF bar ]═══     ~270 mm
                          │  straight down
                          ▼
   [Cam W] ◄╲                              ╱► [Cam E]      ~100 mm  (side cams, ~40–50° down)
            ╲                              ╱
             ╲  ·DF strip·  __[ PHONE ]__  ·DF strip·       ~5 mm   (grazing, below the cams)
 ───────────────────────── FLOOR ─────────────────────────  0 mm   (screen plane ≈ +12 mm)
```

---

## Lighting interaction (ties into [`../lighting/`](../lighting/README.md))

The FOV math forces the side cameras **up to ~4"**, while the dark-field strips live **low (~5 mm)**. That vertical gap resolves the conflicts:

- **No collision / no occlusion** — camera bodies sit above the grazing plane, so they don't block the strips or shadow the device.
- **Dark-field is a top-camera-only capture** — its geometry is defined for the overhead lens; the side cams stay idle during the DF shot (the grazing strips would otherwise sit in their frames).
- **New requirement: an edge / sidewall bright-field state.** A top-down bright-field leaves vertical sidewalls underlit, and the sidewalls are exactly what the side cams inspect. Cheap fix — during the side-camera (bright-field) pass, also switch on the **wall strips** (undimmed, lightly diffused) so each wall cross-lights the *opposite* sidewall. Free with manual hand-switching; it's just a third lighting state.

---

## Capture sequence (per face)

| State | Lights | Cameras capturing |
|---|---|---|
| **A — Bright-field** | Roof bars on | Top (flat face) |
| **B — Edge bright-field** | Wall strips on (diffused) | 4 side (edges + corners) |
| **C — Dark-field** | Wall strips on (bare, grazing) | Top only (scratches) |

Then the operator flips the device and repeats for the back face. (MVP v2's U-cradle would automate the flip — unchanged by this.)

---

## To verify on the bench

1. Mount one N/S camera at ~4", ~40° down → confirm the **full 160 mm edge + both corners** are in frame.
2. Check a real device's corners are legible from the combined side + top views.
3. Confirm the **door-side camera**: if a side camera lands on the hinged front door, it re-registers every time the door closes — either accept a re-home step or relocate that camera off the door.
4. Calibrate all four side cams; confirm ~0.1 mm/px and acceptable distortion after undistort.
