"""
core/generators/ux_fallback.py
=============================================================================
Universal Cognitive Decomposition Engine (UCDE) - Wave 4
Department 1: Product Strategy, Discovery & Human-Centred AI (ISO 9241-210).

Implements Adaptive UX Graceful Degradation Statecharts and Human-in-the-Loop
(HITL) operator handover protocols:
1. Dynamic confidence tracking: AI model confidence threshold (C < 0.70) triggers
   progressive degradation states.
2. Graceful Degradation States:
   - FULL_AUTOMATION (C >= 0.85): Zero interruption, high-velocity autonomous action.
   - SUPERVISED_ASSIST (0.70 <= C < 0.85): AI suggests, operator observes with confidence UI.
   - HITL_CONFIRMATION (0.50 <= C < 0.70): Explicit human sign-off required with visual diff.
   - DETERMINISTIC_FALLBACK (C < 0.50): Suppress LLM, invoke deterministic rule templates.
   - EMERGENCY_OPERATOR_TAKEOVER: Immediate fail-safe halt; operator takes full manual control.
3. Mermaid Statechart generation (stateDiagram-v2) for UI frontend integration.
4. Conforms to ISO 9241-210:2019 (Human-centred design for interactive systems).
=============================================================================
"""

import json
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class UXAutomationLevel(str, Enum):
    """Automation levels for Human-AI teaming according to ISO 9241-210."""
    FULL_AUTOMATION = "FULL_AUTOMATION"
    SUPERVISED_ASSIST = "SUPERVISED_ASSIST"
    HITL_CONFIRMATION = "HITL_CONFIRMATION"
    DETERMINISTIC_FALLBACK = "DETERMINISTIC_FALLBACK"
    EMERGENCY_OPERATOR_TAKEOVER = "EMERGENCY_OPERATOR_TAKEOVER"


class DegradationTrigger(BaseModel):
    """Telemetry trigger causing a UX state transition."""
    model_config = ConfigDict(extra="forbid")

    trigger_id: str = Field(description="Уникальный идентификатор триггера (например, TRIG-CONF-DROP)")
    metric_name: str = Field(description="Контролируемая метрика (например, model_confidence, latency_ms)")
    threshold_value: float = Field(description="Пороговое значение метрики")
    operator: str = Field(description="Оператор сравнения (<, <=, >, >=, ==)")
    description: str = Field(description="Инженерное обоснование триггера деградации")


class DegradationTransition(BaseModel):
    """Formal transition between UX degradation states."""
    model_config = ConfigDict(extra="forbid")

    source_state: UXAutomationLevel = Field(description="Исходное состояние интерфейса")
    target_state: UXAutomationLevel = Field(description="Целевое состояние деградации")
    trigger: DegradationTrigger = Field(description="Событие, инициирующее переход")
    user_notification: str = Field(description="Сообщение оператору о смене режима взаимодействия")
    safety_action: str = Field(description="Действие защитной автоматики (например, pause_actuator, lock_release)")


class HITLHandoverDossier(BaseModel):
    """Protocol for safely transferring execution control from AI to Human Operator."""
    model_config = ConfigDict(extra="forbid")

    handover_id: str = Field(description="Идентификатор протокола передачи управления (например, HO-2026-001)")
    triggering_confidence: float = Field(description="Зафиксированный уровень уверенности модели (C < 0.70)")
    state_snapshot_id: str = Field(description="Хеш снимка состояния контекста (SHA-256)")
    unresolved_conflicts: List[str] = Field(
        default_factory=list, description="Список неразрешенных противоречий в гипотезах"
    )
    recommended_operator_actions: List[str] = Field(
        default_factory=list, description="Рекомендуемые действия для оператора-человека"
    )
    timeout_seconds: int = Field(default=300, description="Таймаут ожидания реакции оператора до аварийного сброса")
    fallback_safe_default: str = Field(
        description="Детерминированное безопасное состояние по умолчанию при невыходе оператора на связь"
    )


class GracefulDegradationPlan(BaseModel):
    """Comprehensive UX degradation plan conforming to ISO 9241-210."""
    model_config = ConfigDict(extra="forbid")

    system_name: str = Field(description="Наименование когнитивной системы")
    current_level: UXAutomationLevel = Field(
        default=UXAutomationLevel.FULL_AUTOMATION, description="Текущий уровень автоматизации интерфейса"
    )
    confidence_threshold_full: float = Field(default=0.85, description="Порог перехода в полную автоматизацию")
    confidence_threshold_supervised: float = Field(default=0.70, description="Порог перехода в режим ассистирования")
    confidence_threshold_hitl: float = Field(default=0.50, description="Порог перехода в режим HITL утверждения")
    transitions: List[DegradationTransition] = Field(
        default_factory=list, description="Граф переходов между состояниями деградации"
    )
    hitl_dossier: Optional[HITLHandoverDossier] = Field(
        default=None, description="Активный протокол передачи управления человеку"
    )


class UXFallbackEngine:
    """
    Engine evaluating runtime telemetry, computing graceful degradation states,
    and generating ISO 9241-210 compliant UX statecharts and handover protocols.
    """

    def __init__(
        self,
        full_threshold: float = 0.85,
        supervised_threshold: float = 0.70,
        hitl_threshold: float = 0.50,
    ) -> None:
        self.full_threshold = full_threshold
        self.supervised_threshold = supervised_threshold
        self.hitl_threshold = hitl_threshold

    def evaluate_telemetry(
        self,
        confidence: float,
        latency_ms: float = 25.0,
        error_rate: float = 0.0,
        hardware_fault: bool = False,
    ) -> UXAutomationLevel:
        """
        Determines the appropriate UX automation level based on confidence and safety telemetry.
        """
        if hardware_fault:
            return UXAutomationLevel.EMERGENCY_OPERATOR_TAKEOVER

        if error_rate > 0.05 or latency_ms > 2000.0:
            return UXAutomationLevel.EMERGENCY_OPERATOR_TAKEOVER

        if confidence >= self.full_threshold:
            return UXAutomationLevel.FULL_AUTOMATION
        elif confidence >= self.supervised_threshold:
            return UXAutomationLevel.SUPERVISED_ASSIST
        elif confidence >= self.hitl_threshold:
            return UXAutomationLevel.HITL_CONFIRMATION
        else:
            return UXAutomationLevel.DETERMINISTIC_FALLBACK

    def generate_default_plan(self, system_name: str = "Universal Cognitive Engine") -> GracefulDegradationPlan:
        """Generates standard ISO 9241-210 degradation statechart plan."""
        transitions = [
            DegradationTransition(
                source_state=UXAutomationLevel.FULL_AUTOMATION,
                target_state=UXAutomationLevel.SUPERVISED_ASSIST,
                trigger=DegradationTrigger(
                    trigger_id="TRIG-CONF-01",
                    metric_name="confidence",
                    threshold_value=self.full_threshold,
                    operator="<",
                    description=f"Model confidence dropped below {self.full_threshold}",
                ),
                user_notification="AI confidence decreased. Switching to supervised assistive mode.",
                safety_action="enable_confidence_badge_and_rationale_preview",
            ),
            DegradationTransition(
                source_state=UXAutomationLevel.SUPERVISED_ASSIST,
                target_state=UXAutomationLevel.HITL_CONFIRMATION,
                trigger=DegradationTrigger(
                    trigger_id="TRIG-CONF-02",
                    metric_name="confidence",
                    threshold_value=self.supervised_threshold,
                    operator="<",
                    description=f"Model confidence dropped below {self.supervised_threshold}",
                ),
                user_notification="AI confidence is marginal. Human confirmation required for state commit.",
                safety_action="lock_transaction_until_explicit_user_signature",
            ),
            DegradationTransition(
                source_state=UXAutomationLevel.HITL_CONFIRMATION,
                target_state=UXAutomationLevel.DETERMINISTIC_FALLBACK,
                trigger=DegradationTrigger(
                    trigger_id="TRIG-CONF-03",
                    metric_name="confidence",
                    threshold_value=self.hitl_threshold,
                    operator="<",
                    description=f"Model confidence dropped below {self.hitl_threshold}",
                ),
                user_notification="AI generation suppressed due to low confidence. Deterministic rules engaged.",
                safety_action="activate_hardcoded_safety_template",
            ),
            DegradationTransition(
                source_state=UXAutomationLevel.DETERMINISTIC_FALLBACK,
                target_state=UXAutomationLevel.EMERGENCY_OPERATOR_TAKEOVER,
                trigger=DegradationTrigger(
                    trigger_id="TRIG-FAULT-01",
                    metric_name="hardware_fault_or_timeout",
                    threshold_value=1.0,
                    operator="==",
                    description="Hardware watchdog tripped or operator timeout elapsed",
                ),
                user_notification="Emergency: Full manual takeover required immediately.",
                safety_action="deenergize_actuators_and_dump_flight_recorder",
            ),
        ]

        return GracefulDegradationPlan(
            system_name=system_name,
            current_level=UXAutomationLevel.FULL_AUTOMATION,
            confidence_threshold_full=self.full_threshold,
            confidence_threshold_supervised=self.supervised_threshold,
            confidence_threshold_hitl=self.hitl_threshold,
            transitions=transitions,
        )

    def export_mermaid_statechart(self, plan: GracefulDegradationPlan) -> str:
        """Exports the graceful degradation state machine to Mermaid format."""
        lines = [
            "stateDiagram-v2",
            "    [*] --> FULL_AUTOMATION",
            "    FULL_AUTOMATION --> SUPERVISED_ASSIST: Confidence < 0.85",
            "    SUPERVISED_ASSIST --> HITL_CONFIRMATION: Confidence < 0.70",
            "    HITL_CONFIRMATION --> DETERMINISTIC_FALLBACK: Confidence < 0.50",
            "    DETERMINISTIC_FALLBACK --> EMERGENCY_OPERATOR_TAKEOVER: Hardware Fault / Timeout",
            "    SUPERVISED_ASSIST --> FULL_AUTOMATION: Confidence >= 0.85",
            "    HITL_CONFIRMATION --> SUPERVISED_ASSIST: Confidence >= 0.70",
            "    DETERMINISTIC_FALLBACK --> HITL_CONFIRMATION: Rules Pass & Operator Responds",
            "    EMERGENCY_OPERATOR_TAKEOVER --> [*]: Safe Shutdown",
        ]
        return "\n".join(lines)

    def create_handover_dossier(
        self,
        confidence: float,
        state_hash: str,
        conflicts: List[str],
        recommended_actions: Optional[List[str]] = None,
        timeout_seconds: int = 300,
    ) -> HITLHandoverDossier:
        """Prepares a formal handover dossier for human operator intervention."""
        actions = recommended_actions or [
            "Review flagged contract invariants in diff viewer",
            "Confirm or reject downstream financial allocation",
            "Sign audit token or select deterministic fallback template",
        ]
        return HITLHandoverDossier(
            handover_id=f"HO-ISO9241-{state_hash[:8].upper()}",
            triggering_confidence=round(confidence, 4),
            state_snapshot_id=state_hash,
            unresolved_conflicts=conflicts,
            recommended_operator_actions=actions,
            timeout_seconds=timeout_seconds,
            fallback_safe_default="Engage Simplex Deterministic Rule Engine (Zero LLM reliance)",
        )
