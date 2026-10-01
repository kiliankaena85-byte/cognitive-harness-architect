"""
tests/test_test_synthesizer.py
=============================================================================
Unit Test Suite for Module 9: Test Synthesizer (Spec-to-Tests)
Universal Cognitive Decomposition Engine (UCDE) - Phase 1
=============================================================================
"""

import shutil
import tempfile
import unittest
from pathlib import Path

from core.schemas.analysis import ApiEndpoint, SystemAnalysisContract
from core.schemas.security import SecurityPolicyContract, StrideThreat
from core.schemas.strategy import BusinessRule, GherkinScenario, StrategyCJMContract
from core.test_synthesizer import TestSynthesizer


class TestTestSynthesizer(unittest.TestCase):
    def setUp(self):
        self.synthesizer = TestSynthesizer()
        self.temp_dir = tempfile.mkdtemp(prefix="ucde_testsynth_test_")

        self.sample_strategy = StrategyCJMContract(
            project_id="UCDE-Project-Alpha",
            product_vision="Automated Cognitive Synthesis Engine with Strict Zero-Trust Verification",
            target_personas=["Security Auditor", "Solution Architect"],
            jobs_to_be_done=["Synthesize executable test suites", "Guarantee full traceability to acceptance criteria"],
            acceptance_criteria=[
                GherkinScenario(
                    id="AC-AUTH-01",
                    given="Operator supplies valid Zero-Trust Bearer credentials",
                    when="Order creation endpoint is invoked",
                    then="Order is registered and confirmed with status 200",
                ),
                GherkinScenario(
                    id="AC-SAGA-02",
                    given="Actuator hardware timeout exceeds threshold",
                    when="State transaction commits",
                    then="Compensating rollback is executed deterministically",
                ),
            ],
            business_rules=[
                BusinessRule(rule_id="BR-01", description="All operations must be audited in append-only log", source_ac_id="AC-AUTH-01"),
                BusinessRule(rule_id="BR-02", description="Actuator interlock mandatory when delay exceeds 1000ms", source_ac_id="AC-SAGA-02"),
            ],
        )

        self.sample_analysis = SystemAnalysisContract(
            architecture_pattern="MODULAR_MONOLITH",
            openapi_version="3.1.0",
            endpoints=[
                ApiEndpoint(path="/api/v1/orders", method="POST", requires_auth=True, idempotent=True, timeout_ms=1000),
                ApiEndpoint(path="/api/v1/health", method="GET", requires_auth=False, idempotent=True, timeout_ms=300),
            ],
            cyclic_dependencies_detected=False,
            error_response_standard="RFC_7807",
        )

        stride_threats = [
            StrideThreat(category="SPOOFING", target_component="AuthGateway", mitigation_strategy="Mutual TLS with Ed25519 tokens"),
            StrideThreat(category="TAMPERING", target_component="Bus", mitigation_strategy="HMAC signatures on message frames"),
            StrideThreat(category="REPUDIATION", target_component="Logger", mitigation_strategy="Append-only Merkle tree logs"),
            StrideThreat(category="INFO_DISCLOSURE", target_component="DB", mitigation_strategy="AES-256-GCM encryption at rest"),
            StrideThreat(category="DENIAL_OF_SERVICE", target_component="Ingress", mitigation_strategy="Token-bucket rate limiting"),
            StrideThreat(category="ELEVATION_OF_PRIVILEGE", target_component="Core", mitigation_strategy="Hardware sandbox capability drop"),
        ]
        self.sample_security = SecurityPolicyContract(
            zero_trust_enforced=True,
            auth_mechanisms=["JWT_ED25519"],
            stride_matrix=stride_threats,
            rate_limiting_rps_per_ip=200,
            data_encryption_at_rest="AES_256_GCM",
            data_encryption_in_transit="TLS_1_3",
        )

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_synthesize_bdd_acceptance_suite_ast(self):
        code, count = self.synthesizer.synthesize_bdd_acceptance_suite(self.sample_strategy, self.sample_analysis)
        valid, err = self.synthesizer.verify_ast(code)
        self.assertTrue(valid, f"AST verification failed: {err}")
        self.assertEqual(count, 2)
        self.assertIn("test_scenario_AC_AUTH_01", code)
        self.assertIn("test_scenario_AC_SAGA_02", code)

    def test_synthesize_boundary_pbt_suite_ast(self):
        code, count = self.synthesizer.synthesize_boundary_pbt_suite(self.sample_analysis)
        valid, err = self.synthesizer.verify_ast(code)
        self.assertTrue(valid, f"AST verification failed: {err}")
        self.assertEqual(count, 4)
        self.assertIn("test_boundary_empty_payload", code)
        self.assertIn("test_boundary_large_payload", code)
        self.assertIn("test_boundary_idempotency_caching", code)

    def test_synthesize_security_stride_suite_ast(self):
        code, count = self.synthesizer.synthesize_security_stride_suite(self.sample_security, self.sample_analysis)
        valid, err = self.synthesizer.verify_ast(code)
        self.assertTrue(valid, f"AST verification failed: {err}")
        self.assertEqual(count, 4)
        self.assertIn("test_stride_spoofing_missing_auth_rejected", code)
        self.assertIn("test_stride_denial_of_service_burst_rate_limiting", code)

    def test_synthesize_rfc7807_suite_ast(self):
        code, count = self.synthesizer.synthesize_rfc7807_suite(self.sample_analysis)
        valid, err = self.synthesizer.verify_ast(code)
        self.assertTrue(valid, f"AST verification failed: {err}")
        self.assertEqual(count, 2)
        self.assertIn("test_404_problem_details_structure", code)

    def test_synthesize_test_suite_complete_coverage(self):
        suites = self.synthesizer.synthesize_test_suite(
            self.sample_strategy,
            self.sample_analysis,
            self.sample_security,
        )
        expected_files = {
            "test_acceptance_bdd.py",
            "test_boundary_pbt.py",
            "test_security_stride.py",
            "test_rfc7807_compliance.py",
        }
        self.assertEqual(set(suites.keys()), expected_files)
        total_tests = sum(s.test_count for s in suites.values())
        self.assertEqual(total_tests, 12)

    def test_write_test_suite_to_disk(self):
        res = self.synthesizer.write_test_suite(
            self.temp_dir,
            self.sample_strategy,
            self.sample_analysis,
            self.sample_security,
        )
        self.assertTrue(res["all_ast_valid"])
        self.assertEqual(res["test_files_count"], 4)
        self.assertEqual(res["total_synthesized_tests"], 12)


if __name__ == "__main__":
    unittest.main()
