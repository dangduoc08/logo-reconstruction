"""Structural check of a reconstructed SVG, read back from the file itself.

For every path: node count by command, and the turn angle at every node. A node turning
by more than SMOOTH_DEG (but less than CORNER_DEG) is a tangent break where the outline
should be smooth: that is reported as a defect. Standard library only.

    python -m logokit check <project>
"""
import math
import re
from pathlib import Path

SMOOTH_DEG = 1.0   # turns below this are smooth joins (coordinates are rounded to 0.01)
CORNER_DEG = 10.0  # turns above this are intended sharp corners (the softest, at the brow tip, is 14°)


def arc_tangents(p0, rx, ry, phi, large, sweep, p1):
    """SVG arc endpoint parametrization (SVG 2, appendix B.2.4), circular arcs only."""
    x1p, y1p = (p0[0] - p1[0]) / 2, (p0[1] - p1[1]) / 2
    r = max(rx, math.hypot(x1p, y1p))
    num = max(0.0, r * r * r * r - r * r * (x1p * x1p + y1p * y1p))
    den = r * r * (x1p * x1p + y1p * y1p)
    coef = math.sqrt(num / den) if den else 0.0
    if large == sweep:
        coef = -coef
    cxp, cyp = coef * y1p, -coef * x1p
    cx, cy = cxp + (p0[0] + p1[0]) / 2, cyp + (p0[1] + p1[1]) / 2

    def tan(p):
        v = (p[0] - cx, p[1] - cy)
        t = (-v[1], v[0])
        return t if sweep else (-t[0], -t[1])
    return tan(p0), tan(p1)


def segments(d):
    toks = re.findall(r"[MLCAZ]|-?[\d.]+", d)
    i, cur, start, out, cmd = 0, None, None, [], None
    while i < len(toks):
        t = toks[i]
        if t in "MLCAZ":
            cmd = t
            i += 1
            if cmd == "Z":
                if cur != start:
                    out.append(("L", cur, start, (start[0] - cur[0], start[1] - cur[1]),
                                (start[0] - cur[0], start[1] - cur[1])))
                continue
            continue
        if cmd == "M":
            cur = start = (float(toks[i]), float(toks[i + 1]))
            i += 2
        elif cmd == "L":
            p = (float(toks[i]), float(toks[i + 1]))
            v = (p[0] - cur[0], p[1] - cur[1])
            out.append(("L", cur, p, v, v))
            cur = p
            i += 2
        elif cmd == "C":
            v = [float(x) for x in toks[i:i + 6]]
            c1, c2, p = (v[0], v[1]), (v[2], v[3]), (v[4], v[5])
            out.append(("C", cur, p, (c1[0] - cur[0], c1[1] - cur[1]), (p[0] - c2[0], p[1] - c2[1])))
            cur = p
            i += 6
        elif cmd == "A":
            rx, ry, phi, large, sweep, x, y = (float(x) for x in toks[i:i + 7])
            p = (x, y)
            t0, t1 = arc_tangents(cur, rx, ry, phi, int(large), int(sweep), p)
            out.append(("A", cur, p, t0, t1))
            cur = p
            i += 7
    return out


def angle(a, b):
    na, nb = math.hypot(*a), math.hypot(*b)
    if na < 1e-9 or nb < 1e-9:
        return 0.0
    c = max(-1.0, min(1.0, (a[0] * b[0] + a[1] * b[1]) / (na * nb)))
    return math.degrees(math.acos(c))


def check(svg: Path) -> int:
    """Print the report; return the number of tangent breaks."""
    text = svg.read_text()
    bad = 0
    total = 0
    for ident, d in re.findall(r'<path id="([^"]+)"[^>]*d="([^"]+)"', text):
        segs = segments(d)
        kinds = {k: sum(1 for s in segs if s[0] == k) for k in "CLA"}
        total += len(segs)
        corners, breaks = 0, []
        for i, s in enumerate(segs):
            prev = segs[i - 1]
            a = angle(prev[4], s[3])
            if a >= CORNER_DEG:
                corners += 1
            elif a > SMOOTH_DEG:
                breaks.append((i, round(a, 2), tuple(round(v, 1) for v in s[1])))
        bad += len(breaks)
        desc = ", ".join(f"{v} {k}" for k, v in kinds.items() if v)
        print(f"{ident:12s} {len(segs):3d} nodes ({desc}); {corners} sharp corners; {len(breaks)} tangent breaks")
        for b in breaks:
            print(f"    break at node {b[0]} {b[2]}: {b[1]}°")
    print(f"total {total} nodes, {bad} tangent breaks")
    return bad
