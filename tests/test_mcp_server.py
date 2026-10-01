"""
tests/test_mcp_server.py
=============================================================================
Unit Test Suite for Model Context Protocol (MCP) Server.
Phase 2 - Universal Cognitive Decomposition Engine (UCDE)
=============================================================================
"""

import json
import unittest
from core.mcp_server import McpServer


class TestMcpServer(unittest.TestCase):
    def setUp(self):
        self.server = McpServer()

    def test_jsonrpc_initialize(self):
        req = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {"clientInfo": {"name": "TestClient", "version": "1.0.0"}},
        }
        resp = self.server.handle_jsonrpc_request(req)
        self.assertEqual(resp["jsonrpc"], "2.0")
        self.assertEqual(resp["id"], 1)
        res = resp["result"]
        self.assertEqual(res["serverInfo"]["name"], "cognitive-harness-architect")
        self.assertEqual(res["serverInfo"]["version"], "1.3.0")
        self.assertIn("tools", res["capabilities"])

    def test_jsonrpc_tools_list(self):
        req = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {},
        }
        resp = self.server.handle_jsonrpc_request(req)
        tools = resp["result"]["tools"]
        tool_names = [t["name"] for t in tools]
        self.assertIn("lint_specification", tool_names)
        self.assertIn("evaluate_pareto", tool_names)
        self.assertIn("synthesize_code", tool_names)
        self.assertIn("synthesize_and_run_tests", tool_names)
        self.assertIn("query_cognitive_memory", tool_names)
        self.assertIn("trace_architectural_lineage", tool_names)

    def test_jsonrpc_tool_call_lint_specification(self):
        req = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "lint_specification",
                "arguments": {
                    "node_id": 8,
                    "artifact": {"all_ast_valid": True, "files": {"main.py": "from app_schemas import ProblemDetails\n..."}},
                },
            },
        }
        resp = self.server.handle_jsonrpc_request(req)
        self.assertFalse(resp["result"]["isError"])
        content_text = resp["result"]["content"][0]["text"]
        payload = json.loads(content_text)
        self.assertTrue(payload["is_compliant"])
        self.assertIn("SPEC_TO_CODE_SYNTAX", payload["checked_standards"])

    def test_jsonrpc_tool_call_query_cognitive_memory(self):
        req = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "query_cognitive_memory",
                "arguments": {
                    "query": "Zero Trust token auth",
                    "user_prompt": "Please build a secure API",
                },
            },
        }
        resp = self.server.handle_jsonrpc_request(req)
        self.assertFalse(resp["result"]["isError"])
        content_text = resp["result"]["content"][0]["text"]
        payload = json.loads(content_text)
        self.assertIn("tier4_grounding_rules", payload)
        self.assertTrue(payload["quarantined_user_prompt"].startswith("<user_brief_quarantine>"))

    def test_jsonrpc_tool_call_evaluate_pareto(self):
        req = {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {
                "name": "evaluate_pareto",
                "arguments": {
                    "candidates": [
                        {"candidate_id": "cand_1", "hypothesis_name": "balanced", "payload": {}},
                        {"candidate_id": "cand_2", "hypothesis_name": "high_throughput", "payload": {}},
                    ]
                },
            },
        }
        resp = self.server.handle_jsonrpc_request(req)
        self.assertFalse(resp["result"]["isError"])
        payload = json.loads(resp["result"]["content"][0]["text"])
        self.assertTrue(payload["winner_found"])
        self.assertEqual(payload["candidates_count"], 2)

    def test_jsonrpc_invalid_method(self):
        req = {
            "jsonrpc": "2.0",
            "id": 99,
            "method": "non_existent_method",
            "params": {},
        }
        resp = self.server.handle_jsonrpc_request(req)
        self.assertIn("error", resp)
        self.assertEqual(resp["error"]["code"], -32601)

    def test_jsonrpc_unknown_tool(self):
        req = {
            "jsonrpc": "2.0",
            "id": 100,
            "method": "tools/call",
            "params": {"name": "ghost_tool", "arguments": {}},
        }
        resp = self.server.handle_jsonrpc_request(req)
        self.assertIn("error", resp)
        self.assertEqual(resp["error"]["code"], -32601)


if __name__ == "__main__":
    unittest.main()
