# Patent: FedEx / ATC Logistics — Automated Cosmetic Inspection

**Patent:** US20140267691A1
**Title:** System and method for automated cosmetic inspection
**Assignee:** ATC Logistics & Electronics / FedEx Supply Chain Logistics and Electronics Inc.
**Inventors:** Clark Humphrey, Brian Morris
**Link:** https://patents.google.com/patent/US20140267691

## Why This Matters

This is the **deepest publicly readable hardware description** in the entire smartphone cosmetic grading space. Worth reading end-to-end for hardware design inspiration.

## Key Hardware Disclosures

### Camera Array
- Multiple cameras positioned at edges, below, and above a base
- Still or video capture capability
- Zoom capability
- Adjustable camera support arms with tilt joints for multi-angle capture
- Portable camera for obscured regions

### Transparent Base
- Base can be transparent → cameras below see through to device back
- **This eliminates the need for a flip mechanism**
- Non-reflective base surface as imaging background (alternative mode)

### Gripping Unit
Two robot arms (107, 108), each supporting multiple gripper types:
- Pinchers
- Fingers
- Jamming grippers
- Friction grips
- Encompassing grips
- Suction systems
- Robotic hands

Arm 108 is telescoping. Both have tilt/rotate joints to present device at arbitrary poses.

### Device Handling
- Conveyor/slide/shaker under the base moves devices at controlled rate
- **Swiveling base portion** rotates the DUT without moving cameras
- X/Y/Z positioning above base

### Lighting
- Supports "various spectrums, wavelengths and frequencies"
- Visible, IR, UV, and even X-ray (aspirational)
- No specific polarization claim

### Other Features
- Defect-marking robot (paint/marker) to physically mark defects on the device
- Barcode/RFID scanner for part identification

## Key Takeaways For Our Design

1. **Transparent base** is a viable alternative to flipping — cameras below capture the back without any mechanical flip
2. **Swiveling base** is simpler than a robot arm for changing the angle
3. **Multiple gripper types** listed — but our silicone sandwich pads achieve the same universal grip more simply
4. This patent is from a logistics/3PL company, not a grading equipment vendor — shows that the problem has been studied by people outside the usual suspects
