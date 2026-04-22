"""
Scratch detection — pure line-segment approach.

"Just look for thin lines." That's exactly what Line Segment Detector does:
it finds straight line segments directly from the gradient field, classified
by contrast and length. No blobs, no ridges, no morphology games.

Pipeline:
  1. FIND THE DEVICE — background is pre-removed (white). Threshold, fill,
     small inset to skip the literal bezel.
  2. DETECT LINE SEGMENTS — OpenCV's LSD on the CLAHE-equalized grayscale.
     Returns every line (x1, y1, x2, y2). Each has a length and a gradient
     strength. We filter:
       * keep segments with length in [MIN_LEN, MAX_LEN]
       * keep only segments that lie inside the device
       * rasterize the kept segments onto a binary mask
  3. GROUP NEARBY SEGMENTS — dilate the rasterized-segment mask; nearby
     scratches merge into one region. Each region = one annotated box.
  4. BOX each region using the tight bounding box of the original
     (undilated) segment pixels inside it. Filter small dust and overlarge
     chains.
"""

import os
import json
import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
IN = os.path.join(HERE, "input.jpg")
GT = os.path.join(HERE, "ground_truth.json")
OUT = lambda name: os.path.join(HERE, name)

# --- Device detection ---
BEZEL_INSET_PX = 10

# --- Line segment filtering ---
MIN_LEN = 6                    # shorter than this = noise
MAX_LEN = 120                  # longer than this = bezel / reflection edge, not a scratch

# --- Grouping ---
GROUP_DILATE_PX = 10

# --- Box filtering ---
MIN_GROUP_AREA = 20
MIN_BBOX_DIM = 6
MAX_BBOX_DIM_FRAC = 0.40


# -----------------------------------------------------------------------------
def find_device_mask(gray):
    _, fg = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
    open_k = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    fg = cv2.morphologyEx(fg, cv2.MORPH_OPEN, open_k)
    close_k = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 25))
    fg = cv2.morphologyEx(fg, cv2.MORPH_CLOSE, close_k)

    contours, _ = cv2.findContours(fg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None, None
    largest = max(contours, key=cv2.contourArea)
    if cv2.contourArea(largest) < 0.05 * gray.size:
        return None, None

    mask = np.zeros_like(gray)
    cv2.drawContours(mask, [largest], -1, 255, -1)
    if BEZEL_INSET_PX > 0:
        erode_k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,
                                            (BEZEL_INSET_PX, BEZEL_INSET_PX))
        mask = cv2.erode(mask, erode_k)
    return mask, largest


def detect_lines(gray, device_mask):
    # Boost local contrast so faint scratches get crisp gradients
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(16, 16))
    eq = clahe.apply(gray)

    lsd = cv2.createLineSegmentDetector()
    lines, _, _, _ = lsd.detect(eq)
    if lines is None:
        return [], np.zeros_like(gray)

    # Rasterize accepted line segments onto a binary mask
    line_mask = np.zeros_like(gray)
    kept = []
    for l in lines:
        x1, y1, x2, y2 = l[0]
        length = float(np.hypot(x2 - x1, y2 - y1))
        if length < MIN_LEN or length > MAX_LEN:
            continue
        # Skip if midpoint is outside the device
        mx, my = int((x1 + x2) / 2), int((y1 + y2) / 2)
        if my < 0 or my >= device_mask.shape[0]:
            continue
        if mx < 0 or mx >= device_mask.shape[1]:
            continue
        if device_mask[my, mx] == 0:
            continue
        kept.append((x1, y1, x2, y2, length))
        cv2.line(line_mask, (int(round(x1)), int(round(y1))),
                 (int(round(x2)), int(round(y2))), 255, 1)

    # Mask strictly to device interior
    line_mask = cv2.bitwise_and(line_mask, device_mask)
    return kept, line_mask


def group_and_box(line_mask, device_mask):
    dilate_k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,
                                         (GROUP_DILATE_PX, GROUP_DILATE_PX))
    dilated = cv2.dilate(line_mask, dilate_k)
    dilated = cv2.bitwise_and(dilated, device_mask)

    x0, y0, dw, dh = cv2.boundingRect(device_mask)
    max_bbox_w = int(MAX_BBOX_DIM_FRAC * dw)
    max_bbox_h = int(MAX_BBOX_DIM_FRAC * dh)

    n, labels, stats, _ = cv2.connectedComponentsWithStats(dilated, connectivity=8)
    boxes = []
    for i in range(1, n):
        group = (labels == i) & (line_mask > 0)
        ys, xs = np.where(group)
        if ys.size == 0:
            continue
        true_area = int(len(xs))
        if true_area < MIN_GROUP_AREA:
            continue
        x_min, x_max = int(xs.min()), int(xs.max())
        y_min, y_max = int(ys.min()), int(ys.max())
        w = x_max - x_min + 1
        h = y_max - y_min + 1
        if w < MIN_BBOX_DIM and h < MIN_BBOX_DIM:
            continue
        if w > max_bbox_w or h > max_bbox_h:
            continue
        boxes.append((x_min, y_min, w, h, true_area))
    return boxes, dilated


def build_bw_canvas(gray, device_mask, line_mask):
    canvas = np.full_like(gray, 255)
    canvas[device_mask > 0] = line_mask[device_mask > 0]
    return canvas


def draw_boxes(img_bgr, boxes, footer_txt):
    out = img_bgr.copy()
    for x, y, w, h, _ in boxes:
        cv2.rectangle(out, (x, y), (x + w, y + h), (0, 0, 255), 2)
    cv2.putText(out, footer_txt, (10, out.shape[0] - 15),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2, cv2.LINE_AA)
    return out


# -----------------------------------------------------------------------------
# Evaluation against ground-truth JSON
# -----------------------------------------------------------------------------
def box_iou(a, b):
    ax1, ay1, ax2, ay2 = a[0], a[1], a[0] + a[2], a[1] + a[3]
    bx1, by1, bx2, by2 = b[0], b[1], b[0] + b[2], b[1] + b[3]
    ix1, iy1 = max(ax1, bx1), max(ay1, by1)
    ix2, iy2 = min(ax2, bx2), min(ay2, by2)
    iw, ih = max(0, ix2 - ix1), max(0, iy2 - iy1)
    inter = iw * ih
    ua = a[2] * a[3] + b[2] * b[3] - inter
    return inter / ua if ua > 0 else 0.0


def evaluate(pred_boxes, gt_path, iou_thr=0.20):
    if not os.path.exists(gt_path):
        return None
    with open(gt_path) as f:
        data = json.load(f)
    gt = [(b['x'], b['y'], b['w'], b['h']) for b in data['boxes']]
    pred = [(x, y, w, h) for x, y, w, h, _ in pred_boxes]

    # Greedy matching by best IoU
    matched_gt = set()
    tp = 0
    for p in pred:
        best_j, best_iou = -1, 0.0
        for j, g in enumerate(gt):
            if j in matched_gt:
                continue
            i = box_iou(p, g)
            if i > best_iou:
                best_iou, best_j = i, j
        if best_iou >= iou_thr:
            matched_gt.add(best_j)
            tp += 1
    fp = len(pred) - tp
    fn = len(gt) - len(matched_gt)
    prec = tp / (tp + fp) if (tp + fp) else 0.0
    rec = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
    return {
        'tp': tp, 'fp': fp, 'fn': fn,
        'precision': prec, 'recall': rec, 'f1': f1,
        'n_pred': len(pred), 'n_gt': len(gt),
        'iou_thr': iou_thr,
    }


# -----------------------------------------------------------------------------
def main():
    raw = cv2.imread(IN, cv2.IMREAD_UNCHANGED)
    if raw is None:
        raise SystemExit(f"Could not read {IN}")
    if raw.ndim == 3 and raw.shape[2] == 4:
        bgr = raw[:, :, :3].astype(np.float32)
        alpha = raw[:, :, 3:4].astype(np.float32) / 255.0
        img = (bgr * alpha + 255.0 * (1 - alpha)).astype(np.uint8)
    else:
        img = raw
    print(f"Loaded {IN}: {img.shape}")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    device_mask, device_contour = find_device_mask(gray)
    if device_mask is None:
        raise SystemExit("Could not find device")

    kept_lines, line_mask = detect_lines(gray, device_mask)
    print(f"Line segments kept after filtering: {len(kept_lines)}")

    boxes, dilated = group_and_box(line_mask, device_mask)
    print(f"Found {len(boxes)} scratch groups")

    # Evaluate
    metrics = evaluate(boxes, GT)
    if metrics:
        m = metrics
        print(f"--- vs ground truth ({m['n_gt']} boxes, IoU ≥ {m['iou_thr']}) ---")
        print(f"  TP: {m['tp']}   FP: {m['fp']}   FN: {m['fn']}")
        print(f"  precision: {m['precision']:.2f}")
        print(f"  recall:    {m['recall']:.2f}")
        print(f"  F1:        {m['f1']:.2f}")

    # Outputs
    bw_canvas_gray = build_bw_canvas(gray, device_mask, line_mask)
    bw_canvas_bgr = cv2.cvtColor(bw_canvas_gray, cv2.COLOR_GRAY2BGR)
    bw_out = draw_boxes(bw_canvas_bgr, boxes, f"{len(boxes)} scratch marks")
    cv2.imwrite(OUT("output_bw.jpg"), bw_out)

    color_out = draw_boxes(img, boxes, f"{len(boxes)} scratch marks")
    cv2.imwrite(OUT("output.jpg"), color_out)

    cv2.imwrite(OUT("debug_device_mask.jpg"), device_mask)
    cv2.imwrite(OUT("debug_lines.jpg"), line_mask)
    cv2.imwrite(OUT("debug_dilated.jpg"), dilated)


if __name__ == "__main__":
    main()
