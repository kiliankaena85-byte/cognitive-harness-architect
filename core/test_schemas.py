"""
core/test_schemas.py
Zero-Trust CDD-TDD Formal Verification Test Suite for Milestone 1 (7 Ministry Schemas).
Compatible with: python -m unittest discover -s core -p "test_*.py"
"""

import sys
import time
import unittest
from pathlib import Path
from typing import Any, Dict, List

# Hypothesis for Property-Based Testing
from hypothesis import given, settings, strategies as st
from pydantic import ValidationError

# Setup pathing for absolute and package-relative discovery
PROJECT_ROOT = Path(__file__).resolve().parent.parent
CORE_DIR = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(CORE_DIR) not in sys.path:
    sys.path.insert(0, str(CORE_DIR))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

try:
    from core.schemas import (
        ApiEndpoint,
        BusinessRule,
        CONTRACT_SCHEMAS_REGISTRY,
        FinanceBudgetContract,
        GherkinScenario,
        HardwareRuntimeContract,
        LegalComplianceContract,
        MINISTRY_ARTIFACT_REGISTRY,
        MINISTRY_CONTRACT_REGISTRY,
        MINISTRY_ID_MAP,
        PersonalDataProcessing,
        REQUIRED_STRIDE_CATEGORIES,
        SecurityPolicyContract,
        StrategyCJMContract,
        StrideThreat,
        SystemAnalysisContract,
        VVQualityContract,
        compute_contract_hash,
        deserialize_contract,
        export_contract_schema,
        get_contract_class,
        serialize_contract,
    )
except ImportError:
    from schemas import (  # type: ignore
        ApiEndpoint,
        BusinessRule,
        CONTRACT_SCHEMAS_REGISTRY,
        FinanceBudgetContract,
        GherkinScenario,
        HardwareRuntimeContract,
        LegalComplianceContract,
        MINISTRY_ARTIFACT_REGISTRY,
        MINISTRY_CONTRACT_REGISTRY,
        MINISTRY_ID_MAP,
        PersonalDataProcessing,
        REQUIRED_STRIDE_CATEGORIES,
        SecurityPolicyContract,
        StrategyCJMContract,
        StrideThreat,
        SystemAnalysisContract,
        VVQualityContract,
        compute_contract_hash,
        deserialize_contract,
        export_contract_schema,
        get_contract_class,
        serialize_contract,
    )


def make_valid_cjm_payload() -> Dict[str, Any]:
    return {
        "project_id": "PRJ-AUTONOMOUS-CORE-001",
        "product_vision": "Autonomous cognitive task decomposition engine with zero-trust verification.",
        "target_personas": ["Enterprise Architect", "DevOps Engineer"],
        "jobs_to_be_done": ["Automate architectural specification synthesis."],
        "acceptance_criteria": [
            {
                "id": "AC-LOGIN-1",
                "given": "User has valid mTLS cert",
                "when": "User submits orchestrate request",
                "then": "Return 200 OK with execution task id",
            },
            {
                "id": "AC-CORE-2",
                "given": "Pipeline receives prompt",
                "when": "Cognitive DAG runs 7 ministries",
                "then": "Output all 7 validated JSON artifacts",
            },
        ],
        "business_rules": [
            {
                "rule_id": "BR-101",
                "description": "Authenticate all incoming connections using mutual TLS.",
                "source_ac_id": "AC-LOGIN-1",
            },
            {
                "rule_id": "BR-102",
                "description": "Execute deterministic zero-trust CDD-TDD gates on artifacts.",
                "source_ac_id": "AC-CORE-2",
            },
        ],
    }


def make_valid_finance_payload() -> Dict[str, Any]:
    return {
        "currency": "RUB",
        "customer_acquisition_cost": 1000.0,
        "lifetime_value": 3500.0,
        "target_margin_pct": 25.0,
        "max_cloud_monthly_opex": 50000.0,
        "max_hardware_capex": 200000.0,
        "break_even_period_months": 18,
    }


def make_valid_legal_payload() -> Dict[str, Any]:
    return {
        "jurisdiction": ["RUS", "EAEU"],
        "personal_data": {
            "processes_personal_data": True,
            "data_subjects": ["Enterprise Customers", "Operators"],
            "localization_country": "RUS",
            "fz152_level": "УЗ-1",
            "gdpr_dpa_required": False,
        },
        "fiscal_receipts_54fz": True,
        "ai_act_risk_category": "LIMITED",
        "approved_open_source_licenses": ["Apache-2.0", "MIT", "BSD-3-Clause"],
    }


def make_valid_security_payload() -> Dict[str, Any]:
    return {
        "zero_trust_enforced": True,
        "auth_mechanisms": ["JWT_ED25519", "MTLS"],
        "stride_matrix": [
            {
                "category": "SPOOFING",
                "target_component": "API_Gateway",
                "mitigation_strategy": "Enforce mTLS client certs",
            },
            {
                "category": "TAMPERING",
                "target_component": "Model_Weights",
                "mitigation_strategy": "Verify SHA-256 HMAC digest",
            },
            {
                "category": "REPUDIATION",
                "target_component": "Audit_Trail",
                "mitigation_strategy": "Append-only cryptographic WORM logging",
            },
            {
                "category": "INFO_DISCLOSURE",
                "target_component": "Vector_Store",
                "mitigation_strategy": "Encrypt embeddings with AES-256-GCM",
            },
            {
                "category": "DENIAL_OF_SERVICE",
                "target_component": "Inference_Worker",
                "mitigation_strategy": "Token-bucket rate limiter 20 RPM",
            },
            {
                "category": "ELEVATION_OF_PRIVILEGE",
                "target_component": "Kernel_Driver",
                "mitigation_strategy": "Enforce strict Linux seccomp filters",
            },
        ],
        "rate_limiting_rps_per_ip": 100,
        "data_encryption_at_rest": "AES_256_GCM",
        "data_encryption_in_transit": "TLS_1_3",
        "fstec_gost_56939_certified": True,
    }


def make_valid_analysis_payload() -> Dict[str, Any]:
    return {
        "architecture_pattern": "EVENT_DRIVEN_MICROSERVICES",
        "openapi_version": "3.1.0",
        "endpoints": [
            {
                "path": "/api/v1/orchestrate",
                "method": "POST",
                "requires_auth": True,
                "idempotent": True,
                "timeout_ms": 3000,
            },
            {
                "path": "/api/v1/health",
                "method": "GET",
                "requires_auth": False,
                "idempotent": True,
                "timeout_ms": 500,
            },
        ],
        "async_message_bus": "KAFKA",
        "database_normalization": "3NF",
        "cyclic_dependencies_detected": False,
    }


def make_valid_hardware_payload() -> Dict[str, Any]:
    return {
        "target_cpu_profile": "Intel Core Ultra 5 125H",
        "target_npu_device": "INTEL_AI_BOOST_VPU_3720",
        "openvino_version": "2026.4.0",
        "max_ram_budget_mb": 512.0,
        "p99_latency_ms": 45.0,
        "cold_start_budget_ms": 95.0,
        "hardware_interlocks_required": False,
        "physical_actuator_latency_ms": 250.0,
    }


def make_valid_quality_payload() -> Dict[str, Any]:
    return {
        "gost_34_602_all_sections_present": True,
        "iso_29148_unambiguity_score": 92.5,
        "rtm_traceability_coverage_pct": 100.0,
        "mutation_score_pct": 98.2,
        "brier_score_calibration": 0.025,
        "hoare_logic_invariants_verified": 9,
        "cryptographic_release_signature": "a1b2c3d4e5f67890" * 4,
    }


# =====================================================================
# 1. Ministry 1: Strategy, Marketing & CJM
# =====================================================================
class TestStrategyCJMContract(unittest.TestCase):
    def test_valid_contract_instantiation(self):
        payload = make_valid_cjm_payload()
        contract = StrategyCJMContract(**payload)
        self.assertEqual(contract.project_id, "PRJ-AUTONOMOUS-CORE-001")
        self.assertEqual(len(contract.acceptance_criteria), 2)
        self.assertEqual(len(contract.business_rules), 2)

    def test_gherkin_scenario_id_regex(self):
        valid_ids = ["AC-LOGIN-1", "AC-CORE-102", "AC-PAYMENT99-1"]
        for aid in valid_ids:
            scen = GherkinScenario(
                id=aid, given="Given user auth", when="When user clicks", then="Then proceed"
            )
            self.assertEqual(scen.id, aid)

        invalid_ids = ["AC-1", "ac-login-1", "AC-LOGIN", "AC--1", "", "LOGIN-1"]
        for aid in invalid_ids:
            with self.assertRaises(ValidationError, msg=f"Should reject {aid}"):
                GherkinScenario(
                    id=aid, given="Given user auth", when="When user clicks", then="Then proceed"
                )

    def test_gherkin_scenario_text_lengths(self):
        with self.assertRaises(ValidationError):
            GherkinScenario(id="AC-OK-1", given="1234", when="12345", then="12345")
        with self.assertRaises(ValidationError):
            GherkinScenario(id="AC-OK-1", given="12345", when="1234", then="12345")
        with self.assertRaises(ValidationError):
            GherkinScenario(id="AC-OK-1", given="12345", when="12345", then="1234")
        scen = GherkinScenario(id="AC-OK-1", given="12345", when="12345", then="12345")
        self.assertEqual(len(scen.given), 5)

    def test_business_rule_rule_id_regex(self):
        valid_rules = ["BR-1", "BR-101", "BR-99999"]
        for rid in valid_rules:
            br = BusinessRule(
                rule_id=rid,
                description="A valid business rule description",
                source_ac_id="AC-OK-1",
            )
            self.assertEqual(br.rule_id, rid)

        invalid_rules = ["BR-", "BR-AUTH", "br-101", "RULE-1", ""]
        for rid in invalid_rules:
            with self.assertRaises(ValidationError):
                BusinessRule(
                    rule_id=rid,
                    description="A valid business rule description",
                    source_ac_id="AC-OK-1",
                )

    def test_business_rule_description_length(self):
        with self.assertRaises(ValidationError):
            BusinessRule(rule_id="BR-1", description="123456789", source_ac_id="AC-OK-1")
        br = BusinessRule(rule_id="BR-1", description="1234567890", source_ac_id="AC-OK-1")
        self.assertEqual(len(br.description), 10)

    def test_strategy_contract_empty_lists(self):
        base = make_valid_cjm_payload()
        for field in [
            "target_personas",
            "jobs_to_be_done",
            "acceptance_criteria",
            "business_rules",
        ]:
            bad = dict(base)
            bad[field] = []
            with self.assertRaises(ValidationError, msg=f"Should reject empty {field}"):
                StrategyCJMContract(**bad)

    def test_strategy_contract_product_vision_length(self):
        base = make_valid_cjm_payload()
        base["product_vision"] = "Short vision (19c)!"  # 19 chars
        with self.assertRaises(ValidationError):
            StrategyCJMContract(**base)
        base["product_vision"] = "Vision with 20 chars"  # 20 chars
        contract = StrategyCJMContract(**base)
        self.assertEqual(len(contract.product_vision), 20)

    def test_bidirectional_traceability_violation(self):
        base = make_valid_cjm_payload()
        base["business_rules"].append(
            {
                "rule_id": "BR-999",
                "description": "Adversarial fee rule with hallucinated source AC",
                "source_ac_id": "AC-NONEXISTENT-99",
            }
        )
        with self.assertRaises(ValidationError) as ctx:
            StrategyCJMContract(**base)
        self.assertIn("Adversarial Rule BR-999", str(ctx.exception))
        self.assertIn("AC-NONEXISTENT-99", str(ctx.exception))

    def test_extra_attributes_forbidden(self):
        base = make_valid_cjm_payload()
        base["adversarial_injection"] = "hacked"
        with self.assertRaises(ValidationError):
            StrategyCJMContract(**base)


# =====================================================================
# 2. Ministry 2: Finance & Unit Economics
# =====================================================================
class TestFinanceBudgetContract(unittest.TestCase):
    def test_valid_contract_instantiation(self):
        payload = make_valid_finance_payload()
        contract = FinanceBudgetContract(**payload)
        self.assertEqual(contract.currency, "RUB")
        self.assertEqual(contract.customer_acquisition_cost, 1000.0)

    def test_currency_literal_enum(self):
        payload = make_valid_finance_payload()
        for curr in ["RUB", "USD", "EUR"]:
            payload["currency"] = curr
            c = FinanceBudgetContract(**payload)
            self.assertEqual(c.currency, curr)

        for bad in ["GBP", "JPY", "BTC", ""]:
            payload["currency"] = bad
            with self.assertRaises(ValidationError):
                FinanceBudgetContract(**payload)

    def test_cac_positive_boundary(self):
        payload = make_valid_finance_payload()
        payload["customer_acquisition_cost"] = 0.0
        with self.assertRaises(ValidationError):
            FinanceBudgetContract(**payload)
        payload["customer_acquisition_cost"] = -10.0
        with self.assertRaises(ValidationError):
            FinanceBudgetContract(**payload)
        payload["customer_acquisition_cost"] = 0.01
        payload["lifetime_value"] = 0.05
        c = FinanceBudgetContract(**payload)
        self.assertGreater(c.customer_acquisition_cost, 0)

    def test_ltv_cac_ratio_boundary(self):
        payload = make_valid_finance_payload()
        payload["customer_acquisition_cost"] = 100.0

        # Sub-3.0 ratio: strictly rejected
        payload["lifetime_value"] = 299.9
        with self.assertRaises(ValidationError) as ctx:
            FinanceBudgetContract(**payload)
        self.assertIn("Unit Economics Insolvent", str(ctx.exception))
        self.assertIn("strictly below 3.0 barrier", str(ctx.exception))

        # Exact 3.0 ratio: accepted
        payload["lifetime_value"] = 300.0
        c = FinanceBudgetContract(**payload)
        self.assertAlmostEqual(c.lifetime_value / c.customer_acquisition_cost, 3.0)

        # Above 3.0 ratio: accepted
        payload["lifetime_value"] = 300.01
        c = FinanceBudgetContract(**payload)
        self.assertGreaterEqual(c.lifetime_value / c.customer_acquisition_cost, 3.0)

    def test_target_margin_pct_boundary(self):
        payload = make_valid_finance_payload()
        payload["target_margin_pct"] = 14.99
        with self.assertRaises(ValidationError):
            FinanceBudgetContract(**payload)
        payload["target_margin_pct"] = 15.0
        c = FinanceBudgetContract(**payload)
        self.assertEqual(c.target_margin_pct, 15.0)

    def test_break_even_period_months_boundary(self):
        payload = make_valid_finance_payload()
        payload["break_even_period_months"] = 25
        with self.assertRaises(ValidationError):
            FinanceBudgetContract(**payload)
        payload["break_even_period_months"] = 24
        c = FinanceBudgetContract(**payload)
        self.assertEqual(c.break_even_period_months, 24)

    def test_opex_capex_positive(self):
        payload = make_valid_finance_payload()
        payload["max_cloud_monthly_opex"] = 0.0
        with self.assertRaises(ValidationError):
            FinanceBudgetContract(**payload)
        payload["max_cloud_monthly_opex"] = 500.0

        payload["max_hardware_capex"] = 0.0
        with self.assertRaises(ValidationError):
            FinanceBudgetContract(**payload)

    @given(
        cac=st.floats(min_value=1.0, max_value=10_000.0, allow_nan=False, allow_infinity=False),
        multiplier=st.floats(min_value=0.01, max_value=2.99, allow_nan=False, allow_infinity=False),
    )
    @settings(max_examples=50, deadline=None)
    def test_pbt_ltv_cac_insolvent_always_rejected(self, cac, multiplier):
        ltv = cac * multiplier
        with self.assertRaises(ValidationError):
            FinanceBudgetContract(
                currency="RUB",
                customer_acquisition_cost=cac,
                lifetime_value=ltv,
                target_margin_pct=20.0,
                max_cloud_monthly_opex=10000.0,
                max_hardware_capex=10000.0,
                break_even_period_months=12,
            )


# =====================================================================
# 3. Ministry 3: Legal & Regulatory Compliance
# =====================================================================
class TestLegalComplianceContract(unittest.TestCase):
    def test_valid_contract_instantiation(self):
        payload = make_valid_legal_payload()
        contract = LegalComplianceContract(**payload)
        self.assertEqual(contract.jurisdiction, ["RUS", "EAEU"])
        self.assertEqual(contract.personal_data.fz152_level, "УЗ-1")

    def test_jurisdiction_min_length(self):
        payload = make_valid_legal_payload()
        payload["jurisdiction"] = []
        with self.assertRaises(ValidationError):
            LegalComplianceContract(**payload)

    def test_fz152_level_literals(self):
        for lvl in ["УЗ-1", "УЗ-2", "УЗ-3", "УЗ-4", "NONE"]:
            pd = PersonalDataProcessing(
                processes_personal_data=True,
                data_subjects=["Users"],
                localization_country="RUS",
                fz152_level=lvl,
                gdpr_dpa_required=False,
            )
            self.assertEqual(pd.fz152_level, lvl)

        for bad in ["УЗ-5", "UZ-1", "HIGH", ""]:
            with self.assertRaises(ValidationError):
                PersonalDataProcessing(
                    processes_personal_data=True,
                    data_subjects=["Users"],
                    localization_country="RUS",
                    fz152_level=bad,
                    gdpr_dpa_required=False,
                )

    def test_fz152_regulatory_fields(self):
        """Verifies 152-FZ / FSTEC regulatory fields on PersonalDataProcessing."""
        # Defaults
        pd_default = PersonalDataProcessing(
            processes_personal_data=True,
            data_subjects=["Users"],
            localization_country="RUS",
            fz152_level="УЗ-2",
            gdpr_dpa_required=False,
        )
        self.assertTrue(pd_default.data_localization_rf)
        self.assertEqual(pd_default.personal_data_categories, ["ОБЩИЕ"])
        self.assertFalse(pd_default.cross_border_transfer_allowed)
        self.assertEqual(pd_default.crypto_algorithm, "ГОСТ_Р_34.12-2015_КУЗНЕЧИК")

        # Custom valid configurations
        pd_custom = PersonalDataProcessing(
            processes_personal_data=True,
            data_subjects=["Employees", "Clients"],
            localization_country="RUS",
            data_localization_rf=True,
            personal_data_categories=["ОБЩИЕ", "СПЕЦИАЛЬНЫЕ", "БИОМЕТРИЧЕСКИЕ"],
            cross_border_transfer_allowed=True,
            crypto_algorithm="ГОСТ_Р_34.12-2015_МАГМА",
            fz152_level="УЗ-1",
            gdpr_dpa_required=True,
        )
        self.assertEqual(len(pd_custom.personal_data_categories), 3)
        self.assertEqual(pd_custom.crypto_algorithm, "ГОСТ_Р_34.12-2015_МАГМА")
        self.assertTrue(pd_custom.cross_border_transfer_allowed)

        # Invalid category rejection
        with self.assertRaises(ValidationError):
            PersonalDataProcessing(
                processes_personal_data=True,
                data_subjects=["Users"],
                localization_country="RUS",
                personal_data_categories=["INVALID_CATEGORY"],
                fz152_level="УЗ-2",
            )

    def test_eu_ai_act_risk_category(self):
        payload = make_valid_legal_payload()

        # UNACCEPTABLE risk triggers compliance veto
        payload["ai_act_risk_category"] = "UNACCEPTABLE"
        with self.assertRaises(ValidationError) as ctx:
            LegalComplianceContract(**payload)
        self.assertIn("Compliance Veto", str(ctx.exception))
        self.assertIn("UNACCEPTABLE", str(ctx.exception))

        # Permitted categories
        for allowed in ["MINIMAL", "LIMITED", "HIGH"]:
            payload["ai_act_risk_category"] = allowed
            c = LegalComplianceContract(**payload)
            self.assertEqual(c.ai_act_risk_category, allowed)

        # Invalid literal
        payload["ai_act_risk_category"] = "PROHIBITED"
        with self.assertRaises(ValidationError):
            LegalComplianceContract(**payload)


# =====================================================================
# 4. Ministry 4: Information Security & Threat Modeling
# =====================================================================
class TestSecurityPolicyContract(unittest.TestCase):
    def test_valid_contract_instantiation(self):
        payload = make_valid_security_payload()
        contract = SecurityPolicyContract(**payload)
        self.assertTrue(contract.zero_trust_enforced)
        self.assertEqual(len(contract.stride_matrix), 6)

    def test_stride_threat_fields(self):
        valid_categories = [
            "SPOOFING",
            "TAMPERING",
            "REPUDIATION",
            "INFO_DISCLOSURE",
            "DENIAL_OF_SERVICE",
            "ELEVATION_OF_PRIVILEGE",
        ]
        for cat in valid_categories:
            t = StrideThreat(
                category=cat,
                target_component="Gateway",
                mitigation_strategy="Valid 10+ chars mitigation",
            )
            self.assertEqual(t.category, cat)

        with self.assertRaises(ValidationError):
            StrideThreat(
                category="UNKNOWN_ATTACK",
                target_component="Gateway",
                mitigation_strategy="Valid mitigation strategy",
            )

        # mitigation min_length=10 boundary
        with self.assertRaises(ValidationError):
            StrideThreat(
                category="SPOOFING",
                target_component="Gateway",
                mitigation_strategy="123456789",
            )
        t = StrideThreat(
            category="SPOOFING",
            target_component="Gateway",
            mitigation_strategy="1234567890",
        )
        self.assertEqual(len(t.mitigation_strategy), 10)

    def test_rate_limiting_boundaries(self):
        payload = make_valid_security_payload()

        payload["rate_limiting_rps_per_ip"] = 0
        with self.assertRaises(ValidationError):
            SecurityPolicyContract(**payload)

        payload["rate_limiting_rps_per_ip"] = 1
        c = SecurityPolicyContract(**payload)
        self.assertEqual(c.rate_limiting_rps_per_ip, 1)

        payload["rate_limiting_rps_per_ip"] = 1000
        c = SecurityPolicyContract(**payload)
        self.assertEqual(c.rate_limiting_rps_per_ip, 1000)

        payload["rate_limiting_rps_per_ip"] = 1001
        with self.assertRaises(ValidationError):
            SecurityPolicyContract(**payload)

    def test_stride_matrix_complete_coverage(self):
        payload = make_valid_security_payload()

        # Less than 6 threats
        payload["stride_matrix"] = payload["stride_matrix"][:5]
        with self.assertRaises(ValidationError):
            SecurityPolicyContract(**payload)

        # 6 threats, but all are SPOOFING (missing other 5 categories)
        payload["stride_matrix"] = [
            {
                "category": "SPOOFING",
                "target_component": f"Comp_{i}",
                "mitigation_strategy": "Valid mitigation text",
            }
            for i in range(6)
        ]
        with self.assertRaises(ValidationError) as ctx:
            SecurityPolicyContract(**payload)
        self.assertIn("Incomplete STRIDE matrix", str(ctx.exception))

    def test_ciphers_and_tls_literals(self):
        payload = make_valid_security_payload()

        # Encryption at rest
        for valid in ["AES_256_GCM", "GOST_KUZNYECHIK"]:
            payload["data_encryption_at_rest"] = valid
            c = SecurityPolicyContract(**payload)
            self.assertEqual(c.data_encryption_at_rest, valid)

        payload["data_encryption_at_rest"] = "DES"
        with self.assertRaises(ValidationError):
            SecurityPolicyContract(**payload)

        # Encryption in transit
        payload = make_valid_security_payload()
        payload["data_encryption_in_transit"] = "TLS_1_2"
        with self.assertRaises(ValidationError):
            SecurityPolicyContract(**payload)


# =====================================================================
# 5. Ministry 5: System Analysis & Architecture
# =====================================================================
class TestSystemAnalysisContract(unittest.TestCase):
    def test_valid_contract_instantiation(self):
        payload = make_valid_analysis_payload()
        contract = SystemAnalysisContract(**payload)
        self.assertEqual(contract.architecture_pattern, "EVENT_DRIVEN_MICROSERVICES")
        self.assertEqual(len(contract.endpoints), 2)

    def test_api_endpoint_fields(self):
        for method in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
            ep = ApiEndpoint(
                path="/test",
                method=method,
                requires_auth=True,
                idempotent=True,
                timeout_ms=5000,
            )
            self.assertEqual(ep.method, method)

        with self.assertRaises(ValidationError):
            ApiEndpoint(
                path="/test",
                method="HEAD",
                requires_auth=True,
                idempotent=True,
                timeout_ms=5000,
            )

        # timeout_ms boundary
        with self.assertRaises(ValidationError):
            ApiEndpoint(
                path="/test",
                method="GET",
                requires_auth=True,
                idempotent=True,
                timeout_ms=5001,
            )

        ep = ApiEndpoint(
            path="/test",
            method="GET",
            requires_auth=True,
            idempotent=True,
            timeout_ms=5000,
        )
        self.assertEqual(ep.timeout_ms, 5000)

    def test_cyclic_dependencies_veto(self):
        payload = make_valid_analysis_payload()
        payload["cyclic_dependencies_detected"] = True
        with self.assertRaises(ValidationError) as ctx:
            SystemAnalysisContract(**payload)
        self.assertIn("Architecture Veto", str(ctx.exception))
        self.assertIn("Cyclic dependencies", str(ctx.exception))

    def test_endpoints_min_length(self):
        payload = make_valid_analysis_payload()
        payload["endpoints"] = []
        with self.assertRaises(ValidationError):
            SystemAnalysisContract(**payload)


# =====================================================================
# 6. Ministry 6: Hardware Runtime & Edge NPU
# =====================================================================
class TestHardwareRuntimeContract(unittest.TestCase):
    def test_valid_contract_instantiation(self):
        payload = make_valid_hardware_payload()
        contract = HardwareRuntimeContract(**payload)
        self.assertEqual(contract.target_cpu_profile, "Intel Core Ultra 5 125H")
        self.assertFalse(contract.hardware_interlocks_required)

    def test_target_npu_device_literals(self):
        payload = make_valid_hardware_payload()
        for dev in ["INTEL_AI_BOOST_VPU_3720", "INTEL_ARC_GPU", "CPU_FALLBACK"]:
            payload["target_npu_device"] = dev
            c = HardwareRuntimeContract(**payload)
            self.assertEqual(c.target_npu_device, dev)

        payload["target_npu_device"] = "CUDA_GPU"
        with self.assertRaises(ValidationError):
            HardwareRuntimeContract(**payload)

    def test_ram_budget_boundary(self):
        payload = make_valid_hardware_payload()
        payload["max_ram_budget_mb"] = 512.0
        c = HardwareRuntimeContract(**payload)
        self.assertEqual(c.max_ram_budget_mb, 512.0)

        payload["max_ram_budget_mb"] = 512.1
        with self.assertRaises(ValidationError):
            HardwareRuntimeContract(**payload)

        payload["max_ram_budget_mb"] = 1024.0
        with self.assertRaises(ValidationError):
            HardwareRuntimeContract(**payload)

    def test_p99_latency_boundary(self):
        payload = make_valid_hardware_payload()
        payload["p99_latency_ms"] = 50.0
        c = HardwareRuntimeContract(**payload)
        self.assertEqual(c.p99_latency_ms, 50.0)

        payload["p99_latency_ms"] = 50.1
        with self.assertRaises(ValidationError):
            HardwareRuntimeContract(**payload)

    def test_cold_start_budget_boundary(self):
        payload = make_valid_hardware_payload()
        payload["cold_start_budget_ms"] = 100.0
        c = HardwareRuntimeContract(**payload)
        self.assertEqual(c.cold_start_budget_ms, 100.0)

        payload["cold_start_budget_ms"] = 100.1
        with self.assertRaises(ValidationError):
            HardwareRuntimeContract(**payload)

    def test_therac25_physical_actuator_hazard_guard(self):
        payload = make_valid_hardware_payload()

        # Exactly 1000.0 ms without interlocks: PASS (> 1000.0 is False)
        payload["physical_actuator_latency_ms"] = 1000.0
        payload["hardware_interlocks_required"] = False
        c = HardwareRuntimeContract(**payload)
        self.assertEqual(c.physical_actuator_latency_ms, 1000.0)

        # 1000.1 ms without interlocks: VETO with Therac-25 Hazard
        payload["physical_actuator_latency_ms"] = 1000.1
        payload["hardware_interlocks_required"] = False
        with self.assertRaises(ValidationError) as ctx:
            HardwareRuntimeContract(**payload)
        self.assertIn("Therac-25 Hazard", str(ctx.exception))
        self.assertIn("Hardware Interlocks", str(ctx.exception))

        # 1000.1 ms with interlocks: PASS
        payload["hardware_interlocks_required"] = True
        c = HardwareRuntimeContract(**payload)
        self.assertTrue(c.hardware_interlocks_required)

        # 5000.0 ms with interlocks: PASS
        payload["physical_actuator_latency_ms"] = 5000.0
        c = HardwareRuntimeContract(**payload)
        self.assertEqual(c.physical_actuator_latency_ms, 5000.0)

    @given(
        latency=st.floats(
            min_value=1000.01, max_value=60_000.0, allow_nan=False, allow_infinity=False
        )
    )
    @settings(max_examples=50, deadline=None)
    def test_pbt_therac25_latency_without_interlocks_always_rejected(self, latency):
        with self.assertRaises(ValidationError):
            HardwareRuntimeContract(
                target_cpu_profile="Intel Core Ultra 5 125H",
                target_npu_device="INTEL_AI_BOOST_VPU_3720",
                max_ram_budget_mb=256.0,
                p99_latency_ms=25.0,
                cold_start_budget_ms=50.0,
                hardware_interlocks_required=False,
                physical_actuator_latency_ms=latency,
            )


# =====================================================================
# 7. Ministry 7: V&V Quality Gate & Certification
# =====================================================================
class TestVVQualityContract(unittest.TestCase):
    def test_valid_contract_instantiation(self):
        payload = make_valid_quality_payload()
        contract = VVQualityContract(**payload)
        self.assertTrue(contract.gost_34_602_all_sections_present)
        self.assertEqual(contract.iso_29148_unambiguity_score, 92.5)

    def test_gost_completeness_flag(self):
        payload = make_valid_quality_payload()
        payload["gost_34_602_all_sections_present"] = False
        with self.assertRaises(ValidationError) as ctx:
            VVQualityContract(**payload)
        self.assertIn("GOST 34.602 Incomplete", str(ctx.exception))

    def test_iso_score_boundary(self):
        payload = make_valid_quality_payload()
        payload["iso_29148_unambiguity_score"] = 84.9
        with self.assertRaises(ValidationError):
            VVQualityContract(**payload)

        payload["iso_29148_unambiguity_score"] = 85.0
        c = VVQualityContract(**payload)
        self.assertEqual(c.iso_29148_unambiguity_score, 85.0)

    def test_rtm_coverage_boundary(self):
        payload = make_valid_quality_payload()
        payload["rtm_traceability_coverage_pct"] = 99.9
        with self.assertRaises(ValidationError):
            VVQualityContract(**payload)

        payload["rtm_traceability_coverage_pct"] = 100.0
        c = VVQualityContract(**payload)
        self.assertEqual(c.rtm_traceability_coverage_pct, 100.0)

    def test_mutation_score_boundary(self):
        payload = make_valid_quality_payload()
        payload["mutation_score_pct"] = 94.9
        with self.assertRaises(ValidationError):
            VVQualityContract(**payload)

        payload["mutation_score_pct"] = 95.0
        c = VVQualityContract(**payload)
        self.assertEqual(c.mutation_score_pct, 95.0)

    def test_brier_score_boundary(self):
        payload = make_valid_quality_payload()
        payload["brier_score_calibration"] = 0.0401
        with self.assertRaises(ValidationError):
            VVQualityContract(**payload)

        payload["brier_score_calibration"] = 0.0400
        c = VVQualityContract(**payload)
        self.assertEqual(c.brier_score_calibration, 0.04)

    def test_hoare_logic_invariants_boundary(self):
        payload = make_valid_quality_payload()
        payload["hoare_logic_invariants_verified"] = 6
        with self.assertRaises(ValidationError):
            VVQualityContract(**payload)

        payload["hoare_logic_invariants_verified"] = 7
        c = VVQualityContract(**payload)
        self.assertEqual(c.hoare_logic_invariants_verified, 7)

    def test_cryptographic_release_signature_length(self):
        payload = make_valid_quality_payload()
        payload["cryptographic_release_signature"] = "a" * 63
        with self.assertRaises(ValidationError):
            VVQualityContract(**payload)

        payload["cryptographic_release_signature"] = "a" * 64
        c = VVQualityContract(**payload)
        self.assertEqual(len(c.cryptographic_release_signature), 64)


# =====================================================================
# 8. Serialization, Deserialization & JSON Schema Export
# =====================================================================
class TestSerializationAndJSONSchema(unittest.TestCase):
    def test_all_contracts_roundtrip_json_serialization(self):
        factories = [
            (StrategyCJMContract, make_valid_cjm_payload()),
            (FinanceBudgetContract, make_valid_finance_payload()),
            (LegalComplianceContract, make_valid_legal_payload()),
            (SecurityPolicyContract, make_valid_security_payload()),
            (SystemAnalysisContract, make_valid_analysis_payload()),
            (HardwareRuntimeContract, make_valid_hardware_payload()),
            (VVQualityContract, make_valid_quality_payload()),
        ]
        for model_cls, payload in factories:
            instance = model_cls(**payload)
            # Dump to JSON
            json_str = instance.model_dump_json()
            self.assertIsInstance(json_str, str)
            # Reconstruct from JSON
            restored = model_cls.model_validate_json(json_str)
            self.assertEqual(instance.model_dump(), restored.model_dump())

    def test_all_contracts_generate_valid_json_schema(self):
        models = [
            StrategyCJMContract,
            FinanceBudgetContract,
            LegalComplianceContract,
            SecurityPolicyContract,
            SystemAnalysisContract,
            HardwareRuntimeContract,
            VVQualityContract,
        ]
        for model_cls in models:
            schema = model_cls.model_json_schema()
            self.assertIsInstance(schema, dict)
            self.assertIn("properties", schema)
            self.assertIn("title", schema)
            self.assertEqual(schema["type"], "object")

    def test_helper_utilities(self):
        payload = make_valid_finance_payload()
        instance = FinanceBudgetContract(**payload)
        # Serialization helper
        serialized = serialize_contract(instance, indent=2)
        self.assertIn("customer_acquisition_cost", serialized)

        # Deserialization helper from JSON str
        restored = deserialize_contract(FinanceBudgetContract, serialized)
        self.assertEqual(restored.customer_acquisition_cost, 1000.0)

        # Deserialization from dict
        from_dict = deserialize_contract(FinanceBudgetContract, payload)
        self.assertEqual(from_dict.lifetime_value, 3500.0)

        # Hash computation
        h = compute_contract_hash(instance)
        self.assertEqual(len(h), 64)
        self.assertTrue(all(c in "0123456789abcdef" for c in h))

        # Schema export helper
        schema = export_contract_schema(FinanceBudgetContract)
        self.assertIn("properties", schema)


# =====================================================================
# 9. Contract Registry & Resolution Tests
# =====================================================================
class TestContractRegistry(unittest.TestCase):
    def test_registry_lookups(self):
        # By integer index 1..7
        for idx in range(1, 8):
            cls = get_contract_class(idx)
            self.assertIsNotNone(cls)

        # By Ministry ID string
        self.assertEqual(get_contract_class("MINISTRY_1_STRATEGY_CJM"), StrategyCJMContract)
        self.assertEqual(get_contract_class("MINISTRY_2_FINANCE"), FinanceBudgetContract)
        self.assertEqual(get_contract_class("MINISTRY_3_LEGAL_COMPLIANCE"), LegalComplianceContract)
        self.assertEqual(get_contract_class("MINISTRY_4_INFOSEC"), SecurityPolicyContract)
        self.assertEqual(get_contract_class("MINISTRY_5_SYSTEM_ARCHITECTURE"), SystemAnalysisContract)
        self.assertEqual(get_contract_class("MINISTRY_6_HARDWARE_RUNTIME"), HardwareRuntimeContract)
        self.assertEqual(get_contract_class("MINISTRY_7_VV_QUALITY_GATE"), VVQualityContract)

        # By canonical artifact filename
        self.assertEqual(get_contract_class("PRD_Specification.json"), StrategyCJMContract)
        self.assertEqual(get_contract_class("Unit_Economics_Budget.json"), FinanceBudgetContract)
        self.assertEqual(get_contract_class("Compliance_Attestation.json"), LegalComplianceContract)
        self.assertEqual(get_contract_class("Security_Policy.agentpolicy"), SecurityPolicyContract)
        self.assertEqual(get_contract_class("System_Contracts.json"), SystemAnalysisContract)
        self.assertEqual(get_contract_class("Hardware_Runtime_Manifest.json"), HardwareRuntimeContract)
        self.assertEqual(get_contract_class("Release_Certified_Artifacts.json"), VVQualityContract)

        # Invalid lookups raise KeyError
        with self.assertRaises(KeyError):
            get_contract_class(99)
        with self.assertRaises(KeyError):
            get_contract_class("UNKNOWN_MINISTRY")


# =====================================================================
# 10. Sub-Millisecond Rejection Benchmark
# =====================================================================
class TestSubMillisecondRejectionBenchmark(unittest.TestCase):
    def test_sub_millisecond_rejection_performance(self):
        """
        Verify that ValidationError is raised in < 1 ms (1000 µs)
        across multiple invalid contract payloads.
        """
        invalid_scenarios = [
            # 1. Insolvent LTV/CAC
            (
                FinanceBudgetContract,
                {
                    **make_valid_finance_payload(),
                    "lifetime_value": 1500.0,
                    "customer_acquisition_cost": 1000.0,
                },
            ),
            # 2. Unmapped source_ac_id
            (
                StrategyCJMContract,
                {
                    **make_valid_cjm_payload(),
                    "business_rules": [
                        {
                            "rule_id": "BR-1",
                            "description": "Unmapped rule text",
                            "source_ac_id": "AC-MISSING-99",
                        }
                    ],
                },
            ),
            # 3. RAM budget violation (> 512 MB)
            (
                HardwareRuntimeContract,
                {**make_valid_hardware_payload(), "max_ram_budget_mb": 1024.0},
            ),
            # 4. Therac-25 hazard (> 1000ms without interlocks)
            (
                HardwareRuntimeContract,
                {
                    **make_valid_hardware_payload(),
                    "physical_actuator_latency_ms": 2500.0,
                    "hardware_interlocks_required": False,
                },
            ),
            # 5. EU AI Act UNACCEPTABLE risk
            (
                LegalComplianceContract,
                {**make_valid_legal_payload(), "ai_act_risk_category": "UNACCEPTABLE"},
            ),
            # 6. Cyclic dependencies detected
            (
                SystemAnalysisContract,
                {**make_valid_analysis_payload(), "cyclic_dependencies_detected": True},
            ),
            # 7. Incomplete STRIDE matrix
            (
                SecurityPolicyContract,
                {
                    **make_valid_security_payload(),
                    "stride_matrix": make_valid_security_payload()["stride_matrix"][:3],
                },
            ),
        ]

        # Warm-up phase (50 iterations)
        for _ in range(50):
            for model_cls, payload in invalid_scenarios:
                try:
                    model_cls(**payload)
                except ValidationError:
                    pass

        # Benchmarked execution phase (200 iterations per scenario = 1,400 evaluations)
        iterations_per_scenario = 200
        total_evaluations = iterations_per_scenario * len(invalid_scenarios)
        latencies_us: List[float] = []

        for _ in range(iterations_per_scenario):
            for model_cls, payload in invalid_scenarios:
                t0 = time.perf_counter()
                try:
                    model_cls(**payload)
                    self.fail(f"Payload failed to raise ValidationError: {payload}")
                except ValidationError:
                    t1 = time.perf_counter()
                    latencies_us.append((t1 - t0) * 1_000_000.0)

        avg_latency_us = sum(latencies_us) / len(latencies_us)
        p95_latency_us = sorted(latencies_us)[int(len(latencies_us) * 0.95)]
        p99_latency_us = sorted(latencies_us)[int(len(latencies_us) * 0.99)]
        max_latency_us = max(latencies_us)

        print(f"\n[Sub-Millisecond Rejection Benchmark Results]")
        print(f"Total Rejections Evaluated: {total_evaluations}")
        print(f"Average Latency: {avg_latency_us:.2f} µs ({avg_latency_us / 1000.0:.4f} ms)")
        print(f"P95 Latency:     {p95_latency_us:.2f} µs ({p95_latency_us / 1000.0:.4f} ms)")
        print(f"P99 Latency:     {p99_latency_us:.2f} µs ({p99_latency_us / 1000.0:.4f} ms)")
        print(f"Max Latency:     {max_latency_us:.2f} µs ({max_latency_us / 1000.0:.4f} ms)")

        # Target: < 1 ms (1000 µs)
        self.assertLess(
            avg_latency_us,
            1000.0,
            f"Average rejection time {avg_latency_us:.2f}µs exceeded 1000µs (1ms) threshold!",
        )
        self.assertLess(
            p99_latency_us,
            5000.0,
            f"P99 rejection time {p99_latency_us:.2f}µs exceeded 5000µs threshold!",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
