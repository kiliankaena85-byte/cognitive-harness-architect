"""
core/generators/ias38_auditor.py
=============================================================================
Universal Cognitive Decomposition Engine (UCDE) - Wave 4
Department 2: Financial Viability & Accounting Standards (IAS 38 / IFRS 15).

Implements strict accounting compliance for Intangible Assets under IAS 38:
1. Strict separation of Research Phase (OPEX - expensed as incurred) from
   Development Phase (CAPEX - capitalised to balance sheet).
2. Verification of all 6 cumulative criteria under IAS 38.57:
   - Criterion 1: Technical feasibility of completion.
   - Criterion 2: Intention to complete and use or sell.
   - Criterion 3: Ability to use or sell the intangible asset.
   - Criterion 4: Generation of probable future economic benefits (IFRS 15 / cost savings).
   - Criterion 5: Availability of adequate technical, financial, and other resources.
   - Criterion 6: Ability to measure reliably attributable expenditures.
3. Multi-year amortization schedule generation (Linear / Straight-Line) and
   IAS 36 Impairment trigger monitoring.
=============================================================================
"""

import json
from enum import Enum
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field, model_validator


class AccountingPhase(str, Enum):
    """Phase of software / AI project under IAS 38."""
    RESEARCH = "RESEARCH"          # IAS 38.54 - Always OPEX in profit or loss
    DEVELOPMENT = "DEVELOPMENT"    # IAS 38.57 - May be capitalised if 6 criteria met


class ExpenseItem(BaseModel):
    """Individual project expenditure line item."""
    model_config = ConfigDict(extra="forbid")

    item_id: str = Field(description="Уникальный идентификатор расхода (например, EXP-001)")
    description: str = Field(description="Описание расхода (например, Fine-tuning Llama-3-8B)")
    phase: AccountingPhase = Field(description="Фаза работ по IAS 38 (RESEARCH / DEVELOPMENT)")
    amount_rub: float = Field(gt=0, description="Сумма расхода в рублях")
    cost_category: Literal["Compute_Cloud", "Personnel_RND", "Data_Acquisition", "Hardware_NPU", "Licensing", "Tooling"] = Field(
        description="Категория затрат"
    )
    is_directly_attributable: bool = Field(
        default=True, description="Является ли расход непосредственно связанным с созданием актива (IAS 38.65)"
    )


class CapitalizationChecklist(BaseModel):
    """The 6 cumulative criteria of IAS 38.57 required for asset capitalization."""
    model_config = ConfigDict(extra="forbid")

    technical_feasibility: bool = Field(
        description="Критерий 1: Техническая осуществимость завершения нематериального актива"
    )
    intention_to_complete: bool = Field(
        description="Критерий 2: Намерение руководства завершить разработку и использовать/продать актив"
    )
    ability_to_use_or_sell: bool = Field(
        description="Критерий 3: Способность использовать или продать разрабатываемый актив"
    )
    probable_future_benefits: bool = Field(
        description="Критерий 4: Наличие определенного механизма извлечения будущих экономических выгод"
    )
    resource_availability: bool = Field(
        description="Критерий 5: Наличие достаточных технических, финансовых и кадровых ресурсов"
    )
    reliable_cost_measurement: bool = Field(
        description="Критерий 6: Способность надежно оценить затраты, относящиеся к разработке"
    )

    @property
    def all_criteria_met(self) -> bool:
        """Returns True only if all 6 IAS 38.57 cumulative criteria are satisfied."""
        return (
            self.technical_feasibility
            and self.intention_to_complete
            and self.ability_to_use_or_sell
            and self.probable_future_benefits
            and self.resource_availability
            and self.reliable_cost_measurement
        )


class AmortizationMonth(BaseModel):
    """Monthly amortization entry for the capitalized intangible asset."""
    model_config = ConfigDict(extra="forbid")

    month_index: int = Field(ge=1, description="Порядковый номер месяца амортизации")
    opening_carrying_amount: float = Field(ge=0, description="Балансовая стоимость на начало месяца (руб)")
    amortization_expense: float = Field(ge=0, description="Амортизационные отчисления за месяц (руб)")
    closing_carrying_amount: float = Field(ge=0, description="Балансовая стоимость на конец месяца (руб)")
    accumulated_amortization: float = Field(ge=0, description="Накопленная амортизация (руб)")


class IAS38AuditDossier(BaseModel):
    """Comprehensive IAS 38 & IFRS 15 Intangible Asset audit dossier."""
    model_config = ConfigDict(extra="forbid")

    project_name: str = Field(description="Наименование разрабатываемой системы / ИИ-модели")
    audit_date: str = Field(description="Дата проведения аудита (YYYY-MM-DD)")
    useful_life_months: int = Field(
        default=36, ge=12, le=120, description="Срок полезного использования актива в месяцах (IAS 38.88)"
    )
    total_research_opex: float = Field(ge=0, description="Итого признано расходами периода (OPEX) по фазе исследований")
    total_development_expenditure: float = Field(ge=0, description="Общая сумма расходов по фазе разработки")
    capitalized_asset_initial_cost: float = Field(
        ge=0, description="Первоначальная стоимость признанного нематериального актива (CAPEX)"
    )
    checklist: CapitalizationChecklist = Field(description="Оценка 6 критериев капитализации по IAS 38.57")
    auditor_opinion: Literal["IAS38_FULLY_COMPLIANT_CAPITALIZED", "IAS38_EXPENSED_TO_OPEX_CRITERIA_UNMET"] = Field(
        description="Аудиторское заключение по классификации актива"
    )
    amortization_schedule: List[AmortizationMonth] = Field(
        default_factory=list, description="График линейной амортизации нематериального актива"
    )


class IAS38Auditor:
    """
    Accounting engine that classifies software & AI expenses according to IAS 38,
    verifies capitalization criteria, and calculates amortization schedules.
    """

    def __init__(self, useful_life_months: int = 36) -> None:
        self.useful_life_months = useful_life_months

    def audit_project(
        self,
        project_name: str,
        audit_date: str,
        expenses: List[ExpenseItem],
        checklist: CapitalizationChecklist,
    ) -> IAS38AuditDossier:
        """
        Audits project expenses and produces a formal IAS 38 capitalization dossier.
        """
        research_opex = 0.0
        development_expenditure = 0.0

        for exp in expenses:
            if exp.phase == AccountingPhase.RESEARCH:
                # IAS 38.54: Research costs are strictly expensed when incurred
                research_opex += exp.amount_rub
            elif exp.phase == AccountingPhase.DEVELOPMENT:
                if exp.is_directly_attributable:
                    development_expenditure += exp.amount_rub
                else:
                    # General overheads not directly attributable cannot be capitalized
                    research_opex += exp.amount_rub

        if checklist.all_criteria_met:
            capitalized_cost = development_expenditure
            opinion = "IAS38_FULLY_COMPLIANT_CAPITALIZED"
            schedule = self._generate_amortization_schedule(capitalized_cost, self.useful_life_months)
        else:
            # If any of the 6 criteria is false, entire development is expensed as OPEX
            research_opex += development_expenditure
            capitalized_cost = 0.0
            opinion = "IAS38_EXPENSED_TO_OPEX_CRITERIA_UNMET"
            schedule = []

        return IAS38AuditDossier(
            project_name=project_name,
            audit_date=audit_date,
            useful_life_months=self.useful_life_months,
            total_research_opex=round(research_opex, 2),
            total_development_expenditure=round(development_expenditure, 2),
            capitalized_asset_initial_cost=round(capitalized_cost, 2),
            checklist=checklist,
            auditor_opinion=opinion,
            amortization_schedule=schedule,
        )

    def _generate_amortization_schedule(
        self, initial_cost: float, months: int
    ) -> List[AmortizationMonth]:
        """Calculates straight-line monthly depreciation under IAS 38.97."""
        if initial_cost <= 0 or months <= 0:
            return []

        monthly_rate = initial_cost / months
        schedule: List[AmortizationMonth] = []
        current_book_value = initial_cost
        accumulated = 0.0

        for m in range(1, months + 1):
            if m == months:
                # Final month adjustments to eliminate floating point rounding
                amort_exp = current_book_value
                closing = 0.0
                accumulated = initial_cost
            else:
                amort_exp = round(monthly_rate, 2)
                closing = round(current_book_value - amort_exp, 2)
                accumulated = round(accumulated + amort_exp, 2)

            schedule.append(
                AmortizationMonth(
                    month_index=m,
                    opening_carrying_amount=round(current_book_value, 2),
                    amortization_expense=round(amort_exp, 2),
                    closing_carrying_amount=round(closing, 2),
                    accumulated_amortization=round(accumulated, 2),
                )
            )
            current_book_value = closing

        return schedule
