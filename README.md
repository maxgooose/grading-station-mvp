# Grading Project

Automated cosmetic grading station for used mobile devices. Fixed-camera enclosure + dual-capture lighting (bright-field + dark-field) + segmentation models → B/C (POC) or Universal + Blueberry (production) grade.

**MVP scope:**
- **MVP v1 (current focus):** fixed-camera enclosure, dual-capture lighting, segmentation pipeline, **feeding mechanism (device in → captures → device out)**. Operator manually flips the device between the front-face and back-face capture passes; the feeding mechanism handles entry and exit only. Feeding-mechanism design is being **finalized today** (mechanism TBD — conveyor, tray, drawer, etc.).
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

## Current status (2026-04-22)

- **Hardware (MVP v1):** enclosure + camera + lighting integration is the active workstream. Operator manually flips devices between captures. **Feeding mechanism (device in / device out) is being finalized today** — see [`hardware/README.md`](hardware/README.md).
- **Hardware (MVP v2 — deferred):** U-cradle flip spec exists at the architectural level (~$150–250 off-the-shelf BOM, buildable in an afternoon). **Not being built now** — kept as a known-good upgrade path so v1 decisions stay compatible with it.
- **Lighting:** dual-capture plan agreed. **Blocking:** zero-cost eyeball test (~15 min) has not been run yet — gates all downstream work.
- **Software:** POC classifier works but has a Grad-CAM background-shortcut problem. Pipeline being rebuilt around dual-capture segmentation + rule-based grading head.
- **Research:** competitor landscape mapped (April 2026). One open-source repo worth reading (Rotberg). One canonical dataset (MSD).

---

## Top-of-stack open questions

1. **Finalize the feeding mechanism today** — pick conveyor vs tray vs drawer vs ?, lock in / out path, decide the hand-off to the load position. See [`hardware/station-integration.md`](hardware/station-integration.md).
2. Run the eyeball test ([`lighting/README.md`](lighting/README.md)).
3. Finalize the per-defect label schema before any CVAT/Roboflow labeling.
4. ~~Order the U-cradle BOM and send the arm DXF to waterjet — build the mechanism.~~ **Deferred to MVP v2.** See [`hardware/README.md`](hardware/README.md).
