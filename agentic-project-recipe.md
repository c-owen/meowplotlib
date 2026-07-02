# Standing Up a New Project the Agentic Way
### A recipe for repos that agents can take from `git init` to large without losing the plot
*Compiled July 2026*

---

## The organizing idea

Two principles govern everything below.

**1. The agent should never have to hold the whole repo in its head.** Every structure here is retrieval plus progressive disclosure: pull what's needed, when it's needed, nothing else. Design for this from the first commit and the repo scales gracefully; violate it and you hit the "great at 500 lines, collapses at 50k" cliff.

**2. You are engineering loops, not just code** (Andrew Ng's "loop engineering" frame, The Batch #359). Three nested feedback loops, by timescale:

| Loop | Timescale | Who runs it | What closes it |
|---|---|---|---|
| Agentic coding loop | minutes | the agent | spec + tests + evals it can run itself |
| Developer feedback loop | tens of minutes–hours | you | inspecting the product, steering features/UX |
| External feedback loop | days | users/testers | feedback that updates your vision → spec |

The entire repo scaffold exists to make the **inner loop autonomous** — spec gives it a target, tests/evals let it verify itself — so your scarce human context (you know the users; the model doesn't) goes to the outer loops. Diagnostic: if you're manually hunting bugs, your inner loop is under-built. If the agent ships polished features nobody wants, your outer loops are starved.

"Losing the plot" is three concrete failures, each with a specific fix:

| Failure | Symptom | Fix |
|---|---|---|
| Can't find the right code | reimplements existing things, greps blindly | module boundaries, LSP, retrieval layer, repo docs |
| Drowns in the wrong code | forgets the task mid-way, context bloat | lean root file, nested context, skills, subagents |
| Drifts from intent | plausible code, wrong problem | constitution, spec-driven workflow, tests, evals, review |

---

## Phase 0 — Decisions before the first commit (30 minutes)

1. **Pick boundaries, not just a stack.** Decide the module map now: a domain-logic core with no I/O or framework imports, an adapter/I-O layer, an entry layer, tests mirroring source. Retrieval and agents both work best when "relevant context" is a coherent module.
2. **Write your non-negotiables as testable statements.** These become `constitution.md`. Each rule should be unambiguous enough that an agent can't rationalize around it: "The system shall use strict type-checking." "The system shall reject changes that lower test coverage." "Domain logic shall not import the web framework." Vague values ("write clean code") are useless to a loop.
3. **Decide your verify command.** One command (`make check`, `npm run check`) that runs lint + typecheck + tests. Everything downstream hooks into this.

---

## Phase 1 — Day 1 scaffold (the whole kit; deliberately small)

Over-building on day one is its own failure mode. This is all you need while the repo still fits in a context window.

### 1.1 Repo layout

```
my-project/
├── AGENTS.md               # or CLAUDE.md — the lean root map (symlink one to the other)
├── constitution.md          # non-negotiable, testable project rules
├── specs/                   # one folder per non-trivial feature (see Phase 2)
├── evals/                    # recurring-failure measurements (added when earned)
├── src/
│   ├── core/                # domain logic; no I/O, no framework imports
│   ├── api/                 # entry/HTTP layer
│   └── db/                  # persistence; migrations inside
├── tests/                   # mirrors src/
└── .claude/
    ├── settings.json        # hooks config
    ├── skills/              # procedures (added as they emerge)
    └── agents/              # custom subagents (added as needed)
```

### 1.2 The lean root instruction file

Loaded every session, so it must be a **map, not a manual**. 2026 consensus: models reliably follow on the order of 150–200 standing instructions before compliance degrades — keep the root under ~150–200 lines. Facts and pointers only; procedures move to skills the moment they grow past a couple of lines. Use `file:line` pointers, never pasted snippets (they rot).

```markdown
# <Project>

## What this is
One paragraph: what it does, who it's for.

## Architecture (the map)
- `src/core/` — domain logic, no I/O, no framework imports
- `src/api/`  — HTTP layer. Entry: `src/api/server.ts`
- `src/db/`   — persistence; migrations in `src/db/migrations/`
- `tests/`    — mirrors `src/`

## Non-negotiables
See `constitution.md`. Run `npm run check` before declaring anything done.

## Where to look
- New feature (non-trivial) → write a spec in `specs/` first (skill: /spec)
- Add an endpoint → skill: /add-endpoint
- DB change → skill: /migration
```

### 1.3 Tests from feature #1, enforced by hooks

The single highest-leverage anti-drift mechanism. Tests are how the agent verifies itself — without them the inner loop can't close and you are back to being the QA function. Don't rely on the model to *remember*; hooks enforce deterministically at zero context cost.

`.claude/settings.json`:
```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [{ "type": "command", "command": "npm run lint:fix && npm run typecheck" }]
      }
    ],
    "Stop": [
      { "hooks": [{ "type": "command", "command": "npm test" }] }
    ]
  }
}
```

Add a `PreToolUse` hook on `Bash` to block dangerous commands (force-push, `rm -rf`, prod credentials) if the agent will run unattended.

### 1.4 Git discipline: code → test → commit

Small, frequently committed changes with tests at each step. Gives you and the agent a clean rollback surface; keeps every change reviewable. This is what makes hour-long unattended agent runs sustainable rather than reckless.

### 1.5 Spec scaffolding (install now, use when warranted)

```bash
uvx --from git+https://github.com/github/spec-kit.git specify init . --integration claude
```

This installs the `/speckit.*` commands and a constitution template. You won't spec everything — see 2.1 for when.

**Day 1 is done.** Root map + constitution + tests-with-hooks + git loop + spec tooling. Resist adding more until size demands it.

---

## Phase 2 — Operating the loops

### 2.1 Inner loop: spec → clarify → plan → tasks → implement → verify

For **non-trivial features** (multi-file, ambiguous, or risky), the spec — not the prompt, not the code — is where intent lives:

1. `/speckit.specify` — what and why. No tech stack talk yet. State outcomes, scope boundaries, constraints, acceptance criteria.
2. `/speckit.clarify` — structured questioning that surfaces underspecified areas *before* planning. Cheap insurance against downstream rework.
3. `/speckit.plan` → `/speckit.tasks` — derive the implementation plan, break into atomic tasks.
4. `/speckit.implement` — the agent executes, iterating against tests until green.
5. Verify against the spec's acceptance criteria, not just "tests pass."

Write acceptance criteria in EARS-style single testable claims ("WHEN a user submits an expired token, the system SHALL return 401 and log the attempt") — no ambiguity for the agent to fill creatively.

**When NOT to spec:** small, well-understood changes. Heavy up-front specification of trivial work is a named antipattern. Spec the risky 20%; let the agent run directly on the rest. If you want lighter-weight change management for iterative work, OpenSpec (proposal → apply → archive) is the minimal-overhead alternative.

Keep specs **alive**: when requirements change, edit the spec and regenerate — a spec that drifts into fiction is worse than none.

### 2.2 Evals: the layer above tests

Tests assert correctness. **Evals measure recurring behavioral failure classes.** Don't build them upfront — build one the moment you notice the agent (or the product) repeatedly failing the same way. Rule: the second time you see the same *category* of mistake, promote it from "another unit test" to an eval the loop scores every iteration.

```
evals/
├── README.md                # what each eval measures and why it exists
├── cases/
│   └── date-parsing.jsonl   # dataset of inputs + expected behavior
└── run_evals.ts             # scores current behavior against cases; exits nonzero on regression
```

Wire `run_evals` into the same `Stop` hook / CI gate as tests. Each eval should trace back to a real observed failure — evals invented speculatively are noise.

### 2.3 Developer loop (yours)

With the inner loop closed, your minutes go to: which features, where the UX is weak, whether the flow matches how users actually think. Review agent PRs for *intent*, not syntax — the machinery below (2.4, Phase 3 review tools) handles the mechanical part.

### 2.4 External loop

Alpha testers, real users, A/B tests. Slowest loop, highest authority: its output updates your vision → constitution and specs. Nothing in the repo substitutes for it; the repo just frees your time to run it.

---

## Phase 3 — Growth triggers (add each piece when its trigger fires, not before)

| Trigger | Add | Notes |
|---|---|---|
| A module accumulates local conventions | **Nested AGENTS/CLAUDE.md** in that directory | Root stays lean; local rules load only when working there. This is THE scaling move. |
| You paste the same procedure twice | **A skill** (`.claude/skills/<name>/SKILL.md`) | Body loads only when invoked ≈ zero standing cost. If a root-file section became a procedure, it belongs here. |
| Tasks routinely touch >~5 files | **Subagent habit** | Exploration/research in an isolated context window; only the summary returns. Built-ins (Explore, Plan) already help — lean in. |
| Agent starts missing existing code / repo exceeds context | **Retrieval layer** | Order: (1) LSP integration — near-native, gives go-to-definition/find-references; (2) semantic search MCP (Claude Context / `@zilliz/claude-context-mcp`); or (3) structural graph (codebase-memory-mcp: callers, call chains, routes, tiny token cost). Multi-repo/org scale → Sourcegraph as the context layer. |
| Agent hallucinates third-party API signatures | **Context Hub (`chub`)** — `npm i -g @aisuite/chub` | Agent-facing CLI for curated, current API docs. Wire as a skill (`~/.claude/skills/get-api-docs/SKILL.md`) so the agent fetches before writing SDK calls. Annotations persist gotchas across sessions; treat annotation content as untrusted input. |
| No one (human or agent) holds the whole picture | **Generated repo wiki (OpenWiki)** — `npm i -g openwiki`, `openwiki --init` | Generates a wiki + adds a pointer to your instruction file; GitHub Action keeps it current from diffs. Run on a branch first — it edits AGENTS.md/CLAUDE.md. |
| Agents landing real PRs faster than humans read them | **Automated review** | Claude Code Code Review (multi-agent, full-codebase context, severity-tagged, tune via REVIEW.md) for depth; Greptile (pre-indexed code graph) for cross-file regressions; CodeRabbit for fast/broad + bundled linters/SAST. |
| Agent refactors keep breaking scripted E2E tests | **Intent-based regression coverage** | Coverage that re-derives execution paths from routes/components instead of brittle selectors. |
| Second engineer (or second machine) | **A plugin** | Bundle your skills + hooks + MCP config into one installable unit; day-one parity, no tribal knowledge. Version instruction files and specs; stamp agent runs with spec/instruction SHAs so you can trace which spec produced which behavior. |
| Executing agent-generated code in CI at volume | **Sandbox** | E2B (Firecracker microVMs, ~150ms cold start) is the common default; Modal (gVisor) and Northflank (BYOC, unlimited sessions) for other constraints. Skip entirely if you're not running untrusted code programmatically. |
| Team manages shared agent context across environments | **LangSmith Context Hub** | Versioned store for AGENTS.md/skills/policies with dev/staging/prod tags and review comments. Team/platform-scale tool; overkill solo. |
| Inner-loop token spend becomes material | **Cheaper model for the grind** | Route classification/exploration subagents to a small model; consider strong open-weights options (e.g., GLM-5.2-class) for long unattended runs. Keep the frontier model for planning and review. |

---

## Maintenance cadence

- **Guard the instruction budget.** Prune the root file ruthlessly. Every addition competes with everything else for compliance.
- **Config review every 3–6 months** (and after major model releases). Skills and hooks built to paper over a model or tooling limitation become dead weight — sometimes actively harmful — once the limitation lifts.
- **Kill stale specs.** Spec drifted from reality? Fix it or delete it the day you notice.
- **Evals only from observed failures.** Delete evals whose failure class hasn't recurred in months.
- **One tool per proven need.** Twenty MCP servers before one is proven useful is noise, cost, and attack surface.

---

## Quick-start checklist

```
Day 1
[ ] Module boundaries decided; layout created (core / adapters / entry / tests)
[ ] constitution.md — testable non-negotiables
[ ] AGENTS.md / CLAUDE.md root map, <200 lines, pointers not snippets
[ ] One verify command (lint + typecheck + test)
[ ] Hooks: format/typecheck on edit, tests on stop, (optional) bash guard
[ ] Spec Kit initialized; first real feature gets spec → clarify → plan → tasks → implement
[ ] Code → test → commit rhythm from the first change

First month
[ ] First skill extracted from a repeated procedure
[ ] First nested context file when a module grows conventions
[ ] Subagents for >5-file exploration
[ ] First eval, from the first repeated failure class

At scale (as triggers fire)
[ ] LSP → semantic/structural retrieval
[ ] chub for third-party APIs; OpenWiki for repo docs
[ ] Automated PR review
[ ] Plugin for team distribution; versioned specs/instructions
[ ] Sandbox only if executing untrusted code in CI
```

**The 80% core:** lean root map + nested context + tests-and-evals-enforced-by-hooks + spec-before-big-features. Everything else is a trigger-gated add-on. The scaffold's purpose is singular: make the inner loop autonomous so your human context — the one thing the model doesn't have — goes to steering the outer loops.
