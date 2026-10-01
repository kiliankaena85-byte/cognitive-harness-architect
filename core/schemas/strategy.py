"""
Ministry 1: Strategy, Marketing & CJM Schema Contract
Artifact: PRD_Specification.json
Stage-Gate: Gate 1: Business Value & Step Invariant
"""

from typing import Dict, List, Literal
from typing_extensions import Self
from pydantic import BaseModel, ConfigDict, Field, model_validator


class GherkinScenario(BaseModel):
    """BDD Acceptance Criteria Scenario."""
    model_config = ConfigDict(extra="forbid")

    id: str = Field(pattern=r"^AC-[A-Z0-9]+-\d+$", description="Уникальный ID сценария приемки")
    given: str = Field(min_length=5, description="Предусловие сценария")
    when: str = Field(min_length=5, description="Действие сценария")
    then: str = Field(min_length=5, description="Ожидаемый результат")


class BusinessRule(BaseModel):
    """Business rule grounded in an upstream Acceptance Criteria."""
    model_config = ConfigDict(extra="forbid")

    rule_id: str = Field(pattern=r"^BR-\d+$", description="Идентификатор бизнес-правила")
    description: str = Field(min_length=10, description="Формальное описание правила")
    source_ac_id: str = Field(description="Строгая ссылка на Acceptance Criteria (защита от семантического хамелеона)")


class StrategyCJMContract(BaseModel):
    """Contract for Ministry 1 (Strategy, Marketing & CJM)."""
    model_config = ConfigDict(extra="forbid")

    project_id: str = Field(min_length=1, description="Идентификатор проекта")
    product_vision: str = Field(min_length=20, description="Видение продукта")
    target_personas: List[str] = Field(min_length=1, description="Целевые персоны")
    jobs_to_be_done: List[str] = Field(min_length=1, description="JTBD задачи пользователя")
    acceptance_criteria: List[GherkinScenario] = Field(min_length=1, description="Сценарии приемки BDD")
    business_rules: List[BusinessRule] = Field(min_length=1, description="Бизнес-правила с привязкой к AC")
    iso_29148_syntax_validated: bool = Field(default=True, description="Соответствие требованиям ISO/IEC/IEEE 29148:2018")
    gherkin_dialect: str = Field(default="ru", description="Диалект Gherkin сценариев (ru / en)")
    babok_baccm_aligned: bool = Field(default=True, description="Соответствие концептуальной модели BACCM (BABOK v3)")
    target_document_profile: Literal["GOST_34_AUTOMATED_SYSTEM", "GOST_19_ESPD_SOFTWARE", "HYBRID_INTEGRATED"] = Field(
        default="GOST_34_AUTOMATED_SYSTEM",
        description="Профиль целевой документации: ГОСТ 34 (АС), ГОСТ 19 (ПО ЕСПД) или Гибридный"
    )
    gost_19_espd_sections_defined: bool = Field(
        default=True, description="Определение структуры разделов ЕСПД по ГОСТ 19.201-78 / ГОСТ 19.404-79"
    )
    gost_7_0_97_requisites: Dict[str, str] = Field(
        default_factory=lambda: {
            "approval_stamp": "УТВЕРЖДАЮ",
            "organization": "АО «Когнитивные Системы»",
            "doc_code": "ТЗ-2026.01",
            "city": "Москва",
        },
        description="Реквизиты оформления титульного листа по ГОСТ Р 7.0.97-2016"
    )

    @model_validator(mode="after")
    def verify_intent_bidirectional_traceability(self) -> Self:
        """
        Enforces that every business rule maps to an existing Acceptance Criteria ID,
        preventing semantic chameleon and ungrounded hallucinations.
        """
        ac_ids = {ac.id for ac in self.acceptance_criteria}
        for rule in self.business_rules:
            if rule.source_ac_id not in ac_ids:
                raise ValueError(
                    f"Adversarial Rule {rule.rule_id}: source_ac_id '{rule.source_ac_id}' not found in ACs!"
                )
        return self


__all__ = ["GherkinScenario", "BusinessRule", "StrategyCJMContract"]
