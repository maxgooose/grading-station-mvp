# Grading Project

Automated cosmetic grading station for used mobile devices. Fixed-camera enclosure + dual-capture lighting (bright-field + dark-field) + segmentation models → B/C (POC) or Universal + Blueberry (production) grade.

**MVP scope:**
- **MVP v1 (current focus):** foam board capture enclosure (no 2020 extrusion frame), outer utility/wiring box at the base, dual-capture lighting (installed before cameras), segmentation pipeline, **feeding mechanism (device in → captures → device out)**. Operator manually flips the device between the front-face and back-face capture passes; the feeding mechanism handles entry and exit only. Feeding-mechanism design is being finalized (mechanism TBD — conveyor, tray, drawer, etc.). Full build sequence in [`hardware/station-integration.md`](hardware/station-integration.md#revised-build-approach-2026-05-04).
- **MVP v2 (deferred — slight consideration only):** automated single-flip device handling (the U-cradle / pivoting flip mechanism). Specced at a high level so v1 doesn't paint us into a corner, but **not being built right now**.

---

## Component map

Every component lives in its own folder with a single `README.md` as the main doc. Start from the component you're working on.

| Folder | What it covers | Start at |
|---|---|---|
| [`grading-criteria/`](grading-criteria/README.md) | The label schemas the model must output: Universal (A, B, C(amz), C, D) and Blueberry (later). The source of truth for every downstream decision. | [`grading-criteria/README.md`](grading-criteria/README.md) |
| [`software/`](software/README.md) | ML/CV pipeline. Current POC (EfficientNet-B0 binary classifier) and the next-arch dual-capture segmentation plan. | [`software/README.md`](software/README.md) |
| [`hardware/`](hardware/README.md) | Physical station: camera layout, cycle timing, BOM. Pivoting U-cradle flip mechanism is specced but **scoped to MVP v2 (deferred)**. | [`hardware/README.md`](hardware/README.md) |
| [`lighting/`](lighting/README.md) | Illumination strategy: bright-field + dark-field dual capture. The most under-valued component of the whole station. | [`lighting/README.md`](lighting/README.md) |
| [`research/`](research/README.md) | Competitor teardowns, patents, related open-source work, datasets. What was ruled in, what was ruled out. | [`research/README.md`](research/README.md) |

---

## Current status (2026-05-04)

- **Hardware (MVP v1):** Enclosure build strategy revised — foam board shell (no 2020 frame), lighting-first, cameras after. Will sit on top of a larger outer utility/wiring box. Full updated build sequence in [`hardware/station-integration.md`](hardware/station-integration.md#revised-build-approach-2026-05-04). Feeding mechanism design still being finalized. Operator manually flips devices between captures.
- **Hardware (MVP v2 — deferred):** U-cradle flip spec exists at the architectural level (~$150–250 off-the-shelf BOM, buildable in an afternoon). **Not being built now** — kept as a known-good upgrade path so v1 decisions stay compatible with it.
- **Lighting:** dual-capture plan agreed. **Blocking:** zero-cost eyeball test (~15 min) has not been run yet — gates all downstream work. Once the foam board shell is built and the lighting is installed, this test runs inside the actual enclosure.
- **Software:** POC classifier works but has a Grad-CAM background-shortcut problem. Pipeline being rebuilt around dual-capture segmentation + rule-based grading head.
- **Research:** competitor landscape mapped (April 2026). One open-source repo worth reading (Rotberg). One canonical dataset (MSD).

---

## Top-of-stack open questions

1. **Finalize the feeding mechanism** — pick conveyor vs tray vs drawer vs ?, lock in / out path, decide the hand-off to the load position. See [`hardware/station-integration.md`](hardware/station-integration.md).
2. **Acquire the outer utility/wiring box** — find a sturdy box for the PSU, MCU, MOSFET board, and wiring. This sets the footprint everything else builds on. ~$15.
3. **Build the foam board capture shell** — matte black foam board panels, light-tight, sitting on top of the utility box. ~$40. Lighting goes in first; cameras only after the lighting is verified.
4. Run the eyeball test inside the foam board shell once lighting is installed ([`lighting/README.md`](lighting/README.md)).
5. Finalize the per-defect label schema before any CVAT/Roboflow labeling.
6. ~~Order the U-cradle BOM and send the arm DXF to waterjet — build the mechanism.~~ **Deferred to MVP v2.** See [`hardware/README.md`](hardware/README.md).
