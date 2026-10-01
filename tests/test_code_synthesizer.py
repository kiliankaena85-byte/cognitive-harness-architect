"""
tests/test_code_synthesizer.py
=============================================================================
Unit Test Suite for Module 8: Code Synthesizer (Spec-to-Code)
Universal Cognitive Decomposition Engine (UCDE) - Phase 1
=============================================================================
"""

import ast
import shutil
import tempfile
import unittest
from pathlib import Path

from core.code_synthesizer import CodeSynthesizer, SynthesizedFile
from core.schemas.analysis import ApiEndpoint, SystemAnalysisContract
from core.schemas.security import SecurityPolicyContract, StrideThreat


class TestCodeSynthesizer(unittest.TestCase):
    def setUp(self):
        self.synthesizer = CodeSynthesizer()
        self.temp_dir = tempfile.mkdtemp(prefix="ucde_synth_test_")

        self.sample_analysis = SystemAnalysisContract(
            architecture_pattern="EVENT_DRIVEN_MICROSERVICES",
            openapi_version="3.1.0",
            endpoints=[
                ApiEndpoint(path="/api/v1/health", method="GET", requires_auth=False, idempotent=True, timeout_ms=500),
                ApiEndpoint(path="/api/v1/orders", method="POST", requires_auth=True, idempotent=True, timeout_ms=1500),
                ApiEndpoint(path="/api/v1/telemetry", method="GET", requires_auth=True, idempotent=False, timeout_ms=800),
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
        self.sample_security = SecurityPolicyContract(
            zero_trust_enforced=True,
            auth_mechanisms=["JWT_ED25519", "MTLS"],
            stride_matrix=stride_threats,
            rate_limiting_rps_per_ip=250,
            data_encryption_at_rest="AES_256_GCM",
            data_encryption_in_transit="TLS_1_3",
        )

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_synthesize_schemas_valid_ast(self):
        code = self.synthesizer.synthesize_schemas(self.sample_analysis.endpoints)
        valid, err = self.synthesizer.verify_ast(code)
        self.assertTrue(valid, f"AST verification failed: {err}")
        self.assertIn("class ProblemDetails(BaseModel):", code)
        self.assertIn("class ApiV1OrdersRequest(BaseModel):", code)
        self.assertIn("class ApiV1HealthResponse(BaseModel):", code)

    def test_synthesize_security_valid_ast(self):
        code = self.synthesizer.synthesize_security(self.sample_security)
        valid, err = self.synthesizer.verify_ast(code)
        self.assertTrue(valid, f"AST verification failed: {err}")
        self.assertIn("class SecurityGuard:", code)
        self.assertIn("RATE_LIMIT_RPS_PER_IP = 250", code)
        self.assertIn("JWT_ED25519", code)

    def test_synthesize_routes_valid_ast(self):
        code = self.synthesizer.synthesize_routes(self.sample_analysis.endpoints)
        valid, err = self.synthesizer.verify_ast(code)
        self.assertTrue(valid, f"AST verification failed: {err}")
        self.assertIn("def get_api_v1_health", code)
        self.assertIn("def post_api_v1_orders", code)
        self.assertIn("IDEMPOTENCY_CACHE", code)

    def test_synthesize_main_valid_ast(self):
        code = self.synthesizer.synthesize_main(self.sample_analysis)
        valid, err = self.synthesizer.verify_ast(code)
        self.assertTrue(valid, f"AST verification failed: {err}")
        self.assertIn("def dispatch_request", code)
        self.assertIn("def create_app", code)
        self.assertIn('("GET", "/api/v1/health")', code)

    def test_synthesize_service_returns_all_expected_files(self):
        files = self.synthesizer.synthesize_service(self.sample_analysis, self.sample_security)
        expected_files = {"__init__.py", "app_schemas.py", "app_security.py", "app_routes.py", "main.py"}
        self.assertEqual(set(files.keys()), expected_files)

        for fname, sfile in files.items():
            self.assertTrue(sfile.ast_valid)
            self.assertEqual(len(sfile.sha256), 64)
            self.assertGreater(sfile.byte_size, 0)

    def test_write_service_writes_to_disk(self):
        res = self.synthesizer.write_service(self.temp_dir, self.sample_analysis, self.sample_security)
        self.assertTrue(res["all_ast_valid"])
        self.assertEqual(res["files_written"], 5)

        for fname in ["__init__.py", "app_schemas.py", "app_security.py", "app_routes.py", "main.py"]:
            fpath = Path(self.temp_dir) / fname
            self.assertTrue(fpath.exists(), f"File '{fname}' was not written.")
            self.assertGreater(fpath.stat().st_size, 0)


if __name__ == "__main__":
    unittest.main()
