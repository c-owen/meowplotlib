"""catplotlib: whimsical cat decorations for matplotlib figures."""

from catplotlib.api import config, disable, enable, set_density, set_seed, set_style
from catplotlib.render.hook import install as _install

__all__ = ["config", "disable", "enable", "set_density", "set_seed", "set_style"]
__version__ = "0.1.0"

_install()
