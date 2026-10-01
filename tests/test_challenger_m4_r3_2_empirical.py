"""
tests/test_challenger_m4_r3_2_empirical.py
=============================================================================
Milestone 4 Round 3 Challenger Empirical Stress Suite:
Independent verification of DAG pipeline execution under nominal, forced
Simplex downgrade, Therac-25 hazard resolution, and transitive cascading
rollback scenarios in core/orchestrator.py.
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

from core.schemas import (
    StrategyCJMContract,
    FinanceBudgetContract,
    LegalComplianceContract,
    SecurityPolicyContract,
    SystemAnalysisContract,
    HardwareRuntimeContract,
    VVQualityContract,
)
from core.ministries.nodes import CandidateDict
from core.orchestrator import (
    DagOrchestrator,
    DagTopology,
    NodeState,
    NodeFSM,
    ArtifactRegistry,
    PipelineResult,
    InvalidStateTransitionError,
    GlobalBudgetExhaustedError,
    SagaVetoError,
    ZeroTrustGateFailure,
    CANONICAL_FILENAMES,
    NODE_SCHEMAS,
)


class TestEmpiricalNominalPipeline(unittest.TestCase):
    """
    Scenario 1: End-to-End Nominal Pipeline Run
    - Run DagOrchestrator(use_mock=True).run(prompt="...")
    - Verify all 7 nodes reach STATE_COMMITTED
    - Verify all 7 artifacts are valid Pydantic V2 schemas
    """

    def setUp(self):
        self.orchestrator = DagOrchestrator(use_mock=True)

    def test_nominal_e2e_execution_all_7_nodes_committed(self):
        prompt = "Enterprise Autonomous Multi-Agent Cognitive Platform"
        result = self.orchestrator.run(prompt=prompt)

        # 1. Pipeline result status
        self.assertEqual(result.status, "SUCCESS")
        self.assertEqual(len(result), 7)

        # 2. Check FSM states of all 7 nodes
        for node_id in range(1, 8):
            state = self.orchestrator.fsm_states.get(node_id)
            self.assertEqual(
                state,
                NodeState.STATE_COMMITTED.value,
                f"Node {node_id} failed to reach STATE_COMMITTED; actual state: {state}",
            )
            # Verify internal FSM instance matches
            self.assertEqual(
                self.orchestrator.node_fsms[node_id].current_state,
                NodeState.STATE_COMMITTED,
            )

        # 3. Verify all 7 canonical artifacts exist in registry and result
        expected_filenames = [
            "PRD_Specification.json",
            "Unit_Economics_Budget.json",
            "Compliance_Attestation.json",
            "Security_Policy.agentpolicy",
            "System_Contracts.json",
            "Hardware_Runtime_Manifest.json",
            "Release_Certified_Artifacts.json",
        ]
        for fname in expected_filenames:
            self.assertIn(fname, result, f"Missing artifact {fname} in pipeline result")
            self.assertIn(fname, self.orchestrator.artifacts, f"Missing {fname} in orchestrator artifacts")

        # 4. Strict Pydantic V2 schema validation for all 7 artifacts
        contract_m1 = StrategyCJMContract.model_validate(result["PRD_Specification.json"])
        contract_m2 = FinanceBudgetContract.model_validate(result["Unit_Economics_Budget.json"])
        contract_m3 = LegalComplianceContract.model_validate(result["Compliance_Attestation.json"])
        contract_m4 = SecurityPolicyContract.model_validate(result["Security_Policy.agentpolicy"])
        contract_m5 = SystemAnalysisContract.model_validate(result["System_Contracts.json"])
        contract_m6 = HardwareRuntimeContract.model_validate(result["Hardware_Runtime_Manifest.json"])
        contract_m7 = VVQualityContract.model_validate(result["Release_Certified_Artifacts.json"])

        self.assertIsNotNone(contract_m1)
        self.assertIsNotNone(contract_m2)
        self.assertIsNotNone(contract_m3)
        self.assertIsNotNone(contract_m4)
        self.assertIsNotNone(contract_m5)
        self.assertIsNotNone(contract_m6)
        self.assertIsNotNone(contract_m7)

        # Invariants on models
        self.assertGreaterEqual(contract_m2.lifetime_value / contract_m2.customer_acquisition_cost, 3.0)
        self.assertLessEqual(contract_m6.max_ram_budget_mb, 512.0)
        self.assertLessEqual(contract_m6.p99_latency_ms, 50.0)

    def test_nominal_disk_export_contract_compliance(self):
        """Verifies disk export produces 7 valid JSON files identical to in-memory models."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            orch = DagOrchestrator(use_mock=True, output_dir=tmp_dir)
            res = orch.run("Disk Export Nominal Test")
            self.assertEqual(res.status, "SUCCESS")

            for nid, fname in CANONICAL_FILENAMES.items():
                file_path = Path(tmp_dir) / fname
                self.assertTrue(file_path.exists(), f"Export file {fname} not found on disk")
                with open(file_path, "r", encoding="utf-8") as f:
                    disk_data = json.load(f)
                schema_cls = NODE_SCHEMAS[nid]
                validated = schema_cls.model_validate(disk_data)
                self.assertIsNotNone(validated)


class TestEmpiricalTherac25HazardWithDownscaling(unittest.TestCase):
    """
    Scenario 2: Therac-25 Hazard Simulation with Downscaling
    - Run with simulate_therac_hazard=True
    - Verify Node 6 detects latency > 1000ms, triggers Saga compensation against Node 5
    - Verify Node 5 rolls back, evolves /api/v1/hardware/interlock-status endpoint
    - Verify Node 6 enables interlocks
    - Verify both nodes commit cleanly
    - STRESS: Couple Therac-25 hazard with Simplex downscaling on Node 6!
    """

    def setUp(self):
        self.orchestrator = DagOrchestrator(use_mock=True)

    def test_therac25_saga_compensation_lifecycle(self):
        prompt = "Oncology Radiation Therapy Control Unit"
        result = self.orchestrator.run(prompt=prompt, simulate_therac_hazard=True)

        # 1. Exactly 1 Saga compensation executed
        compensations = self.orchestrator.saga_compensations_executed
        self.assertEqual(len(compensations), 1)
        comp = compensations[0]

        # 2. Vetoing and target nodes
        self.assertEqual(comp["vetoing_node"], 6)
        self.assertEqual(comp["target_node"], 5)
        self.assertEqual(comp["hazard_code"], "THERAC_25_ACTUATOR_COLLISION")
        self.assertIn("Therac-25 Hazard", comp["prescription"])

        # 3. Node 5 evolved OpenAPI specification
        n5_art = result["System_Contracts.json"]
        self.assertIn("endpoints", n5_art)
        interlock_endpoints = [
            ep for ep in n5_art["endpoints"]
            if "/api/v1/hardware/interlock-status" in ep.get("path", "")
        ]
        self.assertEqual(len(interlock_endpoints), 1, "Node 5 must contain /api/v1/hardware/interlock-status")
        ep = interlock_endpoints[0]
        self.assertEqual(ep["method"], "GET")
        self.assertTrue(ep["idempotent"])
        self.assertEqual(ep["timeout_ms"], 800)

        # 4. Node 6 enabled interlocks with 8000ms actuator latency
        n6_art = result["Hardware_Runtime_Manifest.json"]
        self.assertTrue(n6_art["hardware_interlocks_required"])
        self.assertEqual(n6_art["physical_actuator_latency_ms"], 8000.0)

        # 5. Temporal invariant verification on HardwareRuntimeContract passes cleanly
        hw_model = HardwareRuntimeContract.model_validate(n6_art)
        hw_model.verify_physical_temporal_invariants()

        # 6. Both nodes commit cleanly
        self.assertEqual(self.orchestrator.fsm_states[5], NodeState.STATE_COMMITTED.value)
        self.assertEqual(self.orchestrator.fsm_states[6], NodeState.STATE_COMMITTED.value)

        # 7. Entire pipeline commits
        for nid in range(1, 8):
            self.assertEqual(self.orchestrator.fsm_states[nid], NodeState.STATE_COMMITTED.value)
        self.assertEqual(result.status, "SUCCESS")

    def test_coupled_therac25_hazard_and_simplex_downscale_on_node6(self):
        """
        Adversarial combination:
        Trigger Therac-25 hazard AND force Simplex downscaling on Node 6.
        Verify:
        - Node 6 undergoes Simplex downscale (Frugal profile, RAM <= 256MB, INTEL_AI_BOOST_VPU_3720)
        - Node 6 PRESERVES the Therac-25 interlock requirement (hardware_interlocks_required=True, latency=8000ms)
        - Node 6 stage-gate validation passes with 0 extra_forbidden errors
        - Both Node 5 and Node 6 commit cleanly
        """
        orch = DagOrchestrator(use_mock=True)

        call_count = {"count": 0}
        orig_verify = orch.gate_coordinator.verify_node_stage_gate

        def flaky_node6_verify(node_id, candidate_dict, context=None):
            if node_id == 6:
                call_count["count"] += 1
                # Fail first 3 verification attempts on Node 6 to force Simplex downscaling
                if call_count["count"] <= 3:
                    return False, f"Simulated gate rejection {call_count['count']}", {}
            return orig_verify(node_id, candidate_dict, context)

        with patch.object(orch.gate_coordinator, "verify_node_stage_gate", side_effect=flaky_node6_verify):
            result = orch.run("Radiation Beam Device under Resource Strain", simulate_therac_hazard=True)

        self.assertEqual(result.status, "SUCCESS")

        # Verify Simplex downgrade was applied to Node 6
        downgraded_ids = [d["node_id"] for d in orch.simplex_downgrades_applied]
        self.assertIn(6, downgraded_ids, "Node 6 must have received Simplex downscale")

        # Verify Node 6 FSM went through STATE_SIMPLEX_DOWNGRADE
        n6_history = [h["to"] for h in orch.node_fsms[6].history]
        self.assertIn(NodeState.STATE_SIMPLEX_DOWNGRADE.value, n6_history)

        # Verify Saga compensation was ALSO executed against Node 5
        self.assertGreaterEqual(len(orch.saga_compensations_executed), 1)
        comp = orch.saga_compensations_executed[0]
        self.assertEqual(comp["vetoing_node"], 6)
        self.assertEqual(comp["target_node"], 5)

        # Verify Node 6 artifact properties: BOTH downscaled RAM AND Therac interlocks preserved
        hw_art = result["Hardware_Runtime_Manifest.json"]
        self.assertLessEqual(hw_art["max_ram_budget_mb"], 256.0)
        self.assertTrue(hw_art["hardware_interlocks_required"])
        self.assertEqual(hw_art["physical_actuator_latency_ms"], 8000.0)

        # Verify strict Pydantic V2 validation passes without extra forbidden fields
        hw_model = HardwareRuntimeContract.model_validate(hw_art)
        self.assertIsNotNone(hw_model)
        hw_model.verify_physical_temporal_invariants()

        # Both nodes and entire pipeline committed
        for nid in range(1, 8):
            self.assertEqual(orch.fsm_states[nid], NodeState.STATE_COMMITTED.value)


class TestEmpiricalTransitiveRollbackUnderDownscaledState(unittest.TestCase):
    """
    Scenario 3: Transitive Rollback Under Downscaled State
    - Invalidate Node 1 or Node 2 after Simplex downscaling on Node 6.
    - Verify full transitive closure of descendants reverts to STATE_IDLE with artifacts purged.
    - Verify pipeline can recover and commit all nodes.
    """

    def setUp(self):
        self.orchestrator = DagOrchestrator(use_mock=True)

    def test_transitive_rollback_of_descendants_after_node6_downscaled(self):
        """
        1. Run pipeline until all nodes are committed, with Node 6 downscaled.
        2. Invalidate Node 1 via Saga compensation.
        3. Verify all descendants of Node 1 {2, 3, 4, 5, 6, 7} revert to STATE_IDLE.
        4. Verify all artifacts of descendants are purged from registry and artifacts dict.
        """
        orch = self.orchestrator

        # Run nominal pipeline first so all 7 nodes are COMMITTED
        res = orch.run("Initial pipeline run for rollback test")
        self.assertEqual(res.status, "SUCCESS")

        # Now apply simplex downgrade on Node 6
        orch.apply_simplex_downgrade(6, reason="Simplex downscale before rollback")
        self.assertTrue(orch.node_downgraded[6])

        # Sanity check: Node 1 is COMMITTED, all 7 artifacts in registry
        self.assertEqual(orch.fsm_states[1], NodeState.STATE_COMMITTED.value)
        for nid in range(1, 8):
            self.assertIsNotNone(orch.registry.get_by_id(nid))
            self.assertIn(CANONICAL_FILENAMES[nid], orch.artifacts)

        # Now trigger Saga compensation invalidating Node 1
        orch.execute_saga_compensation(
            vetoing_node=3,  # Legal vetoes Strategy CJM
            target_node=1,
            prescription="Regulatory overhaul requires Strategy revision",
            hazard_code="REGULATORY_INCOMPATIBILITY",
        )

        # Node 1 must be in STATE_SYSTEM2_GENERATE (ready for re-generation)
        self.assertEqual(orch.fsm_states[1], NodeState.STATE_SYSTEM2_GENERATE.value)
        self.assertIsNone(orch.registry.get_by_id(1))
        self.assertNotIn(CANONICAL_FILENAMES[1], orch.artifacts)

        # All descendants of Node 1: {2, 3, 4, 5, 6, 7} MUST be in STATE_IDLE
        descendants = orch.topology.get_descendants(1)
        self.assertEqual(descendants, {2, 3, 4, 5, 6, 7})

        for desc_id in descendants:
            state = orch.fsm_states[desc_id]
            self.assertEqual(
                state,
                NodeState.STATE_IDLE.value,
                f"Descendant Node {desc_id} was not reset to STATE_IDLE; actual: {state}",
            )
            # Artifact purged from registry
            self.assertIsNone(
                orch.registry.get_by_id(desc_id),
                f"Descendant Node {desc_id} artifact was NOT purged from registry",
            )
            # Artifact purged from orchestrator artifacts dict
            self.assertNotIn(
                CANONICAL_FILENAMES[desc_id],
                orch.artifacts,
                f"Descendant Node {desc_id} artifact was NOT purged from artifacts dict",
            )
            # Retry count reset to 0
            self.assertEqual(orch.retry_counts[desc_id], 0)

    def test_transitive_rollback_targeting_node2_finance(self):
        """
        Invalidating Node 2 (Finance):
        Descendants of Node 2 include {5, 6, 7}.
        Non-descendants: Node 1 (Strategy), Node 3 (Legal), Node 4 (Infosec) must REMAIN COMMITTED.
        """
        orch = self.orchestrator

        # Run nominal pipeline first so all 7 nodes are COMMITTED
        res = orch.run("Initial pipeline run for Node 2 rollback test")
        self.assertEqual(res.status, "SUCCESS")

        # Descendants of Node 2 are {4, 5, 6, 7}
        descendants_n2 = orch.topology.get_descendants(2)
        self.assertEqual(descendants_n2, {4, 5, 6, 7})

        # Invalidate Node 2
        orch.execute_saga_compensation(
            vetoing_node=5,
            target_node=2,
            prescription="Budget deficit for API architecture",
        )

        # Node 2 is re-generating
        self.assertEqual(orch.fsm_states[2], NodeState.STATE_SYSTEM2_GENERATE.value)
        self.assertIsNone(orch.registry.get_by_id(2))

        # Descendants {4, 5, 6, 7} are rolled back to STATE_IDLE and purged
        for desc_id in descendants_n2:
            self.assertEqual(orch.fsm_states[desc_id], NodeState.STATE_IDLE.value)
            self.assertIsNone(orch.registry.get_by_id(desc_id))
            self.assertNotIn(CANONICAL_FILENAMES[desc_id], orch.artifacts)

        # Non-descendants Node 1 (Strategy) and Node 3 (Legal) remain COMMITTED!
        self.assertEqual(orch.fsm_states[1], NodeState.STATE_COMMITTED.value)
        self.assertIsNotNone(orch.registry.get_by_id(1))
        self.assertEqual(orch.fsm_states[3], NodeState.STATE_COMMITTED.value)
        self.assertIsNotNone(orch.registry.get_by_id(3))


class TestEmpiricalTerminalFailureGlobalBudget(unittest.TestCase):
    """
    Scenario 4: Terminal Failure on Global Budget
    - Verify K_max > 10 transitions safely to STATE_TERMINAL_FAILED without crashing.
    - Verify execution history and exception invariants.
    """

    def test_global_budget_exhaustion_on_excessive_compensations(self):
        """
        Trigger 11 Saga compensations:
        At K = 11 (> K_max = 10), execute_saga_compensation must raise GlobalBudgetExhaustedError
        and place target node into STATE_TERMINAL_FAILED.
        """
        orch = DagOrchestrator(use_mock=True)
        orch.max_global_iterations = 10

        # Run 10 valid compensations
        for i in range(10):
            # Target alternating between 2 and 5
            target = 5 if i % 2 == 0 else 2
            orch.execute_saga_compensation(
                vetoing_node=6,
                target_node=target,
                prescription=f"Compensating cycle {i+1}",
            )
            self.assertEqual(orch.global_iteration_k, i + 1)

        self.assertEqual(orch.global_iteration_k, 10)

        # 11th compensation must breach budget
        with self.assertRaises(GlobalBudgetExhaustedError) as cm:
            orch.execute_saga_compensation(
                vetoing_node=6,
                target_node=5,
                prescription="11th veto exceeding budget",
            )

        self.assertIn("Global coordination budget K_max (10) exceeded!", str(cm.exception))
        self.assertEqual(orch.fsm_states[5], NodeState.STATE_TERMINAL_FAILED.value)
        self.assertEqual(orch.node_fsms[5].current_state, NodeState.STATE_TERMINAL_FAILED)

    def test_global_budget_exhaustion_on_excessive_simplex_downscales(self):
        """
        Breaching budget via apply_simplex_downgrade transitions to STATE_TERMINAL_FAILED.
        """
        orch = DagOrchestrator(use_mock=True)
        orch.max_global_iterations = 5
        orch.global_iteration_k = 5  # Already at max

        with self.assertRaises(GlobalBudgetExhaustedError):
            orch.apply_simplex_downgrade(node_id=6, reason="Forced budget test")

        self.assertEqual(orch.fsm_states[6], NodeState.STATE_TERMINAL_FAILED.value)
        self.assertEqual(orch.node_fsms[6].current_state, NodeState.STATE_TERMINAL_FAILED)

    def test_run_terminates_gracefully_when_budget_exhausted(self):
        """
        Verifies that when DagOrchestrator.run() encounters budget exhaustion,
        it raises GlobalBudgetExhaustedError, appends FAILED status to execution_history,
        and leaves the failing node in STATE_TERMINAL_FAILED without corrupting state.
        """
        orch = DagOrchestrator(use_mock=True)
        orch.max_global_iterations = 0  # Force immediate exhaustion

        with self.assertRaises(GlobalBudgetExhaustedError):
            orch.run("Test Budget Trip", simulate_therac_hazard=True)

        # Failing node is in STATE_TERMINAL_FAILED
        terminal_nodes = [nid for nid, st in orch.fsm_states.items() if st == NodeState.STATE_TERMINAL_FAILED.value]
        self.assertGreater(len(terminal_nodes), 0)

        # Execution history contains failed record
        self.assertEqual(len(orch.execution_history), 1)
        record = orch.execution_history[0]
        self.assertEqual(record["status"], "FAILED")
        self.assertIn("Global coordination budget", record["error"])


class TestEmpiricalCandidateDictAndExtraForbiddenIntegrity(unittest.TestCase):
    """
    Scenario 5: Schema Isolation & Extra Forbidden Stress Probe
    - Direct probe into CandidateDict behavior
    - Verify that CandidateDict under NO circumstance exposes _cluster_size, _gpu_enabled,
      or _hardware_cost to Pydantic V2 or json.dumps().
    - Verify that bare forbidden keys are absent.
    """

    def test_candidate_dict_strict_pydantic_isolation(self):
        raw = {
            "target_cpu_profile": "intel_core_ultra_5_125h",
            "target_npu_device": "INTEL_AI_BOOST_VPU_3720",
            "openvino_version": "2024.4",
            "max_ram_budget_mb": 256.0,
            "p99_latency_ms": 35.0,
            "cold_start_budget_ms": 50.0,
            "hardware_interlocks_required": True,
            "physical_actuator_latency_ms": 8000.0,
            "_cluster_size": 1,
            "_gpu_enabled": False,
            "_hardware_cost": 150000.0,
        }
        cand = CandidateDict(raw)

        # Direct items() must not contain underscore keys
        for k, v in cand.items():
            self.assertFalse(k.startswith("_"), f"Underscore key leaked in items(): {k}")

        # Direct keys() must not contain underscore keys
        for k in cand.keys():
            self.assertFalse(k.startswith("_"), f"Underscore key leaked in keys(): {k}")

        # Subscripting can still access metadata
        self.assertEqual(cand["_cluster_size"], 1)
        self.assertEqual(cand["_gpu_enabled"], False)
        self.assertEqual(cand["_hardware_cost"], 150000.0)

        # Pydantic V2 validation MUST succeed without extra_forbidden
        model = HardwareRuntimeContract.model_validate(cand)
        self.assertIsInstance(model, HardwareRuntimeContract)

        # json.dumps must not contain metadata keys
        serialized = json.dumps(cand)
        self.assertNotIn("_cluster_size", serialized)
        self.assertNotIn("_gpu_enabled", serialized)
        self.assertNotIn("_hardware_cost", serialized)

    def test_synthesize_downscaled_candidate_node6_all_variations(self):
        """
        Synthesize downscaled candidate across multiple baseline variations:
        Ensure that every synthesized candidate passes HardwareRuntimeContract validation.
        """
        orch = DagOrchestrator(use_mock=True)
        blanket = {"prompt": "Diverse synthesis test"}

        variations = [
            None,
            {"target_npu_device": "INTEL_ARC_GPU", "max_ram_budget_mb": 500.0},
            {"hardware_interlocks_required": True, "physical_actuator_latency_ms": 5000.0},
            {"physical_actuator_latency_ms": 2000.0},  # No explicit interlock, but latency > 1000
            {"physical_actuator_latency_ms": 20.0, "hardware_interlocks_required": False},
        ]

        for base in variations:
            cand = orch._synthesize_downscaled_candidate(6, blanket, base_candidate=base)
            self.assertIsInstance(cand, CandidateDict)
            # Ensure bare keys are popped
            for forbidden in ("cluster_size", "gpu_enabled", "hardware_cost"):
                self.assertNotIn(forbidden, cand)
                self.assertNotIn(forbidden, list(cand.keys()))

            # Must validate cleanly
            model = HardwareRuntimeContract.model_validate(cand)
            self.assertLessEqual(model.max_ram_budget_mb, 256.0)
            self.assertNotEqual(model.target_npu_device, "INTEL_ARC_GPU")


if __name__ == "__main__":
    unittest.main(verbosity=2)
