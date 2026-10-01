"""
Core Schemas Package: Pydantic V2 Contract Schemas for 7 Ministries
Universal Cognitive Decomposition Engine (UCDE)
"""

import hashlib
from typing import Any, Dict, Optional, Type, TypeVar, Union

from pydantic import BaseModel

from .inception import DiscoveryMode, InceptionActor, InceptionContract, SocraticQuestion
from .strategy import BusinessRule, EarsRequirement, GherkinScenario, StrategyCJMContract
from .finance import FinanceBudgetContract, FinancialRiskProfile, MonteCarloSimulationConfig, TokenEconomicsConfig
from .legal import EuAiActDossier, LegalComplianceContract, PersonalDataProcessing, ThreatModel1119
from .security import (
    REQUIRED_STRIDE_CATEGORIES,
    MitreAtlasThreat,
    OwaspLlmSecurityConfig,
    SecurityPolicyContract,
    StrideThreat,
)
from .analysis import (
    ApiEndpoint,
    ArchitectureDecisionRecord,
    AsyncMessageTopic,
    MemoryArchitectureConfig,
    RagPipelineConfig,
    SelfRagConfig,
    SystemAnalysisContract,
)
from .hardware import FaultTreeNode, FmeaFailureMode, HardwareRuntimeContract
from .quality import MutationTestingConfig, RagTriadMetricsConfig, VVQualityContract

T = TypeVar("T", bound=BaseModel)

# Mapping from canonical ministry names / IDs to Pydantic Model classes
CONTRACT_SCHEMAS_REGISTRY: Dict[str, Type[BaseModel]] = {
    "MINISTRY_0_INCEPTION": InceptionContract,
    "MINISTRY_1_STRATEGY_CJM": StrategyCJMContract,
    "MINISTRY_2_FINANCE": FinanceBudgetContract,
    "MINISTRY_3_LEGAL_COMPLIANCE": LegalComplianceContract,
    "MINISTRY_4_INFOSEC": SecurityPolicyContract,
    "MINISTRY_5_SYSTEM_ARCHITECTURE": SystemAnalysisContract,
    "MINISTRY_6_HARDWARE_RUNTIME": HardwareRuntimeContract,
    "MINISTRY_7_VV_QUALITY_GATE": VVQualityContract,
    # Friendly alias keys
    "inception": InceptionContract,
    "strategy": StrategyCJMContract,
    "finance": FinanceBudgetContract,
    "legal": LegalComplianceContract,
    "security": SecurityPolicyContract,
    "analysis": SystemAnalysisContract,
    "hardware": HardwareRuntimeContract,
    "quality": VVQualityContract,
}

# Alias for compatibility with explorer specifications
MINISTRY_CONTRACT_REGISTRY: Dict[str, Type[BaseModel]] = CONTRACT_SCHEMAS_REGISTRY

# Mapping from integer ministry index to Model classes
MINISTRY_ID_MAP: Dict[int, Type[BaseModel]] = {
    0: InceptionContract,
    1: StrategyCJMContract,
    2: FinanceBudgetContract,
    3: LegalComplianceContract,
    4: SecurityPolicyContract,
    5: SystemAnalysisContract,
    6: HardwareRuntimeContract,
    7: VVQualityContract,
}

# Mapping from canonical output artifact filename to Model classes
MINISTRY_ARTIFACT_REGISTRY: Dict[str, Type[BaseModel]] = {
    "Enriched_Project_Brief.json": InceptionContract,
    "PRD_Specification.json": StrategyCJMContract,
    "Unit_Economics_Budget.json": FinanceBudgetContract,
    "Compliance_Attestation.json": LegalComplianceContract,
    "Security_Policy.agentpolicy": SecurityPolicyContract,
    "System_Contracts.json": SystemAnalysisContract,
    "Hardware_Runtime_Manifest.json": HardwareRuntimeContract,
    "Release_Certified_Artifacts.json": VVQualityContract,
}


def get_contract_class(identifier: Union[str, int]) -> Type[BaseModel]:
    """
    Resolves a contract class by ministry ID string, artifact filename, or integer index.
    Raises KeyError if not found.
    """
    if isinstance(identifier, int):
        if identifier in MINISTRY_ID_MAP:
            return MINISTRY_ID_MAP[identifier]
        raise KeyError(f"Unknown ministry index: {identifier}. Must be between 1 and 7.")

    if identifier in CONTRACT_SCHEMAS_REGISTRY:
        return CONTRACT_SCHEMAS_REGISTRY[identifier]
    if identifier in MINISTRY_ARTIFACT_REGISTRY:
        return MINISTRY_ARTIFACT_REGISTRY[identifier]

    raise KeyError(f"Unknown ministry identifier or artifact filename: '{identifier}'")


def export_contract_schema(model_cls: Type[BaseModel]) -> Dict[str, Any]:
    """
    Generates standard OpenAPI 3.1 / JSON Schema Draft 2020-12 representation
    for LLM System 2 constrained decoding.
    """
    return model_cls.model_json_schema()


def serialize_contract(instance: BaseModel, indent: Optional[int] = 2) -> str:
    """
    Serializes a validated contract instance into a formatted JSON string (UTF-8).
    """
    return instance.model_dump_json(indent=indent)


def deserialize_contract(model_cls: Type[T], raw_data: Union[str, bytes, Dict[str, Any]]) -> T:
    """
    Deserializes raw data into a validated contract instance.
    Supports raw JSON string, UTF-8 bytes, or existing dict payloads.
    Throws pydantic.ValidationError if validation fails.
    """
    if isinstance(raw_data, (str, bytes)):
        return model_cls.model_validate_json(raw_data)
    if isinstance(raw_data, dict):
        return model_cls.model_validate(raw_data)
    raise TypeError(f"Unsupported data type for deserialization: {type(raw_data).__name__}")


def compute_contract_hash(instance: BaseModel) -> str:
    """
    Computes deterministic SHA-256 cryptographic digest of a contract instance
    based on compact canonical JSON encoding.
    """
    canonical_json = instance.model_dump_json()
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()


__all__ = [
    # Level 0 Inception
    "InceptionContract",
    "InceptionActor",
    "SocraticQuestion",
    "DiscoveryMode",
    # Ministry 1
    "GherkinScenario",
    "BusinessRule",
    "EarsRequirement",
    "StrategyCJMContract",
    # Ministry 2
    "FinanceBudgetContract",
    "TokenEconomicsConfig",
    "MonteCarloSimulationConfig",
    "FinancialRiskProfile",
    # Ministry 3
    "PersonalDataProcessing",
    "ThreatModel1119",
    "EuAiActDossier",
    "LegalComplianceContract",
    # Ministry 4
    "StrideThreat",
    "MitreAtlasThreat",
    "SecurityPolicyContract",
    "OwaspLlmSecurityConfig",
    "REQUIRED_STRIDE_CATEGORIES",
    # Ministry 5
    "ApiEndpoint",
    "AsyncMessageTopic",
    "RagPipelineConfig",
    "SelfRagConfig",
    "MemoryArchitectureConfig",
    "ArchitectureDecisionRecord",
    "SystemAnalysisContract",
    # Ministry 6
    "HardwareRuntimeContract",
    "FmeaFailureMode",
    "FaultTreeNode",
    # Ministry 7
    "VVQualityContract",
    "RagTriadMetricsConfig",
    "MutationTestingConfig",
    # Registries & Helpers
    "CONTRACT_SCHEMAS_REGISTRY",
    "MINISTRY_CONTRACT_REGISTRY",
    "MINISTRY_ID_MAP",
    "MINISTRY_ARTIFACT_REGISTRY",
    "get_contract_class",
    "export_contract_schema",
    "serialize_contract",
    "deserialize_contract",
    "compute_contract_hash",
]
