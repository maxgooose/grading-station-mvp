# Related Work, Datasets & Repos

Research companion to `optics-for-hire-scratch-detection.md`. Optics for Hire published no code, so these are the closest prior-art resources I was able to locate.

---

## Closest open-source implementations

| Repo | Match | Notes |
|------|-------|-------|
| https://github.com/AryehRotberg/Mobile-Phone-Defect-Segmentation-YOLOv8 | **Closest.** Phone screen scratch segmentation. | YOLOv8-seg instead of U-Net, but same problem domain (phone screens, scratch-class segmentation). |
| https://github.com/jianzhang96/MSD | Dataset + baseline for the canonical phone-screen defect task. | See dataset section below. |
| https://github.com/love6tao/ScratchDetection | CNN with dual-attention for industrial optics surfaces. | Compares against Gabor filter and morphology baselines — useful for picking a classical baseline. |
| https://github.com/volkbay/AIPSDSS | Automated Image Processing for Scratch Detection on Specular Surfaces. | Classical-CV-heavy. Relevant because phone screens *are* specular surfaces. |
| https://github.com/martinzelikovsky/Scratch_Detection_CNN | CNN outputting a scratch mask. | Domain is old film frames, not phone screens — but the mask-output architecture is transferable. |
| https://github.com/NanoNets/nanonets-cracked-screen-detection | Cracked-screen classification. | Classification, not segmentation — less useful for scratch localization but relevant for cracks. |

**No repo implements the exact OFH pipeline** (U-Net screen-mask → classical contour scratch detection on phone screens). It would have to be built.

---

## Datasets

### MSD — Mobile-phone Screen Defect (canonical)
- **Repo:** https://github.com/jianzhang96/MSD
- **Paper:** FDSNeT, Zhang et al., ICASSP 2022
- **Size:** 1,200 images, 1920×1080
- **Classes:** Oil, Scratch, Stain
- **Labels:** PASCAL VOC segmentation masks (pixel-level)
- **Split:** 6:2:2 (train/val/test)
- **Bonus:** 20 defect-free reference images
- **Verdict:** This is the most likely public dataset for pretraining a screen-defect segmentation model before fine-tuning on our lightbox captures. Start here for any supervised approach.

### Other references
- **"Mobile phone screen surface scratch detection based on optimized YOLOv5 (OYm)"** — Zhao, IET Image Processing 2023 — https://ietresearch.onlinelibrary.wiley.com/doi/10.1049/ipr2.12718
- **MSDD-UNet** — https://www.mdpi.com/2079-9292/13/16/3241 — U-Net variant for metal surface scratches. Different substrate, but the architectural modifications for thin linear features are transferable.

---

## Author / organization

- **John Ellis** — founder of Optics for Hire. LinkedIn https://www.linkedin.com/in/jrellisoptics/
- Optics for Hire is a consulting firm; their blog posts are marketing for client work, **not open source**. No GitHub organization exists.
- No papers or patents from OFH on this specific topic.
- Confirmed: `github.com/opticsforhire` returns 404.

---

## Recommended starting points if we want to reproduce the pipeline

1. **Capture first.** Replicate the lightbox geometry on our existing station, confirm scratches are visible in raw frames (eyeball test). Without this, nothing else matters.
2. **Segmentation.** Fine-tune a small U-Net on MSD for screen segmentation → transfer to our captures. Or skip the ML step entirely and use classical segmentation (adaptive threshold + largest connected component) since our station has fixed geometry and the screen is always in roughly the same place.
3. **Scratch detection.** Start with classical contour detection on the masked region. Only escalate to a learned scratch detector if classical methods saturate. Use `love6tao/ScratchDetection` and `volkbay/AIPSDSS` as reference implementations for the classical baselines.
4. **Dataset.** MSD for pretraining / sanity-checking the pipeline on external data. Our own lightbox captures for the final fine-tune.
