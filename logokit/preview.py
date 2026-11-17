"""Contact sheet of every themed variant: light and dark side by side on the style's page."""
from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw


def _render(svg: str, height: int) -> Image.Image:
    with tempfile.TemporaryDirectory() as tmp:
        src, png = Path(tmp) / "t.svg", Path(tmp) / "t.png"
        src.write_text(svg)
        subprocess.run(["rsvg-convert", "-h", str(height), str(src), "-o", str(png)], check=True)
        return Image.open(png).convert("RGB")


def _on_page(svg: str, page: str) -> str:
    # A page-colored rectangle under everything (the marks are transparent).
    head_end = svg.index(">") + 1
    return svg[:head_end] + f'<rect x="-200" y="-200" width="4000" height="4000" fill="{page}"/>' + svg[head_end:]


def contact_sheet(styles: dict, styles_dir: Path, out: Path, cols: int = 3):
    cells = []
    for sid, st in styles.items():
        row = []
        for mode in ("light", "dark"):
            page = st[mode]["page"]
            svg = _on_page((styles_dir / f"{sid}-{mode}.svg").read_text(), page)
            tile = Image.new("RGB", (330, 300), page)
            tile.paste(_render(svg, 270), (10, 15))
            tile.paste(_render(svg, 32), (280, 250))
            row.append(tile)
        cells.append((st["name"], row))
    width = cols * (2 * 330 + 30) + 20
    height = ((len(cells) + cols - 1) // cols) * 340 + 20
    sheet = Image.new("RGB", (width, height), "#d9d9d9")
    draw = ImageDraw.Draw(sheet)
    for i, (name, row) in enumerate(cells):
        x, y = 20 + (i % cols) * (2 * 330 + 30), 20 + (i // cols) * 340
        draw.text((x, y), name, fill="black")
        sheet.paste(row[0], (x, y + 18))
        sheet.paste(row[1], (x + 330, y + 18))
    sheet.save(out)
