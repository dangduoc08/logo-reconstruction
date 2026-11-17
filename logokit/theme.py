"""Recolor a project's reconstructed mark with a style set (styles/<set>.py), light and dark.

The geometry is untouched: only fills change, plus the outline, hard shadow and cut-outs that
some styles call for. The project's theming.py gives each layer a role (brand, accent, detail),
the gradient axes, and any per-style overrides.
"""
from __future__ import annotations

import re
from pathlib import Path


def _layers(svg: str):
    head = re.search(r"<svg[^>]*>", svg).group(0)
    vb = [float(v) for v in re.search(r'viewBox="([^"]+)"', head).group(1).split()]
    layers = re.findall(r'<path id="([^"]+)"[^>]*d="([^"]+)"', svg)
    return head, vb, layers


def _gradient(ident, axis, colors):
    (x1, y1), (x2, y2) = axis
    n = max(1, len(colors) - 1)
    out = [f'    <linearGradient id="{ident}" gradientUnits="userSpaceOnUse" '
           f'x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">']
    out += [f'      <stop offset="{i / n:g}" stop-color="{c}"/>' for i, c in enumerate(colors)]
    out.append("    </linearGradient>")
    return out


def _arcs_only(d: str) -> str:
    """The arc commands of a path as separate open subpaths (each starts where its arc starts)."""
    toks = re.findall(r"[MLCAZ]|-?[\d.]+", d)
    out, cur, start, i, cmd = [], None, None, 0, None
    sizes = {"M": 2, "L": 2, "C": 6, "A": 7}
    while i < len(toks):
        if toks[i] in "MLCAZ":
            cmd = toks[i]
            i += 1
            if cmd == "Z":
                cur = start
            continue
        args = toks[i:i + sizes[cmd]]
        i += sizes[cmd]
        end = (args[-2], args[-1])
        if cmd == "A":
            out.append(f"M {cur[0]} {cur[1]} A {' '.join(args)}")
        if cmd == "M":
            start = end
        cur = end
    return " ".join(out)


_CLOSED: dict = {}


def closed_silhouette(ds: list[str], outline: float, radius: float, region=None, outside=False,
                      gaps_only=False, holes=()) -> str | None:
    """The mark's outline (shapes plus `outline` units) with every gap narrower than about
    2 * `radius` closed (morphological closing: dilate, then erode), as a path. A hard shadow
    masked by it shows only outside the mark, never as slivers in crest notches or gutters.
    Needs skia-pathops and fontTools (requirements.txt); returns None without them."""
    key = (tuple(ds), outline, radius, repr(region), outside, gaps_only, tuple(holes))
    if key in _CLOSED:
        return _CLOSED[key]
    try:
        from fontTools.pens.svgPathPen import SVGPathPen
        from fontTools.svgLib.path import parse_path
        from pathops import LineCap, LineJoin, Path as SkPath, PathOp, op
    except ImportError:
        print("note: skia-pathops / fontTools missing (see requirements.txt): shadows not cleaned from gaps")
        _CLOSED[key] = None
        return None

    def parsed(d):
        p = SkPath()
        parse_path(d, p.getPen())
        return p

    def ring(p, width):  # the band of `width` around p's outline
        r = SkPath()
        r.addPath(p)
        r.stroke(width, LineCap.ROUND_CAP, LineJoin.ROUND_JOIN, 4)
        r.convertConicsToQuads()
        return r

    shape = SkPath()
    for d in ds:
        shape = op(shape, parsed(d), PathOp.UNION)
    if outline:
        shape = op(shape, ring(shape, 2 * outline), PathOp.UNION)
    dilated = op(shape, ring(shape, 2 * radius), PathOp.UNION)
    closed = op(dilated, ring(dilated, 2 * radius), PathOp.DIFFERENCE)
    if region:  # only inside (or, with `outside`, only outside) these (x, y, w, h) rectangles
        for x, y, w, h in ([region] if isinstance(region[0], (int, float)) else region):
            box = SkPath()
            box.moveTo(x, y); box.lineTo(x + w, y); box.lineTo(x + w, y + h); box.lineTo(x, y + h); box.close()
            closed = op(closed, box, PathOp.DIFFERENCE if outside else PathOp.INTERSECTION)
    if gaps_only:  # just what the closing added: the gaps, not the shapes or their outer edge
        closed = op(closed, shape, PathOp.DIFFERENCE)
        for kind, *v in holes:  # never inside these (eye openings)
            if kind == "circle":
                cx, cy, r = v
                closed = op(closed, parsed(f"M {cx - r} {cy} A {r} {r} 0 1 0 {cx + r} {cy} "
                                           f"A {r} {r} 0 1 0 {cx - r} {cy} Z"), PathOp.DIFFERENCE)
        # Overlap the outlines a little (they are drawn over it), or a hairline seam of
        # background shows where the fill meets them.
        closed = op(closed, ring(closed, 4), PathOp.UNION)
    pen = SVGPathPen(None, ntos=lambda v: f"{v:.1f}".rstrip("0").rstrip("."))
    closed.draw(pen)
    _CLOSED[key] = pen.getCommands()
    return _CLOSED[key]


def _shape(kind, *v, attrs=""):
    if kind == "circle":
        return f'<circle cx="{v[0]:g}" cy="{v[1]:g}" r="{v[2]:g}"{attrs}/>'
    if kind == "rect":
        return f'<rect x="{v[0]:g}" y="{v[1]:g}" width="{v[2]:g}" height="{v[3]:g}"{attrs}/>'
    return f'<path d="{v[0]}"{attrs}/>'


def themed(svg: str, style_id: str, style: dict, mode: str, theming, stroke_width=20, shadow=40) -> str:
    """One style, one mode. `stroke_width` and `shadow` are in viewBox units.

    - Outlines (`stroke`) are painted under the fill (`paint-order="stroke"`), so only their
      outer half shows: a thin accent band keeps its full width and stays continuous.
    - The hard shadow (`shadow`) shows only outside the mark: it is masked out of the mark's
      closed silhouette (gaps narrower than about 2 * SHADOW_CLOSE units closed, see
      `closed_silhouette`) and, for sticker styles (`sticker`), out of the project's OPENINGS
      (eye whites) and SHADOW_CLEAR regions (open bays next to them). Sticker pupils (`detail`)
      are the mode's solid `pupil` color.
    """
    theme = style[mode]
    head, (_, _, w, h), layers = _layers(svg)
    prefix = f"{style_id}-{mode}"
    overrides = getattr(theming, "OVERRIDES", {}).get(style_id, {})
    sticker = style.get("sticker", False)
    openings = getattr(theming, "OPENINGS", []) if sticker else []

    paint, cut, roles = {}, [], {}
    for ident, _ in layers:
        role = theming.ROLES[ident]
        roles[ident] = role
        choice = overrides.get(ident, (style["default"][role], role))
        if choice == "cut" or choice[0] == "cut":
            cut.append(ident)
        else:
            paint[ident] = choice

    stroke = (f' stroke="{theme["line"]}" stroke-width="{stroke_width}" stroke-linejoin="round"'
              f' paint-order="stroke"' if style.get("stroke") else "")
    lines = [head,
             f"  <title>{style['name']} ({mode})</title>",
             f"  <!-- {style['name']} style, {mode} mode: {style['about']}. "
             f"Use on {theme['page']} or {theme['surface']}. Generated by logokit theme. -->",
             "  <defs>"]
    gradients = sorted({v for i, v in paint.items() if not (sticker and roles[i] == "detail")})
    for ramp, axis in gradients:
        lines += _gradient(f"{prefix}-{ramp}-{axis}", theming.AXES[axis], theme["ramps"][ramp])
    d = dict(layers)
    if cut:
        lines.append(f'    <mask id="{prefix}-cut" maskUnits="userSpaceOnUse" x="0" y="0" width="{w:g}" height="{h:g}">')
        lines.append(f'      <rect width="{w:g}" height="{h:g}" fill="#FFFFFF"/>')
        # A thin stroke on the cut eats the anti-aliased hairline the shapes would leave along
        # edges the cut shares with their own outline.
        lines += [f'      <path fill="#000000" stroke="#000000" stroke-width="3" d="{d[c]}"/>' for c in cut]
        lines.append("    </mask>")
    clear = openings + (getattr(theming, "SHADOW_CLEAR", []) if sticker else [])
    if style.get("shadow"):
        # Keep the shadow out of every narrow gap of the mark too (crest notches, gutters).
        closed = closed_silhouette([dd for _, dd in layers], stroke_width / 2 if style.get("stroke") else 0,
                                   getattr(theming, "SHADOW_CLOSE", 40),
                                   getattr(theming, "SHADOW_CLOSE_REGION", None))
        if closed:
            clear = clear + [("path", closed)]
    if clear and style.get("shadow"):
        # Everything but the openings and the bays beside them: no shadow seen through an eye.
        lines.append(f'    <mask id="{prefix}-open" maskUnits="userSpaceOnUse" x="0" y="0" width="{w:g}" height="{h:g}">')
        lines.append(f'      <rect width="{w:g}" height="{h:g}" fill="#FFFFFF"/>')
        lines += ["      " + _shape(*o, attrs=' fill="#000000"') for o in clear]
        lines.append("    </mask>")
    lines.append("  </defs>")

    painted = [ident for ident, _ in layers if ident in paint]
    if style.get("shadow"):
        # The whole mark, offset. Details cast no shadow of their own (they sit inside it).
        mask = f' mask="url(#{prefix}-open)"' if clear else ""
        lines.append(f'  <g id="shadow"{mask}>')
        lines.append(f'    <g transform="translate({shadow} {shadow})" fill="{theme["line"]}"{stroke}>')
        lines += [f'      <path d="{d[i]}"/>' for i in painted if roles[i] != "detail"]
        lines.append("    </g>")
        lines.append("  </g>")

    if style.get("fill_gaps") and getattr(theming, "GAP_FILL", None):
        # Hairline gaps between shapes (crest notch bottoms, ear-tuft roots, the cheek gutter)
        # filled with the ink, so the outlines meet instead of leaving a slit of background or
        # shadow. Drawn under the shapes: only the gaps show. Pupils don't count (no outline).
        gaps = closed_silhouette([d[i] for i in painted if roles[i] != "detail"],
                                 stroke_width / 2 if style.get("stroke") else 0, theming.GAP_FILL,
                                 getattr(theming, "GAP_FILL_EXCEPT", None), outside=True, gaps_only=True,
                                 holes=getattr(theming, "OPENINGS", []))
        if gaps:
            lines.append(f'  <path id="gaps" fill="{theme["line"]}" d="{gaps}"/>')

    seal = getattr(theming, "SEAL", {})

    def path(ident):
        ramp, axis = paint[ident]
        fill = theme["pupil"] if sticker and roles[ident] == "detail" else f"url(#{prefix}-{ramp}-{axis})"
        # Details carry no outline: a stroke would close a pupil's highlight notch.
        own = "" if roles[ident] == "detail" else stroke
        out = f'<path id="{ident}" fill="{fill}"{own} d="{d[ident]}"/>'
        if ident in seal and sticker:
            # A hairline in the layer's own color covers the anti-aliased rim of a differently
            # colored shape that ends exactly at this layer's edge underneath it (the head ends at
            # the pupil's arc). Only along the arcs, with butt caps: around the whole outline its
            # round joins poked out of the pupil's sharp corners into the band above. Only sticker
            # styles need it: elsewhere a pupil is the same color as the head under it.
            # The arc stops 0.3% (about 1.4 units) short of each end (pathLength 100): a butt end at the corner left a speck in
            # the band where the arc meets a sharp corner.
            out += (f'<path fill="none" stroke="{fill}" stroke-width="{seal[ident]:g}" stroke-linecap="butt"'
                    f' pathLength="100" stroke-dasharray="0 0.3 99.4 0.3" d="{_arcs_only(d[ident])}"/>')
        return out

    if cut:
        # Cut-outs are holes in the shapes under them; details stay whole.
        lines.append(f'  <g mask="url(#{prefix}-cut)">')
        lines += ["    " + path(i) for i in painted if roles[i] != "detail"]
        lines.append("  </g>")
        lines += ["  " + path(i) for i in painted if roles[i] == "detail"]
    else:
        lines += ["  " + path(i) for i in painted]
    lines.append("</svg>")
    return "\n".join(lines) + "\n"


def write_all(svg_path: Path, out_dir: Path, styles: dict, theming) -> list[Path]:
    svg = svg_path.read_text()
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for style_id, style in styles.items():
        for mode in ("light", "dark"):
            path = out_dir / f"{style_id}-{mode}.svg"
            path.write_text(themed(svg, style_id, style, mode, theming))
            written.append(path)
    return written
