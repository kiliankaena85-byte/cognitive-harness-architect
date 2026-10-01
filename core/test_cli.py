"""
core/test_cli.py
=============================================================================
Milestone 5 Test Suite: CLI Orchestrate Integration & Verification Harness

Tests Cover (5 Test Classes, 18 Test Methods):
1. TestCliArgumentParsing (5 tests)
2. TestCliValidationAndErrorHandling (5 tests)
3. TestCliLine409OccurrencesBugFix (3 tests)
4. TestCliOrchestrateExecution (4 tests)
5. TestCliPerformanceAndIsolation (1 test)

Execution Benchmark: < 5.0 seconds
Discovery: python -m unittest discover -s core -p "test_*.py"
=============================================================================
"""

import io
import json
import hashlib
import os
import sys
import tempfile
import time
import unittest
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import patch, MagicMock

# Path configuration
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
CORE_DIR = PROJECT_ROOT / "core"
if str(CORE_DIR) not in sys.path:
    sys.path.insert(0, str(CORE_DIR))

import cli
from core.orchestrator import (
    DagOrchestrator,
    CANONICAL_FILENAMES,
    NODE_SCHEMAS,
    MINISTRY_NAMES,
)
from core.schemas import (
    StrategyCJMContract,
    FinanceBudgetContract,
    LegalComplianceContract,
    SecurityPolicyContract,
    SystemAnalysisContract,
    HardwareRuntimeContract,
    VVQualityContract,
)


@contextmanager
def capture_cli(argv):
    old_argv = sys.argv
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    out = io.StringIO()
    err = io.StringIO()
    exit_code = 0
    try:
        sys.argv = argv
        sys.stdout = out
        sys.stderr = err
        try:
            cli.main()
        except SystemExit as se:
            exit_code = se.code if se.code is not None else 0
        yield out, err, exit_code
    finally:
        sys.argv = old_argv
        sys.stdout = old_stdout
        sys.stderr = old_stderr


@contextmanager
def fast_gate():
    with patch("core.orchestrator.DeterministicHarnessVerifier") as mock_v:
        mock_v.return_value.run_full_verification.return_value = {
            "overall_score": 96.0,
            "verdict": "PASSED",
            "tests": [],
        }
        yield mock_v


class TestCliArgumentParsing(unittest.TestCase):
    def test_orchestrate_subcommand_registered(self):
        with capture_cli(["cli.py", "orchestrate", "--help"]) as (out, err, code):
            self.assertEqual(code, 0)
            help_text = out.getvalue()
            self.assertIn("--prompt", help_text)
            self.assertIn("--output-dir", help_text)
            self.assertIn("--simulate-therac-hazard", help_text)

    def test_orchestrate_prompt_argument_parsed(self):
        with patch("cli.cmd_orchestrate") as mock_cmd:
            mock_cmd.return_value = 0
            with capture_cli(["cli.py", "orchestrate", "--prompt", "Build High-Throughput Trading Engine"]):
                self.assertTrue(mock_cmd.called)
                args = mock_cmd.call_args[0][0]
                self.assertEqual(args.command, "orchestrate")
                self.assertEqual(args.prompt, "Build High-Throughput Trading Engine")

    def test_orchestrate_output_dir_argument_parsed(self):
        with patch("cli.cmd_orchestrate") as mock_cmd:
            mock_cmd.return_value = 0
            with capture_cli(["cli.py", "orchestrate", "--prompt", "Task", "--output-dir", "custom_output"]):
                args = mock_cmd.call_args[0][0]
                self.assertEqual(args.output_dir, "custom_output")

            with capture_cli(["cli.py", "orchestrate", "--prompt", "Task"]):
                args = mock_cmd.call_args[0][0]
                self.assertIsNone(args.output_dir)

    def test_orchestrate_intent_argument_parsed(self):
        with patch("cli.cmd_orchestrate") as mock_cmd:
            mock_cmd.return_value = 0
            with capture_cli(["cli.py", "orchestrate", "--prompt", "Task", "--intent", "intent.feature"]):
                args = mock_cmd.call_args[0][0]
                self.assertEqual(args.intent, "intent.feature")

            with capture_cli(["cli.py", "orchestrate", "--prompt", "Task"]):
                args = mock_cmd.call_args[0][0]
                self.assertIsNone(args.intent)

    def test_orchestrate_flags_parsing(self):
        with patch("cli.cmd_orchestrate") as mock_cmd:
            mock_cmd.return_value = 0
            with capture_cli(["cli.py", "orchestrate", "--prompt", "Task", "--simulate-therac-hazard", "--live"]):
                args = mock_cmd.call_args[0][0]
                self.assertTrue(args.simulate_therac_hazard)
                self.assertTrue(args.live)

            with capture_cli(["cli.py", "orchestrate", "--prompt", "Task"]):
                args = mock_cmd.call_args[0][0]
                self.assertFalse(args.simulate_therac_hazard)
                self.assertFalse(args.live)
                self.assertTrue(args.mock)


class TestCliValidationAndErrorHandling(unittest.TestCase):
    def test_missing_prompt_raises_system_exit_code_2(self):
        with capture_cli(["cli.py", "orchestrate"]) as (out, err, code):
            self.assertEqual(code, 2)
            self.assertIn("--prompt", err.getvalue().lower())

    def test_unrecognized_arguments_raise_system_exit_code_2(self):
        with capture_cli(["cli.py", "orchestrate", "--prompt", "Valid", "--bogus"]) as (out, err, code):
            self.assertEqual(code, 2)

    def test_empty_prompt_string_rejected(self):
        with capture_cli(["cli.py", "orchestrate", "--prompt", "   "]) as (out, err, code):
            self.assertNotEqual(code, 0)
            combined = out.getvalue() + err.getvalue()
            self.assertIn("prompt cannot be empty", combined.lower())

    def test_nonexistent_intent_file_rejected_cleanly(self):
        bad_path = "non_existent_intent_file_xyz_123.feature"
        with capture_cli(["cli.py", "orchestrate", "--prompt", "Task", "--intent", bad_path]) as (out, err, code):
            self.assertNotEqual(code, 0)
            self.assertIn("intent", err.getvalue().lower())

    def test_valid_intent_file_accepted(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            fpath = Path(tmp_dir) / "test.feature"
            fpath.write_text("Feature: Test\nScenario: AC-01\nGiven A\nWhen B\nThen C\n", encoding="utf-8")
            with fast_gate():
                with capture_cli(["cli.py", "orchestrate", "--prompt", "Task", "--intent", str(fpath)]) as (out, err, code):
                    self.assertEqual(code, 0)


class TestCliLine409OccurrencesBugFix(unittest.TestCase):
    def test_cmd_verify_line_409_missing_occurrences_key_no_crash(self):
        fake_report = {
            "verdict": "FAILED",
            "overall_score": 75.0,
            "verification_duration_ms": 10.0,
            "tests": [{
                "test_id": "ISO-29148-02",
                "name": "Precision Test",
                "passed": False,
                "score": 75.0,
                "fuzzy_terms_found": [{"fuzzy_term": "в реальном времени", "remedy": "Fix"}]
            }]
        }
        with patch("cli.DeterministicHarnessVerifier") as MockV:
            MockV.return_value.run_full_verification.return_value = fake_report
            with capture_cli(["cli.py", "verify"]) as (out, err, code):
                self.assertEqual(code, 0)
                self.assertIn("(1x)", out.getvalue())
                self.assertIn("в реальном времени", out.getvalue())

    def test_cmd_verify_line_409_present_occurrences_key_formatted(self):
        fake_report = {
            "verdict": "FAILED",
            "overall_score": 75.0,
            "verification_duration_ms": 10.0,
            "tests": [{
                "test_id": "ISO-29148-02",
                "name": "Precision Test",
                "passed": False,
                "score": 75.0,
                "fuzzy_terms_found": [{"fuzzy_term": "быстрый", "occurrences": 4, "remedy": "Fix"}]
            }]
        }
        with patch("cli.DeterministicHarnessVerifier") as MockV:
            MockV.return_value.run_full_verification.return_value = fake_report
            with capture_cli(["cli.py", "verify"]) as (out, err, code):
                self.assertEqual(code, 0)
                self.assertIn("(4x)", out.getvalue())

    def test_cmd_verify_line_409_mixed_occurrences_batch(self):
        fake_report = {
            "verdict": "FAILED",
            "overall_score": 70.0,
            "verification_duration_ms": 10.0,
            "tests": [{
                "test_id": "ISO-29148-02",
                "name": "Precision Test",
                "passed": False,
                "score": 70.0,
                "fuzzy_terms_found": [
                    {"fuzzy_term": "term1", "remedy": "Fix1"},
                    {"fuzzy_term": "term2", "occurrences": 3, "remedy": "Fix2"},
                ]
            }]
        }
        with patch("cli.DeterministicHarnessVerifier") as MockV:
            MockV.return_value.run_full_verification.return_value = fake_report
            with capture_cli(["cli.py", "verify"]) as (out, err, code):
                self.assertEqual(code, 0)
                self.assertIn("(1x)", out.getvalue())
                self.assertIn("(3x)", out.getvalue())


class TestCliOrchestrateExecution(unittest.TestCase):
    def test_orchestrate_default_invocation_produces_7_validated_artifacts(self):
        with fast_gate():
            with capture_cli(["cli.py", "orchestrate", "--prompt", "Autonomous Cognitive Pipeline"]) as (out, err, code):
                self.assertEqual(code, 0)
                output = out.getvalue()
                self.assertIn("COMMITTED", output)
                for fname in CANONICAL_FILENAMES.values():
                    self.assertIn(fname, output)

            # Direct invocation of cmd_orchestrate to validate returned PipelineResult
            import argparse
            from contextlib import redirect_stdout
            args = argparse.Namespace(
                prompt="Autonomous Cognitive Pipeline",
                intent=None,
                output_dir=None,
                mock=True,
                live=False,
                simulate_therac_hazard=False,
            )
            with redirect_stdout(io.StringIO()):
                res = cli.cmd_orchestrate(args)
            self.assertEqual(res.status, "SUCCESS")
            for nid in range(1, 8):
                fname = CANONICAL_FILENAMES[nid]
                self.assertIn(fname, res.artifacts)
                schema_cls = NODE_SCHEMAS[nid]
                validated = schema_cls.model_validate(res.artifacts[fname])
                self.assertIsNotNone(validated)
                self.assertEqual(res.fsm_states[nid], "STATE_COMMITTED")

    def test_orchestrate_output_dir_writes_all_7_files_with_sha256_digests(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            with fast_gate():
                with capture_cli(["cli.py", "orchestrate", "--prompt", "Test Export", "--output-dir", tmp_dir]) as (out, err, code):
                    self.assertEqual(code, 0)

                    for nid, fname in CANONICAL_FILENAMES.items():
                        fpath = Path(tmp_dir) / fname
                        self.assertTrue(fpath.exists(), f"File {fname} missing from output dir")
                        data = json.loads(fpath.read_text(encoding="utf-8"))
                        self.assertIsInstance(data, dict)

                        # Schema validation
                        schema_cls = NODE_SCHEMAS[nid]
                        schema_cls.model_validate(data)

                        # Physical SHA-256 digest check
                        h = hashlib.sha256(fpath.read_bytes()).hexdigest()
                        self.assertEqual(len(h), 64)
                        self.assertRegex(h, r"^[a-f0-9]{64}$")

                    # Release certified signature
                    quality_path = Path(tmp_dir) / "Release_Certified_Artifacts.json"
                    quality_data = json.loads(quality_path.read_text(encoding="utf-8"))
                    sig = quality_data.get("cryptographic_release_signature", "")
                    self.assertEqual(len(sig), 64)
                    self.assertRegex(sig, r"^[a-f0-9]{64}$")

                    # Release manifest
                    manifest_path = Path(tmp_dir) / "release_manifest.json"
                    self.assertTrue(manifest_path.exists())
                    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                    self.assertEqual(manifest.get("total_artifacts"), 7)
                    self.assertEqual(manifest.get("cryptographic_release_signature"), sig)
                    for fname in CANONICAL_FILENAMES.values():
                        self.assertIn(fname, manifest["artifacts"])
                        file_h = hashlib.sha256((Path(tmp_dir) / fname).read_bytes()).hexdigest()
                        self.assertEqual(manifest["artifacts"][fname]["sha256_file_digest"], file_h)

    def test_orchestrate_simulate_therac_hazard_exercises_saga_and_commits(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            with fast_gate():
                with capture_cli([
                    "cli.py", "orchestrate",
                    "--prompt", "Therac Accelerator",
                    "--simulate-therac-hazard",
                    "--output-dir", tmp_dir,
                ]) as (out, err, code):
                    self.assertEqual(code, 0)

                    # Read System Analysis
                    sys_data = json.loads((Path(tmp_dir) / "System_Contracts.json").read_text(encoding="utf-8"))
                    has_interlock = any("/interlock" in ep.get("path", "") for ep in sys_data.get("endpoints", []))
                    self.assertTrue(has_interlock, "Therac resolution must append interlock endpoint")

                    # Read Hardware Manifest
                    hw_data = json.loads((Path(tmp_dir) / "Hardware_Runtime_Manifest.json").read_text(encoding="utf-8"))
                    self.assertTrue(hw_data.get("hardware_interlocks_required"))
                    self.assertEqual(hw_data.get("physical_actuator_latency_ms"), 8000.0)

    def test_orchestrate_console_presentation_and_fsm_summary(self):
        with fast_gate():
            with capture_cli(["cli.py", "orchestrate", "--prompt", "Presentation Test"]) as (out, err, code):
                self.assertEqual(code, 0)
                val = out.getvalue()
                self.assertIn("PROJECT HARNESS & SKILL SYNTHESIZER", val)
                self.assertIn("7 MINISTRIES", val.upper())


class TestCliPerformanceAndIsolation(unittest.TestCase):
    def test_cli_suite_runtime_under_5_seconds(self):
        t0 = time.perf_counter()
        with fast_gate():
            with capture_cli(["cli.py", "orchestrate", "--prompt", "Speed Benchmark"]) as (out, err, code):
                self.assertEqual(code, 0)
        elapsed = time.perf_counter() - t0
        self.assertLess(elapsed, 5.0, f"CLI execution took {elapsed:.3f}s, exceeding 5.0s requirement")


if __name__ == "__main__":
    unittest.main(verbosity=2)
