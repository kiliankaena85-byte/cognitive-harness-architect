"""
core/generators/finops_focus.py
=============================================================================
Universal Cognitive Decomposition Engine (UCDE) - Wave 2
Department 2: Financial Engineering & FinOps Tooling.

Exports financial unit economics and AI tokenomics into the open specification
FinOps Open Cost and Usage Specification (FOCUS) Version 1.0.

Standards:
- FinOps Foundation FOCUS 1.0 (Open Cost and Usage Specification)
- IAS 38 (Intangible Assets / CAPEX vs OPEX recognition)
- RFC 4180 (Common Format and MIME Type for Comma-Separated Values)
=============================================================================
"""

import csv
import io
import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field


class FocusRecord(BaseModel):
    """Single standard record in FinOps Open Cost and Usage Specification (FOCUS 1.0)."""
    model_config = ConfigDict(extra="forbid")

    ChargePeriodStart: str = Field(description="Начало расчетного периода (ISO 8601 UTC)")
    ChargePeriodEnd: str = Field(description="Окончание расчетного периода (ISO 8601 UTC)")
    ProviderName: str = Field(default="Internal Cognitive Cloud", description="Поставщик вычислительных ресурсов")
    PublisherName: str = Field(default="UCDE Platform", description="Издатель сервиса")
    ServiceName: str = Field(description="Название сервиса (например, LLM Inference / NPU Acceleration)")
    ServiceCategory: Literal["AI/ML", "Compute", "Storage", "Network", "Management"] = Field(
        default="AI/ML", description="Категория сервиса по каталогу FOCUS"
    )
    ChargeCategory: Literal["Usage", "Purchase", "Adjustment", "Tax"] = Field(
        default="Usage", description="Категория начисления"
    )
    ChargeSubcategory: str = Field(default="On-Demand Inference", description="Подкатегория начисления")
    PricingCategory: Literal["Standard", "Committed", "Dynamic"] = Field(
        default="Standard", description="Категория ценообразования"
    )
    UsageQuantity: float = Field(ge=0.0, description="Количество использованных единиц")
    UsageUnit: str = Field(description="Единица измерения потребления (Tokens, Inferences, CoreHours, GBHours)")
    BilledCost: float = Field(ge=0.0, description="Фактическая стоимость начисления")
    EffectiveCost: float = Field(ge=0.0, description="Эффективная стоимость с учетом кэширования и скидок")
    Currency: str = Field(default="RUB", description="Валюта начисления")
    SubAccountId: str = Field(default="SUB-001", description="Идентификатор субсчета проекта")
    SubAccountName: str = Field(default="Cognitive Pipeline Production", description="Имя субсчета")
    ResourceId: str = Field(description="Уникальный идентификатор ресурса")
    ResourceName: str = Field(description="Понятное имя ресурса")


class FocusDataSet(BaseModel):
    """Container for FOCUS 1.0 dataset."""
    model_config = ConfigDict(extra="forbid")

    focus_version: str = Field(default="1.0", description="Версия спецификации FOCUS")
    generated_at: str = Field(description="Время генерации датасета (ISO 8601 UTC)")
    total_records: int = Field(ge=0, description="Общее число записей")
    total_billed_cost: float = Field(ge=0.0, description="Суммарная стоимость BilledCost")
    total_effective_cost: float = Field(ge=0.0, description="Суммарная эффективная стоимость EffectiveCost")
    currency: str = Field(default="RUB", description="Основная валюта")
    records: List[FocusRecord] = Field(default_factory=list, description="Список записей FOCUS 1.0")


class FinopsFocusExporter:
    """
    Transforms Finance & Token Economics contracts into FOCUS 1.0 standard datasets.
    """

    def export(self, finance_artifact: Dict[str, Any]) -> FocusDataSet:
        """
        Synthesizes a compliant FOCUS 1.0 dataset from Finance contract.
        """
        currency = finance_artifact.get("currency", "RUB")
        monthly_opex = float(finance_artifact.get("max_cloud_monthly_opex", 150000.0))
        capex = float(finance_artifact.get("max_hardware_capex", 500000.0))
        token_econ = finance_artifact.get("token_economics", {})

        prompt_budget = int(token_econ.get("prompt_token_budget", 100000))
        completion_budget = int(token_econ.get("completion_token_budget", 25000))
        cost_per_1k = float(token_econ.get("target_cost_per_thousand_inferences_rub", 150.0))
        cache_hit_pct = float(token_econ.get("context_cache_hit_rate_target_pct", 85.0))

        now_str = datetime.now(timezone.utc).isoformat()
        start_str = datetime.now(timezone.utc).strftime("%Y-%m-01T00:00:00Z")

        # 1. Prompt Tokens Usage (with context caching discount)
        prompt_cost = (prompt_budget / 1000.0) * (cost_per_1k / 20.0)
        effective_prompt_cost = prompt_cost * (1.0 - (cache_hit_pct / 100.0) * 0.75)

        r1 = FocusRecord(
            ChargePeriodStart=start_str,
            ChargePeriodEnd=now_str,
            ServiceName="Cognitive Prompt Token Processor",
            ServiceCategory="AI/ML",
            ChargeCategory="Usage",
            ChargeSubcategory="Input Context Tokens",
            PricingCategory="Standard",
            UsageQuantity=float(prompt_budget),
            UsageUnit="Tokens",
            BilledCost=round(prompt_cost, 2),
            EffectiveCost=round(effective_prompt_cost, 2),
            Currency=currency,
            ResourceId="res-prompt-tokens-pool",
            ResourceName="Reasoning Session Context Window",
        )

        # 2. Completion Tokens Usage
        completion_cost = (completion_budget / 1000.0) * (cost_per_1k / 10.0)
        r2 = FocusRecord(
            ChargePeriodStart=start_str,
            ChargePeriodEnd=now_str,
            ServiceName="Cognitive Output Synthesis",
            ServiceCategory="AI/ML",
            ChargeCategory="Usage",
            ChargeSubcategory="Generated Completion Tokens",
            PricingCategory="Standard",
            UsageQuantity=float(completion_budget),
            UsageUnit="Tokens",
            BilledCost=round(completion_cost, 2),
            EffectiveCost=round(completion_cost, 2),
            Currency=currency,
            ResourceId="res-completion-tokens-pool",
            ResourceName="System 2 Candidate Generator",
        )

        # 3. Monthly Cloud Infrastructure OPEX
        r3 = FocusRecord(
            ChargePeriodStart=start_str,
            ChargePeriodEnd=now_str,
            ServiceName="Cloud Orchestration & Vector DB",
            ServiceCategory="Compute",
            ChargeCategory="Usage",
            ChargeSubcategory="Virtual Machines & Managed DB",
            PricingCategory="Committed",
            UsageQuantity=720.0,
            UsageUnit="Hours",
            BilledCost=round(monthly_opex, 2),
            EffectiveCost=round(monthly_opex * 0.90, 2),
            Currency=currency,
            ResourceId="res-cloud-cluster-prod",
            ResourceName="Kubernetes & Vector Store Infra",
        )

        # 4. Hardware CAPEX Depreciated Share
        monthly_depreciation = capex / 24.0  # 24 months break-even
        r4 = FocusRecord(
            ChargePeriodStart=start_str,
            ChargePeriodEnd=now_str,
            ServiceName="Edge NPU Hardware Infrastructure",
            ServiceCategory="Compute",
            ChargeCategory="Purchase",
            ChargeSubcategory="IAS 38 Capitalized Hardware",
            PricingCategory="Standard",
            UsageQuantity=1.0,
            UsageUnit="Appliance",
            BilledCost=round(monthly_depreciation, 2),
            EffectiveCost=round(monthly_depreciation, 2),
            Currency=currency,
            ResourceId="res-npu-edge-cluster",
            ResourceName="Intel Meteor Lake NPU Accelerators",
        )

        records = [r1, r2, r3, r4]
        total_billed = sum(r.BilledCost for r in records)
        total_effective = sum(r.EffectiveCost for r in records)

        return FocusDataSet(
            focus_version="1.0",
            generated_at=now_str,
            total_records=len(records),
            total_billed_cost=round(total_billed, 2),
            total_effective_cost=round(total_effective, 2),
            currency=currency,
            records=records,
        )

    export_from_contract = export

    def to_csv(self, dataset: FocusDataSet) -> str:
        """
        Emits RFC 4180 compliant CSV string.
        """
        output = io.StringIO()
        fieldnames = list(FocusRecord.model_fields.keys())
        writer = csv.DictWriter(output, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for rec in dataset.records:
            writer.writerow(rec.model_dump())
        return output.getvalue()

    def to_json(self, dataset: FocusDataSet, indent: int = 2) -> str:
        """
        Emits standard JSON string.
        """
        return dataset.model_dump_json(indent=indent)


__all__ = ["FocusRecord", "FocusDataSet", "FinopsFocusExporter"]
