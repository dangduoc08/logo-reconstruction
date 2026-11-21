"""How the owl takes a style set's colors (`python -m logokit theme owlkei`)."""

STYLE_SET = "owlkei"  # styles/owlkei.py

# Logo role of each layer of output/reconstructed.svg.
ROLES = {
    "head": "brand", "body": "brand",
    "brow": "accent", "beak": "accent", "cheek-stripe": "accent",
    "pupil-left": "detail", "pupil-right": "detail",
}

# Gradient axes in viewBox units. By role, plus named axes the overrides use.
AXES = {
    "brand": ((760, 40), (430, 1480)),    # crest tips (top right) down to the chin, along the fan
    "detail": ((760, 40), (430, 1480)),   # pupils share the body's gradient
    "accent": ((90, 790), (860, 1470)),   # brow (top left) to cheek stripe (bottom right)
    "head": ((760, 40), (430, 1180)),     # the head alone
    "lower": ((900, 900), (450, 1480)),   # the lower body alone
    "beak": ((600, 1100), (560, 1360)),   # the beak alone
    "brow": ((90, 790), (480, 1140)),     # the brow alone
}

# Where sticker styles (Bauhaus, Neo-Brutalism) keep the hard shadow out (viewBox units):
# - OPENINGS: the two eye whites (construction: eye centers on y=979, x=735.5 and 377, r=212);
# - SHADOW_CLEAR: the rest of the open bay beside the left eye, from the left edge to the nose.
#   A mask ending at the left eye's circle cut the swoop's shadow into a visible wedge. Left of
#   the mark there is no shadow to cut (it falls down and right), and the rectangle's other
#   edges run inside the head and body.
OPENINGS = [("circle", 735.5, 979, 212), ("circle", 377, 979, 212)]
# Gaps narrower than about twice this (viewBox units, outlines included) count as inside the mark
# for the hard shadow, within SHADOW_CLOSE_REGION only (x, y, w, h): the gutters around the beak.
# Elsewhere (crest notches, ear-tuft gaps) the shadow is left as it falls (owner's choice).
SHADOW_CLOSE = 40
SHADOW_CLOSE_REGION = (380, 1000, 380, 420)
# Styles with `fill_gaps` (Neo-Brutalism) fill gaps narrower than about twice this (viewBox
# units, outlines included) with the ink: the slit left between the outlines where the left and
# middle crest blades meet. Never inside the eye openings, nor in GAP_FILL_EXCEPT (x, y, w, h):
# around the beak (kept as it is) and the sharp V notch beside the left blade (it would blunt).
GAP_FILL = 3
GAP_FILL_EXCEPT = [SHADOW_CLOSE_REGION, (90, 690, 50, 70)]
SHADOW_CLEAR = [("rect", 0, 640, 420, 460)]

# Layers drawn over a shape that ends at the same edge (the head ends at the left pupil's
# lower arc): a hairline of their own color, in viewBox units, hides that shape's
# anti-aliased rim. Without it a thin ring of the head's color circled the left pupil
# wherever pupil and head differ in color: the sticker styles (Neo-Brutalism, Bauhaus) only.
SEAL = {"pupil-left": 1.5}

# Where the owl departs from a style's defaults: layer -> (ramp, axis).
OVERRIDES = {
    # One red accent, on the beak; brow and stripe join the ink.
    "swiss": {"beak": ("red", "beak"), "brow": ("ink", "brand"), "cheek-stripe": ("ink", "brand")},
    # Blocks: blue head, red lower body.
    "bauhaus": {"head": ("blue", "head"), "body": ("red", "lower")},
    # One red accent, on the brow; beak and stripe join the ink.
    "editorial": {"brow": ("red", "brow"), "beak": ("ink", "brand"), "cheek-stripe": ("ink", "brand")},
    # The beak stays ink: it borders the white gutters, so cutting it out erased it.
    "minimal-mono": {"beak": ("ink", "brand")},
}
