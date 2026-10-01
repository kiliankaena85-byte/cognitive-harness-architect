"""
tests/test_sandbox_runner.py
=============================================================================
Verification suite for SandboxRunner & Self-Healing TDD Execution Loop.
Tests:
- Unit test output regex parsing
- Subprocess sandbox isolation and environment variables
- Real synthesized service execution with 100% pass rate
- Self-healing retry callback loop (tau_max <= 3)
- Subprocess timeout handling
=============================================================================
"""

import os
import shutil
import tempfile
import unittest
from pathlib import Path

from core.code_synthesizer import CodeSynthesizer
from core.test_synthesizer import TestSynthesizer
from core.sandbox_runner import SandboxRunner, SandboxExecutionResult
from core.schemas.analysis import ApiEndpoint, SystemAnalysisContract
from core.schemas.security import SecurityPolicyContract, StrideThreat
from core.schemas.strategy import BusinessRule, GherkinScenario, StrategyCJMContract


class TestSandboxRunner(unittest.TestCase):
    """Test suite for isolated subprocess sandbox and self-healing loop."""

    def setUp(self):
        self.runner = SandboxRunner(timeout_sec=10.0, max_self_healing_retries=3)
        self.temp_dir = tempfile.mkdtemp(prefix="ucde_sandbox_test_")

    def tearDown(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_parse_unittest_output_success(self):
        """Regex parser extracts 0 failures/errors on OK output."""
        sample_ok = "Ran 12 tests in 0.045s\n\nOK\n"
        tests_run, failures, errors = SandboxRunner._parse_unittest_output(sample_ok)
        self.assertEqual(tests_run, 12)
        self.assertEqual(failures, 0)
        self.assertEqual(errors, 0)

    def test_parse_unittest_output_failures(self):
        """Regex parser extracts failure and error counts correctly."""
        sample_fail = "Ran 8 tests in 0.120s\n\nFAILED (failures=3, errors=1)\n"
        tests_run, failures, errors = SandboxRunner._parse_unittest_output(sample_fail)
        self.assertEqual(tests_run, 8)
        self.assertEqual(failures, 3)
        self.assertEqual(errors, 1)

    def test_execute_empty_or_nonexistent_directory(self):
        """Nonexistent package directory raises FileNotFoundError."""
        with self.assertRaises(FileNotFoundError):
            self.runner.execute_test_suite(Path(self.temp_dir) / "does_not_exist")

    def test_execute_real_synthesized_service_in_sandbox(self):
        """
        Synthesizes a full service and test suite, runs inside the subprocess sandbox,
        and verifies 100% test pass rate in isolated environment.
        """
        strategy = StrategyCJMContract(
            project_id="SANDBOX-001",
            product_vision="Automated execution verification in sandboxed subprocess",
            target_personas=["Security Auditor", "Solution Architect"],
            jobs_to_be_done=["Execute tests in sandbox", "Validate RFC 7807 compliance"],
            acceptance_criteria=[
                GherkinScenario(
                    id="AC-HEALTH-01",
                    given="Service is running",
                    when="GET /api/v1/health is invoked",
                    then="Status is 200 OK",
                ),
                GherkinScenario(
                    id="AC-ORDERS-01",
                    given="Operator supplies valid Bearer credentials",
                    when="POST /api/v1/orders is invoked",
                    then="Order is registered with status 200",
                ),
            ],
            business_rules=[
                BusinessRule(rule_id="BR-01", description="Valid health check", source_ac_id="AC-HEALTH-01"),
                BusinessRule(rule_id="BR-02", description="Valid orders check", source_ac_id="AC-ORDERS-01"),
            ],
        )

        analysis = SystemAnalysisContract(
            architecture_pattern="MODULAR_MONOLITH",
            openapi_version="3.1.0",
            endpoints=[
                ApiEndpoint(path="/api/v1/health", method="GET", requires_auth=False, idempotent=True, timeout_ms=300),
                ApiEndpoint(path="/api/v1/orders", method="POST", requires_auth=True, idempotent=True, timeout_ms=1000),
            ],
            async_message_bus="REDIS_STREAMS",
            database_normalization="3NF",
            cyclic_dependencies_detected=False,
            error_response_standard="RFC_7807",
            c4_model_level="COMPONENT",
        )

        stride_threats = [
            StrideThreat(category="SPOOFING", target_component="AuthGateway", mitigation_strategy="Mutual TLS with Ed25519 tokens"),
            StrideThreat(category="TAMPERING", target_component="Bus", mitigation_strategy="HMAC signatures on message frames"),
            StrideThreat(category="REPUDIATION", target_component="Logger", mitigation_strategy="Append-only Merkle tree logs"),
            StrideThreat(category="INFO_DISCLOSURE", target_component="DB", mitigation_strategy="AES-256-GCM encryption at rest"),
            StrideThreat(category="DENIAL_OF_SERVICE", target_component="Ingress", mitigation_strategy="Token-bucket rate limiting"),
            StrideThreat(category="ELEVATION_OF_PRIVILEGE", target_component="Core", mitigation_strategy="Hardware sandbox capability drop"),
        ]

        security = SecurityPolicyContract(
            zero_trust_enforced=True,
            auth_mechanisms=["JWT_ED25519"],
            stride_matrix=stride_threats,
            rate_limiting_rps_per_ip=200,
            data_encryption_at_rest="AES_256_GCM",
            data_encryption_in_transit="TLS_1_3",
        )

        # Synthesize service code
        code_synth = CodeSynthesizer()
        code_synth.write_service(self.temp_dir, analysis, security)

        # Synthesize test suite
        test_synth = TestSynthesizer()
        test_synth.write_test_suite(self.temp_dir, strategy, analysis, security)

        # Execute in sandbox
        result = self.runner.execute_test_suite(self.temp_dir)
        self.assertTrue(
            result.success,
            f"Sandbox execution failed: {result.error_summary}\nStdout: {result.stdout}\nStderr: {result.stderr}",
        )
        self.assertGreater(result.tests_run, 0)
        self.assertEqual(result.failures, 0)
        self.assertEqual(result.errors, 0)
        self.assertGreater(result.duration_ms, 0.0)

    def test_execute_with_self_healing_repair_loop(self):
        """
        Creates an initially failing test, provides a self-healing repair callback,
        and verifies the runner autonomously heals and achieves success on attempt 1.
        """
        test_file = Path(self.temp_dir) / "test_flaky.py"
        # Initially failing test
        test_file.write_text(
            "import unittest\n\n"
            "class FlakyTest(unittest.TestCase):\n"
            "    def test_check(self):\n"
            "        self.assertTrue(False, 'Initial failure')\n",
            encoding="utf-8",
        )

        repair_called = []

        def mock_repair_callback(feedback: str, attempt: int) -> bool:
            repair_called.append((feedback, attempt))
            # Fix the test
            test_file.write_text(
                "import unittest\n\n"
                "class FlakyTest(unittest.TestCase):\n"
                "    def test_check(self):\n"
                "        self.assertTrue(True)\n",
                encoding="utf-8",
            )
            return True

        result = self.runner.execute_with_self_healing(self.temp_dir, repair_callback=mock_repair_callback)
        self.assertTrue(result.success)
        self.assertEqual(result.self_healing_attempts, 1)
        self.assertEqual(len(repair_called), 1)

    def test_execute_with_self_healing_max_retries_exhaustion(self):
        """
        Verifies that when repair cannot fix the failure, runner stops after max_self_healing_retries.
        """
        test_file = Path(self.temp_dir) / "test_unfixable.py"
        test_file.write_text(
            "import unittest\n\n"
            "class UnfixableTest(unittest.TestCase):\n"
            "    def test_fail(self):\n"
            "        self.fail('Unfixable defect')\n",
            encoding="utf-8",
        )

        attempts_recorded = []

        def failing_repair_callback(feedback: str, attempt: int) -> bool:
            attempts_recorded.append(attempt)
            # Cannot fix, leaves test as failing
            return True

        result = self.runner.execute_with_self_healing(self.temp_dir, repair_callback=failing_repair_callback)
        self.assertFalse(result.success)
        self.assertEqual(result.self_healing_attempts, 3)
        self.assertEqual(len(attempts_recorded), 3)


if __name__ == "__main__":
    unittest.main()
