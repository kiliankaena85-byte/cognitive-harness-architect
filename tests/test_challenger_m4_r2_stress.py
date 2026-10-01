"""
tests/test_challenger_m4_r2_stress.py
=============================================================================
Milestone 4 Round 2 Independent Empirical Challenger Stress Suite:
Adversarial stress-testing of:
1. Simplex Parameter Downscaling & Zero-Trust Gate Fall-Through Elimination:
   - Verifying genuine downscaling parameters (Frugal profile, cluster=1, GPU=False, RAM<=256MB)
   - Verifying downscaled commit on Node 2 (Finance)
   - RESOLVED (M4-R3 Remediation): Node 6 downscaled candidate uses CandidateDict and
     isolated underscore metadata, ensuring clean commit under Simplex downscaling with 0 extra_forbidden errors
   - Verifying strict halt in STATE_TERMINAL_FAILED + ZeroTrustGateFailure on unresolvable gate failure
   - Verifying no unverified artifacts committed to registry or disk
2. Transitive Multi-Step Cascading Rollback:
   - Verifying veto Node 1 rolls back Nodes 2, 3, 4, 5, 6, 7 to STATE_IDLE with artifacts purged
   - Verifying veto Node 2 rolls back Nodes 4, 5, 6, 7 to STATE_IDLE while keeping Nodes 1 and 3 COMMITTED
   - Verifying veto Node 4 rolls back Nodes 5, 6, 7 to STATE_IDLE
   - Verifying veto Node 5 rolls back Nodes 6, 7 to STATE_IDLE
   - Verifying reverse topological order of cascading invalidation
3. Therac-25 Resolution Flow:
   - Simulating actuator latency collision without prompt keyword leakage
   - Verifying pure FSM re-execution with ZERO forced transitions
   - Verifying Stage Gate verification and clean commit of all 7 artifacts
   - Verifying physical temporal invariants on HardwareRuntimeContract
4. Global Coordination Budget & State Pollution:
   - Strict halt on budget exhaustion
   - Zero state pollution across consecutive runs
=============================================================================
"""

import copy
import json
import os
import sys
import tempfile
import time
import unittest
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import MagicMock, patch

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
CORE_DIR = PROJECT_ROOT / "core"
if str(CORE_DIR) not in sys.path:
    sys.path.insert(0, str(CORE_DIR))

# Schemas
from core.schemas import (
    StrategyCJMContract,
    FinanceBudgetContract,
    LegalComplianceContract,
    SecurityPolicyContract,
    SystemAnalysisContract,
    HardwareRuntimeContract,
    VVQualityContract,
    CONTRACT_SCHEMAS_REGISTRY,
)

# Orchestrator components
from core.orchestrator import (
    DagOrchestrator,
    DagTopology,
    NodeState,
    NodeFSM,
    ArtifactRegistry,
    ZeroTrustGateCoordinator,
    PipelineResult,
    InvalidStateTransitionError,
    GlobalBudgetExhaustedError,
    ZeroTrustGateFailure,
    CANONICAL_FILENAMES,
    NODE_SCHEMAS,
)
from core.npu_darwinian_loop import AllHypothesesDisqualifiedError


class TestSimplexDownscalingAndZeroTrustGateFallThrough(unittest.TestCase):
    """
    Empirical stress-testing of Simplex Parameter Downscaling and
    Zero-Trust Gate Fall-Through Elimination.
    """

    def setUp(self):
        self.orchestrator = DagOrchestrator(use_mock=True)

    def test_simplex_downscaling_parameters_on_node2_finance(self):
        """
        Forces 3 verification failures on Node 2 (Finance).
        Verifies:
        - Downscaling is triggered after 3 retries
        - Simplex downscaled record logged with frugal profile
        - CapEx is capped to <= 350,000 RUB
        - Downscaled candidate passes verification and commits cleanly
        - Committed artifact in registry reflects downscaled CapEx
        """
        orch = DagOrchestrator(use_mock=True)
        call_count = {"count": 0}
        orig_verify = orch.gate_coordinator.verify_node_stage_gate

        def flaky_verify_node2(node_id, candidate_dict, context=None):
            if node_id == 2:
                call_count["count"] += 1
                if call_count["count"] <= 3:
                    return False, f"Simulated Finance Gate rejection {call_count['count']}", {}
            return orig_verify(node_id, candidate_dict, context)

        with patch.object(orch.gate_coordinator, "verify_node_stage_gate", side_effect=flaky_verify_node2):
            result = orch.run("Test Simplex Node 2 Downscale")

        self.assertEqual(result.status, "SUCCESS")
        self.assertEqual(len(orch.simplex_downgrades_applied), 1)
        record = orch.simplex_downgrades_applied[0]
        self.assertEqual(record["node_id"], 2)
        self.assertEqual(record["parameters_mutated"]["profile"], "frugal")

        n2_artifact = orch.registry.get_by_id(2)
        self.assertIsNotNone(n2_artifact)
        self.assertLessEqual(n2_artifact.get("max_hardware_capex", 0.0), 350000.0)

        # Invariant: Node 2 transitions through STATE_SIMPLEX_DOWNGRADE to STATE_COMMITTED
        n2_history = [h["to"] for h in orch.node_fsms[2].history]
        self.assertIn(NodeState.STATE_SIMPLEX_DOWNGRADE.value, n2_history)
        self.assertEqual(orch.fsm_states[2], NodeState.STATE_COMMITTED.value)

    def test_empirical_bug_node6_downscaled_candidate_violates_extra_forbidden(self):
        """
        VERIFICATION OF RESOLVED BEHAVIOR (M4-R3 Remediation):
        Previously, when Node 6 exhausted retries, _synthesize_downscaled_candidate()
        injected non-schema fields ('cluster_size', 'gpu_enabled', 'hardware_cost'),
        causing Pydantic V2 extra_forbidden rejection and ZeroTrustGateFailure.
        With schema-clean synthesis (CandidateDict + leading underscores),
        verify_node_stage_gate() passes cleanly and Node 6 successfully commits
        with downscaled parameters.
        """
        orch = DagOrchestrator(use_mock=True)
        call_count = {"count": 0}
        orig_verify = orch.gate_coordinator.verify_node_stage_gate

        def flaky_verify_node6(node_id, candidate_dict, context=None):
            if node_id == 6:
                call_count["count"] += 1
                if call_count["count"] <= 3:
                    return False, f"Flaky rejection {call_count['count']}", {}
                # On attempt 4 (the downscaled candidate), call the genuine gate
            return orig_verify(node_id, candidate_dict, context)

        with patch.object(orch.gate_coordinator, "verify_node_stage_gate", side_effect=flaky_verify_node6):
            result = orch.run("Test Simplex Node 6 Bug Resolved")

        self.assertEqual(result.status, "SUCCESS")
        self.assertEqual(len(orch.simplex_downgrades_applied), 1)
        record = orch.simplex_downgrades_applied[0]
        self.assertEqual(record["node_id"], 6)
        self.assertEqual(record["action"], "downgrade_cluster_and_disable_gpu")

        n6_artifact = orch.registry.get_by_id(6)
        self.assertIsNotNone(n6_artifact)
        self.assertLessEqual(n6_artifact.get("max_ram_budget_mb", 999.0), 256.0)
        self.assertEqual(n6_artifact.get("target_npu_device"), "INTEL_AI_BOOST_VPU_3720")

        # Invariant: Node 6 transitions through STATE_SIMPLEX_DOWNGRADE to STATE_COMMITTED
        n6_history = [h["to"] for h in orch.node_fsms[6].history]
        self.assertIn(NodeState.STATE_SIMPLEX_DOWNGRADE.value, n6_history)
        self.assertEqual(orch.fsm_states[6], NodeState.STATE_COMMITTED.value)

    def test_node6_direct_synthesis_defect_inspection(self):
        """
        VERIFICATION OF RESOLVED BEHAVIOR (M4-R3 Remediation):
        Directly inspects the output of _synthesize_downscaled_candidate for Node 6:
        Verifies that bare forbidden keys are absent from visible keys,
        and that HardwareRuntimeContract.model_validate() passes cleanly with 0 errors.
        """
        orch = DagOrchestrator(use_mock=True)
        blanket = {"prompt": "test"}
        downscaled_cand = orch._synthesize_downscaled_candidate(node_id=6, blanket=blanket)

        # Assert bare forbidden keys are strictly absent from visible keys:
        self.assertNotIn("cluster_size", list(downscaled_cand.keys()))
        self.assertNotIn("gpu_enabled", list(downscaled_cand.keys()))
        self.assertNotIn("hardware_cost", list(downscaled_cand.keys()))

        # Direct schema validation MUST pass cleanly without extra_forbidden:
        model = HardwareRuntimeContract.model_validate(downscaled_cand)
        self.assertLessEqual(model.max_ram_budget_mb, 256.0)
        self.assertEqual(model.target_npu_device, "INTEL_AI_BOOST_VPU_3720")

        # Internal metadata keys are accessible for CrossMinistryArbiter:
        self.assertEqual(downscaled_cand.get("_cluster_size"), 1)
        self.assertEqual(downscaled_cand.get("_gpu_enabled"), False)
        self.assertEqual(downscaled_cand.get("_hardware_cost"), 150000.0)

    def test_zero_trust_gate_permanent_failure_strictly_halts_in_terminal_failed(self):
        """
        Hostile failure injection: Node 1 stage gate PERMANENTLY rejects.
        Verifies:
        - Orchestrator raises ZeroTrustGateFailure (NO SILENT COMMIT!)
        - Node 1 halts strictly in STATE_TERMINAL_FAILED
        - Registry contains NO artifact for Node 1
        - Pipeline artifacts dict does NOT contain Node 1's file
        - Downstream nodes (2..7) remain in STATE_IDLE and are NOT executed
        - Execution history records status FAILED
        """
        orch = DagOrchestrator(use_mock=True)

        def permanent_fail_gate(node_id, candidate_dict, context=None):
            if node_id == 1:
                return False, "HARD_INVARIANT_VIOLATION: Intent AC mismatch", {"error": "unresolvable"}
            return True, "Pass", {}

        with patch.object(orch.gate_coordinator, "verify_node_stage_gate", side_effect=permanent_fail_gate):
            with self.assertRaises(ZeroTrustGateFailure) as cm:
                orch.run("Hostile Failure Prompt")

            self.assertIn("Ministry_1_Strategy", cm.exception.gate_name)
            self.assertIn("Zero-Trust Stage Gate rejected Node 1", str(cm.exception))

        # Node 1 must be strictly in STATE_TERMINAL_FAILED
        self.assertEqual(orch.fsm_states[1], NodeState.STATE_TERMINAL_FAILED.value)
        self.assertEqual(orch.node_fsms[1].current_state, NodeState.STATE_TERMINAL_FAILED)

        # Absolutely NO artifact committed for Node 1
        self.assertIsNone(orch.registry.get_by_id(1))
        self.assertNotIn(CANONICAL_FILENAMES[1], orch.artifacts)

        # Downstream nodes must NEVER have been started (must be STATE_IDLE)
        for nid in range(2, 8):
            self.assertEqual(
                orch.fsm_states[nid],
                NodeState.STATE_IDLE.value,
                f"Downstream Node {nid} executed despite upstream terminal failure!",
            )
            self.assertIsNone(orch.registry.get_by_id(nid))

        # Execution history check
        self.assertEqual(len(orch.execution_history), 1)
        self.assertEqual(orch.execution_history[0]["status"], "FAILED")

    def test_lmopa_feasibility_permanent_failure_strictly_halts_in_terminal_failed(self):
        """
        Hostile injection: L-MOPA rejects all candidates for Node 3 (Legal) permanently (all F1=0).
        Verifies:
        - AllHypothesesDisqualifiedError raised
        - Node 3 halts in STATE_TERMINAL_FAILED
        - No artifact committed for Node 3 or downstream
        """
        orch = DagOrchestrator(use_mock=True)
        orig_select = orch.selector.select_dominant

        def permanent_reject_lmopa(candidates, context=None, ministry_name=""):
            if "legal" in str(ministry_name).lower():
                return None  # All disqualified
            return orig_select(candidates, context=context, ministry_name=ministry_name)

        with patch.object(orch.selector, "select_dominant", side_effect=permanent_reject_lmopa):
            with self.assertRaises(AllHypothesesDisqualifiedError):
                orch.run("Hostile Legal Prompt")

        self.assertEqual(orch.fsm_states[3], NodeState.STATE_TERMINAL_FAILED.value)
        self.assertIsNone(orch.registry.get_by_id(3))
        self.assertNotIn(CANONICAL_FILENAMES[3], orch.artifacts)


class TestTransitiveMultiStepCascadingRollback(unittest.TestCase):
    """
    Empirical stress-testing of Transitive Multi-Step Cascading Rollback.
    """

    def setUp(self):
        self.orchestrator = DagOrchestrator(use_mock=True)

    def _precommit_all_7_nodes(self, orch: DagOrchestrator):
        """Helper to pre-commit all 7 nodes with dummy valid artifacts."""
        for nid in range(1, 8):
            art = {"node_id": nid, "title": f"Artifact_{nid}"}
            orch.registry.register(nid, art, CANONICAL_FILENAMES[nid])
            orch.artifacts[CANONICAL_FILENAMES[nid]] = art
            orch._force_fsm_state(nid, NodeState.STATE_COMMITTED)

    def test_vetoing_node1_rolls_back_all_descendants_2_through_7(self):
        """
        Requirement 2.1:
        Verify vetoing Node 1 rolls back Nodes 2, 3, 4, 5, 6, 7 to STATE_IDLE with artifacts purged.
        """
        orch = self.orchestrator
        self._precommit_all_7_nodes(orch)

        # All 7 nodes are precommitted
        for nid in range(1, 8):
            self.assertEqual(orch.fsm_states[nid], NodeState.STATE_COMMITTED.value)
            self.assertIsNotNone(orch.registry.get_by_id(nid))

        # Veto target Node 1 (Strategy CJM) from downstream Node 7 (or any arbiter)
        orch.execute_saga_compensation(
            vetoing_node=7,
            target_node=1,
            prescription="Full strategic reset required",
            hazard_code="STRATEGIC_INVALIDATION",
        )

        # 1. Target Node 1 is re-staged in STATE_SYSTEM2_GENERATE and its artifact is purged
        self.assertEqual(orch.fsm_states[1], NodeState.STATE_SYSTEM2_GENERATE.value)
        self.assertIsNone(orch.registry.get_by_id(1))
        self.assertNotIn(CANONICAL_FILENAMES[1], orch.artifacts)

        # 2. Transitive descendants: Nodes 2, 3, 4, 5, 6, 7 MUST ALL be STATE_IDLE
        for nid in [2, 3, 4, 5, 6, 7]:
            self.assertEqual(
                orch.fsm_states[nid],
                NodeState.STATE_IDLE.value,
                f"Node {nid} was not rolled back to STATE_IDLE!",
            )
            # Artifacts must be completely purged from registry and artifacts dict
            self.assertIsNone(
                orch.registry.get_by_id(nid),
                f"Node {nid} artifact was not purged from registry!",
            )
            self.assertNotIn(
                CANONICAL_FILENAMES[nid],
                orch.artifacts,
                f"Node {nid} artifact was not purged from orchestrator.artifacts!",
            )
            # Local retry count must be reset
            self.assertEqual(orch.retry_counts[nid], 0)

    def test_vetoing_node2_rolls_back_nodes_4_5_6_7_preserving_nodes_1_and_3(self):
        """
        Requirement 2.2:
        Verify vetoing Node 2 rolls back Nodes 4, 5, 6, 7 to STATE_IDLE with artifacts purged,
        while strictly preserving upstream Nodes 1 and 3 in STATE_COMMITTED.
        """
        orch = self.orchestrator
        self._precommit_all_7_nodes(orch)

        # Veto target Node 2 (Finance)
        orch.execute_saga_compensation(
            vetoing_node=6,
            target_node=2,
            prescription="Finance budget CaPEx renegotiation",
            hazard_code="BUDGET_COLLISION",
        )

        # 1. Upstream Node 1 and independent Node 3 MUST REMAIN COMMITTED with artifacts INTACT!
        self.assertEqual(orch.fsm_states[1], NodeState.STATE_COMMITTED.value)
        self.assertIsNotNone(orch.registry.get_by_id(1))
        self.assertIn(CANONICAL_FILENAMES[1], orch.artifacts)

        self.assertEqual(orch.fsm_states[3], NodeState.STATE_COMMITTED.value)
        self.assertIsNotNone(orch.registry.get_by_id(3))
        self.assertIn(CANONICAL_FILENAMES[3], orch.artifacts)

        # 2. Target Node 2 artifact purged and in STATE_SYSTEM2_GENERATE
        self.assertEqual(orch.fsm_states[2], NodeState.STATE_SYSTEM2_GENERATE.value)
        self.assertIsNone(orch.registry.get_by_id(2))
        self.assertNotIn(CANONICAL_FILENAMES[2], orch.artifacts)

        # 3. Transitive descendants of Node 2: {4, 5, 6, 7} MUST ALL be STATE_IDLE and purged
        for nid in [4, 5, 6, 7]:
            self.assertEqual(
                orch.fsm_states[nid],
                NodeState.STATE_IDLE.value,
                f"Descendant Node {nid} was not rolled back to STATE_IDLE!",
            )
            self.assertIsNone(orch.registry.get_by_id(nid))
            self.assertNotIn(CANONICAL_FILENAMES[nid], orch.artifacts)
            self.assertEqual(orch.retry_counts[nid], 0)

    def test_vetoing_node4_rolls_back_nodes_5_6_7(self):
        """
        Vetoing Node 4 (Infosec) rolls back {5, 6, 7}, leaving {1, 2, 3} COMMITTED.
        """
        orch = self.orchestrator
        self._precommit_all_7_nodes(orch)

        orch.execute_saga_compensation(
            vetoing_node=7,
            target_node=4,
            prescription="STRIDE policy inadequacy",
        )

        # Nodes 1, 2, 3 remained committed
        for nid in [1, 2, 3]:
            self.assertEqual(orch.fsm_states[nid], NodeState.STATE_COMMITTED.value)
            self.assertIsNotNone(orch.registry.get_by_id(nid))

        # Target Node 4 in STATE_SYSTEM2_GENERATE
        self.assertEqual(orch.fsm_states[4], NodeState.STATE_SYSTEM2_GENERATE.value)
        self.assertIsNone(orch.registry.get_by_id(4))

        # Nodes 5, 6, 7 rolled back to STATE_IDLE
        for nid in [5, 6, 7]:
            self.assertEqual(orch.fsm_states[nid], NodeState.STATE_IDLE.value)
            self.assertIsNone(orch.registry.get_by_id(nid))

    def test_vetoing_node5_rolls_back_nodes_6_7(self):
        """
        Vetoing Node 5 (System Analysis) rolls back {6, 7}, leaving {1, 2, 3, 4} COMMITTED.
        """
        orch = self.orchestrator
        self._precommit_all_7_nodes(orch)

        orch.execute_saga_compensation(
            vetoing_node=6,
            target_node=5,
            prescription="Missing interlock endpoint",
        )

        # Nodes 1, 2, 3, 4 remain COMMITTED
        for nid in [1, 2, 3, 4]:
            self.assertEqual(orch.fsm_states[nid], NodeState.STATE_COMMITTED.value)
            self.assertIsNotNone(orch.registry.get_by_id(nid))

        # Target Node 5 in STATE_SYSTEM2_GENERATE
        self.assertEqual(orch.fsm_states[5], NodeState.STATE_SYSTEM2_GENERATE.value)
        self.assertIsNone(orch.registry.get_by_id(5))

        # Nodes 6, 7 rolled back to STATE_IDLE
        for nid in [6, 7]:
            self.assertEqual(orch.fsm_states[nid], NodeState.STATE_IDLE.value)
            self.assertIsNone(orch.registry.get_by_id(nid))


class TestTherac25ResolutionFlowEmpirical(unittest.TestCase):
    """
    Empirical stress-testing of Therac-25 Resolution Flow.
    """

    def test_therac25_pure_fsm_reexecution_and_clean_commit(self):
        """
        Requirement 3:
        Run Therac-25 simulation and verify:
        - Pure FSM re-execution with ZERO forced transitions in normal execution
        - Stage Gate verification on both initial and re-execution phases
        - Clean commit with all 7 valid artifacts
        - Actuator latency temporal invariant validation
        """
        orch = DagOrchestrator(use_mock=True)
        neutral_prompt = "Radiotherapy Dosage Control System"
        result = orch.run(prompt=neutral_prompt, simulate_therac_hazard=True)

        self.assertEqual(result.status, "SUCCESS")

        # Exactly 1 Saga compensation executed
        self.assertEqual(len(orch.saga_compensations_executed), 1)
        comp = orch.saga_compensations_executed[0]
        self.assertEqual(comp["vetoing_node"], 6)
        self.assertEqual(comp["target_node"], 5)
        self.assertEqual(comp["hazard_code"], "THERAC_25_ACTUATOR_COLLISION")

        # Invariant: Node 5 evolved to include interlock status endpoint
        n5_art = result["System_Contracts.json"]
        interlock_eps = [
            ep for ep in n5_art.get("endpoints", [])
            if "/api/v1/hardware/interlock-status" in ep.get("path", "")
        ]
        self.assertEqual(len(interlock_eps), 1)
        self.assertEqual(interlock_eps[0]["method"], "GET")
        self.assertTrue(interlock_eps[0]["idempotent"])

        # Invariant: Node 6 enabled hardware interlocks
        n6_art = result["Hardware_Runtime_Manifest.json"]
        self.assertTrue(n6_art["hardware_interlocks_required"])
        self.assertEqual(n6_art["physical_actuator_latency_ms"], 8000.0)

        # Invariant: HardwareRuntimeContract temporal verification passes
        hw_model = HardwareRuntimeContract.model_validate(n6_art)
        hw_model.verify_physical_temporal_invariants()

        # Invariant: Pure FSM execution - verify ZERO forced transitions in Node 5 and Node 6 histories
        for nid in [5, 6]:
            forced_transitions = [
                h for h in orch.node_fsms[nid].history
                if h.get("reason", "").startswith("FORCED")
                and "Pipeline execution started" not in h.get("reason", "")
            ]
            self.assertEqual(
                len(forced_transitions),
                0,
                f"Node {nid} contained forced transitions during Therac-25 resolution: {forced_transitions}",
            )

        # Verify all 7 nodes end in STATE_COMMITTED
        for nid in range(1, 8):
            self.assertEqual(orch.fsm_states[nid], NodeState.STATE_COMMITTED.value)

        # Verify all 7 contracts validate cleanly with Pydantic V2
        for nid, schema_cls in NODE_SCHEMAS.items():
            fname = CANONICAL_FILENAMES[nid]
            self.assertIn(fname, result)
            model_inst = schema_cls.model_validate(result[fname])
            self.assertIsNotNone(model_inst)

    def test_therac25_prompt_keyword_decoupling_adversarial(self):
        """
        Adversarial test: Even if the prompt mentions 'Therac' and 'interlock',
        Node 5 does not bypass the Saga cycle; Node 6 must still detect the
        hazard, trigger compensation, and evolve Node 5 cleanly.
        """
        orch = DagOrchestrator(use_mock=True)
        adversarial_prompt = "Therac-25 machine with software interlock bypass attempt"
        result = orch.run(prompt=adversarial_prompt, simulate_therac_hazard=True)

        self.assertEqual(result.status, "SUCCESS")
        self.assertEqual(len(orch.saga_compensations_executed), 1)
        self.assertEqual(orch.saga_compensations_executed[0]["hazard_code"], "THERAC_25_ACTUATOR_COLLISION")


class TestGlobalBudgetAndCrossRunPurity(unittest.TestCase):
    """
    Stress-testing coordination limits and instance re-entrancy.
    """

    def test_global_budget_exhaustion_at_boundary_halts_safely(self):
        """
        Forces global coordination budget K_max (10) exhaustion.
        Verifies GlobalBudgetExhaustedError is raised and target node transitions to STATE_TERMINAL_FAILED.
        """
        orch = DagOrchestrator(use_mock=True)
        orch.global_iteration_k = 10  # At limit

        with self.assertRaises(GlobalBudgetExhaustedError):
            orch.apply_simplex_downgrade(node_id=6, reason="Exceeding budget")

        self.assertEqual(orch.fsm_states[6], NodeState.STATE_TERMINAL_FAILED.value)

    def test_ten_consecutive_runs_zero_state_leakage(self):
        """
        Executes 10 consecutive runs on the same DagOrchestrator instance,
        alternating hazard and normal modes.
        Verifies:
        - No artifact leakage
        - No compensation leakage
        - Execution history records all 10 runs accurately
        """
        orch = DagOrchestrator(use_mock=True)

        for i in range(10):
            hazard = (i % 2 == 1)
            prompt = f"Run {i}: {'Therac Simulation' if hazard else 'Nominal Generation'}"
            res = orch.run(prompt=prompt, simulate_therac_hazard=hazard)

            expected_compensations = 1 if hazard else 0
            self.assertEqual(
                len(res.saga_compensations_executed),
                expected_compensations,
                f"Run {i} failed compensation count check",
            )
            self.assertEqual(
                len(orch.saga_compensations_executed),
                expected_compensations,
                f"Run {i} leaked compensations into orchestrator instance",
            )
            self.assertEqual(len(res), 7)

        self.assertEqual(len(orch.execution_history), 10)


if __name__ == "__main__":
    unittest.main(verbosity=2)
