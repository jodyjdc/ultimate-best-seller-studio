"""humanband.py - the measured human-band gate.

Bridges Ultimate Best Seller Studio to the *Better Humanizer* (`humanizer-pro`)
stylometric scorer, which lives in the `external/better-humanizer` git submodule
(single source of truth — never copied in). Given a chapter or a whole manuscript,
it runs that scorer and reports how close the prose sits to the *real human
distribution* for a register, plus the over-correction self-tells that mark
machine-laundered text.

Design choices:
- The scorer is invoked as a **subprocess**, never imported. The submodule loads
  its corpora relative to its own location, and a subprocess keeps the two
  codebases fully decoupled (different deps, different Python expectations are
  both fine). Everything here is standard library.
- No magic cutoff is hidden. `verdict()` exposes the raw distance, the outlier
  veto, and the exact out-of-band features so a human (or an agent) sees *why*,
  not just pass/fail. `max_distance` is a documented, tunable heuristic.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parents[1]

# Where the Better Humanizer submodule is expected. Overridable so a user who
# installed humanizer-pro elsewhere (e.g. ~/.claude/skills/humanizer-pro) can
# point at it without a submodule checkout.
DEFAULT_SUBMODULE = REPO_ROOT / "external" / "better-humanizer"
ENV_OVERRIDE = "UBSS_HUMANIZER_DIR"

# Heuristic default ceiling on the composite stylometric distance. Lower = closer
# to the human band. Calibrated loosely against humanizer-pro's own eval band:
# comfortably-human literary prose lands well under this; flat, tell-dense AI
# prose lands above it. It is deliberately lenient (this is a flag, not a
# silent reject) and fully tunable per project.
DEFAULT_MAX_DISTANCE = 0.75

# Default register for a novel studio. Fiction = literary; nonfiction projects
# can pass --register journalism|business|technical-docs|scientific|social-media.
DEFAULT_REGISTER = "literary"


class HumanizerUnavailable(RuntimeError):
    """Raised when the Better Humanizer scorer cannot be located."""


@dataclass
class BandScore:
    """One scored unit (a chapter file or a single text)."""

    name: str
    register: str
    distance: float
    outlier: bool
    self_tells: List[str]
    out_of_band: List[str]
    calibrated: bool
    passed: bool
    reasons: List[str] = field(default_factory=list)
    raw: Dict = field(default_factory=dict)

    def as_dict(self) -> Dict:
        return {
            "name": self.name,
            "register": self.register,
            "distance": self.distance,
            "outlier": self.outlier,
            "self_tells": self.self_tells,
            "out_of_band": self.out_of_band,
            "calibrated": self.calibrated,
            "passed": self.passed,
            "reasons": self.reasons,
        }


def humanizer_dir() -> Optional[Path]:
    """Resolve the Better Humanizer root, or None if it is not present.

    If ``UBSS_HUMANIZER_DIR`` is set it is authoritative: that path is the scorer
    location, full stop, and a wrong value surfaces as a clear error rather than
    silently falling back to the submodule (which would mask the misconfiguration).
    With no override, the bundled ``external/better-humanizer`` submodule is used.
    """
    override = os.environ.get(ENV_OVERRIDE)
    base = Path(override) if override else DEFAULT_SUBMODULE
    if (base / "scripts" / "stylo.py").is_file():
        return base
    return None


def require_humanizer() -> Path:
    base = humanizer_dir()
    if base is None:
        raise HumanizerUnavailable(
            "Better Humanizer scorer not found. Initialize the submodule with\n"
            "    git submodule update --init --recursive\n"
            f"or set {ENV_OVERRIDE} to a humanizer-pro checkout containing scripts/stylo.py."
        )
    return base


def score_file(
    path: Path,
    *,
    register: str = DEFAULT_REGISTER,
    expertise: Optional[str] = None,
    persona: Optional[str] = None,
    max_distance: float = DEFAULT_MAX_DISTANCE,
    timeout: int = 120,
) -> BandScore:
    """Run the stylometric scorer on a single UTF-8 text file."""
    base = require_humanizer()
    stylo = base / "scripts" / "stylo.py"
    cmd = [sys.executable, str(stylo), str(path), "--register", register]
    if expertise:
        cmd += ["--expertise", expertise]
    if persona:
        cmd += ["--persona", persona]

    proc = subprocess.run(
        cmd, capture_output=True, text=True, timeout=timeout, check=False
    )
    if proc.returncode != 0:
        raise HumanizerUnavailable(
            f"scorer failed for {path.name} (exit {proc.returncode}): "
            f"{proc.stderr.strip() or proc.stdout.strip()}"
        )
    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:  # pragma: no cover - defensive
        raise HumanizerUnavailable(
            f"scorer returned non-JSON output for {path.name}: {exc}"
        ) from exc

    return verdict(path.name, data, max_distance=max_distance)


def verdict(name: str, data: Dict, *, max_distance: float = DEFAULT_MAX_DISTANCE) -> BandScore:
    """Turn a raw stylo.py result into a transparent pass/flag verdict.

    A unit PASSES when it is not a hard stylometric outlier and its composite
    distance is within `max_distance`. Self-tells (over-correction below a human
    floor) and individual out-of-band features are surfaced as reasons even when
    they do not by themselves fail the unit, so the writer sees the full picture.
    """
    distance = float(data.get("stylo_distance", 0.0))
    outlier = bool(data.get("stylo_outlier", False))
    self_tells = list(data.get("self_tell_flags", []))
    features = data.get("features", {})
    out_of_band = [
        fname
        for fname, f in features.items()
        if isinstance(f, dict) and f.get("status") in {"above", "below"}
    ]

    reasons: List[str] = []
    if outlier:
        reasons.append("hard stylometric outlier (a feature is >3 bands outside human range)")
    if distance > max_distance:
        reasons.append(f"distance {distance:.3f} exceeds ceiling {max_distance:.2f}")
    if self_tells:
        reasons.append("over-correction self-tell(s): " + ", ".join(self_tells))
    if out_of_band:
        reasons.append("out-of-band: " + ", ".join(sorted(out_of_band)))

    passed = (not outlier) and (distance <= max_distance)
    return BandScore(
        name=name,
        register=str(data.get("register", "")),
        distance=round(distance, 4),
        outlier=outlier,
        self_tells=self_tells,
        out_of_band=sorted(out_of_band),
        calibrated=bool(data.get("calibrated", False)),
        passed=passed,
        reasons=reasons,
        raw=data,
    )


def _chapter_files(project: Path) -> List[Path]:
    chapters = project / "manuscript" / "chapters"
    if not chapters.is_dir():
        return []
    return sorted(p for p in chapters.glob("*.md") if p.is_file())


def score_manuscript(
    project: Path,
    *,
    register: str = DEFAULT_REGISTER,
    expertise: Optional[str] = None,
    persona: Optional[str] = None,
    max_distance: float = DEFAULT_MAX_DISTANCE,
    write_report: bool = True,
) -> Dict:
    """Score every chapter in a project and (optionally) write a report.

    Returns a summary dict with per-chapter scores and an aggregate verdict.
    """
    chapters = _chapter_files(project)
    scores: List[BandScore] = [
        score_file(
            ch,
            register=register,
            expertise=expertise,
            persona=persona,
            max_distance=max_distance,
        )
        for ch in chapters
    ]

    passed = [s for s in scores if s.passed]
    flagged = [s for s in scores if not s.passed]
    distances = [s.distance for s in scores]
    summary = {
        "register": register,
        "max_distance": max_distance,
        "chapters_scored": len(scores),
        "chapters_passed": len(passed),
        "chapters_flagged": len(flagged),
        "mean_distance": round(sum(distances) / len(distances), 4) if distances else None,
        "worst_distance": round(max(distances), 4) if distances else None,
        "all_passed": bool(scores) and not flagged,
        "scores": [s.as_dict() for s in scores],
    }

    if write_report:
        report_dir = project / "evaluations" / "human-band"
        report_dir.mkdir(parents=True, exist_ok=True)
        (report_dir / "REPORT.md").write_text(
            _render_report(summary, scores), encoding="utf-8"
        )
        summary["report"] = str((report_dir / "REPORT.md").relative_to(project))

    return summary


def _render_report(summary: Dict, scores: List[BandScore]) -> str:
    lines = [
        "# Human-Band Report",
        "",
        "Measured by the **Better Humanizer** (`humanizer-pro`) stylometric scorer.",
        "Lower distance = closer to the real human distribution for the register.",
        "",
        f"- Register: `{summary['register']}`",
        f"- Distance ceiling: `{summary['max_distance']}`",
        f"- Chapters scored: {summary['chapters_scored']}",
        f"- Passed: {summary['chapters_passed']}  ·  Flagged: {summary['chapters_flagged']}",
        f"- Mean distance: {summary['mean_distance']}  ·  Worst: {summary['worst_distance']}",
        "",
        "| Chapter | Distance | Outlier | Verdict | Notes |",
        "|---|---|---|---|---|",
    ]
    for s in scores:
        verdict_txt = "✅ pass" if s.passed else "⚠️ flag"
        notes = "; ".join(s.reasons) if s.reasons else "in band"
        outlier = "yes" if s.outlier else "no"
        lines.append(
            f"| `{s.name}` | {s.distance:.3f} | {outlier} | {verdict_txt} | {notes} |"
        )
    if not scores:
        lines.append("| _no chapters found_ | — | — | — | write chapters first |")

    lines += [
        "",
        "## How to act on a flag",
        "",
        "A flag is not an automatic reject — it is a measured signal to inspect. "
        "Run `/humanizer-pro` (Claude Code) or the Better Humanizer loop (Codex) on the "
        "flagged chapter with the same register. It will generate candidate rewrites, "
        "veto any that lose meaning or fall outside the human band, and keep the best. "
        "Re-score afterward; the distance should drop and the self-tells clear.",
        "",
        "> Calibration note: the distance ceiling is a tunable heuristic, not a certified "
        "detector score. The numbers above are reproducible; the threshold is editorial.",
        "",
    ]
    return "\n".join(lines)
