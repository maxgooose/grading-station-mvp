# Patent: GDT Inc — Mirror-Based Cosmetic Evaluation

**Patent:** US20150330910A1
**Title:** Cosmetic Evaluation Box for Used Electronics
**Assignee:** GDT Inc
**Link:** https://patents.google.com/patent/US20150330910

## Why This Matters

This is the **most unconventional approach** — no flip mechanism at all. Uses mirrors to capture both surfaces from fixed cameras. Zero moving parts for image acquisition.

## How It Works

1. Phone sits stationary in a clip holder
2. Strategically angled mirrors reflect BOTH surfaces (front and back) into cameras
3. The device's own front and rear cameras may also be used for self-inspection
4. No flipping, no rotation, no robotic arm required

## Key Innovation

**Mirrors eliminate the flip entirely.** By positioning mirrors at precise angles:
- A single camera can see the phone's front face directly AND the back face via a mirror reflection
- Or separate cameras each use mirrors to capture their respective surface
- Edges can be captured by additional angled mirrors

## Implications For Our Design

This is a fundamentally different approach from our sandwich flip:

| | Our Sandwich Flip | GDT Mirror Approach |
|---|---|---|
| Moving parts | 1 (rotation axis) | 0 |
| Complexity | Low mechanical | Low mechanical, high optical |
| Drawbacks | Needs motor + bearings + pads | Mirror distortion, calibration, cleaning |
| Image quality | Direct camera view | Reflected view (potential degradation) |
| Maintenance | Pad replacement | Mirror cleaning + alignment |

### Could We Hybrid This?

Use mirrors for edge cameras instead of mounting cameras at 4 edge positions. A single camera + 4 angled mirrors could potentially capture all 4 edges from one position. This would reduce the camera count from 5 to 2 (one top + one edge-mirror).

Worth prototyping but adds optical complexity.
