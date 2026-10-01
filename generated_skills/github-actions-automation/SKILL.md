---
name: github-actions-automation
description: >-
  Manage GitHub workflows, automated CI/CD releases, issue triage, and secret management using gh CLI and declarative YAML.
---

# GitHub Actions & gh CLI Automation

Laser-focused, narrow-specialized skill for GitHub Actions & gh CLI Automation. Validated against official documentation.

## Capability Split

| Phase | What | Transport | Surface |
| :--- | :--- | :--- | :--- |
| 1 | Repository & Secret Preflight | CLI | `gh secret set` |
| 2 | Workflow Lint & Validation | CLI | `gh workflow view` |
| 3 | Trigger & Monitor Runs | CLI | `gh run watch` |
| 4 | Semantic Release Tagging | CLI | `gh release create` |

## Auth & Preflight Requirements

**Token Name**: `GITHUB_TOKEN`
**Required Scopes**: `repo`, `workflow`, `write:packages`

> [!IMPORTANT]
> Before running commands, verify that `GITHUB_TOKEN` is present in the environment or project `.env` file. Never ask the user to paste credentials directly into chat.

## Execution Steps & Commands

### Auth Status
Checks current GitHub CLI authentication state

```bash
gh auth status
```

### Trigger Workflow
Manually triggers a workflow dispatch with parameters

```bash
gh workflow run test.yml -f environment=staging
```

### Watch Latest Run
Streams live job execution logs in terminal

```bash
gh run watch $(gh run list --limit 1 --json databaseId -q '.[0].databaseId')
```

## Error Handling & Edge Cases

| Error Code | Root Cause | Agent Action |
| :--- | :--- | :--- |
| `HTTP 401` | Bad GITHUB_TOKEN or expired SSH session | Run `gh auth login` or re-export valid GITHUB_TOKEN |
| `HTTP 403` | Resource not accessible by integration (missing workflow permissions) | Update repo Settings -> Actions -> General -> Workflow permissions to Read and Write |

## References

- Detailed API Cheatsheet: [api_cheatsheet.md](./references/api_cheatsheet.md)
- Preflight Verification Script: [preflight_check.ps1](./scripts/preflight_check.ps1)
