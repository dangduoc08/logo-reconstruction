---
description: Analyze a project's source logo and write its geometric reconstruction plan ($ARGUMENTS = project name)
---

Project: `projects/$ARGUMENTS/` (README.md › "Add a project" describes the layout). If
`$ARGUMENTS` is empty, ask which project.

I want you to act as a senior vector graphics engineer specializing in geometric logo reconstruction.

Inspect both:
- `projects/$ARGUMENTS/reference/original.png` (if it exists)
- `projects/$ARGUMENTS/source/original.svg`

My goal is to reconstruct the existing logo from scratch using precise geometric primitives and Bézier curves.

IMPORTANT:
Do not modify any files yet, except the plan below.

Analyze the reference image and existing SVG. Measure, don't eyeball: `logokit.build.load_source`
parses the source paths; `logokit.geometry` has circle and line fits (`fit_circle`, `fit_line`,
`prim_dev`) and intersections. Keep measuring scripts in the scratchpad, not in the repository.

Identify:
1. Fundamental geometric shapes.
2. Circles, arcs, ellipses and rounded rectangles.
3. Custom Bézier paths.
4. Symmetry and geometric relationships.
5. Negative spaces and intersections.
6. Unnecessary anchor points and irregular curves in the original SVG.
7. Areas where the original design can be reconstructed with simpler geometry.

Create `projects/$ARGUMENTS/analysis/geometry-plan.md` containing a detailed reconstruction plan
(model: `projects/owlkei/analysis/geometry-plan.md`), ending with numbered decisions for the owner.

Preserve the original visual identity, silhouette, proportions and composition exactly.

Do not redesign the logo.
