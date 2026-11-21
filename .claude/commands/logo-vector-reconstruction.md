---
description: Rebuild a project's logo from its approved geometry plan, verify it visually, iterate ($ARGUMENTS = project name)
---

Project: `projects/$ARGUMENTS/`. If `$ARGUMENTS` is empty, ask which project.

Now implement the geometric reconstruction based on the approved geometry plan
(`projects/$ARGUMENTS/analysis/geometry-plan.md`).

Write `projects/$ARGUMENTS/construction.py` (model: `projects/owlkei/construction.py`): a
`construct(kit)` that builds every outline with `kit.build(...)` from Pieces (`arc` with a design
circle, `line`, `bez`, `auto`, shared edges with `kit.ref(...)`, `stubs` for grazing circle
intersections) and returns a `Mark`; plus `COMPARE` (the source's colors, background first, and
close-up regions). Then `python -m logokit reconstruct $ARGUMENTS` writes
`projects/$ARGUMENTS/output/reconstructed.svg`.

Requirements:

- Rebuild the logo from scratch.
- Prefer native SVG primitives whenever possible.
- Use minimal Bézier anchor points.
- Use circular arcs for genuinely circular geometry.
- Ensure smooth tangent transitions.
- Remove unnecessary corners and irregularities.
- Preserve the exact original silhouette and proportions.
- Keep the SVG editable and maintainable.

After implementation:

1. Render the SVG to PNG.
2. Create an overlay comparison against the reference
   (`.venv/bin/python -m logokit compare $ARGUMENTS --scale 4`: overlay, diff, zooms, sizes).
3. Create a difference image.
4. Inspect the result at normal size and high magnification, including where layers stack
   (an edge that continues across two shapes must stay one smooth curve).
5. Identify deviations and refine them. `python -m logokit check $ARGUMENTS` must report
   0 tangent breaks.

Write `projects/$ARGUMENTS/analysis/reconstruction-report.md` (model: the owlkei one): structure,
measured accuracy, deliberate deviations, corrections to the plan.

Do not modify the original files.

Do not claim geometric accuracy without visual verification.

Continue iterating until the reconstructed result closely matches the reference.

Optional, when asked for themed variants: write `projects/$ARGUMENTS/theming.py` (layer roles,
gradient axes, per-style overrides; model: the owlkei one), then
`python -m logokit theme $ARGUMENTS` and `.venv/bin/python -m logokit preview $ARGUMENTS`.
