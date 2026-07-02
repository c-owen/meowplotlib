# Tasks: Style System & Assets

**Input**: Design documents from `specs/003-style-system/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/registry-api.md, quickstart.md

**Tests**: Included — constitution #7's zero-code-change guarantee and #3's reproducibility
guarantee both need direct verification; lightweight scope keeps the test count small.

**Organization**: Tasks grouped by user story (spec.md priorities).

## Format: `[ID] [P?] [Story] Description`

## Path Conventions

Single project. `src/catplotlib/assets/`, `src/catplotlib/render/artist.py`, `tests/assets/`.

---

## Phase 1: Setup

- [x] T001 Confirm target Python's `tomllib` availability (`python -c "import sys; print(sys.version_info >= (3, 11))"`) — informational only, both code paths (tomllib vs. fallback) must work regardless of what this prints on the dev machine.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: The manifest parser and core discovery function every user story depends on.

- [x] T002 [P] Implement `src/catplotlib/assets/_toml_fallback.py`: a minimal parser covering only flat `[styles.<name>]` sections with `display_name` (quoted string) and `scale` (float) keys, per research.md. No general TOML feature support — document this narrow scope in the module docstring.
- [x] T003 Implement `StyleInfo` dataclass and `discover_styles(images_dir, manifest_path) -> dict[str, StyleInfo]` in `src/catplotlib/assets/registry.py`, using `tomllib` when `sys.version_info >= (3, 11)` else the T002 fallback; only includes styles with both a non-empty image directory and a manifest entry (depends on T002).
- [x] T004 [P] `tests/assets/test_registry.py`: tests for `discover_styles()` against temp fixture directories — style with both dir+manifest included; style with only one or the other excluded; empty image directory excluded; malformed manifest entry excluded without crashing other styles.

**Checkpoint**: `discover_styles()` is independently correct against fixtures, not yet wired to the real shipped `assets/` tree or to `set_style()`.

---

## Phase 3: User Story 1 - A single style decorates the whole figure (Priority: P1) 🎯 MVP

**Goal**: `set_style("chonk")` → every subsequently placed cat resolves to a "chonk" image.

**Independent Test**: `set_style("chonk")`, render a multi-cat figure, assert every resolved
image path is under `assets/images/chonk/`.

### Tests for User Story 1

- [x] T005 [P] [US1] `tests/assets/test_registry.py`: `available_styles()` against the real shipped tree returns exactly `{"classic", "derp", "chonk"}` (SC-004's precondition — confirms the M0-authored fixtures are intact).
- [x] T006 [US1] `tests/render/test_hook.py` (or a new `tests/render/test_artist.py`): `set_style("chonk")`, render a chaotic-density figure, resolve each cat's image path via the registry, assert all are under `assets/images/chonk/` (SC-001).

### Implementation for User Story 1

- [x] T007 [US1] Implement `available_styles()` in `src/catplotlib/assets/registry.py`, calling `discover_styles()` against the real package tree via `importlib.resources` (depends on T003).
- [x] T008 [US1] Change `render/artist._resolve_image` signature from `(style: str)` to `(placement: Placement)`; look up `placement.style` via `available_styles()`, pick the (currently single, per-style) image (depends on T007).
- [x] T009 [US1] Update `render/hook.py`'s call site to pass the full `placement`, not `placement.style`, to `_resolve_image` (depends on T008).

**Checkpoint**: Single-style selection fully functional end to end.

---

## Phase 4: User Story 2 - Mixing styles on one figure (Priority: P1)

**Goal**: `set_style(["classic","derp"])` or `set_style("mix")` → multiple styles appear on one
figure at typical densities.

**Independent Test**: `set_style("mix")`, seeded chaotic-density render, assert >1 distinct
style appears among resolved cat images across a handful of seeds.

### Tests for User Story 2

- [x] T010 [P] [US2] `tests/assets/test_registry.py`: `resolve_style_names("mix")` returns exactly the current `available_styles()` key set; `resolve_style_names(["classic","derp"])` returns that list unchanged; `resolve_style_names("not-real")` raises `ValueError`.
- [x] T011 [US2] `tests/render/test_artist.py`: across 20 seeds at chaotic density with `set_style("mix")`, more than one distinct style appears among resolved cat images in ≥90% of seeds (SC-002).

### Implementation for User Story 2

- [x] T012 [US2] Implement `resolve_style_names(selection)` in `src/catplotlib/assets/registry.py` per contracts/registry-api.md (depends on T007).
- [x] T013 [US2] Wire `api.set_style()` to call `resolve_style_names()` eagerly (fail-fast on bad names) and store the resolved flat list (or the raw selection, resolved lazily at each render call — pick whichever keeps `Config.style`'s existing type contract; resolve at render time in `render/hook.py._decorate` is simplest and matches M2's existing call site) (depends on T012).

**Checkpoint**: User Stories 1 AND 2 both pass independently.

---

## Phase 5: User Story 3 - Adding a style requires zero code changes (Priority: P2)

**Goal**: A fixture-registered style (temp directory + manifest entry, not the shipped tree) is
discoverable and selectable without touching any `.py` file.

**Independent Test**: In a test, build a temp `assets/images/<new>/` + temp `styles.toml`,
call `discover_styles()` against them directly, assert the new style appears.

### Tests for User Story 3

- [x] T014 [US3] `tests/assets/test_registry.py`: register a fixture style via `discover_styles(temp_images_dir, temp_manifest_path)` (not the shipped tree), assert it's discoverable and its `image_paths` are correct (SC-003). This is largely covered by T004's fixture tests — this task confirms the *exact* SC-003 framing (a style outside the shipped tree, zero production code touched) is explicitly asserted, not just implied.
- [x] T015 [US3] `tests/assets/test_registry.py`: the three shipped launch styles' placeholder PNGs are pairwise pixel-distinct (e.g. compare raw bytes or a coarse array-equality check) — SC-004.

### Implementation for User Story 3

- [x] T016 [US3] No new implementation expected — T003's `discover_styles()` already satisfies zero-code-change extension by construction (parametrized over `images_dir`/`manifest_path`). This task is verification only; fix if T014 reveals a gap (depends on T003, T014).

**Checkpoint**: All three user stories pass independently. Style system feature-complete.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [x] T017 [P] Implement deterministic image-pool indexing in `render/artist._resolve_image` for styles with multiple images: sort `image_paths` by filename, index via `hash((placement.x, placement.y, placement.size, placement.rotation)) % len(pool)` (research.md) (depends on T008).
- [x] T018 [P] `tests/render/test_artist.py`: reproducibility test — same seed, two full render+savefig calls, byte-identical output, using a temporarily-registered multi-image style fixture to actually exercise T017's pool-index logic (not just the single-image launch styles) (SC from quickstart.md).
- [x] T019 Apply `styles.toml`'s `scale` field as a multiplier on rendered cat size in `render/artist.py` (depends on T008).
- [x] T020 Run `quickstart.md`'s manual smoke script end-to-end and confirm all assertions pass.
- [x] T021 Regenerate the gallery (`python scripts/gallery.py`) and visually confirm style variety appears when `set_style("mix")` (manually verify, not an automated assertion — SC-004's "distinguishable" half of FR-008).
- [x] T022 Run `make check` and confirm all green.
- [x] T023 Update `PROGRESS.md`: mark M3 complete, note M4 (config/polish/packaging) is next and has no spec.

---

## Dependencies & Execution Order

- **Setup → Foundational**: blocks all user stories.
- **US1 (Phase 3)**: the MVP — single-style selection, wires the registry into the render path for the first time.
- **US2 (Phase 4)**: depends on US1's `available_styles()`/render wiring (T007) — adds mixing on top.
- **US3 (Phase 5)**: depends on Foundational's `discover_styles()` (T003) directly — verification-heavy, minimal new code, could in principle run in parallel with US1/US2 but is sequenced last since it's lowest priority (P2).
- **Polish (Phase 6)**: depends on US1/US2's render wiring (image-pool indexing needs `_resolve_image` to exist).

### Parallel Opportunities

- T002-T004 (Foundational) can run in parallel.
- T005/T010 (registry-only tests) can run in parallel with each other.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Setup + Foundational.
2. US1 → commit. Single-style selection works end to end.
3. **STOP and VALIDATE**: run US1's tests independently.

### Incremental Delivery

1. Foundational → US1 (MVP) → commit.
2. US2 (mixing) → commit.
3. US3 (zero-code-change verification) → commit.
4. Polish (deterministic pooling, scale application, gallery regen, `make check`, PROGRESS.md) → commit.

Each step's `make check` must be green before its commit (constitution #8).
