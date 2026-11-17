"""Rebuild a traced outline piece by piece, and write the result as SVG.

A project's construction.py describes each outline of the source SVG as a list of Pieces over
anchor ranges (arc, line, Bézier fit, or a reference to pieces built elsewhere) and returns a
Mark; this module turns it into curves with G1 joins and writes output/reconstructed.svg.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from .geometry import (add, arc_center, bez_len, bez_point, cross, curve_end, curve_points,
                       curve_start, curve_tangent, fit_circle, fit_cubics, fit_line, intersect,
                       mul, norm, prim_dev, prim_tangent, project, seg_tan_in, seg_tan_out, sub,
                       unit)

DEFAULT_TOL = 0.8  # max deviation of a fitted Bézier from the measured outline, in units

# ---------------------------------------------------------------------------
# Source SVG (measurement data only)
# ---------------------------------------------------------------------------

def load_source(path: Path):
    """Every <path> of a traced SVG as a list of cubic segments (lines become flat cubics)."""
    text = re.sub(r"<metadata>.*?</metadata>", "", path.read_text(), flags=re.S)
    out = []
    for d in re.findall(r'<path[^>]*d="([^"]*)"', text):
        toks = re.findall(r"[MLCZz]|-?[\d.]+", d)
        segs, i, cmd, cur = [], 0, None, None
        while i < len(toks):
            t = toks[i]
            if t in "MLCZz":
                cmd = t
                i += 1
                continue
            if cmd == "M":
                cur = (float(toks[i]), float(toks[i + 1]))
                i += 2
                cmd = "L"
            elif cmd == "L":
                p = (float(toks[i]), float(toks[i + 1]))
                segs.append((cur, cur, p, p))
                cur = p
                i += 2
            elif cmd == "C":
                v = [float(x) for x in toks[i:i + 6]]
                p = (v[4], v[5])
                segs.append((cur, (v[0], v[1]), (v[2], v[3]), p))
                cur = p
                i += 6
        out.append(segs)
    return out


class Outline:
    """One closed outline of the source, addressed by anchor index (wraps)."""

    def __init__(self, segs):
        self.segs = segs
        self.n = len(segs)

    def seg(self, k): return self.segs[k % self.n]
    def anchor(self, k): return self.seg(k)[0]
    def tan_out(self, k): return seg_tan_out(self.seg(k))
    def tan_in(self, k): return seg_tan_in(self.seg(k - 1))

    def samples(self, a, b, exclude=()):
        pts = []
        for k in range(a, b):
            if k % self.n in exclude:
                continue
            s = self.seg(k)
            m = max(8, int(bez_len(s) / 1.5))
            pts.extend(bez_point(s, i / m) for i in range(m))
        pts.append(self.anchor(b))
        return pts

# ---------------------------------------------------------------------------
# Pieces
# ---------------------------------------------------------------------------

class Piece:
    """Anchors a..b of an outline, rebuilt as `kind`: "arc" (prim given or fitted), "line",
    "bez" (least-squares cubics), "auto" (an arc if one fits within 1.25 units, else bez), or a
    reference made by Builder.ref."""

    def __init__(self, a, b, kind, prim=None, tol=DEFAULT_TOL, exclude=(), ref=None, note="",
                 t_start=None, t_end=None, trim=0.0):
        self.a, self.b, self.kind, self.prim = a, b, kind, prim
        self.t_start, self.t_end = t_start, t_end  # forced travel directions at the ends (Bézier only)
        self.trim = trim  # ignore measured samples this close to either end (trace noise at a join)
        self.tol, self.exclude, self.ref, self.note = tol, set(exclude), ref, note
        self.curves = []  # ("C", bez) | ("L", p0, p1) | ("A", center, r, p0, p1, sweep)
        self.samples = []

    @property
    def start(self): return curve_start(self.curves[0])
    @property
    def end(self): return curve_end(self.curves[-1])


class Builder:
    """Holds the source outlines and every outline built so far (for shared edges)."""

    def __init__(self, source: Path):
        self.source = load_source(source)
        self.built: dict[str, dict[tuple[int, int], Piece]] = {}

    def outline(self, idx) -> Outline:
        return Outline(self.source[idx])

    def build(self, name, outline_idx, specs, corners, stubs=frozenset()):
        """specs: Pieces covering the outline in order; corners: anchors that stay sharp.

        stubs: corners between two primitives that end in a short straight cut instead of
        meeting at their intersection. Two circles crossing at a grazing angle make a hair-thin
        wedge several units longer than the drawn point; the cut keeps the point where it was."""
        ol = self.outline(outline_idx)
        n = len(specs)
        for i, pc in enumerate(specs):
            nxt = specs[(i + 1) % n]
            assert pc.b % ol.n == nxt.a % ol.n, (name, pc.a, pc.b, nxt.a)
            if pc.ref:
                continue
            pc.samples = ol.samples(pc.a, pc.b, pc.exclude)
            if pc.kind == "arc" and pc.prim is None:
                pc.prim = fit_circle(pc.samples)
            elif pc.kind == "line":
                pc.prim = fit_line(pc.samples)
            elif pc.kind == "auto":
                circ = fit_circle(pc.samples)
                if prim_dev(circ, pc.samples) <= 1.25:
                    pc.kind, pc.prim = "arc", circ
                else:
                    pc.kind = "bez"

        # Joints: (end point of the previous piece, start point of this one, tangents).
        joints = []
        for i, pc in enumerate(specs):
            prev = specs[i - 1]
            k = pc.a
            corner = (k % ol.n) in corners
            tin, tout = ol.tan_in(k), ol.tan_out(k)
            p_end = None
            if pc.ref:
                p = pc.ref_start
            elif prev.prim and pc.prim and corner and (k % ol.n) in stubs:
                p_end, p = project(prev.prim, ol.anchor(k)), project(pc.prim, ol.anchor(k))
            elif prev.ref:
                p = prev.ref_end
            elif prev.prim and pc.prim and corner:
                p = intersect(prev.prim, pc.prim, ol.anchor(k))
            elif prev.prim:
                p = project(prev.prim, ol.anchor(k))
            elif pc.prim:
                p = project(pc.prim, ol.anchor(k))
            else:
                p = ol.anchor(k)
            if corner:
                t_end_prev, t_start = tin, tout
            else:
                if prev.ref:
                    t = prev.ref_end_tan
                elif pc.ref:
                    t = pc.ref_start_tan
                elif prev.prim:
                    t = prim_tangent(prev.prim, p, tin)
                elif pc.prim:
                    t = prim_tangent(pc.prim, p, tout)
                else:
                    t = unit(add(tin, tout))
                t_end_prev = t_start = t
            joints.append((p if p_end is None else p_end, p, t_end_prev, t_start))

        for i, pc in enumerate(specs):
            if pc.t_start:
                j = joints[i]
                joints[i] = (j[0], j[1], j[2], pc.t_start)
            if pc.t_end:
                j = joints[(i + 1) % n]
                joints[(i + 1) % n] = (j[0], j[1], pc.t_end, j[3])

        for i, pc in enumerate(specs):
            if pc.ref:
                continue
            _, p0, _, t0 = joints[i]
            p1, _, t1, _ = joints[(i + 1) % n]
            if pc.kind == "line":
                pc.curves = [("L", p0, p1)]
            elif pc.kind == "arc":
                center, r = arc_center(p0, p1, pc.prim[1], pc.prim[2]), pc.prim[2]
                rv = sub(p0, center)
                sweep = 1 if cross(rv, ol.tan_out(pc.a)) > 0 else 0
                pc.curves = [("A", center, r, p0, p1, sweep)]
            else:
                # Where a joint moved off the measured outline (projected onto a primitive), drop
                # the samples right next to it, or the fit chases the old anchor with a tiny piece.
                keep0 = max(3.0, pc.trim, 3 * norm(sub(p0, ol.anchor(pc.a))))
                keep1 = max(3.0, pc.trim, 3 * norm(sub(p1, ol.anchor(pc.b))))
                inner = [q for q in pc.samples[1:-1]
                         if norm(sub(q, ol.anchor(pc.a))) > keep0 and norm(sub(q, ol.anchor(pc.b))) > keep1]
                pts = [p0]
                for q in inner + [p1]:
                    if norm(sub(q, pts[-1])) > 0.05:
                        pts.append(q)
                pc.curves = [("C", b) for b in fit_cubics(pts, t0, mul(t1, -1), pc.tol)]

        self.built[name] = {(pc.a, pc.b): pc for pc in specs}
        return specs

    def ref(self, name, a, b, *, start_a, end_b):
        """A run of pieces already built in another outline, reused verbatim (a shared edge)."""
        src = self.built[name]
        run, k = [], a
        while k != b:
            pc = next(p for (pa, pb), p in src.items() if pa == k)
            run.append(pc)
            k = pc.b
        pc = Piece(start_a, end_b, "ref", ref=(name, a, b), note=f"shared with {name} {a}..{b}")
        pc.curves = [c for p in run for c in p.curves]
        pc.samples = [s for p in run for s in p.samples]
        pc.ref_start = pc.start
        pc.ref_end = pc.end
        pc.ref_start_tan = curve_tangent(pc.curves[0], False)
        pc.ref_end_tan = curve_tangent(pc.curves[-1], True)
        return pc

# ---------------------------------------------------------------------------
# Mark and SVG output
# ---------------------------------------------------------------------------

@dataclass
class Layer:
    id: str
    pieces: list
    fill: str
    description: str


@dataclass
class Gradient:
    """A linear gradient in source coordinates (moved into the output frame on write)."""
    id: str
    start: tuple
    end: tuple
    stops: list  # [(offset, color)]


@dataclass
class Mark:
    title: str
    layers: list  # back to front
    gradients: list = field(default_factory=list)
    # Extra comment lines, given the output frame: note(pt, fmt, origin) -> str.
    notes: list[Callable] = field(default_factory=list)
    pad: float = 48.0
    source_anchors: int = 0  # anchors in the source, for the report


def fmt(v):
    # Two decimals: an arc's center is recomputed from its rounded endpoints, and with one
    # decimal the owl's chin bowl drifted 1.5° at its joint.
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return "0" if s == "-0" else s


class Frame:
    """The output viewBox: the mark's bounding box plus padding, origin at whole units."""

    def __init__(self, mark: Mark):
        xs, ys = [], []
        for layer in mark.layers:
            for pc in layer.pieces:
                for c in pc.curves:
                    for p in curve_points(c, 2.0):
                        xs.append(p[0]); ys.append(p[1])
        self.ox, self.oy = math.floor(min(xs) - mark.pad), math.floor(min(ys) - mark.pad)
        self.w = math.ceil(max(xs) + mark.pad) - self.ox
        self.h = math.ceil(max(ys) + mark.pad) - self.oy

    def pt(self, p): return f"{fmt(p[0] - self.ox)} {fmt(p[1] - self.oy)}"


def path_d(pieces, frame: Frame):
    pt = frame.pt
    out = [f"M {pt(pieces[0].start)}"]
    cur = pieces[0].start
    for pc in pieces:
        if norm(sub(pc.start, cur)) > 1e-6:
            out.append(f"L {pt(pc.start)}")  # a stub cut (see Builder.build)
        cur = pc.end
        for c in pc.curves:
            if c[0] == "L":
                out.append(f"L {pt(c[2])}")
            elif c[0] == "C":
                b = c[1]
                out.append(f"C {pt(b[1])} {pt(b[2])} {pt(b[3])}")
            else:
                _, center, r, p0, p1, sweep = c
                a0 = math.atan2(p0[1] - center[1], p0[0] - center[0])
                a1 = math.atan2(p1[1] - center[1], p1[0] - center[0])
                span = (a1 - a0) % (2 * math.pi) if sweep else (a0 - a1) % (2 * math.pi)
                large = 1 if span > math.pi else 0
                out.append(f"A {fmt(r)} {fmt(r)} 0 {large} {sweep} {pt(p1)}")
    out.append("Z")
    return " ".join(out)


def svg_text(mark: Mark, generator: str) -> str:
    frame = Frame(mark)
    w, h = frame.w, frame.h
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">',
        f"  <title>{mark.title}</title>",
        f"  <!-- Generated by {generator}. Edit the construction, not this file. -->",
    ]
    lines += [f"  <!-- {note(frame.pt, fmt, (frame.ox, frame.oy))} -->" for note in mark.notes]
    if mark.gradients:
        lines.append("  <defs>")
        for g in mark.gradients:
            x1, y1 = g.start[0] - frame.ox, g.start[1] - frame.oy
            x2, y2 = g.end[0] - frame.ox, g.end[1] - frame.oy
            lines.append(f'    <linearGradient id="{g.id}" gradientUnits="userSpaceOnUse" '
                         f'x1="{fmt(x1)}" y1="{fmt(y1)}" x2="{fmt(x2)}" y2="{fmt(y2)}">')
            lines += [f'      <stop offset="{o:g}" stop-color="{c}"/>' for o, c in g.stops]
            lines.append("    </linearGradient>")
        lines.append("  </defs>")
    for layer in mark.layers:
        lines.append(f"  <!-- {layer.description} -->")
        lines.append(f'  <path id="{layer.id}" fill="{layer.fill}" d="{path_d(layer.pieces, frame)}"/>')
    lines.append("</svg>")
    return "\n".join(lines) + "\n"


def report(mark: Mark) -> str:
    frame = Frame(mark)
    out = [f"viewBox 0 0 {frame.w} {frame.h}  (source offset {frame.ox},{frame.oy})"]
    total, worst = 0, 0.0
    for layer in mark.layers:
        stubs = sum(1 for i, pc in enumerate(layer.pieces)
                    if norm(sub(pc.start, layer.pieces[i - 1].end)) > 1e-6)  # stub cuts (L)
        nodes = sum(len(pc.curves) for pc in layer.pieces) + stubs
        total += nodes
        out.append(f"\n{layer.id}: {nodes} nodes")
        for pc in layer.pieces:
            if pc.ref:
                out.append(f"  {pc.a:>3}..{pc.b:<3} ref    {pc.note}")
                continue
            new = [q for c in pc.curves for q in curve_points(c, 0.75)]
            dev = max(min(norm(sub(p, q)) for q in new) for p in pc.samples[::2]) if pc.samples else 0
            kinds = {"C": 0, "L": 0, "A": 0}
            for c in pc.curves:
                kinds[c[0]] += 1
            desc = " ".join(f"{v}{k}" for k, v in kinds.items() if v)
            worst = max(worst, dev if not pc.exclude else 0)
            out.append(f"  {pc.a:>3}..{pc.b:<3} {pc.kind:<5} {desc:<8} maxdev {dev:5.2f}  {pc.note}")
    source = f" (source {mark.source_anchors})" if mark.source_anchors else ""
    out.append(f"\ntotal nodes {total}{source}; worst deviation {worst:.2f} units")
    return "\n".join(out)
