"""Plane geometry for reconstruction: vectors, cubic Béziers, primitives, curve fitting.

A primitive is a tuple: ("circle", center, r) or ("line", point, unit_direction).
A curve is ("C", bezier) | ("L", p0, p1) | ("A", center, r, p0, p1, sweep).
Standard library only.
"""
from __future__ import annotations

import math

MIN_PIECE = 12.0  # shortest Bézier piece a fit may create, in source units

# ---------------------------------------------------------------------------
# Vectors and Béziers
# ---------------------------------------------------------------------------

def add(a, b): return (a[0] + b[0], a[1] + b[1])
def sub(a, b): return (a[0] - b[0], a[1] - b[1])
def mul(a, s): return (a[0] * s, a[1] * s)
def dot(a, b): return a[0] * b[0] + a[1] * b[1]
def cross(a, b): return a[0] * b[1] - a[1] * b[0]
def norm(a): return math.hypot(a[0], a[1])


def unit(a):
    n = norm(a)
    return (a[0] / n, a[1] / n) if n > 1e-12 else (0.0, 0.0)


def bez_point(b, t):
    mt = 1 - t
    return (mt ** 3 * b[0][0] + 3 * mt * mt * t * b[1][0] + 3 * mt * t * t * b[2][0] + t ** 3 * b[3][0],
            mt ** 3 * b[0][1] + 3 * mt * mt * t * b[1][1] + 3 * mt * t * t * b[2][1] + t ** 3 * b[3][1])


def bez_d1(b, t):
    mt = 1 - t
    return (3 * mt * mt * (b[1][0] - b[0][0]) + 6 * mt * t * (b[2][0] - b[1][0]) + 3 * t * t * (b[3][0] - b[2][0]),
            3 * mt * mt * (b[1][1] - b[0][1]) + 6 * mt * t * (b[2][1] - b[1][1]) + 3 * t * t * (b[3][1] - b[2][1]))


def bez_d2(b, t):
    mt = 1 - t
    return (6 * mt * (b[2][0] - 2 * b[1][0] + b[0][0]) + 6 * t * (b[3][0] - 2 * b[2][0] + b[1][0]),
            6 * mt * (b[2][1] - 2 * b[1][1] + b[0][1]) + 6 * t * (b[3][1] - 2 * b[2][1] + b[1][1]))


def bez_len(b):
    return sum(norm(sub(bez_point(b, (i + 1) / 16), bez_point(b, i / 16))) for i in range(16))


def seg_tan_out(s):
    for q in (s[1], s[2], s[3]):
        if norm(sub(q, s[0])) > 1e-9:
            return unit(sub(q, s[0]))
    return (1.0, 0.0)


def seg_tan_in(s):
    for q in (s[2], s[1], s[0]):
        if norm(sub(s[3], q)) > 1e-9:
            return unit(sub(s[3], q))
    return (1.0, 0.0)

# ---------------------------------------------------------------------------
# Primitives
# ---------------------------------------------------------------------------

def fit_circle(pts):
    """Least-squares circle (Kåsa)."""
    sxx = sxy = syy = sx = sy = n = 0.0
    r0 = r1 = r2 = 0.0
    for x, y in pts:
        z = -(x * x + y * y)
        sxx += x * x; sxy += x * y; syy += y * y; sx += x; sy += y; n += 1
        r0 += x * z; r1 += y * z; r2 += z
    m = [[sxx, sxy, sx, r0], [sxy, syy, sy, r1], [sx, sy, n, r2]]
    for c in range(3):
        p = max(range(c, 3), key=lambda k: abs(m[k][c]))
        m[c], m[p] = m[p], m[c]
        for k in range(3):
            if k != c:
                f = m[k][c] / m[c][c]
                m[k] = [m[k][j] - f * m[c][j] for j in range(4)]
    d, e, f = (m[i][3] / m[i][i] for i in range(3))
    cx, cy = -d / 2, -e / 2
    return ("circle", (cx, cy), math.sqrt(cx * cx + cy * cy - f))


def fit_line(pts):
    """Total least-squares line."""
    n = len(pts)
    mx = sum(p[0] for p in pts) / n
    my = sum(p[1] for p in pts) / n
    sxx = sum((p[0] - mx) ** 2 for p in pts)
    syy = sum((p[1] - my) ** 2 for p in pts)
    sxy = sum((p[0] - mx) * (p[1] - my) for p in pts)
    th = 0.5 * math.atan2(2 * sxy, sxx - syy)
    return ("line", (mx, my), (math.cos(th), math.sin(th)))


def dist_to_prim(prim, p):
    if prim[0] == "circle":
        return norm(sub(p, prim[1])) - prim[2]
    return cross(prim[2], sub(p, prim[1]))


def prim_dev(prim, pts):
    return max(abs(dist_to_prim(prim, p)) for p in pts)


def project(prim, p):
    if prim[0] == "circle":
        return add(prim[1], mul(unit(sub(p, prim[1])), prim[2]))
    o, d = prim[1], prim[2]
    return add(o, mul(d, dot(sub(p, o), d)))


def prim_tangent(prim, p, hint):
    """Unit tangent of the primitive at p, oriented like `hint`."""
    if prim[0] == "circle":
        r = sub(p, prim[1])
        t = unit((-r[1], r[0]))
    else:
        t = prim[2]
    return t if dot(t, hint) >= 0 else mul(t, -1)


def intersect(pa, pb, near):
    """Intersection of two primitives nearest to `near` (its projection on pa if none)."""
    cands = []
    if pa[0] == "line" and pb[0] == "line":
        o1, d1 = pa[1], pa[2]
        o2, d2 = pb[1], pb[2]
        den = cross(d1, d2)
        if abs(den) > 1e-12:
            t = cross(sub(o2, o1), d2) / den
            cands.append(add(o1, mul(d1, t)))
    elif pa[0] == "circle" and pb[0] == "circle":
        c0, r0 = pa[1], pa[2]
        c1, r1 = pb[1], pb[2]
        d = norm(sub(c1, c0))
        if 0 < d <= r0 + r1 and d >= abs(r0 - r1):
            a = (r0 * r0 - r1 * r1 + d * d) / (2 * d)
            h = math.sqrt(max(0.0, r0 * r0 - a * a))
            m = add(c0, mul(sub(c1, c0), a / d))
            perp = unit((-(c1[1] - c0[1]), c1[0] - c0[0]))
            cands += [add(m, mul(perp, h)), sub(m, mul(perp, h))]
    else:
        line, circ = (pa, pb) if pa[0] == "line" else (pb, pa)
        o, dvec = line[1], line[2]
        c, r = circ[1], circ[2]
        f = sub(o, c)
        b = dot(f, dvec)
        disc = b * b - (dot(f, f) - r * r)
        if disc >= 0:
            s = math.sqrt(disc)
            cands += [add(o, mul(dvec, -b + s)), add(o, mul(dvec, -b - s))]
    if not cands:
        return project(pa, near)
    return min(cands, key=lambda q: norm(sub(q, near)))


def arc_center(p0, p1, center, r):
    """Center of the radius-r circle through p0 and p1 nearest to `center`: the circle an SVG
    arc command actually draws when an endpoint sits slightly off the design circle."""
    m = mul(add(p0, p1), 0.5)
    half = norm(sub(p1, p0)) / 2
    if half < 1e-9 or half > r:
        return center
    h = math.sqrt(r * r - half * half)
    perp = unit((-(p1[1] - p0[1]), p1[0] - p0[0]))
    return min((add(m, mul(perp, h)), sub(m, mul(perp, h))), key=lambda c: norm(sub(c, center)))

# ---------------------------------------------------------------------------
# Bézier fitting (Schneider, "An algorithm for automatically fitting digitized curves")
# ---------------------------------------------------------------------------

def chord_params(pts):
    u = [0.0]
    for i in range(1, len(pts)):
        u.append(u[-1] + norm(sub(pts[i], pts[i - 1])))
    return [x / u[-1] for x in u]


def generate_bezier(pts, u, t1, t2):
    p0, p3 = pts[0], pts[-1]
    c00 = c01 = c11 = x0 = x1 = 0.0
    for p, t in zip(pts, u):
        mt = 1 - t
        a1 = mul(t1, 3 * mt * mt * t)
        a2 = mul(t2, 3 * mt * t * t)
        c00 += dot(a1, a1); c01 += dot(a1, a2); c11 += dot(a2, a2)
        base = add(mul(p0, mt ** 3 + 3 * mt * mt * t), mul(p3, 3 * mt * t * t + t ** 3))
        tmp = sub(p, base)
        x0 += dot(a1, tmp); x1 += dot(a2, tmp)
    det = c00 * c11 - c01 * c01
    seg = norm(sub(p3, p0))
    al = ar = 0.0
    if abs(det) > 1e-12:
        al = (x0 * c11 - c01 * x1) / det
        ar = (c00 * x1 - x0 * c01) / det
    eps = 1e-6 * seg
    if al < eps or ar < eps:
        al = ar = seg / 3
    return (p0, add(p0, mul(t1, al)), add(p3, mul(t2, ar)), p3)


def reparameterize(b, pts, u):
    out = []
    for p, t in zip(pts, u):
        q = sub(bez_point(b, t), p)
        d1 = bez_d1(b, t)
        d2 = bez_d2(b, t)
        den = dot(d1, d1) + dot(q, d2)
        nt = t - dot(q, d1) / den if abs(den) > 1e-12 else t
        out.append(min(1.0, max(0.0, nt)))
    return out


def max_error(b, pts, u):
    worst, idx = 0.0, len(pts) // 2
    for i, (p, t) in enumerate(zip(pts, u)):
        e = norm(sub(bez_point(b, t), p))
        if e > worst:
            worst, idx = e, i
    return worst, idx


def fit_cubics(pts, t1, t2, tol):
    """Cubics through pts[0] and pts[-1] with end tangents t1 (into the curve) and t2 (back into
    the curve), split at the worst point until every sample is within `tol`. Joins are G1."""
    if len(pts) < 3:
        d = norm(sub(pts[-1], pts[0])) / 3
        return [(pts[0], add(pts[0], mul(t1, d)), add(pts[-1], mul(t2, d)), pts[-1])]
    u = chord_params(pts)
    b = generate_bezier(pts, u, t1, t2)
    err, split = max_error(b, pts, u)
    if err <= tol or len(pts) <= 6:
        return [b]
    if err <= tol * 16:
        for _ in range(30):
            u = reparameterize(b, pts, u)
            b = generate_bezier(pts, u, t1, t2)
            err, split = max_error(b, pts, u)
            if err <= tol:
                return [b]
    # Never split closer than MIN_PIECE units to either end: short pieces are trace noise.
    acc = [0.0]
    for i in range(1, len(pts)):
        acc.append(acc[-1] + norm(sub(pts[i], pts[i - 1])))
    lo = next((i for i, v in enumerate(acc) if v >= MIN_PIECE), 2)
    hi = next((i for i in range(len(acc) - 1, -1, -1) if acc[-1] - acc[i] >= MIN_PIECE), len(pts) - 3)
    if lo >= hi:
        return [b]
    split = min(max(split, lo, 2), hi, len(pts) - 3)
    tc = unit(sub(pts[split - 1], pts[split + 1]))
    return fit_cubics(pts[:split + 1], t1, tc, tol) + fit_cubics(pts[split:], mul(tc, -1), t2, tol)

# ---------------------------------------------------------------------------
# Curves
# ---------------------------------------------------------------------------

def curve_start(c): return c[1][0] if c[0] == "C" else (c[1] if c[0] == "L" else c[3])
def curve_end(c): return c[1][3] if c[0] == "C" else (c[2] if c[0] == "L" else c[4])


def curve_tangent(c, at_end):
    """Travel direction at the start (or end) of a curve."""
    if c[0] == "C":
        b = c[1]
        return seg_tan_in(b) if at_end else seg_tan_out(b)
    if c[0] == "L":
        return unit(sub(c[2], c[1]))
    _, center, r, p0, p1, sweep = c
    p = p1 if at_end else p0
    rv = sub(p, center)
    t = unit((-rv[1], rv[0]))  # direction of increasing angle (sweep = 1)
    return t if sweep else mul(t, -1)


def curve_points(c, step=0.5):
    if c[0] == "C":
        m = max(4, int(bez_len(c[1]) / step))
        return [bez_point(c[1], i / m) for i in range(m + 1)]
    if c[0] == "L":
        m = max(2, int(norm(sub(c[2], c[1])) / step))
        return [add(c[1], mul(sub(c[2], c[1]), i / m)) for i in range(m + 1)]
    _, center, r, p0, p1, sweep = c
    a0 = math.atan2(p0[1] - center[1], p0[0] - center[0])
    a1 = math.atan2(p1[1] - center[1], p1[0] - center[0])
    span = (a1 - a0) % (2 * math.pi) if sweep else -((a0 - a1) % (2 * math.pi))
    m = max(4, int(abs(span) * r / step))
    return [(center[0] + r * math.cos(a0 + span * i / m), center[1] + r * math.sin(a0 + span * i / m))
            for i in range(m + 1)]
