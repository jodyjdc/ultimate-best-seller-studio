# Ultimate Best Seller Studio — design

Date: 2026-06-15
Status: implemented
Author: autonomous build (decisions made on the user's standing delegation to work
overnight "in modo del tutto autonomo … con testa")

## Goal

Fork `felipelobomotta-blip/best-seller-studio` (MIT) into a new private repo
`jodyjdc/ultimate-best-seller-studio`, integrate the user's **Better Humanizer**
(`jodyjdc/better-humanizer`) in place of the original rule-based humanizer by *linking*
to it (single source of truth), and make substantive, defensible improvements across
the engine, packaging, CI, brand, and docs — without vandalizing the upstream author's
good craft work.

## What the source actually is

Not a web app: a Claude Code / Codex **skills + agents book-production pipeline**.
- `agents/`, `skills/` — markdown agent and skill definitions (the product's core value).
- `knowledge/` — bestseller pattern corpora.
- `runner/` — a small, dependency-free Python state machine (file-backed project tree,
  phase manifest, gates, agent packets, reader-swarm scaffolding). Engine, not app.
- `tests/` — 12 unittest cases over the runner.
- `web/landing.html`, `video-demo/` (Remotion), `install.sh/.ps1`, `docs/`, `examples/`.

## Decisions

1. **Better Humanizer = git submodule + thin seam.** Add `external/better-humanizer`
   as a submodule (version-pinned, never copied). Seam: a bridge skill
   (`skills/humanizer-pro/`), a subprocess wrapper (`runner/humanband.py`), and a CLI
   command (`ubss humanize-score`). The scorer is invoked as a subprocess, never
   imported, to keep the codebases decoupled. Rationale: the user asked to *link* so it
   is not maintained twice; a submodule is the git-native single-source-of-truth link.

2. **New capability — measured human-band gate.** The headline 1+1=3 of merging the two
   projects: gate each chapter on a reproducible stylometric distance from the human
   distribution (literary register), alongside the existing qualitative Genesis Score.
   This is genuinely new; the original had no quantitative human-likeness measure.

3. **Runner hardening, not rewrite.** Add `pyproject.toml` (packaging + `ubss` console
   entry point, `book-genesis` alias, ruff/pytest config), `doctor` (readiness
   self-check), `--json` outputs, `tests/__init__.py`, and new tests for the gate and
   doctor. Keep runtime **standard-library only**. The hand-rolled YAML parser is left
   intact: it is test-covered and only parses controlled internal files, so a rewrite is
   high-risk / low-reward.

4. **CI the source lacked.** GitHub Actions matrix (3.11–3.13) running the unittest suite
   and ruff. Submodule is private, so CI does not check it out; the suite skips the
   end-to-end scorer tests when the submodule is absent and fully tests the pure logic.

5. **Rebrand the product layer, keep internal slugs stable.** Repo, README (EN + IT +
   PT), landing page, banners, AGENTS.md intro, installer text → "Ultimate Best Seller
   Studio". Internal skill slugs (`book-bestseller-studio`) stay — referenced by code,
   tests, and ~dozens of cross-links. Engine codename "book-genesis" preserved.
   (Updated in 1.0.1: the `book-genesis-codex` slug WAS renamed → `book-genesis-core`,
   because "codex" on a Claude-first install is misleading; see CHANGELOG.)

6. **Attribution / MIT.** Preserve the original `LICENSE` copyright line verbatim, append
   the user's copyright for modifications, add a `NOTICE` crediting the upstream author
   and repo. Dated upstream launch/marketing docs under `docs/` are left as inherited
   history, not re-authored as the user's own.

## Out of scope (deliberate)

- Rewriting the 100+ craft/prose/marketing markdown files or the agent prompts wholesale.
- Turning the skills package into a SaaS/web app.
- Making `better-humanizer` public (the user's call).
- Rewriting the YAML parser (see decision 3).

## Verification

`python -m unittest` green (27 tests); `ubss doctor` clean; `ubss demo` runs to
completion; `ubss humanize-score` scores real prose via the submodule; landing page
renders in preview; CI green after push.
