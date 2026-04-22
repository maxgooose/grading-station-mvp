# Grading Project

Automated cosmetic grading station for used mobile devices. Fixed-camera enclosure + single-flip device handling + dual-capture lighting (bright-field + dark-field) + segmentation models → B/C (POC) or Universal + Blueberry (production) grade.

---

## Component map

Every component lives in its own folder with a single `README.md` as the main doc. Start from the component you're working on.

| Folder | What it covers | Start at |
|---|---|---|
| [`grading-criteria/`](grading-criteria/README.md) | The label schemas the model must output: Universal (A, B, C(amz), C, D) and Blueberry (later). The source of truth for every downstream decision. | [`grading-criteria/README.md`](grading-criteria/README.md) |
| [`software/`](software/README.md) | ML/CV pipeline. Current POC (EfficientNet-B0 binary classifier) and the next-arch dual-capture segmentation plan. | [`software/README.md`](software/README.md) |
| [`hardware/`](hardware/README.md) | Physical station: pivoting U-cradle flip mechanism, camera layout, cycle timing, BOM. | [`hardware/README.md`](hardware/README.md) |
| [`lighting/`](lighting/README.md) | Illumination strategy: bright-field + dark-field dual capture. The most under-valued component of the whole station. | [`lighting/README.md`](lighting/README.md) |
| [`research/`](research/README.md) | Competitor teardowns, patents, related open-source work, datasets. What was ruled in, what was ruled out. | [`research/README.md`](research/README.md) |

---

## Current status (2026-04-22)

- **Hardware:** U-cradle flip spec finalized (~$150–250 off-the-shelf BOM, buildable in an afternoon). Order parts + waterjet the arm DXF is the next step.
- **Lighting:** dual-capture plan agreed. **Blocking:** zero-cost eyeball test (~15 min) has not been run yet — gates all downstream work.
- **Software:** POC classifier works but has a Grad-CAM background-shortcut problem. Pipeline being rebuilt around dual-capture segmentation + rule-based grading head.
- **Research:** competitor landscape mapped (April 2026). One open-source repo worth reading (Rotberg). One canonical dataset (MSD).

---

## Top-of-stack open questions

1. Run the eyeball test ([`lighting/README.md`](lighting/README.md)).
2. Finalize the per-defect label schema before any CVAT/Roboflow labeling.
3. Order the U-cradle BOM and send the arm DXF to waterjet — build the mechanism ([`hardware/cradle-build-spec.md`](hardware/cradle-build-spec.md)).
