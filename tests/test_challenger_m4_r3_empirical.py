"""
tests/test_challenger_m4_r3_empirical.py
=============================================================================
Milestone 4 Round 3: Challenger Empirical Stress Suite for Node 6 Simplex Downscaling

Tests:
1. Direct Candidate Synthesis Stress:
   - Multiple candidate configurations (empty, ARC GPU, high RAM, low RAM, Therac hazard, long actuator latency)
   - CandidateDict compliance: no bare forbidden keys in keys()/items()
   - HardwareRuntimeContract.model_validate() passes with 0 extra_forbidden errors
   - Temporal invariants verification
   - JSON serialization cleanliness
2. Simulated Stage-Gate Flakiness & FSM Transition Stress:
   - 3 consecutive gate failures on Node 6 trigger apply_simplex_downgrade(6)
   - Node 6 transitions: STATE_STAGE_GATE_VERIFY -> STATE_SIMPLEX_DOWNGRADE -> STATE_COMMITTED
   - Artifact committed to registry and artifacts dict
   - Therac-25 hazard coupled with Simplex downscaling on Node 6
   - Tight CaPEx boundary cross-ministry check (200k RUB budget)
   - Permanent failure rejection into STATE_TERMINAL_FAILED
=============================================================================
"""

import json
import unittest
from pathlib import Path
import sys
from unittest.mock import patch

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
CORE_DIR = PROJECT_ROOT / "core"
if str(CORE_DIR) not in sys.path:
    sys.path.insert(0, str(CORE_DIR))

from core.schemas import HardwareRuntimeContract
from core.ministries.nodes import CandidateDict
from core.orchestrator import (
    DagOrchestrator,
    NodeState,
    CANONICAL_FILENAMES,
    ZeroTrustGateFailure,
)


class TestNode6SimplexEmpiricalStress(unittest.TestCase):
    """Empirical challenger stress suite for Node 6 Simplex downscaling resolution."""

    def setUp(self):
        self.orchestrator = DagOrchestrator(use_mock=True)

    def test_direct_synthesis_empty_base(self):
        """Case A: Empty base candidate."""
        blanket = {"prompt": "Empirical Test Empty Base"}
        cand = self.orchestrator._synthesize_downscaled_candidate(6, blanket, base_candidate=None)
        
        self.assertIsInstance(cand, CandidateDict)
        visible_keys = list(cand.keys())
        self.assertNotIn("cluster_size", visible_keys)
        self.assertNotIn("gpu_enabled", visible_keys)
        self.assertNotIn("hardware_cost", visible_keys)
        for k in visible_keys:
            self.assertFalse(k.startswith("_"), f"Underscore key leaked into visible keys: {k}")

        model = HardwareRuntimeContract.model_validate(cand)
        self.assertLessEqual(model.max_ram_budget_mb, 256.0)
        self.assertNotEqual(model.target_npu_device, "INTEL_ARC_GPU")
        self.assertEqual(cand.get("_cluster_size"), 1)
        self.assertEqual(cand.get("_gpu_enabled"), False)
        self.assertEqual(cand.get("_hardware_cost"), 150000.0)

    def test_direct_synthesis_arc_gpu_and_high_ram(self):
        """Case B: Base candidate with INTEL_ARC_GPU and 512MB RAM."""
        blanket = {"prompt": "Empirical Test ARC GPU"}
        base_cand = {
            "target_cpu_profile": "intel_core_ultra_5_125h",
            "target_npu_device": "INTEL_ARC_GPU",
            "openvino_version": "2024.4",
            "max_ram_budget_mb": 512.0,
            "p99_latency_ms": 40.0,
            "cold_start_budget_ms": 300.0,
            "hardware_interlocks_required": False,
            "physical_actuator_latency_ms": 25.0,
        }
        cand = self.orchestrator._synthesize_downscaled_candidate(6, blanket, base_candidate=base_cand)

        self.assertIsInstance(cand, CandidateDict)
        visible_keys = list(cand.keys())
        for forbidden in ("cluster_size", "gpu_enabled", "hardware_cost"):
            self.assertNotIn(forbidden, visible_keys)

        model = HardwareRuntimeContract.model_validate(cand)
        self.assertLessEqual(model.max_ram_budget_mb, 256.0)
        self.assertEqual(model.target_npu_device, "INTEL_AI_BOOST_VPU_3720")
        
        # Verify JSON dump
        dumped = json.loads(json.dumps(cand))
        for forbidden in ("cluster_size", "gpu_enabled", "hardware_cost", "_cluster_size", "_gpu_enabled", "_hardware_cost"):
            self.assertNotIn(forbidden, dumped)

    def test_direct_synthesis_low_ram_preservation(self):
        """Case C: Base candidate with 128MB RAM (below 256MB cap)."""
        blanket = {"prompt": "Empirical Test Low RAM"}
        base_cand = {
            "target_cpu_profile": "intel_core_ultra_5_125h",
            "target_npu_device": "INTEL_AI_BOOST_VPU_3720",
            "openvino_version": "2024.4",
            "max_ram_budget_mb": 128.0,
            "p99_latency_ms": 30.0,
            "cold_start_budget_ms": 250.0,
            "hardware_interlocks_required": False,
            "physical_actuator_latency_ms": 15.0,
        }
        cand = self.orchestrator._synthesize_downscaled_candidate(6, blanket, base_candidate=base_cand)

        model = HardwareRuntimeContract.model_validate(cand)
        self.assertLessEqual(model.max_ram_budget_mb, 256.0)
        self.assertEqual(model.target_npu_device, "INTEL_AI_BOOST_VPU_3720")

    def test_direct_synthesis_actuator_latency_hazard_preservation(self):
        """Case D: Base candidate with Therac-25 actuator hazard (latency=8000ms, interlocks=True)."""
        blanket = {"prompt": "Empirical Test Therac Hazard"}
        base_cand = {
            "target_cpu_profile": "intel_core_ultra_5_125h",
            "target_npu_device": "INTEL_AI_BOOST_VPU_3720",
            "openvino_version": "2024.4",
            "max_ram_budget_mb": 400.0,
            "p99_latency_ms": 45.0,
            "cold_start_budget_ms": 350.0,
            "hardware_interlocks_required": True,
            "physical_actuator_latency_ms": 8000.0,
        }
        cand = self.orchestrator._synthesize_downscaled_candidate(6, blanket, base_candidate=base_cand)

        model = HardwareRuntimeContract.model_validate(cand)
        self.assertTrue(model.hardware_interlocks_required)
        self.assertEqual(model.physical_actuator_latency_ms, 8000.0)
        self.assertLessEqual(model.max_ram_budget_mb, 256.0)

        # Invariant check must succeed
        inv_check = model.verify_physical_temporal_invariants()
        self.assertIsInstance(inv_check, HardwareRuntimeContract)

    def test_direct_synthesis_actuator_latency_over_1000ms_without_explicit_interlock(self):
        """Case E: Base candidate with latency=2500ms > 1000ms, interlocks initially False."""
        blanket = {"prompt": "Empirical Test Safe Task"}
        base_cand = {
            "target_cpu_profile": "intel_core_ultra_5_125h",
            "target_npu_device": "INTEL_AI_BOOST_VPU_3720",
            "openvino_version": "2024.4",
            "max_ram_budget_mb": 350.0,
            "p99_latency_ms": 35.0,
            "cold_start_budget_ms": 280.0,
            "hardware_interlocks_required": False,
            "physical_actuator_latency_ms": 2500.0,
        }
        cand = self.orchestrator._synthesize_downscaled_candidate(6, blanket, base_candidate=base_cand)

        # Downscale synthesis should activate interlocks because latency > 1000ms
        model = HardwareRuntimeContract.model_validate(cand)
        self.assertTrue(model.hardware_interlocks_required)
        self.assertEqual(model.physical_actuator_latency_ms, 2500.0)

    def test_direct_synthesis_low_actuator_latency(self):
        """Case F: Base candidate with safe actuator latency (latency=50ms, interlocks=False)."""
        blanket = {"prompt": "Standard edge mobile processing"}
        base_cand = {
            "target_cpu_profile": "intel_core_ultra_5_125h",
            "target_npu_device": "INTEL_AI_BOOST_VPU_3720",
            "openvino_version": "2024.4",
            "max_ram_budget_mb": 256.0,
            "p99_latency_ms": 35.0,
            "cold_start_budget_ms": 280.0,
            "hardware_interlocks_required": False,
            "physical_actuator_latency_ms": 50.0,
        }
        cand = self.orchestrator._synthesize_downscaled_candidate(6, blanket, base_candidate=base_cand)

        model = HardwareRuntimeContract.model_validate(cand)
        self.assertFalse(model.hardware_interlocks_required)
        self.assertEqual(model.physical_actuator_latency_ms, 50.0)

    def test_node6_flakiness_downscale_and_commit(self):
        """
        Simulate stage-gate flakiness on Node 6:
        - 3 consecutive failures on Node 6
        - Triggers apply_simplex_downgrade(6)
        - Verifies transition sequence: STATE_STAGE_GATE_VERIFY -> STATE_SIMPLEX_DOWNGRADE -> STATE_COMMITTED
        - Verifies artifact committed and present in artifacts dict
        """
        orch = DagOrchestrator(use_mock=True)
        call_count = {"count": 0}
        orig_verify = orch.gate_coordinator.verify_node_stage_gate

        def flaky_verify(node_id, candidate_dict, context=None):
            if node_id == 6:
                call_count["count"] += 1
                if call_count["count"] <= 3:
                    return False, f"Simulated gate flake {call_count['count']}", {}
            return orig_verify(node_id, candidate_dict, context)

        with patch.object(orch.gate_coordinator, "verify_node_stage_gate", side_effect=flaky_verify):
            result = orch.run("Test Simplex Flakiness Node 6")

        self.assertEqual(result.status, "SUCCESS")
        self.assertTrue(orch.node_downgraded[6])
        self.assertEqual(len(orch.simplex_downgrades_applied), 1)

        # Verify history transitions
        history_transitions = [h["to"] for h in orch.node_fsms[6].history]
        self.assertIn(NodeState.STATE_STAGE_GATE_VERIFY.value, history_transitions)
        self.assertIn(NodeState.STATE_SIMPLEX_DOWNGRADE.value, history_transitions)
        self.assertEqual(history_transitions[-1], NodeState.STATE_COMMITTED.value)

        # Verify transition order: STAGE_GATE_VERIFY occurs before SIMPLEX_DOWNGRADE, which occurs before COMMITTED
        first_verify_idx = history_transitions.index(NodeState.STATE_STAGE_GATE_VERIFY.value)
        downgrade_idx = history_transitions.index(NodeState.STATE_SIMPLEX_DOWNGRADE.value)
        committed_idx = len(history_transitions) - 1

        self.assertLess(first_verify_idx, downgrade_idx)
        self.assertLess(downgrade_idx, committed_idx)

        # Verify artifact presence
        n6_filename = CANONICAL_FILENAMES[6]
        self.assertIn(n6_filename, orch.artifacts)
        artifact = orch.registry.get_by_id(6)
        self.assertIsNotNone(artifact)
        self.assertLessEqual(artifact.get("max_ram_budget_mb", 999.0), 256.0)
        self.assertEqual(artifact.get("target_npu_device"), "INTEL_AI_BOOST_VPU_3720")

    def test_node6_downscaled_under_tight_finance_capex_boundary(self):
        """
        Verify that downscaled Node 6 metadata (_cluster_size=1, _hardware_cost=150,000 RUB)
        successfully satisfies a tight Finance CaPEx budget (e.g. 200,000 RUB).
        Nominal 2-node cluster costs 300,000 RUB (exceeding 200,000 RUB).
        Downscaled 1-node cluster costs 150,000 RUB (under 200,000 RUB).
        """
        orch = DagOrchestrator(use_mock=True)

        # Inject tight max_hardware_capex on Node 2
        orig_run_pipeline = orch._execute_node_pipeline

        def custom_pipeline(node_id, user_prompt, **kwargs):
            res = orig_run_pipeline(node_id, user_prompt, **kwargs)
            if node_id == 2:
                # Set max_hardware_capex to 200,000 RUB (nominal Node 6 would violate: 300k > 200k)
                res["max_hardware_capex"] = 200000.0
                orch.registry.register(2, res, CANONICAL_FILENAMES[2])
                orch.artifacts[CANONICAL_FILENAMES[2]] = res
            return res

        call_count = {"count": 0}
        orig_verify = orch.gate_coordinator.verify_node_stage_gate

        def flaky_node6_then_check_capex(node_id, candidate_dict, context=None):
            if node_id == 6:
                call_count["count"] += 1
                if call_count["count"] <= 3:
                    return False, f"Flake {call_count['count']}", {}
            return orig_verify(node_id, candidate_dict, context)

        with patch.object(orch, "_execute_node_pipeline", side_effect=custom_pipeline):
            with patch.object(orch.gate_coordinator, "verify_node_stage_gate", side_effect=flaky_node6_then_check_capex):
                result = orch.run("Test Tight CaPEx With Node 6 Downscale")

        self.assertEqual(result.status, "SUCCESS")
        self.assertTrue(orch.node_downgraded[6])
        n6_artifact = orch.registry.get_by_id(6)
        self.assertIsNotNone(n6_artifact)

    def test_node6_permanent_failure_halts_in_terminal_failed(self):
        """
        Simulate unresolvable failure on Node 6:
        Even after Simplex downscale, the gate rejects.
        Verifies:
        - ZeroTrustGateFailure is raised
        - Node 6 transitions to STATE_TERMINAL_FAILED
        - No artifact committed for Node 6
        """
        orch = DagOrchestrator(use_mock=True)

        def permanent_fail_node6(node_id, candidate_dict, context=None):
            if node_id == 6:
                return False, "Permanent hardware specification failure", {}
            return True, "Pass", {}

        with patch.object(orch.gate_coordinator, "verify_node_stage_gate", side_effect=permanent_fail_node6):
            with self.assertRaises(ZeroTrustGateFailure) as cm:
                orch.run("Test Permanent Failure Node 6")

            self.assertIn("Ministry_6_Hardware", cm.exception.gate_name)

        self.assertEqual(orch.fsm_states[6], NodeState.STATE_TERMINAL_FAILED.value)
        self.assertIsNone(orch.registry.get_by_id(6))
        self.assertNotIn(CANONICAL_FILENAMES[6], orch.artifacts)

    def test_therac_hazard_coupled_with_node6_simplex_downscale(self):
        """
        Adversarial combination:
        Therac-25 hazard active (requires Saga veto to Node 5 to inject interlocks)
        AND Node 6 experiences stage-gate flakiness during re-execution, triggering Simplex downscale.
        Verifies:
        - 1 Saga compensation to Node 5
        - 1 Simplex downscale applied to Node 6
        - Downscaled Node 6 preserves interlocks (physical_actuator_latency_ms=8000, hardware_interlocks_required=True)
        - All 7 nodes commit to STATE_COMMITTED
        - All 7 artifacts present in output
        """
        orch = DagOrchestrator(use_mock=True)
        gate_6_attempts = {"count": 0}
        orig_verify = orch.gate_coordinator.verify_node_stage_gate

        def flaky_gate_on_node6(node_id, candidate_dict, context=None):
            if node_id == 6:
                gate_6_attempts["count"] += 1
                # Fail the first 3 times Node 6 hits stage gate
                if gate_6_attempts["count"] <= 3:
                    return False, f"Simulated gate failure attempt {gate_6_attempts['count']}", {}
            return orig_verify(node_id, candidate_dict, context)

        with patch.object(orch.gate_coordinator, "verify_node_stage_gate", side_effect=flaky_gate_on_node6):
            result = orch.run(
                prompt="Therac-25 medical radiation therapy system with high latency beam actuator",
                simulate_therac_hazard=True,
            )

        self.assertEqual(result.status, "SUCCESS")
        self.assertEqual(len(orch.saga_compensations_executed), 1)
        self.assertEqual(len(orch.simplex_downgrades_applied), 1)
        self.assertEqual(orch.simplex_downgrades_applied[0]["node_id"], 6)

        # Invariants on committed Node 6 artifact
        n6_art = orch.registry.get_by_id(6)
        self.assertIsNotNone(n6_art)
        self.assertTrue(n6_art.get("hardware_interlocks_required"))
        self.assertEqual(n6_art.get("physical_actuator_latency_ms"), 8000.0)
        self.assertLessEqual(n6_art.get("max_ram_budget_mb"), 256.0)

        # Invariant on committed Node 5 artifact (interlock endpoint present)
        n5_art = orch.registry.get_by_id(5)
        self.assertIsNotNone(n5_art)
        self.assertTrue(any("/interlock" in ep.get("path", "") for ep in n5_art.get("endpoints", [])))

        # All 7 nodes must be in STATE_COMMITTED
        for nid in range(1, 8):
            self.assertEqual(
                orch.fsm_states[nid],
                NodeState.STATE_COMMITTED.value,
                f"Node {nid} not committed!",
            )
        self.assertEqual(len(orch.artifacts), 7)


if __name__ == "__main__":
    unittest.main()
