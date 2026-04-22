# Research

Everything we learned from outside the project: competitor hardware, patents, related open-source work, and datasets. Used to rule things out, find prior art, and avoid re-inventing wheels.

**Status:** Competitor landscape is mapped from public sources (April 2026). Related-work sweep produced one repo worth reading (Rotberg YOLOv8-seg). One dataset is canonical (MSD).

---

## What's here

### Competitor intelligence

| File | What it is |
|---|---|
| [`competitors/`](competitors/README.md) | Per-company dossiers: Phonecheck, Griffyn, Ingram Micro, NSYS, Apkudo, OptoFidelity, FutureDial. Architectures, throughput, pricing, feasibility. |
| [`competitors/patents/`](competitors/patents/) | Key patents: FedEx/ATC (transparent base + gripper), GDT (angled mirrors, no flip), Griffyn, FutureDial. |
| [`index.html`](index.html) | Landing page linking to the two competitor 3D model visualizations below. |
| [`griffyn-deepsight-3d.html`](griffyn-deepsight-3d.html) | 3D model of Griffyn DEEPSIGHT (5-axis arm + 1 camera). |
| [`phonecheck-3d.html`](phonecheck-3d.html) | 3D model of the Phonecheck cabinet-and-turntable robot. |

### Technical literature

| File | What it is |
|---|---|
| [`related-work-and-datasets.md`](related-work-and-datasets.md) | Open-source projects, datasets (MSD is canonical), papers, author notes. Used to find the Rotberg repo and rule out others. |
| [`rotberg-yolov8-repo-analysis.md`](rotberg-yolov8-repo-analysis.md) | Deep dive on the closest open-source implementation (YOLOv8-seg for phone screens). **Verdict:** adopt the decomposition (instance segmentation), not the repo / weights / YOLOv8 specifically. |

---

## Competitor landscape at a glance

Compiled from public sources, patents, trade press, and academic theses. No company in this space publishes internal hardware details — everything is trade secrets behind NDA/sales calls. What's here is the most complete public picture available as of April 2026.

| Company | Product | Architecture | Throughput | Flip mechanism | Price | Feasibility for us |
|---|---|---|---|---|---|---|
| Phonecheck | Robot | Cabinet + turntable/multi-cam | 55/hr | Unknown (trade secret) | Lease only | HIGH |
| Griffyn | DEEPSIGHT | 5-axis robot arm + 1 cam | 60/hr (200/hr pod) | Arm presents all 6 sides | Unknown | LOW |
| Ingram Micro | REV | 20 ft racetrack conveyor | 480/hr | Unknown (photometric scan) | Internal only | MEDIUM |
| NSYS | Reeva Nova | Compact tray unit | 14/hr | Unknown | $4,990 | HIGH |
| Apkudo | RSA / Full Line | Modular cells + conveyor | 250-300/hr | Unknown | NDA | LOW |
| OptoFidelity | SCORE | Benchtop mover unit | Unknown | Linear mover (thesis-documented) | Unknown | MEDIUM |
| FutureDial | SMART Grade | Standalone scanner | Unknown | Unknown | Unknown | MEDIUM |

---

## Industry observations (what the landscape tells us)

1. **Two dominant architectures:** (a) fixed cameras around a stationary/slow DUT, (b) single camera + manipulator that flips the device. We picked (a) with one flip — see [`../hardware/`](../hardware/README.md).
2. **Lighting is the most-hidden variable.** Only Ingram Micro publicly names "photometric scanning". Nobody says "cross-polarized" or "dark-field". This is where our dual-capture plan differentiates — see [`../lighting/`](../lighting/README.md).
3. **40 µm × 3 µm (Griffyn)** is the only published defect resolution. Publishing ours would be a differentiator.
4. **Throughput range:** 14/hr (NSYS) → 480/hr (Ingram). Single-operator sweet spot is 30-70/hr. Our 57 s budget lands us at ~63/hr.
5. **Only one public price:** Reeva Nova at $4,990.
6. **No one has open-sourced** a grading pipeline. This project would be novel as OSS.
7. **Several competitors avoid flipping entirely** — cameras below transparent platform (FedEx/ATC patent), or angled mirrors (GDT patent). Worth re-evaluating if the U-cradle prototype has problems.

---

## Key patents (summarized)

| Patent | Assignee | Key idea |
|---|---|---|
| US20140267691A1 | FedEx / ATC Logistics | Transparent base + articulated gripper + cameras above and below |
| US20150330910A1 | GDT Inc | Angled mirrors — no flip needed, phone stays stationary |
| Griffyn patent | Griffyn Robotech | "Cosmetic Grading Through Image Processing and Method" |
| US20200242751A1 | FutureDial | Enhanced automatic cosmetic grading workflow |

Full breakdowns in [`competitors/patents/`](competitors/patents/).

---

## Related work — what was adopted and what was ruled out

- **Rotberg YOLOv8-seg repo** → adopt the *decomposition* (instance segmentation over binary classification), but **not** the repo, weights, or YOLOv8 architecture specifically. YOLO's mask prototypes handle thin linear features (scratches) poorly. Full analysis in [`rotberg-yolov8-repo-analysis.md`](rotberg-yolov8-repo-analysis.md).
- **MSD (Mobile Screen Defect) dataset** → the canonical public dataset. Useful for pretraining; not a substitute for our own labeled captures since lighting conditions differ.
- **Optics for Hire blog** → not code, not a dataset, but the source of the **dark-field insight** that reshaped our entire pipeline. See [`../lighting/optics-for-hire-scratch-detection.md`](../lighting/optics-for-hire-scratch-detection.md).

---

## Open research questions

1. **Can we find a second public defect resolution number** (beyond Griffyn's 40 µm × 3 µm) to calibrate expectations?
2. **Is there an academic paper on dark-field imaging for consumer electronics grading** beyond the Optics for Hire blog? None found yet.
3. **What does Ingram Micro's "photometric scanning" actually mean** — photometric stereo? Multi-angle sequential capture? Unclear from public sources.
