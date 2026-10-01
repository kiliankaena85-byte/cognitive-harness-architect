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
from typing import Any, Callable, Dict, List, Optional, Union
from pydantic import BaseModel, ConfigDict, Field

from .cognitive_memory import CognitiveMemoryStore
from .code_synthesizer import CodeSynthesizer
from .formal_verifier import FormalVerifier
from .graph_rag import GraphRAGEngine
from .npu_darwinian_loop import NpuParetoSelector
from .sandbox_runner import SandboxRunner
from .standards_linter import StandardsLinter


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
    SERVER_VERSION = "1.5.0"
    PROTOCOL_VERSION = "2024-11-05"

    def __init__(
        self,
        memory_store: Optional[CognitiveMemoryStore] = None,
        linter: Optional[StandardsLinter] = None,
        npu_selector: Optional[NpuParetoSelector] = None,
        code_synthesizer: Optional[CodeSynthesizer] = None,
        sandbox_runner: Optional[SandboxRunner] = None,
        formal_verifier: Optional[FormalVerifier] = None,
    ):
        self.memory: CognitiveMemoryStore = memory_store or CognitiveMemoryStore()
        self.linter: StandardsLinter = linter or StandardsLinter()
        self.npu_selector: NpuParetoSelector = npu_selector or NpuParetoSelector()
        self.code_synth: CodeSynthesizer = code_synthesizer or CodeSynthesizer()
        self.sandbox: SandboxRunner = sandbox_runner or SandboxRunner()
        self.formal_verifier: FormalVerifier = formal_verifier or FormalVerifier()

        self._tools: Dict[str, Tuple[McpToolDefinition, Callable[[Dict[str, Any]], Dict[str, Any]]]] = {}
        self._register_default_tools()

    def _register_default_tools(self) -> None:
        """Registers the 6 core architectural tools."""

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
