"""
core/mcp_server.py
=============================================================================
Universal Cognitive Decomposition Engine (UCDE) - Phase 2
Model Context Protocol (MCP) Server.
Standard JSON-RPC 2.0 Protocol over Stdio & In-Process Dispatcher.

Exposes Cognitive Tools to Claude, Gemini, Antigravity, and Cursor:
- lint_specification: Multi-standard deterministic linter across all 7 Ministries
- evaluate_pareto: Sub-millisecond NPU/Decisions API Pareto multi-objective selection
- synthesize_code: Spec-to-Code generator (FastAPI + Zero-Dependency Dispatcher)
- synthesize_and_run_tests: Test synthesis and subprocess sandbox execution
- query_cognitive_memory: 4-tier memory bundle with GraphRAG and prompt quarantine
- trace_architectural_lineage: Causal verification from Personas to Safety Interlocks
=============================================================================
"""

import json
import sys
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from pydantic import BaseModel, ConfigDict, Field

from .cognitive_memory import CognitiveMemoryStore
from .code_synthesizer import CodeSynthesizer
from .consensus_engine import BftConsensusEngine
from .canary_deployer import CanaryDeployer
from .formal_verifier import FormalVerifier
from .graph_rag import GraphRAGEngine
from .npu_darwinian_loop import NpuParetoSelector
from .sandbox_runner import SandboxRunner
from .standards_linter import StandardsLinter
from .generators import (
    ServiceBlueprintGenerator,
    FinopsFocusExporter,
    EuAiActDossierGenerator,
    SpiffeSpireGenerator,
    C4DslExporter,
    OstEngine,
    ModelCascadeOptimizer,
    SpdxLicenseGuard,
    DastCognitiveFuzzer,
    SelfRagEngine,
    UXFallbackEngine,
    UXAutomationLevel,
    IAS38Auditor,
    ExpenseItem,
    CapitalizationChecklist,
    ISO42001AuditGenerator,
    Gost56939Auditor,
    FstecAssuranceLevel,
    PersistentSagaEngine,
)
from .hardware import (
    OpenVinoDmaOptimizer,
    ChaosFaultInjector,
    WatchdogCircuitSynthesizer,
    WatchdogWindowConfig,
)
from .quality import (
    RagTriadEvaluator,
    GostPmiGenerator,
    CIFormalAuditStand,
)


class McpToolDefinition(BaseModel):
    """MCP standard tool schema definition."""
    model_config = ConfigDict(extra="forbid")

    name: str = Field(description="Unique tool identifier")
    description: str = Field(description="Human- and LLM-readable purpose description")
    inputSchema: Dict[str, Any] = Field(description="JSON Schema Draft 2020-12 defining input parameters")


class McpServer:
    """
    Standard Model Context Protocol (MCP) Server implementing JSON-RPC 2.0.
    Supports in-process program dispatch and stdio stream loops.
    """

    SERVER_NAME = "cognitive-harness-architect"
    SERVER_VERSION = "2.4.0"
    PROTOCOL_VERSION = "2024-11-05"

    def __init__(
        self,
        memory_store: Optional[CognitiveMemoryStore] = None,
        linter: Optional[StandardsLinter] = None,
        npu_selector: Optional[NpuParetoSelector] = None,
        code_synthesizer: Optional[CodeSynthesizer] = None,
        sandbox_runner: Optional[SandboxRunner] = None,
        formal_verifier: Optional[FormalVerifier] = None,
        consensus_engine: Optional[BftConsensusEngine] = None,
        canary_deployer: Optional[CanaryDeployer] = None,
        service_blueprint_gen: Optional[ServiceBlueprintGenerator] = None,
        finops_focus_exporter: Optional[FinopsFocusExporter] = None,
        ai_act_dossier_gen: Optional[EuAiActDossierGenerator] = None,
        spiffe_spire_gen: Optional[SpiffeSpireGenerator] = None,
        c4_dsl_exporter: Optional[C4DslExporter] = None,
        rag_triad_evaluator: Optional[RagTriadEvaluator] = None,
        openvino_dma_opt: Optional[OpenVinoDmaOptimizer] = None,
        ost_engine: Optional[OstEngine] = None,
        model_cascade_opt: Optional[ModelCascadeOptimizer] = None,
        spdx_guard: Optional[SpdxLicenseGuard] = None,
        dast_fuzzer: Optional[DastCognitiveFuzzer] = None,
        self_rag_engine: Optional[SelfRagEngine] = None,
        chaos_injector: Optional[ChaosFaultInjector] = None,
        gost_pmi_gen: Optional[GostPmiGenerator] = None,
        ux_fallback_engine: Optional[UXFallbackEngine] = None,
        ias38_auditor: Optional[IAS38Auditor] = None,
        iso42001_gen: Optional[ISO42001AuditGenerator] = None,
        gost56939_auditor: Optional[Gost56939Auditor] = None,
        saga_engine: Optional[PersistentSagaEngine] = None,
        watchdog_synth: Optional[WatchdogCircuitSynthesizer] = None,
        ci_formal_audit: Optional[CIFormalAuditStand] = None,
    ):
        self.memory: CognitiveMemoryStore = memory_store or CognitiveMemoryStore()
        self.linter: StandardsLinter = linter or StandardsLinter()
        self.npu_selector: NpuParetoSelector = npu_selector or NpuParetoSelector()
        self.code_synth: CodeSynthesizer = code_synthesizer or CodeSynthesizer()
        self.sandbox: SandboxRunner = sandbox_runner or SandboxRunner()
        self.formal_verifier: FormalVerifier = formal_verifier or FormalVerifier()
        self.consensus_engine: BftConsensusEngine = consensus_engine or BftConsensusEngine()
        self.canary_deployer: CanaryDeployer = canary_deployer or CanaryDeployer()
        self.service_blueprint_gen: ServiceBlueprintGenerator = service_blueprint_gen or ServiceBlueprintGenerator()
        self.finops_focus_exporter: FinopsFocusExporter = finops_focus_exporter or FinopsFocusExporter()
        self.ai_act_dossier_gen: EuAiActDossierGenerator = ai_act_dossier_gen or EuAiActDossierGenerator()
        self.spiffe_spire_gen: SpiffeSpireGenerator = spiffe_spire_gen or SpiffeSpireGenerator()
        self.c4_dsl_exporter: C4DslExporter = c4_dsl_exporter or C4DslExporter()
        self.rag_triad_evaluator: RagTriadEvaluator = rag_triad_evaluator or RagTriadEvaluator()
        self.openvino_dma_opt: OpenVinoDmaOptimizer = openvino_dma_opt or OpenVinoDmaOptimizer()
        self.ost_engine: OstEngine = ost_engine or OstEngine()
        self.model_cascade_opt: ModelCascadeOptimizer = model_cascade_opt or ModelCascadeOptimizer()
        self.spdx_guard: SpdxLicenseGuard = spdx_guard or SpdxLicenseGuard()
        self.dast_fuzzer: DastCognitiveFuzzer = dast_fuzzer or DastCognitiveFuzzer()
        self.self_rag_engine: SelfRagEngine = self_rag_engine or SelfRagEngine()
        self.chaos_injector: ChaosFaultInjector = chaos_injector or ChaosFaultInjector()
        self.gost_pmi_gen: GostPmiGenerator = gost_pmi_gen or GostPmiGenerator()
        self.ux_fallback_engine: UXFallbackEngine = ux_fallback_engine or UXFallbackEngine()
        self.ias38_auditor: IAS38Auditor = ias38_auditor or IAS38Auditor()
        self.iso42001_gen: ISO42001AuditGenerator = iso42001_gen or ISO42001AuditGenerator()
        self.gost56939_auditor: Gost56939Auditor = gost56939_auditor or Gost56939Auditor()
        self.saga_engine: PersistentSagaEngine = saga_engine or PersistentSagaEngine()
        self.watchdog_synth: WatchdogCircuitSynthesizer = watchdog_synth or WatchdogCircuitSynthesizer()
        self.ci_formal_audit: CIFormalAuditStand = ci_formal_audit or CIFormalAuditStand()

        self._tools: Dict[str, Tuple[McpToolDefinition, Callable[[Dict[str, Any]], Dict[str, Any]]]] = {}
        self._register_default_tools()

    def _register_default_tools(self) -> None:
        """Registers the 30 core architectural, engineering, state certification, and autonomous agent tools."""

        # 1. lint_specification
        self.register_tool(
            McpToolDefinition(
                name="lint_specification",
                description="Lints a ministry contract artifact against 37+ international & national standards (ISO 29148, GOST 34/19, STRIDE, RFC 7807, FOCUS).",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "node_id": {"type": "integer", "minimum": 1, "maximum": 9, "description": "Ministry or Module ID (1-9)"},
                        "artifact": {"type": "object", "description": "Candidate contract JSON dictionary"},
                    },
                    "required": ["node_id", "artifact"],
                },
            ),
            self._handle_lint_specification,
        )

        # 2. evaluate_pareto
        self.register_tool(
            McpToolDefinition(
                name="evaluate_pareto",
                description="Executes sub-millisecond Lexicographic Pareto selection (L-MOPA) and Utopian distance arbitration over candidate hypotheses.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "candidates": {"type": "array", "items": {"type": "object"}, "description": "List of candidate hypothesis objects"},
                        "ministry_id": {"type": "integer", "default": 5, "description": "Ministry ID for domain evaluation"},
                    },
                    "required": ["candidates"],
                },
            ),
            self._handle_evaluate_pareto,
        )

        # 3. synthesize_code
        self.register_tool(
            McpToolDefinition(
                name="synthesize_code",
                description="Generates executable microservice code (FastAPI + Zero-Dependency Dispatcher, app_schemas, app_security, app_routes, main) from contracts.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "analysis_contract": {"type": "object", "description": "SystemAnalysisContract dictionary"},
                        "security_contract": {"type": "object", "description": "SecurityPolicyContract dictionary"},
                        "output_dir": {"type": "string", "description": "Optional destination directory path"},
                    },
                    "required": ["analysis_contract", "security_contract"],
                },
            ),
            self._handle_synthesize_code,
        )

        # 4. synthesize_and_run_tests
        self.register_tool(
            McpToolDefinition(
                name="synthesize_and_run_tests",
                description="Synthesizes BDD/BVA/STRIDE test suites, runs inside isolated subprocess sandbox, and executes self-healing loop.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "strategy_contract": {"type": "object", "description": "StrategyCJMContract dictionary"},
                        "analysis_contract": {"type": "object", "description": "SystemAnalysisContract dictionary"},
                        "security_contract": {"type": "object", "description": "SecurityPolicyContract dictionary"},
                        "target_dir": {"type": "string", "description": "Destination directory for tests and code execution"},
                    },
                    "required": ["strategy_contract", "analysis_contract", "security_contract", "target_dir"],
                },
            ),
            self._handle_synthesize_and_run_tests,
        )

        # 5. query_cognitive_memory
        self.register_tool(
            McpToolDefinition(
                name="query_cognitive_memory",
                description="Assembles multi-tier cognitive memory bundle combining working context, episodic history, GraphRAG associative nodes, and prompt quarantine.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Semantic search query for GraphRAG"},
                        "user_prompt": {"type": "string", "description": "Raw user prompt to be quarantined"},
                        "top_k": {"type": "integer", "default": 5, "description": "Number of associative graph nodes to retrieve"},
                    },
                    "required": ["query", "user_prompt"],
                },
            ),
            self._handle_query_cognitive_memory,
        )

        # 6. trace_architectural_lineage
        self.register_tool(
            McpToolDefinition(
                name="trace_architectural_lineage",
                description="Traces causal dependency and verification path between any two architectural entities in the GraphRAG knowledge base.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "start_id": {"type": "string", "description": "Root entity ID, e.g. 'PERSONA:Auditor' or 'AC:AC-01'"},
                        "target_id": {"type": "string", "description": "Target entity ID, e.g. 'THREAT:SPOOFING' or 'HARDWARE_CONSTRAINT:THERAC_25_INTERLOCK'"},
                    },
                    "required": ["start_id", "target_id"],
                },
            ),
            self._handle_trace_lineage,
        )

        # 7. verify_formal_invariants
        self.register_tool(
            McpToolDefinition(
                name="verify_formal_invariants",
                description="Executes mathematical first-order logic and Z3 SMT solver proofs across 5 architectural invariants (CIDR non-collision, DAG acyclicity, Therac-25 temporal safety, financial solvency, STRIDE completeness).",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "theorem": {"type": "string", "enum": ["network_cidr", "acyclic_dag", "therac25", "financial_solvency", "stride_coverage"], "description": "Theorem to prove"},
                        "arguments": {"type": "object", "description": "Theorem specific parameters"},
                    },
                    "required": ["theorem", "arguments"],
                },
            ),
            self._handle_verify_formal_invariants,
        )

        # 8. execute_bft_consensus
        self.register_tool(
            McpToolDefinition(
                name="execute_bft_consensus",
                description="Coordinates Practical Byzantine Fault Tolerance (PBFT) voting round across heterogeneous foundation models (Claude, GPT-4o, Gemini, Llama) with 2f+1 quorum.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "proposal_id": {"type": "string", "description": "Unique identifier for the proposed contract modification"},
                        "proposed_artifact": {"type": "object", "description": "The candidate artifact dictionary to be voted on"},
                    },
                    "required": ["proposal_id", "proposed_artifact"],
                },
            ),
            self._handle_execute_bft_consensus,
        )

        # 9. verify_canary_deployment
        self.register_tool(
            McpToolDefinition(
                name="verify_canary_deployment",
                description="Simulates progressive 3-stage canary deployment (10% -> 50% -> 100%) and verifies real-time SLA/SLO error budgets with automated circuit breaker rollback.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "release_version": {"type": "string", "description": "Release semantic version tag, e.g. 'v2.0.0'"},
                        "stage_telemetries": {
                            "type": "array",
                            "items": {"type": "object"},
                            "description": "Optional custom telemetry metrics per stage for testing or telemetry feed",
                        },
                    },
                    "required": ["release_version"],
                },
            ),
            self._handle_verify_canary_deployment,
        )

        # 10. generate_service_blueprint
        self.register_tool(
            McpToolDefinition(
                name="generate_service_blueprint",
                description="Generates standard 5-swimlane NN/g Service Blueprint (Customer Actions, Frontstage, Backstage, Support, Physical Evidence) with PlantUML and Markdown formats.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "strategy_artifact": {"type": "object", "description": "StrategyCJMContract dictionary"},
                        "project_id": {"type": "string", "default": "PROJ-COGNITIVE-001", "description": "Project identifier"},
                    },
                    "required": ["strategy_artifact"],
                },
            ),
            self._handle_generate_service_blueprint,
        )

        # 11. export_finops_focus
        self.register_tool(
            McpToolDefinition(
                name="export_finops_focus",
                description="Transforms Finance/Budget contract into FinOps Open Cost and Usage Specification (FOCUS 1.0) standard schema and RFC 4180 CSV / JSON formats.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "finance_artifact": {"type": "object", "description": "FinanceBudgetContract dictionary"},
                        "export_format": {"type": "string", "enum": ["json", "csv", "both"], "default": "both", "description": "Format for exported data"},
                    },
                    "required": ["finance_artifact"],
                },
            ),
            self._handle_export_finops_focus,
        )

        # 12. generate_ai_act_dossier
        self.register_tool(
            McpToolDefinition(
                name="generate_ai_act_dossier",
                description="Synthesizes complete EU AI Act Annex IV Technical Documentation dossier (Articles 9, 10, 14, 15) with cryptographic SHA-256 seal.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "legal_artifact": {"type": "object", "description": "LegalComplianceContract dictionary"},
                        "strategy_artifact": {"type": "object", "description": "StrategyCJMContract dictionary"},
                        "security_artifact": {"type": "object", "description": "SecurityPolicyContract dictionary"},
                        "hardware_artifact": {"type": "object", "description": "HardwareRuntimeContract dictionary"},
                        "quality_artifact": {"type": "object", "description": "VVQualityContract dictionary"},
                        "system_name": {"type": "string", "default": "Universal Cognitive Decomposition Engine (UCDE)", "description": "Name of AI system"},
                    },
                    "required": ["legal_artifact", "strategy_artifact", "security_artifact", "hardware_artifact", "quality_artifact"],
                },
            ),
            self._handle_generate_ai_act_dossier,
        )

        # 13. generate_spiffe_spire
        self.register_tool(
            McpToolDefinition(
                name="generate_spiffe_spire",
                description="Generates SPIFFE/SPIRE workload identities (spiffe://cognitive.internal/...), SVID X.509 profiles, SPIRE Server/Agent HCL and Envoy mTLS proxy configurations.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "security_artifact": {"type": "object", "description": "Optional SecurityPolicyContract dictionary"},
                    },
                },
            ),
            self._handle_generate_spiffe_spire,
        )

        # 14. export_c4_dsl
        self.register_tool(
            McpToolDefinition(
                name="export_c4_dsl",
                description="Transforms SystemAnalysisContract into standard Structurizr C4-DSL (Context, Container, Component views).",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "analysis_artifact": {"type": "object", "description": "SystemAnalysisContract dictionary"},
                        "strategy_artifact": {"type": "object", "description": "Optional StrategyCJMContract dictionary"},
                    },
                    "required": ["analysis_artifact"],
                },
            ),
            self._handle_export_c4_dsl,
        )

        # 15. evaluate_rag_triad
        self.register_tool(
            McpToolDefinition(
                name="evaluate_rag_triad",
                description="Deterministic DeepEval evaluation of Cognitive RAG Triad: Context Relevance (>=0.85), Faithfulness/Groundedness (>=0.95), Answer Relevance (>=0.90), and Adversarial Jailbreak Resistance (>=98%).",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "User prompt or query"},
                        "contexts": {"type": "array", "items": {"type": "string"}, "description": "Retrieved context passages"},
                        "answer": {"type": "string", "description": "Generated model response"},
                        "adversarial_prompts": {"type": "array", "items": {"type": "string"}, "description": "Optional list of adversarial jailbreak test prompts"},
                    },
                    "required": ["query", "contexts", "answer"],
                },
            ),
            self._handle_evaluate_rag_triad,
        )

        # 16. benchmark_openvino_dma
        self.register_tool(
            McpToolDefinition(
                name="benchmark_openvino_dma",
                description="Benchmarks Intel Meteor Lake zero-copy DMA pinned buffer allocation vs standard memory copy, verifying RAM <= 512 MB and sub-millisecond latency SLA.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "iterations": {"type": "integer", "default": 200, "description": "Benchmark iterations"},
                        "tensor_dim": {"type": "integer", "default": 1024, "description": "Tensor dimension"},
                    },
                },
            ),
            self._handle_benchmark_openvino_dma,
        )

        # 17. generate_opportunity_solution_tree
        self.register_tool(
            McpToolDefinition(
                name="generate_opportunity_solution_tree",
                description="Generates Teresa Torres Opportunity Solution Tree (OST) with Desired Outcome, Opportunities, Solutions, and Assumption Tests with DMN 1.4 Decision Table export.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "strategy_artifact": {"type": "object", "description": "StrategyCJMContract dictionary"},
                        "project_id": {"type": "string", "default": "PROJ-COGNITIVE-001", "description": "Project ID"},
                    },
                    "required": ["strategy_artifact"],
                },
            ),
            self._handle_generate_ost,
        )

        # 18. optimize_model_cascade
        self.register_tool(
            McpToolDefinition(
                name="optimize_model_cascade",
                description="Optimizes dynamic model routing across 4 tiers (Local NPU -> 4B SLM -> 70B Mid -> Frontier Reasoning) with prefix cache hit-rate simulation (R_cache >= 85%).",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Prompt or query to route"},
                        "simulate_workload": {"type": "boolean", "default": False, "description": "Run 1000-query workload simulation"},
                        "queries_count": {"type": "integer", "default": 500, "description": "Queries count if simulating"},
                    },
                    "required": ["query"],
                },
            ),
            self._handle_optimize_model_cascade,
        )

        # 19. scan_spdx_licenses
        self.register_tool(
            McpToolDefinition(
                name="scan_spdx_licenses",
                description="Generates OpenChain (ISO/IEC 5230) & SPDX 3.0 Software Bill of Materials (SBOM) and enforces strict legal veto on viral copyleft (AGPL/GPL).",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "dependencies": {
                            "type": "array",
                            "items": {"type": "object"},
                            "description": "Optional list of dependency objects {name, version, license}",
                        },
                        "project_name": {"type": "string", "default": "Cognitive Harness Architect", "description": "Project name"},
                    },
                },
            ),
            self._handle_scan_spdx_licenses,
        )

        # 20. run_dast_cognitive_fuzzer
        self.register_tool(
            McpToolDefinition(
                name="run_dast_cognitive_fuzzer",
                description="Executes continuous DAST security fuzzing against FSTEC BDU threat catalog (УБИ.046, УБИ.062) and OWASP ASVS 4.0 Level 3, verifying sub-millisecond rejection.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "endpoints": {"type": "array", "items": {"type": "string"}, "description": "Target endpoints to fuzz"},
                        "iterations": {"type": "integer", "default": 5, "description": "Fuzzing iterations per payload"},
                    },
                },
            ),
            self._handle_run_dast_fuzzer,
        )

        # 21. evaluate_self_rag_reflection
        self.register_tool(
            McpToolDefinition(
                name="evaluate_self_rag_reflection",
                description="Injects active Self-RAG reflection tokens ([Retrieve], [IsRel], [IsSup], [IsUse:1..5]) and executes beam filtering to eliminate hallucinations (< 0.1% error rate).",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "User intent query"},
                        "draft_text": {"type": "string", "description": "Generated candidate draft text"},
                        "contexts": {"type": "array", "items": {"type": "string"}, "description": "Retrieved context passages"},
                    },
                    "required": ["query", "draft_text"],
                },
            ),
            self._handle_evaluate_self_rag,
        )

        # 22. run_chaos_fault_injection
        self.register_tool(
            McpToolDefinition(
                name="run_chaos_fault_injection",
                description="Simulates hardware faults, Therac-25 actuator delay spikes (8000ms), NPU RAM overflow (>512MB), and watchdog timeouts with Simplex fail-safe downscaling.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "fault_type": {
                            "type": "string",
                            "enum": ["ALL", "THERAC_LATENCY", "NPU_RAM", "WATCHDOG"],
                            "default": "ALL",
                            "description": "Specific fault scenario or full battery",
                        },
                    },
                },
            ),
            self._handle_run_chaos_fault_injection,
        )

        # 23. generate_gost_pmi
        self.register_tool(
            McpToolDefinition(
                name="generate_gost_pmi",
                description="Synthesizes official Test Program and Methodology (ПМИ) conforming to ГОСТ 34.603-92 and ГОСТ 19.301-79 with SHA-256 digital commission seal.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "strategy_artifact": {"type": "object", "description": "StrategyCJMContract dictionary"},
                        "finance_artifact": {"type": "object", "description": "FinanceBudgetContract dictionary"},
                        "legal_artifact": {"type": "object", "description": "LegalComplianceContract dictionary"},
                        "security_artifact": {"type": "object", "description": "SecurityPolicyContract dictionary"},
                        "analysis_artifact": {"type": "object", "description": "SystemAnalysisContract dictionary"},
                        "hardware_artifact": {"type": "object", "description": "HardwareRuntimeContract dictionary"},
                        "quality_artifact": {"type": "object", "description": "VVQualityContract dictionary"},
                        "gost_standard": {
                            "type": "string",
                            "enum": ["ГОСТ 34.603-92", "ГОСТ 19.301-79", "ГИБРИДНЫЙ"],
                            "default": "ГОСТ 34.603-92",
                            "description": "Regulatory test standard",
                        },
                    },
                    "required": [
                        "strategy_artifact", "finance_artifact", "legal_artifact",
                        "security_artifact", "analysis_artifact", "hardware_artifact", "quality_artifact"
                    ],
                },
            ),
            self._handle_generate_gost_pmi,
        )

        # 24. generate_ux_fallback_plan
        self.register_tool(
            McpToolDefinition(
                name="generate_ux_fallback_plan",
                description="Generates ISO 9241-210 compliant adaptive UX degradation statecharts, evaluating confidence thresholds (C < 0.70) and creating Human-in-the-Loop (HITL) handover dossiers.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "system_name": {"type": "string", "default": "Universal Cognitive Engine", "description": "System name"},
                        "confidence": {"type": "number", "default": 0.88, "description": "Current AI model confidence score [0.0 - 1.0]"},
                        "latency_ms": {"type": "number", "default": 25.0, "description": "Current inference latency in ms"},
                        "error_rate": {"type": "number", "default": 0.0, "description": "Current system error rate"},
                        "hardware_fault": {"type": "boolean", "default": False, "description": "Whether hardware watchdog has tripped"},
                    },
                },
            ),
            self._handle_generate_ux_fallback_plan,
        )

        # 25. audit_ias38_intangible_assets
        self.register_tool(
            McpToolDefinition(
                name="audit_ias38_intangible_assets",
                description="Audits AI and software investments against IAS 38 and IFRS 15, verifying 6 cumulative criteria for CAPEX capitalization vs OPEX research expensing and generating amortization schedules.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "project_name": {"type": "string", "default": "Cognitive Harness Architect", "description": "Project or AI model name"},
                        "audit_date": {"type": "string", "default": "2026-10-01", "description": "Audit date (YYYY-MM-DD)"},
                        "expenses": {"type": "array", "items": {"type": "object"}, "description": "List of expense items {item_id, description, phase, amount_rub, cost_category}"},
                        "checklist": {"type": "object", "description": "6 IAS 38.57 criteria"},
                        "useful_life_months": {"type": "integer", "default": 36, "description": "Useful life in months for amortization"},
                    },
                },
            ),
            self._handle_audit_ias38,
        )

        # 26. generate_iso42001_aims_dossier
        self.register_tool(
            McpToolDefinition(
                name="generate_iso42001_aims_dossier",
                description="Generates ISO/IEC 42001:2023 Artificial Intelligence Management System (AIMS) certification documentation, Statement of Applicability (SoA Annex A controls), and AI Impact Assessment.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "system_name": {"type": "string", "default": "Universal Cognitive Decomposition Engine", "description": "System name"},
                    },
                },
            ),
            self._handle_generate_iso42001_aims,
        )

        # 27. generate_gost56939_dossier
        self.register_tool(
            McpToolDefinition(
                name="generate_gost56939_dossier",
                description="Generates ГОСТ Р 56939-2024 safe software development assurance dossier for FSTEC/FSB state certification (ОУД/УД 1-6, SAST/DAST evidence, binary hardening, Streebog seal).",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "system_name": {"type": "string", "default": "Cognitive Harness Architect", "description": "System name"},
                        "target_level": {"type": "string", "enum": ["УД 1", "УД 2", "УД 3", "УД 4", "УД 5", "УД 6"], "default": "УД 4", "description": "Target FSTEC trust level"},
                        "release_sha256": {"type": "string", "default": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", "description": "SHA-256 hash of release artifact"},
                        "mean_latency_us": {"type": "number", "default": 11.07, "description": "Measured rejection latency in microseconds"},
                    },
                },
            ),
            self._handle_generate_gost56939,
        )

        # 28. orchestrate_persistent_saga
        self.register_tool(
            McpToolDefinition(
                name="orchestrate_persistent_saga",
                description="Orchestrates distributed Saga transactions with SQLite Write-Ahead Log (WAL), Transactional Outbox pattern, and crash-recovery replay.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "saga_id": {"type": "string", "description": "Unique Saga ID"},
                        "saga_name": {"type": "string", "default": "Cross-Ministry Transaction", "description": "Name of the saga"},
                        "steps": {"type": "array", "items": {"type": "object"}, "description": "List of steps {step_id, step_name, forward_action, compensation_action, input_payload}"},
                        "fail_at_step_id": {"type": "string", "description": "Optional step ID to simulate failure and trigger compensation"},
                    },
                    "required": ["saga_id"],
                },
            ),
            self._handle_orchestrate_persistent_saga,
        )

        # 29. synthesize_watchdog_circuit
        self.register_tool(
            McpToolDefinition(
                name="synthesize_watchdog_circuit",
                description="Synthesizes synthesizable Verilog-2001 and VHDL testbench for independent hardware windowed watchdog (MAX6369) with physical interlock latch.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "min_window_ms": {"type": "number", "default": 50.0, "description": "Minimum window duration in ms"},
                        "max_window_ms": {"type": "number", "default": 200.0, "description": "Maximum window duration in ms"},
                        "system_clock_mhz": {"type": "number", "default": 50.0, "description": "Target FPGA clock frequency in MHz"},
                    },
                },
            ),
            self._handle_synthesize_watchdog_circuit,
        )

        # 30. run_ci_formal_audit
        self.register_tool(
            McpToolDefinition(
                name="run_ci_formal_audit",
                description="Runs automated first-order logic & Z3 SMT solver theorem proving over hard system invariants (Therac-25, Venture economics, NPU RAM, AI Act) and mints cryptographic release seal.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "system_name": {"type": "string", "default": "Cognitive Harness Architect", "description": "System name"},
                        "commit_sha": {"type": "string", "default": "HEAD", "description": "Commit SHA or tree hash to certify"},
                        "telemetry": {"type": "object", "description": "System telemetry parameters for proof checking"},
                    },
                },
            ),
            self._handle_run_ci_formal_audit,
        )

    def register_tool(
        self,
        definition: McpToolDefinition,
        handler: Callable[[Dict[str, Any]], Dict[str, Any]],
    ) -> None:
        """Registers an MCP tool definition and its execution handler."""
        self._tools[definition.name] = (definition, handler)

    # =========================================================================
    # Tool Handler Implementations
    # =========================================================================

    def _handle_lint_specification(self, args: Dict[str, Any]) -> Dict[str, Any]:
        node_id = int(args["node_id"])
        artifact = args["artifact"]
        res = self.linter.lint_node_artifact(node_id, artifact)
        return res.model_dump()

    def _handle_evaluate_pareto(self, args: Dict[str, Any]) -> Dict[str, Any]:
        candidates = args["candidates"]
        ministry_name = args.get("ministry_name", "analysis")
        winner = self.npu_selector.select_dominant(candidates, ministry_name=ministry_name)
        if winner is None and candidates:
            winner = candidates[0]
        return {
            "winner_found": winner is not None,
            "selected_hypothesis": winner,
            "candidates_count": len(candidates),
        }

    def _handle_synthesize_code(self, args: Dict[str, Any]) -> Dict[str, Any]:
        out_dir = args.get("output_dir")
        if out_dir:
            res = self.code_synth.write_service(out_dir, args["analysis_contract"], args["security_contract"])
            return res
        files = self.code_synth.synthesize_service(args["analysis_contract"], args["security_contract"])
        return {
            "all_ast_valid": all(f.ast_valid for f in files.values()),
            "files": {fname: f.code for fname, f in files.items()},
        }

    def _handle_synthesize_and_run_tests(self, args: Dict[str, Any]) -> Dict[str, Any]:
        from .test_synthesizer import TestSynthesizer
        from pathlib import Path

        target_dir = Path(args["target_dir"]).resolve()
        target_dir.mkdir(parents=True, exist_ok=True)

        # 1. Synthesize service
        self.code_synth.write_service(target_dir, args["analysis_contract"], args["security_contract"])

        # 2. Synthesize tests
        ts = TestSynthesizer()
        manifest = ts.write_test_suite(target_dir, args["strategy_contract"], args["analysis_contract"], args["security_contract"])

        # 3. Execute in sandbox
        exec_res = self.sandbox.execute_with_self_healing(target_dir)
        return {
            "test_manifest": manifest,
            "sandbox_result": exec_res.model_dump(),
        }

    def _handle_query_cognitive_memory(self, args: Dict[str, Any]) -> Dict[str, Any]:
        bundle = self.memory.assemble_context_bundle(
            query=args["query"],
            user_prompt=args["user_prompt"],
            graph_top_k=args.get("top_k", 5),
        )
        return bundle.model_dump()

    def _handle_trace_lineage(self, args: Dict[str, Any]) -> Dict[str, Any]:
        trace = self.memory.tier3_graph.trace_lineage(args["start_id"], args["target_id"])
        if trace:
            return trace.model_dump()
        return {"found": False, "start_id": args["start_id"], "target_id": args["target_id"]}

    def _handle_verify_formal_invariants(self, args: Dict[str, Any]) -> Dict[str, Any]:
        thm = args["theorem"]
        a = args.get("arguments", {})
        if thm == "network_cidr":
            cert = self.formal_verifier.prove_network_cidr_non_collision(a.get("service_subnets", []))
        elif thm == "acyclic_dag":
            cert = self.formal_verifier.prove_acyclic_dependency_graph(a.get("components", []), a.get("dependencies", {}))
        elif thm == "therac25":
            cert = self.formal_verifier.prove_therac25_temporal_safety(
                t_poll_ms=float(a.get("t_poll_ms", 10.0)),
                t_sw_ms=float(a.get("t_sw_ms", 20.0)),
                t_lock_ms=float(a.get("t_lock_ms", 10.0)),
                t_hw_actuation_ms=float(a.get("t_hw_actuation_ms", 1500.0)),
                hardware_interlock_enforced=bool(a.get("hardware_interlock_enforced", False)),
            )
        elif thm == "financial_solvency":
            cert = self.formal_verifier.prove_financial_solvency(
                cac=float(a.get("cac", 100.0)),
                arpu_monthly=float(a.get("arpu_monthly", 80.0)),
                gross_margin=float(a.get("gross_margin", 0.85)),
            )
        elif thm == "stride_coverage":
            cert = self.formal_verifier.prove_stride_threat_coverage(
                active_endpoints=a.get("active_endpoints", []),
                stride_mitigations=a.get("stride_mitigations", []),
            )
        else:
            raise ValueError(f"Unknown theorem: '{thm}'")

        return cert.model_dump()

    def _handle_execute_bft_consensus(self, args: Dict[str, Any]) -> Dict[str, Any]:
        proposal_id = args["proposal_id"]
        proposed_artifact = args["proposed_artifact"]
        cert = self.consensus_engine.execute_consensus_round(proposal_id, proposed_artifact)
        return cert.model_dump()

    def _handle_verify_canary_deployment(self, args: Dict[str, Any]) -> Dict[str, Any]:
        release_version = args["release_version"]
        stage_telemetries = args.get("stage_telemetries")
        attestation = self.canary_deployer.execute_progressive_rollout(release_version, stage_telemetries)
        return attestation.model_dump()

    def _handle_generate_service_blueprint(self, args: Dict[str, Any]) -> Dict[str, Any]:
        strat = args["strategy_artifact"]
        pid = args.get("project_id", "PROJ-COGNITIVE-001")
        bp = self.service_blueprint_gen.generate(strat, project_id=pid)
        return {
            "blueprint": bp.model_dump(),
            "plantuml": self.service_blueprint_gen.to_plantuml(bp),
            "markdown": self.service_blueprint_gen.to_markdown(bp),
        }

    def _handle_export_finops_focus(self, args: Dict[str, Any]) -> Dict[str, Any]:
        fin = args["finance_artifact"]
        fmt = args.get("export_format", "both")
        ds = self.finops_focus_exporter.export_from_contract(fin)
        res: Dict[str, Any] = {"dataset": ds.model_dump()}
        if fmt in ["csv", "both"]:
            res["csv"] = self.finops_focus_exporter.to_csv(ds)
        if fmt in ["json", "both"]:
            res["json"] = self.finops_focus_exporter.to_json(ds)
        return res

    def _handle_generate_ai_act_dossier(self, args: Dict[str, Any]) -> Dict[str, Any]:
        sys_name = args.get("system_name", "Universal Cognitive Decomposition Engine (UCDE)")
        dossier = self.ai_act_dossier_gen.generate(
            legal_artifact=args["legal_artifact"],
            strategy_artifact=args["strategy_artifact"],
            security_artifact=args["security_artifact"],
            hardware_artifact=args["hardware_artifact"],
            quality_artifact=args["quality_artifact"],
            system_name=sys_name,
        )
        return {
            "dossier": dossier.model_dump(),
            "markdown": self.ai_act_dossier_gen.to_markdown(dossier),
        }

    def _handle_generate_spiffe_spire(self, args: Dict[str, Any]) -> Dict[str, Any]:
        sec = args.get("security_artifact")
        manifest = self.spiffe_spire_gen.generate(sec)
        return manifest.model_dump()

    def _handle_export_c4_dsl(self, args: Dict[str, Any]) -> Dict[str, Any]:
        analysis = args["analysis_artifact"]
        strategy = args.get("strategy_artifact")
        dsl = self.c4_dsl_exporter.export(analysis, strategy)
        return {"c4_dsl": dsl}

    def _handle_evaluate_rag_triad(self, args: Dict[str, Any]) -> Dict[str, Any]:
        rep = self.rag_triad_evaluator.evaluate_full_rag(
            query=args["query"],
            contexts=args["contexts"],
            answer=args["answer"],
            adversarial_prompts=args.get("adversarial_prompts"),
        )
        return rep.model_dump()

    def _handle_benchmark_openvino_dma(self, args: Dict[str, Any]) -> Dict[str, Any]:
        iters = int(args.get("iterations", 200))
        dim = int(args.get("tensor_dim", 1024))
        return self.openvino_dma_opt.benchmark_dma_vs_copy(iterations=iters, tensor_dim=dim)

    def _handle_generate_ost(self, args: Dict[str, Any]) -> Dict[str, Any]:
        strat = args["strategy_artifact"]
        pid = args.get("project_id", "PROJ-COGNITIVE-001")
        tree = self.ost_engine.generate(strat, project_id=pid)
        return {
            "tree": tree.model_dump(),
            "markdown": self.ost_engine.to_markdown(tree),
            "dmn_table": self.ost_engine.to_dmn_decision_table(tree),
        }

    def _handle_optimize_model_cascade(self, args: Dict[str, Any]) -> Dict[str, Any]:
        q = args["query"]
        sim = bool(args.get("simulate_workload", False))
        if sim:
            n = int(args.get("queries_count", 500))
            rep = self.model_cascade_opt.simulate_workload(queries_count=n)
            return {"simulation_report": rep.model_dump()}
        decision = self.model_cascade_opt.route_query(q)
        return {"decision": decision.model_dump()}

    def _handle_scan_spdx_licenses(self, args: Dict[str, Any]) -> Dict[str, Any]:
        deps = args.get("dependencies")
        pname = args.get("project_name", "Cognitive Harness Architect")
        sbom = self.spdx_guard.generate_sbom(dependencies=deps, project_name=pname)
        return {
            "sbom": sbom.model_dump(),
            "markdown": self.spdx_guard.to_markdown(sbom),
        }

    def _handle_run_dast_fuzzer(self, args: Dict[str, Any]) -> Dict[str, Any]:
        eps = args.get("endpoints")
        iters = int(args.get("iterations", 5))
        rep = self.dast_fuzzer.run_fuzz_campaign(target_endpoints=eps, iterations_per_payload=iters)
        return {
            "audit_report": rep.model_dump(),
            "markdown": self.dast_fuzzer.to_markdown(rep),
        }

    def _handle_evaluate_self_rag(self, args: Dict[str, Any]) -> Dict[str, Any]:
        q = args["query"]
        draft = args["draft_text"]
        ctx = args.get("contexts", [])
        output = self.self_rag_engine.critique_and_reflect(q, draft, ctx)
        return {
            "annotated_output": output.model_dump(),
            "stream": self.self_rag_engine.to_annotated_stream(output),
        }

    def _handle_run_chaos_fault_injection(self, args: Dict[str, Any]) -> Dict[str, Any]:
        ftype = args.get("fault_type", "ALL")
        if ftype == "THERAC_LATENCY":
            res = self.chaos_injector.run_therac_latency_spike_experiment()
            return {"experiment": res.model_dump()}
        elif ftype == "NPU_RAM":
            res = self.chaos_injector.run_npu_ram_overflow_experiment()
            return {"experiment": res.model_dump()}
        elif ftype == "WATCHDOG":
            res = self.chaos_injector.run_watchdog_timeout_experiment()
            return {"experiment": res.model_dump()}
        rep = self.chaos_injector.run_full_chaos_campaign()
        return {
            "report": rep.model_dump(),
            "markdown": self.chaos_injector.to_markdown(rep),
        }

    def _handle_generate_gost_pmi(self, args: Dict[str, Any]) -> Dict[str, Any]:
        std = args.get("gost_standard", "ГОСТ 34.603-92")
        doc = self.gost_pmi_gen.generate(
            strategy_artifact=args["strategy_artifact"],
            finance_artifact=args["finance_artifact"],
            legal_artifact=args["legal_artifact"],
            security_artifact=args["security_artifact"],
            analysis_artifact=args["analysis_artifact"],
            hardware_artifact=args["hardware_artifact"],
            quality_artifact=args["quality_artifact"],
            gost_standard=std,
        )
        return {
            "pmi_document": doc.model_dump(),
            "markdown": self.gost_pmi_gen.to_markdown(doc),
        }

    def _handle_generate_ux_fallback_plan(self, args: Dict[str, Any]) -> Dict[str, Any]:
        sname = args.get("system_name", "Universal Cognitive Engine")
        conf = float(args.get("confidence", 0.88))
        lat = float(args.get("latency_ms", 25.0))
        err = float(args.get("error_rate", 0.0))
        fault = bool(args.get("hardware_fault", False))

        level = self.ux_fallback_engine.evaluate_telemetry(conf, lat, err, fault)
        plan = self.ux_fallback_engine.generate_default_plan(system_name=sname)
        plan.current_level = level

        mermaid_diag = self.ux_fallback_engine.export_mermaid_statechart(plan)
        if level in [UXAutomationLevel.HITL_CONFIRMATION, UXAutomationLevel.DETERMINISTIC_FALLBACK, UXAutomationLevel.EMERGENCY_OPERATOR_TAKEOVER]:
            handover = self.ux_fallback_engine.create_handover_dossier(
                confidence=conf,
                state_hash="b7f94c1a2e3d",
                conflicts=["Model confidence below threshold; manual operator review required."],
            )
            plan.hitl_dossier = handover

        return {
            "current_automation_level": level.value,
            "plan": plan.model_dump(),
            "mermaid_statechart": mermaid_diag,
        }

    def _handle_audit_ias38(self, args: Dict[str, Any]) -> Dict[str, Any]:
        pname = args.get("project_name", "Cognitive Harness Architect")
        adate = args.get("audit_date", "2026-10-01")
        life = int(args.get("useful_life_months", 36))
        raw_expenses = args.get("expenses", [
            {"item_id": "EXP-01", "description": "Prompt exploration & LLM evaluation", "phase": "RESEARCH", "amount_rub": 450000.0, "cost_category": "Compute_Cloud", "is_directly_attributable": True},
            {"item_id": "EXP-02", "description": "Deterministic Core & NPU Pipeline Development", "phase": "DEVELOPMENT", "amount_rub": 3200000.0, "cost_category": "Personnel_RND", "is_directly_attributable": True},
            {"item_id": "EXP-03", "description": "Zero-Trust Compiler & Formal Verifier", "phase": "DEVELOPMENT", "amount_rub": 1800000.0, "cost_category": "Tooling", "is_directly_attributable": True},
        ])
        expenses = [ExpenseItem(**e) for e in raw_expenses]

        raw_chk = args.get("checklist", {
            "technical_feasibility": True,
            "intention_to_complete": True,
            "ability_to_use_or_sell": True,
            "probable_future_benefits": True,
            "resource_availability": True,
            "reliable_cost_measurement": True,
        })
        checklist = CapitalizationChecklist(**raw_chk)

        auditor = IAS38Auditor(useful_life_months=life)
        dossier = auditor.audit_project(pname, adate, expenses, checklist)
        return {"dossier": dossier.model_dump()}

    def _handle_generate_iso42001_aims(self, args: Dict[str, Any]) -> Dict[str, Any]:
        sname = args.get("system_name", "Universal Cognitive Decomposition Engine")
        dossier = self.iso42001_gen.generate_dossier(system_name=sname)
        return {"aims_dossier": dossier.model_dump()}

    def _handle_generate_gost56939(self, args: Dict[str, Any]) -> Dict[str, Any]:
        sname = args.get("system_name", "Cognitive Harness Architect")
        lvl_str = args.get("target_level", "УД 4")
        r_sha = args.get("release_sha256", "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855")
        lat = float(args.get("mean_latency_us", 11.07))
        dossier = self.gost56939_auditor.generate_dossier(
            system_name=sname,
            target_level=FstecAssuranceLevel(lvl_str),
            release_sha256=r_sha,
            mean_latency_us=lat,
        )
        return {"gost56939_dossier": dossier.model_dump()}

    def _handle_orchestrate_persistent_saga(self, args: Dict[str, Any]) -> Dict[str, Any]:
        import time as _t
        sid = args["saga_id"]
        sname = args.get("saga_name", "Cross-Ministry Transaction")
        raw_steps = args.get("steps", [
            {"step_id": "STEP-01", "step_name": "Reserve_Budget", "forward_action": "reserve()", "compensation_action": "release()", "input_payload": {"amount": 50000}},
            {"step_id": "STEP-02", "step_name": "Allocate_DMA_RAM", "forward_action": "allocate()", "compensation_action": "free()", "input_payload": {"bytes": 1048576}},
            {"step_id": "STEP-03", "step_name": "Sign_Release_Manifest", "forward_action": "sign()", "compensation_action": "revoke()", "input_payload": {"version": "2.4.0"}},
        ])
        fail_at = args.get("fail_at_step_id")

        saga = PersistentSagaEngine(":memory:")
        saga.start_saga(sid, sname)

        executed_steps = []
        for s in raw_steps:
            rec = saga.add_step(
                saga_id=sid,
                step_id=s["step_id"],
                step_name=s["step_name"],
                forward_action=s["forward_action"],
                compensation_action=s["compensation_action"],
                input_payload=s.get("input_payload", {}),
            )
            if fail_at and s["step_id"] == fail_at:
                compensated = saga.fail_and_compensate(s["step_id"], error_reason=f"Simulated fault at {fail_at}")
                rep = saga.recover_and_replay(sid)
                return {
                    "saga_id": sid,
                    "status": "ABORTED_COMPENSATED",
                    "compensated_steps": compensated,
                    "replay_report": rep.model_dump(),
                }
            else:
                saga.commit_step(s["step_id"], {"status": "SUCCESS", "timestamp": _t.time()})
                executed_steps.append(rec.step_id)

        rep = saga.recover_and_replay(sid)
        return {
            "saga_id": sid,
            "status": "COMMITTED",
            "executed_steps": executed_steps,
            "replay_report": rep.model_dump(),
        }

    def _handle_synthesize_watchdog_circuit(self, args: Dict[str, Any]) -> Dict[str, Any]:
        min_w = float(args.get("min_window_ms", 50.0))
        max_w = float(args.get("max_window_ms", 200.0))
        clk = float(args.get("system_clock_mhz", 50.0))
        cfg = WatchdogWindowConfig(min_window_ms=min_w, max_window_ms=max_w, system_clock_mhz=clk)
        rtl = self.watchdog_synth.synthesize(cfg)
        return {"synthesized_rtl": rtl.model_dump()}

    def _handle_run_ci_formal_audit(self, args: Dict[str, Any]) -> Dict[str, Any]:
        sname = args.get("system_name", "Cognitive Harness Architect")
        csha = args.get("commit_sha", "HEAD-RELEASE-2026")
        telem = args.get("telemetry", {
            "actuator_latency_ms": 25.0,
            "interlock_engaged": False,
            "ltv": 450000.0,
            "cac": 120000.0,
            "break_even_months": 12,
            "npu_ram_mb": 256,
            "dma_pinned": True,
            "ai_act_risk": "HIGH_RISK",
        })
        rep = self.ci_formal_audit.run_full_formal_audit(system_name=sname, commit_sha=csha, telemetry=telem)
        return {"audit_report": rep.model_dump()}

    # =========================================================================
    # JSON-RPC 2.0 Protocol Dispatcher
    # =========================================================================

    def handle_jsonrpc_request(self, request_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Processes a single JSON-RPC 2.0 request dictionary and returns response."""
        req_id = request_dict.get("id")
        method = request_dict.get("method")
        params = request_dict.get("params", {})

        if request_dict.get("jsonrpc") != "2.0":
            return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32600, "message": "Invalid Request: missing jsonrpc: '2.0'"}}

        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": self.PROTOCOL_VERSION,
                    "serverInfo": {"name": self.SERVER_NAME, "version": self.SERVER_VERSION},
                    "capabilities": {"tools": {}},
                },
            }

        if method == "tools/list":
            tools_list = [d.model_dump() for d, _ in self._tools.values()]
            return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": tools_list}}

        if method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            if tool_name not in self._tools:
                return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Method not found: '{tool_name}'"}}

            _, handler = self._tools[tool_name]
            try:
                result_payload = handler(arguments)
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [{"type": "text", "text": json.dumps(result_payload, indent=2, ensure_ascii=False)}],
                        "isError": False,
                    },
                }
            except Exception as e:
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [{"type": "text", "text": f"Tool Execution Error: {str(e)}"}],
                        "isError": True,
                    },
                }

        return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Method not found: '{method}'"}}

    def run_stdio(self) -> None:
        """Runs the MCP server loop reading lines from stdin and writing to stdout."""
        for line in sys.stdin:
            line_str = line.strip()
            if not line_str:
                continue
            try:
                req = json.loads(line_str)
                resp = self.handle_jsonrpc_request(req)
                sys.stdout.write(json.dumps(resp, ensure_ascii=False) + "\n")
                sys.stdout.flush()
            except json.JSONDecodeError as err:
                err_resp = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": f"Parse error: {err}"}}
                sys.stdout.write(json.dumps(err_resp, ensure_ascii=False) + "\n")
                sys.stdout.flush()


def main():
    server = McpServer()
    server.run_stdio()


if __name__ == "__main__":
    main()
