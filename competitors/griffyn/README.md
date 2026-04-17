# Griffyn DEEPSIGHT

**Company:** Griffyn Robotech Pvt Ltd (Pune, India) / Phoenix Innovations LLC (US sales)
**Product:** DEEPSIGHT
**Status:** Shipping, deployed globally

## Hardware (BEST-DOCUMENTED COMPETITOR)

Detailed via Beckhoff partnership case study — most technically disclosed system in the industry.

| Spec | Value |
|------|-------|
| Architecture | Single camera + 5-axis servo manipulator |
| Footprint | Standalone unit or 2-4 machine "pod" |
| Throughput | ~60/hr per machine, ~200/hr in 4-machine pod |
| Defect resolution | **40μm wide × 3μm deep** (industry benchmark) |
| Camera | Single high-res camera (model unknown) |
| Controller | Beckhoff C6015 ultra-compact industrial PC |
| Servos | Beckhoff AM81xx servomotors |
| Drives | Beckhoff EL7211 servomotor EtherCAT terminals |
| Motion software | TwinCAT NC I |
| Communication | EtherCAT (sub-millisecond cycle) |
| Wiring | Beckhoff One Cable Technology (OCT) |
| Machine availability | 95% |

## How It Flips the Device

**5-axis servo manipulator.** This is confirmed, not speculation.

- 5 servo axes for product handling
- Picks up device, presents all 6 faces to a single fixed camera station
- Continuous re-posing (not just 0°/180° like a simple flip)
- Can hold device at any arbitrary angle for the camera

This is the OPPOSITE of our approach — Griffyn uses an expensive multi-axis robot arm ($20K+ in Beckhoff components alone) where we use a single rotation axis.

## Lighting

NOT disclosed. No camera model, resolution, lens, or lighting details published. Ring light, cross-polarized, dome — unknown.

## Patent

**"Cosmetic Grading Through Image Processing and Method"**
- Granted ~August 2019 (US), announced May 31, 2021
- Assigned to Griffyn Robotech Pvt Ltd
- Describes "camera and lighting assemblies to capture images of an object and create a 2D composite image which is processed by an image processing module with a deep learning machine algorithm"
- Full patent document not located on Google Patents (may be indexed under different title/number)

**DEEPSIGHT** is a USPTO-registered trademark:
- Reg. 5903257, serial 88424668
- Reg. 5994916, serial 88511296

## Why This Doesn't Work For Us

- 5-axis Beckhoff servo stack costs $20K+ for the motion components alone
- Requires TwinCAT NC I motion control software expertise
- Complex calibration across 5 axes
- Overkill for A/B/C/D grading — we don't need arbitrary pose angles

## What We Can Learn

- **40μm × 3μm** is the defect resolution to beat (or match). We should measure and publish ours.
- Single camera with manipulator gives maximum flexibility — every angle is reachable
- EtherCAT gives sub-ms cycle for precise positioning — relevant if we ever upgrade
- 95% machine availability is the reliability target

## Sources

- https://griffyn.io/deepsight/
- https://www.beckhoff.com/en-en/company/news/fast-and-precise-surface-inspection-of-smart-devices.html
- https://metrology.news/fast-and-precise-surface-inspection-of-smart-devices-uses-deep-learning/
- https://www.prnewswire.com/news-releases/griffyn-robotech-and-phoenix-innovations-llc-announce-new-patent-for-cosmetic-grading-system-301302246.html
- https://trademarks.justia.com/884/24/deepsight-88424668.html
