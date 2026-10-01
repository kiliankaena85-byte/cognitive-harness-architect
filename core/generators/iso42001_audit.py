"""
core/generators/iso42001_audit.py
=============================================================================
Universal Cognitive Decomposition Engine (UCDE) - Wave 4
Department 3: Legal, Ethics & AI Management Systems (ISO/IEC 42001:2023).

Implements the international standard for Artificial Intelligence Management
Systems (AIMS) conforming to ISO/IEC 42001:2023:
1. Clause 5.2: AI Policy Statement (governance, ethics, sovereignty, safety).
2. Clause 6.1.2 / 6.1.3: AI Risk Assessment & Treatment Plan.
3. Annex A: Statement of Applicability (SoA) covering controls A.2 through A.10:
   - A.2: Policies related to AI
   - A.3: Internal organization & AI Safety Officer
   - A.4: Resources for AI systems (NPU INT8, compute limits)
   - A.5: Assessing impacts of AI systems
   - A.6: AI system life cycle (Saga DAG, CDD/TDD gates)
   - A.7: Data for AI systems (lineage, 152-FZ, privacy)
   - A.8: Information for interested parties (explainability, XAI)
   - A.9: Use of AI systems (human oversight, fallback)
   - A.10: Third-party relationships & foundation model SLAs
4. Clause B.4: AI System Impact Assessment (societal, environmental, energy footprint).
=============================================================================
"""

import json
from enum import Enum
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field


class ControlStatus(str, Enum):
    """Implementation status of ISO/IEC 42001 Annex A control."""
    IMPLEMENTED = "IMPLEMENTED"
    PARTIALLY_IMPLEMENTED = "PARTIALLY_IMPLEMENTED"
    PLANNED = "PLANNED"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class AnnexAControl(BaseModel):
    """Specific ISO/IEC 42001 Annex A control requirement."""
    model_config = ConfigDict(extra="forbid")

    control_id: str = Field(description="Код контрольной меры (например, A.2.1, A.6.2)")
    domain: str = Field(description="Домен AIMS (например, 'AI System Life Cycle', 'Data Governance')")
    title: str = Field(description="Наименование контрольной меры")
    justification: str = Field(description="Обоснование применимости или исключения")
    implementation_status: ControlStatus = Field(description="Статус внедрения в архитектуре")
    technical_mechanism: str = Field(description="Технический механизм системы (например, Z3 Prover, SPIFFE mTLS)")


class AIRiskRecord(BaseModel):
    """Assessment of AI-specific risk under ISO/IEC 42001 Clause 6.1.2."""
    model_config = ConfigDict(extra="forbid")

    risk_id: str = Field(description="Идентификатор риска (например, RISK-AI-01)")
    hazard: str = Field(description="Источник опасности (например, Hallucination, Prompt Injection, Latency Spike)")
    likelihood: Literal["LOW", "MEDIUM", "HIGH"] = Field(description="Вероятность реализации")
    impact: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"] = Field(description="Тяжесть последствий")
    mitigation_control_id: str = Field(description="Связанный контрол Annex A (например, A.9.3)")
    residual_risk: Literal["NEGLIGIBLE", "ACCEPTABLE", "UNACCEPTABLE"] = Field(description="Остаточный риск")


class AIImpactAssessment(BaseModel):
    """AI System Impact Assessment under ISO/IEC 42001 Annex B.4."""
    model_config = ConfigDict(extra="forbid")

    assessment_id: str = Field(description="Идентификатор оценки воздействия (например, AIA-2026-01)")
    human_oversight_mechanism: str = Field(description="Механизм человеческого надзора (ISO 9241-210 HITL)")
    fairness_and_bias_controls: str = Field(description="Меры предотвращения дискриминации и смещения")
    environmental_energy_profile: str = Field(
        description="Энергетический профиль (NPU INT8 50W vs GPU Cluster 800W)"
    )
    societal_impact_rating: Literal["BENEFICIAL_LOW_RISK", "MODERATE_RISK", "HIGH_RISK"] = Field(
        description="Общий рейтинг социального воздействия"
    )


class ISO42001AIMSReport(BaseModel):
    """Comprehensive ISO/IEC 42001 AIMS Audit Dossier."""
    model_config = ConfigDict(extra="forbid")

    system_name: str = Field(description="Наименование сертифицируемой ИИ-системы")
    aims_policy_version: str = Field(description="Версия политики управления ИИ")
    certification_readiness: Literal["READY_FOR_STAGE_2_AUDIT", "REQUIRES_REMEDIATION", "NON_COMPLIANT"] = Field(
        description="Готовность к сертификационному аудиту органом по сертификации"
    )
    controls_implemented_count: int = Field(ge=0, description="Количество внедренных контролей Annex A")
    total_controls_count: int = Field(ge=1, description="Общее количество контролей Annex A")
    statement_of_applicability: List[AnnexAControl] = Field(
        default_factory=list, description="Ведомость применимости мер (Statement of Applicability - SoA)"
    )
    risk_register: List[AIRiskRecord] = Field(
        default_factory=list, description="Реестр рисков ИИ и мер по их снижению"
    )
    impact_assessment: AIImpactAssessment = Field(
        description="Оценка воздействия ИИ на человека, общество и окружающую среду"
    )


class ISO42001AuditGenerator:
    """
    Generator creating formal ISO/IEC 42001:2023 AIMS documentation packages,
    Statement of Applicability (SoA), and AI impact assessments.
    """

    def generate_statement_of_applicability(self) -> List[AnnexAControl]:
        """Generates standard Annex A controls for UCDE architecture."""
        return [
            AnnexAControl(
                control_id="A.2.1",
                domain="Policies related to AI",
                title="AI Policy Formulation and Governance",
                justification="Mandatory for enterprise AI governance and risk accountability",
                implementation_status=ControlStatus.IMPLEMENTED,
                technical_mechanism="core/schemas/legal_compliance.py 152-FZ & EU AI Act validators",
            ),
            AnnexAControl(
                control_id="A.3.2",
                domain="Internal Organization",
                title="AI Roles and Responsibilities",
                justification="Clear delineation between ML engineer, safety auditor, and human operator",
                implementation_status=ControlStatus.IMPLEMENTED,
                technical_mechanism="core/generators/ux_fallback.py HITL handover protocol",
            ),
            AnnexAControl(
                control_id="A.4.2",
                domain="Resources for AI Systems",
                title="Computational Resource Constraints",
                justification="Prevent resource exhaustion and unbounded GPU/cloud spend",
                implementation_status=ControlStatus.IMPLEMENTED,
                technical_mechanism="core/hardware/openvino_dma.py NPU pinned memory <= 512 MB",
            ),
            AnnexAControl(
                control_id="A.5.1",
                domain="Assessing Impacts",
                title="AI System Impact Assessment Procedure",
                justification="Required to identify human rights and safety implications",
                implementation_status=ControlStatus.IMPLEMENTED,
                technical_mechanism="core/generators/iso42001_audit.py Clause B.4 assessment",
            ),
            AnnexAControl(
                control_id="A.6.2",
                domain="AI System Life Cycle",
                title="Verification and Validation in Design",
                justification="Ensures formal proof of hard invariants prior to production release",
                implementation_status=ControlStatus.IMPLEMENTED,
                technical_mechanism="core/quality/ci_formal_audit.py Z3 SMT solver & CDD/TDD gates",
            ),
            AnnexAControl(
                control_id="A.7.3",
                domain="Data for AI Systems",
                title="Data Lineage and Sovereign Provenance",
                justification="Enforces Russian 152-FZ localization and SPDX 3.0 license vetting",
                implementation_status=ControlStatus.IMPLEMENTED,
                technical_mechanism="core/generators/spdx_guard.py OpenChain ISO/IEC 5230 veto engine",
            ),
            AnnexAControl(
                control_id="A.8.2",
                domain="Information for Interested Parties",
                title="Explainability and Transparency (XAI)",
                justification="Users and auditors must understand algorithmic rationale",
                implementation_status=ControlStatus.IMPLEMENTED,
                technical_mechanism="core/generators/self_rag.py critique tokens & C4 Structurizr DSL",
            ),
            AnnexAControl(
                control_id="A.9.3",
                domain="Use of AI Systems",
                title="Human Oversight and Graceful Degradation",
                justification="Guarantees safe takeover when model confidence deteriorates",
                implementation_status=ControlStatus.IMPLEMENTED,
                technical_mechanism="core/generators/ux_fallback.py C < 0.70 automatic degradation",
            ),
            AnnexAControl(
                control_id="A.10.1",
                domain="Third-Party Relationships",
                title="Supplier Foundation Model Auditing",
                justification="Protects against upstream provider downtime and API drift",
                implementation_status=ControlStatus.IMPLEMENTED,
                technical_mechanism="core/generators/model_cascade.py 4-Tier fallback cascade",
            ),
        ]

    def build_risk_register(self) -> List[AIRiskRecord]:
        """Builds standard AI risk assessment register."""
        return [
            AIRiskRecord(
                risk_id="RISK-AI-01",
                hazard="Hallucinatory code / configuration output without ground truth",
                likelihood="MEDIUM",
                impact="HIGH",
                mitigation_control_id="A.6.2",
                residual_risk="ACCEPTABLE",
            ),
            AIRiskRecord(
                risk_id="RISK-AI-02",
                hazard="Actuator race condition exceeding 1000ms safety window (Therac-25)",
                likelihood="LOW",
                impact="CRITICAL",
                mitigation_control_id="A.9.3",
                residual_risk="NEGLIGIBLE",
            ),
            AIRiskRecord(
                risk_id="RISK-AI-03",
                hazard="Unauthorized cross-border personal data transfer (152-FZ violation)",
                likelihood="LOW",
                impact="HIGH",
                mitigation_control_id="A.7.3",
                residual_risk="NEGLIGIBLE",
            ),
        ]

    def generate_dossier(self, system_name: str = "Universal Cognitive Engine") -> ISO42001AIMSReport:
        """Constructs complete ISO/IEC 42001:2023 AIMS Audit Dossier."""
        soa = self.generate_statement_of_applicability()
        risks = self.build_risk_register()
        implemented = sum(1 for c in soa if c.implementation_status == ControlStatus.IMPLEMENTED)

        impact = AIImpactAssessment(
            assessment_id="AIA-2026-001",
            human_oversight_mechanism="ISO 9241-210 Graceful degradation with C < 0.70 mandatory human sign-off",
            fairness_and_bias_controls="Deterministic schema invariant checking & L-MOPA Pareto multi-objective selection",
            environmental_energy_profile="Intel Core Ultra AI Boost NPU execution with < 50W peak consumption",
            societal_impact_rating="BENEFICIAL_LOW_RISK",
        )

        readiness = "READY_FOR_STAGE_2_AUDIT" if implemented == len(soa) else "REQUIRES_REMEDIATION"

        return ISO42001AIMSReport(
            system_name=system_name,
            aims_policy_version="1.0.0-PROD",
            certification_readiness=readiness,
            controls_implemented_count=implemented,
            total_controls_count=len(soa),
            statement_of_applicability=soa,
            risk_register=risks,
            impact_assessment=impact,
        )
