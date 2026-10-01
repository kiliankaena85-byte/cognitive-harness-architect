"""
core/hardware package: Hardware Runtime, Edge NPU & SRE Optimizers.
Universal Cognitive Decomposition Engine (UCDE) - Wave 2
"""

from .openvino_dma import DmaBufferDescriptor, OpenVinoDmaOptimizer

__all__ = ["DmaBufferDescriptor", "OpenVinoDmaOptimizer"]
