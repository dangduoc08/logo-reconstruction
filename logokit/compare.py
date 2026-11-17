"""Raster comparison of a project's reconstruction against its source.

Needs the packages in requirements.txt and rsvg-convert on PATH. The reference is the source
SVG rendered in the reconstruction's frame (a reference/original.png is reported but not used:
it isn't frame-aligned). Writes analysis/compare/*.png and prints the metrics.

    .venv/bin/python -m logokit compare <project> [--scale 4]
"""
from __future__ import annotations

import re
import subprocess
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage


def strip_source(source: Path):
    text = re.sub(r"<metadata>.*?</metadata>", "", source.read_text(), flags=re.S)
    defs = re.findall(r"<defs>.*?</defs>", text, flags=re.S)
    return (defs[0] if defs else ""), re.findall(r"<path[^>]*/>", text)


def render(svg_text, width, path):
    with tempfile.NamedTemporaryFile("w", suffix=".svg", delete=False) as f:
        f.write(svg_text)
    subprocess.run(["rsvg-convert", "-b", "white", "-w", str(width), f.name, "-o", str(path)], check=True)
    return np.asarray(Image.open(path).convert("RGB")).astype(np.int32)


def classify(img, colors):
    """Unmix each pixel into the source's colors (least squares, first color = background) and
    keep the largest coverage.

    Nearest-color matching sent anti-aliased edges to the wrong class (a 50% navy-on-white pixel
    is closer to gold than to either), which drew false outlines around shapes."""
    cols = [np.array(c, dtype=float) for c in colors.values()]
    bg = cols[0]
    basis = np.stack([c - bg for c in cols[1:]], axis=1)  # 3 x k
    pinv = np.linalg.pinv(basis)
    cov = np.clip((img.reshape(-1, 3) - bg) @ pinv.T, 0, 1)
    full = np.concatenate([1 - cov.sum(1, keepdims=True), cov], axis=1)
    return full.argmax(1).reshape(img.shape[:2]).astype(np.int8)


def edge_distance(a, b, scale):
    """Distances from each boundary pixel of mask a to the nearest boundary pixel of mask b, in units."""
    edge = lambda m: m & ~ndimage.binary_erosion(m)
    ea, eb = edge(a), edge(b)
    dist = ndimage.distance_transform_edt(~eb)
    return dist[ea] / scale


def max_thickness(mask):
    """Erosion steps (4-neighbour) until the mask is empty: half the thickest blob, in pixels."""
    m = mask.copy()
    steps = 0
    while m.any():
        steps += 1
        e = m.copy()
        e[1:, :] &= m[:-1, :]; e[:-1, :] &= m[1:, :]
        e[:, 1:] &= m[:, :-1]; e[:, :-1] &= m[:, 1:]
        m = e
        if steps > 200:
            break
    return steps


def compare(source: Path, recon: Path, out: Path, frame, colors: dict, zooms: dict,
            scale: float = 2.0, reference_png: Path | None = None):
    """frame: (ox, oy, w, h), the reconstruction's viewBox in source units."""
    out.mkdir(parents=True, exist_ok=True)
    ox, oy, w, h = frame
    px_w = int(round(w * scale))

    defs, paths = strip_source(source)
    orig_svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{ox} {oy} {w} {h}">'
                f"{defs}{''.join(paths[1:])}</svg>")
    recon_text = recon.read_text()

    if reference_png and reference_png.exists():
        print(f"reference: {reference_png.name} is present but not frame-aligned; using the SVG render")
    ref = render(orig_svg, px_w, out / "reference.png")
    rec = render(recon_text, px_w, out / "reconstructed.png")

    a, b = classify(ref, colors), classify(rec, colors)
    print(f"frame {w}x{h} units at {scale} px/unit -> {ref.shape[1]}x{ref.shape[0]} px")
    for i, name in enumerate(colors):
        if i == 0:
            continue
        inter = np.logical_and(a == i, b == i).sum()
        union = np.logical_or(a == i, b == i).sum()
        only_ref = np.logical_and(a == i, b != i)
        only_rec = np.logical_and(b == i, a != i)
        t_ref = max_thickness(only_ref) / scale
        t_rec = max_thickness(only_rec) / scale
        print(f"{name:5s} IoU {inter / union * 100:6.3f}%  missing {only_ref.sum():6d} px (max half-width {t_ref:.1f} u)"
              f"  extra {only_rec.sum():6d} px (max half-width {t_rec:.1f} u)")
        d = np.concatenate([edge_distance(a == i, b == i, scale), edge_distance(b == i, a == i, scale)])
        print(f"      edge distance (units): median {np.median(d):.2f}  p99 {np.percentile(d, 99):.2f}"
              f"  p99.9 {np.percentile(d, 99.9):.2f}  max {d.max():.2f}")
    mismatch = a != b
    print(f"all   mismatch {mismatch.mean() * 100:.3f}% of pixels")

    # Difference image: faint reference, red = reference only, blue = reconstruction only,
    # magenta = two colors swapped.
    base = 255 - (255 - ref) * 0.25
    diff = base.copy()
    diff[np.logical_and(mismatch, a != 0)] = (220, 30, 30)
    diff[np.logical_and(mismatch, a == 0)] = (30, 90, 230)
    diff[np.logical_and(mismatch, np.logical_and(a != 0, b != 0))] = (230, 0, 230)
    Image.fromarray(diff.astype(np.uint8)).save(out / "diff.png")

    # Overlay: the reference at half opacity under the reconstruction's outlines.
    outline = re.sub(r'fill="[^"]*"', 'fill="none" stroke="#E0102F" stroke-width="0.8"', recon_text)
    outline = outline.replace("<path", '<path vector-effect="non-scaling-stroke"')
    inner = re.search(r"<svg[^>]*>(.*)</svg>", outline, flags=re.S).group(1)
    overlay_svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}">'
                   f'<g opacity="0.45" transform="translate({-ox} {-oy})">{defs}{"".join(paths[1:])}</g>'
                   f"{inner}</svg>")
    (out / "overlay.svg").write_text(overlay_svg)
    render(overlay_svg, px_w, out / "overlay.png")

    # Close-ups at high magnification (8 px per unit), overlay and difference side by side.
    zoom = 8
    for name, (x, y, zw, zh) in zooms.items():
        vb_svg = re.sub(r'viewBox="[^"]+"', f'viewBox="{x} {y} {zw} {zh}"', overlay_svg, count=1)
        ov = render(vb_svg, int(zw * zoom), out / f"zoom-{name}.png")
        crop = diff[int(y * scale):int((y + zh) * scale), int(x * scale):int((x + zw) * scale)]
        crop_img = Image.fromarray(crop.astype(np.uint8)).resize((ov.shape[1], ov.shape[0]), Image.NEAREST)
        sheet = Image.new("RGB", (ov.shape[1] * 2 + 8, ov.shape[0]), "white")
        sheet.paste(Image.fromarray(ov.astype(np.uint8)), (0, 0))
        sheet.paste(crop_img, (ov.shape[1] + 8, 0))
        sheet.save(out / f"zoom-{name}.png")

    # Normal size: reference and reconstruction side by side at 512, 128, 48 and 24 px tall.
    tiles = []
    for size in (512, 128, 48, 24):
        pw = max(1, round(size * w / h))
        r1 = Image.fromarray(render(orig_svg, pw, out / "_tmp.png").astype(np.uint8))
        r2 = Image.fromarray(render(recon_text, pw, out / "_tmp.png").astype(np.uint8))
        tiles += [r1, r2]
    (out / "_tmp.png").unlink()
    sheet = Image.new("RGB", (sum(t.width for t in tiles) + 16 * len(tiles), 560), "white")
    x = 8
    d = ImageDraw.Draw(sheet)
    for i, t in enumerate(tiles):
        sheet.paste(t, (x, 30))
        d.text((x, 8), "ref" if i % 2 == 0 else "new", fill=(0, 0, 0))
        x += t.width + 16
    sheet.save(out / "sizes.png")
