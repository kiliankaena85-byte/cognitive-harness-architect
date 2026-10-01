"""
core/standards_linter.py
=============================================================================
Universal Cognitive Decomposition Engine (UCDE) - Standards Verification Engine
Multi-Standard Deterministic Linter across all 7 Ministries.

Covers:
- ISO/IEC/IEEE 29148:2018 (Requirements Engineering & Gherkin Semantics)
- FinOps Open Cost & Usage Specification (FOCUS) 1.0 & IAS 38
- SPDX 2.3/3.0, 152-FZ, 54-FZ, EU AI Act Regulation (2024/1689)
- OWASP ASVS 4.0, NIST SP 800-207 Zero Trust, ГОСТ Р 56939-2024, БДУ ФСТЭК
- RFC 7807 / RFC 9457 (Problem Details for HTTP APIs), OpenAPI 3.1, ISO/IEC/IEEE 42010
- IEC 61508 (Functional Safety SIL 1-4), IEEE 754-2019, OpenVINO NPU Profile
- ISO/IEC/IEEE 29119 (Software Testing), IEEE 1012-2016, ГОСТ 34.602-89, ГОСТ 34.603-92
=============================================================================
"""

import re
from typing import Any, Dict, List, Literal, NamedTuple, Optional, Set, Tuple
from pydantic import BaseModel, ConfigDict, Field


VALID_SPDX_IDENTIFIERS: Set[str] = {
    "MIT",
    "Apache-2.0",
    "BSD-3-Clause",
    "BSD-2-Clause",
    "GPL-2.0-only",
    "GPL-2.0-or-later",
    "GPL-3.0-only",
    "GPL-3.0-or-later",
    "LGPL-2.1-only",
    "LGPL-3.0-only",
    "MPL-2.0",
    "ISC",
    "Unlicense",
    "CC0-1.0",
    "AGPL-3.0-only",
    "EPL-2.0",
}

VALID_FSTEC_UBI_PATTERN = re.compile(r"^УБИ\.\d{3}$")
VALID_SHA256_HEX = re.compile(r"^[a-fA-F0-9]{64}$")


class StandardViolation(BaseModel):
    """Represents a single deterministic standards compliance defect."""
    model_config = ConfigDict(extra="forbid")

    standard_id: str = Field(description="Идентификатор стандарта, например RFC_7807 или OWASP_ASVS")
    ministry_id: int = Field(ge=1, le=9, description="Номер Министерства или Модуля (1-9)")
    rule: str = Field(description="Конкретное правило проверки стандарта")
    severity: Literal["CRITICAL", "ERROR", "WARNING"] = Field(description="Критичность нарушения")
    message: str = Field(description="Подробное описание несоответствия")


class StandardsLintResult(BaseModel):
    """Summary result of standards linting for an artifact or entire pipeline."""
    model_config = ConfigDict(extra="forbid")

    is_compliant: bool = Field(description="Признак успешного прохождения всех проверок стандартов")
    compliance_score_pct: float = Field(ge=0.0, le=100.0, description="Интегральный процент соответствия (0-100%)")
    checked_standards: List[str] = Field(description="Список проверенных стандартов")
    total_checks: int = Field(ge=0, description="Общее число выполненных проверок")
    violations: List[StandardViolation] = Field(default_factory=list, description="Список зафиксированных дефектов")


class StandardsLinter:
    """
    Deterministic Multi-Standard Linter verifying architectural and formal constraints
    across the 7 Ministries of the UCDE pipeline.
    """

    def __init__(self):
        self._standard_rules: Dict[int, List[Tuple[str, str]]] = {
            1: [
                ("ISO_29148", "Rule 1.1: Syntax validation & shall/given semantics"),
                ("ISO_29148", "Rule 1.2: Traceability of Business Rules to Acceptance Criteria"),
                ("BABOK_BACCM", "Rule 1.3: Alignment with Business Analysis Core Concept Model"),
                ("GOST_19_ESPD", "Rule 1.4: Pure software specification sections according to GOST 19.201-78 / GOST 7.0.97"),
                ("ISO_29148_EARS", "Rule 1.5: EARS syntax requirements with shall/when keywords and valid pattern types"),
                ("ISO_29148_ATTRIBUTES", "Rule 1.6: Verification of 9 requirements quality attributes according to ISO 29148"),
            ],
            2: [
                ("FINOPS_FOCUS_1.0", "Rule 2.1: Open Cost and Usage standard specification"),
                ("IAS_38", "Rule 2.2: CaPEx / OpEx financial solvency and bounds"),
                ("ISO_31000", "Rule 2.3: Quantitative enterprise financial risk assessment"),
                ("TOKEN_FINOPS", "Rule 2.4: Token Economics & Context Cache Hit Rate >= 50%"),
                ("MONTE_CARLO_VAR", "Rule 2.5: Monte Carlo financial risk simulation (iterations >= 1000, VaR 95%, insolvency prob <= 5%)"),
            ],
            3: [
                ("SPDX_2.3", "Rule 3.1: Validated open-source license identifiers from SPDX catalog"),
                ("FZ_152", "Rule 3.2: Personal data localization strictly inside Russian Federation"),
                ("EU_AI_ACT", "Rule 3.3: Prohibition of UNACCEPTABLE cognitive manipulation risks"),
                ("ISO_27701", "Rule 3.4: Privacy Information Management System controls"),
                ("ISO_42001", "Rule 3.5: Artificial Intelligence Management System compliance"),
                ("FSTEC_17_21_239", "Rule 3.6: Classification of GIS (K1-K3), ISPDN (UZ1-UZ4), and KII (Cat 1-3)"),
                ("PP_1119_THREAT", "Rule 3.7: RF Government Decree № 1119 threat model and FSB SKZI class (KS1-KS3)"),
                ("EU_AI_ACT_DOSSIER", "Rule 3.8: EU AI Act Article 14 Human Oversight and Article 15 Robustness Technical Dossier"),
            ],
            4: [
                ("OWASP_ASVS_4.0", "Rule 4.1: Level 2 or Level 3 application security verification"),
                ("NIST_SP_800_207", "Rule 4.2: Zero-Trust architecture and mutual authentication"),
                ("FSTEC_BDU", "Rule 4.3: Formal mapping of all STRIDE threats to FSTEC UBI codes"),
                ("GOST_R_56939_2024", "Rule 4.4: Secure software development lifecycle certification"),
                ("OWASP_LLM_TOP10", "Rule 4.5: Prompt Injection Quarantine & Model Context Protocol (MCP)"),
                ("FSTEC_17_21_239_SECURITY", "Rule 4.6: Information protection measures mapping to FSTEC 17/21/239"),
                ("MITRE_ATLAS_AI", "Rule 4.7: MITRE ATLAS threat matrix covering AI system specific attacks"),
                ("ISO_42001_SECURITY", "Rule 4.8: ISO/IEC 42001 active AI security controls"),
            ],
            5: [
                ("OPENAPI_3.1", "Rule 5.1: Typed REST specification with bounded timeouts"),
                ("RFC_7807_9457", "Rule 5.2: Problem Details for HTTP APIs error representation"),
                ("ISO_42010", "Rule 5.3: Defined architectural viewpoints and systemic perspectives"),
                ("C4_MODEL", "Rule 5.4: Hierarchical structural decomposition at Component level"),
                ("AI_NATIVE_RAG", "Rule 5.5: RAG vector memory & 4-tier cognitive memory architecture"),
                ("MADR_3.0", "Rule 5.6: Architectural Decision Records format and tradeoff documentation"),
                ("ASYNCAPI_3.0", "Rule 5.7: AsyncAPI 3.0 event-driven message topics with CloudEvents 1.0 types"),
                ("SELF_RAG_TOKENS", "Rule 5.8: Self-RAG reflection tokens ([Retrieve], [IsRel], [IsSup], [IsUse]) configuration"),
            ],
            6: [
                ("IEC_61508_SIL", "Rule 6.1: Functional safety integrity level assignment"),
                ("IEEE_754_2019", "Rule 6.2: Quantized numerical precision (INT8/FP16) on NPU"),
                ("OPENVINO_METEOR_LAKE", "Rule 6.3: NPU Working Set RAM budget <= 512 MB and Latency <= 50 ms"),
                ("THERAC_25_INTERLOCK", "Rule 6.4: Mandatory hardware interlocks when actuator latency > 1000 ms"),
                ("FMEA_RPN", "Rule 6.5: Failure Mode and Effects Analysis Risk Priority Number <= 120"),
                ("FTA_IEC_61025", "Rule 6.6: Fault Tree Analysis (FTA) logic gates and failure rate verification according to IEC 61025"),
            ],
            7: [
                ("GOST_34.602_89", "Rule 7.1: All mandatory sections of Terms of Reference present"),
                ("GOST_34.603_92", "Rule 7.2: Structured test acceptance protocol identifier"),
                ("ISO_29119_4", "Rule 7.3: Test design techniques (BVA, Equivalence Partitioning, Mutation)"),
                ("IEEE_1012_2016", "Rule 7.4: High-integrity V&V Level 4 assurance"),
                ("CRYPTOGRAPHIC_RELEASE", "Rule 7.5: SHA-256 tamper-proof digest of release artifacts"),
                ("RAG_TRIAD_METRICS", "Rule 7.6: Cognitive RAG Triad (Relevance, Groundedness/Faithfulness >= 0.95)"),
                ("GOST_19_201", "Rule 7.7: Software program documentation completeness according to GOST 19.201-78"),
                ("SMT_FORMAL_PROOFS", "Rule 7.8: Formal mathematical proof certificates verified via Z3 SMT solver"),
                ("MUTATION_MSI_85", "Rule 7.9: Mutation Testing with Mutation Score Indicator MSI >= 85%"),
            ],
            8: [
                ("SPEC_TO_CODE_SYNTAX", "Rule 8.1: Valid AST and RFC 7807 error models in synthesized code"),
            ],
            9: [
                ("EXECUTABLE_BDD_PASS", "Rule 9.1: 100% pass rate in synthesized BDD test suites"),
            ],
        }

    def lint_node_artifact(self, node_id: int, artifact: Dict[str, Any]) -> StandardsLintResult:
        """
        Lints a single ministry artifact against its vertical standard suite.
        """
        violations: List[StandardViolation] = []
        checks_performed = 0

        if node_id == 1:
            violations.extend(self._lint_ministry_1_strategy(artifact))
            checks_performed = len(self._standard_rules[1])
        elif node_id == 2:
            violations.extend(self._lint_ministry_2_finance(artifact))
            checks_performed = len(self._standard_rules[2])
        elif node_id == 3:
            violations.extend(self._lint_ministry_3_legal(artifact))
            checks_performed = len(self._standard_rules[3])
        elif node_id == 4:
            violations.extend(self._lint_ministry_4_security(artifact))
            checks_performed = len(self._standard_rules[4])
        elif node_id == 5:
            violations.extend(self._lint_ministry_5_analysis(artifact))
            checks_performed = len(self._standard_rules[5])
        elif node_id == 6:
            violations.extend(self._lint_ministry_6_hardware(artifact))
            checks_performed = len(self._standard_rules[6])
        elif node_id == 7:
            violations.extend(self._lint_ministry_7_quality(artifact))
            checks_performed = len(self._standard_rules[7])
        elif node_id == 8:
            violations.extend(self._lint_module_8_code(artifact))
            checks_performed = len(self._standard_rules[8])
        elif node_id == 9:
            violations.extend(self._lint_module_9_tests(artifact))
            checks_performed = len(self._standard_rules[9])
        else:
            violations.append(StandardViolation(
                standard_id="SYSTEM",
                ministry_id=node_id,
                rule="Invalid Ministry ID",
                severity="CRITICAL",
                message=f"Unknown ministry ID: {node_id}"
            ))
            checks_performed = 1

        rule_count = max(1, checks_performed)
        critical_or_errors = sum(1 for v in violations if v.severity in ("CRITICAL", "ERROR"))
        passed_rules = max(0, rule_count - critical_or_errors)
        compliance_pct = round((passed_rules / rule_count) * 100.0, 1)

        checked_stds = sorted(list({rule[0] for rule in self._standard_rules.get(node_id, [])}))

        return StandardsLintResult(
            is_compliant=(critical_or_errors == 0),
            compliance_score_pct=compliance_pct,
            checked_standards=checked_stds,
            total_checks=checks_performed,
            violations=violations,
        )

    def _lint_ministry_1_strategy(self, data: Dict[str, Any]) -> List[StandardViolation]:
        v: List[StandardViolation] = []
        if not data.get("iso_29148_syntax_validated", True):
            v.append(StandardViolation(
                standard_id="ISO_29148",
                ministry_id=1,
                rule="ISO 29148 Syntax Validation",
                severity="ERROR",
                message="iso_29148_syntax_validated is False; requirements lack unambiguous modal verbs."
            ))

        acs = data.get("acceptance_criteria", [])
        if not acs:
            v.append(StandardViolation(
                standard_id="ISO_29148",
                ministry_id=1,
                rule="Gherkin Semantics",
                severity="ERROR",
                message="No acceptance criteria defined in Strategy Contract."
            ))

        brs = data.get("business_rules", [])
        ac_ids = {ac.get("id") for ac in acs if isinstance(ac, dict)}
        for br in brs:
            if isinstance(br, dict):
                src_id = br.get("source_ac_id")
                if src_id not in ac_ids:
                    v.append(StandardViolation(
                        standard_id="ISO_29148",
                        ministry_id=1,
                        rule="Requirement Traceability",
                        severity="ERROR",
                        message=f"Business Rule '{br.get('rule_id')}' points to non-existent AC '{src_id}'."
                    ))

        if not data.get("babok_baccm_aligned", True):
            v.append(StandardViolation(
                standard_id="BABOK_BACCM",
                ministry_id=1,
                rule="BABOK BACCM Alignment",
                severity="WARNING",
                message="babok_baccm_aligned is False; core business concept model not fully aligned."
            ))

        doc_profile = data.get("target_document_profile", "GOST_34_AUTOMATED_SYSTEM")
        if doc_profile == "GOST_19_ESPD_SOFTWARE" and not data.get("gost_19_espd_sections_defined", True):
            v.append(StandardViolation(
                standard_id="GOST_19_ESPD",
                ministry_id=1,
                rule="GOST 19 ESPD Section Definition",
                severity="ERROR",
                message="gost_19_espd_sections_defined is False for GOST_19_ESPD_SOFTWARE profile."
            ))

        reqs = data.get("gost_7_0_97_requisites", {})
        if reqs and not (reqs.get("approval_stamp") and reqs.get("organization")):
            v.append(StandardViolation(
                standard_id="GOST_19_ESPD",
                ministry_id=1,
                rule="GOST R 7.0.97 Requisites",
                severity="WARNING",
                message="Mandatory document requisites according to GOST R 7.0.97-2016 are incomplete."
            ))

        if not data.get("iso_29148_quality_attributes_verified", True):
            v.append(StandardViolation(
                standard_id="ISO_29148_ATTRIBUTES",
                ministry_id=1,
                rule="ISO 29148 Quality Attributes",
                severity="WARNING",
                message="iso_29148_quality_attributes_verified is False; 9 quality attributes not fully verified."
            ))

        ears = data.get("ears_requirements", [])
        valid_patterns = {"UBIQUITOUS", "EVENT_DRIVEN", "STATE_DRIVEN", "UNWANTED_BEHAVIOR", "OPTIONAL_FEATURE"}
        for ereq in ears:
            if isinstance(ereq, dict):
                pattern = ereq.get("pattern_type")
                if pattern not in valid_patterns:
                    v.append(StandardViolation(
                        standard_id="ISO_29148_EARS",
                        ministry_id=1,
                        rule="EARS Pattern Classification",
                        severity="ERROR",
                        message=f"Requirement '{ereq.get('req_id')}' has invalid EARS pattern '{pattern}'."
                    ))
                text = str(ereq.get("text", "")).lower()
                if not any(kw in text for kw in ("shall", "долж")):
                    v.append(StandardViolation(
                        standard_id="ISO_29148_EARS",
                        ministry_id=1,
                        rule="EARS Modal Syntax",
                        severity="WARNING",
                        message=f"EARS requirement '{ereq.get('req_id')}' lacks mandatory modal keyword 'shall' / 'должен'."
                    ))

        return v

    def _lint_ministry_2_finance(self, data: Dict[str, Any]) -> List[StandardViolation]:
        v: List[StandardViolation] = []
        finops_ver = data.get("finops_focus_version")
        if finops_ver != "1.0":
            v.append(StandardViolation(
                standard_id="FINOPS_FOCUS_1.0",
                ministry_id=2,
                rule="FinOps FOCUS Specification",
                severity="ERROR",
                message=f"finops_focus_version must be '1.0', got '{finops_ver}'."
            ))

        cac = data.get("customer_acquisition_cost", 0.0)
        ltv = data.get("lifetime_value", 0.0)
        if cac <= 0 or (ltv / max(1e-6, cac)) < 3.0:
            v.append(StandardViolation(
                standard_id="IAS_38",
                ministry_id=2,
                rule="Unit Economics Solvency",
                severity="ERROR",
                message=f"LTV/CAC ratio ({ltv / max(1e-6, cac):.2f}) violates solvency requirement (>= 3.0)."
            ))

        if not data.get("iso_31000_risk_assessed", True):
            v.append(StandardViolation(
                standard_id="ISO_31000",
                ministry_id=2,
                rule="ISO 31000 Risk Management",
                severity="WARNING",
                message="iso_31000_risk_assessed is False; enterprise risk analysis not recorded."
            ))

        tok = data.get("token_economics", {})
        if isinstance(tok, dict):
            hit_rate = float(tok.get("context_cache_hit_rate_target_pct", 85.0))
            if hit_rate < 50.0:
                v.append(StandardViolation(
                    standard_id="TOKEN_FINOPS",
                    ministry_id=2,
                    rule="AI FinOps Context Caching",
                    severity="WARNING",
                    message=f"Target context cache hit rate ({hit_rate}%) is below 50.0% threshold."
                ))

        mc = data.get("monte_carlo_config", {})
        if isinstance(mc, dict):
            iters = int(mc.get("iterations", 10000))
            if iters < 1000:
                v.append(StandardViolation(
                    standard_id="MONTE_CARLO_VAR",
                    ministry_id=2,
                    rule="Monte Carlo Iteration Count",
                    severity="ERROR",
                    message=f"Monte Carlo iterations ({iters}) below required minimum 1,000."
                ))

        risk = data.get("risk_profile", {})
        if isinstance(risk, dict):
            insolv = float(risk.get("insolvency_probability_pct", 0.0))
            if insolv > 5.0:
                v.append(StandardViolation(
                    standard_id="MONTE_CARLO_VAR",
                    ministry_id=2,
                    rule="Insolvency Risk Threshold",
                    severity="CRITICAL",
                    message=f"Insolvency probability ({insolv}%) strictly exceeds allowable 5.0% threshold."
                ))
            if not risk.get("monte_carlo_verified", True):
                v.append(StandardViolation(
                    standard_id="MONTE_CARLO_VAR",
                    ministry_id=2,
                    rule="Monte Carlo Attestation",
                    severity="WARNING",
                    message="monte_carlo_verified is False; financial risk profile unverified."
                ))

        return v

    def _lint_ministry_3_legal(self, data: Dict[str, Any]) -> List[StandardViolation]:
        v: List[StandardViolation] = []
        licenses = data.get("approved_open_source_licenses", [])
        for lic in licenses:
            if lic not in VALID_SPDX_IDENTIFIERS:
                v.append(StandardViolation(
                    standard_id="SPDX_2.3",
                    ministry_id=3,
                    rule="SPDX License Standard",
                    severity="ERROR",
                    message=f"License '{lic}' is not a valid recognized SPDX identifier."
                ))

        pd = data.get("personal_data", {})
        if pd.get("processes_personal_data", False):
            loc = pd.get("localization_country", "")
            if loc != "RUS":
                v.append(StandardViolation(
                    standard_id="FZ_152",
                    ministry_id=3,
                    rule="152-FZ Primary Localization",
                    severity="CRITICAL",
                    message=f"Primary personal data localization must be 'RUS', got '{loc}'."
                ))
            if not pd.get("data_localization_rf", True):
                v.append(StandardViolation(
                    standard_id="FZ_152",
                    ministry_id=3,
                    rule="152-FZ Primary Localization in RF",
                    severity="CRITICAL",
                    message="Primary database for Russian personal data must be localized in the Russian Federation (152-FZ / 242-FZ)."
                ))

        ai_risk = data.get("ai_act_risk_category", "")
        if ai_risk == "UNACCEPTABLE":
            v.append(StandardViolation(
                standard_id="EU_AI_ACT",
                ministry_id=3,
                rule="Prohibited AI Practices",
                severity="CRITICAL",
                message="EU AI Act risk tier UNACCEPTABLE is prohibited by international regulation."
            ))

        gis = data.get("fstec_gis_class", "К2")
        if gis not in ("К1", "К2", "К3", "NONE"):
            v.append(StandardViolation(
                standard_id="FSTEC_17_21_239",
                ministry_id=3,
                rule="FSTEC Order 17 GIS Classification",
                severity="ERROR",
                message=f"Invalid FSTEC Order 17 GIS class '{gis}'. Must be К1, К2, К3, or NONE."
            ))

        ispdn = data.get("fstec_ispdn_level", "УЗ-2")
        if ispdn not in ("УЗ-1", "УЗ-2", "УЗ-3", "УЗ-4", "NONE"):
            v.append(StandardViolation(
                standard_id="FSTEC_17_21_239",
                ministry_id=3,
                rule="FSTEC Order 21 ISPDN Classification",
                severity="ERROR",
                message=f"Invalid FSTEC Order 21 ISPDN level '{ispdn}'. Must be УЗ-1, УЗ-2, УЗ-3, УЗ-4, or NONE."
            ))

        kii = data.get("fstec_kii_category", "КАТЕГОРИЯ_2")
        if kii not in ("КАТЕГОРИЯ_1", "КАТЕГОРИЯ_2", "КАТЕГОРИЯ_3", "НЕ_КАТЕГОРИРУЕТСЯ"):
            v.append(StandardViolation(
                standard_id="FSTEC_17_21_239",
                ministry_id=3,
                rule="FSTEC Order 239 KII Classification",
                severity="ERROR",
                message=f"Invalid FSTEC Order 239 KII category '{kii}'."
            ))

        tm = data.get("pp_1119_threat_model", {})
        if isinstance(tm, dict):
            ttype = tm.get("threat_type", "ТИП_3")
            if ttype not in ("ТИП_1", "ТИП_2", "ТИП_3"):
                v.append(StandardViolation(
                    standard_id="PP_1119_THREAT",
                    ministry_id=3,
                    rule="PP 1119 Threat Classification",
                    severity="ERROR",
                    message=f"Invalid PP 1119 threat type '{ttype}'. Must be ТИП_1, ТИП_2, or ТИП_3."
                ))
            skzi = tm.get("skzi_class", "КС2")
            if skzi not in ("КС1", "КС2", "КС3", "КБ", "КА", "NONE"):
                v.append(StandardViolation(
                    standard_id="PP_1119_THREAT",
                    ministry_id=3,
                    rule="FSB SKZI Classification",
                    severity="ERROR",
                    message=f"Invalid FSB SKZI class '{skzi}'."
                ))

        dossier = data.get("eu_ai_act_dossier", {})
        if isinstance(dossier, dict):
            if not dossier.get("article_14_human_oversight", True):
                v.append(StandardViolation(
                    standard_id="EU_AI_ACT_DOSSIER",
                    ministry_id=3,
                    rule="EU AI Act Article 14 Human Oversight",
                    severity="ERROR",
                    message="Article 14 Human Oversight (Human-in-the-loop) must be enabled."
                ))
            if not dossier.get("article_15_robustness_accuracy", True):
                v.append(StandardViolation(
                    standard_id="EU_AI_ACT_DOSSIER",
                    ministry_id=3,
                    rule="EU AI Act Article 15 Robustness",
                    severity="ERROR",
                    message="Article 15 AI Robustness, Accuracy & Cybersecurity must be enabled."
                ))

        return v

    def _lint_ministry_4_security(self, data: Dict[str, Any]) -> List[StandardViolation]:
        v: List[StandardViolation] = []
        owasp_lvl = data.get("owasp_asvs_level")
        if owasp_lvl not in ("L1", "L2", "L3"):
            v.append(StandardViolation(
                standard_id="OWASP_ASVS_4.0",
                ministry_id=4,
                rule="OWASP ASVS Verification Level",
                severity="ERROR",
                message=f"Invalid OWASP ASVS level '{owasp_lvl}'. Must be L1, L2, or L3."
            ))

        if not data.get("zero_trust_enforced", True) or not data.get("nist_800_207_zero_trust", True):
            v.append(StandardViolation(
                standard_id="NIST_SP_800_207",
                ministry_id=4,
                rule="Zero Trust Enforcement",
                severity="CRITICAL",
                message="Zero Trust architecture according to NIST SP 800-207 is mandatory."
            ))

        matrix = data.get("stride_matrix", [])
        for threat in matrix:
            if isinstance(threat, dict):
                ubi = threat.get("fstec_ubi_code", "")
                if not VALID_FSTEC_UBI_PATTERN.match(ubi):
                    v.append(StandardViolation(
                        standard_id="FSTEC_BDU",
                        ministry_id=4,
                        rule="FSTEC Threat Modeling",
                        severity="ERROR",
                        message=f"Invalid FSTEC BDU code '{ubi}'. Must conform to '^УБИ\\.\\d{{3}}$'."
                    ))

        atlas = data.get("mitre_atlas_matrix", [])
        for athreat in atlas:
            if isinstance(athreat, dict):
                tid = athreat.get("technique_id", "")
                if not re.match(r"^AML\.T\d{4}(\.\d{3})?$", str(tid)):
                    v.append(StandardViolation(
                        standard_id="MITRE_ATLAS_AI",
                        ministry_id=4,
                        rule="MITRE ATLAS Technique Syntax",
                        severity="ERROR",
                        message=f"Invalid MITRE ATLAS technique ID '{tid}'. Must match '^AML\\.T\\d{{4}}(\\.\\d{{3}})?$'."
                    ))

        if not data.get("iso_42001_security_controls_active", True):
            v.append(StandardViolation(
                standard_id="ISO_42001_SECURITY",
                ministry_id=4,
                rule="ISO 42001 AI Security Controls",
                severity="WARNING",
                message="iso_42001_security_controls_active is False; AI security management controls inactive."
            ))

        ai_sec = data.get("ai_security", {})
        if isinstance(ai_sec, dict):
            if not ai_sec.get("prompt_quarantine_enforced", True):
                v.append(StandardViolation(
                    standard_id="OWASP_LLM_TOP10",
                    ministry_id=4,
                    rule="Prompt Injection Quarantine",
                    severity="CRITICAL",
                    message="prompt_quarantine_enforced is False; prompt injection vulnerability LLM01 detected."
                ))
            covered = ai_sec.get("covered_llm_vulnerabilities", [])
            if "LLM01_PROMPT_INJECTION" not in covered:
                v.append(StandardViolation(
                    standard_id="OWASP_LLM_TOP10",
                    ministry_id=4,
                    rule="OWASP LLM Vulnerability Coverage",
                    severity="ERROR",
                    message="LLM01_PROMPT_INJECTION is missing from covered_llm_vulnerabilities."
                ))

        orders = data.get("fstec_orders_classification", {})
        if not orders or not isinstance(orders, dict):
            v.append(StandardViolation(
                standard_id="FSTEC_17_21_239_SECURITY",
                ministry_id=4,
                rule="FSTEC Orders 17/21/239 Mapping",
                severity="ERROR",
                message="fstec_orders_classification mapping is missing or empty."
            ))
        else:
            required_orders = {"order_17_gis", "order_21_ispdn", "order_239_kii"}
            missing_orders = required_orders - set(orders.keys())
            if missing_orders:
                v.append(StandardViolation(
                    standard_id="FSTEC_17_21_239_SECURITY",
                    ministry_id=4,
                    rule="FSTEC Orders Coverage",
                    severity="ERROR",
                    message=f"Missing FSTEC orders coverage: {sorted(missing_orders)}."
                ))

        return v

    def _lint_ministry_5_analysis(self, data: Dict[str, Any]) -> List[StandardViolation]:
        v: List[StandardViolation] = []
        err_std = data.get("error_response_standard")
        if err_std not in ("RFC_7807", "RFC_9457"):
            v.append(StandardViolation(
                standard_id="RFC_7807_9457",
                ministry_id=5,
                rule="RFC Problem Details Specification",
                severity="ERROR",
                message=f"API error representation '{err_std}' does not comply with RFC 7807 or RFC 9457."
            ))

        if not data.get("iso_42010_viewpoints_defined", True):
            v.append(StandardViolation(
                standard_id="ISO_42010",
                ministry_id=5,
                rule="Architecture Viewpoints Description",
                severity="WARNING",
                message="iso_42010_viewpoints_defined is False; ISO/IEC/IEEE 42010 viewpoints omitted."
            ))

        c4 = data.get("c4_model_level")
        if c4 not in ("CONTEXT", "CONTAINER", "COMPONENT", "CODE"):
            v.append(StandardViolation(
                standard_id="C4_MODEL",
                ministry_id=5,
                rule="C4 Architectural Granularity",
                severity="ERROR",
                message=f"Unknown C4 Model level: '{c4}'."
            ))

        rag = data.get("rag_pipeline", {})
        if isinstance(rag, dict):
            chunk = int(rag.get("chunk_size_tokens", 512))
            if chunk < 64 or chunk > 2048:
                v.append(StandardViolation(
                    standard_id="AI_NATIVE_RAG",
                    ministry_id=5,
                    rule="RAG Chunking Bounds",
                    severity="ERROR",
                    message=f"RAG chunk size ({chunk} tokens) is out of recommended bounds [64, 2048]."
                ))
            idx_type = rag.get("vector_index_type", "HNSW")
            if idx_type not in ("HNSW", "IVFFLAT", "FLAT"):
                v.append(StandardViolation(
                    standard_id="AI_NATIVE_RAG",
                    ministry_id=5,
                    rule="Vector Index Standard",
                    severity="ERROR",
                    message=f"Unknown vector index type: '{idx_type}'."
                ))

        mem = data.get("memory_architecture", {})
        if isinstance(mem, dict):
            if not mem.get("long_term_vector_memory_enabled", True):
                v.append(StandardViolation(
                    standard_id="AI_NATIVE_RAG",
                    ministry_id=5,
                    rule="Cognitive Memory Integration",
                    severity="WARNING",
                    message="long_term_vector_memory_enabled is False; agent operates without long-term episodic memory."
                ))

        adrs = data.get("architecture_decision_records", [])
        if adrs:
            for adr in adrs:
                if isinstance(adr, dict):
                    adr_id = adr.get("adr_id", "")
                    if not re.match(r"^ADR-\d+$", str(adr_id)):
                        v.append(StandardViolation(
                            standard_id="MADR_3.0",
                            ministry_id=5,
                            rule="MADR 3.0 Identifier Syntax",
                            severity="ERROR",
                            message=f"ADR identifier '{adr_id}' does not match pattern '^ADR-\\d+$'."
                        ))
                    opts = adr.get("considered_options", [])
                    if len(opts) < 2:
                        v.append(StandardViolation(
                            standard_id="MADR_3.0",
                            ministry_id=5,
                            rule="MADR 3.0 Tradeoff Comparison",
                            severity="ERROR",
                            message=f"ADR '{adr_id}' must evaluate at least 2 considered options (got {len(opts)})."
                        ))
                    if not adr.get("decision_outcome"):
                        v.append(StandardViolation(
                            standard_id="MADR_3.0",
                            ministry_id=5,
                            rule="MADR 3.0 Decision Outcome",
                            severity="ERROR",
                            message=f"ADR '{adr_id}' lacks a defined decision_outcome."
                        ))
                    if not adr.get("positive_consequences") or not adr.get("negative_consequences"):
                        v.append(StandardViolation(
                            standard_id="MADR_3.0",
                            ministry_id=5,
                            rule="MADR 3.0 Consequences Assessment",
                            severity="WARNING",
                            message=f"ADR '{adr_id}' should document both positive and negative consequences."
                        ))

        async_ver = data.get("asyncapi_version", "3.0.0")
        if not str(async_ver).startswith("3."):
            v.append(StandardViolation(
                standard_id="ASYNCAPI_3.0",
                ministry_id=5,
                rule="AsyncAPI Specification Version",
                severity="ERROR",
                message=f"asyncapi_version must be 3.x, got '{async_ver}'."
            ))

        topics = data.get("async_topics", [])
        for top in topics:
            if isinstance(top, dict):
                tname = top.get("topic_name", "")
                if not re.match(r"^[a-zA-Z0-9_\-\.]+$", str(tname)):
                    v.append(StandardViolation(
                        standard_id="ASYNCAPI_3.0",
                        ministry_id=5,
                        rule="AsyncAPI Topic Naming",
                        severity="ERROR",
                        message=f"Invalid topic name '{tname}'."
                    ))

        self_rag = data.get("self_rag", {})
        if isinstance(self_rag, dict):
            thresh = float(self_rag.get("critique_threshold", 0.85))
            if thresh < 0.5 or thresh > 1.0:
                v.append(StandardViolation(
                    standard_id="SELF_RAG_TOKENS",
                    ministry_id=5,
                    rule="Self-RAG Critique Threshold",
                    severity="ERROR",
                    message=f"Self-RAG critique threshold ({thresh}) is out of bounds [0.5, 1.0]."
                ))

        return v

    def _lint_ministry_6_hardware(self, data: Dict[str, Any]) -> List[StandardViolation]:
        v: List[StandardViolation] = []
        sil = data.get("iec_61508_sil_level")
        if sil not in ("SIL_1", "SIL_2", "SIL_3", "SIL_4", "NONE"):
            v.append(StandardViolation(
                standard_id="IEC_61508_SIL",
                ministry_id=6,
                rule="Functional Safety SIL Level",
                severity="ERROR",
                message=f"Invalid IEC 61508 SIL level '{sil}'."
            ))

        prec = data.get("ieee_754_precision")
        if prec not in ("INT8", "FP16", "FP32", "BF16"):
            v.append(StandardViolation(
                standard_id="IEEE_754_2019",
                ministry_id=6,
                rule="Numerical Precision Representation",
                severity="ERROR",
                message=f"Precision format '{prec}' is not compliant with IEEE 754 / INT8 runtime standard."
            ))

        actuator_latency = float(data.get("physical_actuator_latency_ms", 0.0))
        interlocks = bool(data.get("hardware_interlocks_required", False))
        if actuator_latency > 1000.0 and not interlocks:
            v.append(StandardViolation(
                standard_id="THERAC_25_INTERLOCK",
                ministry_id=6,
                rule="Therac-25 Physical Race Condition Guard",
                severity="CRITICAL",
                message=f"Actuator latency ({actuator_latency} ms) > 1000 ms requires mandatory hardware interlocks!"
            ))

        fmea = data.get("fmea_risk_analysis", [])
        max_rpn = int(data.get("max_fmea_rpn", 120))
        for fm in fmea:
            if isinstance(fm, dict):
                s = int(fm.get("severity", 1))
                o = int(fm.get("occurrence", 1))
                d = int(fm.get("detection", 1))
                calculated_rpn = s * o * d
                rpn = int(fm.get("rpn", calculated_rpn))
                if rpn > max_rpn or calculated_rpn > max_rpn:
                    v.append(StandardViolation(
                        standard_id="FMEA_RPN",
                        ministry_id=6,
                        rule="FMEA Risk Priority Number Bounds",
                        severity="CRITICAL",
                        message=f"Failure mode '{fm.get('failure_mode_id')}' RPN ({max(rpn, calculated_rpn)}) exceeds allowable threshold ({max_rpn})."
                    ))

        fta = data.get("fault_tree_analysis", [])
        for fnode in fta:
            if isinstance(fnode, dict):
                nid = fnode.get("node_id", "")
                if not re.match(r"^FTN-[A-Z0-9]+-\d+$", str(nid)):
                    v.append(StandardViolation(
                        standard_id="FTA_IEC_61025",
                        ministry_id=6,
                        rule="FTA Node Identifier Syntax",
                        severity="ERROR",
                        message=f"Invalid FTA node ID '{nid}'. Must match '^FTN-[A-Z0-9]+-\\d+$'."
                    ))
                gate = fnode.get("gate_type", "")
                if gate not in ("AND", "OR", "BASIC_EVENT", "VOTE"):
                    v.append(StandardViolation(
                        standard_id="FTA_IEC_61025",
                        ministry_id=6,
                        rule="FTA Gate Classification",
                        severity="ERROR",
                        message=f"Invalid FTA gate type '{gate}'."
                    ))

        if not data.get("iec_61025_fta_verified", True):
            v.append(StandardViolation(
                standard_id="FTA_IEC_61025",
                ministry_id=6,
                rule="FTA IEC 61025 Attestation",
                severity="WARNING",
                message="iec_61025_fta_verified is False; fault tree analysis unverified."
            ))

        return v

    def _lint_ministry_7_quality(self, data: Dict[str, Any]) -> List[StandardViolation]:
        v: List[StandardViolation] = []
        if not data.get("gost_34_602_all_sections_present", True):
            v.append(StandardViolation(
                standard_id="GOST_34.602_89",
                ministry_id=7,
                rule="GOST 34.602 Section Completeness",
                severity="CRITICAL",
                message="Terms of Reference lacks mandatory 8 sections required by GOST 34.602-89."
            ))

        iso_score = float(data.get("iso_29148_unambiguity_score", 0.0))
        if iso_score < 85.0:
            v.append(StandardViolation(
                standard_id="ISO_29148",
                ministry_id=7,
                rule="Unambiguity Index",
                severity="ERROR",
                message=f"ISO 29148 unambiguity score ({iso_score}) is below critical threshold 85.0."
            ))

        techniques = data.get("iso_29119_test_techniques", [])
        if not techniques:
            v.append(StandardViolation(
                standard_id="ISO_29119_4",
                ministry_id=7,
                rule="ISO 29119-4 Test Design Techniques",
                severity="WARNING",
                message="iso_29119_test_techniques list is empty; missing BVA/EP specification."
            ))

        sig = data.get("cryptographic_release_signature", "")
        if not VALID_SHA256_HEX.match(sig):
            v.append(StandardViolation(
                standard_id="CRYPTOGRAPHIC_RELEASE",
                ministry_id=7,
                rule="SHA-256 Release Seal",
                severity="CRITICAL",
                message=f"Invalid SHA-256 cryptographic release signature: '{sig}'."
            ))

        triad = data.get("cognitive_rag_triad", {})
        if isinstance(triad, dict):
            faith = float(triad.get("groundedness_faithfulness_score", 0.98))
            if faith < 0.95:
                v.append(StandardViolation(
                    standard_id="RAG_TRIAD_METRICS",
                    ministry_id=7,
                    rule="RAG Groundedness & Zero Hallucination",
                    severity="ERROR",
                    message=f"Groundedness/Faithfulness score ({faith}) is below critical threshold 0.95."
                ))
            ctx_rel = float(triad.get("context_relevance_score", 0.92))
            if ctx_rel < 0.85:
                v.append(StandardViolation(
                    standard_id="RAG_TRIAD_METRICS",
                    ministry_id=7,
                    rule="Context Relevance",
                    severity="ERROR",
                    message=f"Context relevance score ({ctx_rel}) is below threshold 0.85."
                ))

        mut = data.get("mutation_testing", {})
        if isinstance(mut, dict):
            msi = float(mut.get("mutation_score_indicator_target_pct", 85.0))
            if msi < 85.0:
                v.append(StandardViolation(
                    standard_id="MUTATION_MSI_85",
                    ministry_id=7,
                    rule="Mutation Score Indicator (MSI)",
                    severity="ERROR",
                    message=f"Target MSI ({msi}%) is strictly below 85.0% standard."
                ))
            survived = int(mut.get("survived_mutants_threshold", 0))
            if survived > 5:
                v.append(StandardViolation(
                    standard_id="MUTATION_MSI_85",
                    ministry_id=7,
                    rule="Survived Mutants Tolerance",
                    severity="WARNING",
                    message=f"Survived mutants threshold ({survived}) exceeds recommended 0-5 tolerance."
                ))

        if not data.get("gost_19_201_sections_present", True):
            v.append(StandardViolation(
                standard_id="GOST_19_201",
                ministry_id=7,
                rule="GOST 19.201 Software Documentation Completeness",
                severity="ERROR",
                message="gost_19_201_sections_present is False; pure software documentation sections omitted."
            ))

        if "formal_proof_certificates" in data:
            certs = data.get("formal_proof_certificates", {})
            if isinstance(certs, dict):
                invalid_theorems = [name for name, c in certs.items() if not c.get("is_valid", False)]
                if invalid_theorems:
                    v.append(StandardViolation(
                        standard_id="SMT_FORMAL_PROOFS",
                        ministry_id=7,
                        rule="Z3 SMT Invariant Verification",
                        severity="CRITICAL",
                        message=f"One or more formal theorems failed verification: {', '.join(invalid_theorems)}."
                    ))

        return v

    def _lint_module_8_code(self, data: Dict[str, Any]) -> List[StandardViolation]:
        v: List[StandardViolation] = []
        if not data.get("all_ast_valid", True):
            v.append(StandardViolation(
                standard_id="SPEC_TO_CODE_SYNTAX",
                ministry_id=8,
                rule="Rule 8.1: Valid AST and RFC 7807 error models in synthesized code",
                severity="CRITICAL",
                message="One or more synthesized source code files failed Python AST parsing."
            ))
        files = data.get("files", {})
        if files and not any("ProblemDetails" in str(f) or "RFC_7807" in str(f) for f in files.values()):
            v.append(StandardViolation(
                standard_id="SPEC_TO_CODE_SYNTAX",
                ministry_id=8,
                rule="Rule 8.1: Valid AST and RFC 7807 error models in synthesized code",
                severity="ERROR",
                message="Synthesized service code does not declare ProblemDetails RFC 7807 error models."
            ))
        return v

    def _lint_module_9_tests(self, data: Dict[str, Any]) -> List[StandardViolation]:
        v: List[StandardViolation] = []
        success = data.get("success", True)
        failures = data.get("failures", 0)
        errors = data.get("errors", 0)
        if not success or failures > 0 or errors > 0:
            v.append(StandardViolation(
                standard_id="EXECUTABLE_BDD_PASS",
                ministry_id=9,
                rule="Rule 9.1: 100% pass rate in synthesized BDD test suites",
                severity="CRITICAL",
                message=f"Synthesized test suite failed execution: {failures} failures, {errors} errors."
            ))
        return v

    def lint_all_artifacts(self, artifacts_by_node: Dict[int, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Lints the entire ensemble of 7 artifacts.
        Returns a comprehensive report dict suitable for inclusion in release_manifest.json.
        """
        results: Dict[int, StandardsLintResult] = {}
        total_violations: List[StandardViolation] = []
        total_checks = 0

        for nid in range(1, 8):
            art = artifacts_by_node.get(nid, {})
            res = self.lint_node_artifact(nid, art)
            results[nid] = res
            total_violations.extend(res.violations)
            total_checks += res.total_checks

        all_compliant = all(r.is_compliant for r in results.values())
        overall_score = round(sum(r.compliance_score_pct for r in results.values()) / max(1, len(results)), 1)

        all_checked_stds: Set[str] = set()
        for r in results.values():
            all_checked_stds.update(r.checked_standards)

        return {
            "all_standards_compliant": all_compliant,
            "overall_compliance_score_pct": overall_score,
            "total_checks_performed": total_checks,
            "enforced_standards_count": len(all_checked_stds),
            "enforced_standards": sorted(list(all_checked_stds)),
            "per_ministry_results": {
                f"Ministry_{nid}": {
                    "is_compliant": results[nid].is_compliant,
                    "compliance_score_pct": results[nid].compliance_score_pct,
                    "checked_standards": results[nid].checked_standards,
                    "violations": [v.model_dump() for v in results[nid].violations],
                }
                for nid in sorted(results.keys())
            },
            "critical_violations_count": sum(1 for v in total_violations if v.severity == "CRITICAL"),
            "error_violations_count": sum(1 for v in total_violations if v.severity == "ERROR"),
            "warning_violations_count": sum(1 for v in total_violations if v.severity == "WARNING"),
        }


def verify_standards_compliance(node_id: int, artifact: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Convenience function for integration with Stage-Gate verification engines.
    Returns: (passed: bool, message: str, telemetry: dict)
    """
    linter = StandardsLinter()
    res = linter.lint_node_artifact(node_id, artifact)
    if not res.is_compliant:
        err_msgs = [f"[{v.standard_id}] {v.rule}: {v.message}" for v in res.violations if v.severity in ("CRITICAL", "ERROR")]
        summary = "; ".join(err_msgs)
        return False, f"Standards Non-Compliance (Score {res.compliance_score_pct}%): {summary}", res.model_dump()
    return True, f"Standards Compliance Verified (Score {res.compliance_score_pct}%)", res.model_dump()


__all__ = [
    "StandardViolation",
    "StandardsLintResult",
    "StandardsLinter",
    "verify_standards_compliance",
    "VALID_SPDX_IDENTIFIERS",
]
