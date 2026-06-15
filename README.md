<div align="center">

# Ultimate Best Seller Studio

**Turn any idea into a publication-ready book — and prove the prose is human, not just hope it.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)
[![Claude Code](https://img.shields.io/badge/Runs%20on-Claude%20Code%20%2B%20Codex-blueviolet?style=flat-square)](https://claude.ai/code)
[![Human-Band Gate](https://img.shields.io/badge/Human--Band%20Gate-measured-brightgreen?style=flat-square)](docs/humanizer-pro-integration.md)
[![Zero runtime deps](https://img.shields.io/badge/runtime-stdlib%20only-success?style=flat-square)](pyproject.toml)
[![Fork of](https://img.shields.io/badge/fork%20of-best--seller--studio-lightgrey?style=flat-square)](https://github.com/felipelobomotta-blip/best-seller-studio)

*Languages: English · [Italiano](README.it.md) · [Português](README.pt-BR.md)*

</div>

---

You have an idea. Type it in. Eight AI agents research the genre, forge a premise with a
structural-irony engine, write every chapter, score each one independently, revise
anything below the gate, and package the result for publication.

This is a fork of [**best-seller-studio**](https://github.com/felipelobomotta-blip/best-seller-studio)
by Felipe Lobo (MIT), with one big idea added and the engine sharpened around it:

> **A book doesn't just have to *score* well — its prose has to sit inside the real
> human distribution, and now that's measured, not vibed.**

That measurement comes from **[Better Humanizer](https://github.com/jodyjdc/better-humanizer)**,
linked here as a single source of truth (a git submodule) and wired into the pipeline as a
new quantitative gate.

---

## What's new vs best-seller-studio

| | best-seller-studio | **Ultimate Best Seller Studio** |
|---|---|---|
| De-AI pass | rule-based `humanizer` (static checklist) | **Better Humanizer** (`humanizer-pro`): measured, register-aware, anti-over-correction |
| Human-likeness | qualitative only | **measured human-band gate** — reproducible stylometric distance per chapter |
| Packaging | scripts, no install | `pyproject.toml` + `ubss` console command |
| Readiness check | — | `ubss doctor` self-check |
| CLI output | text | text **or `--json`** for every read command |
| CI | none | GitHub Actions (3.11–3.13) + ruff |
| Runtime deps | stdlib | stdlib (unchanged — still runs anywhere Python 3 runs) |

Everything the upstream did well is intact: the file-backed pipeline, the agents, the
Genesis Score, and the knowledge corpora.

---

## Quick start

**1. Get the code (with the Better Humanizer submodule):**

```bash
git clone --recurse-submodules https://github.com/jodyjdc/ultimate-best-seller-studio
cd ultimate-best-seller-studio
# already cloned without --recurse-submodules?
git submodule update --init --recursive
```

**2. Install the skills + agents into Claude Code (and the full Better Humanizer):**

```bash
./install.sh            # macOS / Linux   (install.ps1 on Windows)
```

**3. Check the checkout is ready:**

```bash
python3 -m runner.cli doctor
# [OK  ] python: 3.12.x
# [OK  ] pipeline: 7 phases, 15 agents loaded
# [OK  ] better-humanizer: scorer at external/better-humanizer/scripts/stylo.py
# [OK  ] humanizer-pro bridge: skills/humanizer-pro/SKILL.md
```

**4. Give Claude Code an idea:**

```
I have an idea for a book: [your idea here]
```

The `book-orchestrator` agent runs the whole pipeline. You approve three times; the rest
is automatic.

> Prefer a console command? `pip install -e .` gives you `ubss` (alias: `book-genesis`).

---

## Compatibility

**Built for [Claude Code](https://claude.ai/code) first** — that's where it's most native:
skills load from `~/.claude/skills/`, agents from `~/.claude/agents/`, and you invoke them
with slash commands (`/book-genesis-codex`, `/humanizer-pro`).

**It also runs on any file-aware agent** — Codex, Antigravity, Kimi, and others — because the
product is a reproducible folder of markdown, manifests, and contracts, not a binary:

| Agent | How to run it |
|---|---|
| **Claude Code** | `./install.sh`, then `/book-genesis-codex` · `/humanizer-pro` (first-class) |
| **Codex** | open the repo, point Codex at [`AGENTS.md`](AGENTS.md) and ask it to run the pipeline |
| **Antigravity / Kimi / other** | open the repo and follow `AGENTS.md`; pass the `skills/book-genesis-codex/` folder |

What's **identical everywhere**: the markdown skills/prompts, the Python runner (`ubss`,
`doctor`, `humanize-score`), and the stylometric scoring — `stylo.py` returns the same
numbers on every platform, so the **human-band gate is byte-for-byte reproducible**. What
differs is only the model doing the writing (Claude vs. another), so the prose has a
different flavor while the loop, gates, and measurements stay the same.

Either way the deterministic scorer needs the submodule:
`git submodule update --init --recursive`.

---

## The pipeline (seven phases)

```
Intake → Foundation → Architecture → Drafting → Adversarial Audit → Score → Editorial
```

State is persisted to files (`PROJECT_STATE.yaml`, `ASSUMPTIONS.md`, `artifacts/`,
`manuscript/chapters/`, `evaluations/`, `delivery/`). One active phase prompt at a time.
Draft first, judge later, audit before scoring. Read the agents directly in `agents/` —
they're plain markdown.

---

## Two gates, not one

### Gate 1 — Genesis Score (qualitative)

A separate evaluator agent that never wrote the chapter scores it on a 7-dimension rubric
with a **floor principle** (the book is only as strong as its weakest major dimension),
plus a 20-pattern anti-AI scan and a 4-reader simulation. Chapters between the floor and
the target enter a surgical polish loop.

### Gate 2 — Human-Band Gate (measured) · *new*

```bash
ubss humanize-score <project>            # score every chapter, write a report
ubss humanize-score <project> --gate     # exit non-zero if any chapter is flagged
ubss humanize-score chapter-03.md --register literary --json
```

The [Better Humanizer](https://github.com/jodyjdc/better-humanizer) scorer rates each
chapter's **stylometric distance from the real human distribution** for the `literary`
register — sentence-length burstiness, lexical diversity, a function-word fingerprint,
punctuation rates, AI-tell density, and document-level discourse structure. It flags both
AI tells *and* over-correction (a chapter scrubbed flat is its own tell). Output lands in
`evaluations/human-band/REPORT.md`.

A flag is a measured signal to inspect, not an automatic reject: run `/humanizer-pro` on
the flagged chapter, then re-score. See **[docs/humanizer-pro-integration.md](docs/humanizer-pro-integration.md)**
for the full contract and the honest calibration caveat.

---

## Better Humanizer, linked not copied

The de-AI brain is its own project, pulled in as a version-pinned git submodule so it is
never maintained in two places:

```bash
git submodule update --remote   # bump to the latest Better Humanizer
```

- Upstream: <https://github.com/jodyjdc/better-humanizer>
- Here: `external/better-humanizer/` + the thin seam (`skills/humanizer-pro/`,
  `runner/humanband.py`, `ubss humanize-score`).

It runs on Claude Code (`/humanizer-pro`) and Codex (via its `AGENTS.md`) with an
identical, deterministic Python scorer either way.

---

## The runner CLI

```
ubss init <path> --idea "..."     scaffold a project tree
ubss status <path> [--json]       project status
ubss validate <path> [--json]     check required files
ubss prepare-phase <path>         write the active phase packet
ubss advance-phase <path>         advance once outputs exist
ubss prepare-agent-packet <path> <agent>
ubss prepare-swarm <path>         scaffold a reader-swarm run
ubss demo <path>                  deterministic mechanical demo
ubss doctor [<path>]              readiness self-check
ubss humanize-score <path>        measured human-band gate
```

Standard library only — no runtime dependencies. Tests: `make test` (or
`python3 -m pytest`).

---

## Cost & requirements

- [Claude Code](https://claude.ai/code) (OAuth, no API key) or Codex / any file-aware agent.
- Python 3.9+ for the runner.
- ~$20–30 for a full 20-chapter book on Claude Sonnet 4.6; ~30 min unattended per book.

---

## Honest caveats

- **Not a literal bestseller guarantee.** Cover, marketing, timing, and luck are outside
  the manuscript. The gates attack the word-of-mouth mechanism — the lever we control.
- **The Genesis Score is an internally-calibrated ruler**, not a certified external measure.
- **The human-band distance ceiling is a tunable editorial heuristic**, not an AI-detector
  score; defeating commercial detectors is an explicit non-goal. The numbers are
  reproducible; the threshold is a judgment call. Use it with — not instead of — a human read.

---

## Credits & license

MIT licensed. Forked from [**best-seller-studio**](https://github.com/felipelobomotta-blip/best-seller-studio)
by [Felipe Lobo](https://github.com/felipelobomotta-blip); original copyright retained in
`LICENSE`, full attribution in [`NOTICE.md`](NOTICE.md). Better Humanizer integration and
the upgrades above © 2026 Jody Cecchetto.
