"""
tests/test_wave4_state_certification.py
=============================================================================
Universal Cognitive Decomposition Engine (UCDE) - Wave 4 Test Suite.
Verifies State Certification, Industrial Hardening, ISO Standards,
Hardware Windowed Watchdog RTL Synthesis, Persistent Saga WAL, and MCP Tools 24-30.
=============================================================================
"""

import json
import unittest

from core.generators import (
    UXAutomationLevel,
    DegradationTrigger,
    DegradationTransition,
    HITLHandoverDossier,
    GracefulDegradationPlan,
    UXFallbackEngine,
    AccountingPhase,
    ExpenseItem,
    CapitalizationChecklist,
    IAS38AuditDossier,
    IAS38Auditor,
    ControlStatus,
    ISO42001AIMSReport,
    ISO42001AuditGenerator,
    FstecAssuranceLevel,
    Gost56939Dossier,
    Gost56939Auditor,
    SagaStepStatus,
    PersistentSagaEngine,
)
from core.hardware import (
    WatchdogWindowConfig,
    HardwareWatchdogSimulator,
    WatchdogCircuitSynthesizer,
)
from core.quality import (
    CIFormalAuditStand,
)
from core.mcp_server import McpServer


class TestWave4StateCertification(unittest.TestCase):
    """Test suite validating Wave 4 departmental generators and MCP server tools."""

    def setUp(self):
        self.server = McpServer()

    # =========================================================================
    # 1. Dept 1: UX Fallback & ISO 9241-210 Statecharts
    # =========================================================================
    def test_dept1_ux_fallback_engine(self):
        engine = UXFallbackEngine(full_threshold=0.85, supervised_threshold=0.70, hitl_threshold=0.50)

        # Confidence >= 0.85 -> FULL_AUTOMATION
        lvl1 = engine.evaluate_telemetry(confidence=0.92)
        self.assertEqual(lvl1, UXAutomationLevel.FULL_AUTOMATION)

        # 0.70 <= Confidence < 0.85 -> SUPERVISED_ASSIST
        lvl2 = engine.evaluate_telemetry(confidence=0.78)
        self.assertEqual(lvl2, UXAutomationLevel.SUPERVISED_ASSIST)

        # 0.50 <= Confidence < 0.70 -> HITL_CONFIRMATION
        lvl3 = engine.evaluate_telemetry(confidence=0.62)
        self.assertEqual(lvl3, UXAutomationLevel.HITL_CONFIRMATION)

        # Confidence < 0.50 -> DETERMINISTIC_FALLBACK
        lvl4 = engine.evaluate_telemetry(confidence=0.35)
        self.assertEqual(lvl4, UXAutomationLevel.DETERMINISTIC_FALLBACK)

        # Hardware fault -> EMERGENCY_OPERATOR_TAKEOVER
        lvl5 = engine.evaluate_telemetry(confidence=0.99, hardware_fault=True)
        self.assertEqual(lvl5, UXAutomationLevel.EMERGENCY_OPERATOR_TAKEOVER)

        # Plan & Mermaid export
        plan = engine.generate_default_plan("TestSystem")
        self.assertEqual(len(plan.transitions), 4)
        mermaid = engine.export_mermaid_statechart(plan)
        self.assertIn("stateDiagram-v2", mermaid)
        self.assertIn("FULL_AUTOMATION --> SUPERVISED_ASSIST", mermaid)

        # Handover dossier creation
        dossier = engine.create_handover_dossier(0.65, "hash12345678", ["Conflict in AC-01"])
        self.assertEqual(dossier.triggering_confidence, 0.65)
        self.assertEqual(dossier.state_snapshot_id, "hash12345678")

    # =========================================================================
    # 2. Dept 2: IAS 38 & IFRS 15 Capitalization Auditor
    # =========================================================================
    def test_dept2_ias38_auditor_capitalization_and_amortization(self):
        auditor = IAS38Auditor(useful_life_months=36)

        expenses = [
            ExpenseItem(item_id="EXP-01", description="Research LLM", phase=AccountingPhase.RESEARCH, amount_rub=200000.0, cost_category="Compute_Cloud"),
            ExpenseItem(item_id="EXP-02", description="Deterministic Architecture", phase=AccountingPhase.DEVELOPMENT, amount_rub=1000000.0, cost_category="Personnel_RND"),
            ExpenseItem(item_id="EXP-03", description="Testing Framework", phase=AccountingPhase.DEVELOPMENT, amount_rub=800000.0, cost_category="Tooling"),
        ]

        # Case A: All 6 criteria satisfied -> Capitalized as Intangible Asset
        valid_checklist = CapitalizationChecklist(
            technical_feasibility=True,
            intention_to_complete=True,
            ability_to_use_or_sell=True,
            probable_future_benefits=True,
            resource_availability=True,
            reliable_cost_measurement=True,
        )
        dossier = auditor.audit_project("Cognitive System", "2026-10-01", expenses, valid_checklist)
        self.assertEqual(dossier.total_research_opex, 200000.0)
        self.assertEqual(dossier.total_development_expenditure, 1800000.0)
        self.assertEqual(dossier.capitalized_asset_initial_cost, 1800000.0)
        self.assertEqual(dossier.auditor_opinion, "IAS38_FULLY_COMPLIANT_CAPITALIZED")
        self.assertEqual(len(dossier.amortization_schedule), 36)
        # Final month carrying amount must close at 0.0
        self.assertEqual(dossier.amortization_schedule[-1].closing_carrying_amount, 0.0)

        # Case B: Criterion missing -> Expensed immediately to OPEX
        invalid_checklist = CapitalizationChecklist(
            technical_feasibility=False,
            intention_to_complete=True,
            ability_to_use_or_sell=True,
            probable_future_benefits=True,
            resource_availability=True,
            reliable_cost_measurement=True,
        )
        dossier_fail = auditor.audit_project("Cognitive System", "2026-10-01", expenses, invalid_checklist)
        self.assertEqual(dossier_fail.capitalized_asset_initial_cost, 0.0)
        self.assertEqual(dossier_fail.total_research_opex, 2000000.0)
        self.assertEqual(dossier_fail.auditor_opinion, "IAS38_EXPENSED_TO_OPEX_CRITERIA_UNMET")
        self.assertEqual(len(dossier_fail.amortization_schedule), 0)

    # =========================================================================
    # 3. Dept 3: ISO/IEC 42001:2023 AIMS Audit Generator
    # =========================================================================
    def test_dept3_iso42001_aims_generator(self):
        generator = ISO42001AuditGenerator()
        dossier = generator.generate_dossier("Cognitive Harness Engine")

        self.assertEqual(dossier.system_name, "Cognitive Harness Engine")
        self.assertEqual(dossier.certification_readiness, "READY_FOR_STAGE_2_AUDIT")
        self.assertGreaterEqual(dossier.controls_implemented_count, 9)
        self.assertEqual(dossier.controls_implemented_count, dossier.total_controls_count)
        self.assertGreaterEqual(len(dossier.risk_register), 3)
        self.assertEqual(dossier.impact_assessment.societal_impact_rating, "BENEFICIAL_LOW_RISK")

    # =========================================================================
    # 4. Dept 4: ГОСТ Р 56939-2024 FSTEC Safe Software Dossier
    # =========================================================================
    def test_dept4_gost56939_auditor(self):
        auditor = Gost56939Auditor()
        dossier = auditor.generate_dossier(
            system_name="Cognitive Harness Architect",
            target_level=FstecAssuranceLevel.UD4,
            release_sha256="abc123sha256",
            mean_latency_us=12.5,
        )

        self.assertEqual(dossier.target_assurance_level, FstecAssuranceLevel.UD4)
        self.assertEqual(dossier.certification_verdict, "CERTIFIED_SAFE_SOFTWARE")
        self.assertTrue(dossier.binary_hardening.aslr_enabled)
        self.assertTrue(dossier.binary_hardening.dep_nx_enabled)
        self.assertTrue(dossier.dast_evidence.sla_sub_millisecond_met)
        self.assertIn("abc123sha256", dossier.gost_hash_streebog256)

    # =========================================================================
    # 5. Dept 5: Distributed Saga with SQLite WAL & Outbox
    # =========================================================================
    def test_dept5_persistent_saga_wal_and_compensation(self):
        saga = PersistentSagaEngine(":memory:")
        saga.start_saga("SAGA-TEST-001", "Financial & Hardware Allocation")

        step1 = saga.add_step("SAGA-TEST-001", "S1", "Reserve_Capital", "reserve()", "refund()", {"amount": 100})
        saga.commit_step("S1", {"status": "RESERVED"})

        step2 = saga.add_step("SAGA-TEST-001", "S2", "Allocate_NPU_RAM", "allocate()", "free()", {"mb": 256})
        saga.commit_step("S2", {"status": "ALLOCATED"})

        step3 = saga.add_step("SAGA-TEST-001", "S3", "Deploy_Binary", "deploy()", "rollback()", {"v": "2.4.0"})

        # Simulate failure at step 3 -> triggers reverse compensation
        compensated = saga.fail_and_compensate("S3", "Hardware Interlock Tripped")
        self.assertEqual(compensated, ["S2", "S1"])

        # Crash recovery replay
        report = saga.recover_and_replay("SAGA-TEST-001")
        self.assertTrue(report.recovery_successful)
        self.assertEqual(report.final_saga_status, "ABORTED_COMPENSATED")
        self.assertEqual(report.compensated_steps, 2)
        self.assertEqual(report.committed_steps, 0)

        # Outbox event staging
        event = saga.enqueue_outbox_event("EVT-01", "SAGA-TEST-001", "SagaAborted", {"reason": "Interlock"})
        self.assertEqual(event.event_id, "EVT-01")
        self.assertFalse(event.is_published)

    # =========================================================================
    # 6. Dept 6: Hardware Windowed Watchdog & RTL Synthesis
    # =========================================================================
    def test_dept6_hardware_watchdog_and_verilog_synthesis(self):
        # A. Register simulator
        cfg = WatchdogWindowConfig(min_window_ms=50.0, max_window_ms=200.0)
        sim = HardwareWatchdogSimulator(cfg)

        # First pulse sets baseline
        t1 = sim.feed(100.0)
        self.assertEqual(t1.status, "HEALTHY_RUNNING")
        self.assertFalse(t1.interlock_engaged)

        # Pulse within window (delta = 100ms) -> HEALTHY
        t2 = sim.feed(200.0)
        self.assertEqual(t2.status, "HEALTHY_RUNNING")
        self.assertFalse(t2.interlock_engaged)

        # Early pulse (delta = 20ms < 50ms) -> FAULT_EARLY_PULSE
        t3 = sim.feed(220.0)
        self.assertEqual(t3.status, "FAULT_EARLY_PULSE")
        self.assertTrue(t3.interlock_engaged)

        # Reset and test late pulse
        sim.force_reset()
        sim.feed(100.0)
        t_late = sim.feed(400.0)  # delta = 300ms > 200ms
        self.assertEqual(t_late.status, "FAULT_TIMEOUT")
        self.assertTrue(t_late.interlock_engaged)

        # B. RTL Circuit Synthesizer
        synth = WatchdogCircuitSynthesizer()
        rtl = synth.synthesize(cfg)
        self.assertIn("module watchdog_interlock", rtl.verilog_rtl)
        self.assertIn("CNT_MIN", rtl.verilog_rtl)
        self.assertIn("CNT_MAX", rtl.verilog_rtl)
        self.assertIn("entity watchdog_interlock_tb", rtl.vhdl_testbench)
        self.assertEqual(rtl.target_fpga_family, "Intel Cyclone V / Agilex FPGA")

    # =========================================================================
    # 7. Dept 7: CI/CD Formal SMT Invariant Prover & Release Seal
    # =========================================================================
    def test_dept7_ci_formal_audit_stand(self):
        stand = CIFormalAuditStand(signing_secret="TEST-SECRET-12345")

        # Invariant 1: Therac-25 Safety
        p_safe = stand.prove_therac25_safety(actuator_latency_ms=25.0, interlock_engaged=False)
        self.assertEqual(p_safe.verdict, "PROVED_VALID")

        p_danger = stand.prove_therac25_safety(actuator_latency_ms=1200.0, interlock_engaged=False)
        self.assertEqual(p_danger.verdict, "REFUTED_COUNTEREXAMPLE")
        self.assertIsNotNone(p_danger.counterexample)

        # Invariant 2: Financial Viability
        p_fin = stand.prove_financial_viability(ltv=350000.0, cac=100000.0, break_even_months=18)
        self.assertEqual(p_fin.verdict, "PROVED_VALID")

        # Full formal audit with release seal
        telemetry = {
            "actuator_latency_ms": 15.0,
            "interlock_engaged": False,
            "ltv": 500000.0,
            "cac": 100000.0,
            "break_even_months": 12,
            "npu_ram_mb": 256,
            "dma_pinned": True,
            "ai_act_risk": "HIGH_RISK",
        }
        report = stand.run_full_formal_audit("StateCertifiedEngine", "commit-sha-999", telemetry)
        self.assertTrue(report.all_proved_valid)
        self.assertEqual(report.gate_decision, "APPROVE_PRODUCTION_DEPLOYMENT")
        self.assertEqual(len(report.release_seal.digital_signature_hex), 64)

    # =========================================================================
    # 8. MCP Server Tools 24-30 Dispatch
    # =========================================================================
    def test_mcp_tools_wave4_integration(self):
        # Verify 30 tools registered
        req_list = {"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}
        resp_list = self.server.handle_jsonrpc_request(req_list)
        tools = resp_list["result"]["tools"]
        self.assertGreaterEqual(len(tools), 30)

        # Tool 24: generate_ux_fallback_plan
        req24 = {
            "jsonrpc": "2.0", "id": 24, "method": "tools/call",
            "params": {"name": "generate_ux_fallback_plan", "arguments": {"confidence": 0.65}}
        }
        res24 = self.server.handle_jsonrpc_request(req24)
        self.assertFalse(res24["result"]["isError"])
        data24 = json.loads(res24["result"]["content"][0]["text"])
        self.assertEqual(data24["current_automation_level"], "HITL_CONFIRMATION")
        self.assertIn("mermaid_statechart", data24)

        # Tool 25: audit_ias38_intangible_assets
        req25 = {
            "jsonrpc": "2.0", "id": 25, "method": "tools/call",
            "params": {"name": "audit_ias38_intangible_assets", "arguments": {}}
        }
        res25 = self.server.handle_jsonrpc_request(req25)
        self.assertFalse(res25["result"]["isError"])
        data25 = json.loads(res25["result"]["content"][0]["text"])
        self.assertIn("dossier", data25)
        self.assertEqual(data25["dossier"]["auditor_opinion"], "IAS38_FULLY_COMPLIANT_CAPITALIZED")

        # Tool 26: generate_iso42001_aims_dossier
        req26 = {
            "jsonrpc": "2.0", "id": 26, "method": "tools/call",
            "params": {"name": "generate_iso42001_aims_dossier", "arguments": {"system_name": "TestAI"}}
        }
        res26 = self.server.handle_jsonrpc_request(req26)
        self.assertFalse(res26["result"]["isError"])
        data26 = json.loads(res26["result"]["content"][0]["text"])
        self.assertEqual(data26["aims_dossier"]["certification_readiness"], "READY_FOR_STAGE_2_AUDIT")

        # Tool 27: generate_gost56939_dossier
        req27 = {
            "jsonrpc": "2.0", "id": 27, "method": "tools/call",
            "params": {"name": "generate_gost56939_dossier", "arguments": {"target_level": "УД 4"}}
        }
        res27 = self.server.handle_jsonrpc_request(req27)
        self.assertFalse(res27["result"]["isError"])
        data27 = json.loads(res27["result"]["content"][0]["text"])
        self.assertEqual(data27["gost56939_dossier"]["target_assurance_level"], "УД 4")

        # Tool 28: orchestrate_persistent_saga
        req28 = {
            "jsonrpc": "2.0", "id": 28, "method": "tools/call",
            "params": {"name": "orchestrate_persistent_saga", "arguments": {"saga_id": "MCP-SAGA-01"}}
        }
        res28 = self.server.handle_jsonrpc_request(req28)
        self.assertFalse(res28["result"]["isError"])
        data28 = json.loads(res28["result"]["content"][0]["text"])
        self.assertEqual(data28["status"], "COMMITTED")

        # Tool 29: synthesize_watchdog_circuit
        req29 = {
            "jsonrpc": "2.0", "id": 29, "method": "tools/call",
            "params": {"name": "synthesize_watchdog_circuit", "arguments": {"min_window_ms": 40.0}}
        }
        res29 = self.server.handle_jsonrpc_request(req29)
        self.assertFalse(res29["result"]["isError"])
        data29 = json.loads(res29["result"]["content"][0]["text"])
        self.assertIn("watchdog_interlock", data29["synthesized_rtl"]["module_name"])

        # Tool 30: run_ci_formal_audit
        req30 = {
            "jsonrpc": "2.0", "id": 30, "method": "tools/call",
            "params": {"name": "run_ci_formal_audit", "arguments": {}}
        }
        res30 = self.server.handle_jsonrpc_request(req30)
        self.assertFalse(res30["result"]["isError"])
        data30 = json.loads(res30["result"]["content"][0]["text"])
        self.assertEqual(data30["audit_report"]["gate_decision"], "APPROVE_PRODUCTION_DEPLOYMENT")


if __name__ == "__main__":
    unittest.main()
