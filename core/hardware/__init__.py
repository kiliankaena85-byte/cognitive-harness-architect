"""
core/hardware package: Hardware Runtime, Edge NPU & SRE Optimizers.
Universal Cognitive Decomposition Engine (UCDE) - Waves 2, 3 & 4
"""

from .openvino_dma import DmaBufferDescriptor, OpenVinoDmaOptimizer
from .chaos_fault_injection import ChaosExperimentResult, ChaosResiliencyReport, ChaosFaultInjector
from .watchdog_circuit import (
    WatchdogWindowConfig,
    WatchdogTelemetry,
    SynthesizedRTLDossier,
    HardwareWatchdogSimulator,
    WatchdogCircuitSynthesizer,
)

__all__ = [
    "DmaBufferDescriptor",
    "OpenVinoDmaOptimizer",
    "ChaosExperimentResult",
    "ChaosResiliencyReport",
    "ChaosFaultInjector",
    "WatchdogWindowConfig",
    "WatchdogTelemetry",
    "SynthesizedRTLDossier",
    "HardwareWatchdogSimulator",
    "WatchdogCircuitSynthesizer",
]
