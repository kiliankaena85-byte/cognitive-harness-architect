"""
core/cognitive_memory.py
=============================================================================
Universal Cognitive Decomposition Engine (UCDE) - Phase 2
4-Tier Cognitive Memory Architecture & Prompt Quarantine Guard.

Implements:
- Tier 1: Working Ephemeral Context (LRU bounded working window)
- Tier 2: Episodic Session History (Saga transactions, arbitrations, state hashes)
- Tier 3: Associative Semantic Knowledge Store (Integrated GraphRAG Engine)
- Tier 4: Immutable Architectural Grounding (Standards, Laws, Invariant Rules)
- OWASP LLM Top 10: Strict <user_brief_quarantine> Prompt Injection Quarantine
- Prefix Prompt Caching Telemetry (Hit rate target >= 85%)
=============================================================================
"""

import collections
import hashlib
import re
import time
from typing import Any, Dict, List, Literal, Optional, Tuple, Union
from pydantic import BaseModel, ConfigDict, Field

from .graph_rag import GraphRAGEngine, KnowledgeNode, KnowledgeEdge, GraphQueryResult


class EpisodicEvent(BaseModel):
    """An execution event recorded in Tier 2 episodic memory."""
    model_config = ConfigDict(extra="forbid")

    event_id: str = Field(description="Unique deterministic event identifier")
    timestamp_epoch: float = Field(description="Event creation time")
    event_type: Literal[
        "PIPELINE_START",
        "HYPOTHESIS_GENERATED",
        "PARETO_ARBITRATION",
        "SAGA_ROLLBACK",
        "STAGE_GATE_VERIFICATION",
        "CODE_SYNTHESIS",
        "SANDBOX_EXECUTION",
        "RELEASE_SEALED",
    ] = Field(description="Event classification")
    ministry_id: Optional[int] = Field(default=None, ge=1, le=9, description="Originating ministry/module")
    state_hash: str = Field(description="SHA-256 state fingerprint at time of event")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Structured event payload")


class MemoryRetrievalBundle(BaseModel):
    """Aggregated memory context retrieved for LLM prompt injection."""
    model_config = ConfigDict(extra="forbid")

    tier1_working_context: List[Dict[str, Any]]
    tier2_recent_episodes: List[Dict[str, Any]]
    tier3_associative_graph: List[GraphQueryResult]
    tier4_grounding_rules: List[str]
    cache_prefix_key: str
    quarantined_user_prompt: str


class CognitiveMemoryStore:
    """
    Unified 4-Tier Cognitive Memory System maintaining working context,
    episodic history, associative graph structures, and immutable standards.
    """

    def __init__(
        self,
        tier1_capacity: int = 50,
        graph_embedding_dim: int = 64,
    ):
        self.tier1_capacity: int = int(tier1_capacity)
        # Tier 1: Working ephemeral memory (OrderedDict for LRU)
        self._tier1_working: collections.OrderedDict[str, Dict[str, Any]] = collections.OrderedDict()

        # Tier 2: Episodic history
        self._tier2_episodes: List[EpisodicEvent] = []

        # Tier 3: Associative GraphRAG
        self.tier3_graph: GraphRAGEngine = GraphRAGEngine(embedding_dim=graph_embedding_dim)

        # Tier 4: Immutable Architectural Grounding
        self._tier4_grounding: Dict[str, str] = self._initialize_immutable_grounding()

        # Prefix Cache Telemetry
        self._cache_queries_total: int = 0
        self._cache_hits: int = 0
        self._last_prefix_hash: Optional[str] = None

    def _initialize_immutable_grounding(self) -> Dict[str, str]:
        """Pre-loads immutable core standards and safety invariants."""
        return {
            "ISO_29148": "Shall/Given-When-Then unambiguous requirements engineering semantics.",
            "GOST_34.602_89": "Automated system specification must contain 8 mandatory sections.",
            "GOST_19.201_78": "Software program specification documentation completeness standards.",
            "NIST_SP_800_207": "Zero Trust Architecture: Mandatory token/mTLS verification, no implicit trust.",
            "RFC_7807_9457": "Problem Details for HTTP APIs: Mandatory type, title, status, detail, instance.",
            "FZ_152": "Personal data processing and database localization strictly within Russian Federation.",
            "EU_AI_ACT": "AI Act Regulation 2024/1689: Strict prohibition of UNACCEPTABLE cognitive manipulation risks.",
            "IEC_61508_THERAC25": "Hardware interlocks mandatory when actuator latency exceeds 1000 ms to prevent race hazards.",
            "FMEA_RPN": "Risk Priority Number (RPN) = Severity * Occurrence * Detection must not exceed 120 (SIL-2).",
        }

    # =========================================================================
    # Tier 1: Working Context Operations
    # =========================================================================

    def put_working_context(self, key: str, value: Any) -> None:
        """Stores or updates an ephemeral working context item with LRU eviction."""
        if key in self._tier1_working:
            self._tier1_working.move_to_end(key)
        self._tier1_working[key] = {
            "key": key,
            "value": value,
            "updated_at": time.time(),
        }
        if len(self._tier1_working) > self.tier1_capacity:
            self._tier1_working.popitem(last=False)  # Evict oldest

    def get_working_context(self, key: str) -> Optional[Any]:
        """Retrieves a working context item and marks it recently accessed."""
        if key in self._tier1_working:
            self._tier1_working.move_to_end(key)
            return self._tier1_working[key]["value"]
        return None

    # =========================================================================
    # Tier 2: Episodic History Operations
    # =========================================================================

    def record_episode(
        self,
        event_type: str,
        payload: Dict[str, Any],
        ministry_id: Optional[int] = None,
    ) -> EpisodicEvent:
        """Records an immutable episodic event in the timeline."""
        now = time.time()
        # Compute deterministic state hash
        canon_bytes = f"{now}:{event_type}:{ministry_id}:{str(sorted(payload.items()))}".encode("utf-8")
        st_hash = hashlib.sha256(canon_bytes).hexdigest()

        event = EpisodicEvent(
            event_id=f"EP-{len(self._tier2_episodes)+1:05d}",
            timestamp_epoch=now,
            event_type=event_type,  # type: ignore
            ministry_id=ministry_id,
            state_hash=st_hash,
            payload=payload,
        )
        self._tier2_episodes.append(event)
        return event

    def get_recent_episodes(self, limit: int = 10) -> List[EpisodicEvent]:
        """Returns the most recent N episodic history events."""
        return self._tier2_episodes[-limit:]

    # =========================================================================
    # Tier 4: Immutable Grounding Operations
    # =========================================================================

    def get_grounding_rules(self) -> List[str]:
        """Returns the full list of immutable domain grounding rules."""
        return [f"[{rule_id}] {desc}" for rule_id, desc in self._tier4_grounding.items()]

    # =========================================================================
    # Security: OWASP LLM Prompt Injection Quarantine
    # =========================================================================

    @staticmethod
    def quarantine_user_brief(raw_user_text: str) -> Tuple[str, bool, List[str]]:
        """
        Sanitizes raw user inputs and wraps them in strict XML quarantine tags.
        Detects prompt injection vectors (OWASP LLM01).
        Returns: (quarantined_text: str, is_suspicious: bool, detected_patterns: list)
        """
        suspicious_patterns = [
            r"ignore\s+(all\s+)?(previous|prior)\s+instructions",
            r"system\s+prompt\s+override",
            r"you\s+are\s+now\s+in\s+developer\s+mode",
            r"disregard\s+all\s+safety\s+guidelines",
            r"format\s+c:\s*",
            r"rm\s+-rf\s+/",
            r"reveal\s+(your\s+)?(system\s+prompt|api\s+keys)",
        ]

        flags: List[str] = []
        lowered = raw_user_text.lower()
        for pat in suspicious_patterns:
            if re.search(pat, lowered):
                flags.append(pat)

        # Strip any existing unescaped quarantine tag attempts to avoid tag injection
        clean_text = raw_user_text.replace("<user_brief_quarantine>", "&lt;user_brief_quarantine&gt;")
        clean_text = clean_text.replace("</user_brief_quarantine>", "&lt;/user_brief_quarantine&gt;")

        quarantined = (
            "<user_brief_quarantine>\n"
            f"{clean_text.strip()}\n"
            "</user_brief_quarantine>"
        )

        is_suspicious = len(flags) > 0
        return quarantined, is_suspicious, flags

    # =========================================================================
    # Prefix Cache Telemetry & Context Assembly
    # =========================================================================

    def assemble_context_bundle(
        self,
        query: str,
        user_prompt: str,
        graph_top_k: int = 5,
    ) -> MemoryRetrievalBundle:
        """
        Assembles a comprehensive multi-tier memory bundle for model consumption.
        Enforces prompt quarantine and computes prefix cache telemetry.
        """
        self._cache_queries_total += 1

        # 1. Tier 1 working context snapshot
        t1 = list(self._tier1_working.values())[-10:]

        # 2. Tier 2 recent episodes snapshot
        t2 = [ep.model_dump() for ep in self.get_recent_episodes(limit=5)]

        # 3. Tier 3 associative retrieval from GraphRAG
        t3 = self.tier3_graph.hybrid_retrieve(query, top_k=graph_top_k)

        # 4. Tier 4 immutable grounding rules
        t4 = self.get_grounding_rules()

        # 5. Compute prefix cache key (based on Tier 4 grounding and system instructions)
        prefix_content = "\n".join(sorted(t4))
        prefix_hash = hashlib.sha256(prefix_content.encode("utf-8")).hexdigest()

        if self._last_prefix_hash == prefix_hash:
            self._cache_hits += 1
        self._last_prefix_hash = prefix_hash

        # 6. Apply prompt quarantine
        quarantined_prompt, _, _ = self.quarantine_user_brief(user_prompt)

        return MemoryRetrievalBundle(
            tier1_working_context=t1,
            tier2_recent_episodes=t2,
            tier3_associative_graph=t3,
            tier4_grounding_rules=t4,
            cache_prefix_key=prefix_hash,
            quarantined_user_prompt=quarantined_prompt,
        )

    def get_cache_hit_rate(self) -> float:
        """Returns simulated prefix prompt cache hit rate (0.0 to 100.0%)."""
        if self._cache_queries_total == 0:
            return 100.0
        return round((self._cache_hits / self._cache_queries_total) * 100.0, 2)


__all__ = [
    "EpisodicEvent",
    "MemoryRetrievalBundle",
    "CognitiveMemoryStore",
]
