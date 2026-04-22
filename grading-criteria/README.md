# Grading Criteria

The label schemas the grading model must output. The inspection covers the **entire device** — screen, back, and all edges — not a single view.

**Two customer rubrics:**
1. **Universal** — 5 grades (A, B, C(amz), C, D). **Starting here.**
2. **Blueberry** — 3 grades (Excellent, Good, Acceptable). **Later.**

---

## Universal scale (primary)

**Order, best → worst:** A > B > C(amz) > C > D

| Grade | Definition |
|---|---|
| **A** | Pristine. No scratches. Just as new. *Rare in practice — low-frequency class, handle as rare-class, not balanced.* |
| **B** | Minimal scratches. Barely-seen few scratches on the screen. |
| **C(amz)** | Minimal scratches possible on **both sides** of the device (screen and back). Scratches must not be deep. |
| **C** | Harder and worse than C(amz). Scratches may be deeper, bigger quantity throughout the device, slightly deeper overall. |
| **D** | **One deep scratch is enough** to classify as D. Or: too many scratches and it's too messed up — quantity too high, scratches too deep, visible irregularity. |

### Decision signals the model needs

- **Scratch count** — "few" vs "bigger quantity" vs "too many" separates B → C → D.
- **Scratch depth** — "not deep" vs "a little deep" vs "deep" separates C(amz) → C → D.
- **Per-surface distribution** — screen only (B) vs screen + back (C(amz)+). Needs per-surface segmentation, not a single whole-device mask.
- **Any-one-deep-scratch rule** — D is triggered by a single deep scratch regardless of overall count. The grading head must apply the D rule as an OR gate before count/depth thresholds.
- **Visible irregularity** — catch-all for D. Dents, cracks, chips beyond scratch taxonomy also trigger D.

### Implied grading-head logic (first draft)

```python
# pseudo-rules over the per-surface, per-defect instance list
if any(defect.depth == "deep" for defect in all_defects): return "D"
if total_scratch_count > VERY_HIGH or visible_irregularity: return "D"

if scratches_present(screen) and scratches_present(back):
    if all(d.depth != "a_little_deep" for d in all_scratches): return "C(amz)"
    else: return "C"

if scratches_present(screen) only and all_minimal:
    return "B"

if no_scratches_anywhere: return "A"
```

Depth thresholds ("deep", "a little deep", "not deep") and the `VERY_HIGH` count need to be calibrated against labeled data. They are **not** constants — they need to be learnable or tunable once labeling is under way.

---

## Blueberry scale (later)

Three grades: **Excellent, Good, Acceptable**. Definitions pending — will be documented here when the Blueberry customer work starts.

---

## Mapping to the current POC data

The existing `software/grading-model/data/` has only two folders: `B/` and `C/`. Per prior project context:

- `B/` — true Universal **B** grade.
- `C/` — actually Universal **C(amz)**, labeled "C" only for convenience during the POC.

Future label schemas and directory layouts should disambiguate. Suggested target:

```
software/grading-model/data/
├── A/          (rare — may start empty)
├── B/
├── C_amz/      (renamed from existing C/)
├── C/
└── D/
```

---

## Implications for the rest of the stack

| Component | What this criteria forces |
|---|---|
| [Software](../software/README.md) | Per-surface, per-defect **instance segmentation** — not whole-device classification. Grading head must apply the "one deep scratch = D" rule as an OR gate. A-class needs rare-class handling. |
| [Hardware](../hardware/README.md) | Capture must cover **every surface** — screen, back, and all edges. The U-cradle + multi-camera layout is designed for exactly this. |
| [Lighting](../lighting/README.md) | Depth ("deep" vs "not deep") is what separates C(amz)/C/D. Dark-field scratch capture is the only way to reliably see scratch geometry; bright-field alone cannot distinguish a surface scratch from a deep gouge. |

---

## Open questions

1. **What counts as "deep"?** Needs a measurable proxy — pixel width? dark-field intensity? length? Until labeling starts, this is subjective.
2. **Edge scratches** — which grade bucket do they fall into? The current definitions focus on screen + back. Edges are probably treated as "visible irregularity" under D if severe.
3. **Non-scratch defects** (dents, cracks, chips, paint wear, stains) — the criteria talk about scratches almost exclusively. Where do these land? Likely D for anything beyond cosmetic, but the rubric needs to be explicit.
4. **Inter-annotator agreement** — two graders will disagree on B vs C(amz) on borderline devices. A labeling protocol with reference images per class is needed before bulk labeling.
