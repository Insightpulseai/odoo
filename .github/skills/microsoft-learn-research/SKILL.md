---
name: microsoft-learn-research
description: Meta-skill for querying Microsoft Learn MCP server to resolve Azure architecture questions and validate configurations against official documentation
version: "1.0"
compatibility:
  hosts: [github-copilot, claude-code, codex-cli, cursor, gemini-cli]
tags: [architecture, governance, foundry, networking]
---

# microsoft-learn-research

**Impact tier**: P1 -- Operational Readiness

## Purpose

General-purpose research skill for querying the Microsoft Learn MCP server to
resolve Azure architecture questions, validate configurations against official
documentation, and fill knowledge gaps. This is the meta-skill referenced by
all other skills in this pack when they need MCP queries. It documents best
practices for query construction, result filtering, citation format, and
escalation when MCP results are insufficient.

## When to Use

- Before patching any Azure resource configuration: retrieve the canonical
  Microsoft recommendation first.
- When an unfamiliar Azure service parameter is encountered in IaC.
- When a gap audit references a Microsoft Learn URL that needs full content.
- When other skills' MCP queries return insufficient results and need refinement.

## Required Evidence (inspect these repo paths first)

| Path | What to look for |
|------|-----------------|
| `.codex/config.toml` | MCP server URL registration (`[mcp_servers.microsoft-learn]`) |
| `.github/skills/README.md` | Authority order: repo first, MCP second, docs/specs third |
| `ssot/agent-platform/foundry_tool_policy.yaml` | Tool preference hierarchy: built-in > function calling > OpenAPI > MCP |

## Microsoft Learn MCP Usage

This skill IS the MCP query skill. The three available tools are:

### `microsoft_docs_search`

Breadth search across Microsoft Learn. Returns up to 10 document chunks.

Best practices:
- Use 4-8 specific terms. Vague queries return generic results.
- Include the Azure service name AND the specific feature: `"Azure Container Apps VNet integration"` not just `"container apps networking"`.
- Include the action or concept: `"private access disable public"` not just `"security"`.
- Append SDK language when relevant: `"Python SDK"`, `"Bicep"`, `"REST API"`.

```
microsoft_docs_search("Azure PostgreSQL Flexible Server private access VNet integration Bicep")
microsoft_docs_search("Azure AI Foundry Agent Service Python SDK v2 create agent")
microsoft_docs_search("Azure Container Apps health probes liveness readiness startup Bicep")
```

### `microsoft_code_sample_search`

Targeted code sample search. Supports `language` filter.

Best practices:
- Use for specific implementation patterns, not conceptual questions.
- Always specify `language` when searching for IaC or SDK code.
- Combine service name with the specific pattern: `"bicep postgresql flexible server zone redundant ha"`.

```
microsoft_code_sample_search("bicep container app managed identity key vault", language="bicep")
microsoft_code_sample_search("azure foundry agent python create thread run", language="python")
microsoft_code_sample_search("bicep postgresql flexible server vnet delegation private dns", language="bicep")
```

### `microsoft_docs_fetch`

Retrieves the full markdown of a known Microsoft Learn URL. Use when a
`microsoft_docs_search` result references a page that needs complete content.

Best practices:
- Always use `learn.microsoft.com` URLs, not external links.
- Fetch when you need a complete parameter reference table, not just a snippet.
- Cache the result in `docs/evidence/<stamp>/<skill>/mcp-fetch-<slug>.md`.

```
microsoft_docs_fetch("https://learn.microsoft.com/en-us/azure/postgresql/flexible-server/concepts-networking-private")
microsoft_docs_fetch("https://learn.microsoft.com/en-us/azure/container-apps/scale-app")
microsoft_docs_fetch("https://learn.microsoft.com/en-us/azure/ai-services/agents/overview")
```

## Workflow

1. **Inspect repo** -- Confirm `.codex/config.toml` has the MCP server registered.
   Confirm the skill README authority order. Identify which Azure service and
   feature the research question targets.
2. **Query MCP** -- Start with `microsoft_docs_search` (2-3 queries, refining
   terms if results are too broad). If results reference specific URLs, use
   `microsoft_docs_fetch`. If implementation code is needed, use
   `microsoft_code_sample_search`.
3. **Compare** -- Map MCP results to the current repo state. Note any parameter
   values, API shapes, or architectural recommendations that differ from IaC
   or SSOT.
4. **Patch** -- Apply the finding: update IaC, SSOT YAML, or runbook. Always
   cite the MCP source in a comment: `# Source: microsoft_docs_search("<query>")`.
5. **Verify** -- Confirm the patched file is syntactically valid (Bicep lint,
   Python ruff, YAML parse). Commit evidence with MCP excerpts.

## Outputs

| File | Change |
|------|--------|
| `docs/evidence/<stamp>/microsoft-learn-research/mcp-results.md` | Raw MCP query results with citations |
| The file targeted by the research question | Configuration patched per MCP guidance |

## Completion Criteria

- [ ] `.codex/config.toml` confirms MCP server at `https://learn.microsoft.com/api/mcp`.
- [ ] Each MCP query result is cited in code comments or evidence files using the format: `# Source: microsoft_docs_search("<query>")`.
- [ ] No configuration value was invented: every parameter came from repo evidence, MCP results, or existing SSOT.
- [ ] Evidence directory contains the raw MCP query and result for each research question answered.
- [ ] If MCP returned no useful results for a query, the gap is flagged explicitly in the evidence file as `BLOCKED: MCP returned insufficient results for "<query>"`.
