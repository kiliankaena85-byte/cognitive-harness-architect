import sys
import unittest
from hypothesis import given, settings, strategies as st
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cross_arbiter import CrossMinistryArbiter

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

class TestCrossMinistryArbiter(unittest.TestCase):
    def setUp(self):
        self.arbiter = CrossMinistryArbiter(max_iterations=3)

    def test_pass_without_modifications(self):
        finance = {"MaxBudget": 10000000}
        hardware = {"TotalCost": 5000000, "ClusterSize": 2, "NodeCost": 2500000}
        
        success, resolved_hw, msg = self.arbiter.validate_and_resolve(finance, hardware)
        self.assertTrue(success)
        self.assertEqual(resolved_hw["TotalCost"], 5000000)
        self.assertEqual(resolved_hw["ClusterSize"], 2)

    def test_downgrade_cluster_size(self):
        finance = {"MaxBudget": 10000000}
        hardware = {"TotalCost": 15000000, "ClusterSize": 3, "NodeCost": 5000000}
        
        # Iteration 0: Cost 15M > 10M. Downgrade ClusterSize to 2, Cost becomes 10M.
        # Iteration 1: Cost 10M <= 10M. Resolves!
        success, resolved_hw, msg = self.arbiter.validate_and_resolve(finance, hardware)
        self.assertTrue(success)
        self.assertEqual(resolved_hw["TotalCost"], 10000000)
        self.assertEqual(resolved_hw["ClusterSize"], 2)

    def test_downgrade_gpu(self):
        finance = {"MaxBudget": 1000000}
        hardware = {"TotalCost": 2500000, "ClusterSize": 1, "NodeCost": 500000, "GPU_Enabled": True}
        
        # Iteration 0: Cost 2.5M > 1M. ClusterSize=1, so downgrade GPU. Cost becomes 500k.
        success, resolved_hw, msg = self.arbiter.validate_and_resolve(finance, hardware)
        self.assertTrue(success)
        self.assertEqual(resolved_hw["TotalCost"], 500000)
        self.assertFalse(resolved_hw["GPU_Enabled"])

    def test_deadlock_rejection(self):
        finance = {"MaxBudget": 100000}
        # Even if we downgrade cluster size to 1, cost is 5M. No GPU to disable.
        hardware = {"TotalCost": 15000000, "ClusterSize": 3, "NodeCost": 5000000}
        
        success, resolved_hw, msg = self.arbiter.validate_and_resolve(finance, hardware)
        self.assertFalse(success)
        self.assertIn("Deadlock", msg)

    @given(
        budget=st.integers(min_value=1_000_000, max_value=50_000_000),
        cluster_size=st.integers(min_value=1, max_value=10),
        node_cost=st.integers(min_value=500_000, max_value=5_000_000)
    )
    @settings(max_examples=500, deadline=None)
    def test_pbt_invariant_always_holds_or_rejects(self, budget, cluster_size, node_cost):
        finance = {"MaxBudget": budget}
        hardware = {
            "TotalCost": cluster_size * node_cost,
            "ClusterSize": cluster_size,
            "NodeCost": node_cost
        }
        success, resolved_hw, msg = self.arbiter.validate_and_resolve(finance, hardware)
        
        if success:
            # CDD Invariant: Post-condition {Q} must hold
            self.assertLessEqual(resolved_hw["TotalCost"], finance["MaxBudget"])
        else:
            # Rejection implies even max downgrades failed to meet budget
            self.assertIn("Deadlock", msg)

if __name__ == "__main__":
    unittest.main(verbosity=2)
