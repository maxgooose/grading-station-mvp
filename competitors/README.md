# Competitor Hardware Intelligence

Research compiled from public sources, patents, trade press, and academic theses. No company in this space publishes internal hardware details — all systems are trade secrets behind NDA/sales calls. What's documented here is the most complete public picture available as of April 2026.

## Competitors

| Company | Product | Architecture | Throughput | Flip Mechanism | Price | Feasibility |
|---------|---------|-------------|-----------|----------------|-------|-------------|
| [Phonecheck](phonecheck/) | Robot | Cabinet + turntable/multi-cam | 55/hr | Unknown (trade secret) | Lease only | HIGH |
| [Griffyn](griffyn/) | DEEPSIGHT | 5-axis robot arm + 1 cam | 60/hr (200/hr pod) | Robot arm presents all 6 sides | Unknown | LOW |
| [Ingram Micro](ingram-micro/) | REV | 20ft racetrack conveyor | 480/hr | Unknown (photometric scanning) | Internal only | MEDIUM |
| [NSYS](nsys/) | Reeva Nova | Compact tray unit | 14/hr | Unknown | $4,990 | HIGH |
| [Apkudo](apkudo/) | RSA / Full Line | Modular cells + conveyor | 250-300/hr | Unknown | NDA | LOW |
| [OptoFidelity](optofidelity/) | SCORE | Benchtop mover unit | Unknown | Linear mover (thesis-documented) | Unknown | MEDIUM |
| [FutureDial](futuredial/) | SMART Grade | Standalone scanner | Unknown | Unknown | Unknown | MEDIUM |

## Key Patents

| Patent | Assignee | Key Innovation |
|--------|----------|---------------|
| [US20140267691A1](patents/fedex-atc.md) | FedEx / ATC Logistics | Transparent base + articulated gripper + cameras above/below |
| [US20150330910A1](patents/gdt-mirrors.md) | GDT Inc | Angled mirrors — no flip needed, phone stays stationary |
| [Griffyn patent](patents/griffyn.md) | Griffyn Robotech | "Cosmetic Grading Through Image Processing and Method" |
| [US20200242751A1](patents/futuredial.md) | FutureDial | Enhanced automatic cosmetic grading workflow |

## Industry Observations

1. **Two dominant architectures**: (a) fixed cameras around stationary/slow DUT, (b) single camera + manipulator flipping device
2. **Lighting is the most-hidden variable** — only Ingram Micro publicly names "photometric scanning." Nobody says "cross-polarized"
3. **40μm × 3μm (Griffyn)** is the only published defect resolution. Publishing yours is a differentiator
4. **Throughput range**: 14/hr (NSYS) → 480/hr (Ingram). Single-operator sweet spot is 30-70/hr
5. **Only one public price**: Reeva Nova at $4,990
6. **No one has open-sourced** a grading pipeline. Your project would be novel
7. **Several competitors avoid flipping entirely** — cameras below transparent platform, or mirrors
