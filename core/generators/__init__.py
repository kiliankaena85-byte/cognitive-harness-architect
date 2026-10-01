"""
core/generators package: Specialized Engineering Tooling & Exporters.
Universal Cognitive Decomposition Engine (UCDE) - Waves 2 & 3
"""

# Department 1: Strategy
from .service_blueprint import BlueprintStep, ServiceBlueprint, ServiceBlueprintGenerator
from .ost_engine import (
    AssumptionTestNode,
    SolutionNode,
    OpportunityNode,
    OpportunitySolutionTree,
    OstEngine,
)

# Department 2: Finance
from .finops_focus import FocusRecord, FocusDataSet, FinopsFocusExporter
from .model_cascade import (
    ModelTierSpec,
    RoutingDecision,
    CascadeSimulationReport,
    ModelCascadeOptimizer,
)

# Department 3: Legal
from .ai_act_dossier import AiActDossierSection, EuAiActTechnicalDossier, EuAiActDossierGenerator
from .spdx_guard import SpdxPackageEntry, SbomManifest, SpdxLicenseGuard

# Department 4: Security
from .spiffe_spire import SpiffeRegistrationEntry, SpiffeIdentityManifest, SpiffeSpireGenerator
from .dast_fuzzer import FuzzTestResult, DastAuditReport, DastCognitiveFuzzer

# Department 5: Architecture
from .c4_dsl_exporter import C4DslExporter
from .self_rag import SelfRagSegment, SelfRagAnnotatedOutput, SelfRagEngine

__all__ = [
    # Department 1
    "BlueprintStep",
    "ServiceBlueprint",
    "ServiceBlueprintGenerator",
    "AssumptionTestNode",
    "SolutionNode",
    "OpportunityNode",
    "OpportunitySolutionTree",
    "OstEngine",
    # Department 2
    "FocusRecord",
    "FocusDataSet",
    "FinopsFocusExporter",
    "ModelTierSpec",
    "RoutingDecision",
    "CascadeSimulationReport",
    "ModelCascadeOptimizer",
    # Department 3
    "AiActDossierSection",
    "EuAiActTechnicalDossier",
    "EuAiActDossierGenerator",
    "SpdxPackageEntry",
    "SbomManifest",
    "SpdxLicenseGuard",
    # Department 4
    "SpiffeRegistrationEntry",
    "SpiffeIdentityManifest",
    "SpiffeSpireGenerator",
    "FuzzTestResult",
    "DastAuditReport",
    "DastCognitiveFuzzer",
    # Department 5
    "C4DslExporter",
    "SelfRagSegment",
    "SelfRagAnnotatedOutput",
    "SelfRagEngine",
]
