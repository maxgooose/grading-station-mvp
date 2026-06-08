# Grading Project

Automated cosmetic grading station for used mobile devices. Fixed-camera enclosure + dual-capture lighting (bright-field + dark-field) + segmentation models → B/C (POC) or Universal + Blueberry (production) grade.

**MVP scope:**
- **MVP v1 (current focus):** wooden-plank capture enclosure (no 2020 extrusion frame), outer utility/wiring box at the base, dual-capture lighting (installed before cameras), segmentation pipeline, **feeding mechanism (device in → captures → device out)**. O the feeding mechanism handles entry and exit only. Feeding-mechanism design is being finalized (mechanism TBD — conveyor, tray, drawer, etc.). Full build sequence in [`hardware/station-integration.md`](hardware/station-integration.md#revised-build-approach-2026-05-04).
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

## Current status (2026-06-08)

- **Hardware (MVP v1):** Wooden-plank shell **assembled** (12"×12"×12" cube on a 24"×12" floor plank, panels nailed together per the [v1 cut sheet](hardware/shell-v1-cut-sheet.html)). Still pending: lighting install (next), then camera + light mounting/wiring hardware. Sits on top of the larger outer utility/wiring box. Full build sequence in [`hardware/station-integration.md`](hardware/station-integration.md#revised-build-approach-2026-05-04). Feeding mechanism design still being finalized. Operator manually flips devices between captures.
- **Hardware (MVP v2 — deferred):** U-cradle flip spec exists at the architectural level (~$150–250 off-the-shelf BOM, buildable in an afternoon). **Not being built now** — kept as a known-good upgrade path so v1 decisions stay compatible with it.
- **Lighting:** dual-capture plan confirmed — **eyeball test PASSED 2026-05-09** inside the assembled shell. **Buy decision locked 2026-06-08** (plug-and-play, manually switched — no MOSFET/PSU for v1; see [`lighting/README.md`](lighting/README.md) + [`hardware/v1-parts-order.html`](hardware/v1-parts-order.html)). Next: purchase the lights, install, re-test the capture (with a flicker check), then mount the camera.
- **Software:** POC classifier works but has a Grad-CAM background-shortcut problem. Pipeline being rebuilt around dual-capture segmentation + rule-based grading head.
- **Research:** competitor landscape mapped (April 2026). One open-source repo worth reading (Rotberg). One canonical dataset (MSD).

---

## Top-of-stack open questions

1. **Finalize the feeding mechanism** — pick conveyor vs tray vs drawer vs ?, lock in / out path, decide the hand-off to the load position. See [`hardware/station-integration.md`](hardware/station-integration.md).
2. **Acquire the outer utility/wiring box** — find a sturdy box for the PSU, MCU, MOSFET board, and wiring. This sets the footprint everything else builds on. ~$15.
3. ~~Build the wooden-plank capture shell~~ **Done (2026-06-01).** Matte-finish on the inside still TBD if needed for light-tightness; lighting goes in next, cameras after.
4. ~~**Install lighting and run the eyeball test**~~ Eyeball test **PASSED 2026-05-09**; buy decision **locked 2026-06-08**. Remaining: **purchase + install the lights, then re-test the capture** (add a flicker/banding check) before mounting the camera ([`lighting/README.md`](lighting/README.md)).
5. Finalize the per-defect label schema before any CVAT/Roboflow labeling.
6. ~~Order the U-cradle BOM and send the arm DXF to waterjet — build the mechanism.~~ **Deferred to MVP v2.** See [`hardware/README.md`](hardware/README.md).
