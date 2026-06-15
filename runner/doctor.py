"""doctor.py - environment and wiring self-check for Ultimate Best Seller Studio.

`ubss doctor` answers one question: *is this checkout actually ready to run?*
It is the first thing to run after cloning, and the fastest way to catch the
two most common setup mistakes — an uninitialized Better Humanizer submodule and
a stale Python.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from runner import humanband

REPO_ROOT = Path(__file__).resolve().parents[1]
MIN_PY = (3, 9)


@dataclass
class Check:
    name: str
    ok: bool
    detail: str
    fatal: bool = True  # a failing non-fatal check is a WARN, not a FAIL


def _py_version() -> Check:
    v = sys.version_info
    ok = (v.major, v.minor) >= MIN_PY
    return Check(
        "python",
        ok,
        f"{v.major}.{v.minor}.{v.micro} (need >= {MIN_PY[0]}.{MIN_PY[1]})",
    )


def _pipeline_loads() -> Check:
    try:
        from runner.filesystem import load_agent_registry, load_manifest

        phases = load_manifest()
        agents = load_agent_registry()
        return Check(
            "pipeline",
            len(phases) >= 1 and len(agents) >= 1,
            f"{len(phases)} phases, {len(agents)} agents loaded",
        )
    except Exception as exc:  # pragma: no cover - defensive
        return Check("pipeline", False, f"failed to load: {exc}")


def _humanizer() -> Check:
    base = humanband.humanizer_dir()
    if base is None:
        return Check(
            "better-humanizer",
            False,
            "submodule missing — run `git submodule update --init --recursive`",
        )
    return Check("better-humanizer", True, f"scorer at {base}/scripts/stylo.py")


def _bridge_skill() -> Check:
    skill = REPO_ROOT / "skills" / "humanizer-pro" / "SKILL.md"
    return Check(
        "humanizer-pro bridge",
        skill.is_file(),
        str(skill.relative_to(REPO_ROOT)) if skill.is_file() else "bridge skill missing",
        fatal=False,
    )


def _project(path: Optional[Path]) -> Optional[Check]:
    if path is None:
        return None
    from runner.filesystem import validate_project

    result = validate_project(path)
    ok = bool(result["ok"])
    detail = "all required files present" if ok else "missing: " + ", ".join(result["missing"])
    return Check(f"project {path}", ok, detail, fatal=False)


def run_checks(project: Optional[Path] = None) -> List[Check]:
    checks = [_py_version(), _pipeline_loads(), _humanizer(), _bridge_skill()]
    project_check = _project(project)
    if project_check is not None:
        checks.append(project_check)
    return checks


def render(checks: List[Check]) -> str:
    lines = []
    for c in checks:
        if c.ok:
            mark = "OK  "
        else:
            mark = "FAIL" if c.fatal else "WARN"
        lines.append(f"[{mark}] {c.name}: {c.detail}")
    return "\n".join(lines)


def has_fatal_failure(checks: List[Check]) -> bool:
    return any((not c.ok) and c.fatal for c in checks)
