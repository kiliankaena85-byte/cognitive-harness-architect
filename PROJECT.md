# Project: Universal Cognitive Decomposition Engine (7-Ministry Generative Pipeline)

## Architecture
- **Paradigm**: Dual-System Cognitive Pipeline with Formal Zero-Trust Verification.
  - **System 2 (Generative)**: Stochastic ensemble generation ($N=3..5$ stratified candidates: Defensive, Balanced, High-Throughput, Frugal, Adversarial) using OpenRouter LLMs with key rotation, token bucket rate limiting (20 RPM), circuit breaker, and Markov Blanket context isolation.
  - **System 1 (Reflexive/Evaluative)**: Two-tier fast-path evaluator (Tier 1A OpenVINO INT8 ModernBERT/BGE-small on Intel AI Boost NPU with CPU fallback; Tier 1B Together Tev1-4B Decisions API via OpenRouter `/api/alpha/decisions`).
  - **L-MOPA Arbiter**: Lexicographic Multi-Objective Pareto Arbiter evaluating $\vec{F}(h) = (F_{\text{HardInvariants}}, F_{\text{Security}}, F_{\text{Intent}}, F_{\text{ResourceEff}}, F_{\text{MDL}})$ to eliminate additive weight skew, strictly disqualifying $F_1=0$.
  - **DAG & Saga Orchestrator**: 7-node DAG ($|V|=7, |E|=11$) controlled by a 10-state FSM with Saga compensating transactions ($C_k$), resolving race conditions (Therac-25 pattern) and enforcing Simplex Fail-Safe downscaling ($\tau_{\max} \le 3, K_{\max} \le 10$).
  - **Deterministic Gates**: Verification gates (`gost_verifier.py`, `cross_arbiter.py`, `cdd_tdd_engine.py`, `intent_ministry.py`) ensuring ISO 29148, GOST 34.602, GOST 56939, and Hoare logic invariants.
  - **CLI**: `cli.py orchestrate --prompt "<task>" --intent "<gherkin_file>" --output-dir "<dir>" --mock` producing all 7 validated JSON artifacts.

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | F-SCH-01 | StrategyCJMContract & GherkinScenario/BusinessRule with bidirectional traceability (`source_ac_id`) | M1 | Survey / R1.1 |
| 2 | F-SCH-02 | FinanceBudgetContract with LTV/CAC >= 3.0, margin >= 15%, OPEX/CAPEX, break-even period <= 24 mo | M1 | Survey / R1.2 |
| 3 | F-SCH-03 | LegalComplianceContract with 152-FZ levels, 54-FZ fiscal, EU AI Act risk != UNACCEPTABLE, OSS licenses | M1 | Survey / R1.3 |
| 4 | F-SCH-04 | SecurityPolicyContract with 6 STRIDE categories complete coverage, zero-trust, auth, rate limiting, encryption | M1 | Survey / R1.4 |
| 5 | F-SCH-05 | SystemAnalysisContract with OpenAPI 3.1, ApiEndpoint idempotency/timeouts, acyclic dependency validator | M1 | Survey / R1.5 |
| 6 | F-SCH-06 | HardwareRuntimeContract with Intel Core Ultra 5 125H / Intel AI Boost NPU constraints (RAM <= 512MB, p99 <= 50ms), Therac-25 actuator latency > 1000ms interlock validator | M1 | Survey / R1.6 |
| 7 | F-SCH-07 | VVQualityContract with GOST 34.602 sections, ISO 29148 score >= 85, RTM coverage >= 100%, mutation >= 95%, Brier <= 0.04, Hoare >= 7, SHA-256 release signature | M1 | Survey / R1.7 |
| 8 | F-SCH-08 | Sub-millisecond schema rejection benchmark (< 1 ms ValidationError on invalid payloads) | M1 | Survey / Criteria |
| 9 | F-NPU-01 | Tier 1A local fast-path embedding/semantic scorer on Intel AI Boost NPU / OpenVINO INT8 with CPU fallback | M2 | Survey / R2 |
| 10 | F-NPU-02 | Tier 1B Together Tev1-4B Decisions API via OpenRouter (`/api/alpha/decisions`) with transparent fallback | M2 | Survey / R2 |
| 11 | F-NPU-03 | L-MOPA vector evaluation $\vec{F}(h) = (F_{\text{HardInvariants}}, F_{\text{Security}}, F_{\text{Intent}}, F_{\text{ResourceEff}}, F_{\text{MDL}})$ | M2 | Survey / R2 |
| 12 | F-NPU-04 | L-MOPA strict $F_1 = 0$ disqualification (Hard Invariant feasibility gate) | M2 | Survey / Criteria |
| 13 | F-NPU-05 | L-MOPA Mahalanobis distance tie-breaker to utopian point $\vec{F}^*$ | M2 | Survey / R2 |
| 14 | F-GEN-01 | System 2 ensemble generator of $N = 3 \dots 5$ stratified candidates per ministry (Defensive, Balanced, High-Throughput, Frugal, Adversarial) | M3 | Survey / R3 |
| 15 | F-GEN-02 | Key pool rotation across 5 API keys with round-robin ($K_{\text{next}} = (K_{\text{idx}} + 1) \pmod 5$) | M3 | Survey / R3 |
| 16 | F-GEN-03 | Token-Bucket rate limiter (20 RPM) and exponential backoff with randomized jitter | M3 | Survey / R3 |
| 17 | F-GEN-04 | 3-strike Circuit Breaker with 60s cooldown and model fallback ladder | M3 | Survey / R3 |
| 18 | F-GEN-05 | Prompt injection quarantine (`<user_brief_quarantine>`) and constrained JSON decoding directly into Pydantic V2 schemas | M3 | Survey / R3 |
| 19 | F-GEN-06 | Deterministic offline mock generator for reliable, reproducible testing | M3 | Survey / R3 |
| 20 | F-DAG-01 | DAG topology coordinator for 7 ministries ($|V|=7, |E|=11$) with Markov Blanket context isolation | M4 | Survey / R4 |
| 21 | F-DAG-02 | 10-state node FSM (`STATE_IDLE` through `STATE_COMMITTED` / `STATE_TERMINAL_FAILED`) | M4 | Survey / R4 |
| 22 | F-DAG-03 | Saga transaction coordinator ($T_k / C_k$) with compensating rollback | M4 | Survey / R4 |
| 23 | F-DAG-04 | Therac-25 race condition resolution flow (Node 6 vetoes Node 5, triggers $C_5$, prescribes interlocks/synchronous polling, re-executes Node 5) | M4 | Survey / R4 |
| 24 | F-DAG-05 | Simplex Fail-Safe downscaling on retry limit exhaustion ($\tau_{\max} \le 3$, $K_{\max} \le 10$) | M4 | Survey / R4 |
| 25 | F-DAG-06 | Zero-trust gate verification integration (`gost_verifier`, `cross_arbiter`, `cdd_tdd_engine`, `intent_ministry`) | M4 | Survey / R4 |
| 26 | F-CLI-01 | CLI `orchestrate` command: `python cli.py orchestrate --prompt "<task>" --intent "<gherkin_file>"` | M5 | Survey / R5 |
| 27 | F-CLI-02 | Fix `cli.py:409` `KeyError: 'occurrences'` bug | M5 | Survey / Bug |
| 28 | F-CLI-03 | Production of 7 validated JSON artifacts in output directory | M5 | Survey / R5 |
| 29 | F-E2E-01 | Complete E2E test suite (Tiers 1-4: Feature, Boundary, Pairwise, Real-world Therac-25) passing 100% via `python -m unittest discover -s core -p "test_*.py"` | M5 | Survey / Criteria |
| 30 | F-E2E-02 | Phase 2 Adversarial coverage hardening (Tier 5) | M5 | Project Pattern |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | Pydantic V2 Contract Schemas | `core/schemas/` package with 7 contracts, validators, tests `core/test_schemas.py` | none | DONE |
| M2 | System 1 NPU & Decisions Pareto Arbiter | `core/npu_darwinian_loop.py` two-tier evaluator, L-MOPA vector & selection, tests `core/test_npu_darwinian_loop.py` | M1 | DONE |
| M3 | System 2 Multi-Hypothesis Generator | `core/ministries/nodes.py` stratified ensemble, key rotation, rate limiting, circuit breaker, mock generator, tests `core/test_ministry_nodes.py` | M1 | DONE |
| M4 | DAG Orchestrator with Saga Transactions | `core/orchestrator.py` 7-node DAG, 10-state FSM, Saga coordinator, Therac-25 rollback, Simplex fail-safe, zero-trust gate integration, tests `core/test_orchestrator.py` | M1, M2, M3 | DONE |
| M5 | CLI Integration & Final Verification | `cli.py orchestrate` subcommand, fix `cli.py:409`, E2E test suite pass (Tiers 1-4), Tier 5 adversarial coverage hardening | M4, E2E-Track | IN_PROGRESS |
| E2E | E2E Testing Track | Design & implement opaque-box test suite (Tiers 1-4) in `core/test_e2e_pipeline.py`, publish `TEST_INFRA.md` & `TEST_READY.md` | M1 | DONE |

## Interface Contracts

### M1: `core/schemas/` Exports
- `StrategyCJMContract`, `GherkinScenario`, `BusinessRule`
- `FinanceBudgetContract`
- `LegalComplianceContract`, `PersonalDataProcessing`
- `SecurityPolicyContract`, `StrideThreat`
- `SystemAnalysisContract`, `ApiEndpoint`
- `HardwareRuntimeContract`
- `VVQualityContract`
- All models inherit `pydantic.BaseModel` and enforce validation on invalid data, throwing `pydantic.ValidationError`.

### M2: `core/npu_darwinian_loop.py` Exports
- `class NpuParetoSelector`:
  - `__init__(self, use_npu: bool = True, use_decisions_api: bool = False, openrouter_config_path: Optional[str] = None)`
  - `evaluate_candidate(self, candidate_dict: Dict[str, Any], context: Dict[str, Any]) -> Tuple[float, float, float, float, float]` -> returns $\vec{F}(h) = (F_1, F_2, F_3, F_4, F_5)$.
  - `select_dominant(self, candidates: List[Dict[str, Any]], context: Dict[str, Any]) -> Optional[Dict[str, Any]]` -> returns single dominant candidate or raises/returns None if all disqualified.

### M3: `core/ministries/nodes.py` Exports
- `class MinistryNode`:
  - `__init__(self, ministry_id: int, ministry_name: str, schema_class: Type[BaseModel], use_mock: bool = True)`
  - `generate_hypotheses(self, markov_blanket: Dict[str, Any], n_candidates: int = 5) -> List[Dict[str, Any]]`
- `class OpenRouterResilienceManager`:
  - Handles key rotation, token bucket rate limiter, exponential backoff, circuit breaker.

### M4: `core/orchestrator.py` Exports
- `class DagOrchestrator`:
  - `__init__(self, use_mock: bool = True, output_dir: Optional[str] = None)`
  - `run(self, prompt: str, intent_path: Optional[str] = None) -> Dict[str, Any]` -> returns dict of 7 validated artifacts.
  - `execute_saga_compensation(self, vetoing_node: int, target_node: int, prescription: str) -> None`
  - `apply_simplex_downgrade(self, node_id: int) -> None`

## Code Layout
- `core/schemas/`:
  - `__init__.py`: Package re-exports
  - `strategy.py`: `StrategyCJMContract`, `GherkinScenario`, `BusinessRule`
  - `finance.py`: `FinanceBudgetContract`
  - `legal.py`: `LegalComplianceContract`, `PersonalDataProcessing`
  - `security.py`: `SecurityPolicyContract`, `StrideThreat`
  - `analysis.py`: `SystemAnalysisContract`, `ApiEndpoint`
  - `hardware.py`: `HardwareRuntimeContract`
  - `quality.py`: `VVQualityContract`
- `core/npu_darwinian_loop.py`: Two-tier evaluator & L-MOPA selector
- `core/ministries/nodes.py`: System 2 multi-hypothesis ensemble generator & OpenRouter resilience
- `core/orchestrator.py`: DAG FSM & Saga transaction coordinator
- `cli.py`: CLI interface with `orchestrate` subcommand
- `core/test_schemas.py`: Milestone 1 unit & PBT test suite
- `core/test_npu_darwinian_loop.py`: Milestone 2 test suite
- `core/test_ministry_nodes.py`: Milestone 3 test suite
- `core/test_orchestrator.py`: Milestone 4 test suite
- `core/test_e2e_pipeline.py`: E2E Testing Track test suite (Tiers 1-4)
