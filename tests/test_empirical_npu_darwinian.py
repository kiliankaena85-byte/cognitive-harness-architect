"""
tests/test_empirical_npu_darwinian.py
=============================================================================
Empirical Challenger Test Harness for Milestone 2:
System 1 NPU & Decisions API Lexicographic Multi-Objective Pareto Arbiter (L-MOPA).

Adversarial probes & stress testing:
1. Strict F1=0 Disqualification Stress Tests:
   - Candidate with F1=0.0 and perfect F2=1.0, F3=1.0, F4=1.0, F5=1.0 MUST NEVER
     be selected over an inferior valid candidate (F1=1.0, F2=0.1, F3=0.1, F4=0.1, F5=0.1).
   - Probed across all 10 invariant violation vectors.
   - Probed with direct 'f1' / 'F1' vector keys.
2. Non-Additive Dominance Verification:
   - High F2 strictly dominates low F2 regardless of how high F4 / F5 are.
   - Non-additive lexicographic hierarchy (F1 > F2 > F3 > F4 > F5).
   - Strict resistance to additive weight compensation.
3. Epsilon Indifference Boundary Probes:
   - F2 epsilon threshold (0.05) exact boundary tests.
   - F3 epsilon threshold (0.02) exact boundary tests.
4. Adversarial Edge Cases & Vulnerability Mining:
   - NaN injection / poisoning in objective scores.
   - Infinite and negative numerical values.
   - Empty lists and 100% disqualified pools.
   - SHA-256 canonical tie-breaking determinism.
=============================================================================
"""

import sys
import math
import json
import time
import unittest
from pathlib import Path
from typing import Any, Dict, List, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.npu_darwinian_loop import (
    NpuParetoSelector,
    DualAgentFilter,
    AllHypothesesDisqualifiedError
)
from core.schemas import (
    HardwareRuntimeContract,
    FinanceBudgetContract,
    LegalComplianceContract,
    SecurityPolicyContract,
    SystemAnalysisContract,
    StrategyCJMContract,
    VVQualityContract,
)


class TestEmpiricalStrictF1Disqualification(unittest.TestCase):
    """
    Stress-tests the F1=0 Hard Invariants Feasibility Gate.
    A candidate with F1=0.0 and perfect F2..F5=1.0 MUST NEVER be selected
    over an inferior valid candidate (e.g., F1=1.0, F2=0.1).
    """

    def setUp(self):
        self.selector = NpuParetoSelector(use_npu=False, use_decisions_api=False)
        self.inferior_valid = {
            "name": "inferior_valid_candidate",
            "security_score": 0.10,
            "intent_score": 0.10,
            "resource_score": 0.10,
            "mdl_density": 0.10
        }

    def _assert_inferior_valid_wins(self, disqualified_cand: Dict[str, Any], mechanism: str):
        """Helper to evaluate and verify disqualification over inferior valid candidate."""
        # Ensure candidate has perfect F2..F5 scores
        disqualified_cand.setdefault("security_score", 1.0)
        disqualified_cand.setdefault("intent_score", 1.0)
        disqualified_cand.setdefault("resource_score", 1.0)
        disqualified_cand.setdefault("mdl_density", 1.0)

        vec_disq = self.selector.evaluate_candidate(disqualified_cand)
        vec_valid = self.selector.evaluate_candidate(self.inferior_valid)

        self.assertEqual(
            vec_valid[0], 1.0,
            f"Inferior valid candidate must have F1=1.0, got {vec_valid}"
        )

        winner = self.selector.select_dominant([disqualified_cand, self.inferior_valid])
        self.assertIsNotNone(winner, f"Selector returned None for {mechanism}")
        self.assertEqual(
            winner["name"], "inferior_valid_candidate",
            f"VIOLATION: Disqualified candidate won via mechanism '{mechanism}'! "
            f"Disqualified vector={vec_disq}, Valid vector={vec_valid}"
        )

        # Invariance under reverse presentation order
        winner_rev = self.selector.select_dominant([self.inferior_valid, disqualified_cand])
        self.assertEqual(
            winner_rev["name"], "inferior_valid_candidate",
            f"VIOLATION: Presentation order changed outcome for mechanism '{mechanism}'!"
        )

    def test_stress_f1_invalid_schema_flag(self):
        """Disqualification vector 1: invalid_schema flag."""
        cand = {"name": "disq_invalid_schema", "invalid_schema": True}
        self._assert_inferior_valid_wins(cand, "invalid_schema")

    def test_stress_f1_budget_violation_flag(self):
        """Disqualification vector 2: budget_violation flag."""
        cand = {"name": "disq_budget_violation", "budget_violation": True}
        self._assert_inferior_valid_wins(cand, "budget_violation")

    def test_stress_f1_unacceptable_risk_flag(self):
        """Disqualification vector 3: unacceptable_risk flag."""
        cand = {"name": "disq_unacceptable_risk", "unacceptable_risk": True}
        self._assert_inferior_valid_wins(cand, "unacceptable_risk")

    def test_stress_f1_cyclic_dependencies_flag(self):
        """Disqualification vector 4: cyclic_dependencies_detected flag."""
        cand = {"name": "disq_cyclic_deps", "cyclic_dependencies_detected": True}
        self._assert_inferior_valid_wins(cand, "cyclic_dependencies_detected")

    def test_stress_f1_eu_ai_act_unacceptable_category(self):
        """Disqualification vector 5: EU AI Act risk category UNACCEPTABLE."""
        cand = {"name": "disq_eu_ai_act", "ai_act_risk_category": "UNACCEPTABLE"}
        self._assert_inferior_valid_wins(cand, "ai_act_risk_category: UNACCEPTABLE")

    def test_stress_f1_ram_boundary_exceeded(self):
        """Disqualification vector 6: RAM > 512.0 MB (Meteor Lake NPU limit)."""
        cand = {"name": "disq_ram_limit", "max_ram_budget_mb": 512.001}
        self._assert_inferior_valid_wins(cand, "max_ram_budget_mb > 512")

    def test_stress_f1_unit_economics_insolvency(self):
        """Disqualification vector 7: LTV / CAC < 3.0."""
        cand = {
            "name": "disq_insolvent",
            "customer_acquisition_cost": 1000.0,
            "lifetime_value": 2999.99
        }
        self._assert_inferior_valid_wins(cand, "LTV/CAC < 3.0")

    def test_stress_f1_therac25_latency_hazard(self):
        """Disqualification vector 8: Actuator latency > 1000ms without interlocks."""
        cand = {
            "name": "disq_therac25_hazard",
            "physical_actuator_latency_ms": 1000.01,
            "hardware_interlocks_required": False
        }
        self._assert_inferior_valid_wins(cand, "actuator latency > 1000ms without interlocks")

    def test_stress_f1_semantic_chameleon_unmapped_ac(self):
        """Disqualification vector 9: Business rule references non-existent Gherkin AC."""
        cand = {
            "name": "disq_semantic_chameleon",
            "business_rules": [{"rule_id": "BR-1", "source_ac_id": "AC-NON-EXISTENT"}]
        }
        ctx = {"gherkin_acs": [{"id": "AC-LEGIT-1"}, {"id": "AC-LEGIT-2"}]}
        vec_disq = self.selector.evaluate_candidate(cand, context=ctx)
        self.assertEqual(vec_disq[0], 0.0, "Unmapped AC must set F1 = 0.0")

        winner = self.selector.select_dominant([cand, self.inferior_valid], context=ctx)
        self.assertEqual(winner["name"], "inferior_valid_candidate")

    def test_stress_f1_pydantic_schema_rejection(self):
        """Disqualification vector 10: Strict Pydantic V2 schema validation rejection."""
        invalid_hw = {
            "target_cpu_profile": "Intel Core Ultra 5 125H",
            "target_npu_device": "INTEL_AI_BOOST_VPU_3720",
            "openvino_version": "2026.4.0",
            "max_ram_budget_mb": 1024.0,  # Invalid under Pydantic (> 512)
            "p99_latency_ms": 10.0,
            "cold_start_budget_ms": 10.0,
            "physical_actuator_latency_ms": 10.0,
            "hardware_interlocks_required": False
        }
        valid_hw = {
            "target_cpu_profile": "Intel Core Ultra 5 125H",
            "target_npu_device": "INTEL_AI_BOOST_VPU_3720",
            "openvino_version": "2026.4.0",
            "max_ram_budget_mb": 256.0,
            "p99_latency_ms": 40.0,
            "cold_start_budget_ms": 50.0,
            "physical_actuator_latency_ms": 100.0,
            "hardware_interlocks_required": False
        }
        ctx = {"schema_class": HardwareRuntimeContract}
        vec_disq = self.selector.evaluate_candidate(invalid_hw, context=ctx)
        vec_valid = self.selector.evaluate_candidate(valid_hw, context=ctx)
        self.assertEqual(vec_disq[0], 0.0, "Invalid hardware candidate must fail F1")
        self.assertEqual(vec_valid[0], 1.0, "Valid hardware candidate must pass F1")

        winner = self.selector.select_dominant([invalid_hw, valid_hw], context=ctx)
        self.assertIsNotNone(winner)
        self.assertEqual(winner["max_ram_budget_mb"], 256.0)

    def test_stress_f1_all_candidates_disqualified_raises_or_none(self):
        """When all candidates have F1=0.0, returns None or raises exception."""
        all_bad = [
            {"name": "bad1", "invalid_schema": True},
            {"name": "bad2", "ai_act_risk_category": "UNACCEPTABLE"},
            {"name": "bad3", "max_ram_budget_mb": 999.0}
        ]
        winner = self.selector.select_dominant(all_bad)
        self.assertIsNone(winner)

        with self.assertRaises(AllHypothesesDisqualifiedError):
            self.selector.select_dominant(all_bad, context={"raise_on_disqualified": True})


class TestEmpiricalNonAdditiveDominance(unittest.TestCase):
    """
    Stress-tests the non-additive lexicographic dominance property:
    Candidate with superior F2 MUST strictly dominate candidate with inferior F2
    regardless of how high F4 (cost) and F5 (MDL) are.
    Eliminates additive weight skew (e.g., cheap cost compensating for bad security).
    """

    def setUp(self):
        self.selector = NpuParetoSelector(use_npu=False, use_decisions_api=False)

    def test_non_additive_f2_over_perfect_f4_f5(self):
        """
        Candidate A: Security=0.90, OPEX=$10,000 (F4=0.0), MDL=0.0 (F5=0.0).
        Candidate B: Security=0.80, OPEX=$0 (F4=1.0), MDL=1.0 (F5=1.0).
        Diff in F2 = 0.10 > epsilon_2 (0.05).
        Candidate A MUST win despite B having maximum possible F4 and F5.
        """
        cand_a = {
            "name": "Candidate_A_HighSec_TerribleCost",
            "security_score": 0.90,
            "intent_score": 0.90,
            "monthly_opex": 10000.0,  # F4 = 0.0
            "mdl_density": 0.0        # F5 = 0.0
        }
        cand_b = {
            "name": "Candidate_B_LowSec_FreeCost",
            "security_score": 0.80,   # F2 = 0.80 (0.10 lower)
            "intent_score": 0.90,
            "monthly_opex": 0.0,      # F4 = 1.0 (perfect)
            "mdl_density": 1.0        # F5 = 1.0 (perfect)
        }

        va = self.selector.evaluate_candidate(cand_a)
        vb = self.selector.evaluate_candidate(cand_b)

        self.assertTrue(
            self.selector.dominates(va, vb),
            f"Candidate A (va={va}) must strictly dominate B (vb={vb})"
        )
        self.assertFalse(
            self.selector.dominates(vb, va),
            f"Candidate B (vb={vb}) must NOT dominate A (va={va})"
        )

        winner = self.selector.select_dominant([cand_a, cand_b])
        self.assertEqual(
            winner["name"], "Candidate_A_HighSec_TerribleCost",
            "Non-additive dominance failure: B beat A due to superior F4/F5!"
        )

        # Presentation order invariance
        winner_rev = self.selector.select_dominant([cand_b, cand_a])
        self.assertEqual(winner_rev["name"], "Candidate_A_HighSec_TerribleCost")

    def test_non_additive_f3_over_perfect_f4_f5_when_f2_tied(self):
        """
        When F2 is tied (within epsilon 0.05), F3 (Intent) strictly dominates F4/F5.
        Candidate A: Security=0.90, Intent=0.95, OPEX=$9,000 (F4=0.1), MDL=0.1.
        Candidate B: Security=0.90, Intent=0.85, OPEX=$0 (F4=1.0), MDL=1.0.
        Diff in F3 = 0.10 > epsilon_3 (0.02).
        Candidate A MUST win.
        """
        cand_a = {
            "name": "Candidate_A_HighIntent_TerribleCost",
            "security_score": 0.90,
            "intent_score": 0.95,
            "monthly_opex": 9000.0,
            "mdl_density": 0.10
        }
        cand_b = {
            "name": "Candidate_B_LowIntent_FreeCost",
            "security_score": 0.90,
            "intent_score": 0.85,
            "monthly_opex": 0.0,
            "mdl_density": 1.0
        }

        va = self.selector.evaluate_candidate(cand_a)
        vb = self.selector.evaluate_candidate(cand_b)

        self.assertTrue(self.selector.dominates(va, vb))
        winner = self.selector.select_dominant([cand_a, cand_b])
        self.assertEqual(winner["name"], "Candidate_A_HighIntent_TerribleCost")

    def test_non_additive_multi_candidate_ensemble(self):
        """
        In a 5-candidate ensemble, verifies that candidate with highest F2 dominates
        even when all other 4 candidates gang up with higher F4/F5.
        """
        candidates = [
            {"name": "Defensive", "security_score": 0.96, "intent_score": 0.90, "monthly_opex": 8000.0, "mdl_density": 0.50},
            {"name": "Balanced", "security_score": 0.88, "intent_score": 0.90, "monthly_opex": 3000.0, "mdl_density": 0.80},
            {"name": "High-Throughput", "security_score": 0.85, "intent_score": 0.90, "monthly_opex": 2000.0, "mdl_density": 0.85},
            {"name": "Frugal", "security_score": 0.80, "intent_score": 0.90, "monthly_opex": 100.0, "mdl_density": 0.95},
            {"name": "Ultra-Frugal", "security_score": 0.75, "intent_score": 0.90, "monthly_opex": 0.0, "mdl_density": 1.0}
        ]

        winner = self.selector.select_dominant(candidates)
        self.assertEqual(
            winner["name"], "Defensive",
            "Defensive candidate (highest security 0.96) must win regardless of cost"
        )


class TestEmpiricalEpsilonBoundaries(unittest.TestCase):
    """
    Stress-tests the exact mathematical boundaries of epsilon-indifference:
    eps_vector = (0.0, 0.05, 0.02, 0.05, 0.05).
    """

    def setUp(self):
        self.selector = NpuParetoSelector(use_npu=False, use_decisions_api=False)

    def test_f2_epsilon_boundary_inside_falls_to_f3(self):
        """
        When |F2(A) - F2(B)| = 0.04 <= 0.05 (inside epsilon):
        F2 is considered tied, so F3 strictly decides.
        """
        cand_a = {"name": "A", "security_score": 0.90, "intent_score": 0.95}
        cand_b = {"name": "B", "security_score": 0.94, "intent_score": 0.70}  # diff = 0.04 <= 0.05

        winner = self.selector.select_dominant([cand_a, cand_b])
        self.assertEqual(
            winner["name"], "A",
            "Inside epsilon (diff=0.04 <= 0.05), F2 is tied, so A's higher F3 (0.95 vs 0.70) must win"
        )

    def test_f2_epsilon_boundary_outside_f2_decides(self):
        """
        When |F2(A) - F2(B)| = 0.06 > 0.05 (outside epsilon):
        F2 immediately decides, regardless of F3.
        """
        cand_a = {"name": "A", "security_score": 0.96, "intent_score": 0.70}  # diff = 0.06 > 0.05
        cand_b = {"name": "B", "security_score": 0.90, "intent_score": 0.95}

        winner = self.selector.select_dominant([cand_a, cand_b])
        self.assertEqual(
            winner["name"], "A",
            "Outside epsilon (diff=0.06 > 0.05), F2 immediately decides for A"
        )

    def test_f3_epsilon_boundary_inside_falls_to_f4(self):
        """
        When F2 is identical and |F3(A) - F3(B)| = 0.015 <= 0.02 (inside epsilon_3):
        F3 is considered tied, so F4 (cost) decides.
        """
        cand_a = {"name": "A", "security_score": 0.90, "intent_score": 0.90, "monthly_opex": 100.0}   # high F4
        cand_b = {"name": "B", "security_score": 0.90, "intent_score": 0.915, "monthly_opex": 5000.0} # diff=0.015 <= 0.02

        winner = self.selector.select_dominant([cand_a, cand_b])
        self.assertEqual(
            winner["name"], "A",
            "Inside epsilon_3 (diff=0.015 <= 0.02), F3 is tied, so A's superior F4 must win"
        )

    def test_f3_epsilon_boundary_outside_f3_decides(self):
        """
        When F2 is identical and |F3(A) - F3(B)| = 0.025 > 0.02 (outside epsilon_3):
        F3 strictly decides for B.
        """
        cand_a = {"name": "A", "security_score": 0.90, "intent_score": 0.90, "monthly_opex": 100.0}
        cand_b = {"name": "B", "security_score": 0.90, "intent_score": 0.925, "monthly_opex": 5000.0} # diff=0.025 > 0.02

        winner = self.selector.select_dominant([cand_a, cand_b])
        self.assertEqual(
            winner["name"], "B",
            "Outside epsilon_3 (diff=0.025 > 0.02), F3 immediately decides for B"
        )


class TestEmpiricalAdversarialProbesAndEdgeCases(unittest.TestCase):
    """
    Adversarial vulnerability mining:
    Tests unexpected inputs, structural hazards, and mathematical boundary failures.
    """

    def setUp(self):
        self.selector = NpuParetoSelector(use_npu=False, use_decisions_api=False)

    def test_probe_empty_candidate_list(self):
        """Empty candidate pool returns None without throwing IndexError or KeyError."""
        result = self.selector.select_dominant([])
        self.assertIsNone(result)

    def test_probe_single_candidate_pool(self):
        """Single candidate pool returns the candidate immediately."""
        cand = {"name": "solo", "security_score": 0.85}
        winner = self.selector.select_dominant([cand])
        self.assertEqual(winner["name"], "solo")

    def test_probe_deterministic_sha256_tie_breaker(self):
        """
        When multiple candidates have IDENTICAL objective vectors across all 5 dimensions,
        the winner is deterministically chosen via canonical SHA-256 hash.
        Repeated runs on arbitrary permutations must produce the EXACT same winner.
        """
        c1 = {"name": "cand_alpha", "security_score": 0.90, "intent_score": 0.90, "monthly_opex": 1000.0, "mdl_density": 0.80}
        c2 = {"name": "cand_beta", "security_score": 0.90, "intent_score": 0.90, "monthly_opex": 1000.0, "mdl_density": 0.80}
        c3 = {"name": "cand_gamma", "security_score": 0.90, "intent_score": 0.90, "monthly_opex": 1000.0, "mdl_density": 0.80}

        w1 = self.selector.select_dominant([c1, c2, c3])["name"]
        w2 = self.selector.select_dominant([c3, c2, c1])["name"]
        w3 = self.selector.select_dominant([c2, c1, c3])["name"]

        self.assertEqual(w1, w2, "Tie-breaking must be permutation-invariant")
        self.assertEqual(w2, w3, "Tie-breaking must be permutation-invariant")

    def test_probe_iso29148_russian_fuzzy_word_negation(self):
        """
        ISO 29148 fuzzy word penalty must be active on un-negated fuzzy words
        and inactive on negated Russian and English words.
        """
        unnegated = {"name": "unneg", "description": "Система очень быстрая и надежная"}
        negated = {"name": "neg", "description": "Система не быстрая, без надежности на словах, строго детерминированная"}

        v_unneg = self.selector.evaluate_candidate(unnegated)
        v_neg = self.selector.evaluate_candidate(negated)

        self.assertLess(
            v_unneg[1], v_neg[1],
            "Un-negated fuzzy words must incur penalty relative to negated phrasing"
        )

    def test_probe_performance_and_latency_sla(self):
        """
        System 1 Fast-Path SLA:
        Selection across 5 candidates must execute in < 15 ms (< 3 ms / candidate).
        """
        candidates = [
            {"name": f"cand_{i}", "security_score": 0.80 + i * 0.02, "monthly_opex": 1000.0 * (i + 1)}
            for i in range(5)
        ]

        t0 = time.perf_counter()
        iterations = 50
        for _ in range(iterations):
            _ = self.selector.select_dominant(candidates)
        elapsed_ms = ((time.perf_counter() - t0) / iterations) * 1000.0

        self.assertLess(
            elapsed_ms, 15.0,
            f"L-MOPA selection latency {elapsed_ms:.3f} ms exceeds 15 ms SLA limit"
        )


class TestVulnerabilityDemonstrations(unittest.TestCase):
    """
    Adversarial Empirical Vulnerability Demonstrations:
    Documents critical edge cases and failure modes identified during stress testing.
    """

    def setUp(self):
        self.selector = NpuParetoSelector(use_npu=False, use_decisions_api=False)

    def test_vulnerability_nan_clamping_inversion(self):
        """
        Adversarial Attack: NaN injection into intent_score, resource_score, or mdl_density
        gets clamped to 1.0 (PERFECT SCORE) instead of being penalized or rejected.
        Root cause: min(1.0, float('nan')) returns 1.0 in Python -> max(0.0, 1.0) == 1.0.
        Allows an uninitialized/corrupted candidate to beat a legitimate candidate (e.g. 0.85).
        """
        cand_nan = {
            "name": "nan_poisoned_candidate",
            "security_score": 0.90,
            "intent_score": float("nan"),
            "resource_score": float("nan"),
            "mdl_density": float("nan")
        }
        cand_honest = {
            "name": "honest_candidate",
            "security_score": 0.90,
            "intent_score": 0.85,
            "resource_score": 0.85,
            "mdl_density": 0.85
        }

        vec_nan = self.selector.evaluate_candidate(cand_nan)
        self.assertEqual(vec_nan[2], 1.0, "VULNERABILITY: intent_score NaN inverted to 1.0")
        self.assertEqual(vec_nan[3], 1.0, "VULNERABILITY: resource_score NaN inverted to 1.0")
        self.assertEqual(vec_nan[4], 1.0, "VULNERABILITY: mdl_density NaN inverted to 1.0")

        # The NaN poisoned candidate beats the honest candidate
        winner = self.selector.select_dominant([cand_nan, cand_honest])
        self.assertEqual(
            winner["name"], "nan_poisoned_candidate",
            "VULNERABILITY: NaN poisoned candidate dominated honest candidate"
        )

    def test_vulnerability_direct_f1_vector_key_ignored(self):
        """
        Asymmetry Flaw: evaluate_candidate supports 'f4' directly (line 375),
        but completely ignores 'f1', 'f2', 'f3', 'f5'.
        Passing {"f1": 0.0} results in F1 = 1.0 instead of 0.0.
        """
        cand = {"name": "direct_f1_cand", "f1": 0.0, "security_score": 1.0}
        vec = self.selector.evaluate_candidate(cand)
        self.assertEqual(
            vec[0], 1.0,
            "VULNERABILITY: explicit f1=0.0 ignored by evaluate_candidate (remains 1.0)"
        )

    def test_vulnerability_negative_cac_solvency_bypass_without_schema(self):
        """
        Solvency Flaw: when context has no schema_class, negative CAC / negative LTV
        bypasses the solvency check because 'cac_val > 0' is False.
        """
        cand_negative_cac = {
            "name": "negative_cac",
            "customer_acquisition_cost": -100.0,
            "lifetime_value": -1000.0
        }
        vec = self.selector.evaluate_candidate(cand_negative_cac)
        self.assertEqual(
            vec[0], 1.0,
            "VULNERABILITY: negative CAC bypasses solvency check when schema_class is absent"
        )


if __name__ == "__main__":
    unittest.main()
