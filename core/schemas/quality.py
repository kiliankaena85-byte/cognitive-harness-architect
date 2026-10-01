"""
Ministry 7: V&V Quality Gate & Certification Schema Contract
Artifact: Release_Certified_Artifacts.json
Stage-Gate: Gate 7: Mutation Score >= 0.95 & Brier Score <= 0.04
"""

from typing import List, Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator


class RagTriadMetricsConfig(BaseModel):
    """Evaluation Metrics for Cognitive Retrieval-Augmented Generation (RAG Triad)."""
    model_config = ConfigDict(extra="forbid")

    context_relevance_score: float = Field(ge=0.85, le=1.0, default=0.92, description="Метрика релевантности контекста запросу >= 0.85")
    groundedness_faithfulness_score: float = Field(ge=0.95, le=1.0, default=0.98, description="Метрика фактологической опоры (отсутствие галлюцинаций) >= 0.95")
    answer_relevance_score: float = Field(ge=0.90, le=1.0, default=0.94, description="Метрика релевантности ответа исходному намерению >= 0.90")
    adversarial_jailbreak_resistance_pct: float = Field(ge=98.0, le=100.0, default=99.5, description="Устойчивость к состязательным атакам и взлому промпта >= 98.0%")


class MutationTestingConfig(BaseModel):
    """Mutation Testing Configuration and Mutation Score Indicator (MSI) (ISO 29119-4)."""
    model_config = ConfigDict(extra="forbid")

    framework: Literal["COSMIC_RAY", "MUTMUT", "AST_MUTATOR"] = Field(default="MUTMUT", description="Фреймворк мутационного анализа")
    mutation_score_indicator_target_pct: float = Field(default=85.0, ge=80.0, le=100.0, description="Целевой показатель MSI >= 85.0%")
    survived_mutants_threshold: int = Field(default=0, ge=0, description="Предельное число выживших мутантов")
    killed_mutants_count: int = Field(default=100, ge=0, description="Число нейтрализованных (убитых) мутантов")
    total_mutants_generated: int = Field(default=105, ge=1, description="Общее число сгенерированных мутантов")


class VVQualityContract(BaseModel):
    """Contract for Ministry 7 (V&V Quality Gate & Certification)."""
    model_config = ConfigDict(extra="forbid")

    gost_34_602_all_sections_present: bool = Field(
        default=True, description="Наличие всех обязательных 8 разделов ГОСТ 34.602-89"
    )
    gost_19_201_sections_present: bool = Field(
        default=True, description="Наличие обязательных разделов ЕСПД по ГОСТ 19.201-78"
    )
    iso_29148_unambiguity_score: float = Field(
        ge=85.0, description="Индекс однозначности требований ISO 29148 >= 85"
    )
    rtm_traceability_coverage_pct: float = Field(
        ge=100.0, description="100% покрытие требований тестами в матрице RTM"
    )
    mutation_score_pct: float = Field(
        ge=95.0, description="Мутационный скор тестов >= 95%"
    )
    mutation_testing: MutationTestingConfig = Field(
        default_factory=MutationTestingConfig, description="Конфигурация мутационного анализа и метрика MSI"
    )
    cognitive_rag_triad: RagTriadMetricsConfig = Field(
        default_factory=RagTriadMetricsConfig, description="Метрики качества когнитивной генерации RAG Triad"
    )
    brier_score_calibration: float = Field(
        le=0.04, description="Калибровка вероятностей прогнозов Браера <= 0.04"
    )
    hoare_logic_invariants_verified: int = Field(
        ge=7, description="Количество формально верифицированных инвариантов Хоара >= 7"
    )
    iso_29119_test_techniques: List[str] = Field(
        default_factory=lambda: ["BOUNDARY_VALUE_ANALYSIS", "EQUIVALENCE_PARTITIONING", "MUTATION_TESTING"],
        description="Методы проектирования тестов по стандарту ISO/IEC/IEEE 29119-4"
    )
    ieee_1012_v_and_v_level: Literal["LEVEL_1", "LEVEL_2", "LEVEL_3", "LEVEL_4"] = Field(
        default="LEVEL_4", description="Уровень верификации и валидации по стандарту IEEE 1012"
    )
    gost_34_603_protocol_id: str = Field(
        default="ПМИ-34.603-2026-001", description="Идентификатор протокола испытаний по ГОСТ 34.603-92"
    )
    cryptographic_release_signature: str = Field(
        min_length=64,
        pattern=r"^[a-fA-F0-9]{64}$",
        description="Криптографический дайджест релиза SHA-256 (64 hex-символа)"
    )

    @field_validator("gost_34_602_all_sections_present")
    @classmethod
    def assert_gost_complete(cls, v: bool) -> bool:
        """Enforce that all mandatory GOST 34.602 sections are present."""
        if not v:
            raise ValueError("GOST 34.602 Incomplete: All mandatory sections must be present!")
        return v


__all__ = ["RagTriadMetricsConfig", "MutationTestingConfig", "VVQualityContract"]
