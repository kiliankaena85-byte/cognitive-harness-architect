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
)
from .hardware import OpenVinoDmaOptimizer
from .quality import RagTriadEvaluator


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
    SERVER_VERSION = "2.2.0"
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

        self._tools: Dict[str, Tuple[McpToolDefinition, Callable[[Dict[str, Any]], Dict[str, Any]]]] = {}
        self._register_default_tools()

    def _register_default_tools(self) -> None:
        """Registers the 16 core architectural and engineering tools."""

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
