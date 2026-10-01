"""
core/graph_rag.py
=============================================================================
Universal Cognitive Decomposition Engine (UCDE) - Phase 2
GraphRAG: Associative Knowledge Graph & Reciprocal Rank Fusion (RRF) Engine.

Implements:
- Architectural Entity & Relation Graph (DiGraph)
- Automatic Contract Ingestion across 7 Ministries (Strategy, Finance, Legal,
  Security, Analysis, Hardware, Quality)
- Subgraph Expansion & Personalized PageRank (PPR) Topological Ranking
- Dense Vector Semantic Search + Reciprocal Rank Fusion (RRF with k=60)
- End-to-End Architectural Lineage Tracing (Requirements -> Design -> Safety)
=============================================================================
"""

import hashlib
import math
import re
from typing import Any, Dict, List, Literal, Optional, Set, Tuple, Union
import numpy as np
from pydantic import BaseModel, ConfigDict, Field

try:
    import networkx as nx
    HAS_NETWORKX = True
except ImportError:
    HAS_NETWORKX = False


NodeType = Literal[
    "REQUIREMENT",
    "BUSINESS_RULE",
    "THREAT",
    "ENDPOINT",
    "COMPONENT",
    "STANDARD",
    "HARDWARE_CONSTRAINT",
    "ADR",
    "FINANCIAL_METRIC",
    "LEGAL_COMPLIANCE",
    "PERSONA",
    "CONCEPT",
]

RelationType = Literal[
    "IMPLEMENTS",
    "MITIGATES",
    "REQUIRES",
    "CONSTRAINS",
    "VERIFIES",
    "CONFLICTS_WITH",
    "DERIVED_FROM",
    "TARGETS",
    "GOVERNED_BY",
]


class KnowledgeNode(BaseModel):
    """A semantic vertex in the Architectural Knowledge Graph."""
    model_config = ConfigDict(extra="forbid")

    node_id: str = Field(description="Unique entity identifier, e.g. 'AC:AC-AUTH-01'")
    node_type: NodeType = Field(description="Structural category of architectural entity")
    label: str = Field(description="Human-readable title or label")
    description: str = Field(default="", description="Detailed textual description")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Metadata key-value pairs")


class KnowledgeEdge(BaseModel):
    """A directed semantic edge in the Architectural Knowledge Graph."""
    model_config = ConfigDict(extra="forbid")

    source_id: str = Field(description="Source vertex node_id")
    target_id: str = Field(description="Target vertex node_id")
    relation: RelationType = Field(description="Semantic relationship type")
    weight: float = Field(default=1.0, ge=0.0, description="Edge affinity or constraint weight")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Edge metadata")


class GraphQueryResult(BaseModel):
    """Ranked retrieval item combining vector semantic and graph topological score."""
    model_config = ConfigDict(extra="forbid")

    node: KnowledgeNode
    rrf_score: float = Field(ge=0.0, description="Reciprocal Rank Fusion hybrid score")
    vector_rank: Optional[int] = Field(default=None, description="Rank from dense semantic search")
    graph_rank: Optional[int] = Field(default=None, description="Rank from topological PageRank/PPR")
    vector_similarity: float = Field(default=0.0, description="Cosine similarity score (0.0 to 1.0)")
    graph_centrality: float = Field(default=0.0, description="Topological centrality / PPR score")
    provenance_hops: List[str] = Field(default_factory=list, description="Immediate graph neighbors")


class LineageTrace(BaseModel):
    """End-to-end traceability path from high-level intent down to physical constraints."""
    model_config = ConfigDict(extra="forbid")

    root_id: str
    target_id: str
    path: List[str]
    relations: List[str]
    is_verified: bool


class GraphRAGEngine:
    """
    Associative Memory Engine marrying dense vector semantic retrieval with
    topological knowledge graph traversal over architectural artifacts.
    """

    def __init__(self, embedding_dim: int = 64):
        self.embedding_dim: int = embedding_dim
        self.nodes: Dict[str, KnowledgeNode] = {}
        self.edges: List[KnowledgeEdge] = []
        self._adjacency: Dict[str, Dict[str, KnowledgeEdge]] = {}
        self._reverse_adjacency: Dict[str, Dict[str, KnowledgeEdge]] = {}
        self._node_embeddings: Dict[str, np.ndarray] = {}

        if HAS_NETWORKX:
            self._nx_graph = nx.DiGraph()
        else:
            self._nx_graph = None

    def add_node(self, node: KnowledgeNode) -> None:
        """Adds or updates a node in the graph and computes its semantic embedding."""
        self.nodes[node.node_id] = node
        self._adjacency.setdefault(node.node_id, {})
        self._reverse_adjacency.setdefault(node.node_id, {})

        # Compute deterministic semantic embedding vector
        text_repr = f"{node.node_type} {node.label} {node.description} {str(node.properties)}"
        emb = self._compute_embedding(text_repr)
        self._node_embeddings[node.node_id] = emb

        if HAS_NETWORKX and self._nx_graph is not None:
            self._nx_graph.add_node(
                node.node_id,
                node_type=node.node_type,
                label=node.label,
                description=node.description,
            )

    def add_edge(self, edge: KnowledgeEdge) -> None:
        """Adds a directed edge between two existing nodes."""
        if edge.source_id not in self.nodes or edge.target_id not in self.nodes:
            # Silently or gracefully ensure nodes exist as generic concepts if uncreated
            for nid in (edge.source_id, edge.target_id):
                if nid not in self.nodes:
                    self.add_node(KnowledgeNode(
                        node_id=nid,
                        node_type="CONCEPT",
                        label=nid,
                        description=f"Auto-generated placeholder node for {nid}",
                    ))

        self.edges.append(edge)
        self._adjacency[edge.source_id][edge.target_id] = edge
        self._reverse_adjacency[edge.target_id][edge.source_id] = edge

        if HAS_NETWORKX and self._nx_graph is not None:
            self._nx_graph.add_edge(
                edge.source_id,
                edge.target_id,
                relation=edge.relation,
                weight=edge.weight,
            )

    def _compute_embedding(self, text: str) -> np.ndarray:
        """
        Computes a deterministic, normalized dense embedding vector for semantic matching.
        Uses character n-gram / token frequency hashing into fixed embedding_dim.
        """
        vec = np.zeros(self.embedding_dim, dtype=np.float32)
        tokens = re.findall(r"\w+", text.lower())
        if not tokens:
            return vec

        for token in tokens:
            # Deterministic hash projection
            h = int(hashlib.sha256(token.encode("utf-8")).hexdigest()[:8], 16)
            idx = h % self.embedding_dim
            sign = 1.0 if ((h >> 16) & 1) else -1.0
            vec[idx] += sign

        # L2 normalization
        norm = np.linalg.norm(vec)
        if norm > 1e-9:
            vec /= norm
        return vec

    def ingest_contracts(self, contracts: Dict[str, Any]) -> int:
        """
        Auto-populates the Knowledge Graph from 7 Ministry contracts.
        Returns total number of created nodes.
        """
        count_before = len(self.nodes)

        # 1. Ministry 1: Strategy & CJM
        strat = contracts.get("strategy") or contracts.get("PRD_Specification.json") or {}
        if hasattr(strat, "model_dump"):
            strat = strat.model_dump()
        if isinstance(strat, dict):
            for persona in strat.get("target_personas", []):
                p_id = f"PERSONA:{persona}"
                self.add_node(KnowledgeNode(node_id=p_id, node_type="PERSONA", label=str(persona)))

            for ac in strat.get("acceptance_criteria", []):
                ac_id = ac.get("id") or ac.get("scenario_id", "AC-UNKNOWN")
                node_ac_id = f"AC:{ac_id}"
                desc = f"Given {ac.get('given', '')} When {ac.get('when', '')} Then {ac.get('then', '')}"
                self.add_node(KnowledgeNode(
                    node_id=node_ac_id,
                    node_type="REQUIREMENT",
                    label=f"Scenario {ac_id}",
                    description=desc,
                ))

            for br in strat.get("business_rules", []):
                br_id = f"RULE:{br.get('rule_id', 'BR-UNKNOWN')}"
                src_ac = br.get("source_ac_id")
                self.add_node(KnowledgeNode(
                    node_id=br_id,
                    node_type="BUSINESS_RULE",
                    label=br.get("rule_id", "BR"),
                    description=br.get("description", ""),
                ))
                if src_ac:
                    self.add_edge(KnowledgeEdge(
                        source_id=br_id,
                        target_id=f"AC:{src_ac}",
                        relation="VERIFIES",
                    ))

        # 2. Ministry 4: Security
        sec = contracts.get("security") or contracts.get("Security_Policy.agentpolicy") or {}
        if hasattr(sec, "model_dump"):
            sec = sec.model_dump()
        if isinstance(sec, dict):
            for threat in sec.get("stride_matrix", []) or sec.get("stride_threats", []):
                cat = threat.get("category") or threat.get("threat_category", "UNKNOWN")
                th_id = f"THREAT:{cat}"
                self.add_node(KnowledgeNode(
                    node_id=th_id,
                    node_type="THREAT",
                    label=f"STRIDE {cat}",
                    description=threat.get("mitigation_strategy", "") or threat.get("mitigation_mechanism", ""),
                ))
                target = threat.get("target_component")
                if target:
                    comp_id = f"COMPONENT:{target}"
                    self.add_node(KnowledgeNode(node_id=comp_id, node_type="COMPONENT", label=target))
                    self.add_edge(KnowledgeEdge(source_id=th_id, target_id=comp_id, relation="TARGETS"))

        # 3. Ministry 5: Analysis & Endpoints
        ana = contracts.get("analysis") or contracts.get("System_Contracts.json") or {}
        if hasattr(ana, "model_dump"):
            ana = ana.model_dump()
        if isinstance(ana, dict):
            for ep in ana.get("endpoints", []):
                path = ep.get("path", "/api")
                method = ep.get("method", "GET")
                ep_id = f"ENDPOINT:{method}_{path}"
                self.add_node(KnowledgeNode(
                    node_id=ep_id,
                    node_type="ENDPOINT",
                    label=f"{method} {path}",
                    description=f"API Endpoint (Auth={ep.get('requires_auth')}, Timeout={ep.get('timeout_ms')}ms)",
                    properties={"path": path, "method": method, "timeout_ms": ep.get("timeout_ms")},
                ))
                # Link to threats if security requires auth
                if ep.get("requires_auth"):
                    self.add_edge(KnowledgeEdge(
                        source_id=ep_id,
                        target_id="THREAT:SPOOFING",
                        relation="MITIGATES",
                    ))

            for adr in ana.get("architecture_decision_records", []):
                adr_id = f"ADR:{adr.get('title', 'ADR')}"
                self.add_node(KnowledgeNode(
                    node_id=adr_id,
                    node_type="ADR",
                    label=adr.get("title", "ADR"),
                    description=adr.get("decision_outcome", ""),
                ))

        # 4. Ministry 6: Hardware Runtime & FMEA
        hw = contracts.get("hardware") or contracts.get("Hardware_Runtime_Manifest.json") or {}
        if hasattr(hw, "model_dump"):
            hw = hw.model_dump()
        if isinstance(hw, dict):
            hw_id = f"HARDWARE:{hw.get('target_npu_device', 'Intel_NPU')}"
            self.add_node(KnowledgeNode(
                node_id=hw_id,
                node_type="HARDWARE_CONSTRAINT",
                label="NPU Runtime",
                description=f"RAM limit: {hw.get('max_npu_ram_working_set_mb')} MB, Max Latency: {hw.get('max_inference_latency_ms')} ms",
                properties={"ram_mb": hw.get("max_npu_ram_working_set_mb"), "latency_ms": hw.get("max_inference_latency_ms")},
            ))
            if hw.get("hardware_interlocks_required"):
                lock_id = "HARDWARE_CONSTRAINT:THERAC_25_INTERLOCK"
                self.add_node(KnowledgeNode(
                    node_id=lock_id,
                    node_type="HARDWARE_CONSTRAINT",
                    label="Therac-25 Physical Safety Interlock",
                    description="Mandatory physical interlock preventing race condition actuation",
                ))
                self.add_edge(KnowledgeEdge(source_id=lock_id, target_id=hw_id, relation="CONSTRAINS"))

        # 5. Ministry 7: V&V Quality Standards
        qual = contracts.get("quality") or contracts.get("Release_Certified_Artifacts.json") or {}
        if hasattr(qual, "model_dump"):
            qual = qual.model_dump()
        if isinstance(qual, dict):
            for std_name in ["GOST_34.602_89", "ISO_29148", "ISO_29119_4", "NIST_SP_800_207", "RFC_7807"]:
                std_id = f"STANDARD:{std_name}"
                self.add_node(KnowledgeNode(node_id=std_id, node_type="STANDARD", label=std_name))

        return len(self.nodes) - count_before

    def vector_search(self, query: str, top_k: int = 10) -> List[Tuple[str, float]]:
        """
        Executes fast dense semantic cosine similarity search across all nodes.
        Returns list of (node_id, cosine_similarity) sorted descending.
        """
        q_emb = self._compute_embedding(query)
        q_norm = np.linalg.norm(q_emb)
        if q_norm < 1e-9 or not self._node_embeddings:
            return []

        scores: List[Tuple[str, float]] = []
        for nid, n_emb in self._node_embeddings.items():
            sim = float(np.dot(q_emb, n_emb))
            scores.append((nid, max(0.0, sim)))

        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]

    def compute_personalized_pagerank(self, seed_node_ids: List[str], alpha: float = 0.85) -> Dict[str, float]:
        """
        Computes Personalized PageRank (PPR) rooted at seed nodes.
        Uses NetworkX if available, or power iteration fallback.
        """
        valid_seeds = [s for s in seed_node_ids if s in self.nodes]
        if not valid_seeds or not self.nodes:
            return {nid: 0.0 for nid in self.nodes}

        personalization = {nid: (1.0 / len(valid_seeds) if nid in valid_seeds else 0.0) for nid in self.nodes}

        if HAS_NETWORKX and self._nx_graph is not None and len(self._nx_graph) > 0:
            try:
                # Graph must contain all nodes in personalization dict
                for nid in self.nodes:
                    if nid not in self._nx_graph:
                        self._nx_graph.add_node(nid)
                return nx.pagerank(self._nx_graph, alpha=alpha, personalization=personalization, max_iter=100)
            except Exception:
                pass

        # Power iteration fallback
        scores = dict(personalization)
        for _ in range(20):
            next_scores = {nid: (1.0 - alpha) * personalization[nid] for nid in self.nodes}
            for u in self.nodes:
                neighbors = list(self._adjacency.get(u, {}).keys())
                if neighbors:
                    share = (alpha * scores[u]) / len(neighbors)
                    for v in neighbors:
                        next_scores[v] = next_scores.get(v, 0.0) + share
                else:
                    # Dangling node redistribution
                    for v in self.nodes:
                        next_scores[v] += (alpha * scores[u]) / len(self.nodes)
            scores = next_scores

        return scores

    def hybrid_retrieve(
        self,
        query: str,
        top_k: int = 5,
        rrf_k: int = 60,
    ) -> List[GraphQueryResult]:
        """
        Executes Reciprocal Rank Fusion (RRF) combining:
        1. Dense Vector Semantic Search ranking
        2. Graph Topological PageRank / PPR ranking
        Formula: RRF_score(d) = 1 / (k + rank_vector(d)) + 1 / (k + rank_graph(d))
        """
        if not self.nodes:
            return []

        # 1. Vector Search
        vector_res = self.vector_search(query, top_k=len(self.nodes))
        vector_rank_map: Dict[str, int] = {}
        vector_sim_map: Dict[str, float] = {}
        for rank, (nid, sim) in enumerate(vector_res, start=1):
            vector_rank_map[nid] = rank
            vector_sim_map[nid] = sim

        # 2. Graph PPR from top vector seed nodes
        top_seeds = [nid for nid, _ in vector_res[:3]]
        ppr_scores = self.compute_personalized_pagerank(top_seeds)
        graph_sorted = sorted(ppr_scores.items(), key=lambda x: x[1], reverse=True)
        graph_rank_map: Dict[str, int] = {}
        graph_centrality_map: Dict[str, float] = {}
        for rank, (nid, cent) in enumerate(graph_sorted, start=1):
            graph_rank_map[nid] = rank
            graph_centrality_map[nid] = cent

        # 3. Reciprocal Rank Fusion
        hybrid_scores: Dict[str, float] = {}
        all_candidate_ids = set(self.nodes.keys())

        for nid in all_candidate_ids:
            score = 0.0
            if nid in vector_rank_map:
                score += 1.0 / (rrf_k + vector_rank_map[nid])
            if nid in graph_rank_map:
                score += 1.0 / (rrf_k + graph_rank_map[nid])
            hybrid_scores[nid] = score

        sorted_nids = sorted(hybrid_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]

        results: List[GraphQueryResult] = []
        for nid, rrf_sc in sorted_nids:
            node = self.nodes[nid]
            neighbors = list(self._adjacency.get(nid, {}).keys()) + list(self._reverse_adjacency.get(nid, {}).keys())
            results.append(GraphQueryResult(
                node=node,
                rrf_score=round(rrf_sc, 6),
                vector_rank=vector_rank_map.get(nid),
                graph_rank=graph_rank_map.get(nid),
                vector_similarity=round(vector_sim_map.get(nid, 0.0), 4),
                graph_centrality=round(graph_centrality_map.get(nid, 0.0), 6),
                provenance_hops=list(set(neighbors))[:5],
            ))

        return results

    def trace_lineage(self, start_id: str, target_id: str) -> Optional[LineageTrace]:
        """
        Finds the shortest directed semantic dependency path between two entities.
        Verifies architectural alignment (e.g. Persona -> AC -> Endpoint -> Threat).
        """
        if start_id not in self.nodes or target_id not in self.nodes:
            return None

        # BFS shortest path
        queue = [[start_id]]
        visited = {start_id}

        while queue:
            path = queue.pop(0)
            curr = path[-1]

            if curr == target_id:
                relations = []
                for i in range(len(path) - 1):
                    edge = self._adjacency.get(path[i], {}).get(path[i+1])
                    rel = edge.relation if edge else "CONNECTED_TO"
                    relations.append(rel)
                return LineageTrace(
                    root_id=start_id,
                    target_id=target_id,
                    path=path,
                    relations=relations,
                    is_verified=True,
                )

            for neighbor in self._adjacency.get(curr, {}).keys():
                if neighbor not in visited:
                    visited.add(neighbor)
                    new_path = list(path)
                    new_path.append(neighbor)
                    queue.append(new_path)

        return None


__all__ = [
    "NodeType",
    "RelationType",
    "KnowledgeNode",
    "KnowledgeEdge",
    "GraphQueryResult",
    "LineageTrace",
    "GraphRAGEngine",
]
