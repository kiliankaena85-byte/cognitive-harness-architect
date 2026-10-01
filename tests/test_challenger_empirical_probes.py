"""
tests/test_challenger_empirical_probes.py
=============================================================================
Milestone 3 Empirical Challenger Verification & Stress Harness.
Exhaustively stress-tests:
1. TokenBucketRateLimiter: Timing accuracy, quadratic distortion elimination,
   concurrency safety, and timeout semantics.
2. OpenRouterResilienceManager: Circuit breaker state re-checking, outbound HTTP
   halting after 3 failures across max_retries boundaries and error types.
3. DeterministicMockGenerator.evolve(): Therac-25 race condition adaptation
   under English, Russian, case-varied, and adversarial feedback.
=============================================================================
"""

import copy
import hashlib
import json
import socket
import sys
import threading
import time
import unittest
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock, patch

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.ministries.nodes import (
    STRATIFIED_PROFILES,
    CandidateDict,
    CandidateProfile,
    CircuitBreaker,
    CircuitBreakerOpenError,
    CircuitState,
    DeterministicMockGenerator,
    HardwareRuntimeNode,
    KeyPoolManager,
    MinistryNode,
    OpenRouterResilienceManager,
    RateLimitExceededError,
    SecurityQuarantineManager,
    StrategyNode,
    SystemAnalysisNode,
    TokenBucketRateLimiter,
    compute_backoff_delay,
    create_ministry_node,
)
from core.schemas import (
    CONTRACT_SCHEMAS_REGISTRY,
    MINISTRY_ID_MAP,
    HardwareRuntimeContract,
    SystemAnalysisContract,
)


class VirtualClock:
    """Deterministic virtual time controller."""
    def __init__(self, initial_time: float = 1700000000.0):
        self._current_time: float = float(initial_time)

    def time(self) -> float:
        return self._current_time

    def advance(self, seconds: float) -> None:
        self._current_time += float(seconds)


class TestEmpiricalTokenBucketTimingAndDistortion(unittest.TestCase):
    """
    Stress-testing TokenBucketRateLimiter.acquire() timing accuracy
    and verifying zero quadratic distortion.
    """

    def test_acquire_timing_accuracy_wall_clock(self):
        """
        Empirically measure real wall-clock elapsed time vs reported time
        for 60 RPM (1.0 token/sec), capacity=1.0.
        Verifies:
        - Reported time ~ 1.0s.
        - Absolute difference between reported time and real wall-clock time < 0.15s.
        - Old quadratic bug (~5.5s) does NOT occur.
        """
        limiter = TokenBucketRateLimiter(rpm=60.0, capacity=1.0)

        # Drain the single available token
        self.assertTrue(limiter.try_acquire(1.0))
        self.assertFalse(limiter.try_acquire(1.0))

        t_start = time.perf_counter()
        reported_wait = limiter.acquire(1.0)
        t_elapsed = time.perf_counter() - t_start

        # 1. Reported wait must closely match actual elapsed time
        self.assertAlmostEqual(reported_wait, t_elapsed, delta=0.15)

        # 2. Wait must be close to 1.0s (within 0.85s .. 1.25s)
        self.assertGreaterEqual(reported_wait, 0.85)
        self.assertLessEqual(reported_wait, 1.25)

        # 3. Elimination of quadratic accumulation (which was 5.5s)
        self.assertLess(
            reported_wait, 2.0,
            f"Quadratic distortion detected: reported {reported_wait:.3f}s"
        )

    def test_acquire_timing_virtual_clock_multi_rates(self):
        """
        Test timing calculations across multiple RPM rates (20 RPM, 60 RPM, 120 RPM)
        using a virtual clock stepped in deterministic 50ms increments.
        """
        rates = [20.0, 60.0, 120.0]

        for rpm in rates:
            clock = VirtualClock()
            rate = rpm / 60.0
            expected_wait = 1.0 / rate  # seconds for 1 token

            limiter = TokenBucketRateLimiter(rpm=rpm, capacity=1.0, clock_fn=clock.time)

            # Drain
            self.assertTrue(limiter.try_acquire(1.0))
            self.assertEqual(limiter.tokens, 0.0)

            # In virtual time, simulate spinning until acquire succeeds
            # We patch time.sleep to advance our virtual clock by 50ms
            def fake_sleep(dur):
                clock.advance(dur)

            with patch("time.sleep", side_effect=fake_sleep):
                reported = limiter.acquire(1.0)

            # The reported time must equal or slightly exceed expected_wait by at most 1 step (0.1s)
            self.assertGreaterEqual(reported, expected_wait - 0.001)
            self.assertLessEqual(reported, expected_wait + 0.105)

    def test_acquire_timeout_exhaustion(self):
        """
        acquire() must raise RateLimitExceededError when deficit cannot be satisfied
        within the given timeout.
        """
        limiter = TokenBucketRateLimiter(rpm=20.0, capacity=1.0)
        limiter.try_acquire(1.0)  # Drain

        # Need 3.0s to refill 1 token (20 RPM). Timeout = 0.15s
        t0 = time.perf_counter()
        with self.assertRaises(RateLimitExceededError) as ctx:
            limiter.acquire(1.0, timeout=0.15)
        elapsed = time.perf_counter() - t0

        self.assertIn("timed out after waiting", str(ctx.exception))
        self.assertLess(elapsed, 0.5)

    def test_concurrent_multi_threaded_acquire(self):
        """
        Concurrent multi-threaded stress:
        10 threads concurrently attempting to acquire 1 token from a limiter
        with capacity=5, rate=60 RPM.
        All 10 must eventually acquire a token without race conditions,
        corrupt token balance, or deadlock.
        """
        limiter = TokenBucketRateLimiter(rpm=60.0, capacity=5.0)
        acquired_times: List[float] = []
        lock = threading.Lock()

        def worker():
            wait_time = limiter.acquire(1.0, timeout=10.0)
            with lock:
                acquired_times.append(wait_time)

        threads = [threading.Thread(target=worker) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=15.0)
            self.assertFalse(t.is_alive(), "Worker thread deadlocked during acquire")

        self.assertEqual(len(acquired_times), 10)
        # First 5 should have minimal wait (< 0.1s) because capacity=5
        immediate = sum(1 for w in acquired_times if w < 0.1)
        self.assertGreaterEqual(immediate, 4)

    def test_acquire_tokens_exceeding_capacity_with_timeout(self):
        """
        Adversarial edge case: Requesting tokens > capacity must raise RateLimitExceededError
        when timeout is provided, rather than hanging indefinitely.
        """
        limiter = TokenBucketRateLimiter(rpm=60.0, capacity=1.0)
        t0 = time.perf_counter()
        with self.assertRaises(RateLimitExceededError):
            limiter.acquire(tokens=5.0, timeout=0.1)
        elapsed = time.perf_counter() - t0
        self.assertLess(elapsed, 0.3)

    def test_acquire_fractional_tokens(self):
        """
        Rate limiter supports fractional tokens (e.g. 0.5 tokens).
        """
        limiter = TokenBucketRateLimiter(rpm=60.0, capacity=1.0)
        self.assertTrue(limiter.try_acquire(0.5))
        self.assertAlmostEqual(limiter.tokens, 0.5, places=2)
        self.assertTrue(limiter.try_acquire(0.5))
        self.assertAlmostEqual(limiter.tokens, 0.0, places=2)
        self.assertFalse(limiter.try_acquire(0.1))


class TestEmpiricalCircuitBreakerNetworkHalting(unittest.TestCase):
    """
    Stress-testing OpenRouterResilienceManager.execute_request()
    circuit breaker state checks and network request halting.
    """

    def test_execute_request_halts_outbound_calls_after_3_http_failures(self):
        """
        Test that execute_request() halts outbound HTTP requests after exactly
        3 consecutive HTTP 500 failures when max_retries=3.
        Assert that mock_urlopen was invoked exactly 3 times, NOT 4.
        """
        mgr = OpenRouterResilienceManager(
            api_keys=["sk-or-v1-key1"],
            max_retries=3,
            circuit_failure_threshold=3,
        )

        with patch("time.sleep"), patch("urllib.request.urlopen") as mock_url:
            mock_url.side_effect = urllib.error.HTTPError(
                "https://openrouter.ai/api/v1/chat/completions",
                500,
                "Internal Server Error",
                {},
                None,
            )

            with self.assertRaises(CircuitBreakerOpenError):
                mgr.execute_request({"model": "test", "messages": []})

            self.assertEqual(
                mock_url.call_count, 3,
                f"Outbound HTTP call was not halted after 3 failures! Count: {mock_url.call_count}"
            )
            self.assertEqual(mgr.circuit_state, "OPEN")

    def test_execute_request_halts_after_3_failures_even_with_high_max_retries(self):
        """
        Adversarial test: Even if max_retries is set to 10, the 3-strike circuit breaker
        must trip after 3 failures and halt all subsequent retries (attempts 4..10).
        Total HTTP calls must remain strictly 3!
        """
        mgr = OpenRouterResilienceManager(
            api_keys=["sk-or-v1-key1"],
            max_retries=10,
            circuit_failure_threshold=3,
        )

        with patch("time.sleep"), patch("urllib.request.urlopen") as mock_url:
            mock_url.side_effect = urllib.error.HTTPError(
                "https://openrouter.ai/api/v1/chat/completions",
                503,
                "Service Unavailable",
                {},
                None,
            )

            with self.assertRaises(CircuitBreakerOpenError):
                mgr.execute_request({"model": "test", "messages": []})

            self.assertEqual(
                mock_url.call_count, 3,
                f"Circuit breaker failed to halt high max_retries! Count: {mock_url.call_count}"
            )
            self.assertEqual(mgr.circuit_state, "OPEN")

    def test_execute_request_halts_on_non_http_exceptions(self):
        """
        Test that network errors (socket timeouts, URLErrors) are caught, recorded,
        and halt at 3 failures without escaping unhandled.
        """
        mgr = OpenRouterResilienceManager(
            api_keys=["sk-or-v1-key1"],
            max_retries=3,
            circuit_failure_threshold=3,
        )

        with patch("time.sleep"), patch("urllib.request.urlopen") as mock_url:
            mock_url.side_effect = urllib.error.URLError("Connection reset by peer")

            with self.assertRaises(CircuitBreakerOpenError):
                mgr.execute_request({"model": "test", "messages": []})

            self.assertEqual(mock_url.call_count, 3)
            self.assertEqual(mgr.circuit_state, "OPEN")

    def test_execute_request_blocks_immediately_when_already_open(self):
        """
        If the circuit is already in OPEN state before execute_request() is invoked,
        zero network requests must be initiated.
        """
        mgr = OpenRouterResilienceManager(api_keys=["sk-key"])
        # Force breaker to OPEN
        for _ in range(3):
            mgr.record_failure(500)
        self.assertEqual(mgr.circuit_state, "OPEN")

        with patch("urllib.request.urlopen") as mock_url:
            with self.assertRaises(CircuitBreakerOpenError):
                mgr.execute_request({"model": "test"})

            self.assertEqual(mock_url.call_count, 0, "Network request sent while breaker was OPEN!")

    def test_circuit_half_open_recovery_and_re_trip(self):
        """
        Test state transitions during HALF-OPEN state:
        - Transition from OPEN to HALF_OPEN after cooldown.
        - Single probe request allowed.
        - If probe succeeds -> CLOSED.
        - If probe fails -> back to OPEN immediately without extra retries.
        """
        clock = VirtualClock()
        mgr = OpenRouterResilienceManager(api_keys=["sk-key"], clock_fn=clock.time)

        for _ in range(3):
            mgr.record_failure(500)
        self.assertEqual(mgr.circuit_state, "OPEN")

        # Advance past 60s cooldown and evaluate can_request()
        clock.advance(60.1)
        self.assertTrue(mgr.can_request())
        self.assertEqual(mgr.circuit_state, "HALF_OPEN")

        # Probe failure trips back to OPEN immediately
        mgr.record_failure(500)
        self.assertEqual(mgr.circuit_state, "OPEN")
        self.assertFalse(mgr.can_request())

        # Advance again and probe
        clock.advance(60.1)
        self.assertTrue(mgr.can_request())
        self.assertEqual(mgr.circuit_state, "HALF_OPEN")

        # Probe success recovers circuit to CLOSED
        mgr.record_success()
        self.assertEqual(mgr.circuit_state, "CLOSED")
        self.assertEqual(mgr.failure_count, 0)
        self.assertTrue(mgr.can_request())


class TestEmpiricalMockGeneratorEvolution(unittest.TestCase):
    """
    Stress-testing DeterministicMockGenerator.evolve() under multilingual,
    casing, and domain-specific feedback strings.
    """

    def setUp(self):
        self.mock_gen = DeterministicMockGenerator()
        self.bal_prof = STRATIFIED_PROFILES["balanced"]

    def test_evolve_english_race_condition_feedback(self):
        """
        English race condition feedback variations must reliably activate interlocks
        in Node 6 (Hardware) and add interlock endpoint in Node 5 (System Analysis).
        """
        english_feedbacks = [
            "race condition",
            "Race Condition",
            "RACE CONDITION",
            "Critical race condition detected between software task and physical beam",
            "Therac-25 race hazard in actuator positioning",
            "Actuator latency violation requires interlock check",
        ]

        for fb in english_feedbacks:
            # 1. Hardware Node Evolution
            hw_cand = self.mock_gen.generate_candidate(6, "HardwareRuntime", self.bal_prof, {})
            self.assertFalse(hw_cand["hardware_interlocks_required"])
            self.assertEqual(hw_cand["physical_actuator_latency_ms"], 50.0)

            hw_evolved = self.mock_gen.evolve(fb, hw_cand)
            self.assertTrue(
                hw_evolved["hardware_interlocks_required"],
                f"Failed to enable interlocks for English feedback: '{fb}'"
            )
            self.assertEqual(hw_evolved["physical_actuator_latency_ms"], 8000.0)
            HardwareRuntimeContract.model_validate(hw_evolved)

            # 2. System Analysis Node Evolution
            sa_cand = self.mock_gen.generate_candidate(5, "SystemAnalysis", self.bal_prof, {})
            self.assertFalse(any("/interlock" in ep["path"] for ep in sa_cand["endpoints"]))

            sa_evolved = self.mock_gen.evolve(fb, sa_cand)
            self.assertTrue(
                any("/interlock" in ep["path"] for ep in sa_evolved["endpoints"]),
                f"Failed to add interlock endpoint for English feedback: '{fb}'"
            )
            SystemAnalysisContract.model_validate(sa_evolved)

    def test_evolve_russian_feedback_variations(self):
        """
        Russian feedback variations matching GOST and safety terminology must
        reliably activate interlocks in Node 6 and endpoints in Node 5.
        """
        russian_feedbacks = [
            "состояние гонки",
            "СОСТОЯНИЕ ГОНКИ",
            "Состояние Гонки",
            "Обнаружена опасная гонка сигналов привода",
            "Гонка данных в канале управления",
            "Необходима аппаратная блокировка актуатора",
            "Блокировка привода обязательна по ГОСТ",
            "Аппаратная защита от перегрузки",
            "аппаратный останов",
        ]

        for fb in russian_feedbacks:
            # Hardware
            hw_cand = self.mock_gen.generate_candidate(6, "HardwareRuntime", self.bal_prof, {})
            hw_evolved = self.mock_gen.evolve(fb, hw_cand)
            self.assertTrue(
                hw_evolved["hardware_interlocks_required"],
                f"Failed to enable interlocks for Russian feedback: '{fb}'"
            )
            self.assertEqual(hw_evolved["physical_actuator_latency_ms"], 8000.0)
            HardwareRuntimeContract.model_validate(hw_evolved)

            # System Analysis
            sa_cand = self.mock_gen.generate_candidate(5, "SystemAnalysis", self.bal_prof, {})
            sa_evolved = self.mock_gen.evolve(fb, sa_cand)
            self.assertTrue(
                any("/interlock" in ep["path"] for ep in sa_evolved["endpoints"]),
                f"Failed to add interlock endpoint for Russian feedback: '{fb}'"
            )
            SystemAnalysisContract.model_validate(sa_evolved)

    def test_evolve_idempotence(self):
        """
        Evolving an already evolved candidate with additional or repeated feedback
        must be strictly idempotent (no duplicated endpoints, stable latency).
        """
        sa_cand = self.mock_gen.generate_candidate(5, "SystemAnalysis", self.bal_prof, {})
        initial_eps = len(sa_cand["endpoints"])

        fb = "Critical race condition detected"
        evolved_1 = self.mock_gen.evolve(fb, sa_cand)
        self.assertEqual(len(evolved_1["endpoints"]), initial_eps + 1)

        evolved_2 = self.mock_gen.evolve(fb, evolved_1)
        self.assertEqual(len(evolved_2["endpoints"]), initial_eps + 1)

        evolved_3 = self.mock_gen.evolve("аппаратная блокировка", evolved_2)
        self.assertEqual(len(evolved_3["endpoints"]), initial_eps + 1)

    def test_evolve_non_hazard_feedback_preserves_artifact(self):
        """
        Feedback unrelated to hardware hazards (e.g. margin, CAC, UI) must not
        trigger false-positive hardware modifications.
        """
        hw_cand = self.mock_gen.generate_candidate(6, "HardwareRuntime", self.bal_prof, {})
        unrelated_feedback = "Increase target profit margin to 25% and reduce CAC"

        evolved = self.mock_gen.evolve(unrelated_feedback, hw_cand)
        self.assertFalse(evolved["hardware_interlocks_required"])
        self.assertEqual(evolved["physical_actuator_latency_ms"], 50.0)

    def test_evolve_non_hardware_nodes_safe(self):
        """
        Passing candidates from Strategy (Node 1) or Finance (Node 2) to evolve()
        must not inject hardware keys or crash.
        """
        strategy_cand = self.mock_gen.generate_candidate(1, "StrategyCJM", self.bal_prof, {})
        evolved_s = self.mock_gen.evolve("Critical race condition in physical actuator", strategy_cand)
        self.assertNotIn("hardware_interlocks_required", evolved_s)
        self.assertNotIn("physical_actuator_latency_ms", evolved_s)

    def test_candidate_dict_metadata_preservation_exhaustive(self):
        """
        Verify metadata retention across all 4 standard copy/init mechanisms.
        """
        cand = CandidateDict({
            "target_cpu_profile": "Intel Core Ultra 5 125H",
            "_profile": "Balanced",
            "__profile__": "Balanced",
            "_seed": 202,
        })
        # 1. copy()
        c1 = cand.copy()
        self.assertEqual(c1["_profile"], "Balanced")
        self.assertEqual(c1["_seed"], 202)

        # 2. copy.copy()
        c2 = copy.copy(cand)
        self.assertEqual(c2["_profile"], "Balanced")

        # 3. copy.deepcopy()
        c3 = copy.deepcopy(cand)
        self.assertEqual(c3["_profile"], "Balanced")

        # 4. CandidateDict(cand)
        c4 = CandidateDict(cand)
        self.assertEqual(c4["_profile"], "Balanced")

    def test_evolve_adversarial_input_types(self):
        """
        Test resilience against unexpected feedback types: None, numbers, empty string, dict.
        """
        hw_cand = self.mock_gen.generate_candidate(6, "HardwareRuntime", self.bal_prof, {})

        for weird_input in [None, "", "   ", 12345, 0.0, True, False]:
            res = self.mock_gen.evolve(weird_input, hw_cand)
            self.assertIsInstance(res, dict)
            self.assertFalse(res["hardware_interlocks_required"])


if __name__ == "__main__":
    unittest.main()
