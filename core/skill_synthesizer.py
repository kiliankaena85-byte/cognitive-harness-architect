"""
Narrow-Specialized Skill Synthesizer
Generates deep, narrow-specialized Antigravity skills (SKILL.md + references/ + scripts/).
Follows Antigravity specifications and progressive disclosure guidelines.
"""

from typing import Dict, Any, List
from pathlib import Path
import json


class SkillSynthesizer:
    """
    Synthesizes production-grade, validated Antigravity skills from verified technical documentation.
    """

    def __init__(self, output_root: Path = None):
        self.output_root = output_root

    def synthesize_skill(
        self,
        skill_name: str,
        title: str,
        description: str,
        phases: List[Dict[str, str]],
        auth_config: Dict[str, Any],
        cli_commands: List[Dict[str, str]],
        error_handling: List[Dict[str, str]],
        reference_notes: str,
        output_dir: Path
    ) -> Path:
        """
        Builds the complete directory structure for the narrow skill.
        """
        skill_dir = output_dir / skill_name
        skill_dir.mkdir(parents=True, exist_ok=True)
        refs_dir = skill_dir / "references"
        refs_dir.mkdir(exist_ok=True)
        scripts_dir = skill_dir / "scripts"
        scripts_dir.mkdir(exist_ok=True)

        # 1. Generate SKILL.md
        skill_md_content = self._render_skill_md(
            skill_name=skill_name,
            title=title,
            description=description,
            phases=phases,
            auth_config=auth_config,
            cli_commands=cli_commands,
            error_handling=error_handling
        )
        (skill_dir / "SKILL.md").write_text(skill_md_content, encoding="utf-8")

        # 2. Generate references/api_cheatsheet.md
        ref_content = f"# {title} Reference & API Cheatsheet\n\n"
        ref_content += f"> Sourced strictly from verified official documentation.\n\n"
        ref_content += reference_notes
        (refs_dir / "api_cheatsheet.md").write_text(ref_content, encoding="utf-8")

        # 3. Generate diagnostic / test script in scripts/
        test_script_content = self._render_test_script(skill_name, auth_config)
        (scripts_dir / "preflight_check.ps1").write_text(test_script_content, encoding="utf-8")

        return skill_dir

    def _render_skill_md(
        self,
        skill_name: str,
        title: str,
        description: str,
        phases: List[Dict[str, str]],
        auth_config: Dict[str, Any],
        cli_commands: List[Dict[str, str]],
        error_handling: List[Dict[str, str]]
    ) -> str:
        lines = [
            "---",
            f"name: {skill_name}",
            f"description: >-",
            f"  {description.strip()}",
            "---",
            "",
            f"# {title}",
            "",
            f"Laser-focused, narrow-specialized skill for {title}. Validated against official documentation.",
            "",
            "## Capability Split",
            "",
            "| Phase | What | Transport | Surface |",
            "| :--- | :--- | :--- | :--- |"
        ]

        for p in phases:
            lines.append(f"| {p.get('phase', '1')} | {p.get('what', '')} | {p.get('transport', 'CLI')} | `{p.get('surface', '')}` |")

        lines.extend([
            "",
            "## Auth & Preflight Requirements",
            "",
            f"**Token Name**: `{auth_config.get('env_var', 'API_TOKEN')}`",
            f"**Required Scopes**: {', '.join([f'`{s}`' for s in auth_config.get('scopes', ['read', 'write'])])}",
            "",
            "> [!IMPORTANT]",
            f"> Before running commands, verify that `{auth_config.get('env_var', 'API_TOKEN')}` is present in the environment or project `.env` file. Never ask the user to paste credentials directly into chat.",
            "",
            "## Execution Steps & Commands",
            ""
        ])

        for cmd in cli_commands:
            lines.extend([
                f"### {cmd.get('name', 'Operation')}",
                cmd.get('description', ''),
                "",
                "```bash",
                cmd.get('command', ''),
                "```",
                ""
            ])

        lines.extend([
            "## Error Handling & Edge Cases",
            "",
            "| Error Code | Root Cause | Agent Action |",
            "| :--- | :--- | :--- |"
        ])

        for err in error_handling:
            lines.append(f"| `{err.get('code', 'ERROR')}` | {err.get('cause', '')} | {err.get('action', '')} |")

        lines.extend([
            "",
            "## References",
            "",
            "- Detailed API Cheatsheet: [api_cheatsheet.md](./references/api_cheatsheet.md)",
            "- Preflight Verification Script: [preflight_check.ps1](./scripts/preflight_check.ps1)",
            ""
        ])

        return "\n".join(lines)

    def _render_test_script(self, skill_name: str, auth_config: Dict[str, Any]) -> str:
        env_var = auth_config.get("env_var", "API_TOKEN")
        return f"""# Preflight Diagnostic Script for {skill_name}
Write-Host "Checking preflight environment for {skill_name}..." -ForegroundColor Cyan

if ([string]::IsNullOrWhiteSpace($env:{env_var})) {{
    Write-Host "[FAIL] Missing environment variable: {env_var}" -ForegroundColor Red
    Write-Host "Please set {env_var} in your environment or project .env" -ForegroundColor Yellow
    exit 1
}}

Write-Host "[OK] Credential {env_var} is present." -ForegroundColor Green
exit 0
"""
