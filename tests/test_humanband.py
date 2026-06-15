"""Tests for the human-band gate (runner/humanband.py).

The pure verdict/aggregation logic is tested with synthetic scorer output, so it
runs everywhere — including CI, where the private Better Humanizer submodule is
absent. The end-to-end scorer test is skipped unless a scorer is actually present.
"""
import os
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from runner import humanband  # type: ignore  # noqa: E402


def _raw(distance, outlier=False, self_tells=None, features=None, register="literary"):
    return {
        "register": register,
        "calibrated": True,
        "stylo_distance": distance,
        "stylo_outlier": outlier,
        "self_tell_flags": self_tells or [],
        "features": features or {},
    }


class VerdictTests(unittest.TestCase):
    def test_clean_text_passes(self):
        v = humanband.verdict("ch.md", _raw(0.30), max_distance=0.75)
        self.assertTrue(v.passed)
        self.assertEqual([], v.reasons)
        self.assertEqual("literary", v.register)

    def test_distance_over_ceiling_flags(self):
        v = humanband.verdict("ch.md", _raw(0.90), max_distance=0.75)
        self.assertFalse(v.passed)
        self.assertTrue(any("exceeds ceiling" in r for r in v.reasons))

    def test_outlier_always_flags_even_if_close(self):
        v = humanband.verdict("ch.md", _raw(0.10, outlier=True), max_distance=0.75)
        self.assertFalse(v.passed)
        self.assertTrue(any("outlier" in r for r in v.reasons))

    def test_self_tells_surface_as_reason_but_do_not_alone_fail(self):
        v = humanband.verdict("ch.md", _raw(0.20, self_tells=["em_dash_rate"]), max_distance=0.75)
        self.assertTrue(v.passed)  # still in band overall
        self.assertEqual(["em_dash_rate"], v.self_tells)
        self.assertTrue(any("self-tell" in r for r in v.reasons))

    def test_out_of_band_features_extracted(self):
        feats = {
            "ttr": {"status": "in"},
            "em_dash_rate": {"status": "above"},
            "contraction_rate": {"status": "below"},
        }
        v = humanband.verdict("ch.md", _raw(0.40, features=feats), max_distance=0.75)
        self.assertEqual(["contraction_rate", "em_dash_rate"], v.out_of_band)

    def test_as_dict_is_json_safe(self):
        import json

        v = humanband.verdict("ch.md", _raw(0.40), max_distance=0.75)
        json.dumps(v.as_dict())  # must not raise


class ResolutionTests(unittest.TestCase):
    def test_missing_scorer_raises_with_guidance(self):
        os.environ[humanband.ENV_OVERRIDE] = "/nonexistent/humanizer-pro-xyz"
        try:
            self.assertIsNone(humanband.humanizer_dir())
            with self.assertRaises(humanband.HumanizerUnavailable) as ctx:
                humanband.require_humanizer()
            self.assertIn("submodule", str(ctx.exception).lower())
        finally:
            del os.environ[humanband.ENV_OVERRIDE]

    def test_env_override_is_honored(self):
        with tempfile.TemporaryDirectory() as d:
            scripts = Path(d) / "scripts"
            scripts.mkdir()
            (scripts / "stylo.py").write_text("# stub\n", encoding="utf-8")
            os.environ[humanband.ENV_OVERRIDE] = d
            try:
                self.assertEqual(Path(d), humanband.humanizer_dir())
            finally:
                del os.environ[humanband.ENV_OVERRIDE]


@unittest.skipUnless(humanband.humanizer_dir(), "Better Humanizer submodule not present")
class IntegrationTests(unittest.TestCase):
    def test_score_file_runs_real_scorer(self):
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as f:
            f.write(
                "The rain found the gaps in the awning. Tomas waited, and didn't move. "
                "A dog crossed the square; somewhere a radio played an old song his mother "
                "used to hum off-key when she thought no one could hear.\n"
            )
            path = Path(f.name)
        try:
            score = humanband.score_file(path, register="literary")
            self.assertEqual("literary", score.register)
            self.assertIsInstance(score.distance, float)
            self.assertIn(score.passed, (True, False))
        finally:
            path.unlink(missing_ok=True)

    def test_score_manuscript_writes_report(self):
        with tempfile.TemporaryDirectory() as d:
            project = Path(d)
            chapters = project / "manuscript" / "chapters"
            chapters.mkdir(parents=True)
            (chapters / "chapter-01.md").write_text(
                "She read the letter twice. The second time she understood it, and wished "
                "she hadn't. Outside, the city kept its usual indifference.\n",
                encoding="utf-8",
            )
            summary = humanband.score_manuscript(project, register="literary")
            self.assertEqual(1, summary["chapters_scored"])
            self.assertTrue((project / "evaluations" / "human-band" / "REPORT.md").exists())


if __name__ == "__main__":
    unittest.main()
