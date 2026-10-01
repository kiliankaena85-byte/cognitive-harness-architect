import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from intent_ministry import IntentMinistryValidator

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

class TestIntentMinistry(unittest.TestCase):
    def setUp(self):
        self.validator = IntentMinistryValidator()
        self.gherkin_acs = [
            {"id": "AC-1", "text": "Given user is logged in, When they click refund, Then return 100% money."},
            {"id": "AC-2", "text": "Given anonymous user, When they click refund, Then show login prompt."}
        ]

    def test_perfect_compliance(self):
        prd = {
            "business_rules": [
                {"rule_id": "BR-101", "desc": "Process full refund", "source_ac_id": "AC-1"},
                {"rule_id": "BR-102", "desc": "Redirect to /login", "source_ac_id": "AC-2"}
            ]
        }
        res = self.validator.validate_traceability(self.gherkin_acs, prd)
        self.assertTrue(res["passed"])
        self.assertEqual(len(res["errors"]), 0)

    def test_missing_user_intent(self):
        # LLM "forgot" to implement AC-2 (login prompt)
        prd = {
            "business_rules": [
                {"rule_id": "BR-101", "desc": "Process full refund", "source_ac_id": "AC-1"}
            ]
        }
        res = self.validator.validate_traceability(self.gherkin_acs, prd)
        self.assertFalse(res["passed"])
        self.assertIn("AC-2", res["uncovered_acs"])

    def test_adversarial_compliance_hallucination(self):
        # LLM implemented everything, but added a hidden fee!
        prd = {
            "business_rules": [
                {"rule_id": "BR-101", "desc": "Process full refund", "source_ac_id": "AC-1"},
                {"rule_id": "BR-102", "desc": "Redirect to /login", "source_ac_id": "AC-2"},
                {"rule_id": "BR-103", "desc": "Charge a 20% processing fee", "source_ac_id": None}
            ]
        }
        res = self.validator.validate_traceability(self.gherkin_acs, prd)
        self.assertFalse(res["passed"])
        self.assertIn("BR-103", res["unmapped_hallucinated_rules"])
        self.assertIn("Adversarial Hallucination!", res["errors"][0])

if __name__ == "__main__":
    unittest.main(verbosity=2)
