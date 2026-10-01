"""
tests/test_wave1_standards_expansion.py
=============================================================================
Universal Cognitive Decomposition Engine (UCDE) - Wave 1 Verification Suite.
Deep Standards & Syntax Upgrades across all 7 Ministries:
- Node 1: EARS Syntax Requirements & ISO 29148 Quality Attributes
- Node 2: FinOps Monte Carlo Simulation (10k iters) & Value-at-Risk (VaR 95%)
- Node 3: RF PP № 1119 Threat Model (SKZI KS1-KS3) & EU AI Act Technical Dossier
- Node 4: MITRE ATLAS Matrix (AI System Tactics & Techniques)
- Node 5: AsyncAPI 3.0 / CloudEvents 1.0 & Self-RAG Reflection Tokens
- Node 6: Fault Tree Analysis (FTA IEC 61025 / ГОСТ Р 27.302)
- Node 7: Mutation Testing (MSI >= 85%) & RAG Triad Groundedness
=============================================================================
"""

import copy
import re
import time
import unittest
from typing import Any, Dict

from pydantic import ValidationError

from core.schemas import (
    CONTRACT_SCHEMAS_REGISTRY,
    MINISTRY_ID_MAP,
    StrategyCJMContract,
    EarsRequirement,
    FinanceBudgetContract,
    MonteCarloSimulationConfig,
    FinancialRiskProfile,
    LegalComplianceContract,
    ThreatModel1119,
    EuAiActDossier,
    SecurityPolicyContract,
    MitreAtlasThreat,
    SystemAnalysisContract,
    AsyncMessageTopic,
    SelfRagConfig,
    HardwareRuntimeContract,
    FaultTreeNode,
    VVQualityContract,
    MutationTestingConfig,
    get_contract_class,
)
from core.ministries.nodes import DeterministicMockGenerator, STRATIFIED_PROFILES
from core.standards_linter import StandardsLinter, StandardsLintResult


class TestWave1StrategyNodeExpansion(unittest.TestCase):
    """Test suite for Node 1: EARS Syntax & ISO 29148 Quality Attributes."""

    def setUp(self):
        self.mock_gen = DeterministicMockGenerator()
        self.linter = StandardsLinter()
        self.valid_data = self.mock_gen._mock_strategy(STRATIFIED_PROFILES["balanced"], "balanced")

    def test_ears_requirements_valid(self):
        contract = StrategyCJMContract.model_validate(self.valid_data)
        self.assertGreaterEqual(len(contract.ears_requirements), 2)
        for req in contract.ears_requirements:
            self.assertTrue(req.req_id.startswith("REQ-"))
            self.assertIn(req.pattern_type, ["UBIQUITOUS", "EVENT_DRIVEN", "STATE_DRIVEN", "UNWANTED_BEHAVIOR", "OPTIONAL_FEATURE"])
            self.assertTrue(len(req.text) >= 10)

    def test_ears_unmapped_ac_rejected_by_validator(self):
        bad_data = copy.deepcopy(self.valid_data)
        bad_data["ears_requirements"].append({
            "req_id": "REQ-EARS-99",
            "pattern_type": "UBIQUITOUS",
            "text": "The system shall reject unmapped requirements immediately.",
            "source_persona": "Auditor",
            "source_ac_id": "AC-NON-EXISTENT-ID",
        })
        with self.assertRaises(ValidationError) as ctx:
            StrategyCJMContract.model_validate(bad_data)
        self.assertIn("AC-NON-EXISTENT-ID", str(ctx.exception))

    def test_linter_checks_ears_pattern_and_modal_syntax(self):
        bad_data = copy.deepcopy(self.valid_data)
        bad_data["ears_requirements"].append({
            "req_id": "REQ-EARS-BAD",
            "pattern_type": "INVALID_PATTERN_TYPE",
            "text": "System does something without modal keyword",
            "source_persona": "Auditor",
            "source_ac_id": self.valid_data["acceptance_criteria"][0]["id"],
        })
        # Model validator will reject invalid pattern, but testing linter directly:
        res = self.linter.lint_node_artifact(1, bad_data)
        self.assertFalse(res.is_compliant)
        self.assertTrue(any(v.standard_id == "ISO_29148_EARS" for v in res.violations))


class TestWave1FinanceNodeExpansion(unittest.TestCase):
    """Test suite for Node 2: FinOps Monte Carlo Simulation & VaR 95%."""

    def setUp(self):
        self.mock_gen = DeterministicMockGenerator()
        self.linter = StandardsLinter()
        self.valid_data = self.mock_gen._mock_finance(STRATIFIED_PROFILES["balanced"], "balanced")

    def test_monte_carlo_and_var_valid(self):
        contract = FinanceBudgetContract.model_validate(self.valid_data)
        self.assertEqual(contract.monte_carlo_config.iterations, 10000)
        self.assertEqual(contract.monte_carlo_config.confidence_level, 0.95)
        self.assertLessEqual(contract.risk_profile.insolvency_probability_pct, 5.0)
        self.assertTrue(contract.risk_profile.monte_carlo_verified)

    def test_excessive_insolvency_risk_rejected_by_schema(self):
        bad_data = copy.deepcopy(self.valid_data)
        bad_data["risk_profile"]["insolvency_probability_pct"] = 12.5  # > 5.0 limit
        with self.assertRaises(ValidationError) as ctx:
            FinanceBudgetContract.model_validate(bad_data)
        self.assertIn("insolvency_probability_pct", str(ctx.exception))

    def test_insufficient_monte_carlo_iterations_flagged_by_linter(self):
        bad_data = copy.deepcopy(self.valid_data)
        bad_data["monte_carlo_config"]["iterations"] = 500  # < 1000 required
        res = self.linter.lint_node_artifact(2, bad_data)
        self.assertFalse(res.is_compliant)
        self.assertTrue(any("MONTE_CARLO_VAR" in v.standard_id for v in res.violations))


class TestWave1LegalNodeExpansion(unittest.TestCase):
    """Test suite for Node 3: PP 1119 Threat Model & EU AI Act Dossier."""

    def setUp(self):
        self.mock_gen = DeterministicMockGenerator()
        self.linter = StandardsLinter()
        self.valid_data = self.mock_gen._mock_legal(STRATIFIED_PROFILES["balanced"], "balanced")

    def test_pp_1119_and_ai_act_dossier_valid(self):
        contract = LegalComplianceContract.model_validate(self.valid_data)
        self.assertIn(contract.pp_1119_threat_model.threat_type, ["ТИП_1", "ТИП_2", "ТИП_3"])
        self.assertIn(contract.pp_1119_threat_model.skzi_class, ["КС1", "КС2", "КС3", "КБ", "КА", "NONE"])
        self.assertTrue(contract.eu_ai_act_dossier.article_14_human_oversight)
        self.assertTrue(contract.eu_ai_act_dossier.article_15_robustness_accuracy)

    def test_disabled_human_oversight_flagged_by_linter(self):
        bad_data = copy.deepcopy(self.valid_data)
        bad_data["eu_ai_act_dossier"]["article_14_human_oversight"] = False
        res = self.linter.lint_node_artifact(3, bad_data)
        self.assertFalse(res.is_compliant)
        self.assertTrue(any("Article 14 Human Oversight" in v.message for v in res.violations))


class TestWave1SecurityNodeExpansion(unittest.TestCase):
    """Test suite for Node 4: MITRE ATLAS Matrix & ISO 42001 Controls."""

    def setUp(self):
        self.mock_gen = DeterministicMockGenerator()
        self.linter = StandardsLinter()
        self.valid_data = self.mock_gen._mock_security(STRATIFIED_PROFILES["balanced"], "balanced")

    def test_mitre_atlas_matrix_valid(self):
        contract = SecurityPolicyContract.model_validate(self.valid_data)
        self.assertGreaterEqual(len(contract.mitre_atlas_matrix), 2)
        for t in contract.mitre_atlas_matrix:
            self.assertTrue(re.match(r"^AML\.T\d{4}(\.\d{3})?$", t.technique_id))
            self.assertTrue(len(t.mitigation) >= 10)
        self.assertTrue(contract.iso_42001_security_controls_active)

    def test_invalid_mitre_technique_id_rejected_by_schema(self):
        bad_data = copy.deepcopy(self.valid_data)
        bad_data["mitre_atlas_matrix"].append({
            "tactic": "INITIAL_ACCESS",
            "technique_id": "INVALID-TECHNIQUE-123",
            "technique_name": "Bad Technique",
            "mitigation": "Some mitigation text here",
        })
        with self.assertRaises(ValidationError) as ctx:
            SecurityPolicyContract.model_validate(bad_data)
        self.assertIn("technique_id", str(ctx.exception))


class TestWave1AnalysisNodeExpansion(unittest.TestCase):
    """Test suite for Node 5: AsyncAPI 3.0 & Self-RAG Reflection."""

    def setUp(self):
        self.mock_gen = DeterministicMockGenerator()
        self.linter = StandardsLinter()
        self.valid_data = self.mock_gen._mock_system_analysis(STRATIFIED_PROFILES["balanced"], "balanced", False)

    def test_asyncapi_and_self_rag_valid(self):
        contract = SystemAnalysisContract.model_validate(self.valid_data)
        self.assertEqual(contract.asyncapi_version, "3.0.0")
        self.assertGreaterEqual(len(contract.async_topics), 1)
        self.assertTrue(contract.self_rag.retrieve_reflection_token)
        self.assertTrue(contract.self_rag.is_rel_reflection_token)
        self.assertTrue(contract.self_rag.is_sup_reflection_token)
        self.assertTrue(contract.self_rag.is_use_reflection_token)
        self.assertGreaterEqual(contract.self_rag.critique_threshold, 0.85)

    def test_invalid_topic_name_rejected_by_schema(self):
        bad_data = copy.deepcopy(self.valid_data)
        bad_data["async_topics"].append({
            "topic_name": "invalid topic with spaces!",
            "event_type": "com.test.event",
            "schema_format": "JSON_SCHEMA",
            "retention_hours": 24,
        })
        with self.assertRaises(ValidationError) as ctx:
            SystemAnalysisContract.model_validate(bad_data)
        self.assertIn("topic_name", str(ctx.exception))


class TestWave1HardwareNodeExpansion(unittest.TestCase):
    """Test suite for Node 6: Fault Tree Analysis (FTA IEC 61025)."""

    def setUp(self):
        self.mock_gen = DeterministicMockGenerator()
        self.linter = StandardsLinter()
        self.valid_data = self.mock_gen._mock_hardware(STRATIFIED_PROFILES["balanced"], "balanced", False)

    def test_fault_tree_analysis_valid(self):
        contract = HardwareRuntimeContract.model_validate(self.valid_data)
        self.assertGreaterEqual(len(contract.fault_tree_analysis), 3)
        self.assertTrue(contract.iec_61025_fta_verified)
        top_node = contract.fault_tree_analysis[0]
        self.assertEqual(top_node.node_id, "FTN-GATE-01")
        self.assertEqual(top_node.gate_type, "OR")
        self.assertEqual(len(top_node.children_node_ids), 2)

    def test_invalid_fta_node_id_rejected_by_schema(self):
        bad_data = copy.deepcopy(self.valid_data)
        bad_data["fault_tree_analysis"].append({
            "node_id": "malformed_node_id",
            "gate_type": "AND",
            "description": "Malformed node",
            "probability_per_hour": 1e-5,
            "children_node_ids": [],
        })
        with self.assertRaises(ValidationError) as ctx:
            HardwareRuntimeContract.model_validate(bad_data)
        self.assertIn("node_id", str(ctx.exception))


class TestWave1QualityNodeExpansion(unittest.TestCase):
    """Test suite for Node 7: Mutation Testing (MSI >= 85%)."""

    def setUp(self):
        self.mock_gen = DeterministicMockGenerator()
        self.linter = StandardsLinter()
        self.valid_data = self.mock_gen._mock_quality(STRATIFIED_PROFILES["balanced"], "balanced")

    def test_mutation_testing_valid(self):
        contract = VVQualityContract.model_validate(self.valid_data)
        self.assertGreaterEqual(contract.mutation_testing.mutation_score_indicator_target_pct, 85.0)
        self.assertEqual(contract.mutation_testing.survived_mutants_threshold, 0)
        self.assertIn(contract.mutation_testing.framework, ["MUTMUT", "COSMIC_RAY", "AST_MUTATOR"])

    def test_low_msi_flagged_by_linter(self):
        bad_data = copy.deepcopy(self.valid_data)
        bad_data["mutation_testing"]["mutation_score_indicator_target_pct"] = 80.0
        res = self.linter.lint_node_artifact(7, bad_data)
        self.assertFalse(res.is_compliant)
        self.assertTrue(any("MUTATION_MSI_85" in v.standard_id for v in res.violations))


class TestWave1SubMillisecondValidationSLA(unittest.TestCase):
    """Verify that all new Wave 1 Pydantic V2 validations execute in sub-millisecond time (< 1.0 ms)."""

    def setUp(self):
        self.mock_gen = DeterministicMockGenerator()

    def test_rejection_latencies_sub_millisecond(self):
        trials = 1000

        # Node 1: EARS unmapped AC
        bad_s = self.mock_gen._mock_strategy(STRATIFIED_PROFILES["balanced"], "balanced")
        bad_s["ears_requirements"].append({
            "req_id": "REQ-EARS-BAD",
            "pattern_type": "UBIQUITOUS",
            "text": "The system shall fail fast and cleanly.",
            "source_persona": "Tester",
            "source_ac_id": "AC-GHOST",
        })

        t0 = time.perf_counter()
        for _ in range(trials):
            try:
                StrategyCJMContract.model_validate(bad_s)
            except ValidationError:
                pass
        t_strat = (time.perf_counter() - t0) / trials * 1000.0
        self.assertLess(t_strat, 1.0, f"Strategy rejection latency {t_strat:.3f} ms exceeds 1.0 ms SLA")

        # Node 2: Insolvency probability
        bad_f = self.mock_gen._mock_finance(STRATIFIED_PROFILES["balanced"], "balanced")
        bad_f["risk_profile"]["insolvency_probability_pct"] = 9.9

        t0 = time.perf_counter()
        for _ in range(trials):
            try:
                FinanceBudgetContract.model_validate(bad_f)
            except ValidationError:
                pass
        t_fin = (time.perf_counter() - t0) / trials * 1000.0
        self.assertLess(t_fin, 1.0, f"Finance rejection latency {t_fin:.3f} ms exceeds 1.0 ms SLA")

        # Node 4: MITRE ATLAS malformed ID
        bad_sec = self.mock_gen._mock_security(STRATIFIED_PROFILES["balanced"], "balanced")
        bad_sec["mitre_atlas_matrix"].append({
            "tactic": "INITIAL_ACCESS",
            "technique_id": "BAD-ID",
            "technique_name": "Test",
            "mitigation": "Long enough mitigation string",
        })

        t0 = time.perf_counter()
        for _ in range(trials):
            try:
                SecurityPolicyContract.model_validate(bad_sec)
            except ValidationError:
                pass
        t_sec = (time.perf_counter() - t0) / trials * 1000.0
        self.assertLess(t_sec, 1.0, f"Security rejection latency {t_sec:.3f} ms exceeds 1.0 ms SLA")


if __name__ == "__main__":
    unittest.main()
