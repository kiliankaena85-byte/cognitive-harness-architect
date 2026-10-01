"""
core/generators/service_blueprint.py
=============================================================================
Universal Cognitive Decomposition Engine (UCDE) - Wave 2
Department 1: Product Strategy, CJM & Business Analysis Tooling.

Generates complete Service Blueprints according to Nielsen Norman Group (NN/g)
standard with 5 distinct swimlanes:
1. Customer Actions (derived from JTBD & Acceptance Criteria)
2. Frontstage Interactions (Touchpoints & UI/API boundary)
3. Line of Visibility
4. Backstage Interactions (Core Cognitive Orchestration & Stage-Gates)
5. Line of Internal Interaction
6. Support Processes (NPU Acceleration, SMT Formal Verifier, Vector Memory, Consensus)
7. Physical Evidence / Emitted Artifacts

Outputs:
- Structured JSON representation (Pydantic V2 validated)
- PlantUML Swimlane Activity Diagram (.puml)
- Markdown Table Specification (.md)
=============================================================================
"""

import json
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class BlueprintStep(BaseModel):
    """Single step in a Service Blueprint swimlane."""
    model_config = ConfigDict(extra="forbid")

    step_id: str = Field(description="Уникальный идентификатор шага")
    name: str = Field(description="Название действия или процесса")
    description: str = Field(description="Детальное описание выполнения шага")
    actor: str = Field(description="Субъект выполнения (персона, сервис или подсистема)")
    linked_ac_id: Optional[str] = Field(default=None, description="Связанный критерий приемки (AC-ID)")


class ServiceBlueprint(BaseModel):
    """Full 5-swimlane Service Blueprint specification."""
    model_config = ConfigDict(extra="forbid")

    project_id: str = Field(description="Идентификатор проекта")
    version: str = Field(default="1.0.0", description="Версия Blueprint")
    customer_actions: List[BlueprintStep] = Field(description="Действия пользователя / заказчика")
    frontstage_touchpoints: List[BlueprintStep] = Field(description="Точки взаимодействия (Frontstage)")
    backstage_processes: List[BlueprintStep] = Field(description="Внутренние процессы системы (Backstage)")
    support_processes: List[BlueprintStep] = Field(description="Опорные процессы и инфраструктура (Support)")
    physical_evidence: List[str] = Field(description="Материальные свидетельства и артефакты")


class ServiceBlueprintGenerator:
    """
    Generates standard Service Blueprints from Strategy and Architecture contracts.
    """

    def generate(
        self,
        strategy_artifact: Dict[str, Any],
        analysis_artifact: Optional[Dict[str, Any]] = None,
        project_id: Optional[str] = None,
    ) -> ServiceBlueprint:
        """
        Synthesizes a 5-swimlane Service Blueprint.
        """
        proj_id = project_id or strategy_artifact.get("project_id", "UCDE-Project")
        personas = strategy_artifact.get("target_personas", ["Enterprise Architect"])
        acs = strategy_artifact.get("acceptance_criteria", [])
        primary_persona = personas[0] if personas else "User"

        # 1. Customer Actions
        customer_actions: List[BlueprintStep] = []
        for i, ac in enumerate(acs):
            if isinstance(ac, dict):
                customer_actions.append(BlueprintStep(
                    step_id=f"CA-{i+1:02d}",
                    name=f"Execute: {ac.get('given', 'Action')[:40]}...",
                    description=f"User triggers event: {ac.get('when', '')}",
                    actor=primary_persona,
                    linked_ac_id=ac.get("id"),
                ))
        if not customer_actions:
            customer_actions.append(BlueprintStep(
                step_id="CA-01",
                name="Submit Project Brief",
                description="User uploads specification brief to the cognitive system",
                actor=primary_persona,
                linked_ac_id=None,
            ))

        # 2. Frontstage Touchpoints
        frontstage_touchpoints: List[BlueprintStep] = [
            BlueprintStep(
                step_id="FS-01",
                name="Cognitive Portal / CLI Interface",
                description="Secure interface capturing requirements and rendering stage-gate progress",
                actor="API Gateway / Web UI",
                linked_ac_id=customer_actions[0].linked_ac_id if customer_actions else None,
            ),
            BlueprintStep(
                step_id="FS-02",
                name="Zero-Trust Authentication Barrier",
                description="Mutual TLS / JWT verification validating user tokens before dispatch",
                actor="Auth Gateway",
                linked_ac_id=None,
            ),
        ]

        # 3. Backstage Processes
        backstage_processes: List[BlueprintStep] = [
            BlueprintStep(
                step_id="BS-01",
                name="7-Ministry Multi-Hypothesis Generation",
                description="System 2 parallel synthesis across Strategy, Finance, Legal, Security, Architecture, Hardware, Quality",
                actor="Saga Orchestrator",
                linked_ac_id=None,
            ),
            BlueprintStep(
                step_id="BS-02",
                name="Zero-Trust CDD/TDD Validation Stage-Gates",
                description="Deterministic verification of Pydantic V2 schemas and financial/security invariants",
                actor="Stage Gate Coordinator",
                linked_ac_id=None,
            ),
            BlueprintStep(
                step_id="BS-03",
                name="Multi-Agent PBFT Consensus Voting",
                description="3-phase Byzantine agreement over candidate hypotheses with quorum verification",
                actor="PBFT Consensus Engine",
                linked_ac_id=None,
            ),
        ]

        # 4. Support Processes
        support_processes: List[BlueprintStep] = [
            BlueprintStep(
                step_id="SP-01",
                name="Hardware NPU Accelerated Pareto Ranking",
                description="OpenVINO INT8 L-MOPA lexicographic Pareto optimization on Intel AI Boost NPU",
                actor="Intel AI Boost NPU VPU-3720",
                linked_ac_id=None,
            ),
            BlueprintStep(
                step_id="SP-02",
                name="Formal SMT Theorem Verification",
                description="Z3 SMT Solver proving CIDR, DAG acyclicity, Therac-25 race-freedom, and Solvency",
                actor="Microsoft Z3 SMT Solver",
                linked_ac_id=None,
            ),
            BlueprintStep(
                step_id="SP-03",
                name="4-Tier Cognitive Memory & GraphRAG",
                description="Reciprocal Rank Fusion (RRF k=60) semantic similarity retrieval and prompt quarantine",
                actor="Cognitive Memory Engine",
                linked_ac_id=None,
            ),
        ]

        # 5. Physical Evidence
        physical_evidence: List[str] = [
            "PRD_Specification.json (ISO 29148 / EARS)",
            "Unit_Economics_Budget.json (FinOps FOCUS 1.0)",
            "Compliance_Attestation.json (152-FZ / EU AI Act)",
            "Security_Policy.agentpolicy (Zero Trust / MITRE ATLAS)",
            "System_Contracts.json (OpenAPI 3.1 / AsyncAPI 3.0)",
            "Hardware_Runtime_Manifest.json (FMEA / FTA IEC 61025)",
            "Release_Certified_Artifacts.json (SHA-256 Digest)",
        ]

        return ServiceBlueprint(
            project_id=proj_id,
            version="1.0.0",
            customer_actions=customer_actions,
            frontstage_touchpoints=frontstage_touchpoints,
            backstage_processes=backstage_processes,
            support_processes=support_processes,
            physical_evidence=physical_evidence,
        )

    def to_plantuml(self, blueprint: ServiceBlueprint) -> str:
        """
        Emits clean PlantUML Activity Diagram with 5 Swimlanes.
        """
        lines = [
            "@startuml",
            f"title Service Blueprint: {blueprint.project_id} (v{blueprint.version})",
            "skinparam monochrome true",
            "skinparam shadowing false",
            "skinparam defaultFontName Arial",
            "",
            "|#E8F4F8|Customer Actions|",
            "start",
        ]

        for step in blueprint.customer_actions:
            lines.append(f":{step.name}\\n({step.actor});")

        lines.extend([
            "",
            "|#FFF9E6|Frontstage Interactions|",
        ])
        for step in blueprint.frontstage_touchpoints:
            lines.append(f":{step.name}\\n[{step.actor}];")

        lines.extend([
            "",
            "|#F4F0EA|Line of Visibility (Backstage)|",
        ])
        for step in blueprint.backstage_processes:
            lines.append(f":{step.name}\\n{{{step.actor}}};")

        lines.extend([
            "",
            "|#EAEFF5|Support Processes & Infrastructure|",
        ])
        for step in blueprint.support_processes:
            lines.append(f":{step.name}\\n/{step.actor}/;")

        lines.extend([
            "",
            "|#E8F8F5|Physical Evidence & Artifacts|",
            ":Emitted Formal Deliverables:",
        ])
        for ev in blueprint.physical_evidence:
            lines.append(f"-[#gray]-> * {ev};")

        lines.extend([
            "stop",
            "@enduml",
        ])
        return "\n".join(lines)

    def to_markdown(self, blueprint: ServiceBlueprint) -> str:
        """
        Emits structured Markdown table with swimlanes.
        """
        lines = [
            f"# Service Blueprint: {blueprint.project_id}",
            f"**Version:** {blueprint.version} | **Standard:** Nielsen Norman Group (NN/g)",
            "",
            "## 1. Swimlane Architecture",
            "",
            "| Swimlane | Step ID | Name & Actor | Description | Linked Criteria |",
            "| :--- | :--- | :--- | :--- | :--- |",
        ]

        for step in blueprint.customer_actions:
            lines.append(f"| **Customer Action** | `{step.step_id}` | **{step.name}** ({step.actor}) | {step.description} | `{step.linked_ac_id or 'N/A'}` |")

        for step in blueprint.frontstage_touchpoints:
            lines.append(f"| **Frontstage** | `{step.step_id}` | **{step.name}** ({step.actor}) | {step.description} | `{step.linked_ac_id or 'N/A'}` |")

        for step in blueprint.backstage_processes:
            lines.append(f"| **Backstage** | `{step.step_id}` | **{step.name}** ({step.actor}) | {step.description} | `{step.linked_ac_id or 'N/A'}` |")

        for step in blueprint.support_processes:
            lines.append(f"| **Support Process** | `{step.step_id}` | **{step.name}** ({step.actor}) | {step.description} | `{step.linked_ac_id or 'N/A'}` |")

        lines.extend([
            "",
            "## 2. Physical Evidence & Artifacts Emitted",
            "",
        ])
        for ev in blueprint.physical_evidence:
            lines.append(f"- [x] `{ev}`")

        return "\n".join(lines)


__all__ = ["BlueprintStep", "ServiceBlueprint", "ServiceBlueprintGenerator"]
