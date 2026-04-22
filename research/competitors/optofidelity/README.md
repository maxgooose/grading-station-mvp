# OptoFidelity SCORE

**Company:** OptoFidelity (Tampere, Finland) — acquired by Assurant in October 2025
**Product:** SCORE (cosmetic grading) + FUSION (functional testing)
**Status:** Shipping

## Hardware (MOST DOCUMENTED INTERNALS via university thesis)

A Tampere University thesis by Jyri Raninen (August 2022) titled "Defining refurbished smart phone handling in a modular test cell" describes the SCORE's internal mechanism.

| Spec | Value |
|------|-------|
| Architecture | Benchtop light-shielded enclosure |
| Dimensions | 902 × 406 × 358 mm (~35 × 16 × 14 in) |
| Throughput | Not publicly disclosed |
| Power | Regular AC + WiFi only |
| Operator | Manual load, or 6-axis robot arm for automated feeding |

## How It Captures All Sides (THESIS-DOCUMENTED)

**"Mover" assembly:**
1. Phone is clamped between a **fixed bottom block** and a **spring-loaded top block**
2. Phone **slides linearly** through the unit on **guide rollers**
3. Cameras scan the device as it passes through

### Inspects:
- Display (full surface)
- Back cover
- Sides, top, bottom edges
- Corners
- User-defined regions of interest (screws, camera lens, logo)

### Automated Feeding (SmartCell integration):
- **Han's Robot Elfin** 6-axis robot arm
- **Pneumatic parallel-jaw gripper fingers**
- Picks phones from a buffer, inserts into SCORE's mover

### Open Question:
How the back is captured is not fully described. Likely either:
- Phone processed in two passes (screen-up, then screen-down)
- Cameras positioned both above and below the mover path

## FUSION (Sibling Functional Tester)

Has documented hardware evolution:
- "Light cube" (enlarged in 2022 to support wide-angle DUT cameras)
- "Touch finger" tool with integrated mute switch
- "Suction cup studs" to fix slippery DUTs
- Linux OS, "Bertta" server
- 6-axis robot for touch panel testing

## Why This Is Relevant To Us

The SCORE's linear mover concept is an alternative to our rotation-based flip:
- Phone slides through a scanning tunnel instead of being flipped in place
- Spring-loaded clamping is conceptually similar to our U-cradle (spring-loaded sliding arm)
- Benchtop form factor (~35" wide) proves you don't need a huge enclosure

The Assurant acquisition (Oct 2025) may affect what information becomes public.

## Sources

- https://www.optofidelity.com/en/score
- https://www.optofidelity.com/en/fusion
- https://www.optofidelity.com/blog/fusion-hardware-development-over-the-years
- https://www.optofidelity.com/insights/blogs/cosmetic-condition-score
- https://www.optofidelity.com/insights/webinars/automated-cosmetic-grading-for-pre-owned-smartphones-with-score
- Raninen, Jyri. "Defining refurbished smart phone handling in a modular test cell." Tampere University, August 2022. https://trepo.tuni.fi/bitstream/handle/10024/141770/RaninenJyri.pdf
- https://resource-recycling.com/e-scrap/2025/10/16/assurant-acquires-optofidelity-to-speed-repair-and-reuse-work/
