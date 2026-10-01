"""
Ministry 2: Finance & Unit Economics Schema Contract
Artifact: Unit_Economics_Budget.json
Stage-Gate: Gate 2: LTV/CAC >= 3.0 & Infra OPEX Cap
"""

from typing import Literal
from typing_extensions import Self
from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, field_validator, model_validator


class TokenEconomicsConfig(BaseModel):
    """Token Economics and LLM FinOps Cost Model."""
    model_config = ConfigDict(extra="forbid")

    prompt_token_budget: int = Field(default=100000, gt=0, description="Бюджет входных токенов на сессию рассуждения")
    completion_token_budget: int = Field(default=25000, gt=0, description="Бюджет выходных токенов на генерацию")
    target_cost_per_thousand_inferences_rub: float = Field(
        default=150.0, gt=0, description="Целевая себестоимость 1000 инференсов в рублях"
    )
    context_cache_hit_rate_target_pct: float = Field(
        default=85.0, ge=0.0, le=100.0, description="Целевой процент кэширования контекста (Context Caching Hit Rate)"
    )


class FinanceBudgetContract(BaseModel):
    """Contract for Ministry 2 (Finance & Unit Economics)."""
    model_config = ConfigDict(extra="forbid")

    currency: Literal["RUB", "USD", "EUR"] = "RUB"
    customer_acquisition_cost: float = Field(gt=0, description="Стоимость привлечения клиента (CAC)")
    lifetime_value: float = Field(gt=0, description="Пожизненная ценность клиента (LTV)")
    target_margin_pct: float = Field(ge=15.0, description="Минимальная маржинальность транзакции >= 15%")
    max_cloud_monthly_opex: float = Field(gt=0, description="Лимит расходов на облако в месяц (OPEX)")
    max_hardware_capex: float = Field(gt=0, description="Предельный бюджет на закупку оборудования (CAPEX)")
    break_even_period_months: int = Field(gt=0, le=24, description="Срок окупаемости <= 24 месяцев")
    finops_focus_version: str = Field(default="1.0", description="Соответствие спецификации FinOps Open Cost and Usage Specification (FOCUS 1.0)")
    iso_31000_risk_assessed: bool = Field(default=True, description="Оценка финансовых рисков по стандарту ISO 31000:2018")
    token_economics: TokenEconomicsConfig = Field(
        default_factory=TokenEconomicsConfig, description="Экономика токенов и FinOps для LLM/нейросетей"
    )

    @field_validator("lifetime_value")
    @classmethod
    def validate_ltv_cac_ratio(cls, v: float, info: ValidationInfo) -> float:
        """Field-level validator enforcing solvency barrier: LTV / CAC >= 3.0."""
        cac = info.data.get("customer_acquisition_cost")
        if cac is not None and cac > 0:
            ratio = v / cac
            if ratio < 3.0:
                raise ValueError(
                    f"Unit Economics Insolvent: LTV/CAC ratio {ratio:.2f} is strictly below 3.0 barrier!"
                )
        return v

    @model_validator(mode="after")
    def validate_unit_economics_model(self) -> Self:
        """Model-level double-guard validator ensuring LTV/CAC >= 3.0 invariant holds."""
        if self.customer_acquisition_cost > 0:
            ratio = self.lifetime_value / self.customer_acquisition_cost
            if ratio < 3.0:
                raise ValueError(
                    f"Unit Economics Insolvent: LTV/CAC ratio {ratio:.2f} is strictly below 3.0 barrier!"
                )
        return self


__all__ = ["TokenEconomicsConfig", "FinanceBudgetContract"]
