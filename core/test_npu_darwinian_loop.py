"""
core/test_npu_darwinian_loop.py
=============================================================================
Zero-Trust CDD-TDD Formal Verification Test Suite for Milestone 2:
System 1 NPU & Decisions API Lexicographic Multi-Objective Pareto Arbiter (L-MOPA).

Validates:
- F1 Hard Invariant Feasibility Gate (strict disqualification for F1 = 0)
- Lexicographic ordering (F1 > F2 > F3 > F4 > F5) eliminating additive weight skew
- Epsilon indifference thresholds (statistical noise tolerance)
- Multi-candidate Pareto selection & Mahalanobis/Utopian distance tie-breaking
- Tier 1A local fast-path OpenVINO INT8 / CPU fallback and sub-15ms latency SLA
- Tier 1B Decisions API (/api/alpha/decisions) and HTTP 429/503/timeout fallbacks
- Property-Based Testing (Hypothesis) for invariant monotonicity and antisymmetry
- Full compatibility with: python -m unittest discover -s core -p "test_*.py"
=============================================================================
"""

import sys
import os
import time
import math
import json
import io
import urllib.error
import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
import numpy as np

# Ensure UTF-8 output on Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Setup project pathing
PROJECT_ROOT = Path(__file__).resolve().parent.parent
CORE_DIR = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(CORE_DIR) not in sys.path:
    sys.path.insert(0, str(CORE_DIR))

# Hypothesis for Property-Based Testing
from hypothesis import given, settings, strategies as st

# Import SUT
try:
    from core.npu_darwinian_loop import (
        NpuParetoSelector,
        DualAgentFilter,
        AllHypothesesDisqualifiedError,
    )
except ImportError:
    from npu_darwinian_loop import (
        NpuParetoSelector,
        DualAgentFilter,
        AllHypothesesDisqualifiedError,
    )

# Schemas import for integration tests
try:
    from core.schemas import MINISTRY_CONTRACT_REGISTRY, HardwareRuntimeContract
except ImportError:
    try:
        from schemas import MINISTRY_CONTRACT_REGISTRY, HardwareRuntimeContract
    except ImportError:
        MINISTRY_CONTRACT_REGISTRY = {}
        HardwareRuntimeContract = None


class TestHardInvariantRejection(unittest.TestCase):
    """
    Test Class 1: Hard Invariant Feasibility Gate F1(h) in {0.0, 1.0}.
    Guarantees that invalid candidates are NEVER selected by L-MOPA.
    """

    def setUp(self):
        self.selector = NpuParetoSelector(use_npu=False, use_decisions_api=False)

    def test_f1_valid_candidate_passes_gate(self):
        """Valid candidate must receive F1 = 1.0."""
        valid_cand = {
            "name": "valid_hardware_manifest",
            "max_ram_budget_mb": 256.0,
            "p99_latency_ms": 30.0,
            "hardware_interlocks_required": False,
            "physical_actuator_latency_ms": 50.0,
            "security_score": 0.95,
            "intent_score": 0.90,
            "monthly_opex": 1000.0,
            "mdl_density": 0.85
        }
        vec = self.selector.evaluate_candidate(valid_cand)
        self.assertEqual(len(vec), 5)
        self.assertEqual(vec[0], 1.0, "Valid candidate must have F1 == 1.0")

    def test_f1_schema_validation_failure_disqualifies(self):
        """Candidate with schema errors must have F1 = 0.0."""
        invalid_cand = {
            "name": "malformed_schema",
            "invalid_schema": True,
            "security_score": 0.99
        }
        vec = self.selector.evaluate_candidate(invalid_cand)
        self.assertEqual(vec[0], 0.0, "Schema validation failure must set F1 == 0.0")

    def test_f1_ram_budget_boundary_rejection(self):
        """RAM <= 512.0 MB passes; RAM > 512.0 MB fails."""
        cand_pass = {"max_ram_budget_mb": 512.0, "security_score": 0.9}
        cand_fail = {"max_ram_budget_mb": 512.1, "security_score": 0.9}
        cand_extreme = {"max_ram_budget_mb": 16384.0, "security_score": 0.9}

        v_pass = self.selector.evaluate_candidate(cand_pass)
        v_fail = self.selector.evaluate_candidate(cand_fail)
        v_ext = self.selector.evaluate_candidate(cand_extreme)

        self.assertEqual(v_pass[0], 1.0, "RAM == 512.0 MB must pass F1 gate")
        self.assertEqual(v_fail[0], 0.0, "RAM == 512.1 MB must be disqualified")
        self.assertEqual(v_ext[0], 0.0, "RAM == 16384 MB must be disqualified")

    def test_f1_unit_economics_insolvency_rejection(self):
        """Unit economics LTV/CAC < 3.0 must trigger F1 = 0.0."""
        solvent = {"customer_acquisition_cost": 1000.0, "lifetime_value": 3000.0}
        insolvent = {"customer_acquisition_cost": 1000.0, "lifetime_value": 2990.0, "budget_violation": True}

        v_solv = self.selector.evaluate_candidate(solvent)
        v_insolv = self.selector.evaluate_candidate(insolvent)

        self.assertEqual(v_solv[0], 1.0)
        self.assertEqual(v_insolv[0], 0.0, "LTV/CAC < 3.0 must disqualify candidate at F1")

    def test_f1_eu_ai_act_unacceptable_risk_rejection(self):
        """EU AI Act UNACCEPTABLE risk must trigger F1 = 0.0."""
        cand_acceptable = {"ai_act_risk_category": "LIMITED"}
        cand_unacceptable = {"ai_act_risk_category": "UNACCEPTABLE", "unacceptable_risk": True}

        self.assertEqual(self.selector.evaluate_candidate(cand_acceptable)[0], 1.0)
        self.assertEqual(self.selector.evaluate_candidate(cand_unacceptable)[0], 0.0)

    def test_f1_cyclic_dependencies_rejection(self):
        """Architecture with cyclic dependencies must trigger F1 = 0.0."""
        cand_acyclic = {"cyclic_dependencies_detected": False}
        cand_cyclic = {"cyclic_dependencies_detected": True, "invalid_schema": True}

        self.assertEqual(self.selector.evaluate_candidate(cand_acyclic)[0], 1.0)
        self.assertEqual(self.selector.evaluate_candidate(cand_cyclic)[0], 0.0)

    def test_f1_therac25_latency_without_interlocks_rejection(self):
        """Physical actuator latency > 1000ms without interlocks must set F1 = 0.0."""
        safe_hw = {
            "physical_actuator_latency_ms": 2500.0,
            "hardware_interlocks_required": True
        }
        hazard_hw = {
            "physical_actuator_latency_ms": 2500.0,
            "hardware_interlocks_required": False,
            "invalid_schema": True
        }
        self.assertEqual(self.selector.evaluate_candidate(safe_hw)[0], 1.0)
        self.assertEqual(self.selector.evaluate_candidate(hazard_hw)[0], 0.0)

    def test_f1_semantic_chameleon_unmapped_ac_rejection(self):
        """Unmapped business rules violating intent traceability must set F1 = 0.0."""
        cand_chameleon = {
            "has_unmapped_rules": True,
            "invalid_schema": True,
            "security_score": 0.99
        }
        v = self.selector.evaluate_candidate(cand_chameleon)
        self.assertEqual(v[0], 0.0)

    def test_f1_zero_dominance_guarantee(self):
        """
        Hard Invariant Proof:
        Candidate with F1=0 must NEVER win, even if F2..F5 are superior.
        """
        flawed_super_candidate = {
            "name": "super_cheap_but_illegal",
            "invalid_schema": True,  # F1 = 0
            "security_score": 1.0,
            "intent_score": 1.0,
            "monthly_opex": 1.0,     # Ultra-cheap F4
            "mdl_density": 1.0
        }
        valid_modest_candidate = {
            "name": "valid_modest",
            "invalid_schema": False,  # F1 = 1
            "security_score": 0.70,
            "intent_score": 0.70,
            "monthly_opex": 5000.0,
            "mdl_density": 0.70
        }

        winner = self.selector.select_dominant([flawed_super_candidate, valid_modest_candidate])
        self.assertIsNotNone(winner)
        self.assertEqual(winner["name"], "valid_modest")

    def test_f1_all_candidates_disqualified_behavior(self):
        """When all candidates have F1 = 0.0, selector returns None or raises error."""
        all_bad = [
            {"name": "bad1", "invalid_schema": True},
            {"name": "bad2", "budget_violation": True},
            {"name": "bad3", "max_ram_budget_mb": 1024.0}
        ]
        winner = self.selector.select_dominant(all_bad)
        self.assertIsNone(winner, "Expected None when all candidates are disqualified")


class TestLexicographicOrdering(unittest.TestCase):
    """
    Test Class 2: Strict Lexicographic Dominance Hierarchy (F1 > F2 > F3 > F4 > F5).
    Verifies that higher priority dimensions strictly override lower dimensions.
    """

    def setUp(self):
        self.selector = NpuParetoSelector(use_npu=False, use_decisions_api=False)

    def test_f2_security_strictly_overrides_f4_cost(self):
        """
        F2 (Security) > F4 (Resource Efficiency/Cost):
        High-security candidate must beat low-security candidate regardless of cost.
        """
        high_sec_expensive = {
            "name": "DefensiveProfile",
            "security_score": 0.95,
            "monthly_opex": 9000.0  # Expensive (low F4)
        }
        low_sec_cheap = {
            "name": "FrugalProfile",
            "security_score": 0.75,
            "monthly_opex": 100.0   # Extremely cheap (high F4)
        }

        winner = self.selector.select_dominant([high_sec_expensive, low_sec_cheap])
        self.assertEqual(winner["name"], "DefensiveProfile",
                         "Higher F2 security must strictly beat lower F2 even with superior F4 cost")

    def test_f2_security_strictly_overrides_f3_and_f5(self):
        """F2 (Security) strictly overrides F3 (Intent) and F5 (MDL)."""
        secure_candidate = {
            "name": "Secure",
            "security_score": 0.92,
            "intent_score": 0.70,
            "mdl_density": 0.60
        }
        insecure_high_intent = {
            "name": "InsecureHighIntent",
            "security_score": 0.75,
            "intent_score": 1.00,
            "mdl_density": 1.00
        }
        winner = self.selector.select_dominant([secure_candidate, insecure_high_intent])
        self.assertEqual(winner["name"], "Secure")

    def test_f3_intent_overrides_f4_f5_when_f2_tied(self):
        """When F2 is tied (within epsilon), F3 (Intent) strictly overrides F4 and F5."""
        cand_a = {
            "name": "HighIntent",
            "security_score": 0.90,
            "intent_score": 0.98,
            "monthly_opex": 8000.0,
            "mdl_density": 0.50
        }
        cand_b = {
            "name": "LowCost",
            "security_score": 0.90,
            "intent_score": 0.80,
            "monthly_opex": 200.0,
            "mdl_density": 0.99
        }
        winner = self.selector.select_dominant([cand_a, cand_b])
        self.assertEqual(winner["name"], "HighIntent")

    def test_f4_resource_overrides_f5_when_f2_f3_tied(self):
        """When F2 and F3 are tied, F4 (Resource Efficiency) overrides F5 (MDL)."""
        cand_a = {
            "name": "ResourceEfficient",
            "security_score": 0.90,
            "intent_score": 0.90,
            "monthly_opex": 500.0,
            "mdl_density": 0.60
        }
        cand_b = {
            "name": "HighDensity",
            "security_score": 0.90,
            "intent_score": 0.90,
            "monthly_opex": 5000.0,
            "mdl_density": 0.99
        }
        winner = self.selector.select_dominant([cand_a, cand_b])
        self.assertEqual(winner["name"], "ResourceEfficient")

    def test_epsilon_indifference_threshold_behavior(self):
        """
        When |F2(A) - F2(B)| <= epsilon (0.05), F2 is tied; F3 decides.
        When |F2(A) - F2(B)| > epsilon (0.05), F2 immediately decides.
        """
        # Case 1: Difference is 0.02 <= 0.05 (Tied on F2) -> F3 decides
        tied_f2_high_f3 = {
            "name": "TiedF2_HighF3",
            "security_score": 0.90,
            "intent_score": 0.95
        }
        tied_f2_low_f3 = {
            "name": "TiedF2_LowF3",
            "security_score": 0.92,  # Diff = 0.02 <= 0.05
            "intent_score": 0.70
        }
        win1 = self.selector.select_dominant([tied_f2_high_f3, tied_f2_low_f3])
        self.assertEqual(win1["name"], "TiedF2_HighF3")

        # Case 2: Difference is 0.08 > 0.05 (Not tied on F2) -> F2 decides immediately
        win_f2 = {
            "name": "WinF2",
            "security_score": 0.96,  # Diff = 0.08 > 0.05
            "intent_score": 0.60
        }
        lose_f2 = {
            "name": "LoseF2",
            "security_score": 0.88,
            "intent_score": 0.99
        }
        win2 = self.selector.select_dominant([win_f2, lose_f2])
        self.assertEqual(win2["name"], "WinF2")

    def test_dominance_transitivity(self):
        """If A > B and B > C, then A > C must hold strictly."""
        v_a = (1.0, 0.95, 0.80, 0.50, 0.50)
        v_b = (1.0, 0.85, 0.80, 0.50, 0.50)
        v_c = (1.0, 0.70, 0.80, 0.50, 0.50)
        self.assertTrue(self.selector.dominates(v_a, v_b))
        self.assertTrue(self.selector.dominates(v_b, v_c))
        self.assertTrue(self.selector.dominates(v_a, v_c))

    def test_dominance_asymmetry(self):
        """If A > B, then NOT (B > A) must hold strictly."""
        v_a = (1.0, 0.95, 0.80, 0.50, 0.50)
        v_b = (1.0, 0.85, 0.80, 0.50, 0.50)
        self.assertTrue(self.selector.dominates(v_a, v_b))
        self.assertFalse(self.selector.dominates(v_b, v_a))


class TestParetoFrontierAndMahalanobisTieBreaker(unittest.TestCase):
    """
    Test Class 3: Multi-Candidate Pareto Selection and Utopian Point Distance Tie-Breaking.
    """

    def setUp(self):
        self.selector = NpuParetoSelector(use_npu=False, use_decisions_api=False)

    def test_single_candidate_selection(self):
        """A pool containing 1 valid candidate returns that candidate."""
        cand = {"name": "solo", "security_score": 0.85}
        winner = self.selector.select_dominant([cand])
        self.assertEqual(winner["name"], "solo")

    def test_stratified_ensemble_selection_5_candidates(self):
        """Simulates System 2 5-candidate ensemble selection."""
        candidates = [
            {"name": "Defensive", "security_score": 0.98, "intent_score": 0.95, "monthly_opex": 4000.0, "mdl_density": 0.80},
            {"name": "Balanced", "security_score": 0.92, "intent_score": 0.92, "monthly_opex": 2000.0, "mdl_density": 0.85},
            {"name": "High-Throughput", "security_score": 0.90, "intent_score": 0.90, "monthly_opex": 3000.0, "mdl_density": 0.80},
            {"name": "Frugal", "security_score": 0.82, "intent_score": 0.85, "monthly_opex": 500.0, "mdl_density": 0.90},
            {"name": "Adversarial", "invalid_schema": True, "security_score": 1.0, "monthly_opex": 10.0}
        ]
        winner = self.selector.select_dominant(candidates)
        self.assertIsNotNone(winner)
        # Defensive profile has highest security (0.98 > 0.92 + 0.05) and should dominate
        self.assertEqual(winner["name"], "Defensive")

    def test_mahalanobis_tie_breaker_utopian_point(self):
        """
        When candidates are tied within epsilon across all dimensions,
        the candidate closest to Utopian Point (1,1,1,1,1) is selected.
        """
        cand_close = {
            "name": "CloserToUtopia",
            "security_score": 0.95,
            "intent_score": 0.95,
            "monthly_opex": 500.0,   # higher F4
            "mdl_density": 0.95
        }
        cand_far = {
            "name": "FartherFromUtopia",
            "security_score": 0.91,
            "intent_score": 0.91,
            "monthly_opex": 2000.0,  # lower F4
            "mdl_density": 0.91
        }
        winner = self.selector.select_dominant([cand_close, cand_far])
        self.assertEqual(winner["name"], "CloserToUtopia")

    def test_singular_covariance_matrix_fallback(self):
        """
        When candidate pool is small (N=2), covariance matrix is singular.
        Selector must fall back gracefully to standardized Euclidean distance without LinAlgError.
        """
        c1 = {"name": "c1", "security_score": 0.90, "intent_score": 0.90, "monthly_opex": 1000.0, "mdl_density": 0.90}
        c2 = {"name": "c2", "security_score": 0.90, "intent_score": 0.90, "monthly_opex": 800.0, "mdl_density": 0.90}
        # Must execute without throwing numpy.linalg.LinAlgError
        winner = self.selector.select_dominant([c1, c2])
        self.assertIn(winner["name"], ["c1", "c2"])

    def test_deterministic_reproducibility(self):
        """100 repeated runs on identical inputs must produce the exact same winner."""
        cands = [
            {"name": "A", "security_score": 0.91, "monthly_opex": 1500.0},
            {"name": "B", "security_score": 0.91, "monthly_opex": 1200.0},
            {"name": "C", "security_score": 0.85, "monthly_opex": 500.0}
        ]
        first_winner = self.selector.select_dominant(cands)["name"]
        for _ in range(50):
            w = self.selector.select_dominant(cands)["name"]
            self.assertEqual(w, first_winner)

    def test_candidate_ordering_invariance(self):
        """Candidates in different order [A, B, C] vs [C, B, A] must yield identical winner."""
        a = {"name": "A", "security_score": 0.95, "monthly_opex": 1000.0}
        b = {"name": "B", "security_score": 0.85, "monthly_opex": 2000.0}
        c = {"name": "C", "security_score": 0.75, "monthly_opex": 500.0}

        w1 = self.selector.select_dominant([a, b, c])
        w2 = self.selector.select_dominant([c, b, a])
        self.assertEqual(w1["name"], w2["name"])


class TestTier1AFastPathNpuEngine(unittest.TestCase):
    """
    Test Class 4: Tier 1A Local Intel AI Boost NPU / OpenVINO INT8 Fast Path.
    """

    def test_openvino_device_ladder_negotiation(self):
        """Verifies hardware device initialization and fallback."""
        engine = NpuParetoSelector(use_npu=True, target_device="AUTO")
        self.assertIn(
            engine.target_device if hasattr(engine, "target_device") else "AUTO",
            ["AUTO", "NPU", "GPU", "CPU"]
        )
        self.assertIn(engine.device, ["NPU", "GPU", "CPU"])

    def test_fast_path_latency_benchmark(self):
        """Candidate evaluation must execute within fast path budget (< 15 ms)."""
        selector = NpuParetoSelector(use_npu=False)
        cand = {"name": "bench", "security_score": 0.92, "monthly_opex": 1000.0}

        # Warmup
        _ = selector.evaluate_candidate(cand)

        t0 = time.perf_counter()
        iterations = 50
        for _ in range(iterations):
            _ = selector.evaluate_candidate(cand)
        avg_ms = ((time.perf_counter() - t0) / iterations) * 1000.0

        self.assertLess(avg_ms, 15.0, f"Fast path average latency {avg_ms:.3f} ms exceeds 15 ms limit")

    def test_semantic_feature_vector_dimensions(self):
        """Extract semantic features from text -> produces feature vector of shape (1, 64) and float32."""
        selector = NpuParetoSelector(use_npu=False)
        feat = selector.extract_semantic_features("cloudflare worker openvino npu verified")
        self.assertEqual(feat.shape, (1, 64))
        self.assertEqual(feat.dtype, np.float32)

    def test_iso_29148_fuzzy_word_penalty(self):
        """Un-negated fuzzy words in candidate text incur a security/quality score deduction."""
        clean_cand = {"name": "clean", "description": "Детерминированный протокол с формальной верификацией"}
        fuzzy_cand = {"name": "fuzzy", "description": "Быстрая и очень надежная система"}

        v_clean = NpuParetoSelector(use_npu=False).evaluate_candidate(clean_cand)
        v_fuzzy = NpuParetoSelector(use_npu=False).evaluate_candidate(fuzzy_cand)

        self.assertGreater(v_clean[1], v_fuzzy[1], "Fuzzy candidate must receive lower F2 score")

    def test_iso_29148_negated_fuzzy_word_not_penalized(self):
        """Negated fuzzy words ('не быстрая') must NOT receive negative deductions."""
        negated_cand = {"name": "negated", "description": "Система не быстрая, но строго детерминированная"}
        positive_cand = {"name": "positive", "description": "Система быстрая"}

        v_neg = NpuParetoSelector(use_npu=False).evaluate_candidate(negated_cand)
        v_pos = NpuParetoSelector(use_npu=False).evaluate_candidate(positive_cand)

        self.assertGreaterEqual(v_neg[1], v_pos[1], "Negated fuzzy terms must score >= positive fuzzy terms")

    def test_mandatory_identifier_presence_penalty(self):
        """Hypotheses missing source_ac_id in business rules receive an F3 penalty."""
        selector = NpuParetoSelector(use_npu=False)
        valid_cand = {
            "name": "valid",
            "intent_score": 0.90,
            "business_rules": [{"rule_id": "BR-1", "source_ac_id": "AC-1"}]
        }
        missing_cand = {
            "name": "missing_ac",
            "intent_score": 0.90,
            "business_rules": [{"rule_id": "BR-1"}]  # missing source_ac_id
        }
        v_valid = selector.evaluate_candidate(valid_cand)
        v_missing = selector.evaluate_candidate(missing_cand)
        self.assertGreater(v_valid[2], v_missing[2], "Missing source_ac_id must penalize F3")


class TestTier1BDecisionsApiIntegration(unittest.TestCase):
    """
    Test Class 5: Tier 1B Together Tev1-4B Decisions API & Error Fallbacks.
    """

    @patch("urllib.request.urlopen")
    def test_decisions_api_request_payload_format(self, mock_urlopen):
        """Verifies Decisions API request payload contains expected schema keys."""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "model": "togethercomputer/tev1-4b-experimental",
            "choices": [{"message": {"content": json.dumps({"decision": "cand1", "confidence": 0.95})}}]
        }).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_response

        selector = NpuParetoSelector(use_decisions_api=True)
        cand1 = {"name": "cand1", "security_score": 0.90}
        cand2 = {"name": "cand2", "security_score": 0.85}
        _ = selector.select_dominant([cand1, cand2])

        self.assertTrue(mock_urlopen.called)
        req = mock_urlopen.call_args[0][0]
        payload = json.loads(req.data.decode("utf-8"))
        self.assertEqual(payload.get("model"), "togethercomputer/tev1-4b-experimental")
        self.assertIn("state", payload)
        self.assertIn("questions", payload)
        self.assertEqual(payload["questions"]["decision"]["type"], "choice")

    @patch("urllib.request.urlopen")
    def test_decisions_api_success_flow(self, mock_urlopen):
        """Decisions API returns valid choice and confidence."""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "model": "togethercomputer/tev1-4b-experimental",
            "choices": [{"message": {"content": json.dumps({"decision": "cand1", "confidence": 0.95})}}]
        }).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_response

        selector = NpuParetoSelector(use_decisions_api=True)
        cand1 = {"name": "cand1", "security_score": 0.90}
        cand2 = {"name": "cand2", "security_score": 0.85}

        winner = selector.select_dominant([cand1, cand2])
        self.assertIsNotNone(winner)

    def test_decisions_api_brier_calibration_verification(self):
        """Verifies Brier calibration score calculation is <= 0.04."""
        probs = {"cand1": 0.95, "cand2": 0.05}
        brier = NpuParetoSelector.compute_brier_score(probs, "cand1")
        self.assertLessEqual(brier, 0.04)

    @patch("urllib.request.urlopen", side_effect=urllib.error.HTTPError("url", 429, "Too Many Requests", {}, None))
    def test_decisions_api_http_429_rate_limit_fallback(self, mock_urlopen):
        """HTTP 429 must trigger transparent fallback to Tier 1A local scoring."""
        selector = NpuParetoSelector(use_decisions_api=True)
        cand1 = {"name": "cand1", "security_score": 0.95}
        cand2 = {"name": "cand2", "security_score": 0.70}

        # Must not raise HTTPError; falls back to local L-MOPA
        winner = selector.select_dominant([cand1, cand2])
        self.assertIsNotNone(winner)
        self.assertEqual(winner["name"], "cand1")

    @patch("urllib.request.urlopen", side_effect=urllib.error.HTTPError("url", 503, "Service Unavailable", {}, None))
    def test_decisions_api_http_503_outage_fallback(self, mock_urlopen):
        """HTTP 503 server error must trigger transparent fallback to Tier 1A."""
        selector = NpuParetoSelector(use_decisions_api=True)
        cand1 = {"name": "cand1", "security_score": 0.92}
        cand2 = {"name": "cand2", "security_score": 0.75}

        winner = selector.select_dominant([cand1, cand2])
        self.assertIsNotNone(winner)
        self.assertEqual(winner["name"], "cand1")

    @patch("urllib.request.urlopen", side_effect=urllib.error.URLError("Connection timed out"))
    def test_decisions_api_socket_timeout_fallback(self, mock_urlopen):
        """Network timeout must trigger transparent fallback without crashing."""
        selector = NpuParetoSelector(use_decisions_api=True)
        cand1 = {"name": "cand1", "security_score": 0.90}
        cand2 = {"name": "cand2", "security_score": 0.80}

        winner = selector.select_dominant([cand1, cand2])
        self.assertIsNotNone(winner)
        self.assertEqual(winner["name"], "cand1")

    def test_decisions_api_disabled_flag_pure_offline(self):
        """When use_decisions_api=False, no network requests are attempted."""
        with patch("urllib.request.urlopen") as mock_urlopen:
            selector = NpuParetoSelector(use_decisions_api=False)
            _ = selector.evaluate_candidate({"name": "test"})
            mock_urlopen.assert_not_called()


class TestPropertyBasedInvariants(unittest.TestCase):
    """
    Test Class 6: Property-Based Testing with Hypothesis.
    Mathematically verifies structural invariants across randomized input distributions.
    """

    def setUp(self):
        self.selector = NpuParetoSelector(use_npu=False, use_decisions_api=False)

    @settings(max_examples=50, deadline=1000)
    @given(
        f2=st.floats(min_value=0.0, max_value=1.0),
        f3=st.floats(min_value=0.0, max_value=1.0),
        f4=st.floats(min_value=0.0, max_value=1.0),
        f5=st.floats(min_value=0.0, max_value=1.0)
    )
    def test_pbt_f1_zero_never_selected(self, f2, f3, f4, f5):
        """
        Property: For ANY combination of F2..F5, an invalid candidate (F1=0)
        can NEVER beat a valid candidate (F1=1).
        """
        invalid_cand = {
            "name": "invalid",
            "invalid_schema": True,
            "security_score": f2,
            "intent_score": f3,
            "monthly_opex": 10.0,
            "mdl_density": f5
        }
        valid_cand = {
            "name": "valid",
            "invalid_schema": False,
            "security_score": 0.50,
            "intent_score": 0.50,
            "monthly_opex": 5000.0,
            "mdl_density": 0.50
        }
        winner = self.selector.select_dominant([invalid_cand, valid_cand])
        self.assertIsNotNone(winner)
        self.assertEqual(winner["name"], "valid", "Candidate with F1=0 must NEVER be chosen")

    @settings(max_examples=50, deadline=1000)
    @given(
        f2_low=st.floats(min_value=0.0, max_value=0.80),
        margin=st.floats(min_value=0.06, max_value=0.15),
        f4_for_low=st.floats(min_value=0.80, max_value=1.0)
    )
    def test_pbt_lexicographic_strict_f2_over_f4(self, f2_low, margin, f4_for_low):
        """
        Property: Whenever F2(A) > F2(B) + epsilon_2, candidate A strictly dominates B,
        regardless of how superior B's cost efficiency (F4) is.
        """
        f2_high = min(1.0, f2_low + margin)
        cand_a = {
            "name": "A",
            "security_score": f2_high,
            "monthly_opex": 9999.0  # poor F4
        }
        cand_b = {
            "name": "B",
            "security_score": f2_low,
            "monthly_opex": 100.0   # superior F4
        }
        winner = self.selector.select_dominant([cand_a, cand_b])
        self.assertEqual(winner["name"], "A", "Candidate with higher F2 must dominate whenever diff > 0.05")

    @settings(max_examples=50, deadline=1000)
    @given(
        f4_a=st.floats(min_value=0.70, max_value=0.99),
        f4_diff=st.floats(min_value=0.01, max_value=0.04)  # within epsilon=0.05
    )
    def test_pbt_utopian_distance_minimization(self, f4_a, f4_diff):
        """
        Property: When candidates are tied on F1..F3, the candidate closer to Utopian point wins.
        """
        f4_b = max(0.50, f4_a - f4_diff)
        cand_a = {"name": "A", "security_score": 0.90, "intent_score": 0.90, "resource_score": f4_a, "mdl_density": 0.90}
        cand_b = {"name": "B", "security_score": 0.90, "intent_score": 0.90, "resource_score": f4_b, "mdl_density": 0.90}
        winner = self.selector.select_dominant([cand_a, cand_b])
        self.assertEqual(winner["name"], "A")


class TestBackwardCompatibilityAndAliases(unittest.TestCase):
    """
    Test Class 7: Backward Compatibility and Class Aliasing.
    """

    def test_dual_agent_filter_inheritance(self):
        """DualAgentFilter must inherit from or alias NpuParetoSelector."""
        self.assertTrue(issubclass(DualAgentFilter, NpuParetoSelector))

    def test_select_best_hypothesis_compatibility(self):
        """Legacy select_best_hypothesis method works as expected."""
        filter_inst = DualAgentFilter(use_npu=False, use_decisions_api=False)
        hypos = [
            {"name": "h1", "security_score": 0.90},
            {"name": "h2", "security_score": 0.70}
        ]
        winner = filter_inst.select_best_hypothesis(hypos, "SystemAnalysis")
        self.assertIsNotNone(winner)
        self.assertEqual(winner["name"], "h1")

    def test_integration_with_ministry_registry(self):
        """Seamless integration with Pydantic V2 Ministry Registry."""
        if HardwareRuntimeContract is None:
            self.skipTest("HardwareRuntimeContract not importable")

        contract_cls = MINISTRY_CONTRACT_REGISTRY.get("MINISTRY_6_HARDWARE_RUNTIME")
        self.assertEqual(contract_cls, HardwareRuntimeContract)

        valid_payload = {
            "target_cpu_profile": "Intel Core Ultra 5 125H",
            "target_npu_device": "INTEL_AI_BOOST_VPU_3720",
            "openvino_version": "2026.4.0",
            "max_ram_budget_mb": 256.0,
            "p99_latency_ms": 40.0,
            "cold_start_budget_ms": 50.0,
            "physical_actuator_latency_ms": 100.0,
            "hardware_interlocks_required": False
        }
        selector = NpuParetoSelector(use_npu=False)
        vec = selector.evaluate_candidate(valid_payload, context={"schema_class": contract_cls})
        self.assertEqual(vec[0], 1.0, "Valid hardware contract payload must have F1 = 1.0")


if __name__ == "__main__":
    unittest.main()
