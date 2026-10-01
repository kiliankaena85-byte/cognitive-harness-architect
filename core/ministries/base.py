import json
import uuid
import sys
from pathlib import Path

# Fix for windows encoding
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "core"))

from npu_darwinian_loop import DualAgentFilter

class BaseMinistry:
    def __init__(self, name: str, system_prompt: str, use_mock: bool = True):
        self.name = name
        self.system_prompt = system_prompt
        self.use_mock = use_mock
        self.darwinian_filter = DualAgentFilter()

    def generate(self, state: dict) -> dict:
        """Generates 10 hypotheses and uses NPU filter to select the best one."""
        print(f"[{self.name}] Generating hypotheses based on context...")
        
        hypotheses = self._call_llm_multiple_times(state, n=5)
        
        # NPU Tensor filter selects the best Pareto-optimal hypothesis
        best_hypothesis = self.darwinian_filter.select_best_hypothesis(hypotheses, self.name)
        
        print(f"[{self.name}] NPU selected optimal artifact.")
        return best_hypothesis

    def evolve(self, feedback: str, previous_artifact: dict, state: dict) -> dict:
        """When a Stage-Gate blocks the artifact, evolve it based on deterministic feedback."""
        print(f"[{self.name}] EVOLVING artifact based on Validator Feedback: {feedback}")
        
        # In a real system, the prompt would include the previous_artifact and the feedback.
        # We simulate a "fixed" artifact.
        fixed_artifact = self._mock_evolve_llm(previous_artifact, feedback)
        return fixed_artifact

    def _call_llm_multiple_times(self, state: dict, n: int) -> list:
        if self.use_mock:
            return self._mock_llm_generation(state, n)
        # Real LLM call logic would go here
        return []

    def _mock_llm_generation(self, state: dict, n: int) -> list:
        raise NotImplementedError("Subclasses must implement mock generation")

    def _mock_evolve_llm(self, artifact: dict, feedback: str) -> dict:
        raise NotImplementedError("Subclasses must implement mock evolution")
