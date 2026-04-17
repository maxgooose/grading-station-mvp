# Engineering Docs

Working notes on the grading station's imaging + modeling pipeline. Read in this order if you're new to the problem or picking up the project after a break.

## Files

1. **[lighting-decision-and-plan.md](lighting-decision-and-plan.md)** — **START HERE.** Current decision on lighting (keep the Amazon lightbox, add a dark-field rig), the dual-capture plan, the zero-cost eyeball test to run before any hardware change, and open questions.
2. **[optics-for-hire-scratch-detection.md](optics-for-hire-scratch-detection.md)** — Full technical analysis of the Optics for Hire blog post. Hardware, illumination principle, pipeline, transferable lessons. The source of the dark-field idea.
3. **[related-work-and-datasets.md](related-work-and-datasets.md)** — Open-source projects, datasets (MSD is the canonical one), papers, author notes. Used to find the Rotberg repo and rule out others.
4. **[rotberg-yolov8-repo-analysis.md](rotberg-yolov8-repo-analysis.md)** — Deep dive on the closest open-source implementation (YOLOv8-seg for phone screens). Verdict: adopt the decomposition (instance segmentation), not the repo or weights or YOLOv8 architecture specifically.

## Current TL;DR

- Current binary EfficientNet-B0 classifier has a Grad-CAM background-shortcut problem. Needs replacing.
- Target architecture: **dual-capture (bright-field + dark-field) → two segmentation models → rule-based grading head.**
- Lightbox: **keep** the Amazon photo tent for bright-field capture. **Add** a cheap dark-field rig for scratches. Do not return the tent.
- Blocking next step: **run the zero-cost eyeball test** in `lighting-decision-and-plan.md` before any hardware purchase or model work.
- After that: pilot-label 20 images for scratch masks, train a YOLOv8-seg baseline, compare to U-Net, decide architecture from data.

## Code references

- `references/Mobile-Phone-Defect-Segmentation-YOLOv8/` — cloned Rotberg repo, kept as a code reference for how thin an Ultralytics + Roboflow pipeline can be (~150 LoC).
- `grading-model/scripts/` — current project code (EfficientNet-B0 train/predict/gradcam). To be replaced or augmented once the dual-capture plan is underway.
