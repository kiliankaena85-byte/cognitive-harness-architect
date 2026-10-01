"""
core/schemas/inception.py
=============================================================================
Universal Cognitive Decomposition Engine (UCDE)
Level 0: Cognitive Inception & Intent Discovery Schema Contracts.

Defines strict Pydantic V2 models for Module 0 (Intent Inception):
1. InceptionActor: Persona, target goal (JTBD), privilege level.
2. SocraticQuestion: Non-technical clarifying questions with domain recommendations.
3. InceptionContract: The formal handover contract between Module 0 and Ministry 1
   (Strategy & CJM).
4. DiscoveryMode: Execution mode enum (INTERACTIVE, AUTO, BYPASS).
=============================================================================
"""

from enum import Enum
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field


class DiscoveryMode(str, Enum):
    """Operational mode for Level 0 Cognitive Inception."""
    INTERACTIVE = "INTERACTIVE"  # Socratic dialogue with user via CLI/chat
    AUTO = "AUTO"                # Autonomous sovereign enrichment based on domain archetypes
    BYPASS = "BYPASS"            # Direct passthrough for experienced architects / CI pipelines


class InceptionActor(BaseModel):
    """User or system persona identified during intention inception."""
    model_config = ConfigDict(extra="forbid")

    role_name: str = Field(min_length=2, description="Наименование роли (например, SRE_Engineer, Security_Auditor)")
    jtbd_goal: str = Field(min_length=5, description="Ключевая потребность или цель пользователя (Jobs-To-Be-Done)")
    privilege_level: Literal["GUEST", "USER", "OPERATOR", "ADMIN", "SYSTEM"] = Field(
        default="USER", description="Уровень ролевого доступа (RBAC)"
    )


class SocraticQuestion(BaseModel):
    """Jargon-free clarifying question designed for non-technical founders or domain experts."""
    model_config = ConfigDict(extra="forbid")

    question_id: str = Field(description="Уникальный код вопроса (например, Q1_ACTORS, Q2_OPERATIONS)")
    prompt_text: str = Field(min_length=10, description="Формулировка вопроса на человеческом языке")
    target_dimension: Literal["ACTORS", "OPERATIONS", "HARDWARE", "SECURITY", "LEGAL", "BUDGET", "RELIABILITY"] = Field(
        description="Инженерное измерение, закрываемое данным вопросом"
    )
    purpose: str = Field(description="Инженерное обоснование вопроса для 7 Министерств")
    default_recommendation: str = Field(description="Рекомендуемый выбор по отраслевым эталонам")
    suggested_options: List[str] = Field(default_factory=list, description="Варианты ответов A/B/C")


class InceptionContract(BaseModel):
    """
    Formal Level 0 Contract bridging raw user prompt with Ministry 1 (StrategyCJMContract).
    Guarantees zero schema drift and mathematical completeness.
    """
    model_config = ConfigDict(extra="forbid")

    project_name: str = Field(min_length=2, description="Каноническое название проекта")
    target_domain: str = Field(min_length=2, description="Определенный домен архитектуры")
    vagueness_score: float = Field(
        ge=0.0, le=1.0, description="Коэффициент неполноты/абстракции (0.0 - полная спецификация, 1.0 - сырая мысль)"
    )
    actors: List[InceptionActor] = Field(min_length=1, description="Целевые персоны и их JTBD")
    functional_requirements: List[str] = Field(min_length=1, description="Специфицированные функциональные требования")
    hardware_envelope: Dict[str, Any] = Field(
        description="Аппаратные ограничения (NPU, RAM <= 512MB, Watchdog, Latency SLA)"
    )
    compliance_regime: List[str] = Field(
        description="Регуляторные требования (152-ФЗ, ГОСТ Р 56939-2024, ISO 42001)"
    )
    ears_requirements_draft: List[Dict[str, str]] = Field(
        default_factory=list, description="Черновые требования в нотации EARS"
    )
    acceptance_criteria_draft: List[Dict[str, str]] = Field(
        default_factory=list, description="Черновые сценарии приемки Gherkin (Given-When-Then)"
    )
    is_fully_enriched: bool = Field(default=True, description="Флаг готовности к передаче в 7 Министерств")
    source_prompt_hash: str = Field(description="SHA-256 хеш исходного пользовательского промпта")
    sanitized_prompt: str = Field(description="Санитизированный промпт без инъекций")
