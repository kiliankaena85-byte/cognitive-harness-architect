"""
Ministry of Intent (BDD/Gherkin Validator)
Protects against 'Adversarial Compliance / Semantic Chameleon'.
Ensures every generated rule maps back to user's exact Gherkin Acceptance Criteria.
"""

from typing import Dict, Any, List

class IntentMinistryValidator:
    def __init__(self):
        pass

    def validate_traceability(self, gherkin_acs: List[Dict[str, str]], generated_prd: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validates the bidirectional Traceability Matrix.
        1. All Gherkin ACs must be covered.
        2. All business rules in PRD must originate from a Gherkin AC.
        """
        ac_ids = {ac["id"] for ac in gherkin_acs}
        
        # Extract mapped ACs from the generated PRD
        business_rules = generated_prd.get("business_rules", [])
        
        mapped_acs = set()
        unmapped_rules = []

        for rule in business_rules:
            source_id = rule.get("source_ac_id")
            if source_id and source_id in ac_ids:
                mapped_acs.add(source_id)
            else:
                unmapped_rules.append(rule["rule_id"])

        uncovered_acs = list(ac_ids - mapped_acs)

        passed = len(uncovered_acs) == 0 and len(unmapped_rules) == 0

        errors = []
        if uncovered_acs:
            errors.append(f"Missing implementation for Acceptance Criteria: {uncovered_acs}")
        if unmapped_rules:
            errors.append(f"Adversarial Hallucination! Unmapped rules added by LLM: {unmapped_rules}")

        return {
            "passed": passed,
            "uncovered_acs": uncovered_acs,
            "unmapped_hallucinated_rules": unmapped_rules,
            "errors": errors
        }
