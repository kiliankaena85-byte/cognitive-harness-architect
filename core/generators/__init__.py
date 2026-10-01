"""
core/generators package: Specialized Engineering Tooling & Exporters.
Universal Cognitive Decomposition Engine (UCDE) - Waves 2, 3 & 4
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
from .ux_fallback import (
    UXAutomationLevel,
    DegradationTrigger,
    DegradationTransition,
    HITLHandoverDossier,
    GracefulDegradationPlan,
    UXFallbackEngine,
)

# Department 2: Finance
from .finops_focus import FocusRecord, FocusDataSet, FinopsFocusExporter
from .model_cascade import (
    ModelTierSpec,
    RoutingDecision,
    CascadeSimulationReport,
    ModelCascadeOptimizer,
)
from .ias38_auditor import (
    AccountingPhase,
    ExpenseItem,
    CapitalizationChecklist,
    AmortizationMonth,
    IAS38AuditDossier,
    IAS38Auditor,
)

# Department 3: Legal
from .ai_act_dossier import AiActDossierSection, EuAiActTechnicalDossier, EuAiActDossierGenerator
from .spdx_guard import SpdxPackageEntry, SbomManifest, SpdxLicenseGuard
from .iso42001_audit import (
    ControlStatus,
    AnnexAControl,
    AIRiskRecord,
    AIImpactAssessment,
    ISO42001AIMSReport,
    ISO42001AuditGenerator,
)

# Department 4: Security
from .spiffe_spire import SpiffeRegistrationEntry, SpiffeIdentityManifest, SpiffeSpireGenerator
from .dast_fuzzer import FuzzTestResult, DastAuditReport, DastCognitiveFuzzer
from .gost56939_audit import (
    FstecAssuranceLevel,
    SASTEvidenceRecord,
    BinaryHardeningEvidence,
    DASTFuzzingSummary,
    Gost56939Dossier,
    Gost56939Auditor,
)

# Department 5: Architecture
from .c4_dsl_exporter import C4DslExporter
from .self_rag import SelfRagSegment, SelfRagAnnotatedOutput, SelfRagEngine
from .persistent_saga import (
    SagaStepStatus,
    SagaStepRecord,
    OutboxEvent,
    SagaReplayReport,
    PersistentSagaEngine,
)

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
    "UXAutomationLevel",
    "DegradationTrigger",
    "DegradationTransition",
    "HITLHandoverDossier",
    "GracefulDegradationPlan",
    "UXFallbackEngine",
    # Department 2
    "FocusRecord",
    "FocusDataSet",
    "FinopsFocusExporter",
    "ModelTierSpec",
    "RoutingDecision",
    "CascadeSimulationReport",
    "ModelCascadeOptimizer",
    "AccountingPhase",
    "ExpenseItem",
    "CapitalizationChecklist",
    "AmortizationMonth",
    "IAS38AuditDossier",
    "IAS38Auditor",
    # Department 3
    "AiActDossierSection",
    "EuAiActTechnicalDossier",
    "EuAiActDossierGenerator",
    "SpdxPackageEntry",
    "SbomManifest",
    "SpdxLicenseGuard",
    "ControlStatus",
    "AnnexAControl",
    "AIRiskRecord",
    "AIImpactAssessment",
    "ISO42001AIMSReport",
    "ISO42001AuditGenerator",
    # Department 4
    "SpiffeRegistrationEntry",
    "SpiffeIdentityManifest",
    "SpiffeSpireGenerator",
    "FuzzTestResult",
    "DastAuditReport",
    "DastCognitiveFuzzer",
    "FstecAssuranceLevel",
    "SASTEvidenceRecord",
    "BinaryHardeningEvidence",
    "DASTFuzzingSummary",
    "Gost56939Dossier",
    "Gost56939Auditor",
    # Department 5
    "C4DslExporter",
    "SelfRagSegment",
    "SelfRagAnnotatedOutput",
    "SelfRagEngine",
    "SagaStepStatus",
    "SagaStepRecord",
    "OutboxEvent",
    "SagaReplayReport",
    "PersistentSagaEngine",
]
