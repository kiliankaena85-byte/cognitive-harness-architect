"""
tests/test_graph_rag.py
=============================================================================
Unit Test Suite for GraphRAG Engine & Associative Architectural Memory.
Phase 2 - Universal Cognitive Decomposition Engine (UCDE)
=============================================================================
"""

import unittest
from core.graph_rag import (
    GraphRAGEngine,
    KnowledgeNode,
    KnowledgeEdge,
    GraphQueryResult,
    LineageTrace,
)


class TestGraphRAGEngine(unittest.TestCase):
    def setUp(self):
        self.rag = GraphRAGEngine(embedding_dim=32)

    def test_add_nodes_and_edges(self):
        n1 = KnowledgeNode(node_id="REQ:01", node_type="REQUIREMENT", label="Zero Trust Auth", description="Must require token")
        n2 = KnowledgeNode(node_id="EP:01", node_type="ENDPOINT", label="POST /login", description="Login endpoint")
        self.rag.add_node(n1)
        self.rag.add_node(n2)

        edge = KnowledgeEdge(source_id="EP:01", target_id="REQ:01", relation="IMPLEMENTS")
        self.rag.add_edge(edge)

        self.assertEqual(len(self.rag.nodes), 2)
        self.assertEqual(len(self.rag.edges), 1)

    def test_vector_search_semantic_matching(self):
        self.rag.add_node(KnowledgeNode(
            node_id="SEC:SPOOFING",
            node_type="THREAT",
            label="SPOOFING",
            description="Attacker impersonates a legitimate user using forged credentials",
        ))
        self.rag.add_node(KnowledgeNode(
            node_id="HW:NPU",
            node_type="HARDWARE_CONSTRAINT",
            label="Intel AI Boost NPU",
            description="Physical neural processing unit with 512 MB memory constraint",
        ))

        results = self.rag.vector_search("impersonate credentials forged", top_k=2)
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0][0], "SEC:SPOOFING")
        self.assertGreater(results[0][1], 0.0)

    def test_ingest_7_ministry_contracts(self):
        mock_contracts = {
            "strategy": {
                "target_personas": ["Chief Information Security Officer"],
                "acceptance_criteria": [
                    {"id": "AC-01", "given": "Valid cert", "when": "Request is sent", "then": "Accept 200"}
                ],
                "business_rules": [
                    {"rule_id": "BR-101", "description": "Mandatory TLS", "source_ac_id": "AC-01"}
                ],
            },
            "security": {
                "stride_matrix": [
                    {"category": "SPOOFING", "mitigation_strategy": "Mutual TLS", "target_component": "Gateway"}
                ]
            },
            "analysis": {
                "endpoints": [
                    {"path": "/api/v1/auth", "method": "POST", "requires_auth": True, "timeout_ms": 500}
                ],
                "architecture_decision_records": [
                    {"title": "ADR-01-Use-Event-Driven", "decision_outcome": "Accepted Redis streams"}
                ]
            },
            "hardware": {
                "target_npu_device": "Intel_NPU_125H",
                "max_npu_ram_working_set_mb": 512,
                "max_inference_latency_ms": 45,
                "hardware_interlocks_required": True,
            },
            "quality": {
                "gost_34_602_all_sections_present": True,
            }
        }

        created = self.rag.ingest_contracts(mock_contracts)
        self.assertGreater(created, 5)
        self.assertIn("PERSONA:Chief Information Security Officer", self.rag.nodes)
        self.assertIn("AC:AC-01", self.rag.nodes)
        self.assertIn("RULE:BR-101", self.rag.nodes)
        self.assertIn("THREAT:SPOOFING", self.rag.nodes)
        self.assertIn("COMPONENT:Gateway", self.rag.nodes)
        self.assertIn("ENDPOINT:POST_/api/v1/auth", self.rag.nodes)
        self.assertIn("HARDWARE_CONSTRAINT:THERAC_25_INTERLOCK", self.rag.nodes)

    def test_hybrid_retrieve_rrf(self):
        self.test_ingest_7_ministry_contracts()

        results = self.rag.hybrid_retrieve("mutual TLS authentication and security", top_k=3, rrf_k=60)
        self.assertGreater(len(results), 0)
        for r in results:
            self.assertIsInstance(r, GraphQueryResult)
            self.assertGreater(r.rrf_score, 0.0)
            self.assertIsNotNone(r.node)

    def test_trace_lineage_shortest_path(self):
        # Create a causal chain: Persona -> AC -> Rule
        self.rag.add_node(KnowledgeNode(node_id="P1", node_type="PERSONA", label="Auditor"))
        self.rag.add_node(KnowledgeNode(node_id="AC1", node_type="REQUIREMENT", label="Scenario 1"))
        self.rag.add_node(KnowledgeNode(node_id="BR1", node_type="BUSINESS_RULE", label="Rule 1"))

        self.rag.add_edge(KnowledgeEdge(source_id="P1", target_id="AC1", relation="DERIVED_FROM"))
        self.rag.add_edge(KnowledgeEdge(source_id="AC1", target_id="BR1", relation="VERIFIES"))

        trace = self.rag.trace_lineage("P1", "BR1")
        self.assertIsNotNone(trace)
        self.assertEqual(trace.path, ["P1", "AC1", "BR1"])
        self.assertEqual(trace.relations, ["DERIVED_FROM", "VERIFIES"])
        self.assertTrue(trace.is_verified)

    def test_trace_lineage_no_path_returns_none(self):
        self.rag.add_node(KnowledgeNode(node_id="A", node_type="CONCEPT", label="A"))
        self.rag.add_node(KnowledgeNode(node_id="B", node_type="CONCEPT", label="B"))
        trace = self.rag.trace_lineage("A", "B")
        self.assertIsNone(trace)


if __name__ == "__main__":
    unittest.main()
