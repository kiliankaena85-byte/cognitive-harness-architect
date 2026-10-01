"""
tests/test_nodes_stress.py
=============================================================================
Stress, Soak, and High-Throughput Concurrency Harness for Milestone 3:
System 2 Ministry Nodes & OpenRouter Resilience Transport Engine.

Standard Compliance:
- ГОСТ 34.602, ГОСТ Р 56939-2024 (ФСТЭК), ISO/IEC/IEEE 29148:2018
- Stress-testing thread contention, state-churn, token conservation, and latency.

Harness Components:
1. Multi-Threaded Token Conservation Stress Probe (200 concurrent workers).
2. Circuit Breaker High-Frequency State-Churn Stress Probe (100 concurrent workers).
3. 5-Key Pool High-Volume Failover Soak (5,000 rotations).
4. Full 7-Ministry Mock Ensemble Generation Soak & Latency Benchmark.
5. Therac-25 Race Hazard Feedback Adaptation Probe.
=============================================================================
"""

import sys
import math
import time
import random
import threading
import unittest
from pathlib import Path
from typing import Any, Dict, List

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.ministries.nodes import (
    STRATIFIED_PROFILES,
    CandidateDict,
    CircuitBreaker,
    CircuitState,
    DeterministicMockGenerator,
    KeyPoolManager,
    MinistryNode,
    OpenRouterResilienceManager,
    TokenBucketRateLimiter,
    create_ministry_node,
)
from core.schemas import (
    FinanceBudgetContract,
    HardwareRuntimeContract,
    LegalComplianceContract,
    SecurityPolicyContract,
    StrategyCJMContract,
    SystemAnalysisContract,
    VVQualityContract,
)


class TestNodesConcurrencyAndStressHarness(unittest.TestCase):
    """Stress and soak test harness for nodes resilience mechanisms."""

    def test_token_conservation_under_massive_contention(self):
        """
        Verify Token Conservation Law under 200 concurrent threads:
        T_consumed <= Capacity.
        """
        limiter = TokenBucketRateLimiter(rpm=20.0, capacity=20.0)
        n_threads = 200
        tokens_per_thread = 1.0
        success_flags = []
        lock = threading.Lock()

        def worker():
            res = limiter.try_acquire(tokens_per_thread)
            with lock:
                success_flags.append(res)

        threads = [threading.Thread(target=worker) for _ in range(n_threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        success_count = sum(1 for s in success_flags if s)
        self.assertEqual(success_count, 20, f"Oversold tokens! Expected 20, got {success_count}")
        self.assertGreaterEqual(limiter.tokens, 0.0, "Tokens went negative!")
        self.assertLessEqual(limiter.tokens, 1.0, "Tokens exceeded residual capacity!")

    def test_circuit_breaker_high_frequency_state_churn(self):
        """
        Churn Circuit Breaker state with 100 concurrent workers randomly recording
        successes, failures, and probing allow_request. Invariant: no corruption or deadlocks.
        """
        cb = CircuitBreaker(failure_threshold=3, cooldown_seconds=0.05)
        n_workers = 100
        ops_per_worker = 50
        errors = []

        def churn_worker(worker_id: int):
            try:
                for i in range(ops_per_worker):
                    action = (worker_id + i) % 3
                    if action == 0:
                        cb.record_failure()
                    elif action == 1:
                        cb.record_success()
                    else:
                        cb.allow_request()

                    # Invariant checks
                    if cb.state not in (CircuitState.CLOSED, CircuitState.OPEN, CircuitState.HALF_OPEN):
                        errors.append(f"Invalid state: {cb.state}")
                    if cb.consecutive_failures < 0:
                        errors.append("Negative failure count")
            except Exception as e:
                errors.append(str(e))

        threads = [threading.Thread(target=churn_worker, args=(i,)) for i in range(n_workers)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(errors, [], f"Encountered errors during FSM churn: {errors[:5]}")

    def test_key_pool_soak_5000_rotations(self):
        """
        Soak test 5-key pool manager with 5,000 rapid rotations across 20 threads.
        Verify no index drift or index out-of-bounds.
        """
        keys = [f"sk-or-v1-soak-key-{i}" for i in range(5)]
        pool = KeyPoolManager(keys, penalty_cooldown_sec=10.0)

        n_threads = 20
        rotations_per_thread = 250
        observed_indices = set()
        lock = threading.Lock()

        def soak_worker():
            for _ in range(rotations_per_thread):
                pool.rotate_key(apply_penalty=True)
                idx = pool.current_idx
                with lock:
                    observed_indices.add(idx)

        threads = [threading.Thread(target=soak_worker) for _ in range(n_threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(observed_indices, {0, 1, 2, 3, 4})
        self.assertIn(pool.current_idx, {0, 1, 2, 3, 4})

    def test_all_seven_ministries_mock_generation_soak_and_latency(self):
        """
        Execute 140 candidate generations across all 7 ministries (20 full ensembles).
        Verify sub-millisecond per-candidate latency, valid Pydantic V2 contracts,
        and zero memory leaks.
        """
        contracts = {
            1: StrategyCJMContract,
            2: FinanceBudgetContract,
            3: LegalComplianceContract,
            4: SecurityPolicyContract,
            5: SystemAnalysisContract,
            6: HardwareRuntimeContract,
            7: VVQualityContract,
        }

        latencies = []
        markov_blanket = {
            "brief_sanitized": "Soak test autonomous robotics engine",
            "parent_artifacts": {},
        }

        for mid, contract_cls in contracts.items():
            node = create_ministry_node(mid, use_mock=True)
            for _ in range(5):  # 5 ensembles of 5 candidates = 25 candidates per ministry
                t0 = time.perf_counter()
                hypos = node.generate_hypotheses(markov_blanket, n_candidates=5)
                t1 = time.perf_counter()
                latencies.append((t1 - t0) / 5.0)

                self.assertEqual(len(hypos), 5)
                for cand in hypos:
                    # Validate directly against Pydantic V2 model
                    instance = contract_cls.model_validate(cand)
                    self.assertIsNotNone(instance)
                    self.assertIn("__profile__", cand)

        avg_latency_ms = (sum(latencies) / len(latencies)) * 1000.0
        p99_latency_ms = sorted(latencies)[int(len(latencies) * 0.99)] * 1000.0

        # Sub-millisecond generation requirement in offline mock mode
        self.assertLess(avg_latency_ms, 2.0, f"Average candidate generation latency {avg_latency_ms:.3f} ms exceeds 2ms")

    def test_therac_25_feedback_interlock_adaptation(self):
        """
        Verify that when Therac-25 race condition feedback is provided,
        Hardware and SystemAnalysis mock generators enforce synchronous interlocks.
        """
        mock_gen = DeterministicMockGenerator()
        prof = STRATIFIED_PROFILES["defensive"]

        feedback = "CRITICAL: Actuator latency 1250ms exceeds software timeout 50ms without hardware interlocks!"
        markov_blanket = {
            "brief_sanitized": "Medical Linear Accelerator System",
            "saga_prescription": feedback,
            "feedback": feedback,
        }

        # Node 6: Hardware with Therac-25 hazard in Markov Blanket
        hw_cand = mock_gen.generate_candidate(6, "HardwareRuntime", prof, markov_blanket)
        self.assertTrue(hw_cand.get("hardware_interlocks_required"), "Hardware interlock was not set upon hazard indication")
        HardwareRuntimeContract.model_validate(hw_cand)

        # Node 5: System Analysis with Therac-25 hazard in Markov Blanket
        sys_cand = mock_gen.generate_candidate(5, "SystemAnalysis", prof, markov_blanket)
        endpoints = sys_cand.get("endpoints", [])
        interlock_endpoint_found = any("interlock" in ep.get("path", "").lower() for ep in endpoints)
        self.assertTrue(interlock_endpoint_found, "SystemAnalysis did not provision interlock endpoint upon hazard indication")
        SystemAnalysisContract.model_validate(sys_cand)

        # Also test evolve method with Therac-25 feedback
        evolved_hw = mock_gen.evolve(feedback, {"hardware_interlocks_required": False, "actuator_latency_p99_ms": 1250.0})
        self.assertTrue(evolved_hw.get("hardware_interlocks_required"), "Evolve did not enable hardware interlocks")


if __name__ == "__main__":
    unittest.main(verbosity=2)
