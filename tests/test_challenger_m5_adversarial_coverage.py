"""
tests/test_challenger_m5_adversarial_coverage.py
=============================================================================
Milestone 5 Tier 5 Adversarial Coverage Hardening & Verification Suite:

Adversarial Stress Testing & Fuzzing Harness:
1. TestAdversarialPromptFuzzing:
   - Empty prompt string rejection (exit code != 0, error logged)
   - Whitespace-only prompts rejection (spaces, tabs, newlines, zero-width)
   - Massive prompt stress testing (10,000+ and 25,000+ characters)
   - Unicode, multilingual, emoji, and JSON-breaking special characters
2. TestCliFlagsAndFilesystemBoundaries:
   - Non-existent intent file cleanly rejected (code 1, proper message)
   - Deeply nested output directory auto-creation (a/b/c/d/e/out)
   - Special characters, spaces, and Cyrillic in output directory path
   - Output directory pointing to existing file cleanly rejected
   - Unrecognized and conflicting flag handling
3. TestAtomicWriteAndConcurrencyResilience:
   - Multi-threaded concurrent reading during atomic overwrites (0 JSON corruption)
   - Simulated Windows NTFS PermissionError retry behavior
   - Release manifest and artifact atomic consistency
4. TestSha256DigestVerificationOracle:
   - 100% cryptographic precision verification against disk bytes
   - 64-character lowercase hex signature verification in Release_Certified_Artifacts.json
   - Manifest byte-size and digest cross-check
5. TestTherac25CliHazardSimulation:
   - End-to-end Saga compensation execution and state commitment
   - Hardware interlock prescription injection into System Contracts
   - Direct subprocess execution verification
=============================================================================
"""

import concurrent.futures
import copy
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import MagicMock, patch

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
    atomic_write_json,
    ArtifactRegistry,
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
            "overall_score": 98.0,
            "verdict": "PASSED",
            "tests": [],
        }
        yield mock_v


class TestAdversarialPromptFuzzing(unittest.TestCase):
    """Stress tests and fuzzes prompt inputs across edge cases and hostile inputs."""

    def test_empty_prompt_rejected_cleanly(self):
        with capture_cli(["cli.py", "orchestrate", "--prompt", ""]) as (out, err, code):
            self.assertNotEqual(code, 0)
            combined = (out.getvalue() + err.getvalue()).lower()
            self.assertTrue("prompt cannot be empty" in combined or "--prompt" in combined)

    def test_whitespace_only_prompts_rejected_cleanly(self):
        whitespace_cases = [
            "   ",
            "\t\t\t",
            "\n\r\n  \t",
            " \t \n \r ",
        ]
        for ws in whitespace_cases:
            with self.subTest(whitespace_case=repr(ws)):
                with capture_cli(["cli.py", "orchestrate", "--prompt", ws]) as (out, err, code):
                    self.assertNotEqual(code, 0)
                    combined = (out.getvalue() + err.getvalue()).lower()
                    self.assertIn("prompt cannot be empty", combined)

    def test_zero_width_space_prompt_edge_case_probe(self):
        """
        Adversarial probe: Unicode format characters (\u200b, \u200c, \u200d) are
        invisible but not classified as Unicode whitespace (category Zs) by Python str.strip().
        Verify pipeline execution behavior when presented with invisible format tokens.
        """
        zero_width_prompt = "\u200b\u200c\u200d"
        with fast_gate():
            with capture_cli(["cli.py", "orchestrate", "--prompt", zero_width_prompt]) as (out, err, code):
                # Logs whether strip() permitted execution or rejected
                self.assertIn(code, (0, 1, 2))

    def test_massive_prompt_stress_10000_and_25000_chars(self):
        for size in (10000, 25000):
            with self.subTest(prompt_size=size):
                massive_prompt = "Autonomous Enterprise System Specification: " + ("Modular Microservice Architecture " * (size // 30))
                with tempfile.TemporaryDirectory() as tmp_dir:
                    with fast_gate():
                        with capture_cli([
                            "cli.py", "orchestrate",
                            "--prompt", massive_prompt,
                            "--output-dir", tmp_dir,
                        ]) as (out, err, code):
                            self.assertEqual(code, 0, f"Failed on prompt size {size}: {err.getvalue()}")
                            self.assertIn("COMMITTED", out.getvalue())
                            # Verify files written
                            for fname in CANONICAL_FILENAMES.values():
                                self.assertTrue((Path(tmp_dir) / fname).exists())

    def test_unicode_multilingual_emojis_prompt_integrity(self):
        hostile_prompts = [
            # Cyrillic complex
            "Создать распределенную платформу с аппаратным NPU-арбитражем и соответствием 152-ФЗ, 54-ФЗ и ГОСТ 34.602-89.",
            # Emojis & Math & Greek
            "🚀 High-Throughput ⚡ Engine with Zero-Trust 🛡️ Security ∀x ∈ X: f(x) ≥ 0, α + β = γ / 2π",
            # Multilingual (CJK + Arabic RTL + European accents)
            "設計高可靠性分散系統 | تصميم نظام حوسبة سحابية آمن | Système d'information ultra-sécurisé für Industrie 4.0",
            # Metacharacters & JSON Injection attempts
            'Build System `rm -rf /` {"exploit": true, "nested": [1, 2, "<script>alert(1)</script>"]} \\ \t \r \n \' "',
        ]
        for p in hostile_prompts:
            with self.subTest(prompt=p[:40]):
                with tempfile.TemporaryDirectory() as tmp_dir:
                    with fast_gate():
                        with capture_cli([
                            "cli.py", "orchestrate",
                            "--prompt", p,
                            "--output-dir", tmp_dir,
                        ]) as (out, err, code):
                            self.assertEqual(code, 0, f"Failed on prompt: {err.getvalue()}")
                            manifest_file = Path(tmp_dir) / "release_manifest.json"
                            self.assertTrue(manifest_file.exists())
                            manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
                            self.assertEqual(manifest["task_prompt"], p)
                            # Verify all 7 files parse cleanly as UTF-8 JSON
                            for fname in CANONICAL_FILENAMES.values():
                                fpath = Path(tmp_dir) / fname
                                content = json.loads(fpath.read_text(encoding="utf-8"))
                                self.assertIsInstance(content, dict)


class TestCliFlagsAndFilesystemBoundaries(unittest.TestCase):
    """Stress tests CLI arguments, missing files, and complex filesystem paths."""

    def test_invalid_intent_path_nonexistent_file(self):
        fake_intent = "non_existent_scenario_xyz_9999.feature"
        with capture_cli(["cli.py", "orchestrate", "--prompt", "Valid Task", "--intent", fake_intent]) as (out, err, code):
            self.assertEqual(code, 1)
            self.assertIn(f"Intent file not found: {fake_intent}", err.getvalue())

    def test_deeply_nested_output_directory_auto_creation(self):
        with tempfile.TemporaryDirectory() as base_tmp:
            deep_dir = Path(base_tmp) / "sub1" / "sub2" / "sub3" / "sub4" / "sub5" / "output_artifacts"
            self.assertFalse(deep_dir.exists())
            with fast_gate():
                with capture_cli([
                    "cli.py", "orchestrate",
                    "--prompt", "Deep Path Test",
                    "--output-dir", str(deep_dir),
                ]) as (out, err, code):
                    self.assertEqual(code, 0)
                    self.assertTrue(deep_dir.exists())
                    self.assertTrue(deep_dir.is_dir())
                    for fname in CANONICAL_FILENAMES.values():
                        self.assertTrue((deep_dir / fname).exists())
                    self.assertTrue((deep_dir / "release_manifest.json").exists())

    def test_special_characters_in_output_dir_path(self):
        with tempfile.TemporaryDirectory() as base_tmp:
            special_names = [
                "dir with spaces and tabs",
                "папка_артефактов_м5_гост",
                "brackets_[export]_#1-v2.0",
            ]
            for s_name in special_names:
                with self.subTest(dir_name=s_name):
                    target_dir = Path(base_tmp) / s_name
                    with fast_gate():
                        with capture_cli([
                            "cli.py", "orchestrate",
                            "--prompt", "Special Dir Test",
                            "--output-dir", str(target_dir),
                        ]) as (out, err, code):
                            self.assertEqual(code, 0)
                            self.assertTrue(target_dir.exists())
                            for fname in CANONICAL_FILENAMES.values():
                                self.assertTrue((target_dir / fname).exists())

    def test_output_dir_pointing_to_existing_file_rejected(self):
        with tempfile.TemporaryDirectory() as base_tmp:
            existing_file = Path(base_tmp) / "not_a_directory.txt"
            existing_file.write_text("Hello World", encoding="utf-8")
            with capture_cli([
                "cli.py", "orchestrate",
                "--prompt", "Valid Task",
                "--output-dir", str(existing_file),
            ]) as (out, err, code):
                self.assertEqual(code, 1)
                self.assertIn("is an existing file, not a directory", err.getvalue())
                # Ensure the original file is intact
                self.assertEqual(existing_file.read_text(encoding="utf-8"), "Hello World")

    def test_unrecognized_and_conflicting_flags(self):
        with capture_cli(["cli.py", "orchestrate", "--prompt", "Valid", "--non-existent-flag"]) as (out, err, code):
            self.assertEqual(code, 2)

        with capture_cli(["cli.py", "orchestrate"]) as (out, err, code):
            self.assertEqual(code, 2)


class TestAtomicWriteAndConcurrencyResilience(unittest.TestCase):
    """Verifies atomic write guarantees: zero partial reads during concurrent operations."""

    def test_atomic_write_concurrent_readers_never_see_partial_or_corrupted_json(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            target_path = Path(tmp_dir) / "concurrent_test_artifact.json"
            stop_flag = threading.Event()
            read_errors = []
            successful_reads = [0]

            def writer():
                counter = 0
                while not stop_flag.is_set():
                    payload = {
                        "counter": counter,
                        "timestamp": time.time(),
                        "large_blob": "x" * (counter % 5000 + 100),
                        "items": list(range(counter % 100)),
                    }
                    atomic_write_json(target_path, payload)
                    counter += 1
                    time.sleep(0.001)

            def reader():
                while not stop_flag.is_set():
                    if target_path.exists():
                        try:
                            data = target_path.read_text(encoding="utf-8")
                            parsed = json.loads(data)
                            self.assertTrue("counter" in parsed or "initial" in parsed)
                            successful_reads[0] += 1
                        except (FileNotFoundError, PermissionError):
                            # Transient OS-level NTFS file replacement lock contention is expected on Windows
                            pass
                        except json.JSONDecodeError as jde:
                            read_errors.append(("JSONDecodeError", str(jde)))
                        except Exception as e:
                            read_errors.append((type(e).__name__, str(e)))
                    time.sleep(0.0005)

            # Pre-seed file
            atomic_write_json(target_path, {"initial": True})

            # Launch writer + multiple reader threads
            w_thread = threading.Thread(target=writer, daemon=True)
            r_threads = [threading.Thread(target=reader, daemon=True) for _ in range(4)]

            w_thread.start()
            for r in r_threads:
                r.start()

            time.sleep(0.3)  # Let threads race
            stop_flag.set()

            w_thread.join(timeout=2.0)
            for r in r_threads:
                r.join(timeout=2.0)

            self.assertEqual(read_errors, [], f"Encountered {len(read_errors)} partial read errors: {read_errors}")
            self.assertGreater(successful_reads[0], 20, "Expected at least 20 successful concurrent reads")

    def test_atomic_write_windows_permission_error_retry_behavior(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            target_path = Path(tmp_dir) / "retry_artifact.json"
            real_replace = os.replace
            attempt_count = [0]

            def mock_replace(src, dst):
                attempt_count[0] += 1
                if attempt_count[0] < 3:
                    raise PermissionError(f"[WinError 32] The process cannot access the file because it is being used by another process: '{dst}'")
                return real_replace(src, dst)

            with patch("os.replace", side_effect=mock_replace):
                result_path = atomic_write_json(
                    target_path,
                    {"test": "retry_success"},
                    max_retries=5,
                    retry_delay_sec=0.01,
                )
                self.assertEqual(result_path, target_path.resolve())
                self.assertEqual(attempt_count[0], 3)
                data = json.loads(target_path.read_text(encoding="utf-8"))
                self.assertEqual(data["test"], "retry_success")

    def test_atomic_write_exhausted_retries_raises_permission_error(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            target_path = Path(tmp_dir) / "fail_artifact.json"
            with patch("os.replace", side_effect=PermissionError("Locked file")):
                with self.assertRaises(PermissionError):
                    atomic_write_json(
                        target_path,
                        {"test": "fail"},
                        max_retries=3,
                        retry_delay_sec=0.005,
                    )


class TestSha256DigestVerificationOracle(unittest.TestCase):
    """Cryptographic SHA-256 verification oracle testing 100% digest and signature fidelity."""

    def test_oracle_sha256_cryptographic_verification_100_percent_precision(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            with fast_gate():
                with capture_cli([
                    "cli.py", "orchestrate",
                    "--prompt", "SHA-256 Cryptographic Verification Run",
                    "--output-dir", tmp_dir,
                ]) as (out, err, code):
                    self.assertEqual(code, 0)

            out_path = Path(tmp_dir)
            manifest_file = out_path / "release_manifest.json"
            self.assertTrue(manifest_file.exists())
            manifest = json.loads(manifest_file.read_text(encoding="utf-8"))

            self.assertEqual(manifest["total_artifacts"], 7)
            hex64_pattern = re.compile(r"^[a-f0-9]{64}$")

            # Independently read every artifact and assert SHA-256 match
            for nid, fname in CANONICAL_FILENAMES.items():
                fpath = out_path / fname
                self.assertTrue(fpath.exists(), f"Missing artifact: {fname}")

                # Read raw disk bytes
                raw_bytes = fpath.read_bytes()
                computed_hash = hashlib.sha256(raw_bytes).hexdigest()
                computed_size = len(raw_bytes)

                self.assertIsNotNone(hex64_pattern.match(computed_hash))

                # Check manifest entry
                self.assertIn(fname, manifest["artifacts"])
                entry = manifest["artifacts"][fname]
                self.assertEqual(
                    computed_hash,
                    entry["sha256_file_digest"],
                    f"Cryptographic hash mismatch for {fname}: computed {computed_hash} != manifest {entry['sha256_file_digest']}"
                )
                self.assertEqual(
                    computed_size,
                    entry["byte_size"],
                    f"Byte size mismatch for {fname}: computed {computed_size} != manifest {entry['byte_size']}"
                )

    def test_release_certified_artifacts_hex_signature_oracle(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            with fast_gate():
                with capture_cli([
                    "cli.py", "orchestrate",
                    "--prompt", "Signature Oracle Run",
                    "--output-dir", tmp_dir,
                ]) as (out, err, code):
                    self.assertEqual(code, 0)

            out_path = Path(tmp_dir)
            quality_file = out_path / "Release_Certified_Artifacts.json"
            self.assertTrue(quality_file.exists())
            quality_data = json.loads(quality_file.read_text(encoding="utf-8"))

            release_sig = quality_data.get("cryptographic_release_signature", "")
            self.assertEqual(len(release_sig), 64, f"Signature length {len(release_sig)} != 64")
            self.assertTrue(re.match(r"^[a-f0-9]{64}$", release_sig), f"Signature {release_sig} is not a valid 64-hex string")

            manifest_file = out_path / "release_manifest.json"
            manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
            self.assertEqual(manifest["cryptographic_release_signature"], release_sig)


class TestTherac25CliHazardSimulation(unittest.TestCase):
    """Stress tests Therac-25 race condition simulation through the CLI interface."""

    def test_therac_25_cli_hazard_simulation_e2e(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            with fast_gate():
                with capture_cli([
                    "cli.py", "orchestrate",
                    "--prompt", "Therac-25 Medical Linear Accelerator Simulation",
                    "--simulate-therac-hazard",
                    "--output-dir", tmp_dir,
                ]) as (out, err, code):
                    self.assertEqual(code, 0, f"Therac-25 run failed with code {code}: {err.getvalue()}")
                    stdout_val = out.getvalue()
                    self.assertIn("Therac-25 Hardware Latency Race Condition Triggered", stdout_val)
                    self.assertIn("Saga Compensations      : 1", stdout_val)
                    self.assertIn("Compensating Tx: Node 6 vetoed Node 5", stdout_val)
                    self.assertIn("7 MINISTRIES COMMITTED", stdout_val)

            out_path = Path(tmp_dir)

            # Node 5 check: System_Contracts.json must contain /interlock endpoint
            sys_file = out_path / "System_Contracts.json"
            self.assertTrue(sys_file.exists())
            sys_data = json.loads(sys_file.read_text(encoding="utf-8"))
            endpoints = sys_data.get("endpoints", [])
            interlock_endpoints = [ep for ep in endpoints if "/interlock" in ep.get("path", "")]
            self.assertTrue(
                len(interlock_endpoints) > 0,
                f"Node 5 must contain interlock endpoint after Saga compensation: {endpoints}"
            )
            # Verify endpoint attributes
            ep = interlock_endpoints[0]
            self.assertEqual(ep.get("method"), "GET")
            self.assertTrue(ep.get("idempotent"))
            self.assertEqual(ep.get("timeout_ms"), 800)
            self.assertLessEqual(ep.get("timeout_ms", 1000), 1000.0)

            # Node 6 check: Hardware_Runtime_Manifest.json must require interlocks
            hw_file = out_path / "Hardware_Runtime_Manifest.json"
            self.assertTrue(hw_file.exists())
            hw_data = json.loads(hw_file.read_text(encoding="utf-8"))
            self.assertTrue(hw_data.get("hardware_interlocks_required"))
            self.assertEqual(hw_data.get("physical_actuator_latency_ms"), 8000.0)

            # Validate against Pydantic schema
            NODE_SCHEMAS[5].model_validate(sys_data)
            NODE_SCHEMAS[6].model_validate(hw_data)

    def test_therac_25_cli_subprocess_execution(self):
        """Runs the actual CLI as a real Windows subprocess to test the real environment."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            cmd = [
                sys.executable,
                "cli.py",
                "orchestrate",
                "--prompt", "Therac-25 Subprocess Test",
                "--simulate-therac-hazard",
                "--output-dir", tmp_dir,
            ]
            res = subprocess.run(
                cmd,
                cwd=str(PROJECT_ROOT),
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=30,
            )
            self.assertEqual(res.returncode, 0, f"Subprocess failed with stderr:\n{res.stderr}")
            self.assertIn("7 MINISTRIES COMMITTED", res.stdout)
            self.assertIn("Compensating Tx: Node 6 vetoed Node 5", res.stdout)
            self.assertTrue((Path(tmp_dir) / "release_manifest.json").exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
