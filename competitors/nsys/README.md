# NSYS Reeva Nova

**Company:** NSYS Group (founded 2016, UK HQ, global offices)
**Product:** Reeva Nova (successor to original Reeva, launched ~2020)
**Global premiere:** MWC26 (Barcelona, 2-5 March 2026)

## Hardware

| Spec | Value |
|------|-------|
| Architecture | Compact tray-based unit |
| Footprint | Compact (exact dimensions not published) |
| Throughput | 14 devices/hr per machine (~4 min/device) |
| Operator model | 1 operator can run 5 machines = ~70/hr |
| At scale | ~1,000/day per line |
| Controller | Intel-based onboard industrial PC (Nova gen) |
| Interface | Touchscreen LCD |
| Functions | 5-step: cosmetic + functional + pricing + erasure + warehouse tracking |
| **Price** | **Starting from $4,990** (only public price in the industry) |

## How It Captures All Sides

**Unknown.** Workflow is described as:
1. Operator places device in a tray
2. Robot closes
3. Fully automated 5-step sequence runs
4. Results displayed on touchscreen

Camera module upgraded in Nova gen to detect:
- Lens haze
- Sensor artifacts
- Micro-scratches
- Full display surface including corners and edge zones

Phrasing implies at least multiple image acquisitions, possibly multiple cameras. No flip mechanism described publicly.

## Imaging

- "Camera module" (singular phrasing in marketing, but multiple acquisitions)
- Evaluates "entire display surface including corners and edge zones"
- Runs pattern-on-screen test for display defects (device is powered on)
- Parallel activation rail — multiple DUTs can be activated from cables at once

## Pricing

**$4,990 starting** — the only public price in the entire industry. Positioned as "most affordable robot on the market."

## Why This Is Relevant To Us

Reeva Nova is the closest spiritual cousin to our grading station:
- Compact form factor (not a factory floor installation)
- Tray-based loading (similar to our feed mechanism concept)
- Single-operator workflow
- Low throughput per unit but scales by running multiples

Our station at ~$1,400 BOM and ~300 devices/hr would significantly undercut on price AND outperform on throughput.

## Sources

- https://nsysgroup.com/robotics/
- https://nsysgroup.com/blog/reeva-nova/
- https://nsysgroup.com/blog/mwc-gsmx-26/
- https://nsysgroup.com/blog/manual-software-assisted-or-robotic-phone-testing/
- https://aimgroup.com/2026/03/04/nsys-launches-next-gen-diagnostics-robot-for-device-evaluation-at-mwc/
