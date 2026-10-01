"""
Unit & Stress Tests for Pre-Mortem Wave Plan Safeguards (Waves 1-6)
Verifies:
- Wave 1: Augmented Chebyshev ASF fallback under singular covariance matrices.
- Wave 2: Monotonic Epoch Fencing Tokens preventing Split-Brain in DAG FSM.
- Wave 3: FSTEC BDU Threat code regex and auto-population.
- Wave 4: Denial-of-Wallet budget guard ($5.00 limit).
- Wave 6: Steganographic Unicode character stripping (Zero-Width spaces/injectors).
"""

import math
import sys
import unittest
from pathlib import Path

# Fix Windows encoding
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.npu_darwinian_loop import NpuParetoSelector
from core.ministries.nodes import SecurityQuarantineManager
from core.orchestrator import DagOrchestrator, GlobalBudgetExhaustedError, NodeState
from core.schemas.security import StrideThreat, SecurityPolicyContract, DEFAULT_STRIDE_TO_UBI


class TestPreMortemSafeguards(unittest.TestCase):

    def test_wave1_augmented_chebyshev_asf_singularity(self):
        """Wave 1: Evaluates that completely collinear/singular vectors do not crash or produce NaN."""
        selector = NpuParetoSelector()
        
        # 3 identical candidate vectors -> Covariance is all zeros (singular det = 0)
        singular_vectors = [
            (1.0, 0.8, 0.8, 0.8, 0.8),
            (1.0, 0.8, 0.8, 0.8, 0.8),
            (1.0, 0.8, 0.8, 0.8, 0.8)
        ]
        
        distances = selector._compute_utopian_distances(singular_vectors)
        self.assertEqual(len(distances), 3)
        for d in distances:
            self.assertFalse(math.isnan(d) or math.isinf(d))
            self.assertGreater(d, 0.0)

        # Directly test the static Wierzbicki ASF calculation
        asf = selector.compute_augmented_chebyshev_asf((1.0, 0.9, 0.9, 0.9, 0.9))
        self.assertAlmostEqual(asf, 0.1004, places=3)

    def test_wave2_fencing_token_monotonicity(self):
        """Wave 2: Evaluates that each state transition increments epoch fencing tokens."""
        orchestrator = DagOrchestrator(use_mock=True)
        initial_token = orchestrator.fencing_token
        
        orchestrator._sync_fsm_state(1, NodeState.STATE_INPUT_VALIDATION, "Validating input")
        token_after_1 = orchestrator.fencing_token
        self.assertGreater(token_after_1, initial_token)
        
        orchestrator._sync_fsm_state(1, NodeState.STATE_SYSTEM2_GENERATE, "Generating")
        token_after_2 = orchestrator.fencing_token
        self.assertGreater(token_after_2, token_after_1)

    def test_wave3_fstec_bdu_threat_mapping(self):
        """Wave 3: Evaluates that all STRIDE categories automatically receive valid УБИ codes."""
        for cat, ubi in DEFAULT_STRIDE_TO_UBI.items():
            threat = StrideThreat(
                category=cat,
                target_component="TestComponent",
                mitigation_strategy="Valid 10+ characters mitigation text"
            )
            self.assertEqual(threat.fstec_ubi_code, ubi)
            self.assertTrue(threat.fstec_ubi_code.startswith("УБИ."))

    def test_wave4_denial_of_wallet_guard(self):
        """Wave 4: Evaluates that exceeding $5.00 API budget triggers GlobalBudgetExhaustedError."""
        orchestrator = DagOrchestrator(use_mock=True)
        
        # Spend $4.50 -> Should succeed
        orchestrator.record_api_cost(4.50)
        self.assertEqual(orchestrator.current_estimated_cost_usd, 4.50)
        
        # Spend another $0.60 -> Total $5.10 > $5.00 -> Must raise
        with self.assertRaises(GlobalBudgetExhaustedError):
            orchestrator.record_api_cost(0.60)

    def test_wave6_steganographic_unicode_stripping(self):
        """Wave 6: Evaluates that hidden zero-width spaces are stripped and flagged."""
        # Inject zero-width space (\u200B) and zero-width joiner (\u200D) into prompt
        malicious_input = "Создать\u200B систему\u200D управления"
        
        quarantined, has_injection, violations = SecurityQuarantineManager.sanitize_and_quarantine(malicious_input)
        
        self.assertTrue(has_injection)
        self.assertIn("STEGANOGRAPHIC_UNICODE_CHARACTERS", violations)
        self.assertNotIn("\u200B", quarantined)
        self.assertNotIn("\u200D", quarantined)
        self.assertIn("Создать систему управления", quarantined)


if __name__ == "__main__":
    unittest.main()
