"""
Multi-Pass Zero-Hallucination Research Engine
Conducts multi-pass web research against official developer documentation, GitHub repos, and registries.
Rejects hallucinated memory cutoffs in favor of verified live technical specifications.
"""

from typing import Dict, Any, List
import re
from core.npu_engine import IntelNpuDecisionEngine


class MultiPassDocCrawler:
    """
    Executes a structured 4-pass verification pipeline for a given technology or skill domain.
    """

    def __init__(self, npu_engine: IntelNpuDecisionEngine = None):
        self.npu = npu_engine or IntelNpuDecisionEngine()

    def generate_research_plan(self, domain: str, tech_name: str) -> Dict[str, Any]:
        """
        Plans multi-pass queries targeted strictly at official documentation sources.
        """
        # Pass 1: Canonical source discovery
        pass_1_queries = [
            f"{tech_name} official documentation quickstart 2026",
            f"{tech_name} npm package or github repository",
            f"{tech_name} breaking changes latest release"
        ]

        # Pass 2: Configuration schema & CLI flags
        pass_2_queries = [
            f"{tech_name} cli commands flags reference",
            f"{tech_name} configuration file schema json yaml"
        ]

        # Pass 3: Auth & Rate Limits & Error Handling
        pass_3_queries = [
            f"{tech_name} authentication api token permissions scopes",
            f"{tech_name} error codes rate limits retry policy"
        ]

        return {
            "tech_name": tech_name,
            "domain": domain,
            "passes": [
                {"pass": 1, "objective": "Discover official docs & canonical package", "queries": pass_1_queries},
                {"pass": 2, "objective": "Extract CLI commands & configuration schemas", "queries": pass_2_queries},
                {"pass": 3, "objective": "Extract authentication scopes & error codes", "queries": pass_3_queries},
                {"pass": 4, "objective": "NPU-assisted verification & anti-hallucination gate", "rubric": "freshness, zero-hallucination, official origin"}
            ]
        }

    def validate_scraped_documentation(self, raw_content: str, tech_name: str) -> Dict[str, Any]:
        """
        Pass 4: Anti-Hallucination Validation Gate.
        Evaluates scraped technical content on Intel AI Boost NPU to verify authenticity and freshness.
        """
        # 1. Proposition check on NPU
        noul_result = self.npu.noul(raw_content[:2000], "verified_docs")
        
        # 2. Quality scoring on NPU
        score_result = self.npu.score(tech_name + ": " + raw_content[:1500], "official developer docs, CLI accuracy, modern LTS")

        # 3. Heuristic checks for key technical artifacts
        has_cli_commands = bool(re.search(r"(`|```)(npm|npx|wrangler|gh|git|pip|python|cargo)\s+", raw_content))
        has_auth_scope = bool(re.search(r"(token|auth|key|secret|scope|credential)", raw_content, re.IGNORECASE))
        has_config_example = bool(re.search(r"(\.json|\.toml|\.yaml|\.yml|config)", raw_content, re.IGNORECASE))

        is_valid = noul_result["value"] and score_result["rating"] >= 6 and (has_cli_commands or has_config_example)

        return {
            "tech_name": tech_name,
            "is_validated": is_valid,
            "npu_confidence": noul_result["probability"],
            "quality_rating": score_result["rating"],
            "has_cli_commands": has_cli_commands,
            "has_auth_scope": has_auth_scope,
            "has_config_example": has_config_example,
            "validation_device": self.npu.device_name
        }
