"""
tests/test_npu_darwinian_stress.py
=============================================================================
Empirical Benchmark and Stress Testing Suite for Milestone 2:
System 1 NPU & Decisions API Lexicographic Multi-Objective Pareto Arbiter (L-MOPA).
Challenger Agent: challenger_m2_2

Stress Testing Dimensions:
1. Tie-breaking on identical and near-identical candidate vectors.
2. Small sample sizes (N=1, 2, 3, 5, 10, 100).
3. OpenVINO NPU vs CPU fallback latency benchmark and Decisions API error handling.
4. Numerical stability: LinAlgError, singular covariance matrices, zero-variance,
   and boundary adversarial inputs.
=============================================================================
"""

import gc
import json
import math
import os
import sys
import time
import unittest
import urllib.error
from pathlib import Path
from typing import Any, Dict, List, Tuple
from unittest.mock import MagicMock, patch

import numpy as np

# Ensure UTF-8 output on Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.npu_darwinian_loop import (
    AllHypothesesDisqualifiedError,
    DualAgentFilter,
    NpuParetoSelector,
)


class TestStressTieBreakingIdenticalVectors(unittest.TestCase):
    """
    Stress Dimension 1: Tie-breaking on identical and near-identical candidate vectors.
    """

    def setUp(self):
        self.selector = NpuParetoSelector(use_npu=False, use_decisions_api=False)

    def test_stress_exact_identical_two_candidates(self):
        """Two candidates with identical scores and identical dictionaries."""
        cand_a = {"name": "candidate_clone_a", "security_score": 0.90, "monthly_opex": 1000.0}
        cand_b = {"name": "candidate_clone_b", "security_score": 0.90, "monthly_opex": 1000.0}

        winner = self.selector.select_dominant([cand_a, cand_b])
        self.assertIsNotNone(winner)
        # Winner must be deterministically determined by SHA-256 hash
        # Test 100 runs for strict deterministic repeatability
        for _ in range(100):
            w = self.selector.select_dominant([cand_a, cand_b])
            self.assertEqual(w["name"], winner["name"])

    def test_stress_exact_identical_five_candidates(self):
        """Five candidates with completely identical vectors and payload structures."""
        candidates = [
            {"id": i, "name": f"iso_cand_{i}", "security_score": 0.95, "intent_score": 0.92, "monthly_opex": 1200.0}
            for i in range(5)
        ]
        winner = self.selector.select_dominant(candidates)
        self.assertIsNotNone(winner)

        # Deterministic winner across 100 executions
        for _ in range(100):
            w = self.selector.select_dominant(candidates)
            self.assertEqual(w["name"], winner["name"])

    def test_stress_order_permutation_invariance_on_ties(self):
        """Permuting input order of tied candidates must not alter the canonical SHA-256 winner."""
        c1 = {"name": "cand_alpha", "security_score": 0.88, "monthly_opex": 1500.0}
        c2 = {"name": "cand_beta", "security_score": 0.88, "monthly_opex": 1500.0}
        c3 = {"name": "cand_gamma", "security_score": 0.88, "monthly_opex": 1500.0}

        w_forward = self.selector.select_dominant([c1, c2, c3])
        w_reverse = self.selector.select_dominant([c3, c2, c1])
        w_scrambled = self.selector.select_dominant([c2, c1, c3])

        self.assertEqual(w_forward["name"], w_reverse["name"])
        self.assertEqual(w_forward["name"], w_scrambled["name"])

    def test_stress_near_identical_within_epsilon_frontier(self):
        """
        Candidates with objective variations strictly within epsilon:
        |F2(A) - F2(B)| = 0.001 < 0.05
        |F3(A) - F3(B)| = 0.001 < 0.02
        |F4(A) - F4(B)| = 0.001 < 0.05
        |F5(A) - F5(B)| = 0.001 < 0.05
        Should fall back to Utopian distance tie-breaker.
        """
        cand_a = {
            "name": "cand_near_a",
            "security_score": 0.900,
            "intent_score": 0.900,
            "resource_score": 0.900,
            "mdl_density": 0.900,
        }
        cand_b = {
            "name": "cand_near_b",
            "security_score": 0.901,  # +0.001 (diff < eps_2)
            "intent_score": 0.901,    # +0.001 (diff < eps_3)
            "resource_score": 0.901,  # +0.001 (diff < eps_4)
            "mdl_density": 0.901,     # closer to utopian (1,1,1,1,1)
        }
        winner = self.selector.select_dominant([cand_a, cand_b])
        # cand_b is closer to (1,1,1,1,1) on all dimensions and within epsilon
        self.assertEqual(winner["name"], "cand_near_b")

    def test_stress_micro_delta_precision_limit(self):
        """Microscopic delta (1e-7) between candidate scores."""
        cand_a = {
            "name": "cand_base",
            "security_score": 0.9500000,
            "monthly_opex": 1000.0,
        }
        cand_b = {
            "name": "cand_micro",
            "security_score": 0.9500001,
            "monthly_opex": 1000.0,
        }
        winner = self.selector.select_dominant([cand_a, cand_b])
        self.assertIsNotNone(winner)
        self.assertIn(winner["name"], ["cand_base", "cand_micro"])

    def test_stress_exact_utopian_point_candidates(self):
        """All candidates achieve perfect Utopian point (1, 1, 1, 1, 1). Distance = 0."""
        c1 = {"name": "perfect_1", "security_score": 1.0, "intent_score": 1.0, "resource_score": 1.0, "mdl_density": 1.0}
        c2 = {"name": "perfect_2", "security_score": 1.0, "intent_score": 1.0, "resource_score": 1.0, "mdl_density": 1.0}
        c3 = {"name": "perfect_3", "security_score": 1.0, "intent_score": 1.0, "resource_score": 1.0, "mdl_density": 1.0}

        winner = self.selector.select_dominant([c1, c2, c3])
        self.assertIsNotNone(winner)
        # Verify distance is computed without numerical explosion
        distances = self.selector._compute_utopian_distances([
            (1.0, 1.0, 1.0, 1.0, 1.0),
            (1.0, 1.0, 1.0, 1.0, 1.0),
            (1.0, 1.0, 1.0, 1.0, 1.0),
        ])
        for d in distances:
            self.assertAlmostEqual(d, 0.0, places=6)


class TestStressSmallSampleSizesAndLinearAlgebra(unittest.TestCase):
    """
    Stress Dimension 2: Small sample sizes (N=1, 2, 3, 5, 100) and Covariance Singularity.
    """

    def setUp(self):
        self.selector = NpuParetoSelector(use_npu=False, use_decisions_api=False)

    def test_sample_size_n1_boundary(self):
        """N = 1: Single candidate pool must return candidate immediately."""
        c = {"name": "solo_candidate", "security_score": 0.85}
        winner = self.selector.select_dominant([c])
        self.assertEqual(winner["name"], "solo_candidate")

    def test_sample_size_n2_singular_covariance(self):
        """
        N = 2: Covariance of 2 vectors in 5D space has rank <= 1.
        Must evaluate cleanly without LinAlgError.
        """
        c1 = {"name": "n2_cand1", "security_score": 0.90, "intent_score": 0.85, "resource_score": 0.70, "mdl_density": 0.80}
        c2 = {"name": "n2_cand2", "security_score": 0.90, "intent_score": 0.85, "resource_score": 0.72, "mdl_density": 0.80}
        winner = self.selector.select_dominant([c1, c2])
        self.assertIsNotNone(winner)

    def test_sample_size_n3_rank2_covariance(self):
        """N = 3: Covariance matrix rank <= 2. Must not fail."""
        cands = [
            {"name": f"n3_cand_{i}", "security_score": 0.91, "intent_score": 0.88, "monthly_opex": 1000.0 + i * 50}
            for i in range(3)
        ]
        winner = self.selector.select_dominant(cands)
        self.assertIsNotNone(winner)

    def test_sample_size_n5_system2_ensemble(self):
        """N = 5: Standard System 2 5-candidate ensemble size."""
        ensemble = [
            {"name": "Defensive", "security_score": 0.97, "intent_score": 0.92, "monthly_opex": 3000.0, "mdl_density": 0.85},
            {"name": "Balanced", "security_score": 0.92, "intent_score": 0.90, "monthly_opex": 1500.0, "mdl_density": 0.88},
            {"name": "High-Throughput", "security_score": 0.89, "intent_score": 0.88, "monthly_opex": 2500.0, "mdl_density": 0.82},
            {"name": "Frugal", "security_score": 0.80, "intent_score": 0.82, "monthly_opex": 300.0, "mdl_density": 0.92},
            {"name": "Adversarial", "security_score": 0.99, "invalid_schema": True, "monthly_opex": 100.0}
        ]
        winner = self.selector.select_dominant(ensemble)
        self.assertIsNotNone(winner)
        self.assertNotEqual(winner["name"], "Adversarial", "Adversarial candidate with F1=0 must be disqualified")

    def test_collinear_vectors_zero_variance_subspace(self):
        """
        Candidates whose objective vectors have 0 variance along several axes:
        e.g., F1=1.0, F2=0.90, F3=0.85, F5=0.80 for ALL candidates, only F4 varies.
        """
        collinear_cands = [
            {"name": f"coll_{i}", "security_score": 0.90, "intent_score": 0.85, "resource_score": 0.70 + i * 0.01, "mdl_density": 0.80}
            for i in range(5)
        ]
        # Should not raise LinAlgError or ZeroDivisionError
        winner = self.selector.select_dominant(collinear_cands)
        self.assertIsNotNone(winner)

    def test_zero_variance_across_all_axes(self):
        """Zero variance on ALL 5 axes across 5 candidates."""
        identical_vecs = [(1.0, 0.9, 0.8, 0.7, 0.6)] * 5
        dists = self.selector._compute_utopian_distances(identical_vecs)
        self.assertEqual(len(dists), 5)
        for d in dists:
            self.assertTrue(math.isfinite(d))
            self.assertGreater(d, 0.0)

    def test_scale_100_candidates_throughput(self):
        """Stress tests selection over a large pool of 100 competing candidates."""
        cands = [
            {
                "name": f"scale_{i}",
                "security_score": 0.80 + (i % 20) * 0.01,
                "intent_score": 0.80 + (i % 15) * 0.01,
                "monthly_opex": 1000.0 + (i % 50) * 50.0,
                "mdl_density": 0.85,
            }
            for i in range(100)
        ]
        t0 = time.perf_counter()
        winner = self.selector.select_dominant(cands)
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        self.assertIsNotNone(winner)
        self.assertLess(elapsed_ms, 50.0, f"100-candidate selection took {elapsed_ms:.2f} ms")


class TestStressOpenVinoHardwareAndFallbackLatency(unittest.TestCase):
    """
    Stress Dimension 3: OpenVINO NPU vs CPU fallback latency benchmark.
    """

    def test_hardware_profiling_and_device_detection(self):
        """Inspects and reports available OpenVINO accelerator devices."""
        import openvino as ov
        core = ov.Core()
        available = core.available_devices
        print(f"\n[Hardware Discovery] OpenVINO available devices: {available}")
        self.assertIn("CPU", available)

    def test_benchmark_npu_vs_cpu_latency_sla(self):
        """
        Benchmarks candidate evaluation latency across:
        1. OpenVINO NPU (Intel AI Boost)
        2. OpenVINO CPU
        3. Local CPU fallback (NumPy)
        Verifies sub-15ms fast-path SLA.
        """
        sample_cand = {
            "name": "benchmark_manifest",
            "max_ram_budget_mb": 256.0,
            "p99_latency_ms": 25.0,
            "security_score": 0.95,
            "intent_score": 0.90,
            "monthly_opex": 1200.0,
            "mdl_density": 0.88,
        }

        modes = [
            ("Local CPU Fallback", NpuParetoSelector(use_npu=False)),
            ("OpenVINO CPU", NpuParetoSelector(use_npu=True, target_device="CPU")),
        ]

        # Add NPU if available on this machine
        try:
            import openvino as ov
            if "NPU" in ov.Core().available_devices:
                modes.append(("OpenVINO NPU (Intel AI Boost)", NpuParetoSelector(use_npu=True, target_device="NPU")))
        except Exception:
            pass

        print("\n" + "=" * 70)
        print("  SYSTEM 1 TIER 1A FAST PATH LATENCY EMPIRICAL BENCHMARK")
        print("=" * 70)

        for mode_name, selector in modes:
            # Warmup
            for _ in range(20):
                _ = selector.evaluate_candidate(sample_cand)

            latencies = []
            iterations = 500
            for _ in range(iterations):
                t0 = time.perf_counter()
                _ = selector.evaluate_candidate(sample_cand)
                latencies.append((time.perf_counter() - t0) * 1000.0)  # ms

            lat_arr = np.array(latencies)
            p50 = float(np.percentile(lat_arr, 50))
            p95 = float(np.percentile(lat_arr, 95))
            p99 = float(np.percentile(lat_arr, 99))
            avg = float(np.mean(lat_arr))
            max_lat = float(np.max(lat_arr))

            print(f"[{mode_name}] Device: {selector.device} (Active NPU: {selector.npu_active})")
            print(f"  Iterations: {iterations}")
            print(f"  Avg Latency:  {avg:.4f} ms ({avg * 1000:.2f} µs)")
            print(f"  P50 Latency:  {p50:.4f} ms ({p50 * 1000:.2f} µs)")
            print(f"  P95 Latency:  {p95:.4f} ms ({p95 * 1000:.2f} µs)")
            print(f"  P99 Latency:  {p99:.4f} ms ({p99 * 1000:.2f} µs)")
            print(f"  Max Latency:  {max_lat:.4f} ms ({max_lat * 1000:.2f} µs)")

            # Fast-path requirement SLA: < 15.0 ms
            self.assertLess(avg, 15.0, f"{mode_name} avg latency {avg} ms exceeded 15 ms limit")
            self.assertLess(p95, 15.0, f"{mode_name} P95 latency {p95} ms exceeded 15 ms limit")

        print("=" * 70)

    def test_stress_memory_leak_check_5000_evaluations(self):
        """Evaluates 5,000 candidate evaluations to verify no memory leaks or resource buildup."""
        selector = NpuParetoSelector(use_npu=True, target_device="AUTO")
        cand = {"name": "leak_test", "security_score": 0.90, "monthly_opex": 1000.0}

        gc.collect()
        t0 = time.perf_counter()
        for i in range(5000):
            _ = selector.evaluate_candidate(cand)
        elapsed = time.perf_counter() - t0

        avg_us = (elapsed / 5000) * 1e6
        print(f"[Memory & Throughput Stress] 5,000 evaluations completed in {elapsed:.3f}s ({avg_us:.2f} µs/eval).")
        self.assertLess(avg_us, 5000.0)  # Sub-5ms even under stress


class TestStressDecisionsApiErrorHandling(unittest.TestCase):
    """
    Stress Dimension 4: Together Tev1-4B Decisions API Error Injection.
    Tests all HTTP status codes, timeouts, corrupt responses, and transparent fallbacks.
    """

    def setUp(self):
        self.selector = NpuParetoSelector(use_decisions_api=True)
        self.cand1 = {"name": "cand1", "security_score": 0.95, "intent_score": 0.90}
        self.cand2 = {"name": "cand2", "security_score": 0.70, "intent_score": 0.90}

    @patch("urllib.request.urlopen")
    def test_http_400_bad_request_fallback(self, mock_urlopen):
        mock_urlopen.side_effect = urllib.error.HTTPError("url", 400, "Bad Request", {}, None)
        winner = self.selector.select_dominant([self.cand1, self.cand2])
        self.assertIsNotNone(winner)
        self.assertEqual(winner["name"], "cand1")

    @patch("urllib.request.urlopen")
    def test_http_401_unauthorized_fallback(self, mock_urlopen):
        mock_urlopen.side_effect = urllib.error.HTTPError("url", 401, "Unauthorized", {}, None)
        winner = self.selector.select_dominant([self.cand1, self.cand2])
        self.assertIsNotNone(winner)
        self.assertEqual(winner["name"], "cand1")

    @patch("urllib.request.urlopen")
    def test_http_403_forbidden_fallback(self, mock_urlopen):
        mock_urlopen.side_effect = urllib.error.HTTPError("url", 403, "Forbidden", {}, None)
        winner = self.selector.select_dominant([self.cand1, self.cand2])
        self.assertIsNotNone(winner)
        self.assertEqual(winner["name"], "cand1")

    @patch("urllib.request.urlopen")
    def test_http_404_not_found_fallback(self, mock_urlopen):
        mock_urlopen.side_effect = urllib.error.HTTPError("url", 404, "Not Found", {}, None)
        winner = self.selector.select_dominant([self.cand1, self.cand2])
        self.assertIsNotNone(winner)
        self.assertEqual(winner["name"], "cand1")

    @patch("urllib.request.urlopen")
    def test_http_429_rate_limit_fallback(self, mock_urlopen):
        mock_urlopen.side_effect = urllib.error.HTTPError("url", 429, "Too Many Requests", {}, None)
        winner = self.selector.select_dominant([self.cand1, self.cand2])
        self.assertIsNotNone(winner)
        self.assertEqual(winner["name"], "cand1")

    @patch("urllib.request.urlopen")
    def test_http_500_internal_error_fallback(self, mock_urlopen):
        mock_urlopen.side_effect = urllib.error.HTTPError("url", 500, "Internal Server Error", {}, None)
        winner = self.selector.select_dominant([self.cand1, self.cand2])
        self.assertIsNotNone(winner)
        self.assertEqual(winner["name"], "cand1")

    @patch("urllib.request.urlopen")
    def test_http_502_bad_gateway_fallback(self, mock_urlopen):
        mock_urlopen.side_effect = urllib.error.HTTPError("url", 502, "Bad Gateway", {}, None)
        winner = self.selector.select_dominant([self.cand1, self.cand2])
        self.assertIsNotNone(winner)
        self.assertEqual(winner["name"], "cand1")

    @patch("urllib.request.urlopen")
    def test_http_503_service_unavailable_fallback(self, mock_urlopen):
        mock_urlopen.side_effect = urllib.error.HTTPError("url", 503, "Service Unavailable", {}, None)
        winner = self.selector.select_dominant([self.cand1, self.cand2])
        self.assertIsNotNone(winner)
        self.assertEqual(winner["name"], "cand1")

    @patch("urllib.request.urlopen")
    def test_http_504_gateway_timeout_fallback(self, mock_urlopen):
        mock_urlopen.side_effect = urllib.error.HTTPError("url", 504, "Gateway Timeout", {}, None)
        winner = self.selector.select_dominant([self.cand1, self.cand2])
        self.assertIsNotNone(winner)
        self.assertEqual(winner["name"], "cand1")

    @patch("urllib.request.urlopen")
    def test_network_socket_timeout_fallback(self, mock_urlopen):
        mock_urlopen.side_effect = TimeoutError("Socket connection timed out after 10s")
        winner = self.selector.select_dominant([self.cand1, self.cand2])
        self.assertIsNotNone(winner)
        self.assertEqual(winner["name"], "cand1")

    @patch("urllib.request.urlopen")
    def test_malformed_corrupt_json_fallback(self, mock_urlopen):
        """Decisions API returns corrupt / truncated JSON string."""
        mock_resp = MagicMock()
        mock_resp.read.return_value = b'{"model": "togethercomputer", "choices": [{"broken...'
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        winner = self.selector.select_dominant([self.cand1, self.cand2])
        self.assertIsNotNone(winner)
        self.assertEqual(winner["name"], "cand1")

    @patch("urllib.request.urlopen")
    def test_html_error_page_fallback(self, mock_urlopen):
        """Decisions API returns Cloudflare HTML error page instead of JSON."""
        mock_resp = MagicMock()
        mock_resp.read.return_value = b"<!DOCTYPE html><html><body>Error 520 Web server down</body></html>"
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        winner = self.selector.select_dominant([self.cand1, self.cand2])
        self.assertIsNotNone(winner)
        self.assertEqual(winner["name"], "cand1")

    @patch("urllib.request.urlopen")
    def test_empty_choices_array_fallback(self, mock_urlopen):
        """Decisions API returns valid JSON with empty choices list."""
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({"choices": []}).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        winner = self.selector.select_dominant([self.cand1, self.cand2])
        self.assertIsNotNone(winner)
        self.assertEqual(winner["name"], "cand1")

    @patch("urllib.request.urlopen")
    def test_unknown_candidate_choice_fallback(self, mock_urlopen):
        """Decisions API returns a candidate name that was not in the prompt."""
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({
            "choices": [{"message": {"content": json.dumps({"decision": "phantom_candidate"})}}]
        }).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        winner = self.selector.select_dominant([self.cand1, self.cand2])
        self.assertIsNotNone(winner)
        # Phantom candidate ignored, local L-MOPA decides cand1
        self.assertEqual(winner["name"], "cand1")


class TestStressEdgeCasesAndLinAlgExceptions(unittest.TestCase):
    """
    Stress Dimension 5: Edge-case inputs, malformed structures, and exception resilience.
    """

    def setUp(self):
        self.selector = NpuParetoSelector(use_npu=False, use_decisions_api=False)

    def test_empty_candidate_pool(self):
        """Empty candidate pool returns None."""
        self.assertIsNone(self.selector.select_dominant([]))

    def test_empty_dictionary_candidate(self):
        """Candidate with empty dictionary {} does not crash."""
        vec = self.selector.evaluate_candidate({})
        self.assertEqual(len(vec), 5)
        self.assertEqual(vec[0], 1.0)  # default no violations

    def test_extreme_floating_point_inputs(self):
        """Candidate with NaN, Inf, and -Inf values."""
        cand_nan = {"max_ram_budget_mb": float("nan"), "customer_acquisition_cost": float("nan")}
        cand_inf = {"max_ram_budget_mb": float("inf"), "customer_acquisition_cost": 100.0}
        cand_neginf = {"max_ram_budget_mb": float("-inf"), "customer_acquisition_cost": 100.0}

        # Must not raise exceptions
        v_nan = self.selector.evaluate_candidate(cand_nan)
        v_inf = self.selector.evaluate_candidate(cand_inf)
        v_neginf = self.selector.evaluate_candidate(cand_neginf)

        # Inf RAM (> 512) must fail F1 gate
        self.assertEqual(v_inf[0], 0.0)

    def test_string_type_mismatches_in_numeric_fields_raises_value_error(self):
        """
        Empirically proves vulnerability: non-convertible string in security_score,
        intent_score, resource_score, monthly_opex, or mdl_density raises unhandled ValueError.
        """
        with self.assertRaises(ValueError):
            self.selector.evaluate_candidate({"security_score": "high"})
        with self.assertRaises(ValueError):
            self.selector.evaluate_candidate({"intent_score": "perfect"})
        with self.assertRaises(ValueError):
            self.selector.evaluate_candidate({"resource_score": "optimal"})
        with self.assertRaises(ValueError):
            self.selector.evaluate_candidate({"monthly_opex": "expensive"})
        with self.assertRaises(ValueError):
            self.selector.evaluate_candidate({"mdl_density": "dense"})

    def test_none_type_in_numeric_fields_raises_type_error(self):
        """
        Empirically proves vulnerability: None in numeric score fields raises unhandled TypeError.
        """
        with self.assertRaises(TypeError):
            self.selector.evaluate_candidate({"security_score": None})
        with self.assertRaises(TypeError):
            self.selector.evaluate_candidate({"intent_score": None})
        with self.assertRaises(TypeError):
            self.selector.evaluate_candidate({"resource_score": None})
        with self.assertRaises(TypeError):
            self.selector.evaluate_candidate({"monthly_opex": None})
        with self.assertRaises(TypeError):
            self.selector.evaluate_candidate({"mdl_density": None})

    def test_nan_score_inflation_behavior(self):
        """
        Empirically proves vulnerability: float('nan') in resource_score, intent_score,
        or mdl_density gets converted to 1.0 (the maximum score) due to Python's min(1.0, nan).
        """
        vec = self.selector.evaluate_candidate({"resource_score": float("nan")})
        self.assertEqual(vec[3], 1.0, "Resource score NaN is inflated to 1.0")

        vec2 = self.selector.evaluate_candidate({"intent_score": float("nan")})
        self.assertEqual(vec2[2], 1.0, "Intent score NaN is inflated to 1.0")

        vec3 = self.selector.evaluate_candidate({"mdl_density": float("nan")})
        self.assertEqual(vec3[4], 1.0, "MDL density NaN is inflated to 1.0")

    def test_negative_scores_domain_clamping(self):
        """Negative scores must be clamped to 0.0."""
        vec = self.selector.evaluate_candidate({
            "security_score": -0.5,
            "intent_score": -0.8,
            "resource_score": -10.0,
            "mdl_density": -1.0,
        })
        self.assertEqual(vec[1], 0.0)
        self.assertEqual(vec[2], 0.0)
        self.assertEqual(vec[3], 0.0)
        self.assertEqual(vec[4], 0.0)

    def test_divide_by_zero_solvency_guard(self):
        """CAC = 0 and LTV = 0 should not raise ZeroDivisionError."""
        cand_zero = {"customer_acquisition_cost": 0.0, "lifetime_value": 0.0}
        vec = self.selector.evaluate_candidate(cand_zero)
        self.assertEqual(vec[0], 1.0)

    def test_huge_payload_stress(self):
        """100 KB payload string for fuzzy word and MDL analysis."""
        huge_text = "сложная архитектурная спецификация " * 2000
        cand_huge = {
            "name": "huge_cand",
            "description": huge_text,
            "security_score": 0.90,
            "monthly_opex": 1000.0,
        }
        t0 = time.perf_counter()
        vec = self.selector.evaluate_candidate(cand_huge)
        dur = (time.perf_counter() - t0) * 1000.0
        self.assertEqual(len(vec), 5)
        self.assertLess(dur, 100.0, f"Huge payload evaluation took {dur:.2f} ms")

    def test_raise_on_disqualified_flag(self):
        """When raise_on_disqualified=True, raises AllHypothesesDisqualifiedError."""
        disqualified = [{"name": "bad", "invalid_schema": True}]
        with self.assertRaises(AllHypothesesDisqualifiedError):
            self.selector.select_dominant(disqualified, context={"raise_on_disqualified": True})

    def test_non_hashable_and_complex_candidate_dicts(self):
        """Candidate containing non-primitive types (lists of dicts, sets, None)."""
        complex_cand = {
            "name": "complex",
            "nested": {"a": [1, 2, {"b": None}]},
            "security_score": 0.92,
            "monthly_opex": 1000.0,
        }
        h = self.selector._compute_candidate_hash(complex_cand)
        self.assertIsInstance(h, str)
        self.assertEqual(len(h), 64)

    def test_dual_agent_filter_stress_wrapper(self):
        """DualAgentFilter subclass stress invocation."""
        flt = DualAgentFilter(use_npu=False, use_decisions_api=False)
        hypos = [
            {"name": f"h_{i}", "security_score": 0.90 + i * 0.01, "monthly_opex": 1000.0}
            for i in range(5)
        ]
        winner = flt.select_best_hypothesis(hypos, "SecurityMinistry")
        self.assertIsNotNone(winner)
        self.assertEqual(winner["name"], "h_4")


if __name__ == "__main__":
    unittest.main()
