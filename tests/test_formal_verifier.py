"""
tests/test_formal_verifier.py
=============================================================================
Unit & Verification Test Suite for Z3 SMT Formal Theorem Prover Engine.
Phase 3 - Universal Cognitive Decomposition Engine (UCDE)
=============================================================================
"""

import unittest
from core.formal_verifier import FormalVerifier, ProofCertificate


class TestFormalVerifier(unittest.TestCase):
    def setUp(self):
        self.verifier = FormalVerifier(timeout_ms=3000)

    # =========================================================================
    # Theorem 1: Network CIDR Non-Collision
    # =========================================================================

    def test_theorem1_disjoint_subnets_pass(self):
        subnets = [
            ("auth_service", "10.0.1.0/24", [8080]),
            ("order_service", "10.0.2.0/24", [8080]),
            ("payment_service", "10.0.3.0/24", [8080]),
        ]
        cert = self.verifier.prove_network_cidr_non_collision(subnets)
        self.assertTrue(cert.is_valid)
        self.assertEqual(cert.status, "PROVED_SAT")
        self.assertIn("Verified non-collision", cert.diagnostic_summary)
        self.assertEqual(len(cert.certificate_hash), 64)

    def test_theorem1_overlapping_subnets_port_collision_fails(self):
        subnets = [
            ("gateway", "192.168.1.0/24", [443, 80]),
            ("ingress_proxy", "192.168.1.128/25", [443]),  # Overlaps in 192.168.1.128 - 192.168.1.255 on port 443
        ]
        cert = self.verifier.prove_network_cidr_non_collision(subnets)
        self.assertFalse(cert.is_valid)
        self.assertEqual(cert.status, "COUNTEREXAMPLE_FOUND")
        self.assertIsNotNone(cert.counterexample)
        self.assertIn("colliding_ip", cert.counterexample)

    # =========================================================================
    # Theorem 2: Acyclic Dependency Graph
    # =========================================================================

    def test_theorem2_valid_dag_passes(self):
        components = ["frontend", "api_gateway", "order_service", "postgres"]
        dependencies = {
            "frontend": ["api_gateway"],
            "api_gateway": ["order_service"],
            "order_service": ["postgres"],
            "postgres": [],
        }
        cert = self.verifier.prove_acyclic_dependency_graph(components, dependencies)
        self.assertTrue(cert.is_valid)
        self.assertEqual(cert.status, "PROVED_SAT")
        self.assertIn("DAG verified", cert.diagnostic_summary)

    def test_theorem2_cyclic_dependency_fails(self):
        components = ["svc_a", "svc_b", "svc_c"]
        dependencies = {
            "svc_a": ["svc_b"],
            "svc_b": ["svc_c"],
            "svc_c": ["svc_a"],  # Cycle!
        }
        cert = self.verifier.prove_acyclic_dependency_graph(components, dependencies)
        self.assertFalse(cert.is_valid)
        self.assertEqual(cert.status, "UNSAT_PROVED")
        self.assertIn("Cyclic dependency detected", cert.diagnostic_summary)

    def test_theorem2_self_loop_fails(self):
        components = ["faulty_node"]
        dependencies = {"faulty_node": ["faulty_node"]}
        cert = self.verifier.prove_acyclic_dependency_graph(components, dependencies)
        self.assertFalse(cert.is_valid)
        self.assertEqual(cert.status, "COUNTEREXAMPLE_FOUND")

    # =========================================================================
    # Theorem 3: Therac-25 Temporal Safety Invariant
    # =========================================================================

    def test_theorem3_hardware_interlock_guarantee(self):
        # Even with severe SW latency, hardware interlock provides 100% guarantee
        cert = self.verifier.prove_therac25_temporal_safety(
            t_poll_ms=500.0,
            t_sw_ms=1000.0,
            t_lock_ms=500.0,
            t_hw_actuation_ms=500.0,
            hardware_interlock_enforced=True,
        )
        self.assertTrue(cert.is_valid)
        self.assertEqual(cert.status, "PROVED_SAT")
        self.assertIn("Hardware interlock", cert.diagnostic_summary)

    def test_theorem3_race_condition_detected_without_interlock(self):
        # SW delay (200 + 400 + 500 = 1100ms) > HW actuation (1000ms)
        cert = self.verifier.prove_therac25_temporal_safety(
            t_poll_ms=200.0,
            t_sw_ms=400.0,
            t_lock_ms=500.0,
            t_hw_actuation_ms=1000.0,
            hardware_interlock_enforced=False,
        )
        self.assertFalse(cert.is_valid)
        self.assertEqual(cert.status, "COUNTEREXAMPLE_FOUND")
        self.assertIn("Therac-25 race condition possible", cert.diagnostic_summary)
        self.assertIsNotNone(cert.counterexample)

    def test_theorem3_provably_safe_software_reaction(self):
        # SW reaction (10 + 20 + 10 = 40ms) << HW actuation (1500ms)
        cert = self.verifier.prove_therac25_temporal_safety(
            t_poll_ms=10.0,
            t_sw_ms=20.0,
            t_lock_ms=10.0,
            t_hw_actuation_ms=1500.0,
            hardware_interlock_enforced=False,
        )
        self.assertTrue(cert.is_valid)
        self.assertEqual(cert.status, "UNSAT_PROVED")
        self.assertIn("strictly faster", cert.diagnostic_summary)

    # =========================================================================
    # Theorem 4: Financial Solvency & Churn Invariant
    # =========================================================================

    def test_theorem4_provably_solvent_unit_economics(self):
        # CAC = 100, ARPU = 80, Margin = 0.85, churn in [1%, 10%]
        # Min LTV = (80 * 0.85) / 0.10 = 680 => Ratio = 6.8 >= 3.0
        cert = self.verifier.prove_financial_solvency(
            cac=100.0,
            arpu_monthly=80.0,
            gross_margin=0.85,
            churn_range=(0.01, 0.10),
        )
        self.assertTrue(cert.is_valid)
        self.assertEqual(cert.status, "UNSAT_PROVED")
        self.assertIn("LTV/CAC >= 3.0 across entire churn range", cert.diagnostic_summary)

    def test_theorem4_insolvent_unit_economics_counterexample(self):
        # CAC = 400, ARPU = 40, Margin = 0.70, churn in [1%, 20%]
        # At churn = 0.15: LTV = (40 * 0.7) / 0.15 = 186.6 => Ratio = 0.46 < 3.0
        cert = self.verifier.prove_financial_solvency(
            cac=400.0,
            arpu_monthly=40.0,
            gross_margin=0.70,
            churn_range=(0.01, 0.20),
        )
        self.assertFalse(cert.is_valid)
        self.assertEqual(cert.status, "COUNTEREXAMPLE_FOUND")
        self.assertIn("Insolvency hazard", cert.diagnostic_summary)
        self.assertIsNotNone(cert.counterexample)
        self.assertLess(cert.counterexample["ltv_cac_ratio"], 3.0)

    # =========================================================================
    # Theorem 5: STRIDE Threat Coverage
    # =========================================================================

    def test_theorem5_complete_stride_coverage(self):
        endpoints = ["/api/v1/orders", "/api/v1/health"]
        mitigations = [
            {"category": "SPOOFING", "mitigation_strategy": "mTLS"},
            {"category": "TAMPERING", "mitigation_strategy": "HMAC"},
            {"category": "REPUDIATION", "mitigation_strategy": "Signed audit log"},
            {"category": "INFO_DISCLOSURE", "mitigation_strategy": "AES-GCM-256"},
            {"category": "DENIAL_OF_SERVICE", "mitigation_strategy": "Token-bucket limiter"},
            {"category": "ELEVATION_OF_PRIVILEGE", "mitigation_strategy": "Drop capabilities"},
        ]
        cert = self.verifier.prove_stride_threat_coverage(endpoints, mitigations)
        self.assertTrue(cert.is_valid)
        self.assertEqual(cert.status, "PROVED_SAT")
        self.assertIn("Full STRIDE coverage formally proved", cert.diagnostic_summary)

    def test_theorem5_missing_stride_category_fails(self):
        endpoints = ["/api/v1/orders"]
        mitigations = [
            {"category": "SPOOFING", "mitigation_strategy": "mTLS"},
            {"category": "TAMPERING", "mitigation_strategy": "HMAC"},
            # Missing REPUDIATION, INFO_DISCLOSURE, DoS, EoP
        ]
        cert = self.verifier.prove_stride_threat_coverage(endpoints, mitigations)
        self.assertFalse(cert.is_valid)
        self.assertEqual(cert.status, "COUNTEREXAMPLE_FOUND")
        self.assertIn("REPUDIATION", cert.counterexample["missing_threat_categories"])


if __name__ == "__main__":
    unittest.main()
