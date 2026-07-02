"""Discovers styles from the assets dir + manifest. Zero-code-change style extension.

Re-scans the filesystem on every query rather than caching (see research.md) — style counts are
tiny, and this keeps "drop a file, it just works" true even mid-process.
"""

from __future__ import annotations

import importlib.resources
import sys
from dataclasses import dataclass, field
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:
    from catplotlib.assets import _toml_fallback as tomllib  # type: ignore[no-redef]

IMAGE_SUFFIXES = (".png",)


@dataclass(frozen=True)
class StyleInfo:
    """A discovered, valid style: has both an image directory and a manifest entry."""

    name: str
    display_name: str
    scale: float = 1.0
    image_paths: list[Path] = field(default_factory=list)


def _parse_manifest(manifest_path: Path) -> dict[str, dict[str, object]]:
    if not manifest_path.is_file():
        return {}
    if sys.version_info >= (3, 11):
        with manifest_path.open("rb") as f:
            data = tomllib.load(f)
    else:
        data = tomllib.loads(manifest_path.read_text(encoding="utf-8"))
    styles = data.get("styles", {})
    return styles if isinstance(styles, dict) else {}


def discover_styles(images_dir: Path, manifest_path: Path) -> dict[str, StyleInfo]:
    """Scan `images_dir` + parse `manifest_path`; return styles with both present."""
    manifest_styles = _parse_manifest(manifest_path)
    result: dict[str, StyleInfo] = {}

    if not images_dir.is_dir():
        return result

    for style_dir in sorted(images_dir.iterdir()):
        if not style_dir.is_dir():
            continue
        name = style_dir.name
        manifest_entry = manifest_styles.get(name)
        if not isinstance(manifest_entry, dict):
            continue

        image_paths = sorted(p for p in style_dir.iterdir() if p.suffix.lower() in IMAGE_SUFFIXES)
        if not image_paths:
            continue

        display_name = manifest_entry.get("display_name")
        if not isinstance(display_name, str):
            continue
        scale = manifest_entry.get("scale", 1.0)
        if not isinstance(scale, int | float):
            scale = 1.0

        result[name] = StyleInfo(
            name=name,
            display_name=display_name,
            scale=float(scale),
            image_paths=image_paths,
        )

    return result


def available_styles() -> dict[str, StyleInfo]:
    """Discover styles from the package's own bundled assets tree."""
    images_root = importlib.resources.files("catplotlib.assets") / "images"
    manifest = importlib.resources.files("catplotlib.assets") / "styles.toml"
    with (
        importlib.resources.as_file(images_root) as images_dir,
        importlib.resources.as_file(manifest) as manifest_path,
    ):
        return discover_styles(images_dir, manifest_path)


def resolve_style_names(selection: str | list[str]) -> list[str]:
    """Resolve set_style()'s raw value to a flat, validated list of style names."""
    styles = available_styles()

    if selection == "mix":
        return list(styles)

    names = [selection] if isinstance(selection, str) else selection
    for name in names:
        if name not in styles:
            raise ValueError(f"Unknown style: {name!r}. Available styles: {sorted(styles)}")
    return list(names)
