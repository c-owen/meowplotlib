"""Tests for catplotlib.assets.registry — see specs/003-style-system/."""

from __future__ import annotations

from pathlib import Path

import pytest

from catplotlib.assets.registry import available_styles, discover_styles, resolve_style_names

# --- Foundational: discover_styles() against fixtures --------------------------------


def _write_png(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    # Minimal valid 1x1 PNG (not a real cat, just needs to exist as a file with a .png suffix).
    path.write_bytes(
        bytes.fromhex(
            "89504e470d0a1a0a0000000d494844520000000100000001080600000"
            "01f15c4890000000a4944415478da6360000002000155a3e0e50000000049454e44ae426082"
        )
    )


def _write_manifest(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_discover_styles_requires_both_dir_and_manifest_entry(tmp_path: Path) -> None:
    images_dir = tmp_path / "images"
    manifest = tmp_path / "styles.toml"

    _write_png(images_dir / "onlydir" / "a.png")  # no manifest entry
    _write_manifest(
        manifest,
        '[styles.onlymanifest]\ndisplay_name = "Only Manifest"\n'
        '\n[styles.both]\ndisplay_name = "Both"\nscale = 1.0\n',
    )
    _write_png(images_dir / "both" / "a.png")

    styles = discover_styles(images_dir, manifest)

    assert set(styles) == {"both"}


def test_discover_styles_excludes_empty_image_directory(tmp_path: Path) -> None:
    images_dir = tmp_path / "images"
    manifest = tmp_path / "styles.toml"
    (images_dir / "empty").mkdir(parents=True)
    _write_manifest(manifest, '[styles.empty]\ndisplay_name = "Empty"\n')

    styles = discover_styles(images_dir, manifest)

    assert styles == {}


def test_discover_styles_missing_manifest_or_dir_returns_empty(tmp_path: Path) -> None:
    assert discover_styles(tmp_path / "nope", tmp_path / "also-nope.toml") == {}


def test_discover_styles_malformed_entry_does_not_break_others(tmp_path: Path) -> None:
    images_dir = tmp_path / "images"
    manifest = tmp_path / "styles.toml"
    _write_png(images_dir / "good" / "a.png")
    _write_png(images_dir / "bad" / "a.png")
    _write_manifest(
        manifest,
        "[styles.bad]\n# missing display_name entirely\n"
        '\n[styles.good]\ndisplay_name = "Good"\nscale = 1.0\n',
    )

    styles = discover_styles(images_dir, manifest)

    assert set(styles) == {"good"}


def test_discover_styles_returns_all_images_in_pool(tmp_path: Path) -> None:
    images_dir = tmp_path / "images"
    manifest = tmp_path / "styles.toml"
    _write_png(images_dir / "multi" / "b.png")
    _write_png(images_dir / "multi" / "a.png")
    _write_manifest(manifest, '[styles.multi]\ndisplay_name = "Multi"\n')

    styles = discover_styles(images_dir, manifest)

    assert [p.name for p in styles["multi"].image_paths] == ["a.png", "b.png"]  # sorted
    assert styles["multi"].scale == 1.0  # default when omitted


# --- User Story 1: single style ------------------------------------------------------


def test_available_styles_returns_the_three_launch_styles() -> None:
    styles = available_styles()
    assert set(styles) == {"classic", "derp", "chonk"}


def test_launch_style_placeholders_are_pairwise_pixel_distinct() -> None:
    styles = available_styles()
    contents = {name: info.image_paths[0].read_bytes() for name, info in styles.items()}
    values = list(contents.values())
    assert len(set(values)) == len(values)


# --- User Story 2: mixing --------------------------------------------------------------


def test_resolve_style_names_single_and_list() -> None:
    assert resolve_style_names("chonk") == ["chonk"]
    assert resolve_style_names(["classic", "derp"]) == ["classic", "derp"]


def test_resolve_style_names_mix_returns_all_registered() -> None:
    assert set(resolve_style_names("mix")) == {"classic", "derp", "chonk"}


def test_resolve_style_names_unknown_raises() -> None:
    with pytest.raises(ValueError, match="Unknown style"):
        resolve_style_names("not-a-real-style")

    with pytest.raises(ValueError, match="Unknown style"):
        resolve_style_names(["classic", "not-a-real-style"])
