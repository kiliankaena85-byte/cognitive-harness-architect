# TEST_INFRA — Comprehensive Test Infrastructure & 4-Tier Methodology

**Document Version:** 1.0-STRICT  
**Standard Compliance:** ГОСТ 34.603-92, ГОСТ Р 56939-2024 (ФСТЭК SDLC), ISO/IEC/IEEE 29148:2018, Hoare Logic {P} S {Q}  
**Hardware & Runtime Baseline:** Intel Core Ultra 5 125H, Intel AI Boost NPU (VPU 3720), Python 3.10+, Pydantic V2, Unittest, Hypothesis  

---

## 1. Test Architecture & Runner Specification

### 1.1. Core Test Philosophy: Opaque-Box Determinism & Zero-Trust
The test infrastructure for the **Universal Cognitive Decomposition Engine (7-Ministry Generative Pipeline)** enforces strict opaque-box verification. Tests interact with the engine exclusively across documented public interface contracts, CLI entry points, and deterministic verification gates. 

Key architectural characteristics:
1. **Runner Framework**: Standard Python `unittest` test suite discovered and executed with zero third-party test-runner lock-in:
   ```bash
   # Dedicated E2E pipeline test execution:
   python -m unittest discover -s core -p "test_e2e_pipeline.py"

   # Full project test discovery across all modules:
   python -m unittest discover -s core -p "test_*.py"
   ```
2. **Offline Hermeticity & Mock Fixtures**: Tests must run deterministically in restricted, air-gapped CI/CD environments without external OpenRouter internet access or specialized hardware driver dependencies. High-fidelity mock and simulated fixtures emulate:
   - OpenRouter System 2 LLM inference (with 5-key rotation, 429/500 faults, rate limiting, and circuit breaker simulation).
   - Intel AI Boost NPU / OpenVINO INT8 embedding and semantic cosine similarity scoring with CPU fallback.
   - Together Tev1-4B Decisions API (`/api/alpha/decisions`) discrete choice evaluation.
3. **Dual-Mode Contract Resolution**: To support progressive milestone delivery (M1 through M5) without broken builds, the E2E test harness (`core/test_e2e_pipeline.py`) dynamically queries production modules (`core.schemas`, `core.npu_darwinian_loop`, `core.ministries.nodes`, `core.orchestrator`, `cli`), and falls back to mathematical reference implementations adhering to `PROJECT.md` specifications.

---

## 2. 4-Tier Test Methodology

The testing architecture is organized into four complementary verification tiers:

```
+-----------------------------------------------------------------------------------+
| Tier 4: Real-World Scenarios (Therac-25 Race Condition, FinTech, Edge IoT)       |
+-----------------------------------------------------------------------------------+
| Tier 3: Cross-Feature Interactions (Pairwise Combinations, Saga Trans-Matrix)    |
+-----------------------------------------------------------------------------------+
| Tier 2: Boundary & Corner Cases (>=5 test cases per feature for 30 features)     |
+-----------------------------------------------------------------------------------+
| Tier 1: Feature Coverage (>=5 test cases per feature for 30 features)            |
+-----------------------------------------------------------------------------------+
```

---

### Tier 1: Feature Coverage (>=5 Test Cases per Feature for All 30 Features)

Tier 1 establishes full functional coverage across all 30 features enumerated in `PROJECT.md`. Every feature is verified by at least 5 distinct test cases covering its nominal, functional, and structural requirements.

| Feature ID | Feature Name | Test Cases (>=5) |
|---|---|---|
| **F-SCH-01** | `StrategyCJMContract` & Bidirectional Traceability | 1. Nominal PRD validation with valid Gherkin ACs and rules.<br>2. Multiple user personas and jobs-to-be-done validation.<br>3. Exact Gherkin syntax matching regex pattern `^AC-[A-Z0-9]+-\d+$`.<br>4. Rule linking verification where `source_ac_id` exists in AC set.<br>5. Extraction of bidirectional traceability graph. |
| **F-SCH-02** | `FinanceBudgetContract` & Unit Economics | 1. Nominal budget with LTV/CAC = 4.0, margin = 25%, break-even = 12 mo.<br>2. OPEX and CAPEX numerical bounds verification ($>0$).<br>3. Multi-currency support (RUB, USD, EUR).<br>4. Break-even threshold test at upper bound (24 months).<br>5. Target margin threshold test at lower bound (15.0%). |
| **F-SCH-03** | `LegalComplianceContract` & Regulatory | 1. Nominal attestation with 152-FZ УЗ-1 and 54-FZ fiscal receipts.<br>2. Allowed personal data processing levels (УЗ-1, УЗ-2, УЗ-3, УЗ-4, NONE).<br>3. Jurisdiction list validation (e.g. `["RUS", "EAEU"]`).<br>4. Approved OSS licenses list (MIT, Apache-2.0, BSD-3).<br>5. Permitted EU AI Act risk levels (MINIMAL, LIMITED, HIGH). |
| **F-SCH-04** | `SecurityPolicyContract` & STRIDE Matrix | 1. Nominal security policy with all 6 STRIDE categories present.<br>2. Zero-trust enforcement boolean validation.<br>3. Supported auth mechanisms (JWT_ED25519, MTLS, OIDC_PKCE).<br>4. Rate limiting RPS per IP within range (1..1000).<br>5. Encryption at rest (AES_256_GCM, GOST_KUZNYECHIK) & in transit (TLS_1_3). |
| **F-SCH-05** | `SystemAnalysisContract` & System Topology | 1. Nominal microservice specification with OpenAPI 3.1.<br>2. Multi-endpoint validation with HTTP methods (GET, POST, etc.).<br>3. Idempotent flag enforcement for state mutations.<br>4. Message bus selection (KAFKA, RABBITMQ, REDIS_STREAMS, NATS).<br>5. DB normalization constraints (3NF, BCNF, DENORMALIZED_READ_REPLICAS). |
| **F-SCH-06** | `HardwareRuntimeContract` & NPU Constraints | 1. Nominal Intel Core Ultra 5 125H / Intel AI Boost NPU configuration.<br>2. Target NPU devices (INTEL_AI_BOOST_VPU_3720, INTEL_ARC_GPU, CPU_FALLBACK).<br>3. OpenVINO 2026.4.0 runtime string validation.<br>4. Valid latency budget under 50 ms and cold start <= 100 ms.<br>5. Hardware interlocks required flag when actuator latency > 1000 ms. |
| **F-SCH-07** | `VVQualityContract` & Certification Invariants | 1. Nominal quality certification with ISO 29148 >= 85 and RTM = 100%.<br>2. GOST 34.602 all 8 sections presence confirmation.<br>3. Mutation score percentage >= 95% validation.<br>4. Brier score probability calibration <= 0.04.<br>5. Cryptographic SHA-256 digest validation (64 hex characters). |
| **F-SCH-08** | Sub-Millisecond Schema Rejection Benchmark | 1. Benchmark invalid LTV/CAC rejection execution duration ($< 1$ ms).<br>2. Benchmark missing field rejection execution duration ($< 1$ ms).<br>3. Benchmark regex mismatch rejection execution duration ($< 1$ ms).<br>4. Benchmark numerical bounds violation rejection ($< 1$ ms).<br>5. Benchmark Therac-25 un-interlocked latency rejection ($< 1$ ms). |
| **F-NPU-01** | Tier 1A Local Fast-Path Scorer (NPU/CPU) | 1. Semantic cosine distance calculation to ideal schema.<br>2. OpenVINO INT8 model execution simulation on NPU.<br>3. Transparent fallback to CPU vector execution on missing VPU.<br>4. Penalization of prohibited qualitative ISO 29148 words.<br>5. Fast evaluation execution time budget verification ($< 15$ ms). |
| **F-NPU-02** | Tier 1B Together Tev1-4B Decisions API | 1. Discrete choice selection between candidate hypothesis pairs.<br>2. OpenRouter `/api/alpha/decisions` payload serialization.<br>3. Fallback to Tier 1A local scorer on simulated Decisions API timeout.<br>4. Confidence calibration verification (Brier score metric).<br>5. Categorical classification of architectural risk patterns. |
| **F-NPU-03** | L-MOPA Vector Evaluation $\vec{F}(h)$ | 1. Exact 5-tuple vector calculation $(F_1, F_2, F_3, F_4, F_5)$.<br>2. Correct evaluation of $F_1$ (Hard Invariants binary $\{0,1\}$).<br>3. Correct evaluation of $F_2$ (Security & STRIDE score $[0,1]$).<br>4. Correct evaluation of $F_3$ (Intent traceability score $[0,1]$).<br>5. Evaluation of $F_4$ (Resource efficiency) and $F_5$ (MDL density). |
| **F-NPU-04** | L-MOPA Strict $F_1=0$ Disqualification | 1. Disqualification of candidate with schema type mismatch ($F_1=0$).<br>2. Disqualification of candidate with budget violation ($F_1=0$).<br>3. Disqualification of candidate with RAM > 512 MB ($F_1=0$).<br>4. Rejection of all candidates when all have $F_1=0$ (returns None).<br>5. Assurance that high scores on $F_2..F_5$ never rescue an $F_1=0$ candidate. |
| **F-NPU-05** | L-MOPA Mahalanobis Tie-Breaker | 1. Resolution of Pareto-equivalent candidates using distance to utopian $\vec{F}^*$.<br>2. Covariance matrix scaling across heterogeneous objective metrics.<br>3. Deterministic winner selection on identical non-dominated fronts.<br>4. Statistical indistinguishability threshold $\epsilon_k$ application.<br>5. Anti-skew verification preventing short descriptions from beating secure ones. |
| **F-GEN-01** | Stratified Ensemble Generator ($N=3..5$) | 1. Generation of Defensive / High-Security candidate ($T=0.20$).<br>2. Generation of Balanced candidate ($T=0.40$).<br>3. Generation of High-Throughput candidate ($T=0.70$).<br>4. Generation of Frugal / Edge-Optimized candidate ($T=0.30$).<br>5. Generation of Adversarial Contrast / Red-Team candidate ($T=0.60$). |
| **F-GEN-02** | 5-Key Pool Rotation ($K_{\text{next}}$) | 1. Round-robin rotation upon successful generation ($K_{\text{idx}} \to (K_{\text{idx}}+1)\%5$).<br>2. Immediate key failover on HTTP 429 status code.<br>3. Exhaustion handling when all 5 keys encounter rate limits.<br>4. Preservation of per-key request metrics and telemetry.<br>5. State restoration of healthy keys after backoff interval. |
| **F-GEN-03** | Token-Bucket Rate Limiter (20 RPM) & Jitter | 1. Admission of requests under token limit (20 tokens available).<br>2. Delay or rejection when token bucket is exhausted.<br>3. Token refill over time according to 20 RPM leak rate.<br>4. Exponential backoff calculation $t = 2^r \cdot 0.5 + \mathcal{U}(0, 0.2)$.<br>5. Maximum retry attempt enforcement ($r \le 3$). |
| **F-GEN-04** | 3-Strike Circuit Breaker & Fallback Ladder | 1. Circuit breaker remains CLOSED during nominal HTTP 200 responses.<br>2. Circuit breaker trips to OPEN after 3 consecutive failures (HTTP 429/5xx).<br>3. Automatic rejection or rerouting during 60s cooldown period.<br>4. Transition to HALF-OPEN after cooldown and probing with test request.<br>5. Step-down through Model Fallback Ladder (Nemotron $\to$ Cohere $\to$ Local Mock). |
| **F-GEN-05** | Prompt Quarantine & Constrained JSON Decoding | 1. Isolation of user prompt within `<user_brief_quarantine>` tags.<br>2. AST filtering of role-switch phrases (`system:`, `ignore instructions`).<br>3. Rejection of unescaped prompt injection payloads.<br>4. Constrained decoding directly into target Pydantic V2 model.<br>5. Discarding of raw markdown backticks and conversational fluff before parsing. |
| **F-GEN-06** | Deterministic Offline Mock Generator | 1. Predictable offline candidate synthesis for all 7 ministries.<br>2. Seed-deterministic reproducibility across repeated invocations.<br>3. Generation of intentionally flawed candidates for test harnesses.<br>4. Zero external network socket calls during mock operation.<br>5. Conformance of mock outputs to valid Pydantic V2 schemas. |
| **F-DAG-01** | DAG Topology Coordinator ($|V|=7, |E|=11$) | 1. Validation of DAG acyclicity (topological ordering).<br>2. Dependency resolution: Node 1 (Strategy) precedes all downstream nodes.<br>3. Dependency resolution: Nodes 2, 3, 4 execute before Nodes 5, 6, 7.<br>4. Markov Blanket isolation: nodes receive only brief and direct parents' outputs.<br>5. Parallel readiness detection for independent nodes. |
| **F-DAG-02** | 10-State Node FSM | 1. State transition from `STATE_IDLE` to `STATE_INPUT_VALIDATION`.<br>2. State transition through `STATE_SYSTEM2_GENERATE` and `STATE_SYSTEM1_FILTER`.<br>3. State transition through `STATE_STAGE_GATE_VERIFY` and `STATE_CROSS_ARBITRATION`.<br>4. Final commitment transition to `STATE_COMMITTED` with SHA-256 hash.<br>5. Exception transitions to `STATE_SAGA_COMPENSATION` and `STATE_TERMINAL_FAILED`. |
| **F-DAG-03** | Saga Transaction Coordinator ($T_k / C_k$) | 1. Forward execution registration of transaction $T_k$.<br>2. Compensation execution $C_k$ on downstream node veto.<br>3. Rollback of artifact state and cache invalidation.<br>4. Transmission of deterministic failure feedback to target node.<br>5. Successful re-execution and commitment after compensation. |
| **F-DAG-04** | Therac-25 Race Condition Resolution Flow | 1. Simulation of Node 5 (System Analysis) proposing un-interlocked fast async operation.<br>2. Node 6 (Hardware) detecting physical actuator latency (8000 ms) and vetoing.<br>3. Saga coordinator triggering $C_5$ with interlock prescription.<br>4. Node 5 regenerating contract with `hardware_interlocks_required = True`.<br>5. Node 6 verifying updated contract and lifting veto. |
| **F-DAG-05** | Simplex Fail-Safe Downscaling ($\tau_{\max} \le 3$) | 1. Tracking of retry count per node ($\tau \le 3$).<br>2. Tracking of global DAG agreement iterations ($K \le 10$).<br>3. Downscaling action on $\tau = 3$: reduction of cluster size.<br>4. Downscaling action: disabling discrete GPU and falling back to NPU.<br>5. Halting with structured failure report if downscaling cannot satisfy budget. |
| **F-DAG-06** | Zero-Trust Verification Gate Integration | 1. Integration of `gost_verifier.py` checking GOST 34.602 sections.<br>2. Integration of `intent_ministry.py` verifying bidirectional AC coverage.<br>3. Integration of `cdd_tdd_engine.py` checking Hoare logic invariants.<br>4. Integration of `cross_arbiter.py` validating budget vs hardware costs.<br>5. Gate threshold enforcement (overall score >= 90 required for pass). |
| **F-CLI-01** | CLI `orchestrate` Subcommand | 1. CLI parsing of `--prompt` and `--intent` arguments.<br>2. CLI parsing of `--output-dir` and `--mock` flags.<br>3. Correct exit code 0 on successful pipeline completion.<br>4. Non-zero exit code and error message on invalid intent file path.<br>5. Verification of console output banner and progress tracking. |
| **F-CLI-02** | CLI `KeyError: 'occurrences'` Regression Fix | 1. Execution of ISO 29148 check with NLP spaCy lemmatization enabled.<br>2. Safe access to fuzzy terms findings using `.get('occurrences', 1)`.<br>3. Formatting of single-word violations without KeyError crash.<br>4. Formatting of multi-word violations without KeyError crash.<br>5. Verification that `cli.py cmd_verify` exits cleanly with score report. |
| **F-CLI-03** | Production of 7 Validated JSON Artifacts | 1. Production of `PRD_Specification.json` in output directory.<br>2. Production of `Unit_Economics_Budget.json` in output directory.<br>3. Production of `Compliance_Attestation.json` in output directory.<br>4. Production of `Security_Policy.agentpolicy` in output directory.<br>5. Production of `System_Contracts.json`, `Hardware_Runtime_Manifest.json`, `Release_Certified_Artifacts.json`. |
| **F-E2E-01** | Complete E2E Suite Execution (Tiers 1-4) | 1. Execution via `python -m unittest discover -s core -p "test_e2e_pipeline.py"`.<br>2. Execution via `python -m unittest discover -s core -p "test_*.py"`.<br>3. 100% pass rate across all test suites.<br>4. Zero unhandled exceptions or test crashes.<br>5. Execution duration within reasonable development bounds ($< 30$ seconds). |
| **F-E2E-02** | Adversarial Coverage Hardening (Tier 5) | 1. Resistance against prompt injection escape attempts.<br>2. Resistance against Semantic Chameleon unmapped rule injection.<br>3. Rejection of corrupted JSON structures and type perturbations.<br>4. Resilience under simulated key pool depletion.<br>5. Rejection of astronomical numbers, negative limits, and NaN values. |

---

### Tier 2: Boundary & Corner Cases (>=5 Test Cases per Feature for All 30 Features)

Tier 2 targets boundary conditions, limits, edge cases, and unexpected input combinations:

1. **F-SCH-01 (Strategy Boundary)**:
   - AC ID with min length pattern `AC-A-1`.
   - Business rule with description exactly 10 characters (boundary).
   - Empty personas list (violates `min_length=1`).
   - AC containing whitespace-only strings.
   - Circular rule references or rules referencing non-existent AC IDs.
2. **F-SCH-02 (Finance Boundary)**:
   - $LTV/CAC = 2.999$ (strictly below 3.0, must reject).
   - $LTV/CAC = 3.000$ (exact boundary, must accept).
   - Target margin = $14.99\%$ (strictly below 15.0%, must reject).
   - Target margin = $15.00\%$ (exact boundary, must accept).
   - Break-even period = 24 months (accepted) vs 25 months (rejected).
3. **F-SCH-03 (Legal Boundary)**:
   - `ai_act_risk_category = "UNACCEPTABLE"` (must raise `ValueError`).
   - `ai_act_risk_category = "HIGH"` (acceptable boundary).
   - Unknown FZ-152 level (e.g. `УЗ-5`, must be rejected).
   - Empty jurisdiction list (must fail `min_length=1`).
   - Empty approved OSS licenses list.
4. **F-SCH-04 (Security Boundary)**:
   - STRIDE matrix with exactly 5 categories (missing one category, must reject).
   - STRIDE matrix with 6 categories each having 1 threat (exact boundary, must accept).
   - Rate limit RPS = 0 (rejected, must be > 0).
   - Rate limit RPS = 1000 (accepted boundary) vs 1001 (rejected).
   - Empty auth mechanisms list (rejected).
5. **F-SCH-05 (System Analysis Boundary)**:
   - Cyclic dependencies flag `cyclic_dependencies_detected = True` (must raise `ValueError`).
   - Endpoint timeout = 5000 ms (accepted) vs 5001 ms (rejected).
   - Endpoint path with trailing slashes, empty path, or malformed URL patterns.
   - Non-idempotent POST endpoint vs idempotent GET/PUT.
   - Empty endpoints list (violates `min_length=1`).
6. **F-SCH-06 (Hardware Boundary)**:
   - RAM budget = 512.0 MB (accepted) vs 512.1 MB (rejected).
   - Latency p99 = 50.0 ms (accepted) vs 50.1 ms (rejected).
   - Physical actuator latency = 1000.0 ms without interlocks (accepted).
   - Physical actuator latency = 1000.1 ms without interlocks (Therac-25 violation, rejected).
   - Physical actuator latency = 8000.0 ms WITH interlocks (accepted).
7. **F-SCH-07 (Quality Boundary)**:
   - ISO 29148 score = 84.99 (rejected) vs 85.00 (accepted).
   - RTM coverage = 99.99% (rejected) vs 100.00% (accepted).
   - Mutation score = 94.99% (rejected) vs 95.00% (accepted).
   - Brier score = 0.0400 (accepted) vs 0.0401 (rejected).
   - SHA-256 signature length = 63 chars (rejected) vs 64 chars (accepted).
8. **F-SCH-08 (Speed Benchmark Boundary)**:
   - Execution time measured over 100 iterations with mean < 1 ms.
   - Large payload with 1,000 invalid items rejected in < 5 ms.
   - High-concurrency simultaneous invalid object parsing.
   - Memory overhead during rejection remaining constant ($O(1)$ leak check).
   - Cold start rejection duration <= 2 ms.
9. **F-NPU-01 (NPU Fast-Path Boundary)**:
   - Candidate with zero occurrences of forbidden words (receives maximum baseline score).
   - Candidate with all forbidden words (heavily penalized).
   - Empty candidate dictionary handling without NullPointerException.
   - Extreme embedding distance calculation (orthogonal vs identical vectors).
   - OpenVINO runtime error simulated triggering graceful CPU fallback.
10. **F-NPU-02 (Decisions API Boundary)**:
    - OpenRouter API returning HTTP 408 / Timeout (fallback to Tier 1A).
    - API returning empty choices list.
    - Malformed JSON returned from Decisions endpoint.
    - Brier score exactly 0.04 boundary validation.
    - High-frequency decision requests under rate pressure.
11. **F-NPU-03 (L-MOPA Vector Boundary)**:
    - Vector with all components at theoretical maximum $(1, 1, 1, \text{high}, 1)$.
    - Vector with all components at minimum $(0, 0, 0, 0, 0)$.
    - Statistical indistinguishability threshold $\epsilon = 0.0$ vs $\epsilon = 0.05$.
    - Negative resource efficiency values handling.
    - Invariant ordering preservation: priority of $F_1$ over $F_2$, $F_2$ over $F_3$, etc.
12. **F-NPU-04 ($F_1=0$ Gate Boundary)**:
    - Candidate with $F_1 = 0$ and $F_2 = 1.0, F_3 = 1.0, F_4 = 1.0, F_5 = 1.0$ (must be rejected).
    - Candidate with $F_1 = 1.0$ and $F_2 = 0.5$ (must defeat the above candidate).
    - Multiple candidates all having $F_1 = 0$ (must return empty/None).
    - Candidate with $F_1$ fluctuating near float boundary ($0.999 \to$ treated as non-binary or checked against strict invariant).
    - Invariant violation in nested sub-model propagating to $F_1 = 0$.
13. **F-NPU-05 (Mahalanobis Distance Boundary)**:
    - Collinear objective components leading to singular covariance matrix (handled via pseudo-inverse/regularization).
    - Zero variance in a specific objective across candidates.
    - Single candidate remaining on Pareto front (trivial distance calculation).
    - Candidate exactly coinciding with Utopian point $\vec{F}^*$ (distance = 0).
    - Equidistant candidates resolved deterministically by secondary key.
14. **F-GEN-01 (Stratified Ensemble Boundary)**:
    - Minimum candidates requested $N=1$ (fallback to balanced).
    - Maximum candidates requested $N=10$ (bounded to 5).
    - Extreme temperature values $T=0.0$ and $T=1.0$ handled safely.
    - Identical random seed producing identical candidate output.
    - Diversity check ensuring candidates across the 5 profiles have distinct attributes.
15. **F-GEN-02 (Key Rotation Boundary)**:
    - Empty key pool handling (raises configuration exception).
    - Single active key pool handling (rotation loops to same key without crash).
    - All 5 keys returning HTTP 429 simultaneously.
    - Rapid sequential key rotation across 100 requests.
    - Key masking in logs preventing token credential leakage.
16. **F-GEN-03 (Rate Limiter Boundary)**:
    - Requesting 20 tokens in single burst (all permitted).
    - Requesting 21st token immediately (delayed or queued).
    - Token refill calculation after exactly 60 seconds (full bucket restored).
    - Jitter calculation producing strictly positive numbers ($t > 0$).
    - Zero-token initial bucket behavior.
17. **F-GEN-04 (Circuit Breaker Boundary)**:
    - Exactly 2 failures (circuit remains CLOSED).
    - 3rd consecutive failure trips circuit to OPEN.
    - Request arriving at $t = 59.9$s of cooldown (rejected / circuit OPEN).
    - Request arriving at $t = 60.1$s of cooldown (circuit transitions to HALF-OPEN).
    - Successful request in HALF-OPEN resets failure counter to 0 (circuit CLOSED).
18. **F-GEN-05 (Quarantine Boundary)**:
    - Prompt containing closing tag `</user_brief_quarantine>` inside user input (properly escaped).
    - Prompt containing Unicode zero-width spaces and control characters.
    - Large prompt payload (100 KB) sanitized without buffer overflow.
    - JSON response enclosed in nested markdown fences ```` ```json ... ``` ```` correctly stripped.
    - Truncated JSON response triggering immediate syntax error handling.
19. **F-GEN-06 (Mock Generator Boundary)**:
    - Unknown ministry ID requested (handled safely).
    - Zero candidate count requested.
    - Mock generator memory footprint remains $< 10$ MB.
    - Deterministic output matching hardcoded snapshot on fixed seed.
    - Mock generation latency $< 5$ ms per candidate.
20. **F-DAG-01 (DAG Topology Boundary)**:
    - Graph with isolated vertex (detected and rejected).
    - Insertion of cyclic edge (e.g. Node 7 $\to$ Node 1) detected by topological sort.
    - Verification that Markov Blanket for Node 6 contains only its direct parents (Node 4 and Node 5).
    - Simultaneous execution of independent nodes (Node 2 and Node 5 parallel branches).
    - Empty context dictionary passed to root node.
21. **F-DAG-02 (Node FSM Boundary)**:
    - Invalid state transition attempt (e.g. `STATE_IDLE` direct to `STATE_COMMITTED` raises `IllegalStateTransitionError`).
    - Multiple consecutive calls to commit on already committed node.
    - FSM state serialization and deserialization across crashes.
    - Error in `STATE_SYSTEM2_GENERATE` correctly routing to `STATE_SAGA_COMPENSATION`.
    - Maximum state transition history retention.
22. **F-DAG-03 (Saga Rollback Boundary)**:
    - Compensation called on root node (Node 1) without parents.
    - Compensation called on node with multiple dependent children.
    - Compensation action itself throwing an exception (handled with terminal fail-safe).
    - Double compensation invocation on same node (idempotent).
    - Verification that compensated node state is cleared from shared blackboard.
23. **F-DAG-04 (Therac-25 Boundary)**:
    - Hardware latency at boundary $1000$ ms (no veto) vs $1001$ ms (veto triggered).
    - Prescription message containing exact keywords `"Hardware Interlock"`.
    - Node 5 re-executing with prescription and producing `hardware_interlocks_required = True`.
    - Verification that re-verification succeeds and pipeline continues to Node 7.
    - Simulated repeated veto triggering Simplex downscaling after 3 tries.
24. **F-DAG-05 (Simplex Downscaling Boundary)**:
    - Retry count $\tau = 1, 2$ permits re-prompting.
    - Retry count $\tau = 3$ triggers algorithmic downscaling.
    - Cluster size downscaled from 1 to 0 (cannot downscale further, triggers terminal failure).
    - Global budget $K = 10$ iterations reached (aborts whole DAG gracefully).
    - Downscaled parameters written to audit log with rationale.
25. **F-DAG-06 (Zero-Trust Gate Boundary)**:
    - GOST verifier running on document missing exactly 1 mandatory section (overall score drops, gate fails).
    - Intent verifier running on PRD with 1 unmapped business rule (gate fails with `Adversarial Hallucination`).
    - CDD-TDD engine verifying invalid Hoare precondition $\{P\}$ (gate fails).
    - Cross-ministry arbiter encountering negative budget (gate fails immediately).
    - Gate score at boundary $89.9$ (fails) vs $90.0$ (passes).
26. **F-CLI-01 (CLI Execution Boundary)**:
    - CLI called with `--help` prints help and returns exit code 0.
    - CLI called with non-existent intent file returns error and exit code 2.
    - CLI called with relative vs absolute output directory paths.
    - CLI called with empty prompt string `""` handled with validation message.
    - Concurrent CLI invocations writing to separate output directories.
27. **F-CLI-02 (`KeyError: 'occurrences'` Boundary)**:
    - Finding dict with key `"occurrences": 3` formatted correctly as `"(3x)"`.
    - Finding dict with missing key `"occurrences"` formatted safely as `"(1x)"` or omitted without crash.
    - Finding dict with empty dictionary `{}` handled safely.
    - Finding list containing 0 violations formatted as clean pass.
    - Multiple fuzzy terms in single sentence handled without index collision.
28. **F-CLI-03 (7 Artifacts Boundary)**:
    - Output directory does not exist prior to run (CLI auto-creates it).
    - Output directory has read-only permissions (clean error reported).
    - Verification that all 7 files have valid JSON syntax and matching schemas.
    - Verification that `Release_Certified_Artifacts.json` contains valid SHA-256 digests of the other 6 files.
    - Artifact file sizes within expected bounds (1 KB to 500 KB).
29. **F-E2E-01 (E2E Suite Boundary)**:
    - Running test suite with zero environment variables set (passes).
    - Running test suite on Windows paths containing spaces and Cyrillic characters.
    - Test runner stdout and stderr configured for UTF-8 without unicode encoding errors.
    - Fast test teardown cleaning up all temporary directories.
    - Zero lingering background threads or socket leaks.
30. **F-E2E-02 (Adversarial Boundary)**:
    - Extreme nested JSON depth (e.g. 50 levels of brackets).
    - SQL injection and command injection strings inside prompt arguments.
    - Integer overflow inputs (e.g. budget = $10^{18}$).
    - Floating point NaN, Inf, and -Inf values in numerical fields.
    - Null-byte strings `\x00` in requirement descriptions.

---

### Tier 3: Cross-Feature Interactions (Pairwise Combinations)

Tier 3 exercises interactions across multiple subsystems:

1. **Schema Validation $\times$ L-MOPA Filtering (F-SCH-01..07 $\times$ F-NPU-03..04)**:
   - When an ensemble generator produces 5 candidates, Pydantic V2 schemas filter invalid payloads, setting $F_1 = 0$.
   - L-MOPA verifies that even if an invalid candidate has the highest semantic similarity ($F_3$) or lowest OPEX ($F_4$), it is discarded before reaching the Pareto front.
2. **Saga Rollback $\times$ Zero-Trust Stage Gate (F-DAG-03 $\times$ F-DAG-06)**:
   - Node 5 passes initial schema validation, but fails `IntentMinistryValidator` because a business rule lacks `source_ac_id`.
   - The Stage Gate triggers a Saga compensating transaction $C_5$, re-prompting Node 5 with explicit failure feedback.
   - Upon re-generation, the rule is linked to an AC, the gate passes, and Node 5 is committed.
3. **Hardware Latency $\times$ Simplex Downscaling (F-SCH-06 $\times$ F-DAG-04 $\times$ F-DAG-05)**:
   - Simulated Therac-25 race condition: Actuator latency is 8000 ms, software expects 50 ms.
   - Repeated re-prompting fails to resolve hardware latency constraints.
   - At retry $\tau = 3$, Simplex Fail-Safe downscales the architecture: downscaling cluster size or forcing hardware interlocks and synchronous polling.
4. **Key Rotation $\times$ Token-Bucket Rate Limiter $\times$ Circuit Breaker (F-GEN-02 $\times$ F-GEN-03 $\times$ F-GEN-04)**:
   - Under heavy load, the generator drains tokens from the bucket.
   - When HTTP 429 is encountered, key rotation switches to the next key.
   - If all 5 keys encounter 429s within 3 consecutive attempts, the Circuit Breaker trips to OPEN, falling back to local deterministic mock generation.
5. **CLI End-to-End Execution $\times$ Full 7-Artifact Manifest (F-CLI-01 $\times$ F-CLI-03 $\times$ F-SCH-07)**:
   - The CLI orchestrates the full 7-ministry DAG.
   - All 7 JSON artifacts are created on disk.
   - `Release_Certified_Artifacts.json` computes the cryptographic SHA-256 hash of each file, validating full end-to-end integrity.

---

### Tier 4: Real-World Scenarios

#### Scenario 4.1: The Therac-25 Medical Linear Accelerator Benchmark
- **Domain**: Radiation Therapy Machine with dual mode: low-power Electron Beam (25 kV) vs high-power Megavolt X-ray (25 MeV).
- **Hazard**: Optical beam flattener turntable requires 8,000 ms of physical actuator motion to position heavy tungsten target.
- **Race Condition**: Operator enters commands rapidly within 8 seconds ($T_{\text{operator}} = 4000\text{ ms} < T_{\text{turntable}} = 8000\text{ ms}$). Software switches to 25 MeV before flattener is in place, causing massive lethal radiation overdose without hardware interlocks.
- **Test Flow**:
  1. Input brief specifies medical accelerator with 8000 ms actuator latency.
  2. Node 5 (System Analysis) generates API specification with asynchronous non-blocking command dispatch.
  3. Node 6 (Hardware Runtime) detects $T_{\text{actuator}} > 1000\text{ ms}$ and `hardware_interlocks_required == False`.
  4. Node 6 triggers **VETO**, invoking Saga compensation $C_5$.
  5. Orchestrator transmits prescription: *"Mandatory hardware interlock switch and synchronous turntable status polling required."*
  6. Node 5 regenerates specification incorporating physical interlocks.
  7. Node 6 verifies and approves; Node 7 (V&V) signs release certificate with cryptographic SHA-256 hash.

#### Scenario 4.2: Enterprise FinTech Core (High-Assurance Banking)
- **Domain**: Automated Core Banking & Payment Clearing Gateway.
- **Regulatory Invariants**: 152-FZ УЗ-1 (highest data protection level with Russian data localization), 54-FZ fiscal receipts, EU AI Act High-Risk classification, STRIDE full mitigation (mTLS + JWT ED25519).
- **Economic Invariants**: $LTV/CAC \ge 4.5$, transaction target margin $\ge 20\%$, monthly OPEX $\le 500,000$ RUB.
- **Test Flow**:
  1. System 2 synthesizes financial and legal contracts.
  2. Boundary stress test attempts to pass $LTV/CAC = 2.8$ $\to$ immediately rejected with `ValidationError`.
  3. Compliant contracts generated, passing through NPU L-MOPA selection with high security score $F_2 \ge 0.95$.
  4. All 7 ministry artifacts committed and written to disk with full zero-trust audit trail.

---

## 3. Test Runner Commands & CI/CD Integration

### 3.1. Standard Unittest Invocation
```bash
# Execute the comprehensive E2E test suite:
python -m unittest discover -s core -p "test_e2e_pipeline.py" -v

# Execute all project unit tests:
python -m unittest discover -s core -p "test_*.py" -v
```

### 3.2. Verification Criteria
- **Pass Rate**: 100% (zero failures, zero errors).
- **Execution Time**: Under 30 seconds for entire suite.
- **Hermeticity**: Zero external internet network dependencies.
