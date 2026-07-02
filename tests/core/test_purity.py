"""Constitution #1: core/ SHALL NOT import matplotlib or perform I/O."""

from __future__ import annotations

import ast
from pathlib import Path

CORE_DIR = Path(__file__).resolve().parent.parent.parent / "src" / "meowplotlib" / "core"

BANNED_MODULE_PREFIXES = ("matplotlib",)
BANNED_IO_MODULES = {"pathlib", "open", "io"}


def _imported_modules(tree: ast.Module) -> set[str]:
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)
    return modules


def test_core_does_not_import_matplotlib() -> None:
    for path in CORE_DIR.glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        modules = _imported_modules(tree)
        offenders = {m for m in modules if m.startswith(BANNED_MODULE_PREFIXES)}
        assert not offenders, f"{path} imports matplotlib: {offenders}"


def test_core_does_not_open_files() -> None:
    for path in CORE_DIR.glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                assert node.func.id != "open", f"{path} calls open() directly"
