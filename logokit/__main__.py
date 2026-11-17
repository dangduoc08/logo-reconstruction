"""logokit command line.

    python -m logokit reconstruct <project> [--quiet]   build output/reconstructed.svg
    python -m logokit check <project>                   node counts and tangent breaks
    python -m logokit compare <project> [--scale N]     raster metrics + analysis/compare/ (numpy, Pillow, SciPy)
    python -m logokit theme <project>                   output/styles/<style>-<mode>.svg
    python -m logokit preview <project>                 output/styles/preview.png (Pillow)
    python -m logokit all <project>                     reconstruct, check, theme
"""
from __future__ import annotations

import argparse
import sys

from .project import Project


def reconstruct(p: Project, quiet=False):
    from .build import report, svg_text
    p.output.mkdir(parents=True, exist_ok=True)
    p.reconstructed.write_text(svg_text(p.mark, f"logokit from projects/{p.name}/construction.py"))
    print(f"wrote {p.reconstructed.relative_to(p.dir.parent.parent)}")
    if not quiet:
        print(report(p.mark))


def check(p: Project) -> int:
    from .check import check as run
    return run(p.reconstructed)


def compare(p: Project, scale: float):
    from .build import Frame
    from .compare import compare as run
    f = Frame(p.mark)
    cfg = p.construction.COMPARE
    run(p.source, p.reconstructed, p.compare_dir, (f.ox, f.oy, f.w, f.h), cfg["colors"],
        cfg.get("zooms", {}), scale=scale, reference_png=p.reference_png)


def theme(p: Project):
    from .theme import write_all
    written = write_all(p.reconstructed, p.styles_dir, p.style_set(), p.theming)
    print(f"wrote {len(written)} files to {p.styles_dir.relative_to(p.dir.parent.parent)}/")


def preview(p: Project):
    from .preview import contact_sheet
    out = p.styles_dir / "preview.png"
    contact_sheet(p.style_set(), p.styles_dir, out)
    print(f"wrote {out.relative_to(p.dir.parent.parent)}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="logokit", description=__doc__.split("\n\n")[0])
    ap.add_argument("command", choices=["reconstruct", "check", "compare", "theme", "preview", "all"])
    ap.add_argument("project")
    ap.add_argument("--scale", type=float, default=2.0, help="compare: pixels per source unit")
    ap.add_argument("--quiet", action="store_true", help="reconstruct: no deviation report")
    args = ap.parse_args(argv)
    p = Project(args.project)
    if args.command == "reconstruct":
        reconstruct(p, args.quiet)
    elif args.command == "check":
        return 1 if check(p) else 0
    elif args.command == "compare":
        compare(p, args.scale)
    elif args.command == "theme":
        theme(p)
    elif args.command == "preview":
        preview(p)
    else:
        reconstruct(p, quiet=True)
        if check(p):
            return 1
        theme(p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
