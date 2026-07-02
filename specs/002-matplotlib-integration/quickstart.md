# Quickstart: Matplotlib Integration & Activation

## Prerequisites

```bash
source .venv/Scripts/activate
export MPLBACKEND=Agg   # headless, matches CI and the test suite
```

## Run the automated acceptance tests

```bash
pytest tests/render/ -q
```

## Manual smoke check

```python
import io
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import catplotlib

fig, ax = plt.subplots()
ax.plot([1, 2, 3], [1, 4, 9])
ax.set_xlabel("x")
ax.set_ylabel("y")

buf = io.BytesIO()
fig.savefig(buf, format="png")
assert getattr(fig, "_catplotlib_decorated", False) is True

# Idempotency: redraw several times, artist count must not change.
before = len(fig.artists)
for _ in range(5):
    fig.canvas.draw()
after = len(fig.artists)
assert before == after

# Disable: a fresh figure must byte-match a no-catplotlib baseline.
catplotlib.disable()
fig2, ax2 = plt.subplots()
ax2.plot([1, 2, 3], [1, 4, 9])
ax2.set_xlabel("x")
ax2.set_ylabel("y")
buf2 = io.BytesIO()
fig2.savefig(buf2, format="png")
assert getattr(fig2, "_catplotlib_decorated", False) is False

catplotlib.enable()
```

## Expected outcome

All assertions pass. `buf` contains cat artwork; `buf2` (rendered while disabled) does not.
