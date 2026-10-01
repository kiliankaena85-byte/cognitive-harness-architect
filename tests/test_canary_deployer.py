"""
tests/test_canary_deployer.py
=============================================================================
Unit Test Suite for Progressive Canary Deployment & Rollback Engine.
Phase 4 - Universal Cognitive Decomposition Engine (UCDE)
=============================================================================
"""

import unittest
from core.canary_deployer import (
    CanaryDeployer,
    DeploymentAttestation,
    StageTelemetry,
)


class TestCanaryDeployer(unittest.TestCase):
    def setUp(self):
        self.deployer = CanaryDeployer(
            max_p95_latency_ms=50.0,
            max_error_rate_pct=0.1,  # 99.9% SLO
            target_env="k8s-prod-cluster",
        )

    def test_progressive_rollout_full_success(self):
        healthy_stages = [
            {"stage": "STAGE_10_CANARY", "traffic": 10, "p95": 14.2, "error_pct": 0.0, "5xx": 0},
            {"stage": "STAGE_50_PROGRESSIVE", "traffic": 50, "p95": 22.5, "error_pct": 0.01, "5xx": 0},
            {"stage": "STAGE_100_PRODUCTION", "traffic": 100, "p95": 28.9, "error_pct": 0.02, "5xx": 0},
        ]
        attestation = self.deployer.execute_progressive_rollout("v2.0.0", healthy_stages)

        self.assertTrue(attestation.promoted_to_production)
        self.assertEqual(attestation.status, "SUCCESS_PROMOTED")
        self.assertIsNone(attestation.rollback_reason)
        self.assertEqual(len(attestation.stages_completed), 3)
        self.assertEqual(len(attestation.attestation_seal), 64)

    def test_latency_regression_triggers_stage1_rollback(self):
        degraded_stages = [
            # P95 latency 75.0ms breaches 50.0ms threshold
            {"stage": "STAGE_10_CANARY", "traffic": 10, "p95": 75.0, "error_pct": 0.0, "5xx": 0},
            {"stage": "STAGE_50_PROGRESSIVE", "traffic": 50, "p95": 20.0, "error_pct": 0.0, "5xx": 0},
            {"stage": "STAGE_100_PRODUCTION", "traffic": 100, "p95": 20.0, "error_pct": 0.0, "5xx": 0},
        ]
        attestation = self.deployer.execute_progressive_rollout("v2.0.0", degraded_stages)

        self.assertFalse(attestation.promoted_to_production)
        self.assertEqual(attestation.status, "ROLLED_BACK")
        self.assertIn("breached SLO", attestation.rollback_reason)
        self.assertIn("75.0ms", attestation.rollback_reason)
        # Should halt immediately at Stage 1
        self.assertEqual(len(attestation.stages_completed), 1)

    def test_error_rate_breach_triggers_stage2_rollback(self):
        degraded_stages = [
            {"stage": "STAGE_10_CANARY", "traffic": 10, "p95": 15.0, "error_pct": 0.0, "5xx": 0},
            # Error rate 0.45% breaches 0.1% threshold
            {"stage": "STAGE_50_PROGRESSIVE", "traffic": 50, "p95": 30.0, "error_pct": 0.45, "5xx": 0},
            {"stage": "STAGE_100_PRODUCTION", "traffic": 100, "p95": 25.0, "error_pct": 0.0, "5xx": 0},
        ]
        attestation = self.deployer.execute_progressive_rollout("v2.0.0", degraded_stages)

        self.assertFalse(attestation.promoted_to_production)
        self.assertEqual(attestation.status, "ROLLED_BACK")
        self.assertIn("0.45%", attestation.rollback_reason)
        self.assertEqual(len(attestation.stages_completed), 2)

    def test_http_5xx_errors_trigger_instant_rollback(self):
        degraded_stages = [
            {"stage": "STAGE_10_CANARY", "traffic": 10, "p95": 10.0, "error_pct": 0.0, "5xx": 0},
            # 5xx error observed
            {"stage": "STAGE_50_PROGRESSIVE", "traffic": 50, "p95": 12.0, "error_pct": 0.05, "5xx": 2},
        ]
        attestation = self.deployer.execute_progressive_rollout("v2.0.0", degraded_stages)

        self.assertFalse(attestation.promoted_to_production)
        self.assertEqual(attestation.status, "ROLLED_BACK")
        self.assertIn("5xx Errors: 2", attestation.rollback_reason)


if __name__ == "__main__":
    unittest.main()
