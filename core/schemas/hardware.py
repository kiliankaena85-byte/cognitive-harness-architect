"""
Ministry 6: Hardware Runtime & Edge NPU Schema Contract
Artifact: Hardware_Runtime_Manifest.json
Stage-Gate: Gate 6: RAM Budget <= 16GB & NPU Latency <= 50ms (NPU Subsystem RAM <= 512 MB)
"""

from typing import Any, List, Literal
from typing_extensions import Self
from pydantic import BaseModel, ConfigDict, Field, model_validator


class FmeaFailureMode(BaseModel):
    """Failure Mode and Effects Analysis (FMEA) Component (ГОСТ Р 27.302-2009 / IEC 60812)."""
    model_config = ConfigDict(extra="forbid")

    failure_mode_id: str = Field(min_length=1, description="Идентификатор вида отказа, например FM-01")
    component: str = Field(min_length=1, description="Аппаратный компонент (привод, NPU, шина памяти)")
    potential_failure_mode: str = Field(min_length=5, description="Потенциальный вид отказа")
    potential_effect: str = Field(min_length=5, description="Потенциальные последствия отказа")
    severity: int = Field(ge=1, le=10, description="Тяжесть последствий S (1-10)")
    occurrence: int = Field(ge=1, le=10, description="Вероятность возникновения O (1-10)")
    detection: int = Field(ge=1, le=10, description="Обнаруживаемость D (1-10)")
    rpn: int = Field(default=0, ge=0, le=1000, description="Коэффициент приоритета риска RPN = S * O * D")
    mitigation_action: str = Field(min_length=5, description="Корректирующее или превентивное действие")

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)
        calculated = self.severity * self.occurrence * self.detection
        if self.rpn == 0 or self.rpn != calculated:
            self.rpn = calculated


class FaultTreeNode(BaseModel):
    """Fault Tree Analysis (FTA) Node conforming to IEC 61025 / ГОСТ Р 27.302."""
    model_config = ConfigDict(extra="forbid")

    node_id: str = Field(pattern=r"^FTN-[A-Z0-9]+-\d+$", description="Уникальный идентификатор узла FTA (например FTN-GATE-01)")
    gate_type: Literal["AND", "OR", "BASIC_EVENT", "VOTE"] = Field(description="Тип логического вентиля FTA")
    description: str = Field(min_length=5, description="Описание логического вентиля или базисного события")
    probability_per_hour: float = Field(default=1e-6, ge=0.0, le=1.0, description="Интенсивность отказов в час (lambda)")
    children_node_ids: List[str] = Field(default_factory=list, description="Идентификаторы дочерних узлов в дереве отказов")


class HardwareRuntimeContract(BaseModel):
    """Contract for Ministry 6 (Hardware Runtime & Edge NPU)."""
    model_config = ConfigDict(extra="forbid")

    target_cpu_profile: str = Field(
        default="Intel Core Ultra 5 125H", description="Целевой профиль мобильного процессора Meteor Lake"
    )
    target_npu_device: Literal["INTEL_AI_BOOST_VPU_3720", "INTEL_ARC_GPU", "CPU_FALLBACK"] = Field(
        default="INTEL_AI_BOOST_VPU_3720", description="Аппаратное устройство выполнения тензорных операций"
    )
    openvino_version: str = Field(default="2026.4.0", description="Версия OpenVINO Runtime")
    max_ram_budget_mb: float = Field(
        gt=0, le=512.0, description="Жесткий инвариант: не более 512 МБ RAM для NPU подсистемы"
    )
    p99_latency_ms: float = Field(
        gt=0, le=50.0, description="Жесткий инвариант: p99 латентность инференса не более 50 мс"
    )
    cold_start_budget_ms: float = Field(gt=0, le=100.0, description="Бюджет времени холодного старта <= 100 мс")
    hardware_interlocks_required: bool = Field(
        default=False, description="Требование аппаратных блокировок (Hardware Interlocks)"
    )
    physical_actuator_latency_ms: float = Field(
        default=0.0, ge=0.0, description="Время отклика физического привода в миллисекундах"
    )
    iec_61508_sil_level: Literal["SIL_1", "SIL_2", "SIL_3", "SIL_4", "NONE"] = Field(
        default="SIL_2", description="Уровень полноты функциональной безопасности (IEC 61508 / ISO 26262 ASIL)"
    )
    ieee_754_precision: Literal["FP32", "FP16", "BF16", "INT8"] = Field(
        default="INT8", description="Формат квантования и точности вычислений (IEEE 754 / INT8 OpenVINO)"
    )
    fmea_risk_analysis: List[FmeaFailureMode] = Field(
        default_factory=list, description="Матрица FMEA анализа надежности и безопасности (ГОСТ Р 27.302-2009)"
    )
    max_fmea_rpn: int = Field(
        default=120, le=120, description="Предельно допустимый порог риска RPN <= 120 (IEC 61508 SIL-2)"
    )
    fault_tree_analysis: List[FaultTreeNode] = Field(
        default_factory=list, description="Дерево отказов FTA по стандарту IEC 61025 / ГОСТ Р 27.302"
    )
    iec_61025_fta_verified: bool = Field(
        default=True, description="Подтверждение анализа дерева отказов по IEC 61025"
    )

    @model_validator(mode="after")
    def verify_physical_temporal_invariants(self) -> Self:
        """
        Therac-25 Race Condition & FMEA RPN Safety Guard:
        1. If physical actuator latency > 1000ms, mandatory hardware interlocks must be required.
        2. Ensure all FMEA failure modes satisfy RPN <= max_fmea_rpn.
        """
        if self.physical_actuator_latency_ms > 1000.0 and not self.hardware_interlocks_required:
            raise ValueError(
                "Therac-25 Hazard: Physical actuator latency > 1000ms requires mandatory Hardware Interlocks!"
            )
        for fm in self.fmea_risk_analysis:
            if fm.rpn > self.max_fmea_rpn:
                raise ValueError(
                    f"FMEA Violation: Failure mode '{fm.failure_mode_id}' RPN ({fm.rpn}) exceeds allowable threshold ({self.max_fmea_rpn})!"
                )
        return self


__all__ = ["FmeaFailureMode", "FaultTreeNode", "HardwareRuntimeContract"]
