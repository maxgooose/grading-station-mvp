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
2. Top camera shoots front face
3. 4 edge cameras shoot all edges simultaneously
4. Top pad descends, sandwiches device (~20N force via spring)
5. Rotate 180° over ~1.5 seconds
6. Top pad lifts
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

## Top Pad Actuator

- Lead screw or pneumatic cylinder
- 50mm travel (handles 6mm thin iPad to 16mm folded Z Flip)
- Spring between actuator and pad — provides consistent 20N regardless of device thickness

## Physics Check

Worst case: iPad Pro 682g at 90° rotation.
- Gravity pulling sideways: 6.7N
- Friction from two silicone pads at 20N clamp: ~20N
- 3x safety margin. It holds.

## Frame

- Aluminum plates both sides
- 12mm steel shaft through sealed bearings
- Naturally balanced (symmetric pads)

## Devices Covered

| Device | Why it works |
|--------|-------------|
| Standard phones | Camera bump sinks into pad, flip holds easily |
| Large tablets | Pads sized for iPad Pro, force margin is fine |
| Foldables (folded) | Extra thickness handled by actuator travel range |
| Foldables (unfolded) | Soft pad conforms to hinge crease |
| Curved-edge screens | Pad contacts flat center, curves hang free |
| Cracked/broken devices | Friction-based hold, not vacuum — doesn't care |

## First Prototype Test

Two silicone pads, a hinge, a clamp at 20N, a handle. Flip by hand 50 times with: iPhone SE, Galaxy Z Flip folded, iPad Pro, worst-condition phone you have. If nothing shifts, the design is validated.

## BOM (Flip Mechanism Only)

| Part | Est. Cost |
|------|-----------|
| 2x silicone pad sheet (cut to size) | $30 |
| 2x aluminum backing plate 300x230x6mm | $40 |
| NEMA 23 stepper + 5:1 gearbox | $65 |
| Stepper driver (TMC2209 or similar) | $15 |
| Lead screw actuator (top pad, 50mm stroke) | $35 |
| 12mm steel shaft + 2x pillow block bearings | $25 |
| Rotary encoder | $15 |
| Aluminum frame plates + hardware | $50 |
| Compression spring (force control) | $5 |
| **Total** | **~$280** |
