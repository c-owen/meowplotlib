"""Packaging smoke test: build the wheel, install it in a clean venv, run the one-liner.

Per STANDUP_PLAN.md §8. Slower than the rest of the suite (builds + creates a venv) since it
exercises the actual installed-package path (importlib.resources against real wheel contents)
rather than the editable dev install every other test runs against.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import venv
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent

SMOKE_SCRIPT = """
import io
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import catplotlib

fig, ax = plt.subplots()
ax.plot([1, 2, 3], [1, 4, 9])
buf = io.BytesIO()
fig.savefig(buf, format="png")
assert getattr(fig, "_catplotlib_decorated", False) is True
cat_count = sum(1 for a in fig.axes if getattr(a, "_catplotlib_cat", False))
assert cat_count > 0
print("SMOKE_TEST_OK", cat_count)
"""


@pytest.mark.skipif(shutil.which("uv") is None, reason="requires uv for fast venv creation")
def test_wheel_installs_and_renders_cats_in_a_clean_venv(tmp_path: Path) -> None:
    dist_dir = tmp_path / "dist"
    subprocess.run(
        [sys.executable, "-m", "build", "--wheel", "--outdir", str(dist_dir)],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
    )
    wheels = list(dist_dir.glob("*.whl"))
    assert len(wheels) == 1, f"expected exactly one wheel, found {wheels}"

    venv_dir = tmp_path / "venv"
    venv.create(venv_dir, with_pip=True)
    venv_python = (
        venv_dir / "Scripts" / "python.exe"
        if sys.platform == "win32"
        else (venv_dir / "bin" / "python")
    )

    subprocess.run(
        ["uv", "pip", "install", "--python", str(venv_python), str(wheels[0])],
        check=True,
        capture_output=True,
    )

    result = subprocess.run(
        [str(venv_python), "-c", SMOKE_SCRIPT],
        capture_output=True,
        text=True,
        env={**os.environ, "MPLBACKEND": "Agg"},
    )
    assert result.returncode == 0, result.stderr
    assert "SMOKE_TEST_OK" in result.stdout
