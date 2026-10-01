"""
tests/test_empirical_schemas.py
Empirical Verification & Boundary Stress Harness for Milestone 1 (core/schemas/).
Executes rigorous empirical probes across float precision, temporal invariants,
STRIDE category coverage, intent traceability, regulatory tiers, and rejection latency.
"""

import math
import sys
import time
import unittest
from pathlib import Path
from typing import Any, Dict, List

from pydantic import ValidationError

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.schemas import (
    ApiEndpoint,
    BusinessRule,
    CONTRACT_SCHEMAS_REGISTRY,
    FinanceBudgetContract,
    GherkinScenario,
    HardwareRuntimeContract,
    LegalComplianceContract,
    MINISTRY_ARTIFACT_REGISTRY,
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


def valid_strategy_data() -> Dict[str, Any]:
    return {
        "project_id": "PRJ-EMPIRICAL-001",
        "product_vision": "Empirically verified cognitive pipeline architecture.",
        "target_personas": ["Security Auditor", "Formal Verification Specialist"],
        "jobs_to_be_done": ["Stress-test Pydantic V2 schemas under boundary adversarial inputs."],
        "acceptance_criteria": [
            {
                "id": "AC-TEST-1",
                "given": "System is under adversarial probe",
                "when": "Invalid inputs are injected",
                "then": "Reject within sub-millisecond bound",
            },
            {
                "id": "AC-SEC-2",
                "given": "STRIDE threat model is submitted",
                "when": "Any of 6 categories is missing",
                "then": "Raise formal validation error",
            },
        ],
        "business_rules": [
            {
                "rule_id": "BR-1",
                "description": "Every business rule must strictly ground in an acceptance criterion.",
                "source_ac_id": "AC-TEST-1",
            },
            {
                "rule_id": "BR-2",
                "description": "Zero trust policy must be enforced for all public API routes.",
                "source_ac_id": "AC-SEC-2",
            },
        ],
    }


def valid_finance_data() -> Dict[str, Any]:
    return {
        "currency": "RUB",
        "customer_acquisition_cost": 100.0,
        "lifetime_value": 350.0,
        "target_margin_pct": 20.0,
        "max_cloud_monthly_opex": 15000.0,
        "max_hardware_capex": 50000.0,
        "break_even_period_months": 12,
    }


def valid_legal_data() -> Dict[str, Any]:
    return {
        "jurisdiction": ["RUS"],
        "personal_data": {
            "processes_personal_data": True,
            "data_subjects": ["Russian Citizens"],
            "localization_country": "RUS",
            "fz152_level": "УЗ-1",
            "gdpr_dpa_required": False,
        },
        "fiscal_receipts_54fz": True,
        "ai_act_risk_category": "LIMITED",
        "approved_open_source_licenses": ["MIT", "Apache-2.0"],
    }


def valid_security_data() -> Dict[str, Any]:
    return {
        "zero_trust_enforced": True,
        "auth_mechanisms": ["JWT_ED25519", "MTLS"],
        "stride_matrix": [
            {
                "category": "SPOOFING",
                "target_component": "Auth_Service",
                "mitigation_strategy": "mTLS mutual authentication with hardware keys",
            },
            {
                "category": "TAMPERING",
                "target_component": "Pipeline_State",
                "mitigation_strategy": "Cryptographic HMAC SHA-256 state seals",
            },
            {
                "category": "REPUDIATION",
                "target_component": "Audit_Logger",
                "mitigation_strategy": "Append-only immutable write-once audit log",
            },
            {
                "category": "INFO_DISCLOSURE",
                "target_component": "Secrets_Vault",
                "mitigation_strategy": "Hardware-accelerated AES-256-GCM encryption",
            },
            {
                "category": "DENIAL_OF_SERVICE",
                "target_component": "Public_Gateway",
                "mitigation_strategy": "Token-bucket rate limiting 200 RPS per tenant",
            },
            {
                "category": "ELEVATION_OF_PRIVILEGE",
                "target_component": "Sandbox_Runner",
                "mitigation_strategy": "Strict Linux cgroups v2 and seccomp filters",
            },
        ],
        "rate_limiting_rps_per_ip": 500,
        "data_encryption_at_rest": "AES_256_GCM",
        "data_encryption_in_transit": "TLS_1_3",
        "fstec_gost_56939_certified": True,
    }


def valid_analysis_data() -> Dict[str, Any]:
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
            }
        ],
        "async_message_bus": "NATS",
        "database_normalization": "3NF",
        "cyclic_dependencies_detected": False,
    }


def valid_hardware_data() -> Dict[str, Any]:
    return {
        "target_cpu_profile": "Intel Core Ultra 5 125H",
        "target_npu_device": "INTEL_AI_BOOST_VPU_3720",
        "openvino_version": "2026.4.0",
        "max_ram_budget_mb": 512.0,
        "p99_latency_ms": 50.0,
        "cold_start_budget_ms": 100.0,
        "hardware_interlocks_required": False,
        "physical_actuator_latency_ms": 500.0,
    }


def valid_quality_data() -> Dict[str, Any]:
    return {
        "gost_34_602_all_sections_present": True,
        "iso_29148_unambiguity_score": 90.0,
        "rtm_traceability_coverage_pct": 100.0,
        "mutation_score_pct": 96.0,
        "brier_score_calibration": 0.03,
        "hoare_logic_invariants_verified": 8,
        "cryptographic_release_signature": "f" * 64,
    }


class TestEmpiricalLtvCacPrecisionProbes(unittest.TestCase):
    """Empirical probes for LTV/CAC ratio float precision and boundary behavior."""

    def test_probe_2_9999_vs_3_0_boundary(self):
        """Probe exact boundary around 3.0 ratio with high-precision values."""
        base = valid_finance_data()
        cac = 10000.0

        # Sub-barrier 2.9999: LTV = 29999.0 -> ratio = 2.9999 -> REJECT
        base["customer_acquisition_cost"] = cac
        base["lifetime_value"] = 29999.0
        with self.assertRaises(ValidationError) as ctx:
            FinanceBudgetContract(**base)
        self.assertIn("Unit Economics Insolvent", str(ctx.exception))
        self.assertIn("strictly below 3.0 barrier", str(ctx.exception))

        # Exact barrier 3.0: LTV = 30000.0 -> ratio = 3.0000 -> ACCEPT
        base["lifetime_value"] = 30000.0
        contract = FinanceBudgetContract(**base)
        self.assertEqual(contract.lifetime_value / contract.customer_acquisition_cost, 3.0)

        # Super-barrier 3.0001: LTV = 30001.0 -> ACCEPT
        base["lifetime_value"] = 30001.0
        contract = FinanceBudgetContract(**base)
        self.assertGreater(contract.lifetime_value / contract.customer_acquisition_cost, 3.0)

    def test_probe_float_representation_and_near_epsilon(self):
        """
        Empirically probe IEEE-754 floating point behavior.
        Note: In IEEE-754, 0.3 / 0.1 evaluates to 2.9999999999999996.
        Verify contract behavior on precision edge cases.
        """
        base = valid_finance_data()

        # CAC = 1.0, LTV = 2.999999999999999 (one epsilon below 3.0)
        base["customer_acquisition_cost"] = 1.0
        base["lifetime_value"] = 3.0 - 1e-15
        with self.assertRaises(ValidationError):
            FinanceBudgetContract(**base)

        # CAC = 1.0, LTV = 3.0
        base["lifetime_value"] = 3.0
        c = FinanceBudgetContract(**base)
        self.assertEqual(c.lifetime_value, 3.0)

        # CAC = 0.1, LTV = 0.3 (IEEE-754 division evaluates to 2.9999999999999996 < 3.0)
        base["customer_acquisition_cost"] = 0.1
        base["lifetime_value"] = 0.3
        # Because ratio evaluates strictly < 3.0 in Python float, it raises ValidationError
        with self.assertRaises(ValidationError) as ctx:
            FinanceBudgetContract(**base)
        self.assertIn("Unit Economics Insolvent", str(ctx.exception))

    def test_probe_multi_scale_ltv_cac_generator(self):
        """Empirical generator testing scale invariance from micro-transactions to enterprise contracts."""
        scales = [1.0, 10.0, 100.0, 1_000.0, 50_000.0, 1_000_000.0]
        base = valid_finance_data()

        for scale in scales:
            cac = scale
            # Insolvent: 2.95 * cac
            base["customer_acquisition_cost"] = cac
            base["lifetime_value"] = 2.95 * cac
            with self.assertRaises(ValidationError, msg=f"Scale {scale} failed to reject 2.95x"):
                FinanceBudgetContract(**base)

            # Solvent: 3.05 * cac
            base["lifetime_value"] = 3.05 * cac
            c = FinanceBudgetContract(**base)
            self.assertGreaterEqual(c.lifetime_value / c.customer_acquisition_cost, 3.0)


class TestEmpiricalTherac25LatencyProbes(unittest.TestCase):
    """Empirical probes for Therac-25 race guard and hardware boundary constraints."""

    def test_probe_actuator_latency_1000_vs_1000_1_ms(self):
        """Probe temporal boundary at 1000.0 ms without hardware interlocks."""
        base = valid_hardware_data()

        # Exactly 1000.0 ms without interlocks: strictly <= 1000.0 -> ALLOWED
        base["physical_actuator_latency_ms"] = 1000.0
        base["hardware_interlocks_required"] = False
        contract = HardwareRuntimeContract(**base)
        self.assertEqual(contract.physical_actuator_latency_ms, 1000.0)
        self.assertFalse(contract.hardware_interlocks_required)

        # 1000.1 ms without interlocks: strictly > 1000.0 -> THERAC-25 VETO
        base["physical_actuator_latency_ms"] = 1000.1
        base["hardware_interlocks_required"] = False
        with self.assertRaises(ValidationError) as ctx:
            HardwareRuntimeContract(**base)
        self.assertIn("Therac-25 Hazard", str(ctx.exception))
        self.assertIn("requires mandatory Hardware Interlocks", str(ctx.exception))

        # 1000.0001 ms without interlocks: strictly > 1000.0 -> THERAC-25 VETO
        base["physical_actuator_latency_ms"] = 1000.0001
        with self.assertRaises(ValidationError):
            HardwareRuntimeContract(**base)

        # 1000.1 ms with interlocks: ALLOWED
        base["physical_actuator_latency_ms"] = 1000.1
        base["hardware_interlocks_required"] = True
        contract = HardwareRuntimeContract(**base)
        self.assertTrue(contract.hardware_interlocks_required)
        self.assertEqual(contract.physical_actuator_latency_ms, 1000.1)

    def test_probe_hardware_budgets_strict_ceilings(self):
        """Probe Meteor Lake NPU hardware budget boundary ceilings."""
        base = valid_hardware_data()

        # RAM budget: 512.0 MB (PASS) vs 512.0001 MB (FAIL)
        base["max_ram_budget_mb"] = 512.0
        c = HardwareRuntimeContract(**base)
        self.assertEqual(c.max_ram_budget_mb, 512.0)

        base["max_ram_budget_mb"] = 512.0001
        with self.assertRaises(ValidationError):
            HardwareRuntimeContract(**base)

        # P99 latency: 50.0 ms (PASS) vs 50.0001 ms (FAIL)
        base["max_ram_budget_mb"] = 512.0
        base["p99_latency_ms"] = 50.0
        c = HardwareRuntimeContract(**base)
        self.assertEqual(c.p99_latency_ms, 50.0)

        base["p99_latency_ms"] = 50.0001
        with self.assertRaises(ValidationError):
            HardwareRuntimeContract(**base)

        # Cold start: 100.0 ms (PASS) vs 100.0001 ms (FAIL)
        base["p99_latency_ms"] = 50.0
        base["cold_start_budget_ms"] = 100.0
        c = HardwareRuntimeContract(**base)
        self.assertEqual(c.cold_start_budget_ms, 100.0)

        base["cold_start_budget_ms"] = 100.0001
        with self.assertRaises(ValidationError):
            HardwareRuntimeContract(**base)


class TestEmpiricalStrideCoverageProbes(unittest.TestCase):
    """Empirical probes for STRIDE matrix coverage and duplicate category dynamics."""

    def test_probe_stride_duplicate_categories_behavior(self):
        """
        Probe behavior when categories are duplicated.
        If all 6 categories are present, multiple threats in the same category are ALLOWED.
        If 6 threats are present but 1 category is duplicated and another is missing, it must FAIL.
        """
        base = valid_security_data()

        # Case A: 7 threats - 2 SPOOFING threats, all 6 categories present -> ACCEPTED
        extended_matrix = list(base["stride_matrix"])
        extended_matrix.append(
            {
                "category": "SPOOFING",
                "target_component": "Internal_Service_Mesh",
                "mitigation_strategy": "SPIFFE/SPIRE workload identities with short-lived tokens",
            }
        )
        base["stride_matrix"] = extended_matrix
        contract = SecurityPolicyContract(**base)
        self.assertEqual(len(contract.stride_matrix), 7)

        # Case B: 6 threats - 2 SPOOFING, 0 ELEVATION_OF_PRIVILEGE -> REJECTED
        corrupted_matrix = [t for t in base["stride_matrix"] if t["category"] != "ELEVATION_OF_PRIVILEGE"]
        # Now length is 6, but missing ELEVATION_OF_PRIVILEGE
        self.assertEqual(len(corrupted_matrix), 6)
        base["stride_matrix"] = corrupted_matrix
        with self.assertRaises(ValidationError) as ctx:
            SecurityPolicyContract(**base)
        self.assertIn("Incomplete STRIDE matrix", str(ctx.exception))
        self.assertIn("ELEVATION_OF_PRIVILEGE", str(ctx.exception))

    def test_probe_stride_casing_and_literal_enforcement(self):
        """Probe case sensitivity on STRIDE categories."""
        base = valid_security_data()
        matrix = list(base["stride_matrix"])
        matrix[0] = {
            "category": "spoofing",  # lowercase invalid literal
            "target_component": "Auth_Service",
            "mitigation_strategy": "Valid mitigation text longer than 10 characters",
        }
        base["stride_matrix"] = matrix
        with self.assertRaises(ValidationError):
            SecurityPolicyContract(**base)


class TestEmpiricalIntentTraceabilityProbes(unittest.TestCase):
    """Empirical probes for CJM intent traceability and unmapped source_ac_id."""

    def test_probe_unmapped_source_ac_id_adversarial_rejection(self):
        """Probe injection of ungrounded business rules with hallucinated AC IDs."""
        base = valid_strategy_data()

        # Inject unmapped source_ac_id
        base["business_rules"].append(
            {
                "rule_id": "BR-99",
                "description": "Hallucinated business rule referencing non-existent AC.",
                "source_ac_id": "AC-GHOST-999",
            }
        )
        with self.assertRaises(ValidationError) as ctx:
            StrategyCJMContract(**base)
        self.assertIn("Adversarial Rule BR-99", str(ctx.exception))
        self.assertIn("source_ac_id 'AC-GHOST-999' not found in ACs!", str(ctx.exception))

    def test_probe_many_to_one_rule_ac_traceability(self):
        """Probe multiple business rules referencing a single Acceptance Criterion (valid N:1)."""
        base = valid_strategy_data()
        base["business_rules"] = [
            {
                "rule_id": "BR-101",
                "description": "Rule 101 grounded in AC-TEST-1 with detailed specifications.",
                "source_ac_id": "AC-TEST-1",
            },
            {
                "rule_id": "BR-102",
                "description": "Rule 102 also grounded in AC-TEST-1 with supplementary specs.",
                "source_ac_id": "AC-TEST-1",
            },
        ]
        contract = StrategyCJMContract(**base)
        self.assertEqual(len(contract.business_rules), 2)

    def test_probe_orphan_acceptance_criteria(self):
        """
        Probe whether an Acceptance Criterion without any referencing Business Rules is permitted.
        Traceability invariant requires all business rules to map to ACs (no ungrounded rules).
        """
        base = valid_strategy_data()
        # Add an extra AC that has no rule pointing to it
        base["acceptance_criteria"].append(
            {
                "id": "AC-ORPHAN-9",
                "given": "User navigates to unlinked page",
                "when": "No business rules explicitly reference this AC",
                "then": "The contract should still validate as long as rules are grounded",
            }
        )
        contract = StrategyCJMContract(**base)
        self.assertEqual(len(contract.acceptance_criteria), 3)

    def test_probe_duplicate_ac_ids_and_rule_ids_behavior(self):
        """
        Empirically probe whether duplicate AC IDs or rule IDs are permitted or rejected.
        Current implementation permits duplicates (set-membership check does not enforce uniqueness).
        """
        base = valid_strategy_data()
        # Duplicate AC ID
        base["acceptance_criteria"].append(base["acceptance_criteria"][0])
        contract = StrategyCJMContract(**base)
        self.assertEqual(len(contract.acceptance_criteria), 3)

        # Duplicate Rule ID
        base["business_rules"].append(base["business_rules"][0])
        contract2 = StrategyCJMContract(**base)
        self.assertEqual(len(contract2.business_rules), 3)


class TestEmpiricalExtendedEdgeCases(unittest.TestCase):
    """Empirical probes for subtle edge cases: domain caps, route collisions, and FZ-152 consistency."""

    def test_probe_quality_domain_caps(self):
        """
        Probe whether quality metrics enforce natural mathematical domains:
        - Brier score >= 0.0
        - Percentages <= 100.0%
        Observations show schemas enforce specified thresholds (ge/le) but leave opposite natural bounds uncapped.
        """
        base = valid_quality_data()
        # Negative Brier score is accepted because only le=0.04 is defined
        base["brier_score_calibration"] = -0.5
        c = VVQualityContract(**base)
        self.assertEqual(c.brier_score_calibration, -0.5)

        # Score > 100% is accepted because only ge=85.0 is defined
        base["iso_29148_unambiguity_score"] = 150.0
        c = VVQualityContract(**base)
        self.assertEqual(c.iso_29148_unambiguity_score, 150.0)

    def test_probe_duplicate_endpoints_in_system_analysis(self):
        """
        Empirically probe whether multiple endpoints with identical (method, path) are permitted.
        Currently permitted as List[ApiEndpoint] without collision check.
        """
        base = valid_analysis_data()
        base["endpoints"].append(base["endpoints"][0])
        contract = SystemAnalysisContract(**base)
        self.assertEqual(len(contract.endpoints), 2)

    def test_probe_fz152_personal_data_coherence(self):
        """
        Probe whether processes_personal_data=False with fz152_level="УЗ-1" is accepted.
        Field-level validation accepts any valid literal without cross-field coupling.
        """
        base = valid_legal_data()
        base["personal_data"]["processes_personal_data"] = False
        base["personal_data"]["fz152_level"] = "УЗ-1"
        contract = LegalComplianceContract(**base)
        self.assertFalse(contract.personal_data.processes_personal_data)
        self.assertEqual(contract.personal_data.fz152_level, "УЗ-1")


class TestEmpiricalLegalFz152SecurityTiers(unittest.TestCase):
    """Empirical probes for 152-FZ security levels, Cyrillic literals, and AI Act."""

    def test_probe_fz152_cyrillic_vs_latin_enforcement(self):
        """
        Probe Cyrillic vs Latin character handling for FZ-152 protection levels.
        Schema expects Russian Cyrillic: 'УЗ-1', 'УЗ-2', 'УЗ-3', 'УЗ-4', 'NONE'.
        Latin 'UZ-1' must be rejected.
        """
        base = valid_legal_data()

        # Valid Cyrillic tiers
        cyrillic_tiers = ["УЗ-1", "УЗ-2", "УЗ-3", "УЗ-4", "NONE"]
        for tier in cyrillic_tiers:
            base["personal_data"]["fz152_level"] = tier
            c = LegalComplianceContract(**base)
            self.assertEqual(c.personal_data.fz152_level, tier)

        # Latin lookalikes (Latin 'U', 'Z')
        latin_lookalikes = ["UZ-1", "UZ-2", "UZ-3", "UZ-4", "уз-1", "None"]
        for bad in latin_lookalikes:
            base["personal_data"]["fz152_level"] = bad
            with self.assertRaises(ValidationError, msg=f"Failed to reject Latin/invalid tier: {bad}"):
                LegalComplianceContract(**base)

    def test_probe_eu_ai_act_unacceptable_risk_veto(self):
        """Probe EU AI Act regulatory compliance veto."""
        base = valid_legal_data()

        base["ai_act_risk_category"] = "UNACCEPTABLE"
        with self.assertRaises(ValidationError) as ctx:
            LegalComplianceContract(**base)
        self.assertIn("Compliance Veto", str(ctx.exception))
        self.assertIn("UNACCEPTABLE risk under EU AI Act", str(ctx.exception))

        for allowed in ["MINIMAL", "LIMITED", "HIGH"]:
            base["ai_act_risk_category"] = allowed
            c = LegalComplianceContract(**base)
            self.assertEqual(c.ai_act_risk_category, allowed)


class TestEmpiricalSystemAnalysisAndQualityProbes(unittest.TestCase):
    """Empirical probes for Architecture acyclicity and Quality Gate metrics."""

    def test_probe_cyclic_dependencies_architectural_veto(self):
        """Probe acyclic dependency validator."""
        base = valid_analysis_data()
        base["cyclic_dependencies_detected"] = True
        with self.assertRaises(ValidationError) as ctx:
            SystemAnalysisContract(**base)
        self.assertIn("Architecture Veto", str(ctx.exception))
        self.assertIn("Cyclic dependencies found", str(ctx.exception))

        base["cyclic_dependencies_detected"] = False
        c = SystemAnalysisContract(**base)
        self.assertFalse(c.cyclic_dependencies_detected)

    def test_probe_quality_gate_boundaries(self):
        """Probe VV quality gate boundaries (ISO, RTM, Mutation, Brier, Hoare, SHA-256)."""
        base = valid_quality_data()

        # GOST incomplete
        base["gost_34_602_all_sections_present"] = False
        with self.assertRaises(ValidationError) as ctx:
            VVQualityContract(**base)
        self.assertIn("GOST 34.602 Incomplete", str(ctx.exception))
        base["gost_34_602_all_sections_present"] = True

        # ISO 29148 < 85.0
        base["iso_29148_unambiguity_score"] = 84.999
        with self.assertRaises(ValidationError):
            VVQualityContract(**base)
        base["iso_29148_unambiguity_score"] = 85.0
        self.assertEqual(VVQualityContract(**base).iso_29148_unambiguity_score, 85.0)

        # RTM coverage < 100.0%
        base["rtm_traceability_coverage_pct"] = 99.999
        with self.assertRaises(ValidationError):
            VVQualityContract(**base)
        base["rtm_traceability_coverage_pct"] = 100.0
        self.assertEqual(VVQualityContract(**base).rtm_traceability_coverage_pct, 100.0)

        # Mutation score < 95.0%
        base["mutation_score_pct"] = 94.999
        with self.assertRaises(ValidationError):
            VVQualityContract(**base)
        base["mutation_score_pct"] = 95.0
        self.assertEqual(VVQualityContract(**base).mutation_score_pct, 95.0)

        # Brier score > 0.04
        base["brier_score_calibration"] = 0.040001
        with self.assertRaises(ValidationError):
            VVQualityContract(**base)
        base["brier_score_calibration"] = 0.040000
        self.assertEqual(VVQualityContract(**base).brier_score_calibration, 0.04)

        # Hoare logic invariants < 7
        base["hoare_logic_invariants_verified"] = 6
        with self.assertRaises(ValidationError):
            VVQualityContract(**base)
        base["hoare_logic_invariants_verified"] = 7
        self.assertEqual(VVQualityContract(**base).hoare_logic_invariants_verified, 7)

        # SHA-256 digest format
        base["cryptographic_release_signature"] = "abc123"  # invalid length
        with self.assertRaises(ValidationError):
            VVQualityContract(**base)
        base["cryptographic_release_signature"] = "g" * 64  # non-hex char 'g'
        with self.assertRaises(ValidationError):
            VVQualityContract(**base)
        base["cryptographic_release_signature"] = "a1B2c3D4e5F67890" * 4  # mixed-case valid hex 64
        self.assertEqual(len(VVQualityContract(**base).cryptographic_release_signature), 64)


class TestEmpiricalSubMillisecondStressBenchmark(unittest.TestCase):
    """Extensive empirical benchmark verifying sub-millisecond rejection performance."""

    def test_empirical_rejection_stress_matrix(self):
        """Execute 3,500 rejection evaluations across all 7 schemas and compute percentiles."""
        invalid_scenarios = [
            (FinanceBudgetContract, {**valid_finance_data(), "lifetime_value": 299.99, "customer_acquisition_cost": 100.0}),
            (StrategyCJMContract, {**valid_strategy_data(), "business_rules": [{"rule_id": "BR-1", "description": "Ungrounded rule text here", "source_ac_id": "AC-NONEXISTENT"}]}),
            (HardwareRuntimeContract, {**valid_hardware_data(), "physical_actuator_latency_ms": 1000.1, "hardware_interlocks_required": False}),
            (SecurityPolicyContract, {**valid_security_data(), "stride_matrix": valid_security_data()["stride_matrix"][:4]}),
            (LegalComplianceContract, {**valid_legal_data(), "ai_act_risk_category": "UNACCEPTABLE"}),
            (SystemAnalysisContract, {**valid_analysis_data(), "cyclic_dependencies_detected": True}),
            (VVQualityContract, {**valid_quality_data(), "gost_34_602_all_sections_present": False}),
        ]

        # Warm-up (100 passes)
        for _ in range(100):
            for model_cls, payload in invalid_scenarios:
                try:
                    model_cls(**payload)
                except ValidationError:
                    pass

        # Measurement: 500 rounds * 7 scenarios = 3,500 evaluations
        rounds = 500
        latencies_us: List[float] = []

        for _ in range(rounds):
            for model_cls, payload in invalid_scenarios:
                t0 = time.perf_counter()
                try:
                    model_cls(**payload)
                    self.fail(f"Payload unexpectedly passed: {payload}")
                except ValidationError:
                    t1 = time.perf_counter()
                    latencies_us.append((t1 - t0) * 1_000_000.0)

        latencies_sorted = sorted(latencies_us)
        total_count = len(latencies_sorted)
        avg_us = sum(latencies_sorted) / total_count
        p50_us = latencies_sorted[int(total_count * 0.50)]
        p90_us = latencies_sorted[int(total_count * 0.90)]
        p95_us = latencies_sorted[int(total_count * 0.95)]
        p99_us = latencies_sorted[int(total_count * 0.99)]
        max_us = max(latencies_sorted)

        print("\n--- Empirical Sub-Millisecond Rejection Stress Test Results ---")
        print(f"Total Evaluations: {total_count}")
        print(f"Average: {avg_us:.3f} µs ({avg_us / 1000.0:.5f} ms)")
        print(f"P50:     {p50_us:.3f} µs ({p50_us / 1000.0:.5f} ms)")
        print(f"P90:     {p90_us:.3f} µs ({p90_us / 1000.0:.5f} ms)")
        print(f"P95:     {p95_us:.3f} µs ({p95_us / 1000.0:.5f} ms)")
        print(f"P99:     {p99_us:.3f} µs ({p99_us / 1000.0:.5f} ms)")
        print(f"Max:     {max_us:.3f} µs ({max_us / 1000.0:.5f} ms)")

        # Target: avg < 1000 µs (1.0 ms)
        self.assertLess(avg_us, 1000.0, f"Average rejection latency {avg_us:.2f} µs exceeds 1000 µs limit")
        self.assertLess(p99_us, 5000.0, f"P99 rejection latency {p99_us:.2f} µs exceeds 5000 µs limit")


if __name__ == "__main__":
    unittest.main(verbosity=2)
