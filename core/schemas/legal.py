"""
Ministry 3: Legal & Regulatory Compliance Schema Contract
Artifact: Compliance_Attestation.json
Stage-Gate: Gate 3: Data Sovereignty & License Immunity
"""

from typing import List, Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator


class PersonalDataProcessing(BaseModel):
    """Specification of 152-FZ / GDPR personal data processing."""
    model_config = ConfigDict(extra="forbid")

    processes_personal_data: bool = Field(description="Признак обработки персональных данных")
    data_subjects: List[str] = Field(default_factory=list, description="Субъекты персональных данных")
    localization_country: str = Field(default="RUS", description="Страна первичной локализации баз данных")
    data_localization_rf: bool = Field(default=True, description="Требование первичной локализации баз данных на территории РФ (242-ФЗ)")
    personal_data_categories: List[Literal["ОБЩИЕ", "СПЕЦИАЛЬНЫЕ", "БИОМЕТРИЧЕСКИЕ", "ОБЩЕДОСТУПНЫЕ"]] = Field(
        default_factory=lambda: ["ОБЩИЕ"],
        description="Категории обрабатываемых персональных данных по ст. 10, 11 152-ФЗ"
    )
    cross_border_transfer_allowed: bool = Field(
        default=False,
        description="Разрешение трансграничной передачи ПДн (ст. 12 152-ФЗ)"
    )
    crypto_algorithm: Literal[
        "ГОСТ_Р_34.12-2015_КУЗНЕЧИК",
        "ГОСТ_Р_34.12-2015_МАГМА",
        "AES-256-GCM"
    ] = Field(
        default="ГОСТ_Р_34.12-2015_КУЗНЕЧИК",
        description="Алгоритм криптографической защиты данных (ФСТЭК/ФСБ)"
    )
    fz152_level: Literal["УЗ-1", "УЗ-2", "УЗ-3", "УЗ-4", "NONE"] = Field(
        description="Уровень защищенности ИСПДн по 152-ФЗ"
    )
    gdpr_dpa_required: bool = Field(default=False, description="Необходимость соглашения DPA по GDPR")


class LegalComplianceContract(BaseModel):
    """Contract for Ministry 3 (Legal & Regulatory Compliance)."""
    model_config = ConfigDict(extra="forbid")

    jurisdiction: List[str] = Field(min_length=1, description="Юрисдикции применения")
    personal_data: PersonalDataProcessing = Field(description="Параметры обработки персональных данных")
    fiscal_receipts_54fz: bool = Field(default=True, description="Фискализация чеков по 54-ФЗ")
    ai_act_risk_category: Literal["MINIMAL", "LIMITED", "HIGH", "UNACCEPTABLE"] = Field(
        default="LIMITED", description="Категория риска по EU AI Act"
    )
    approved_open_source_licenses: List[str] = Field(
        min_length=1, description="Разрешенные лицензии открытого ПО (MIT, Apache-2.0, BSD-3)"
    )
    spdx_license_standard: str = Field(default="SPDX-2.3", description="Стандарт спецификации лицензий ISO/IEC 5962:2021 (SPDX)")
    iso_27701_privacy_controls: bool = Field(default=True, description="Соответствие системе менеджмента конфиденциальности ISO/IEC 27701:2019")
    iso_42001_ai_management: bool = Field(default=True, description="Соответствие стандарту менеджмента систем ИИ ISO/IEC 42001:2023")
    fstec_gis_class: Literal["К1", "К2", "К3", "NONE"] = Field(
        default="К2", description="Класс защищенности ГИС по Приказу ФСТЭК России № 17"
    )
    fstec_ispdn_level: Literal["УЗ-1", "УЗ-2", "УЗ-3", "УЗ-4", "NONE"] = Field(
        default="УЗ-2", description="Уровень защищенности ПДн в ИСПДн по Приказу ФСТЭК России № 21"
    )
    fstec_kii_category: Literal["КАТЕГОРИЯ_1", "КАТЕГОРИЯ_2", "КАТЕГОРИЯ_3", "НЕ_КАТЕГОРИРУЕТСЯ"] = Field(
        default="КАТЕГОРИЯ_2", description="Категория значимости объекта КИИ по Приказу ФСТЭК России № 239"
    )
    gost_7_0_97_doc_attributes_present: bool = Field(
        default=True, description="Наличие обязательных реквизитов документа по ГОСТ Р 7.0.97-2016"
    )

    @field_validator("ai_act_risk_category")
    @classmethod
    def reject_unacceptable_risk(cls, v: str) -> str:
        """Compliance veto for prohibited EU AI Act risk category."""
        if v == "UNACCEPTABLE":
            raise ValueError(
                "Compliance Veto: System architecture classified as UNACCEPTABLE risk under EU AI Act!"
            )
        return v


__all__ = ["PersonalDataProcessing", "LegalComplianceContract"]
