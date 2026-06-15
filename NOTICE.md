# NOTICE

**Ultimate Best Seller Studio** is a fork and substantial extension of
**best-seller-studio** by Felipe Lobo.

- Upstream project: <https://github.com/felipelobomotta-blip/best-seller-studio>
- Upstream author: Felipe Lobo (<https://github.com/felipelobomotta-blip>)
- Upstream license: MIT (see `LICENSE`, original copyright retained)

The upstream agents, skills, knowledge corpora, prompts, examples, brand assets, and
the Python runner are the work of the upstream author and are used here under the MIT
License. The original copyright notice is preserved in `LICENSE`.

## Changes in this fork

- Replaced the rule-based `humanizer` skill with **Better Humanizer** (`humanizer-pro`),
  integrated as a git submodule (`external/better-humanizer`) — a separate project, the
  single source of truth, never copied in.
  - Better Humanizer: <https://github.com/jodyjdc/better-humanizer>
- Added a measured **human-band gate** (`runner/humanband.py`, `ubss humanize-score`)
  that scores manuscripts against the real human distribution for a register.
- Hardened the runner: `pyproject.toml` packaging, `ubss` console entry point, a
  `doctor` self-check, `--json` outputs, and an expanded test suite.
- Added GitHub Actions CI (the upstream had none).
- Rebranded the product layer to "Ultimate Best Seller Studio" and refreshed the
  README (EN/IT/PT), landing page, and installers.

Modifications in this fork are © 2026 Jody Cecchetto, released under the same MIT License.

Dated launch and marketing documents under `docs/` (Reddit kits, social campaigns,
distribution kits) are inherited from the upstream launch and describe the upstream
project's history; they are kept for provenance, not re-authored.
