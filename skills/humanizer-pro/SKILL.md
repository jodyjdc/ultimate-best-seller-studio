---
name: humanizer-pro
description: |
  Measured, register-aware de-AI rewriter for manuscript prose. This is a BRIDGE
  to the standalone Better Humanizer project (single source of truth), not a copy
  of it. Use when a chapter reads synthetic, fails the anti-AI scan, or needs to
  sit inside the real human distribution for fiction (literary register). Replaces
  the old rule-based `humanizer`. Generates candidate rewrites, scores each with a
  hybrid stylometric + LLM-judge scorer against a human reference band (floor AND
  ceiling, so it never over-corrects into machine-laundered prose), vetoes any that
  lose meaning, keeps the best, and proves it with a number.
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
  - AskUserQuestion
---

# humanizer-pro (bridge)

This skill does **not** reimplement humanization. It points at the **Better
Humanizer** — a measured, self-improving rewriter that is maintained as its own
project so it never has to be kept in sync in two places.

- **Upstream (single source of truth):** <https://github.com/jodyjdc/better-humanizer>
- **In this repo:** the `external/better-humanizer` git submodule (version-pinned).
  Initialize it once with `git submodule update --init --recursive`.

When `install.sh` / `install.ps1` runs, it installs the *full* Better Humanizer
on top of this bridge, so in Claude Code `/humanizer-pro` is the complete tool —
scorer, corpora, judges, registers, and personas — not this pointer.

## Why it replaced the old `humanizer`

The previous `humanizer` skill was a static checklist of ~33 known AI "tells" from
Wikipedia's *Signs of AI writing*. Better Humanizer keeps that pattern knowledge
and adds the three things a checklist cannot do:

1. **Measurement, not vibes.** `scripts/stylo.py` (standard-library, no deps) rates
   every rewrite against a real human reference band: sentence-length burstiness,
   lexical diversity (MTLD), a function-word fingerprint, punctuation rates, tell
   counts, and document-level discourse structure.
2. **Register awareness.** "Human" is register-specific. Seven calibrated registers
   ship — for a novel studio the one that matters is **`literary`** (it tolerates
   ~13× the em dashes of casual prose, expects high burstiness, and so on).
3. **Anti-over-correction.** Every band has a floor *and* a ceiling. Scrubbing a
   chapter to zero em dashes, flat rhythm, or zero contractions is itself a tell,
   and it is penalized as a `self_tell`.

## How to use it in the book pipeline

Run it on a chapter (or a passage) after drafting, before scoring — the same slot
the old `humanizer` occupied in Phase 3 polish and the Phase 4/5 editorial passes.

**Claude Code**

```
/humanizer-pro
# then give it the chapter text (or path) and register: literary
```

**Codex / any file-aware agent** — open `external/better-humanizer/` and follow
`SKILL.md` (it routes through `AGENTS.md`). The loop is platform-agnostic; the
scoring is a deterministic Python subprocess, so the result is identical.

**Measured human-band gate (this repo's addition).** The runner wraps the scorer so
you can gate a whole manuscript on human-likeness, alongside the Genesis Score:

```bash
ubss humanize-score <project>            # scores manuscript/chapters, writes a report
ubss humanize-score <project> --gate     # exit non-zero if any chapter is flagged
ubss humanize-score chapter-03.md --register literary --json
```

A flag is a *measured signal to inspect*, not an automatic reject: re-run the
Better Humanizer loop on the flagged chapter, then re-score. The distance should
drop and the self-tells clear. See `docs/humanizer-pro-integration.md` for the
full contract and the honest calibration caveat.

## Rule

Do not paste humanization logic, lexicons, corpora, or scoring code into this repo.
If the technique needs to change, change it upstream in `jodyjdc/better-humanizer`
and bump the submodule pointer here (`git submodule update --remote`).
