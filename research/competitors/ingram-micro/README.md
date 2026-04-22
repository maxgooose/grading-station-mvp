# Ingram Micro REV

**Company:** Ingram Micro Lifecycle (formerly HYLA Mobile, now part of Ingram Micro)
**Product:** REV (Robotic Electronic Validation)
**Status:** Internal use only — not sold commercially

## Hardware

Highest throughput system in the industry. Massive factory-floor installation.

| Spec | Value |
|------|-------|
| Architecture | 20 ft × 4 ft oval "racetrack" conveyor |
| Throughput | **480 devices/hr per machine** (1.9M/year) |
| Pallet capacity | 16 pallets × 16 devices each = 256 DUT positions in motion |
| Test stations | 6 X-Y tables with 2 independent arms each |
| Simultaneous tests | 100+ functional tests possible |
| Cosmetic method | **Photometric scanning** (multi-angle illumination) |

## How It Captures All Sides

**Unknown.** The photometric scanning approach suggests:

- Multi-angle illumination to recover surface normals and microtopography
- This is different from simple photography — it reconstructs 3D surface detail
- Devices stay powered-on and plugged in throughout the entire racetrack loop
- Likely cameras at multiple fixed stations around the racetrack

**Photometric scanning is the only lighting technique ANY competitor has publicly named.** This is significant — it's a different approach from standard photography or cross-polarized capture.

### What is Photometric Scanning?

Multiple images of the same object taken under different lighting directions. By comparing how the surface looks under each light angle, you can reconstruct:
- Surface normals (3D orientation of each pixel)
- Micro-topography (tiny dents, scratches as surface height changes)
- Albedo (true color, separated from shading)

This is more information-rich than a single cross-polarized photo, but requires multiple captures per view angle.

## Pricing

**Not for sale.** This is Ingram Micro's internal competitive advantage for their reverse logistics business. They process devices on behalf of carriers (T-Mobile, AT&T, etc.) and retailers.

## Why This Doesn't Work For Us

- 20×4 ft floor footprint — needs a warehouse
- 256 device positions in continuous motion — massive mechanical complexity
- Internal system, can't buy it
- Designed for carrier-scale volumes (millions/year)

## What We Can Learn

- **Photometric scanning** is worth investigating as a complement to cross-polarized capture
- Racetrack approach keeps devices powered on and connected throughout — useful for functional testing
- X-Y tables (gantry-style) are an alternative to robot arms for positioning test probes
- At scale, batch processing on a conveyor beats serial processing in a booth

## Sources

- https://www.ingrammicrolifecycle.com/solutions/rev
- https://www.ingrammicroservices.com/blog/REV-walkthrough-new-automation-grading/
- https://www.rcrwireless.com/20210121/5g/a-thousand-times-faster-ingram-micro-claims-a-revolution-in-reverse-logistics-for-mobile-retailers
