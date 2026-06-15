"""Tests for the doctor self-check (runner/doctor.py)."""
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from runner import doctor as doctor_mod  # type: ignore  # noqa: E402
from runner.filesystem import scaffold_project  # type: ignore  # noqa: E402


class DoctorTests(unittest.TestCase):
    def test_checks_cover_core_wiring(self):
        checks = doctor_mod.run_checks()
        names = {c.name for c in checks}
        self.assertIn("python", names)
        self.assertIn("pipeline", names)
        self.assertIn("better-humanizer", names)

    def test_python_and_pipeline_checks_pass(self):
        checks = {c.name: c for c in doctor_mod.run_checks()}
        self.assertTrue(checks["python"].ok)
        self.assertTrue(checks["pipeline"].ok)

    def test_render_marks_status(self):
        checks = [
            doctor_mod.Check("a", True, "fine"),
            doctor_mod.Check("b", False, "broken", fatal=True),
            doctor_mod.Check("c", False, "soft", fatal=False),
        ]
        out = doctor_mod.render(checks)
        self.assertIn("[OK  ] a", out)
        self.assertIn("[FAIL] b", out)
        self.assertIn("[WARN] c", out)

    def test_has_fatal_failure_distinguishes_warn_from_fail(self):
        self.assertTrue(
            doctor_mod.has_fatal_failure([doctor_mod.Check("x", False, "", fatal=True)])
        )
        self.assertFalse(
            doctor_mod.has_fatal_failure([doctor_mod.Check("x", False, "", fatal=False)])
        )

    def test_project_check_validates_when_path_given(self):
        with tempfile.TemporaryDirectory() as d:
            project = Path(d)
            scaffold_project(project, idea="", adapter="codex", model_name="gpt-5.5")
            checks = doctor_mod.run_checks(project)
            project_checks = [c for c in checks if c.name.startswith("project ")]
            self.assertEqual(1, len(project_checks))
            self.assertTrue(project_checks[0].ok)


if __name__ == "__main__":
    unittest.main()
