"""
Project Harness & Skill Synthesizer - Configuration
Hardware profile: Intel Core Ultra 5 125H (Meteor Lake), Intel AI Boost NPU, 16GB RAM.
Environment: Windows 11, OpenVINO 2024+, Node.js MCP server.
"""

import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent
GLOBAL_GEMINI_DIR = Path(r"C:\Users\Артем\.gemini")
GLOBAL_SKILLS_DIR = GLOBAL_GEMINI_DIR / "skills"
DEFAULT_SCRATCH_DIR = GLOBAL_GEMINI_DIR / "antigravity" / "scratch"
OPENVINO_LIB_DIR = r"C:\Users\Артем\AppData\Local\Programs\Python\Python311\Lib\site-packages\openvino\libs"

# Hardware Constraints
HARDWARE_PROFILE = {
    "cpu": "Intel Core Ultra 5 125H",
    "npu": "Intel AI Boost (Meteor Lake VPU)",
    "gpu": "Intel Arc Graphics",
    "ram_gb": 16,
    "battery_optimized": True,
    "preferred_runtime": "native_npu_directml_node_python",
    "disallowed_runtimes": ["heavy_docker_desktop", "cloud_gpu_only"]
}

# Skill Authoring Standards (Antigravity Standard)
SKILL_STANDARDS = {
    "required_files": ["SKILL.md"],
    "recommended_dirs": ["references", "scripts"],
    "frontmatter_keys": ["name", "description"],
    "tone": "imperative, narrow-specialized, zero-fluff, production-grade",
    "max_context_cost_kb": 25  # Keep main SKILL.md compact, offload docs to references/
}
