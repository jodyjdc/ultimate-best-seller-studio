# Better Humanizer integration

Ultimate Best Seller Studio replaces the original rule-based `humanizer` skill with
the **Better Humanizer** (`humanizer-pro`) — a measured, register-aware rewriter that
scores prose against the *real human distribution* instead of trusting a checklist.

This document is the contract: how the two projects are wired, why it was done this
way, and how to act on a result.

## The link, not a copy

Better Humanizer is maintained as its own project and pulled in here as a
**git submodule**, so it is never duplicated and never drifts out of sync:

- Upstream (single source of truth): <https://github.com/jodyjdc/better-humanizer>
- Here: `external/better-humanizer` (version-pinned to a commit)

```bash
git submodule update --init --recursive   # first checkout
git submodule update --remote             # later: bump to upstream latest
```

Everything in `external/better-humanizer/` is upstream's. The seam on this side is
three thin pieces:

| Piece | What it is |
|---|---|
| `skills/humanizer-pro/SKILL.md` | a bridge skill that points agents at the real tool |
| `runner/humanband.py` | a subprocess wrapper around `scripts/stylo.py` |
| `ubss humanize-score` | a CLI command that gates a manuscript on human-likeness |

The scorer is invoked as a **subprocess**, never imported, so the two codebases stay
fully decoupled (the submodule loads its corpora relative to its own location).

## The measured human-band gate

The original pipeline gated chapters on the **Genesis Score** (a qualitative,
agent-judged 7–10 dimension rubric) and a 20-pattern anti-AI scan. Better Humanizer
adds a third, *quantitative* gate that nothing in the original pipeline had: a
reproducible stylometric distance from the human band for the register.

```bash
ubss humanize-score <project>                 # score every chapter, write a report
ubss humanize-score <project> --gate          # exit 3 if any chapter is flagged
ubss humanize-score <project> --json          # machine-readable
ubss humanize-score chapter-03.md --register literary
```

It writes `evaluations/human-band/REPORT.md`:

| Chapter | Distance | Outlier | Verdict | Notes |
|---|---|---|---|---|
| `chapter-01.md` | 0.41 | no | ✅ pass | in band |
| `chapter-02.md` | 0.92 | no | ⚠️ flag | distance exceeds ceiling; out-of-band: sentence_length_cv |

- **Distance** — composite stylometric distance from the human reference band. Lower
  is more human. Combines sentence-length burstiness, lexical diversity, a
  function-word fingerprint, punctuation rates, AI-tell density, and document-level
  discourse structure.
- **Outlier** — a hard veto: some feature sits more than three bands outside the human
  range. An outlier always flags, regardless of distance.
- **Self-tells** — over-correction *below* a human floor (zero em dashes, flat rhythm,
  zero contractions). Laundering a chapter flat is itself a tell, and it is surfaced.

## Registers

"Human" is register-specific. For a novel studio the default is **`literary`**, which
expects high sentence-length burstiness and tolerates far more em dashes than casual
prose. Nonfiction projects can pass another of the seven shipped registers:

`literary` · `journalism` · `business` · `scientific` · `technical-docs` ·
`social-media` · `spontaneous`

```bash
ubss humanize-score <project> --register journalism      # e.g. a reported nonfiction book
```

## Acting on a flag

A flag is a **measured signal to inspect, not an automatic reject**:

1. Run the Better Humanizer loop on the flagged chapter at the same register —
   `/humanizer-pro` in Claude Code, or open `external/better-humanizer/` in Codex.
   It generates candidate rewrites, scores each, vetoes any that lose meaning or fall
   outside the human band, and keeps the best.
2. Re-run `ubss humanize-score`. The distance should drop and the self-tells clear.

## Honest calibration caveat

The distance **ceiling** (`--max-distance`, default `0.75`) is a tunable editorial
heuristic, not a certified AI-detector score, and defeating commercial detectors is an
explicit non-goal of Better Humanizer. The numbers are *reproducible*; the threshold is
a judgment call. Treat the gate as a high-signal prompt to look closer, in concert with
the Genesis Score and a human read — never as the sole arbiter of quality.

## CI note

The `external/better-humanizer` submodule is private, so CI does not check it out (the
default `GITHUB_TOKEN` cannot clone a different private repo). The test suite is
designed to **skip** the end-to-end scorer tests when the submodule is absent and to
fully exercise the pure verdict/aggregation logic with synthetic inputs. To run the
integration tests in CI, add a PAT with read access to the submodule and enable
`submodules: recursive` in the checkout step.
