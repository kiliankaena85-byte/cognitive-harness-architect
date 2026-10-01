import sys
import json
import urllib.request
import urllib.error
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_FILE = PROJECT_ROOT / "openrouter_config.json"

class Tev1Evaluator:
    def __init__(self):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            self.config = json.load(f)
        self.api_keys = self.config.get("api_keys", [])
        self.current_key_idx = 0

    def query_decisions_api(self, state: str, instructions: str, criteria: dict) -> str:
        url = "https://openrouter.ai/api/alpha/decisions"
        model_name = "togethercomputer/tev1-4b-experimental"
        
        payload = {
            "model": model_name,
            "state": state,
            "questions": {
                "decision": {
                    "type": "choice",
                    "instructions": instructions,
                    "criteria": criteria
                }
            }
        }

        key = self.api_keys[self.current_key_idx % len(self.api_keys)]
        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        }

        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return json.dumps(data, indent=2)
        except urllib.error.HTTPError as e:
            err = e.read().decode("utf-8") if e.fp else str(e)
            return f"Error: HTTP {e.code} - {err}"
        except Exception as e:
            return f"Error: {str(e)}"

    def evaluate_solutions(self):
        print("Evaluating Solution 1...")
        state1 = "Our DAG architecture has 7 independent nodes (Ministries). The Finance Node approves a 10M budget. The Hardware Node designs a 50M cluster. The GOST parser validates both documents independently as structurally correct. The mathematical CDD-TDD verifies logic within each document independently."
        instructions1 = "Which solution is the mathematically and architecturally most robust way to prevent this Semantic Gap?"
        criteria1 = {
            "A": "Train the Gemini generator to double-check previous documents.",
            "B": "Implement a deterministic Cross-Ministry Contract Validator in Python that computes assertions across all outputs.",
            "C": "Send all documents to a third LLM for a final summary check.",
            "D": "Ignore it, the NPU ModernBERT will flag it."
        }
        ans1 = self.query_decisions_api(state1, instructions1, criteria1)
        print("Result 1:", ans1)
        
        print("\nEvaluating Solution 2...")
        state2 = "The current GOST compliance parser uses regex to ban fuzzy words like 'fast' or 'reliable'. It falsely flags the valid sentence: 'The system must not be fast, but strictly deterministic.' because it sees the word 'fast'."
        instructions2 = "What is the optimal deterministic approach to fix this False Positive without relying on Generative AI?"
        criteria2 = {
            "A": "Ask an LLM to read the sentence and decide if it's fuzzy.",
            "B": "Use an NLP Dependency Parser to construct an AST of the sentence and verify if 'fast' is negated.",
            "C": "Remove the word 'fast' from the banned regex list entirely."
        }
        ans2 = self.query_decisions_api(state2, instructions2, criteria2)
        print("Result 2:", ans2)
        
        print("\nEvaluating Solution 3...")
        state3 = "Adversarial Compliance (Semantic Chameleon): The LLM generates a mathematically perfect and GOST-compliant specification that completely distorts the business logic (e.g., changing 'refund possible' to 'refund with 100% fee'). The CDD-TDD tests pass because the math is internally consistent."
        instructions3 = "Which mechanism completely eliminates this vulnerability in a Zero-Trust architecture?"
        criteria3 = {
            "A": "The Ministry of Intent: Requiring the human to write BDD/Gherkin Acceptance Criteria before generation, and mathematically mapping generated spec rules back to a Gherkin AC.",
            "B": "Asking the LLM 'Are you sure this matches what the user wanted?'",
            "C": "Increasing the NPU embedding threshold."
        }
        ans3 = self.query_decisions_api(state3, instructions3, criteria3)
        print("Result 3:", ans3)

if __name__ == "__main__":
    evaluator = Tev1Evaluator()
    evaluator.evaluate_solutions()
