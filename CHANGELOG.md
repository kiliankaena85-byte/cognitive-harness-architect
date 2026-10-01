# Changelog: Universal Cognitive Decomposition Engine (UCDE)

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.4.0] - 2026-10-01
### Added
- **Phase 2: Cognitive Memory & Model Context Protocol (MCP):**
  - **GraphRAG Associative Knowledge Graph (`core/graph_rag.py`):**
    - Multi-entity knowledge graph connecting Requirements, Personas, Threats, Endpoints, Components, Hardware, and Standards.
    - Automatic contract ingestion across all 7 ministries.
    - Hybrid dense vector semantic search + Personalized PageRank (PPR) topological graph traversal.
    - Reciprocal Rank Fusion (RRF with $k=60$) for unified ranking.
    - Shortest-path causal lineage tracing (`trace_lineage`) from high-level personas down to hardware safety interlocks.
  - **Multi-Tier Cognitive Memory Store (`core/cognitive_memory.py`):**
    - 4-Tier Memory: Tier 1 (Working LRU context), Tier 2 (Episodic history with SHA-256 state hashes), Tier 3 (GraphRAG associative graph), Tier 4 (Immutable domain grounding).
    - OWASP LLM Top 10 Prompt Injection Quarantine Guard: Sanitizes input and wraps into strict `<user_brief_quarantine>` tags, flagging hostile override patterns.
    - Deterministic prefix prompt caching telemetry simulating KV cache hit rates ($\ge 85\%$).
  - **Model Context Protocol (MCP) Server (`core/mcp_server.py`):**
    - Standard JSON-RPC 2.0 protocol over stdio and programmatic dispatcher.
    - 6 Core Architectural Tools: `lint_specification`, `evaluate_pareto`, `synthesize_code`, `synthesize_and_run_tests`, `query_cognitive_memory`, `trace_architectural_lineage`.
  - **Saga Orchestrator Safety Hardening (`core/orchestrator.py`):**
    - Enforced compensation deadline timeout (`compensation_timeout_sec = 5.0`).
    - Bidirectional handshake acknowledgment recording with fencing tokens.
  - **Full Verification Suite:**
    - Expanded test suite from 304 to **324 unit/integration tests**, achieving 100% pass rate.
    - Maintained sub-millisecond rejection SLA ($5.67$ µs mean, $31.9$ µs P99, $< 1.0$ ms SLA).

---

## [1.3.0] - 2026-10-01
### Added
- **Phase 1: Spec-to-Code & Executable Tests (Closed-Loop TDD Engine):**
  - **Module 8 (`CodeSynthesizer` - `core/code_synthesizer.py`):**
    - Deterministic code generator transforming Pydantic V2 SystemAnalysis and SecurityPolicy contracts into executable microservices.
    - Zero-dependency in-process `dispatch_request` table + optional FastAPI application bootstrap with RFC 7807 exception handler.
    - Automated Pydantic V2 request/response models and `ProblemDetails` RFC 7807/9457 error models.
    - NIST SP 800-207 Zero-Trust security guards with token verification, sliding token-bucket rate limiter (DoD/FSTEC УБИ.031), and SHA-256 idempotency cache.
    - 100% Python AST parsing validation prior to emission.
  - **Module 9 (`TestSynthesizer` - `core/test_synthesizer.py`):**
    - Direct compilation of Gherkin BDD scenarios into executable `unittest.TestCase` suites with full acceptance criteria traceability (`source_ac_id`).
    - ISO/IEC/IEEE 29119-4 boundary value stress tests and property-based test suites.
    - Automated penetration testing verifying all 6 STRIDE threat categories against FSTEC BDU threat database.
    - Strict RFC 7807 error schema validation tests.
  - **Sandbox Runner & Self-Healing Loop (`core/sandbox_runner.py`):**
    - Subprocess sandbox isolation with wall-clock timeout guards ($\le 10.0$ s) and clean environment variable virtualization.
    - Structured test execution parser (tests run, failures, errors, tracebacks).
    - Autonomous closed-loop repair feedback cycle bounded by $\tau_{\max} \le 3$ retries without infinite loops.
  - **Standards Linter Integration (`core/standards_linter.py`):**
    - Added `Rule 8.1: SPEC_TO_CODE_SYNTAX` verifying AST syntax validity and RFC 7807 declaration.
    - Added `Rule 9.1: EXECUTABLE_BDD_PASS` enforcing 100% executable test pass rate.
  - **Full Verification Suite:**
    - Expanded test suite to **304 unit/integration tests**, achieving 100% pass rate.
    - Maintained sub-millisecond rejection SLA ($5.28$ µs average, $14.5$ µs P99, $< 1.0$ ms SLA).

---

## [1.2.0] - 2026-10-01
### Added
- **MADR 3.0 ADR Generation (Node 5 - System Analysis):**
  - Added `ArchitectureDecisionRecord` model conforming to Markdown Architectural Decision Records 3.0.
  - Mandatory evaluation of $\ge 2$ considered options, decision drivers, positive/negative consequences, and compliance verification.
  - Deterministic linter rule `Rule 5.6: MADR_3.0` enforcing tradeoff analysis.
- **FMEA Risk Priority Number Analysis (Node 6 - Hardware Runtime):**
  - Added `FmeaFailureMode` model according to ГОСТ Р 27.302-2009 / IEC 60812.
  - Automatic calculation of $RPN = \text{Severity} \times \text{Occurrence} \times \text{Detection}$.
  - Strict SIL-2 safety threshold invariant: $RPN \le 120$.
  - Interlock protection against physical race hazards (Therac-25 defense).
- **FSTEC Orders № 17, 21, 239 Information Security Classification (Nodes 3 & 4):**
  - Order № 17 (GIS): Classes `К1`, `К2`, `К3`.
  - Order № 21 (ISPDn): Protection levels `УЗ-1`, `УЗ-2`, `УЗ-3`, `УЗ-4`.
  - Order № 239 (KII): Critical infrastructure categories `1`, `2`, `3`.
  - Mapping to FSTEC Threat Database (`^УБИ\.\d{3}$`) in STRIDE threat matrix.
- **Dual Documentation Profiles Architecture (Nodes 1 & 7):**
  - Selection between `GOST_34_AUTOMATED_SYSTEM` (Automated Systems), `GOST_19_ESPD_SOFTWARE` (pure Software), and `HYBRID_INTEGRATED` (AI PAC).
  - Validation of mandatory sections for ГОСТ 34.602-89 (8 sections) and ГОСТ 19.201-78 (8 sections).
  - Formatting requisites for document title pages according to ГОСТ Р 7.0.97-2016.
- **Comprehensive Test Coverage:**
  - Expanded unit test suite from 24 to 30 tests in `tests/test_standards_linter.py`.
  - 100% pass rate across 276 tests in full discover suite.
  - Verified 37 standards in `release_manifest.json` with 100.0% compliance score.

---

## [1.1.0] - 2026-10-01
### Added
- **AI-Native Cognitive Architecture Standards:**
  - `RagPipelineConfig`: HNSW vector index, 1024-dim dense embeddings (`bge-m3`), hybrid BM25 search with Reciprocal Rank Fusion (RRF), cross-encoder reranking.
  - `MemoryArchitectureConfig`: 4-tier cognitive memory (context window 32k, long-term vector memory, GraphRAG associative memory, explicit prefix prompt caching).
  - `TokenEconomicsConfig`: Prompt/completion token budgets, target cost per 1k inferences, context cache hit rate target $\ge 85\%$.
  - `OwaspLlmSecurityConfig`: OWASP LLM Top 10 mitigations, strict XML tag isolation quarantine (`<user_brief_quarantine>`), Model Context Protocol (MCP) authentication.
  - `RagTriadMetricsConfig`: Zero-hallucination metrics (Context Relevance $\ge 0.85$, Groundedness/Faithfulness $\ge 0.95$, Answer Relevance $\ge 0.90$, Jailbreak Resistance $\ge 98\%$).
- Deterministic standards linter rules for AI-native verification.

---

## [1.0.0] - 2026-10-01
### Added
- **Universal Cognitive Decomposition Engine (7 Ministries):**
  - Ministry 1: Strategy, Marketing & CJM (`StrategyCJMContract`).
  - Ministry 2: Finance & Unit Economics (`FinanceBudgetContract`).
  - Ministry 3: Legal & Regulatory Compliance (`LegalComplianceContract`).
  - Ministry 4: Information Security (`SecurityPolicyContract`).
  - Ministry 5: System Analysis & Architecture (`SystemAnalysisContract`).
  - Ministry 6: Hardware Runtime & Edge NPU (`HardwareRuntimeContract`).
  - Ministry 7: V&V Quality Gate (`VVQualityContract`).
- **Core Orchestration & Zero-Trust Verification:**
  - Saga transaction pattern coordinator with automated rollback and compensating transactions.
  - System 1 NPU & Decisions Pareto Arbiter (`L-MOPA`).
  - System 2 Multi-Hypothesis Generator with OpenRouter API rotation.
  - Zero-Trust CDD-TDD verification engine based on Hoare Logic invariants $\{P\} S \{Q\}$.
  - Simplex fail-safe downscaling after 3 retries.
  - Sub-millisecond schema rejection SLA ($< 1$ ms).
