---
name: cloudflare-workers
description: >-
  Deploy, configure, and orchestrate Cloudflare Workers, KV namespaces, and D1 serverless SQL databases using Wrangler v3.
---

# Cloudflare Workers & D1 Edge Runtime

Laser-focused, narrow-specialized skill for Cloudflare Workers & D1 Edge Runtime. Validated against official documentation.

## Capability Split

| Phase | What | Transport | Surface |
| :--- | :--- | :--- | :--- |
| 1 | Local Dev & Emulation | CLI | `npx wrangler dev` |
| 2 | D1 Database Migrations | CLI | `npx wrangler d1 migrations apply` |
| 3 | KV Key-Value Binding | REST/CLI | `npx wrangler kv:key put` |
| 4 | Edge Deployment | CLI | `npx wrangler deploy` |

## Auth & Preflight Requirements

**Token Name**: `CLOUDFLARE_API_TOKEN`
**Required Scopes**: `Account.Workers`, `Account.D1`, `Account.KV Storage`

> [!IMPORTANT]
> Before running commands, verify that `CLOUDFLARE_API_TOKEN` is present in the environment or project `.env` file. Never ask the user to paste credentials directly into chat.

## Execution Steps & Commands

### Initialize Project
Generates a clean TypeScript worker structure with wrangler.jsonc

```bash
npm create cloudflare@latest -- --type hello-world --ts
```

### Local Emulation
Starts Miniflare-based local simulation matching edge constraints

```bash
npx wrangler dev --port 8787
```

### Apply D1 Schema
Applies SQL migrations locally or remotely

```bash
npx wrangler d1 migrations apply <DB_NAME> --local
```

## Error Handling & Edge Cases

| Error Code | Root Cause | Agent Action |
| :--- | :--- | :--- |
| `10001` | Invalid Cloudflare API Token or missing permissions | Verify CLOUDFLARE_API_TOKEN and check Account-level scopes in CF dashboard |
| `429` | Rate limit exceeded on Edge KV/D1 mutations | Implement exponential backoff retry with jitter |

## References

- Detailed API Cheatsheet: [api_cheatsheet.md](./references/api_cheatsheet.md)
- Preflight Verification Script: [preflight_check.ps1](./scripts/preflight_check.ps1)
