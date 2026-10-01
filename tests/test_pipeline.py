"""
Unit tests for Project Harness & Skill Synthesizer
"""

import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.npu_engine import IntelNpuDecisionEngine
from core.decomposer import ProjectVectorDecomposer
from core.multi_pass_crawler import MultiPassDocCrawler
from core.skill_synthesizer import SkillSynthesizer


def test_npu_decision_primitives():
    engine = IntelNpuDecisionEngine()
    assert engine.device in ["NPU", "CPU", "GPU"]

    # Test Choice
    c = engine.choice("Cloudflare edge backend", ["Cloudflare Workers", "AWS Lambda", "Local Docker"])
    assert "choice" in c
    assert c["choice"] == "Cloudflare Workers"

    # Test Score
    s = engine.score("Cloudflare Workers Wrangler v3", "freshness and stability")
    assert s["rating"] >= 1 and s["rating"] <= 10

    # Test Noul
    n = engine.noul("Официальная документация с сайта разработчика Cloudflare", "verified_docs")
    assert n["value"] is True
    print("[PASS] NPU Decision Primitives verified on:", engine.device_name)


def test_vector_decomposition():
    decomposer = ProjectVectorDecomposer()
    res = decomposer.decompose("Cloudflare workers API with GitHub actions and Word docx")
    assert len(res["vectors"]) >= 3
    assert "skills_audit" in res
    print("[PASS] Vector Decomposition verified. Total vectors:", len(res["vectors"]))


def test_crawler_research_plan():
    crawler = MultiPassDocCrawler()
    plan = crawler.generate_research_plan("Cloud", "Cloudflare Workers")
    assert len(plan["passes"]) == 4
    print("[PASS] Multi-pass research plan verified.")


if __name__ == "__main__":
    test_npu_decision_primitives()
    test_vector_decomposition()
    test_crawler_research_plan()
    print("\nALL VERIFICATION TESTS PASSED SUCCESSFULLY!")
