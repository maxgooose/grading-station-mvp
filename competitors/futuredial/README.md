# FutureDial SMART Grade

**Company:** FutureDial Inc. (Sunnyvale, CA)
**Product:** SMART Grade + SMART Processing Platform
**Status:** Shipped, 1.5M+ devices graded

## Hardware

| Spec | Value |
|------|-------|
| Architecture | Standalone enclosed scanner |
| RADI platform dimensions | W 494 × L 743/835 × H 728 mm (~19 × 29 × 29 in) |
| SMART Grade dimensions | Not published (RADI gives a ballpark) |
| Cameras | "High-speed scanning cameras" (count unknown) |
| Lighting | "Diverse lighting" — strongly implies multiple light source types |
| Throughput | Not publicly stated per machine |
| Scale | 1.5M+ devices cosmetically graded, 420M+ devices processed total |
| Patents | 69+ total, including US20200242751A1 |

## How It Captures All Sides

**Unknown.** "High-speed scanning cameras and diverse lighting to deep-scan all the surfaces and corners of Android and iOS mobile devices."

"Diverse lighting" likely means multiple light types (bright-field + dark-field / directional). No flip mechanism described.

## Patent: US20200242751A1 — "Enhanced automatic cosmetic grading"

- Assignee: Future Dial Inc.
- 87+ figures
- Heavy on software/workflow: QR-code identification, data transfer, device-to-robot handoff
- Light on imaging hardware: no detailed camera/lighting/gripper teardown
- Does reference the RADI platform for functional testing (separate from SMART Grade)

## RADI Platform (Functional Testing, Separate Product)

Published datasheet with actual dimensions and specs:
- W 494 × L 743/835 × H 728 mm
- Small robotic arm for button pressing and touch simulation
- Separate from SMART Grade but shows FutureDial's hardware style

## What We Can Learn

- "Diverse lighting" suggests they've discovered that single-source lighting isn't enough
- 69+ patents means heavy IP protection — study the patents for architecture ideas
- SMART Processing Platform is modular (receiving / functional test / cosmetic grade / data erasure) — good integration model for our WholeCellIO pipeline
- 1.5M devices graded proves market demand at scale

## Sources

- https://www.futuredial.com/
- https://www.futuredial.com/accurate-grading-bigger-profits/
- https://www.futuredial.com/wp-content/uploads/2018/03/PDF_RADI-Test-Platform-Product-Sheet_2.20.2018.pdf
- https://www.prnewswire.com/news-releases/over-1-5-million-mobile-phones-cosmetically-graded-for-resale-by-futuredials-smart-grade-robots-301410997.html
- https://patents.google.com/patent/US20200242751A1/en
