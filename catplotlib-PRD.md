# catplotlib — Product Requirements Document

**Status:** Draft v1
**Owner:** Product
**Audience:** Engineering (implementation handoff)

---

## Overview

`catplotlib` is a Python package that adds whimsical cat artwork to the borders of `matplotlib` figures with a single import. It is a "decorator" library in the spirit of `seaborn` — it doesn't replace `matplotlib`, it sits on top of it and changes how figures render, with zero required changes to existing plotting code.

The product is unapologetically a novelty/delight tool, not a data-viz utility. Its entire value is emotional and social: it makes plots more fun to look at, more memorable in a talk or notebook, and more shareable. Success looks like people screenshotting their cat-bordered charts and posting them, not like measurable gains in "data comprehension."

---

## Problem Statement

Data scientists and engineers spend a lot of time looking at and sharing `matplotlib` charts — in notebooks, in Slack, in slide decks, in READMEs. Default `matplotlib` output is famously utilitarian and a little joyless, and existing styling tools (`seaborn`, custom `rcParams`, themes) only address color palettes, fonts, and layout — none of them address personality or humor.

There is a long-running tradition of novelty Python packages (`antigravity`, `this`, `wat`, joke ASCII-art libraries, etc.) that exist purely to make developers smile, and a similar tradition of meme/animal-themed developer tooling. There isn't currently a well-known equivalent for `matplotlib` that adds cats to plots. This is a low-stakes, high-delight gap: nobody is losing money over it, but there's a clear opportunity to make something people enjoy using and want to show off.

**Who feels this:** Python users who make charts regularly (data scientists, analysts, students, hobbyist coders) and who enjoy expressive/fun developer tools. Also relevant to educators and conference speakers who want a lighthearted visual hook in presentations.

**Cost of not solving it:** None — this is an opportunity bet, not a pain-relief bet. The "cost" is purely the opportunity cost of not shipping something fun and shareable.

---

## Goals

1. **Trivial adoption**: A user can go from "never heard of this" to "cats on my plot" in under one minute — a single `pip install` and a single `import` line, no required configuration.
2. **Delight and shareability**: The default output should be genuinely charming and screenshot-worthy without any tuning by the user.
3. **Non-destructive by default**: Adding `catplotlib` to an existing project must never obscure data, break existing layouts, or alter chart semantics (axes, legends, data points remain fully readable).
4. **Configurable whimsy**: Users who want more control (density, art style, placement, randomness seed) can get it through a small, discoverable configuration surface — without needing that configuration to get a good default result.
5. **A library of distinct, recognizable cat "styles"** (e.g. classic, derp, chonk, and other meme-inspired variants) that users can select or mix, so the tool has replay value rather than being a one-joke novelty.

### Non-Goals

- **Not a charting library.** `catplotlib` will never provide its own plot types, data transforms, or replace `matplotlib`/`seaborn` for actual visualization work. Out of scope permanently.
- **Not pursuing statistical/appearance neutrality.** Unlike `seaborn`, this tool is not trying to be "safe" for professional or academic publication by default — that's a possible configuration state (e.g. "off"), not the design center.
- **Not building original character art in-house for v1.** We are not standing up an illustration pipeline or commissioning original mascot art as part of this release; v1 ships with a small set of externally-sourced or provided art assets. Custom/commissioned art is a future consideration, not a v1 requirement.
- **Not supporting plotting libraries other than `matplotlib`** (e.g. Plotly, Bokeh, Altair) in v1. Seaborn compatibility is in scope only because Seaborn is built directly on `matplotlib` figures/axes.
- **Not building a GUI or web app.** This is a Python library configured in code, not a hosted service or visual editor.

---

## Personas & User Stories

**Primary persona — "Playful Data Scientist":** Writes Python in Jupyter/Colab notebooks regularly, cares about the output looking nice, follows novelty/joke dev tools on social media and enjoys sharing them.

- As a playful data scientist, I want to add one import to my notebook and have my existing plots get cat decorations, so that I don't have to rewrite any plotting code to get the effect.
- As a playful data scientist, I want the cats placed so they never cover my data, axes, or legend, so that my chart is still fully usable and readable.
- As a playful data scientist, I want to control how many cats appear and how chaotic the placement looks, so that I can dial the effect from "subtle" to "over the top" depending on my audience.
- As a playful data scientist, I want to pick a specific cat "mood" or style (e.g. a chonky cat vs. a derpy cat), so that the joke matches the vibe I'm going for.
- As a playful data scientist, I want the same code to produce the same cat layout when I set a seed, so that a chart doesn't visually change every time I regenerate it for a report.

**Secondary persona — "Conference/Classroom Presenter":** Builds slide decks or teaching notebooks and wants a lighthearted visual moment without spending design time.

- As a presenter, I want a low-effort way to make a technical chart feel less dry for a live audience, so that I can use it as a small moment of levity in a talk.
- As a presenter, I want to easily turn the effect off for the charts that need to stay professional (e.g. exporting a client-facing report from the same notebook), so that I'm not stuck with cats everywhere.

**Tertiary persona — "Package Browser":** Discovers the package on GitHub/PyPI/social media and just wants to be delighted quickly, possibly without ever using it in a real project.

- As a package browser, I want the README to show an eye-catching before/after example immediately, so that I understand the whole value proposition in five seconds without reading documentation.

---

## Requirements

### Must-Have (P0)

**1. One-line activation**
- Importing the package applies the effect to subsequently rendered/saved `matplotlib` figures without additional setup calls.
- Acceptance criteria:
  - [ ] A user with an existing `matplotlib` script can add a single import line and see cats appear on the next plot they render or save, with no other code changes.
  - [ ] Works for both interactive display (e.g. in a notebook) and file export (e.g. `savefig`).

**2. Non-destructive rendering**
- Cat artwork is confined to a border/margin region and never overlaps the plot's data area, axis labels, tick labels, or legend by default.
- Acceptance criteria:
  - [ ] Across a representative set of common chart types (line, bar, scatter, histogram) and figure sizes, cats do not visually overlap data or text elements at default settings.
  - [ ] The effect degrades gracefully on very small figures (e.g. thumbnail-sized) rather than producing broken or illegible output — reduced cat count/size is acceptable, visual corruption is not.

**3. Whimsical, randomized placement**
- Cats are placed with randomized position, size, and rotation within their allowed zone, so that repeated plots don't look mechanically tiled.
- Acceptance criteria:
  - [ ] Two plots generated back-to-back (without a fixed seed) visibly differ in cat placement.
  - [ ] Placement still respects the non-destructive rule above regardless of randomization.

**4. Reproducibility control**
- A seed setting exists so a user can lock in a specific "random" layout and get identical output on repeated runs.
- Acceptance criteria:
  - [ ] Setting the same seed value twice, on the same plot, produces pixel-identical (or visually identical) cat placement.
  - [ ] Leaving the seed unset preserves default randomized behavior.

**5. Density control**
- Users can adjust how many cats appear, from sparse to heavily populated.
- Acceptance criteria:
  - [ ] At least three meaningfully distinct density levels are available (e.g. sparse / normal / chaotic), and the difference between them is visually obvious.

**6. Multiple cat styles, selectable**
- At least three distinct, recognizable cat art styles are available at launch (e.g. a "classic" straightforward cat plus two meme-inspired variants such as "derp" and "chonk"), and a user can select one or allow a mix.
- Acceptance criteria:
  - [ ] Each style is visually distinguishable from the others at typical render size (i.e. not just a minor palette change).
  - [ ] A user can select a single style for the whole figure, or allow the tool to mix styles across cats on the same figure.

**7. Global on/off control**
- A user can fully disable the effect within a session (e.g. for a specific figure or for the rest of the script) without uninstalling the package or restarting their environment.
- Acceptance criteria:
  - [ ] A documented, discoverable way exists to turn the effect off and back on within the same running session.

### Nice-to-Have (P1)

- **Placement mode control**: choice between border-only, corners-only, or scattered-anywhere-non-overlapping placement.
- **Size range control**: user-adjustable min/max cat size independent of density.
- **Rotation control**: ability to cap or disable rotation of individual cats.
- **Per-figure override**: ability to set different config (style, density, on/off) for one specific figure without changing the global/session default.
- **Style weighting**: when mixing styles, let the user bias the mix (e.g. "mostly classic, occasional chonk") rather than uniform random selection.
- **Expanded style library**: additional meme-inspired styles beyond the initial three (e.g. sleepy/loaf, floofy, judgmental side-eye).

### Future Considerations (P2)

- Support for other plotting libraries (Plotly, Bokeh, Altair).
- A "long cat" style that stretches along an entire edge rather than tiling as discrete images, implying a different placement model than the rest of the styles.
- Community-contributed style packs (a defined format for third parties to add their own cat art sets).
- Animated/GIF export support (cats that shift between frames).
- A companion "gallery" mode or command that renders a quick preview grid of all available styles/settings without requiring the user to build their own test plot.

We are not committing to these for v1, but P0/P1 design decisions (especially around how styles and placement are configured) should not accidentally foreclose them.

---

## Success Metrics

This is a novelty/delight product; success is primarily about reach and sentiment, not retention or revenue.

**Leading indicators (first 2–4 weeks post-launch):**
- Package installs (PyPI download count).
- GitHub stars / repo engagement as a proxy for "people found this delightful enough to bookmark or share."
- Qualitative social sharing: mentions, screenshots, or posts showing generated output (tracked manually/informally given this is a small novelty project).

**Lagging indicators (1–3 months post-launch):**
- Sustained or growing install trend (vs. a one-time spike from an initial launch post), indicating word-of-mouth pickup rather than a single burst.
- Community contributions (issues, PRs, requests for new styles) as a signal of genuine engagement rather than passive downloads.

**Explicit non-metrics:** We are not measuring or optimizing for retention, session length, or any claim about improved data comprehension — those framings don't fit what this product is for.

---

## Constraints & Assumptions

- **Distribution:** Standard Python packaging (installable via `pip`), consistent with how `matplotlib`/`seaborn` are typically installed.
- **Dependency footprint:** Should add minimal required dependencies beyond `matplotlib` itself, to keep adoption friction low.
- **Art assets:** v1 art assets will be provided/sourced externally (not generated by the engineering team as part of this spec); the implementation should treat the art set as swappable/extensible rather than hard-coded, so provided assets can be dropped in without redesigning the placement system.
- **No backend/service:** Everything runs client-side in the user's Python process. No network calls, accounts, or hosted components.

---

## Open Questions

- **[Product]** Should the effect be opt-in per figure by default, or opt-out globally after import? Current spec assumes "opt-out globally after import" (import applies it everywhere) but this affects the "non-destructive" expectations for teams who share notebooks. (Non-blocking, but should be resolved before finalizing the P0 activation behavior.)
- **[Design/Product]** For the "mixed styles on one figure" behavior (P0 requirement 6), what's the right default mix — even weighting across styles, or classic-dominant with occasional meme styles? (Non-blocking; can ship a reasonable default and adjust based on early feedback.)
- **[Engineering]** What is the right default behavior on very small or export-constrained figures (e.g. a 2x2 inch thumbnail) — reduce cat count automatically, or leave sizing entirely to the user's density/size settings? (Non-blocking, but affects the "graceful degradation" acceptance criterion under requirement 2.)

---

## Timeline Considerations

No hard external deadline. Recommended phasing:

- **Phase 1 (v1 / this spec):** All P0 requirements. Ship with the minimum viable style set (three styles) and core config surface (density, style, seed, on/off).
- **Phase 2 (fast follow):** P1 requirements — placement modes, size/rotation controls, per-figure overrides, expanded style library.
- **Phase 3 (future):** P2 considerations, prioritized based on community feedback and contribution activity after Phase 1/2 are live.
