"""The nine owlkei design styles as logo palettes, light and dark.

Source: the owlkei repository (packages/tokens/src/styles/<id>.ts, docs/styles-reference.json,
docs/reference/dashboard-lab.html), copied here so this repository stands alone.

Per style:
- `ramps`: named gradients (stops light to deep). A flat color is a ramp of one color twice.
- `default`: which ramp each logo role gets. Roles: `brand` (the main shapes), `accent` (the
  contrasting details), `detail` (small inner features such as pupils: never outlined, never
  shadowed). "cut" makes that role a hole in the shapes under it.
- `stroke` / `shadow`: the inked styles outline every shape in `line` (Bauhaus, Neo-Brutalism
  draw `2px solid var(--text)`); Neo-Brutalism also casts `6px 6px 0 var(--text)`.
- `fill_gaps`: hairline gaps between shapes are filled with `line` (project GAP_FILL).
- `sticker`: no shadow falls inside the project's openings (eye whites); pupils are a solid
  `pupil` color.
- `page` / `surface` / `line`: the style's page and surface backgrounds and text color.
"""

STYLES = {
    "soft": {
        "name": "Soft",
        "about": "violet primary, warm amber accents (c3), soft and rounded",
        "default": {"brand": "brand", "accent": "accent", "detail": "brand"},
        "light": {"page": "#F8F6FF", "surface": "#FFFFFF", "line": "#241F3D",
                  "ramps": {"brand": ["#5B3DF5", "#2C0BD5", "#1D078D"], "accent": ["#FBBF24", "#C2410C"]}},
        "dark": {"page": "#16132A", "surface": "#201C38", "line": "#EFEAFF",
                 "ramps": {"brand": ["#AFA0FF", "#8A74FF", "#6547FF"], "accent": ["#FDE68A", "#FBBF24"]}},
    },
    "swiss": {
        "name": "Swiss",
        "about": "ink with a single red accent",
        "default": {"brand": "ink", "accent": "red", "detail": "ink"},
        "light": {"page": "#FFFFFF", "surface": "#FFFFFF", "line": "#111111",
                  "ramps": {"ink": ["#404040", "#111111"], "red": ["#ED1C3E", "#C8102E"]}},
        "dark": {"page": "#0F0F0F", "surface": "#171717", "line": "#F5F5F5",
                 "ramps": {"ink": ["#F5F5F5", "#A3A3A3"], "red": ["#FF5A6E", "#FF112E"]}},
    },
    "bauhaus": {
        "name": "Bauhaus",
        "about": "the three primaries as blocks, ink outlines",
        "default": {"brand": "blue", "accent": "yellow", "detail": "ink"},
        "stroke": True,
        "sticker": True,
        "light": {"page": "#F3EDE2", "surface": "#FFFAF0", "line": "#141414",
                  "pupil": "#141414",
                  "ramps": {"blue": ["#2F55DF", "#1D3FBB"], "red": ["#C0271B", "#8E1D14"],
                            "yellow": ["#FFD23F", "#F2B705"], "ink": ["#141414", "#141414"]}},
        "dark": {"page": "#121212", "surface": "#1C1C1C", "line": "#F3EDE2",
                 "pupil": "#F3EDE2",
                 "ramps": {"blue": ["#94ABFF", "#5C7EFF"], "red": ["#FF7A6E", "#E0503F"],
                           "yellow": ["#FFE27A", "#FFD23F"], "ink": ["#F3EDE2", "#F3EDE2"]}},
    },
    "brutalism": {
        "name": "Brutalism",
        "about": "raw black, link-blue accents",
        "default": {"brand": "ink", "accent": "link", "detail": "ink"},
        "light": {"page": "#FFFFFF", "surface": "#FFFFFF", "line": "#000000",
                  "ramps": {"ink": ["#333333", "#000000"], "link": ["#3838FF", "#0000EE"]}},
        "dark": {"page": "#000000", "surface": "#000000", "line": "#FFFFFF",
                 "ramps": {"ink": ["#FFFFFF", "#BDBDBD"], "link": ["#A3C4FF", "#8AB4FF"]}},
    },
    "neo-brutalism": {
        "name": "Neo-Brutalism",
        "about": "loud pink and yellow, thick ink outlines, hard offset shadow",
        "default": {"brand": "pink", "accent": "yellow", "detail": "ink"},
        "stroke": True,
        "shadow": True,
        "fill_gaps": True,
        "sticker": True,
        "light": {"page": "#FDF3E1", "surface": "#FFFFFF", "line": "#000000",
                  "pupil": "#000000",
                  "ramps": {"pink": ["#FF6B9D", "#E3216D"], "yellow": ["#FFE14D", "#FFD400"],
                            "ink": ["#000000", "#000000"]}},
        "dark": {"page": "#141414", "surface": "#1F1F1F", "line": "#FFFFFF",
                 "pupil": "#FFFFFF",
                 "ramps": {"pink": ["#FF86B0", "#FF1B6A"], "yellow": ["#FFE98C", "#FFD400"],
                           "ink": ["#FFFFFF", "#FFFFFF"]}},
    },
    "editorial": {
        "name": "Editorial",
        "about": "ink with a single press-red accent",
        "default": {"brand": "ink", "accent": "red", "detail": "ink"},
        "light": {"page": "#F3EEE3", "surface": "#F7F3EA", "line": "#1B1813",
                  "ramps": {"ink": ["#4A4236", "#1B1813"], "red": ["#D52525", "#941A1A"]}},
        "dark": {"page": "#14120E", "surface": "#1A1712", "line": "#ECE4D3",
                 "ramps": {"ink": ["#ECE4D3", "#A89D89"], "red": ["#E78A7D", "#DC5744"]}},
    },
    "minimal-mono": {
        "name": "Minimal Mono",
        "about": "one ink; accents are cut out of it",
        "default": {"brand": "ink", "accent": "cut", "detail": "ink"},
        "light": {"page": "#FAFAFA", "surface": "#FFFFFF", "line": "#171717",
                  "ramps": {"ink": ["#525252", "#171717"]}},
        "dark": {"page": "#0A0A0A", "surface": "#141414", "line": "#FAFAFA",
                 "ramps": {"ink": ["#FAFAFA", "#A3A3A3"]}},
    },
    "corporate": {
        "name": "Corporate",
        "about": "trust-blue, teal accents (c2)",
        "default": {"brand": "blue", "accent": "teal", "detail": "blue"},
        "light": {"page": "#F4F6F9", "surface": "#FFFFFF", "line": "#0F1D33",
                  "ramps": {"blue": ["#0E72D6", "#0B5CAD", "#05294D"], "teal": ["#3CCF9F", "#0F8A6B"]}},
        "dark": {"page": "#0B1220", "surface": "#111A2D", "line": "#E6EDF7",
                 "ramps": {"blue": ["#64A8FF", "#2081FF", "#0060DB"], "teal": ["#9BE8CC", "#3CCF9F"]}},
    },
    "nordic": {
        "name": "Nordic",
        "about": "muted blue-grey, sage accents (c2)",
        "default": {"brand": "slate", "accent": "sage", "detail": "slate"},
        "light": {"page": "#F2F5F7", "surface": "#FFFFFF", "line": "#1D2A33",
                  "ramps": {"slate": ["#3D78A0", "#2F5D7C", "#162C3B"], "sage": ["#95C4A2", "#4D7A5C"]}},
        "dark": {"page": "#11181D", "surface": "#18222A", "line": "#E7EEF2",
                 "ramps": {"slate": ["#B8D2E5", "#86B2D3", "#5593C1"], "sage": ["#C9E3D0", "#95C4A2"]}},
    },
}
