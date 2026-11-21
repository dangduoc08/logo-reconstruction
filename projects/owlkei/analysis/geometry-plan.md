# Owl logo — geometric reconstruction plan

Status: analysis only. No source file has been changed.

## 0. Inputs and method

| Input | State |
|---|---|
| `reference/original.png` | **Missing.** The folder doesn't exist. This analysis uses a raster of `source/original.svg` rendered with `rsvg-convert` as the visual reference. Add the PNG before the reconstruction starts if it differs from the SVG. |
| `source/original.svg` | A Recraft AI traced vector (C2PA metadata says "Recraft AI Generated Image"). viewBox `0 0 5902 3219`, shown at 1408×768 with `preserveAspectRatio="none"`. It holds 10 paths, about 12 kB of C2PA metadata and a full-canvas white rectangle. |

How the numbers were measured:

- Every path was parsed and each Bézier segment was sampled 12 to 40 times.
- Arcs were found with least-squares circle fits (Kåsa). The table reports the maximum and mean radial deviation.
- Straight edges were found with total-least-squares line fits.
- Concentricity was tested by measuring the distance of each sample from a candidate center.
- All coordinates are in source units, where 1 unit is about 0.24 px at the original 1408 px width.

The mark occupies only `x 2427–3481, y 524–1958`, which is **1054 × 1434 units** (aspect ratio 0.735). The rest of the canvas is empty white.

## 1. Inventory of the original SVG

| # | Fill | Role | Anchors | Bbox (x0,y0 – x1,y1) | Notes |
|---|---|---|---|---|---|
| 0 | `#FFFFFF` | Background rectangle | 5 | full canvas | Remove: the mark should be transparent |
| 1 | `#222C68` navy | Upper head: 3 crest feathers, crown, 2 ear tufts, rear bump, nose bridge, left pupil's lower rim | 90 | 2427,524 – 3473,1666 | 10 segments under 10 units long, 21 tangent kinks |
| 2 | gradient `#CA8F3A → #A88554` | Left brow band | 16 | 2466,1267 – 2860,1617 | Overlaps #1 and #3 |
| 3 | `#222C68` | Left pupil (visible part) | 7 | 2665,1415 – 2818,1552 | Duplicates part of #1's outline |
| 4 | `#222C68` | Lower face and body: chin bowl, left cheek spike, right cheek bump | 31 | 2547,1397 – 3481,1958 | |
| 5 | `#C68B38` gold | Beak | 13 | 2903,1578 – 3050,1830 | 4 near-zero segments at the tip |
| 6 | `#C68B38` | Right cheek stripe (crescent) | 18 | 2965,1690 – 3248,1956 | Dent at 3003–3065, 1894–1936 |
| 7 | `#1C1933` | Sliver on #6 | 9 | 3003,1894 – 3065,1936 | **Trace artifact**: a dark seam visible inside the gold stripe |
| 8 | `#1F1E40` | Sliver on #6 | 13 | 3003,1919 – 3021,1936 | **Trace artifact**: 10 of its 12 segments are under 10 units |
| 9 | `#222C68` | Right pupil with highlight notch | 10 | 3026,1369 – 3210,1550 | |

There are **202 anchors** in total (197 without the background). Three navy tones exist (`#222C68`, `#1F1E40`, `#1C1933`), but only `#222C68` is intended.

## 2. Fundamental geometry (measured)

### 2.1 Circles

| Element | Center | Radius | Fit max / mean deviation | Source segments |
|---|---|---|---|---|
| Right pupil | (3113.6, 1455.5) | **98.2** | 1.0 / 0.26 | #9 0–5 |
| Left pupil | (2755.0, 1454.9) | **98.7** | 0.6 / 0.19 | #3 4–6, #1 42–44 |
| Right eye white (disc) | (3113.5, 1454.9) | **212.0** | 1.9 / 0.39 | #1 31–35 + #4 0–2 |
| Left eye white (disc) | about (2755, 1455) | **about 212** (210–220 from the pupil center, mean 211.9) | — | #4 16–21 |
| Pupil highlight (cut-out) | (3160.9, 1407.5) | **37.7** | 0.9 / 0.22 | #9 6–9 |
| Head / chin bowl | about (3000, 1510) | **about 447** (444–450 along the whole bottom and left side) | 1.3 / 0.36 | #4 7–14 |

### 2.2 Secondary arcs (one circle each, not concentric with anything)

| Element | Center | Radius | Max deviation |
|---|---|---|---|
| Cheek stripe outer edge | (2896.2, 1598.7) | 365.2 | 0.4 |
| Cheek stripe inner edge | (2857.3, 1637.5) | 330.5 | 0.4 |
| Beak left edge | (3165.3, 1713.1) | 262.7 | 0.9 |
| Beak inner (lower right) edge | (3118.0, 1839.4) | 191.7 | 0.1 |
| Right cheek bump | (3438.0, 1501.0) | 114.3 | 1.4 |
| Ear tuft 1, upper edge | (3117.7, 624.8) | 461.2 | 0.7 |
| Ear tuft 1, under edge | (3270.4, 937.7) | 199.0 | 0.9 |
| Ear tuft 2, upper edge | (3309.6, 867.6) | 265.3 | 0.3 |
| Left feather tip arc | (2468.7, 952.0) | 103.4 | 1.3 |

### 2.3 Straight edges (crest feathers)

All feather sides are straight lines with a deviation of at most 0.7 units. Angles are measured from vertical; positive means leaning right.

| Feather | Outer / left edge | Inner / right edge | Taper | Width at mid-length |
|---|---|---|---|---|
| Left (L) | −12.7° (through 2479,1092) | −8.7° (that side is curved: deviation 11.7, so it needs a Bézier) | about 4° | about 129 |
| Middle (M) | +9.0° (through 2644,981) | +5.9° (through 2817,789) | about 3° | about 141 |
| Right (R) | +26.3° (through 2924,786) | +24.0° (through 3052,883) | about 2.3° | about 158 |

- **Fan pivot:** the left edges of L, M and R meet near **(2565, 1500)**, within ±25 units. The crest is a fan of three tapered blades radiating from a point below and left of the left eye.
- **Angular steps:** 21.7° (L→M) and 17.3° (M→R). These are not equal, so the steps stay as measured.
- **Widths:** each blade is about 12% wider than the previous one, from left to right.

## 3. Geometric relationships

1. **The eyes are identical.** Both pupils have a radius of about 98.5 and both whites have a radius of 212, with their centers on one horizontal line at **y ≈ 1455**. The centers are 358.6 apart. The white/pupil ratio is 2.155, and the highlight/pupil ratio is 0.383.
2. **The right eye is concentric**: its pupil and white share the center (3113.5, 1455).
3. **The beak's top edge and the lower body's top edge lie on the right eye's white circle** (r = 212, deviation under 2). The eye disc is the cutter that shapes both.
4. **The two eye discs overlap**: 2 × 212 > 358.6. The left eye is mostly covered by the head and brow (a ¾ view), so only a crescent of its white and part of its pupil show.
5. **The highlight notch:** the highlight center sits 67.5 units from the pupil center at 45° (up and right). Because 67.5 + 37.7 = 105.2 > 98.2, the highlight breaks through the pupil edge and opens into the white ring. The notch is a boolean result, not a drawn curve.
6. **The head bowl is one circle**, center (3000, 1510), r = 447. Its center is about 55 units below the eye line and about 66 right of the midpoint between the pupils. The bottom of the mark (y 1958) is the circle's lowest point.
7. **The crest feather tips share a motif:** a sharp outer-left corner, then one convex arc sweeping down to the inner-right edge (a "blade" tip). The ear tufts repeat it, pointing to the upper right.
8. **Feather-root notches** sit at nearly the same height: y 1241 (left of L), 1258 (L|M), 1224 (M|R) and 1231 (R|crown). Each is a sharp V with a tiny fillet.
9. **No bilateral symmetry.** The composition is a deliberate ¾ turn: the left eye is occluded, the crest fans left to right, and the tufts and cheek bump sit on the right. Rotational and mirror symmetry don't apply. The rhythm comes from the repeated radii (212, 98) and the fan.

## 4. Negative spaces and overlaps

| Negative space | Built from |
|---|---|
| Right eye white ring | Disc r 212 minus pupil r 98.2, with the highlight r 37.7 carved out of the pupil |
| Left eye white crescent | Left disc r 212 minus the head (#1), the brow (#2) and the pupil |
| Gutter between head and beak | Variable width, about 37.6 |
| Gutter between nose bridge and body | About 43.8 |
| Gutter between ear and cheek bump | About 25.7 |
| Left cheek pocket | About 118 between brow and cheek; bounded by the left eye circle below |
| Tuft gaps and feather V-notches | Background |

Overlaps that must become clean layering or booleans:

- **Brow (#2) over head (#1):** the brow's lower edge duplicates #1's outline at segments 44–47.
- **Left pupil (#3) under the brow:** #3, #1 (segments 42–43) and #2 (its last segments) each trace the same lower pupil arc. That is three copies of one curve.
- **Beak (#5) against body (#4):** they share an edge with zero gap, so the body is cut by the beak (#4 segments 23–29 reproduce the beak outline).

The gutter widths differ (25.7 / 37.6 / 43.8). To preserve the identity exactly, they stay as measured: unifying them would be a redesign (see decision D4).

## 5. Unnecessary anchors and irregular curves

| Location | Problem | Fix |
|---|---|---|
| #1 segments 7–10 (2830,1195 → 2807,1231 → 2812,1227 → 2828,1211) | A micro-zigzag at the R / crown notch | One corner plus one fillet |
| #1 segments 19–21, 27–28, 52–53, 59–60, 62–64, 74–76, 78–79 | Segments 1 to 5 units long between collinear handles | Merge into neighbors |
| #1 segments 0–5 and 83–88 | The right feather is split into 11 segments, but its sides are straight | 2 lines + 1 tip arc |
| #1 segments 65–73 | The middle feather uses 9 segments | 2 lines + 1 tip arc |
| #1 segments 31–35 | The eye ring is drawn with 5 cubics | One circular arc (`A`) |
| #4 segments 7–14 | The head bowl is drawn with 8 cubics | One arc |
| #4 segments 14–16 (2550,1532 → 2547,1504 → 2547,1495) | A 3-segment spike tip | One sharp corner |
| #5 segments 6–9 (2930,1802 → … → 2924,1818) | 4 segments within 10 units at the beak tip | One corner |
| #6 segments 8–13 | A dent with a dark seam (#7, #8) | One smooth inner arc; delete #7 and #8 |
| #9 segments 4–5 (3157,1369 → 3150,1371) | A 7-unit stub where the highlight meets the pupil | Boolean of two circles |
| #2 (16 anchors) | Irregular top edge (deviation 17.6 from its best arc) | Two-cubic band with G2 joins |
| Gradient on the brow | Very subtle (`#CA8F3A → #A88554`, ΔL about 6%), and only on the brow, so it doesn't match the flat gold of the beak and stripe | Decision D1 |

## 6. Reconstruction blueprint

Coordinates stay in source units while working, so each step can be overlaid on the original. They are translated only at export (section 8).

### 6.1 Construction primitives (exact values, rounded to 0.5 units)

```
EYE_Y        = 1455
PUPIL_R      = 98.5
WHITE_R      = 212
EYE_R_C      = (3113.5, 1455)
EYE_L_C      = (2755,   1455)            # EYE_R_C.x - 358.5
HILITE_C     = EYE_R_C + 67.5 * (cos45°, -sin45°) = (3161.2, 1407.3)
HILITE_R     = 37.7
HEAD_C       = (3000, 1510)
HEAD_R       = 447
FAN_PIVOT    = (2565, 1500)
FEATHER_ANG  = L −12.7°, M +9.0°, R +26.3°   (outer edges, from vertical)
FEATHER_TAPER= L 4.0°, M 3.1°, R 2.3°
```

### 6.2 Build order (layers, back to front)

1. **Head silhouette (navy).** A union of the following:
   - **Chin bowl:** an arc on HEAD_C r 447, from the left cheek (about 2550,1500) to the right side (about 3417,1665).
   - **Right flank:** a near-straight Bézier from (3417,1665) up to (3466,1454), then the cheek bump arc (c 3438,1501, r 114.3).
   - **Rear bump** (#1 segments 25–31). It is free-form: 2 cubics, with deviation up to 13.9 from any circle.
   - **Crown:** the upper contour (#1 segments 11–16), free-form with 2 cubics. It is close to r 491 but deviates by 7.3.
   - **Ear tufts:** each is 2 arcs, (461.2 + 199.0) and (265.3 + a free under-curve), with sharp tips at (3469,917) and (3473,1073).
   - **Three crest blades:** each has 2 straight sides and 1 tip arc from the sharp outer corner to the inner side. The L blade's inner side is a single cubic (it is curved).
   - **Left cheek spike** at (2547,1495), and the left brow-side swoop (#1 segments 47–51) down to (2431,1171).
2. **Subtract from the head:** the right eye disc (EYE_R_C, r 212), the left eye disc (EYE_L_C, r 212), the white gutters (offset bands along the beak and nose, at the measured widths), the feather V-notches and the tuft gaps.
3. **Pupils (navy):**
   - Right: a circle r 98.5, minus the highlight circle (which produces the notch).
   - Left: a circle r 98.5 on EYE_L_C, clipped by the brow.
4. **Brow (gold):** a band from (2466,1267) to the tip (2868,1666). Its top edge is free-form (2 cubics) and its bottom edge follows the pupil arc. Draw it after the left pupil so it covers it, as in the original's visible result.
5. **Beak (gold):**
   - Top edge: an arc on the right eye white circle (r 212).
   - Left edge: an arc (c 3165.3,1713.1, r 262.7).
   - Inner edge: an arc (c 3118,1839.4, r 191.7).
   - The tip is a sharp corner at (2926,1830).
6. **Cheek stripe (gold):** a crescent between two arcs (r 365.2 and r 330.5), with sharp ends at (3248,1690) and (2965,1956). It carries no dark slivers.

### 6.3 Path conventions for the output

- Prefer `A` (arc) commands for true circles. Use cubic Béziers only for the free-form edges listed above, with handles at about 0.5523 × radius where an arc is approximated.
- Joins are **G1 or better** wherever the original is smooth, and **sharp corners** only at the points listed: feather and tuft tips, notches, the spike, the beak tip and the stripe ends.
- Flatten the result to a few final paths (`fill-rule="evenodd"` where holes exist):
  1. navy (head + pupils, eye holes cut),
  2. gold (beak + stripe + brow).

  Every shape is solid, so no masks, clip paths or filters are needed.
- Two colors only: `#222C68` and `#C68B38`, plus the optional brow gradient (D1).

### 6.4 Anchor budget

| Part | Original | Target |
|---|---|---|
| Head silhouette with tufts, blades and notches | 90 + 31 | about 55–65 |
| Pupils, highlight and eye holes | 17 | about 8 (arcs) |
| Brow | 16 | about 5 |
| Beak | 13 | about 4 |
| Cheek stripe and artifacts | 18 + 9 + 13 | about 4 |
| **Total** | **202** | **about 80–90** (−55% or more) |

## 7. Verification plan

1. **Overlay:** render the original and the reconstruction at the same scale (a 4096 px wide crop of the mark) and diff them per color.
2. **Acceptance:**
   - IoU of at least 99.0% per color layer.
   - A maximum edge deviation of 1.5 units on edges built from primitives, and 3 units on free-form edges.
   - Silhouette bbox within ±1 unit of `2427,524 – 3481,1958`.
3. **Visual checks:**
   - at 16, 32, 64 and 512 px,
   - on white and on dark backgrounds (the navy may need a light variant later; out of scope),
   - with no seams between abutting shapes (beak and body share an edge, so build them by boolean, never by two independently traced curves).
4. **Tools available locally:**
   - `rsvg-convert` for rasterizing,
   - plain Python for the geometry generator and the pixel diff (no numpy, Inkscape or ImageMagick installed).

## 8. Output plan (after approval)

- `output/owl-mark.svg`: the reconstructed mark, transparent background, tight viewBox with even padding. The translate is applied to the coordinates, so the file carries no `transform`.
- `output/construction.svg`: the same mark with the construction overlay (circles, fan lines, pivot, centers) for review.
- `analysis/diff.png` and an IoU report: the evidence for the acceptance criteria.
- The generator script that produces the SVG from the primitives in 6.1, so values stay editable.

## 9. Open decisions for the owner

| # | Question | Default if not answered |
|---|---|---|
| D1 | Keep the brow's subtle gradient, or make the brow flat `#C68B38` like the beak and stripe? | Keep the gradient (preserve the original) |
| D2 | Idealize near-equal values that are probably intentional (pupils 98.2 / 98.7 → 98.5; eye whites → 212; the head as one circle r 447)? Each change is ≤ 1 unit. | Yes |
| D3 | Delete the dark slivers #7 and #8 and smooth the stripe's dent (both are trace artifacts)? | Yes |
| D4 | Keep the measured gutter widths (25.7 / 37.6 / 43.8), or unify them to one width? Unifying changes the look slightly. | Keep as measured |
| D5 | Final canvas: tight square for an app icon, or tight to the mark's own aspect ratio (0.735)? | The mark's aspect ratio, with even padding |
| D6 | Provide `reference/original.png` if it differs from the SVG render. | Use the SVG render |
