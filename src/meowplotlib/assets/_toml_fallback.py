"""Minimal parser for styles.toml on Python < 3.11 (no stdlib tomllib).

NOT a general-purpose TOML parser. Covers exactly the subset styles.toml uses: flat
`[styles.<name>]` sections, each with a quoted `display_name` string and an optional numeric
`scale`. See specs/003-style-system/research.md for why this exists instead of a dependency.
"""

from __future__ import annotations

import re

_SECTION_RE = re.compile(r"^\[styles\.([A-Za-z0-9_-]+)\]\s*$")
_STRING_KV_RE = re.compile(r'^display_name\s*=\s*"([^"]*)"\s*$')
_FLOAT_KV_RE = re.compile(r"^scale\s*=\s*([0-9.]+)\s*$")


def loads(text: str) -> dict[str, object]:
    """Parse styles.toml's specific shape into {"styles": {name: {...}}}."""
    styles: dict[str, dict[str, object]] = {}
    current: str | None = None

    for raw_line in text.splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line:
            continue

        section_match = _SECTION_RE.match(line)
        if section_match:
            current = section_match.group(1)
            styles[current] = {}
            continue

        if current is None:
            continue

        string_match = _STRING_KV_RE.match(line)
        if string_match:
            styles[current]["display_name"] = string_match.group(1)
            continue

        float_match = _FLOAT_KV_RE.match(line)
        if float_match:
            styles[current]["scale"] = float(float_match.group(1))
            continue

    return {"styles": styles}
