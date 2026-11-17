"""A logo project: projects/<name>/ with its source, construction, theming and outputs."""
from __future__ import annotations

import importlib.util
import sys
from functools import cached_property
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _load(path: Path, name: str):
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))  # construction modules import logokit
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class Project:
    def __init__(self, name: str):
        self.name = name
        self.dir = ROOT / "projects" / name
        if not self.dir.is_dir():
            known = ", ".join(sorted(p.name for p in (ROOT / "projects").iterdir() if p.is_dir()))
            raise SystemExit(f"no project '{name}' (projects: {known})")

    # Layout
    @property
    def source(self): return self.dir / "source" / "original.svg"
    @property
    def reference_png(self): return self.dir / "reference" / "original.png"
    @property
    def analysis(self): return self.dir / "analysis"
    @property
    def compare_dir(self): return self.analysis / "compare"
    @property
    def output(self): return self.dir / "output"
    @property
    def reconstructed(self): return self.output / "reconstructed.svg"
    @property
    def styles_dir(self): return self.output / "styles"

    # Modules
    @cached_property
    def construction(self):
        return _load(self.dir / "construction.py", f"{self.name}_construction")

    @cached_property
    def theming(self):
        return _load(self.dir / "theming.py", f"{self.name}_theming")

    def style_set(self) -> dict:
        set_name = getattr(self.theming, "STYLE_SET", "owlky")
        return _load(ROOT / "styles" / f"{set_name}.py", f"styles_{set_name}").STYLES

    @cached_property
    def mark(self):
        from .build import Builder
        return self.construction.construct(Builder(self.source))
