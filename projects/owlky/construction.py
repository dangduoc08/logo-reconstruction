"""Owl mark: geometric reconstruction of source/original.svg (analysis/geometry-plan.md).

Anchor indices refer to the outlines of the source SVG (path #1 = upper head, #2 = brow,
#3 = left pupil, #4 = lower body, #5 = beak, #6 = cheek stripe, #9 = right pupil; #0 is the
background, #7 and #8 are trace slivers that are dropped).
"""
import math

from logokit.build import Builder, Gradient, Layer, Mark, Piece as P
from logokit.geometry import curve_tangent, fit_circle, mul

TITLE = "Owl mark"

# Design constants (source units). Plan § 6.1, idealized per decision D2.
EYE_Y = 1455.0
EYE_R_C = (3113.5, EYE_Y)
EYE_L_C = (2755.0, EYE_Y)
WHITE_R = 212.0
PUPIL_R = 98.5
HILITE_R = 37.85
HILITE_D = 67.6  # highlight center distance from the pupil center, at 45° up-right (measured 67.6 at 45.6°)
HILITE_C = (EYE_R_C[0] + HILITE_D * math.cos(math.radians(45)),
            EYE_R_C[1] - HILITE_D * math.sin(math.radians(45)))

EYE_WHITE_R = ("circle", EYE_R_C, WHITE_R)
PUPIL_RIGHT = ("circle", EYE_R_C, PUPIL_R)
PUPIL_LEFT = ("circle", EYE_L_C, PUPIL_R)
HIGHLIGHT = ("circle", HILITE_C, HILITE_R)

NAVY = "#222C68"
GOLD = "#C68B38"

# For `logokit compare`: the source's colors (pixels are unmixed into these) and close-up
# regions in viewBox units of the reconstruction (x, y, w, h).
COMPARE = {
    "colors": {"white": (255, 255, 255), "navy": (34, 44, 104), "gold": (198, 139, 56)},
    "zooms": {
        "crest-tips": (0, 0, 760, 420),
        "feather-roots": (40, 640, 480, 180),
        "ear-tufts": (780, 400, 360, 360),
        "eyes": (230, 760, 720, 420),
        "highlight": (700, 860, 160, 140),
        "beak": (480, 1060, 260, 340),
        "cheek-stripe": (560, 1180, 340, 330),
        "left-cheek": (120, 960, 380, 260),
    },
}


def construct(kit: Builder) -> Mark:
    # Upper head (#1): crest blades, crown, ear tufts, rear bump, nose bridge, right-eye socket,
    # left pupil's lower arc.
    head = kit.build("head", 1, [
        P(0, 2, "bez", note="right blade tip"),
        P(2, 5, "line", note="right blade, inner side"),
        P(5, 9, "bez", tol=1.0, note="crown to notch (zigzag 7–8 dropped)"),
        P(9, 18, "bez", note="crown and ear tuft 1, upper edge"),
        P(18, 22, "bez", note="ear tuft 1, under edge (kinks 20–21 smoothed)"),
        P(22, 24, "bez", note="ear tuft 2, upper edge"),
        P(24, 25, "bez", note="ear tuft 2, under edge"),
        P(25, 28, "bez", note="rear feathers"),
        P(28, 31, "bez", note="rear bump to eye socket"),
        P(31, 36, "arc", prim=EYE_WHITE_R, note="right eye white"),
        P(36, 38, "bez", note="nose bridge, right"),
        P(38, 40, "bez", note="nose bridge tip"),
        P(40, 42, "bez", note="nose bridge, left"),
        P(42, 44, "arc", prim=PUPIL_LEFT, note="left pupil"),
        P(44, 48, "bez", note="brow, lower edge"),
        P(48, 50, "bez", note="left swoop"),
        P(50, 52, "bez", note="left swoop to blade"),
        P(52, 54, "bez", note="left blade root"),
        P(54, 57, "line", note="left blade, outer side"),
        P(57, 59, "bez", note="left blade tip"),
        P(59, 64, "bez", note="left blade, inner side"),
        P(64, 65, "bez", note="middle blade root fillet"),
        P(65, 70, "line", note="middle blade, outer side"),
        P(70, 72, "bez", note="middle blade tip"),
        P(72, 73, "line", note="middle blade, inner side"),
        P(73, 80, "bez", note="middle blade root"),
        P(80, 81, "bez", note="right blade root fillet"),
        P(81, 89, "line", note="right blade, outer side"),
    ], corners={0, 9, 18, 22, 24, 25, 28, 36, 38, 40, 42, 44, 50, 52, 57, 64, 70, 80})

    # Beak (#5).
    beak = kit.build("beak", 5, [
        P(0, 2, "arc", prim=EYE_WHITE_R, note="top edge on the eye white"),
        P(2, 4, "line", note="lower edge from the right point (hook at 2–3 dropped)"),
        P(4, 9, "bez", note="inner edge (kinks 4 and 5 merged into one corner)"),
        P(9, 12, "auto", note="outer edge"),
    ], corners={0, 2, 4, 9})

    # Chin bowl: one arc from the right flank to the left cheek (segments 7–12). The upper-left
    # part (12–14) bends to a larger radius without a tangent circle joint, so it is a Bézier
    # (plan § 2.1 assumed one circle; it deviates 3.9 units).
    bowl = fit_circle(kit.outline(4).samples(7, 12))

    # Lower face and body (#4). Shares the beak's outer edge.
    body = kit.build("body", 4, [
        P(28, 31, "arc", prim=EYE_WHITE_R, note="top edge on the eye white"),
        P(1, 5, "bez", note="eye white, lower right (1.5 inside the circle), to the cheek bump"),
        P(5, 7, "bez", note="right flank"),
        P(7, 12, "arc", prim=bowl, note="chin bowl"),
        P(12, 16, "bez", note="chin bowl, upper left, to the cheek spike"),
        P(16, 22, "bez", note="left cheek, white crescent"),
        P(22, 25, "bez", note="chin notch to beak tip"),
        kit.ref("beak", 9, 12, start_a=25, end_b=28),
    ], corners={5, 16, 22, 25, 28})

    # Brow (#2): own upper edge, lower edge shared with the head.
    brow = kit.build("brow", 2, [
        P(0, 7, "bez", note="upper edge"),
        kit.ref("head", 40, 48, start_a=7, end_b=15),
    ], corners={0, 7})

    # Left pupil (#3): drawn over the brow. Its lower arc is the head's (shared edge). Its upper
    # edge is the visible lower edge of the brow band between the head's brow edge (left) and the
    # nose-bridge edge (right), so it leaves and joins them tangentially. The trace turned 47° at
    # the right end (a nub that bit into the gold band) and 19° at the left end.
    brow_left = kit.built["head"][(44, 48)]
    brow_right = kit.built["head"][(40, 42)]
    pupil_left = kit.build("pupil_left", 3, [
        P(0, 4, "bez", note="upper edge, under the brow (G1 with the brow band's lower edge)",
          t_start=mul(curve_tangent(brow_left.curves[0], False), -1),
          t_end=mul(curve_tangent(brow_right.curves[-1], True), -1), trim=15.0, tol=2.5),
        kit.ref("head", 42, 44, start_a=4, end_b=6),
    ], corners={0, 4})

    # Cheek stripe (#6): the dent at segments 8–13 and slivers #7, #8 are dropped (D3).
    stripe = kit.build("stripe", 6, [
        P(0, 2, "bez", note="right end"),
        P(2, 6, "bez", note="outer edge"),
        P(6, 17, "auto", exclude=range(8, 14), note="inner edge (dent removed)"),
    ], corners={0, 2, 6})

    # Right pupil (#9): pupil circle with the highlight circle cut out.
    pupil = kit.build("pupil", 9, [
        P(0, 5, "arc", prim=PUPIL_RIGHT, note="pupil"),
        P(5, 9, "arc", prim=HIGHLIGHT, note="highlight cut-out"),
    ], corners={0, 5}, stubs={0, 5})

    def construction_note(pt, fmt, origin):
        return (f"Construction (viewBox units): eyes on y={fmt(EYE_Y - origin[1])}; "
                f"right eye center {pt(EYE_R_C)}, left eye center {pt(EYE_L_C)}; "
                f"eye white r={fmt(WHITE_R)}, pupil r={fmt(PUPIL_R)}, "
                f"highlight r={fmt(HILITE_R)} at {pt(HILITE_C)}.")

    return Mark(
        title=TITLE,
        layers=[  # back to front, same stacking as the source
            Layer("head", head, NAVY, "Upper head: crest, crown, ear tufts, nose bridge"),
            Layer("brow", brow, "url(#brow-gradient)", "Left brow"),
            Layer("pupil-left", pupil_left, NAVY, "Left pupil, partly under the brow"),
            Layer("body", body, NAVY, "Lower face and body"),
            Layer("beak", beak, GOLD, "Beak"),
            Layer("cheek-stripe", stripe, GOLD, "Right cheek stripe"),
            Layer("pupil-right", pupil, NAVY, "Right pupil with highlight"),
        ],
        # Decision D1: keep the brow's gradient.
        gradients=[Gradient("brow-gradient", (2694.08, 1382.22), (2635.97, 1492.0),
                            [(0, "#CA8F3A"), (1, "#A88554")])],
        notes=[construction_note],
        source_anchors=202,
    )
