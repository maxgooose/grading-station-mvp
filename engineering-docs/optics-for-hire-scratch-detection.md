# Optics for Hire — Phone Screen Scratch Detection

**Source:** https://www.opticsforhire.com/blog/scratch-detect-convolutional-neural-network/
**Companion:** https://www.opticsforhire.com/blog/defect-detection/ (Nov 2024, same lab)
**Author:** John Ellis (founder, Optics for Hire)
**Code available:** No — no public repo, no GitHub org, no paper. Blog-only.

---

## Thesis of the article

Scratch detection is an **optics problem, not a model problem**. The CNN is a small piece; the lightbox geometry is what makes scratches visible to the sensor in the first place. If the lighting is wrong, no model will save you. If the lighting is right, even classical contour detection works.

---

## Hardware stack

| Part | Spec |
|------|------|
| Camera | OV2710 USB Camera Module, 2 MP |
| Lens | 4 mm M12-mount CCTV lens (stock 160° wide-angle was swapped out — too distorted for fine features) |
| Illumination | Two LED strips mounted on the **top** side of the enclosure, each fronted by a scattering/diffusion plate |
| Enclosure | Closed box — ambient light excluded |

Total optics BOM is under $50. This is deliberate: the point is that the *geometry* carries the signal, not the camera.

---

## Illumination principle (the core insight)

> "Light should be dissipated equally on the bottom side to highlight scratches on the screen and to avoid direct reflections onto the camera which can lead to the appearance of light reflections."

Unpacked:

1. **Even diffuse fill across the device surface** — no bright or dark patches. Diffusion plates in front of the LED strips do this work.
2. **No specular path from LED → screen → camera.** If the LED, screen, and camera form a mirror-reflection geometry, the LED image lands in the camera and saturates the sensor, drowning out any scratch signal. The top-mounted strips are positioned so their reflection angle bounces *away* from the lens.
3. **Scratches then appear as bright scattered lines on a dark screen.** The intact screen surface reflects light away from the camera (dark background); scratches scatter light in all directions, so some of it reaches the camera (bright foreground). This is the standard **dark-field** principle — you light the subject such that only defects send light back to the sensor.

This is the opposite of bright-field, where you want uniform illumination to land in the camera and defects appear as dark spots against a bright background. Dark-field gives much higher contrast for sub-pixel linear features like scratches.

### Tension with cross-polarization

Cross-polarized imaging kills specular reflections to reveal subsurface/color information. But **scratches need specular scatter to be visible** — killing specular also kills the scratch signal. A station that wants both glare-free screen-content capture *and* scratch detection likely needs two separate captures, not one.

---

## Processing pipeline

Hybrid: CNN for segmentation, classical CV for defect detection. No end-to-end scratch-classifier CNN.

1. **Screen segmentation (U-Net).** A U-Net convolutional network produces a binary mask of the phone screen region within the frame. This is the only deep-learning step.
2. **Preprocessing.** Contrast enhancement on the masked region to emphasize defects. Article does not name the specific filter.
3. **Background removal.** Multiply by the U-Net mask to zero out non-screen pixels.
4. **Clean + binarize.** Remove small noise objects and random stray pixels, then threshold to a binary defect map.
5. **Contour detection.** Standard `cv2.findContours`-style contour extraction on the binary map.
6. **Filter.** Shape/size/aspect-ratio filtering on contours to keep real scratches and reject noise.

### Why hybrid beats end-to-end on this task

- **Data efficiency.** U-Net for screen segmentation needs far fewer labels than an end-to-end scratch grader (screens are visually consistent; screen *defects* are wildly varied).
- **Interpretability.** Each scratch is a contour with coordinates, length, and area — you can measure it, localize it, and show it to a human. An end-to-end classifier just says "C".
- **No background shortcut.** The segmentation step forces the defect detector to only look at screen pixels. The model cannot cheat by reading the background tray, lighting, or device bezel.
- **Debuggable.** Each stage produces an image you can eyeball. When it fails you know which stage failed.

---

## What the article does NOT say

Omitted — this is an engineering writeup, not a paper. None of the following are documented:

- Dataset size, sourcing, or label distribution
- U-Net training recipe (loss, optimizer, epochs, augmentation)
- Performance metrics (IoU, precision, recall, scratch-level F1)
- Threshold/contour-filter parameter values
- Minimum detectable scratch size
- Per-frame processing latency
- How they handle screen-on vs. screen-off content
- How they handle curved-edge OLED screens

The companion article on generic surface defect detection claims >50 FPS with OpenCV + Python, ~10 μm resolution on polished stainless steel, and use of "blob detection, edge detection with find contours, adaptive color filtering, mathematical morphology, image histogram analysis" — but that's a different setup (dark-field with red coherent and white light sources) and doesn't use U-Net.

---

## Transferable lessons for our grading station

1. **Lightbox geometry is the highest-leverage variable.** Before tuning the model, verify that scratches are visible to the human eye in raw captures. If they aren't, no model will find them.
2. **Dark-field > bright-field for scratches.** Position lights so specular reflection bounces away from the camera; scratches scatter light into the camera and appear bright on a dark field.
3. **Avoid cross-polarization on the scratch-detection capture.** It kills the exact signal we want. If cross-polarized capture is needed for something else, take a second non-polarized exposure for scratch detection.
4. **Segment first, detect second.** A segmentation mask eliminates the background-shortcut failure mode that Grad-CAM already caught in our current model.
5. **Classical CV on well-lit images is not obsolete.** Contour detection with shape filters works when the input has high scratch-to-background contrast. Save the deep-learning budget for problems where classical methods genuinely fail.
6. **Instance-level output beats image-level labels.** Per-scratch coordinates + length let you make defensible grading decisions ("4 scratches, longest 12 mm → grade C") instead of opaque class probabilities.
