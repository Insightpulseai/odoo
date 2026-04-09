---
name: Microsoft Docs Fallback
description: Use when a task depends on Microsoft product facts, Azure platform behavior, Foundry, Fabric, Entra, Azure DevOps, Azure Database for PostgreSQL, or Microsoft SDK/API/CLI syntax, and local indexed knowledge is missing, stale, or ambiguous. Also use for Microsoft-platform troubleshooting.
---

# Microsoft Docs Fallback

## Purpose

Fallback from local project knowledge to trusted official Microsoft documentation through Microsoft Learn MCP.

## When to use

Use this skill when:
- local project docs/specs/SSOT do not answer the question
- the task requires current Microsoft product behavior
- troubleshooting involves Azure or Microsoft services
- the answer needs official Microsoft API, SDK, CLI, limit, or configuration guidance

## Source priority

1. Local indexed project knowledge
2. Microsoft Learn MCP
3. Other official vendor documentation only if Microsoft Learn MCP does not cover the issue

## Tool guidance

- Use `microsoft-docs` for:
  - architecture
  - setup/configuration
  - service limits
  - conceptual guidance
  - security guidance
- Use `microsoft-code-reference` for:
  - SDK/API lookups
  - CLI syntax
  - examples
  - code samples
  - error fixing
  - troubleshooting

## Troubleshooting workflow

1. Summarize the local symptom precisely.
2. Inspect local project docs/config/specs first.
3. Identify which part depends on Microsoft platform behavior.
4. Query Microsoft Learn MCP for the specific service and symptom.
5. Reconcile local intended architecture with official platform behavior.
6. Return:
   - likely root cause
   - recommended fix
   - whether the fix is project-local or platform-contract-driven
   - source class used

## Output format

- `Local finding`
- `Microsoft Learn finding`
- `Decision`
- `Patch or next step`

## Anti-patterns

- Do not use generic web/blog content before Microsoft Learn MCP.
- Do not overwrite project architecture with vendor defaults unless the local design is clearly broken.
- Do not cite Microsoft docs for project-specific conventions that only exist in local SSOT.
