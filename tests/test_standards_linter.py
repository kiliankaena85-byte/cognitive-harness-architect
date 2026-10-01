"""
tests/test_standards_linter.py
=============================================================================
Unit Test Suite for Deterministic Multi-Standard Linter (`core/standards_linter.py`)
Universal Cognitive Decomposition Engine (UCDE)

Tests:
1. TestMinistry1StrategyStandards (ISO 29148, BABOK BACCM, Gherkin syntax & traceability)
2. TestMinistry2FinanceStandards (FinOps FOCUS 1.0, IAS 38 solvency, ISO 31000)
3. TestMinistry3LegalStandards (SPDX 2.3/3.0 catalog, 152-FZ localization, EU AI Act)
4. TestMinistry4SecurityStandards (OWASP ASVS 4.0, NIST SP 800-207, FSTEC BDU ^УБИ\.\d{3}$)
5. TestMinistry5AnalysisStandards (RFC 7807/9457 Problem Details, OpenAPI 3.1, C4 Model)
6. TestMinistry6HardwareStandards (IEC 61508 SIL, IEEE 754 precision, Therac-25 race condition)
7. TestMinistry7QualityStandards (GOST 34.602, GOST 34.603, ISO 29119-4, SHA-256 seal)
8. TestEnsembleLintingAndGateIntegration (Full pipeline ensemble linting & Zero-Trust gate rejection)
=============================================================================
"""

import copy
import hashlib
import sys
import unittest
from pathlib import Path

# Force UTF-8 on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.standards_linter import (
    StandardsLinter,
    StandardsLintResult,
    StandardViolation,
    verify_standards_compliance,
    VALID_SPDX_IDENTIFIERS,
)
from core.ministries.nodes import DeterministicMockGenerator, STRATIFIED_PROFILES
from core.orchestrator import ZeroTrustGateCoordinator


class TestMinistry1StrategyStandards(unittest.TestCase):
    def setUp(self):
        self.linter = StandardsLinter()
        self.mock_gen = DeterministicMockGenerator()
        self.valid_artifact = self.mock_gen._mock_strategy(STRATIFIED_PROFILES["balanced"], "balanced")

    def test_valid_strategy_passes(self):
        res = self.linter.lint_node_artifact(1, self.valid_artifact)
        self.assertTrue(res.is_compliant)
        self.assertEqual(res.compliance_score_pct, 100.0)
        self.assertIn("ISO_29148", res.checked_standards)

    def test_broken_traceability_flagged(self):
        bad_artifact = copy.deepcopy(self.valid_artifact)
        bad_artifact["business_rules"].append({
            "rule_id": "BR-GHOST",
            "description": "Rule pointing nowhere",
            "source_ac_id": "AC-NON-EXISTENT"
        })
        res = self.linter.lint_node_artifact(1, bad_artifact)
        self.assertFalse(res.is_compliant)
        self.assertTrue(any("AC-NON-EXISTENT" in v.message for v in res.violations))

    def test_gost_19_espd_profile_validation(self):
        bad = copy.deepcopy(self.valid_artifact)
        bad["target_document_profile"] = "GOST_19_ESPD_SOFTWARE"
        bad["gost_19_espd_sections_defined"] = False
        res = self.linter.lint_node_artifact(1, bad)
        self.assertFalse(res.is_compliant)
        self.assertTrue(any("GOST_19_ESPD" in v.standard_id for v in res.violations))


class TestMinistry2FinanceStandards(unittest.TestCase):
    def setUp(self):
        self.linter = StandardsLinter()
        self.mock_gen = DeterministicMockGenerator()
        self.valid_artifact = self.mock_gen._mock_finance(STRATIFIED_PROFILES["balanced"], "balanced")

    def test_valid_finance_passes(self):
        res = self.linter.lint_node_artifact(2, self.valid_artifact)
        self.assertTrue(res.is_compliant)
        self.assertEqual(res.compliance_score_pct, 100.0)
        self.assertIn("FINOPS_FOCUS_1.0", res.checked_standards)

    def test_invalid_finops_version_rejected(self):
        bad = copy.deepcopy(self.valid_artifact)
        bad["finops_focus_version"] = "0.9-draft"
        res = self.linter.lint_node_artifact(2, bad)
        self.assertFalse(res.is_compliant)
        self.assertTrue(any("finops_focus_version" in v.message for v in res.violations))

    def test_insolvent_ltv_cac_rejected(self):
        bad = copy.deepcopy(self.valid_artifact)
        bad["lifetime_value"] = 50000.0
        bad["customer_acquisition_cost"] = 40000.0  # LTV/CAC = 1.25 < 3.0
        res = self.linter.lint_node_artifact(2, bad)
        self.assertFalse(res.is_compliant)
        self.assertTrue(any("solvency" in v.message.lower() for v in res.violations))


class TestMinistry3LegalStandards(unittest.TestCase):
    def setUp(self):
        self.linter = StandardsLinter()
        self.mock_gen = DeterministicMockGenerator()
        self.valid_artifact = self.mock_gen._mock_legal(STRATIFIED_PROFILES["balanced"], "balanced")

    def test_valid_legal_passes(self):
        res = self.linter.lint_node_artifact(3, self.valid_artifact)
        self.assertTrue(res.is_compliant)
        self.assertIn("SPDX_2.3", res.checked_standards)

    def test_non_spdx_license_rejected(self):
        bad = copy.deepcopy(self.valid_artifact)
        bad["approved_open_source_licenses"].append("MY_CUSTOM_PROPRIETARY_LICENSE")
        res = self.linter.lint_node_artifact(3, bad)
        self.assertFalse(res.is_compliant)
        self.assertTrue(any("MY_CUSTOM_PROPRIETARY_LICENSE" in v.message for v in res.violations))

    def test_foreign_data_localization_critical_violation(self):
        bad = copy.deepcopy(self.valid_artifact)
        bad["personal_data"]["localization_country"] = "USA"
        res = self.linter.lint_node_artifact(3, bad)
        self.assertFalse(res.is_compliant)
        self.assertTrue(any(v.severity == "CRITICAL" and "152-FZ" in v.rule for v in res.violations))

    def test_unacceptable_ai_act_prohibited(self):
        bad = copy.deepcopy(self.valid_artifact)
        bad["ai_act_risk_category"] = "UNACCEPTABLE"
        res = self.linter.lint_node_artifact(3, bad)
        self.assertFalse(res.is_compliant)
        self.assertTrue(any("UNACCEPTABLE" in v.message for v in res.violations))

    def test_fstec_orders_classification_validation(self):
        bad = copy.deepcopy(self.valid_artifact)
        bad["fstec_gis_class"] = "INVALID_CLASS"
        res = self.linter.lint_node_artifact(3, bad)
        self.assertFalse(res.is_compliant)
        self.assertTrue(any("FSTEC_17_21_239" in v.standard_id for v in res.violations))


class TestMinistry4SecurityStandards(unittest.TestCase):
    def setUp(self):
        self.linter = StandardsLinter()
        self.mock_gen = DeterministicMockGenerator()
        self.valid_artifact = self.mock_gen._mock_security(STRATIFIED_PROFILES["balanced"], "balanced")

    def test_valid_security_passes(self):
        res = self.linter.lint_node_artifact(4, self.valid_artifact)
        self.assertTrue(res.is_compliant)
        self.assertIn("OWASP_ASVS_4.0", res.checked_standards)
        self.assertIn("FSTEC_BDU", res.checked_standards)

    def test_invalid_owasp_level_rejected(self):
        bad = copy.deepcopy(self.valid_artifact)
        bad["owasp_asvs_level"] = "L0_NONE"
        res = self.linter.lint_node_artifact(4, bad)
        self.assertFalse(res.is_compliant)

    def test_malformed_fstec_bdu_code_rejected(self):
        bad = copy.deepcopy(self.valid_artifact)
        bad["stride_matrix"][0]["fstec_ubi_code"] = "CVE-2024-1234"
        res = self.linter.lint_node_artifact(4, bad)
        self.assertFalse(res.is_compliant)
        self.assertTrue(any("FSTEC BDU" in v.message for v in res.violations))

    def test_fstec_orders_security_mapping_validation(self):
        bad = copy.deepcopy(self.valid_artifact)
        bad["fstec_orders_classification"] = {}
        res = self.linter.lint_node_artifact(4, bad)
        self.assertFalse(res.is_compliant)
        self.assertTrue(any("FSTEC_17_21_239_SECURITY" in v.standard_id for v in res.violations))


class TestMinistry5AnalysisStandards(unittest.TestCase):
    def setUp(self):
        self.linter = StandardsLinter()
        self.mock_gen = DeterministicMockGenerator()
        self.valid_artifact = self.mock_gen._mock_system_analysis(STRATIFIED_PROFILES["balanced"], "balanced", False)

    def test_valid_analysis_passes(self):
        res = self.linter.lint_node_artifact(5, self.valid_artifact)
        self.assertTrue(res.is_compliant)
        self.assertIn("RFC_7807_9457", res.checked_standards)

    def test_invalid_error_response_standard_rejected(self):
        bad = copy.deepcopy(self.valid_artifact)
        bad["error_response_standard"] = "CUSTOM_XML_FAULT"
        res = self.linter.lint_node_artifact(5, bad)
        self.assertFalse(res.is_compliant)
        self.assertTrue(any("RFC 7807" in v.message for v in res.violations))

    def test_madr_3_0_adr_validation(self):
        bad = copy.deepcopy(self.valid_artifact)
        bad["architecture_decision_records"] = [{
            "adr_id": "ADR-001",
            "title": "Bad ADR with single option",
            "status": "ACCEPTED",
            "deciders": ["Architect"],
            "context_and_problem_statement": "Need a database engine.",
            "decision_drivers": ["Performance"],
            "considered_options": ["Option 1 Only"],  # < 2 options
            "decision_outcome": "Pick Option 1",
            "positive_consequences": ["Fast"],
            "negative_consequences": ["None"],
        }]
        res = self.linter.lint_node_artifact(5, bad)
        self.assertFalse(res.is_compliant)
        self.assertTrue(any("MADR_3.0" in v.standard_id for v in res.violations))


class TestMinistry6HardwareStandards(unittest.TestCase):
    def setUp(self):
        self.linter = StandardsLinter()
        self.mock_gen = DeterministicMockGenerator()
        self.valid_artifact = self.mock_gen._mock_hardware(STRATIFIED_PROFILES["balanced"], "balanced", False)

    def test_valid_hardware_passes(self):
        res = self.linter.lint_node_artifact(6, self.valid_artifact)
        self.assertTrue(res.is_compliant)
        self.assertIn("IEC_61508_SIL", res.checked_standards)

    def test_therac25_race_hazard_caught(self):
        bad = copy.deepcopy(self.valid_artifact)
        bad["physical_actuator_latency_ms"] = 5000.0
        bad["hardware_interlocks_required"] = False
        res = self.linter.lint_node_artifact(6, bad)
        self.assertFalse(res.is_compliant)
        self.assertTrue(any(v.severity == "CRITICAL" and "Therac-25" in v.rule for v in res.violations))

    def test_fmea_rpn_threshold_validation(self):
        bad = copy.deepcopy(self.valid_artifact)
        bad["fmea_risk_analysis"] = [{
            "failure_mode_id": "FM-CATASTROPHIC",
            "component": "NPU Memory Controller",
            "potential_failure_mode": "Memory bit-flip under voltage droop",
            "potential_effect": "Uncontrolled actuation without interlock",
            "severity": 9,
            "occurrence": 5,
            "detection": 4,  # RPN = 9 * 5 * 4 = 180 > 120
            "rpn": 180,
            "mitigation_action": "Add ECC parity",
        }]
        res = self.linter.lint_node_artifact(6, bad)
        self.assertFalse(res.is_compliant)
        self.assertTrue(any("FMEA_RPN" in v.standard_id for v in res.violations))


class TestMinistry7QualityStandards(unittest.TestCase):
    def setUp(self):
        self.linter = StandardsLinter()
        self.mock_gen = DeterministicMockGenerator()
        self.valid_artifact = self.mock_gen._mock_quality(STRATIFIED_PROFILES["balanced"], "balanced")

    def test_valid_quality_passes(self):
        res = self.linter.lint_node_artifact(7, self.valid_artifact)
        self.assertTrue(res.is_compliant)
        self.assertIn("GOST_34.602_89", res.checked_standards)

    def test_missing_gost_sections_critical_violation(self):
        bad = copy.deepcopy(self.valid_artifact)
        bad["gost_34_602_all_sections_present"] = False
        res = self.linter.lint_node_artifact(7, bad)
        self.assertFalse(res.is_compliant)
        self.assertTrue(any(v.severity == "CRITICAL" and "GOST" in v.rule for v in res.violations))

    def test_invalid_release_seal_rejected(self):
        bad = copy.deepcopy(self.valid_artifact)
        bad["cryptographic_release_signature"] = "not-a-valid-sha256"
        res = self.linter.lint_node_artifact(7, bad)
        self.assertFalse(res.is_compliant)
        self.assertTrue(any("SHA-256" in v.message for v in res.violations))

    def test_gost_19_201_software_docs_validation(self):
        bad = copy.deepcopy(self.valid_artifact)
        bad["gost_19_201_sections_present"] = False
        res = self.linter.lint_node_artifact(7, bad)
        self.assertFalse(res.is_compliant)
        self.assertTrue(any("GOST_19_201" in v.standard_id for v in res.violations))


class TestEnsembleLintingAndGateIntegration(unittest.TestCase):
    def setUp(self):
        self.linter = StandardsLinter()
        self.mock_gen = DeterministicMockGenerator()
        self.coordinator = ZeroTrustGateCoordinator()

    def test_lint_all_artifacts_100_percent_compliant(self):
        ensemble = {
            1: self.mock_gen._mock_strategy(STRATIFIED_PROFILES["balanced"], "balanced"),
            2: self.mock_gen._mock_finance(STRATIFIED_PROFILES["balanced"], "balanced"),
            3: self.mock_gen._mock_legal(STRATIFIED_PROFILES["balanced"], "balanced"),
            4: self.mock_gen._mock_security(STRATIFIED_PROFILES["balanced"], "balanced"),
            5: self.mock_gen._mock_system_analysis(STRATIFIED_PROFILES["balanced"], "balanced", False),
            6: self.mock_gen._mock_hardware(STRATIFIED_PROFILES["balanced"], "balanced", False),
            7: self.mock_gen._mock_quality(STRATIFIED_PROFILES["balanced"], "balanced"),
        }
        report = self.linter.lint_all_artifacts(ensemble)
        self.assertTrue(report["all_standards_compliant"])
        self.assertEqual(report["overall_compliance_score_pct"], 100.0)
        self.assertEqual(report["critical_violations_count"], 0)
        self.assertEqual(report["error_violations_count"], 0)
        self.assertGreaterEqual(report["enforced_standards_count"], 15)

    def test_zero_trust_gate_rejection_on_standards_failure(self):
        bad_legal = self.mock_gen._mock_legal(STRATIFIED_PROFILES["balanced"], "balanced")
        bad_legal["approved_open_source_licenses"] = ["PROPRIETARY_CLOSED_SOURCE_NO_SPDX"]
        passed, msg, telem = self.coordinator.verify_node_stage_gate(3, bad_legal, {})
        self.assertFalse(passed)
        self.assertIn("Standards Non-Compliance", msg)

    def test_ai_native_rag_pipeline_validation(self):
        analysis = self.mock_gen._mock_system_analysis(STRATIFIED_PROFILES["balanced"], "balanced", False)
        res = self.linter.lint_node_artifact(5, analysis)
        self.assertTrue(res.is_compliant)
        self.assertIn("AI_NATIVE_RAG", res.checked_standards)

        bad_analysis = copy.deepcopy(analysis)
        bad_analysis["rag_pipeline"]["chunk_size_tokens"] = 9999  # > 2048
        bad_res = self.linter.lint_node_artifact(5, bad_analysis)
        self.assertFalse(bad_res.is_compliant)
        self.assertTrue(any("chunk size" in v.message.lower() for v in bad_res.violations))

    def test_ai_native_security_prompt_quarantine_validation(self):
        sec = self.mock_gen._mock_security(STRATIFIED_PROFILES["balanced"], "balanced")
        res = self.linter.lint_node_artifact(4, sec)
        self.assertTrue(res.is_compliant)
        self.assertIn("OWASP_LLM_TOP10", res.checked_standards)

        bad_sec = copy.deepcopy(sec)
        bad_sec["ai_security"]["prompt_quarantine_enforced"] = False
        bad_res = self.linter.lint_node_artifact(4, bad_sec)
        self.assertFalse(bad_res.is_compliant)
        self.assertTrue(any(v.severity == "CRITICAL" and "prompt_quarantine" in v.message for v in bad_res.violations))

    def test_ai_native_quality_rag_triad_validation(self):
        qual = self.mock_gen._mock_quality(STRATIFIED_PROFILES["balanced"], "balanced")
        res = self.linter.lint_node_artifact(7, qual)
        self.assertTrue(res.is_compliant)
        self.assertIn("RAG_TRIAD_METRICS", res.checked_standards)

        bad_qual = copy.deepcopy(qual)
        bad_qual["cognitive_rag_triad"]["groundedness_faithfulness_score"] = 0.80  # < 0.95
        bad_res = self.linter.lint_node_artifact(7, bad_qual)
        self.assertFalse(bad_res.is_compliant)
        self.assertTrue(any("faithfulness" in v.message.lower() for v in bad_res.violations))


class TestModules8And9Standards(unittest.TestCase):
    def setUp(self):
        self.linter = StandardsLinter()

    def test_synthesized_code_valid_passes(self):
        valid_code_data = {
            "all_ast_valid": True,
            "files": {
                "main.py": "from app_schemas import ProblemDetails\n...",
                "app_schemas.py": "class ProblemDetails(BaseModel): pass",
            }
        }
        res = self.linter.lint_node_artifact(8, valid_code_data)
        self.assertTrue(res.is_compliant)
        self.assertIn("SPEC_TO_CODE_SYNTAX", res.checked_standards)

    def test_synthesized_code_ast_failure(self):
        bad_code_data = {
            "all_ast_valid": False,
            "files": {}
        }
        res = self.linter.lint_node_artifact(8, bad_code_data)
        self.assertFalse(res.is_compliant)
        self.assertTrue(any(v.standard_id == "SPEC_TO_CODE_SYNTAX" for v in res.violations))

    def test_synthesized_tests_100_percent_pass(self):
        test_result = {
            "success": True,
            "tests_run": 10,
            "failures": 0,
            "errors": 0,
        }
        res = self.linter.lint_node_artifact(9, test_result)
        self.assertTrue(res.is_compliant)
        self.assertIn("EXECUTABLE_BDD_PASS", res.checked_standards)

    def test_synthesized_tests_failure_violation(self):
        bad_test_result = {
            "success": False,
            "tests_run": 10,
            "failures": 1,
            "errors": 0,
        }
        res = self.linter.lint_node_artifact(9, bad_test_result)
        self.assertFalse(res.is_compliant)
        self.assertTrue(any(v.standard_id == "EXECUTABLE_BDD_PASS" for v in res.violations))


if __name__ == "__main__":
    unittest.main()
