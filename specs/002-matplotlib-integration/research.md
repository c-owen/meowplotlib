# Research: Matplotlib Integration & Activation

Findings below come from inspecting matplotlib 3.10.8's installed source in this environment
(`matplotlib.figure`, `matplotlib.backend_bases`) via a research subagent, plus the clarify
session resolving the enable/disable mechanism and bbox granularity.

## Decision: Monkeypatch `matplotlib.figure.Figure.draw`

Wrap `Figure.draw(self, renderer)` at import time: `Figure.draw = _wrapped(Figure.draw)`.

**Rationale**: `Figure.savefig()` → `FigureCanvasBase.print_figure()` → `self.figure.draw(renderer)`
internally, and interactive backends' `canvas.draw()` also ultimately calls `Figure.draw`. This
is the single shared point where both the display path and the savefig path converge, satisfying
FR-002 with one hook instead of two separate patches (e.g. patching `savefig` AND `show`
separately, which would need to independently stay in sync).

**Alternatives considered**: `canvas.mpl_connect('draw_event', ...)` (rejected: fires *after*
rendering completes, too late to inject artists that then get included in that same render
pass — would require forcing a second draw, doubling render cost and reintroducing idempotency
risk); separately monkeypatching `Figure.savefig` and relying on `show()` triggering a draw via
its own path (rejected: two hook sites to keep behaviorally identical is more risk, not less,
for no benefit since `Figure.draw` already covers both).

## Decision: Per-instance idempotency flag, set inside the wrapper

Inside the wrapped `draw()`: if `getattr(self, "_meowplotlib_decorated", False)` is falsy, extract
exclusions, call M1's `place_cats()`, add the resulting artists via `self.add_artist(...)`, then
set `self._meowplotlib_decorated = True`. Always call the original `draw()` afterward (decoration
adds artists; the original draw still needs to render everything, cats included).

**Rationale**: A new `Figure()` instance has no `_meowplotlib_decorated` attribute, so the flag
naturally starts falsy — no explicit reset logic needed for new figures (confirmed in research:
each `plt.figure()` call constructs a fresh `Figure` object). The flag lives on the instance, not
a global registry, so there's no memory-leak/cleanup concern for figures that get garbage
collected.

**Alternatives considered**: A module-level `WeakSet` of decorated figure ids (rejected: strictly
more complex than an instance attribute for the same guarantee, and instance attributes are the
idiomatic matplotlib extension pattern — e.g. matplotlib itself stores plenty of private
`_`-prefixed state directly on `Figure`/`Axes` instances).

## Decision: Permanent single patch + `Config.enabled` flag-check (per clarify)

`Figure.draw` is replaced exactly once at import time, for the lifetime of the process. The
wrapper's first action on every call is to check `meowplotlib.core.config.get_config().enabled`;
if `False`, it calls the original draw immediately and returns, executing no other meowplotlib
code. `enable()`/`disable()` (already stubbed in `api.py` from M0) simply mutate that flag — no
re-patching.

**Rationale**: Confirmed with the user (see spec Clarifications) — a permanent class-level patch
is unavoidable for a zero-code-change activation model regardless of which option was chosen; the
flag-check approach is simpler and avoids re-entrancy bugs from repeated enable/disable calls.
Because the disabled path executes literally nothing but a call-through, output is provably
byte-identical to unpatched matplotlib (FR-004), satisfying constitution #4 without needing to
prove anything about monkeypatch reversibility.

**Alternatives considered**: Unpatch/repatch on every `disable()`/`enable()` call (rejected by
user after discussing implications — no behavioral benefit for this codebase, more edge cases).

## Decision: Whole-axes `get_tightbbox()` for exclusion extraction (per clarify)

For each `Axes` on the figure: call `ax.get_tightbbox(renderer)`, which already unions the data
area with its tick labels and axis labels into one bbox. If the axes has a legend
(`ax.get_legend()` is not `None`), additionally include the legend's `get_window_extent(renderer)`.
Convert each result from display (pixel) coordinates to figure-fraction coordinates via
`figure.transFigure.inverted()` before passing to M1's `place_cats()` (M1's contract expects
figure-fraction `Rect`s).

A renderer is obtained via `figure._get_renderer()` — confirmed in research this does not require
a prior draw pass and works uniformly across Agg and non-Agg interactive backends.

**Rationale**: Matches the clarify decision — a small handful of exclusion rectangles per figure
(one or two per axes) rather than one per tick label, keeping M1's O(exclusions × candidates)
collision-checking cost low and the extraction code simple. Being conservative (excluding a bit
more area than strictly necessary) only makes cats keep more distance from text, never overlap it
— acceptable and arguably desirable for a "never obscure data" product promise.

**Alternatives considered**: Per-element bboxes (rejected by user at clarify — more precision than
needed, more extraction code and collision-check cost, more surface area for bugs).

## Decision: M3 stub for style resolution during M2 (per spec Assumptions)

M2's artist-drawing step needs *some* image to draw per placement. Since M3 (style registry) may
not exist yet when M2 is implemented, M2 uses a minimal internal stub: a single simple
placeholder shape (e.g. reusing one of M0's already-generated placeholder PNGs directly, or an
even simpler filled circle) hardcoded as the only "style" available to the render layer for M2's
own tests. M3 replaces this stub with the real `assets/registry.py` lookup; M2's own tests do not
depend on M3 existing.

**Rationale**: Explicitly called out as an acceptable assumption in the spec so M2 isn't blocked
on M3 sequencing. STANDUP_PLAN.md's milestone order (M2 before M3) already anticipates this — M2
is scoped as "matplotlib integration," and style *selection* is M3's job, not M2's.

**Alternatives considered**: Block M2 implementation until M3 lands (rejected: STANDUP_PLAN.md's
explicit milestone order puts M2 before M3, and M2's own acceptance criteria don't require real
style variety — only that decoration exists, doesn't overlap, is idempotent, and disables
cleanly).
