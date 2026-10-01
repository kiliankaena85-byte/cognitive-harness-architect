"""
Harness Scaffolder
Sets up a brand new project workspace equipped with narrow-specialized skills,
agent rules, and harness verification configuration.
"""

from typing import Dict, Any, List
from pathlib import Path
import json


class ProjectHarnessScaffolder:
    def __init__(self):
        pass

    def scaffold_project(
        self,
        target_dir: Path,
        project_name: str,
        decomposed_data: Dict[str, Any],
        synthesized_skills: List[Path]
    ) -> Dict[str, Any]:
        """
        Creates the complete project structure with .agents/skills/ and project rules.
        """
        target_dir.mkdir(parents=True, exist_ok=True)
        agents_dir = target_dir / ".agents"
        skills_dir = agents_dir / "skills"
        rules_dir = agents_dir / "rules"
        skills_dir.mkdir(parents=True, exist_ok=True)
        rules_dir.mkdir(parents=True, exist_ok=True)

        # 1. Copy synthesized skills into workspace .agents/skills/
        deployed_skills = []
        for src_skill in synthesized_skills:
            if src_skill.is_dir():
                dest_skill = skills_dir / src_skill.name
                dest_skill.mkdir(parents=True, exist_ok=True)
                
                # Copy files
                for item in src_skill.rglob("*"):
                    rel = item.relative_to(src_skill)
                    target = dest_skill / rel
                    if item.is_dir():
                        target.mkdir(parents=True, exist_ok=True)
                    else:
                        target.parent.mkdir(parents=True, exist_ok=True)
                        target.write_bytes(item.read_bytes())
                deployed_skills.append(src_skill.name)

        # 2. Write GEMINI.md / AGENTS.md rules file
        rules_content = self._render_project_rules(project_name, decomposed_data, deployed_skills)
        (target_dir / "AGENTS.md").write_text(rules_content, encoding="utf-8")
        (target_dir / "GEMINI.md").write_text(rules_content, encoding="utf-8")

        # 3. Write harness.config.json
        harness_config = {
            "project_name": project_name,
            "architecture_vectors": decomposed_data.get("vectors", []),
            "active_skills": deployed_skills,
            "hardware_acceleration": {
                "npu": "Intel AI Boost (Meteor Lake)",
                "ram_limit_gb": 16,
                "offline_support": True
            },
            "scaffolded_at": "2026-09-30"
        }
        (target_dir / "harness.config.json").write_text(
            json.dumps(harness_config, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

        return {
            "project_path": str(target_dir),
            "project_name": project_name,
            "deployed_skills": deployed_skills,
            "harness_file": str(target_dir / "harness.config.json")
        }

    def _render_project_rules(self, project_name: str, data: Dict[str, Any], skills: List[str]) -> str:
        lines = [
            f"# Project Architecture & Agent Guidelines: {project_name}",
            "",
            "> Automated Harness & Skill Scaffolding by Antigravity Dual-Agent Coprocessor.",
            "",
            "## Available Narrow-Specialized Skills",
            "",
            "The following verified skills are mounted in `.agents/skills/`:",
            ""
        ]

        for s in skills:
            lines.append(f"- **`{s}`**: Specialized operational procedures, exact CLI flags, and failure mitigation.")

        lines.extend([
            "",
            "## Core Operational Directives",
            "",
            "1. **Zero Hallucination**: Do NOT invent CLI flags or API parameters from memory. Always inspect the relevant skill in `.agents/skills/<name>/SKILL.md` or its `references/` directory.",
            "2. **Hardware Constraints**: This project is tuned for Intel Core Ultra (Meteor Lake) with 16GB RAM. Avoid launching heavy Docker containers or memory-leaking daemons.",
            "3. **Progressive Disclosure**: Consult the `references/` directory within skills for full API schemas.",
            ""
        ])

        return "\n".join(lines)
