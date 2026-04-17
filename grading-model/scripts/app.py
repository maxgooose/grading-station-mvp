"""
Drag-and-drop web UI for the grading model.
Run:  python3 scripts/app.py
Open: http://localhost:7860
"""

import os
import sys
import ssl
from pathlib import Path

sys.stdout.reconfigure(line_buffering=True)

import certifi
os.environ.setdefault("SSL_CERT_FILE", certifi.where())
ssl._create_default_https_context = ssl.create_default_context

import torch
from PIL import Image
import numpy as np
import pillow_heif
import gradio as gr

# Shared inference primitives.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from predict import (
    CLASSES,
    DEVICE,
    DEFAULT_TTA_PASSES,
    latest_run,
    load_model,
    load_temperature,
    load_threshold,
    predict_with_tta,
    label_from_probs,
)
from gradcam import (
    GradCAM,
    PREP as GRADCAM_PREP,
    display_pil_224,
    overlay as overlay_heatmap,
)

pillow_heif.register_heif_opener()

ROOT = Path(__file__).resolve().parent.parent

RUN_DIR = latest_run()
print(f"[run] {RUN_DIR}")
print(f"[device] {DEVICE}")

MODEL = load_model(RUN_DIR)
TEMPERATURE = load_temperature(RUN_DIR)
C_THRESHOLD = load_threshold(RUN_DIR)
print(f"[calibration] T={TEMPERATURE:.4f}  c_threshold={C_THRESHOLD:.2f}")

# Grad-CAM needs grads on the model, even in eval mode.
for _p in MODEL.parameters():
    _p.requires_grad = True
CAM = GradCAM(MODEL, MODEL.features[-1])
C_IDX = CLASSES.index("C")


def run_gradcam(image_path) -> Image.Image:
    """Run a single-view Grad-CAM for class C. Returns a PIL image overlay."""
    pil = Image.open(image_path).convert("RGB")
    display = display_pil_224(pil)
    x = GRADCAM_PREP(pil).unsqueeze(0).to(DEVICE)
    heatmap, _ = CAM(x, target_class=C_IDX)
    mixed = overlay_heatmap(display, heatmap)  # [H, W, 3] float 0..1
    mixed_u8 = (mixed * 255).clip(0, 255).astype(np.uint8)
    return Image.fromarray(mixed_u8)


def classify_one(image_path):
    """Returns (label, [P_B, P_C]) from the calibrated model."""
    probs = predict_with_tta(
        MODEL, image_path, temperature=TEMPERATURE, tta_passes=DEFAULT_TTA_PASSES
    )
    label = label_from_probs(probs, C_THRESHOLD)
    return label, probs


def classify_batch(files):
    if not files:
        return [], "No files uploaded.", []
    rows = []
    heatmaps = []
    counts = {c: 0 for c in CLASSES}
    for f in files:
        path = f if isinstance(f, str) else f.name
        try:
            pred, probs = classify_one(path)
            rows.append([
                Path(path).name,
                pred,
                f"{probs[0] * 100:.1f}%",
                f"{probs[1] * 100:.1f}%",
            ])
            counts[pred] += 1
            try:
                overlay_pil = run_gradcam(path)
                caption = f"{Path(path).name} • {pred} • P_C={probs[1]:.2f}"
                heatmaps.append((overlay_pil, caption))
            except Exception as cam_err:
                print(f"[gradcam] failed on {Path(path).name}: {cam_err}")
        except Exception as e:
            rows.append([Path(path).name, "ERROR", str(e)[:30], ""])
    summary = (
        f"**{len(rows)} image(s) classified** — predicted B: {counts['B']}, "
        f"predicted C: {counts['C']}  •  heatmap shows 'why C?'"
    )
    return rows, summary, heatmaps


HIDE_FOOTER_CSS = """
footer { display: none !important; }
.footer { display: none !important; }
.show-api { display: none !important; }
.built-with { display: none !important; }
div.svelte-mpyp5e { display: none !important; }
"""

with gr.Blocks(title="Grading Model POC", css=HIDE_FOOTER_CSS) as demo:
    gr.Markdown(
        f"# Grading Model POC\n"
        f"**Run:** `{RUN_DIR.name}`  •  **Device:** `{DEVICE}`  •  "
        f"**Classes:** {', '.join(CLASSES)}  •  "
        f"**C threshold:** `{C_THRESHOLD:.2f}` (calibrated, T={TEMPERATURE:.2f})\n\n"
        f"Drag and drop one or more images (HEIC, JPEG, PNG) — the model will predict Grade B vs Grade C for each."
    )
    with gr.Row():
        with gr.Column(scale=1):
            inp = gr.Files(
                label="Upload images (HEIC, JPEG, PNG)",
                file_count="multiple",
                file_types=["image", ".heic", ".HEIC", ".heif"],
            )
            btn = gr.Button("Classify all", variant="primary")
        with gr.Column(scale=2):
            summary = gr.Markdown("")
            out = gr.Dataframe(
                headers=["image", "prediction", "B %", "C %"],
                datatype=["str", "str", "str", "str"],
                label="Results",
                wrap=True,
            )

    gr.Markdown("### Grad-CAM — where the model is looking (red = high attention for class C)")
    gallery = gr.Gallery(
        label="Heatmaps",
        show_label=False,
        columns=4,
        height="auto",
        preview=True,
    )

    btn.click(fn=classify_batch, inputs=inp, outputs=[out, summary, gallery])
    inp.change(fn=classify_batch, inputs=inp, outputs=[out, summary, gallery])


if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7860, show_error=True, inbrowser=True)
