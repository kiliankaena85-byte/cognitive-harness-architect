"""
tests/test_wave3_autonomous_agents.py
=============================================================================
Universal Cognitive Decomposition Engine (UCDE) - Wave 3 Verification Suite.
Autonomous Agents & Adaptive Intelligence across all 7 Departments:
- Dept 1: Opportunity Solution Trees (OST) & DMN 1.4 Business Rules
- Dept 2: Dynamic Model Cascade Optimizer & Tokenomics Cache Simulator
- Dept 3: SPDX 3.0 / OpenChain License Guard (Copyleft Veto)
- Dept 4: Continuous Cognitive DAST & Fuzzing Agent (FSTEC BDU / OWASP ASVS)
- Dept 5: Self-RAG Active Reflection Engine ([Retrieve], [IsRel], [IsSup])
- Dept 6: Chaos Fault Injection Stand (Therac-25 Latency & SRE Resiliency)
- Dept 7: Automated Test Program & Methodology (ПМИ ГОСТ 34.603 / ГОСТ 19.301)
- MCP Server: 23-Tool JSON-RPC 2.0 Integration & Dispatcher (v2.3.0)
=============================================================================
"""

import json
import unittest

from core.ministries.nodes import DeterministicMockGenerator, STRATIFIED_PROFILES
from core.generators import (
    OstEngine,
    OpportunitySolutionTree,
    ModelCascadeOptimizer,
    CascadeSimulationReport,
    SpdxLicenseGuard,
    SbomManifest,
    DastCognitiveFuzzer,
    DastAuditReport,
    SelfRagEngine,
    SelfRagAnnotatedOutput,
)
from core.hardware import ChaosFaultInjector, ChaosResiliencyReport
from core.quality import GostPmiGenerator, GostPmiDocument
from core.mcp_server import McpServer


class TestWave3AutonomousAgents(unittest.TestCase):
    """Full comprehensive test suite for Wave 3 autonomous agents and engines."""

    def setUp(self):
        self.mock_gen = DeterministicMockGenerator()
        self.profile = STRATIFIED_PROFILES["balanced"]
        self.strat_art = self.mock_gen.generate_candidate(1, "strategy", self.profile, {})
        self.fin_art = self.mock_gen.generate_candidate(2, "finance", self.profile, {})
        self.leg_art = self.mock_gen.generate_candidate(3, "legal", self.profile, {})
        self.sec_art = self.mock_gen.generate_candidate(4, "security", self.profile, {})
        self.sys_art = self.mock_gen.generate_candidate(5, "analysis", self.profile, {})
        self.hw_art = self.mock_gen.generate_candidate(6, "hardware", self.profile, {})
        self.vv_art = self.mock_gen.generate_candidate(7, "quality", self.profile, {})

    # =========================================================================
    # Department 1: Opportunity Solution Trees & DMN 1.4
    # =========================================================================

    def test_department_1_ost_engine(self):
        engine = OstEngine()
        tree = engine.generate(self.strat_art, project_id="PROJ-W3-001")

        self.assertIsInstance(tree, OpportunitySolutionTree)
        self.assertEqual(tree.project_id, "PROJ-W3-001")
        self.assertGreaterEqual(len(tree.opportunities), 3)
        self.assertGreaterEqual(tree.total_solutions_count, 3)
        self.assertGreaterEqual(tree.total_assumptions_count, 5)

        # Markdown verification
        md = engine.to_markdown(tree)
        self.assertIn("# Opportunity Solution Tree (OST):", md)
        self.assertIn("Desired Outcome:", md)
        self.assertIn("🟢 PASSED", md)

        # DMN 1.4 Decision Table export
        dmn = engine.to_dmn_decision_table(tree)
        self.assertEqual(dmn["dmn_version"], "1.4")
        self.assertEqual(dmn["hit_policy"], "RULE_ORDER")
        self.assertGreaterEqual(len(dmn["rules"]), 5)
        for r in dmn["rules"]:
            self.assertIn(r["output_decision"], ["COMMIT_HYPOTHESIS", "TRIGGER_SAGA_ROLLBACK"])

    # =========================================================================
    # Department 2: Model Cascade Optimizer & Tokenomics
    # =========================================================================

    def test_department_2_model_cascade_optimizer(self):
        opt = ModelCascadeOptimizer()

        # 1. Simple query routes to Fast-Path / SLM
        d_simple = opt.route_query("Classify user requirement tag", forced_min_quality=0.72)
        self.assertIn(d_simple.selected_tier, [0, 1])

        # 2. Safety-critical query routes to Tier 3 Frontier
        d_safety = opt.route_query("Validate Therac-25 physical interlock proof", forced_min_quality=0.98)
        self.assertEqual(d_safety.selected_tier, 3)
        self.assertGreater(d_safety.estimated_cost_rub, d_simple.estimated_cost_rub)

        # 3. Workload simulation
        sim = opt.simulate_workload(queries_count=200)
        self.assertIsInstance(sim, CascadeSimulationReport)
        self.assertEqual(sim.total_queries, 200)
        self.assertGreaterEqual(sim.total_savings_pct, 40.0)
        self.assertLess(sim.avg_latency_ms, 500.0)
        self.assertTrue(sim.sla_compliance_verified)

    # =========================================================================
    # Department 3: SPDX 3.0 / OpenChain License Guard
    # =========================================================================

    def test_department_3_spdx_license_guard(self):
        guard = SpdxLicenseGuard()

        # 1. Permissive dependencies pass
        clean_deps = [
            {"name": "pydantic", "version": "2.8.2", "license": "MIT"},
            {"name": "fastapi", "version": "0.111.0", "license": "MIT"},
            {"name": "openvino", "version": "2024.2.0", "license": "Apache-2.0"},
        ]
        clean_sbom = guard.generate_sbom(clean_deps)
        self.assertIsInstance(clean_sbom, SbomManifest)
        self.assertTrue(clean_sbom.all_packages_compliant)
        self.assertEqual(clean_sbom.viral_license_violations_count, 0)

        # 2. Viral copyleft triggers veto
        contaminated_deps = clean_deps + [
            {"name": "hostile-lib", "version": "1.0.0", "license": "AGPL-3.0-only"}
        ]
        contaminated_sbom = guard.generate_sbom(contaminated_deps)
        self.assertFalse(contaminated_sbom.all_packages_compliant)
        self.assertEqual(contaminated_sbom.viral_license_violations_count, 1)

        # Markdown report
        md = guard.to_markdown(contaminated_sbom)
        self.assertIn("COMPLIANCE VETO", md)
        self.assertIn("AGPL-3.0-only", md)

    # =========================================================================
    # Department 4: Continuous DAST Fuzzing Agent
    # =========================================================================

    def test_department_4_dast_cognitive_fuzzer(self):
        fuzzer = DastCognitiveFuzzer()
        report = fuzzer.run_fuzz_campaign(iterations_per_payload=3)

        self.assertIsInstance(report, DastAuditReport)
        self.assertGreater(report.total_mutations_executed, 20)
        self.assertEqual(report.failed_defenses_count, 0)
        self.assertTrue(report.zero_trust_invariants_satisfied)
        self.assertLess(report.p99_rejection_latency_us, 1000.0)

        # Markdown report
        md = fuzzer.to_markdown(report)
        self.assertIn("# DAST Security Fuzzing Audit Report", md)
        self.assertIn("NIST SP 800-207 Zero-Trust Boundary active", md)

    # =========================================================================
    # Department 5: Self-RAG Active Reflection Engine
    # =========================================================================

    def test_department_5_self_rag_engine(self):
        engine = SelfRagEngine()

        query = "What is the NPU direct memory access latency SLA?"
        contexts = [
            "The OpenVINO DMA optimizer provides sub-millisecond latency under 50 ms SLA.",
            "Pinned host buffers are 64-byte aligned."
        ]

        # Valid draft matching context
        valid_draft = "The OpenVINO DMA optimizer provides sub-millisecond latency under 50 ms SLA. Pinned buffers are 64-byte aligned."
        output = engine.critique_and_reflect(query, valid_draft, contexts)

        self.assertIsInstance(output, SelfRagAnnotatedOutput)
        self.assertGreaterEqual(output.overall_faithfulness_pct, 90.0)
        self.assertLess(output.hallucination_rate_pct, 0.1)
        self.assertEqual(output.filtered_segments_count, 0)

        # Stream format verification
        stream = engine.to_annotated_stream(output)
        self.assertIn("[Retrieve]", stream)
        self.assertIn("[IsRel]", stream)
        self.assertIn("[IsSup]", stream)

        # Hallucination filter test
        hallucinating_draft = "The NPU connects to an unauthenticated public quantum satellite in orbit."
        h_output = engine.critique_and_reflect(query, hallucinating_draft, contexts)
        self.assertEqual(h_output.filtered_segments_count, 1)

    # =========================================================================
    # Department 6: Chaos Fault Injection & SRE Stand
    # =========================================================================

    def test_department_6_chaos_fault_injection(self):
        chaos = ChaosFaultInjector()

        # 1. Therac latency spike with interlock
        r1 = chaos.run_therac_latency_spike_experiment(hardware_interlock_present=True)
        self.assertTrue(r1.system_recovered_safely)
        self.assertEqual(r1.fail_safe_state_achieved, "SAFE_PHYSICAL_INTERLOCK_ENGAGED")

        # 2. Therac latency spike without interlock
        r2 = chaos.run_therac_latency_spike_experiment(hardware_interlock_present=False)
        self.assertFalse(r2.system_recovered_safely)
        self.assertIn("CATASTROPHIC", r2.fail_safe_state_achieved)

        # 3. NPU RAM overflow quota
        r3 = chaos.run_npu_ram_overflow_experiment(requested_mb=768.0)
        self.assertTrue(r3.system_recovered_safely)
        self.assertEqual(r3.fail_safe_state_achieved, "QUOTA_BLOCKED_WITH_CLEAN_ERROR")

        # 4. Watchdog retry cap
        r4 = chaos.run_watchdog_timeout_experiment(retries_attempted=4)
        self.assertTrue(r4.system_recovered_safely)
        self.assertEqual(r4.fail_safe_state_achieved, "DOWNGRADED_TO_DETERMINISTIC_SAFE_PROFILE")

        # 5. Full campaign
        campaign = chaos.run_full_chaos_campaign()
        self.assertIsInstance(campaign, ChaosResiliencyReport)
        self.assertTrue(campaign.all_resiliency_invariants_passed)

    # =========================================================================
    # Department 7: ГОСТ 34.603 / ГОСТ 19.301 ПМИ Generator
    # =========================================================================

    def test_department_7_gost_pmi_generator(self):
        pmi_gen = GostPmiGenerator()
        doc = pmi_gen.generate(
            strategy_artifact=self.strat_art,
            finance_artifact=self.fin_art,
            legal_artifact=self.leg_art,
            security_artifact=self.sec_art,
            analysis_artifact=self.sys_art,
            hardware_artifact=self.hw_art,
            quality_artifact=self.vv_art,
            gost_standard="ГОСТ 34.603-92",
        )

        self.assertIsInstance(doc, GostPmiDocument)
        self.assertEqual(doc.gost_standard, "ГОСТ 34.603-92")
        self.assertEqual(doc.total_checks_count, 7)
        self.assertEqual(doc.passed_checks_count, 7)
        self.assertEqual(doc.commission_verdict, "РЕКОМЕНДОВАНО_К_ПРИЕМКЕ")
        self.assertEqual(len(doc.digital_seal_sha256), 64)

        # Markdown verification
        md = pmi_gen.to_markdown(doc)
        self.assertIn("# ПРОГРАММА И МЕТОДИКА ПРИЕМОЧНЫХ ИСПЫТАНИЙ", md)
        self.assertIn("ГОСТ 34.603-92", md)
        self.assertIn("🟢 СООТВЕТСТВУЕТ", md)
        self.assertIn("РЕКОМЕНДОВАНО_К_ПРИЕМКЕ", md)

    # =========================================================================
    # MCP Server: Wave 3 Tool In-Process Dispatcher & JSON-RPC
    # =========================================================================

    def test_mcp_server_wave3_tools_integration(self):
        server = McpServer()
        self.assertEqual(server.SERVER_VERSION, "2.3.0")

        # 1. Verify 23 tools registered
        list_resp = server.handle_jsonrpc_request({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
        tools = list_resp["result"]["tools"]
        tool_names = {t["name"] for t in tools}
        expected_wave3_tools = {
            "generate_opportunity_solution_tree",
            "optimize_model_cascade",
            "scan_spdx_licenses",
            "run_dast_cognitive_fuzzer",
            "evaluate_self_rag_reflection",
            "run_chaos_fault_injection",
            "generate_gost_pmi",
        }
        self.assertTrue(expected_wave3_tools.issubset(tool_names))
        self.assertEqual(len(tool_names), 23)

        # 2. Call generate_opportunity_solution_tree
        resp = server.handle_jsonrpc_request({
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "generate_opportunity_solution_tree",
                "arguments": {"strategy_artifact": self.strat_art},
            },
        })
        self.assertFalse(resp["result"]["isError"])
        parsed = json.loads(resp["result"]["content"][0]["text"])
        self.assertIn("tree", parsed)
        self.assertIn("dmn_table", parsed)

        # 3. Call optimize_model_cascade
        resp = server.handle_jsonrpc_request({
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "optimize_model_cascade",
                "arguments": {"query": "Validate Z3 SMT prover invariant", "simulate_workload": False},
            },
        })
        self.assertFalse(resp["result"]["isError"])
        parsed = json.loads(resp["result"]["content"][0]["text"])
        self.assertIn("decision", parsed)

        # 4. Call scan_spdx_licenses
        resp = server.handle_jsonrpc_request({
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "scan_spdx_licenses",
                "arguments": {
                    "dependencies": [{"name": "numpy", "version": "1.26.0", "license": "BSD-3-Clause"}]
                },
            },
        })
        self.assertFalse(resp["result"]["isError"])
        parsed = json.loads(resp["result"]["content"][0]["text"])
        self.assertTrue(parsed["sbom"]["all_packages_compliant"])

        # 5. Call run_dast_cognitive_fuzzer
        resp = server.handle_jsonrpc_request({
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {
                "name": "run_dast_cognitive_fuzzer",
                "arguments": {"endpoints": ["/api/v1/verify"], "iterations": 1},
            },
        })
        self.assertFalse(resp["result"]["isError"])
        parsed = json.loads(resp["result"]["content"][0]["text"])
        self.assertTrue(parsed["audit_report"]["zero_trust_invariants_satisfied"])

        # 6. Call evaluate_self_rag_reflection
        resp = server.handle_jsonrpc_request({
            "jsonrpc": "2.0",
            "id": 6,
            "method": "tools/call",
            "params": {
                "name": "evaluate_self_rag_reflection",
                "arguments": {
                    "query": "What is the NPU memory budget?",
                    "draft_text": "The NPU working set RAM is capped at 512 MB.",
                    "contexts": ["The NPU working set RAM is capped at 512 MB."],
                },
            },
        })
        self.assertFalse(resp["result"]["isError"])
        parsed = json.loads(resp["result"]["content"][0]["text"])
        self.assertEqual(parsed["annotated_output"]["filtered_segments_count"], 0)

        # 7. Call run_chaos_fault_injection
        resp = server.handle_jsonrpc_request({
            "jsonrpc": "2.0",
            "id": 7,
            "method": "tools/call",
            "params": {
                "name": "run_chaos_fault_injection",
                "arguments": {"fault_type": "ALL"},
            },
        })
        self.assertFalse(resp["result"]["isError"])
        parsed = json.loads(resp["result"]["content"][0]["text"])
        self.assertTrue(parsed["report"]["all_resiliency_invariants_passed"])

        # 8. Call generate_gost_pmi
        resp = server.handle_jsonrpc_request({
            "jsonrpc": "2.0",
            "id": 8,
            "method": "tools/call",
            "params": {
                "name": "generate_gost_pmi",
                "arguments": {
                    "strategy_artifact": self.strat_art,
                    "finance_artifact": self.fin_art,
                    "legal_artifact": self.leg_art,
                    "security_artifact": self.sec_art,
                    "analysis_artifact": self.sys_art,
                    "hardware_artifact": self.hw_art,
                    "quality_artifact": self.vv_art,
                },
            },
        })
        self.assertFalse(resp["result"]["isError"])
        parsed = json.loads(resp["result"]["content"][0]["text"])
        self.assertEqual(parsed["pmi_document"]["commission_verdict"], "РЕКОМЕНДОВАНО_К_ПРИЕМКЕ")


if __name__ == "__main__":
    unittest.main()
