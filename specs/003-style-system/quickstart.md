# Quickstart: Style System & Assets

## Prerequisites

```bash
source .venv/Scripts/activate
export MPLBACKEND=Agg
```

## Run the automated acceptance tests

```bash
pytest tests/assets/ -q
```

## Manual smoke check

```python
from catplotlib.assets.registry import available_styles, resolve_style_names

styles = available_styles()
assert set(styles) == {"classic", "derp", "chonk"}

assert resolve_style_names("chonk") == ["chonk"]
assert resolve_style_names(["classic", "derp"]) == ["classic", "derp"]
assert set(resolve_style_names("mix")) == {"classic", "derp", "chonk"}

try:
    resolve_style_names("not-a-real-style")
    raise AssertionError("expected ValueError")
except ValueError:
    pass
```

```python
import io
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import catplotlib

catplotlib.set_style("chonk")
catplotlib.set_seed(1)
catplotlib.set_density("chaotic")

fig, ax = plt.subplots()
ax.plot([1, 2, 3], [1, 4, 9])
buf = io.BytesIO()
fig.savefig(buf, format="png")

# reproducibility survives style resolution end to end
buf2 = io.BytesIO()
fig2, ax2 = plt.subplots()
ax2.plot([1, 2, 3], [1, 4, 9])
fig2.savefig(buf2, format="png")
assert buf.getvalue() == buf2.getvalue()
```

## Expected outcome

All assertions pass. `styles` contains exactly the three launch styles; an unregistered style
name raises immediately; seeded renders remain byte-identical across repeated calls even with
multi-image style pools in play.
