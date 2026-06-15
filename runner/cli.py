from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from runner import doctor as doctor_mod  # noqa: E402
from runner import humanband
from runner.filesystem import (  # noqa: E402
    advance_phase,
    create_demo,
    load_state_summary,
    prepare_agent_packet,
    prepare_phase,
    prepare_swarm_run,
    scaffold_project,
    validate_project,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ubss",
        description="Ultimate Best Seller Studio runner — file-backed book pipeline "
        "with a measured human-band gate (Better Humanizer).",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Create a project tree")
    init_parser.add_argument("path")
    init_parser.add_argument("--idea", default="")
    init_parser.add_argument("--language", default="")
    init_parser.add_argument("--adapter", default="codex")
    init_parser.add_argument("--model", default="gpt-5.5")
    init_parser.add_argument("--force", action="store_true")

    status_parser = subparsers.add_parser("status", help="Print project status")
    status_parser.add_argument("path")
    status_parser.add_argument("--json", action="store_true", help="emit JSON")

    validate_parser = subparsers.add_parser("validate", help="Validate required project files")
    validate_parser.add_argument("path")
    validate_parser.add_argument("--json", action="store_true", help="emit JSON")

    prepare_parser = subparsers.add_parser("prepare-phase", help="Write work/current-phase.md")
    prepare_parser.add_argument("path")

    advance_parser = subparsers.add_parser("advance-phase", help="Advance after required outputs exist")
    advance_parser.add_argument("path")

    swarm_parser = subparsers.add_parser("prepare-swarm", help="Create a book-swarm run folder")
    swarm_parser.add_argument("path")
    swarm_parser.add_argument("--slug", default="reader-swarm")
    swarm_parser.add_argument("--mode", default="hybrid")

    agent_parser = subparsers.add_parser("prepare-agent-packet", help="Create a specialist agent packet")
    agent_parser.add_argument("path")
    agent_parser.add_argument("agent")

    demo_parser = subparsers.add_parser("demo", help="Create a deterministic mechanical demo")
    demo_parser.add_argument("path")
    demo_parser.add_argument("--adapter", default="codex")
    demo_parser.add_argument("--model", default="gpt-5.5")

    doctor_parser = subparsers.add_parser(
        "doctor", help="Check the checkout is ready (python, pipeline, Better Humanizer submodule)"
    )
    doctor_parser.add_argument("path", nargs="?", default=None, help="optional project to validate")

    hb_parser = subparsers.add_parser(
        "humanize-score",
        help="Score a chapter/manuscript against the human band via Better Humanizer",
    )
    hb_parser.add_argument("path", help="a text file, or a project dir (scores manuscript/chapters)")
    hb_parser.add_argument("--register", default=humanband.DEFAULT_REGISTER)
    hb_parser.add_argument("--expertise", choices=["novice", "practitioner", "expert"], default=None)
    hb_parser.add_argument("--persona", default=None, help="persona name defined in humanizer-pro")
    hb_parser.add_argument(
        "--max-distance", type=float, default=humanband.DEFAULT_MAX_DISTANCE,
        help="distance ceiling for a pass (heuristic, tunable)",
    )
    hb_parser.add_argument("--json", action="store_true", help="emit JSON")
    hb_parser.add_argument("--no-report", action="store_true", help="do not write evaluations/human-band/REPORT.md")
    hb_parser.add_argument(
        "--gate", action="store_true",
        help="exit non-zero if any unit is flagged (for CI / pipeline gating)",
    )

    return parser


def _cmd_humanize_score(args) -> int:
    target = Path(args.path)
    try:
        if target.is_dir():
            summary = humanband.score_manuscript(
                target,
                register=args.register,
                expertise=args.expertise,
                persona=args.persona,
                max_distance=args.max_distance,
                write_report=not args.no_report,
            )
            if args.json:
                print(json.dumps(summary, indent=2))
            else:
                print(
                    f"register={summary['register']} scored={summary['chapters_scored']} "
                    f"passed={summary['chapters_passed']} flagged={summary['chapters_flagged']} "
                    f"mean_distance={summary['mean_distance']} worst={summary['worst_distance']}"
                )
                if summary.get("report"):
                    print(f"report: {summary['report']}")
                for s in summary["scores"]:
                    if not s["passed"]:
                        print(f"  flag {s['name']}: {'; '.join(s['reasons'])}")
            all_passed = summary["all_passed"]
        else:
            score = humanband.score_file(
                target,
                register=args.register,
                expertise=args.expertise,
                persona=args.persona,
                max_distance=args.max_distance,
            )
            if args.json:
                print(json.dumps(score.as_dict(), indent=2))
            else:
                verdict = "pass" if score.passed else "flag"
                print(
                    f"{score.name}: {verdict} register={score.register} "
                    f"distance={score.distance} outlier={score.outlier}"
                )
                if score.reasons:
                    print("  " + "; ".join(score.reasons))
            all_passed = score.passed
    except humanband.HumanizerUnavailable as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if args.gate and not all_passed:
        return 3
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "doctor":
        project = Path(args.path) if args.path else None
        checks = doctor_mod.run_checks(project)
        print(doctor_mod.render(checks))
        return 1 if doctor_mod.has_fatal_failure(checks) else 0

    if args.command == "humanize-score":
        return _cmd_humanize_score(args)

    target = Path(args.path)

    if args.command == "init":
        scaffold_project(
            target,
            idea=args.idea,
            language=args.language,
            adapter=args.adapter,
            model_name=args.model,
            force=args.force,
        )
        print(f"Initialized project at {target}")
        return 0

    if args.command == "status":
        summary = load_state_summary(target)
        if getattr(args, "json", False):
            print(json.dumps(summary, indent=2))
        else:
            for key in ("title", "adapter", "model_name", "current_phase", "status"):
                print(f"{key}={summary[key]}")
        return 0

    if args.command == "validate":
        result = validate_project(target)
        if getattr(args, "json", False):
            print(json.dumps(result, indent=2))
            return 0 if result["ok"] else 1
        if not result["ok"]:
            print("Validation failed")
            for item in result["missing"]:
                print(item)
            return 1
        print("Validation ok")
        return 0

    if args.command == "prepare-phase":
        packet_path = prepare_phase(target)
        print(f"Prepared phase packet at {packet_path}")
        return 0

    if args.command == "advance-phase":
        result = advance_phase(target)
        if not result["ok"]:
            print("Advance failed")
            for item in result["pending"]:
                print(item)
            return 1
        print(f"Advanced to {result['next_phase']}")
        return 0

    if args.command == "prepare-swarm":
        run_dir = prepare_swarm_run(target, slug=args.slug, mode=args.mode)
        print(f"Prepared book-swarm run at {run_dir}")
        return 0

    if args.command == "prepare-agent-packet":
        packet_path = prepare_agent_packet(target, args.agent)
        print(f"Prepared agent packet at {packet_path}")
        return 0

    if args.command == "demo":
        create_demo(target, adapter=args.adapter, model_name=args.model)
        print(f"Created completed mechanical demo at {target}")
        return 0

    parser.error("Unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
