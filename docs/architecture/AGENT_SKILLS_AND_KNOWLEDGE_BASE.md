# Agent Skills and Knowledge Base

> **Status**: Active
> **SSOT**: `ssot/agent-platform/`
> **Last updated**: 2026-04-10

---

## Overview

The agent skill pack is a set of benchmark gap-closure skills living in `.github/skills/`. Each skill teaches the agent runtime how to ground responses against Microsoft Learn documentation, repo-local SSOT, and Azure AI Search. The knowledge base layer reconciles external MCP-sourced content against repo-authoritative truth — repo always wins on conflict.

---

## Architecture

```
.github/skills/<skill-name>/
        SKILL.md  +  examples.md
              |
              v
  MCP query plan (learn_mcp_topic_map.yaml)
              |
              v
  Microsoft Learn MCP  ──────────────────────────────────────────┐
  https://learn.microsoft.com/api/mcp                            |
    tools: microsoft_docs_search                                  |
           microsoft_code_sample_search                           |
           microsoft_docs_fetch                                   |
              |                                                   |
              v                                                   v
  Azure AI Search (srch-ipai-dev)          Repo SSOT (ssot/**, docs/architecture/**)
  index: ipai-knowledge-index              knowledge_sources.yaml (source_precedence[0])
              |                                   |
              └──────────────┬────────────────────┘
                             v
                  Reconciled knowledge (repo wins on conflict)
                             |
                             v
              Agent runtime (Foundry, ipai-copilot project)
```

---

## Skill Pack

All 10 skill directories currently in `.github/skills/`:

| Skill | Tier | Category |
|-------|------|----------|
| `aca-private-networking` | tier1 | Azure Runtime |
| `azure-foundry-architecture` | tier1 | AI / Foundry |
| `azure-foundry-grounding` | tier1 | AI / Foundry |
| `azure-observability-baseline` | tier2 | Azure Runtime |
| `azure-pg-ha-dr` | tier2 | Azure Runtime |
| `azure-policy-guardrails` | tier2 | Security |
| `entra-mfa-ca-hardening` | tier2 | Security / Identity |
| `odoo-copilot-evals` | tier2 | Odoo Runtime |
| `odoo-image-supply-chain` | tier3 | Odoo Runtime |
| `odoo-release-promotion` | tier3 | Release / CI |
| `service-matrix-truth` | tier3 | Governance |

Each skill directory contains exactly two files: `SKILL.md` (definition) and `examples.md` (usage examples). The test contract enforces this on every CI run.

---

## Knowledge Sources

Source precedence is enforced in `ssot/agent-platform/knowledge_sources.yaml`. Lower number = higher authority. On conflict, the higher-priority source always wins and the divergence must be documented.

| Priority | Source Type | Description |
|----------|-------------|-------------|
| 1 | `repo_ssot` | `ssot/**/*.yaml` — platform intent and doctrine |
| 2 | `architecture_doc` | `docs/architecture/**` — design decisions and contracts |
| 3 | `microsoft_learn` | Microsoft Learn MCP — official Azure / Foundry docs |
| 4 | `github_samples` | Azure-Samples and OCA GitHub repositories |
| 5 | `secondary` | Vendor docs, community references |

---

## Microsoft Learn MCP Integration

**Endpoint**: `https://learn.microsoft.com/api/mcp`

**Available tools**:

| Tool | Use |
|------|-----|
| `microsoft_docs_search` | Full-text search across Microsoft Learn |
| `microsoft_code_sample_search` | Search Azure-Samples and code examples |
| `microsoft_docs_fetch` | Fetch full content of a specific doc URL |

**Query patterns** (from `ssot/agent-platform/learn_mcp_topic_map.yaml`):

```yaml
topics:
  - id: aca-networking
    query: "Azure Container Apps private networking VNET ingress"
    tools: [microsoft_docs_search, microsoft_docs_fetch]
    tier: tier1

  - id: foundry-agent-service
    query: "Azure AI Foundry Agent Service SDK v2 create agent"
    tools: [microsoft_docs_search, microsoft_code_sample_search]
    tier: tier1
```

The refresh script (`scripts/agent_platform/refresh_microsoft_learn_kb.py`) validates the topic map and generates the query plan. It does not call MCP directly — that requires the agent runtime.

---

## SSOT Override Policy

When repo-local SSOT conflicts with Microsoft Learn documentation:

1. **Repo wins**. The SSOT in `ssot/agent-platform/` reflects actual platform decisions, which may diverge from generic Azure guidance.
2. **Document the divergence**. Add a `divergence` field to the relevant entry in `knowledge_sources.yaml`.
3. **Do not suppress the Microsoft Learn content**. Record it as `secondary` evidence alongside the repo position.

Example divergence documentation:

```yaml
# In knowledge_sources.yaml
- id: pg-ha-topology
  type: repo_ssot
  path: ssot/agent-platform/azure-pg-ha-dr/
  diverges_from: microsoft_learn
  divergence_reason: >
    Microsoft Learn recommends Zone-Redundant HA by default. This repo uses
    Same-Zone HA on General Purpose due to cost constraints until HA gate passes.
```

---

## Refreshing the Knowledge Base

```bash
# Dry run (default) — validates manifests, generates query plan, no files written
python scripts/agent_platform/refresh_microsoft_learn_kb.py

# Execute — writes evidence report to docs/evidence/<YYYYMMDD-HHMM>/kb-refresh/report.yaml
python scripts/agent_platform/refresh_microsoft_learn_kb.py --execute

# Custom output directory
python scripts/agent_platform/refresh_microsoft_learn_kb.py --execute --output-dir docs/evidence/custom/
```

**What the script checks**:
- All four SSOT manifests exist and are valid YAML
- Each topic in `learn_mcp_topic_map.yaml` has `id`, `query`, `tools`, `tier`
- `knowledge_sources.yaml` source precedence is in correct order
- All repo-local paths in `knowledge_sources.yaml` exist on disk
- `skills_manifest.yaml` references only skills that exist in `.github/skills/`
- `knowledge_taxonomy.yaml` topic IDs are in the topic map
- No MVP-critical topics (tier1/tier2) appear in `deferred_optional`

**Output**: `docs/evidence/<stamp>/kb-refresh/report.yaml` — a structured YAML with topic gaps, missing paths, scope creep warnings, and the full MCP query plan.

---

## Validating Outputs

```bash
# Run the full contract test suite
python -m pytest tests/agent_platform/test_knowledge_contract.py -v

# Run a single test class
python -m pytest tests/agent_platform/test_knowledge_contract.py::TestManifestExistence -v
```

**Test coverage**:

| Test Class | What It Checks |
|------------|----------------|
| `TestManifestExistence` | All four SSOT manifests exist and parse as valid YAML |
| `TestKnowledgeSources` | Source precedence order; repo-local path existence |
| `TestTopicMap` | Required fields per topic; unique IDs; valid MCP tools |
| `TestSkillsManifest` | Declared skills exist on disk; no duplicates |
| `TestKnowledgeTaxonomy` | Valid topic key references; no MVP topics in deferred |
| `TestSkillsOnDisk` | Every skill dir has both `SKILL.md` and `examples.md` |
| `TestCrossManifestConsistency` | Cross-reference checks between all four manifests |

---

## Manifests

All manifests live in `ssot/agent-platform/`:

| File | Purpose |
|------|---------|
| `learn_mcp_topic_map.yaml` | Maps each knowledge topic to MCP query parameters and tier |
| `knowledge_sources.yaml` | Declares source types, precedence order, and repo-local paths |
| `skills_manifest.yaml` | Authoritative list of all skills in the skill pack |
| `knowledge_taxonomy.yaml` | Taxonomy of topics: active, deferred, excluded |

Companion manifests (existing):

| File | Purpose |
|------|---------|
| `ssot/agents/knowledge-bindings.yaml` | Agent-to-knowledge-collection bindings |
| `ssot/agent-platform/foundry_tool_policy.yaml` | Tool approval and allowed_tools policy |
| `ssot/agent-platform/mcp_policy.yaml` | MCP transport, scope, and server policy |

---

## Scope Boundaries

**In scope**:
- `.github/skills/` skill directories (benchmark gap-closure)
- `ssot/agent-platform/` manifests for knowledge and skills
- Microsoft Learn MCP as a secondary knowledge source (never primary)
- Azure AI Search index `ipai-knowledge-index` on `srch-ipai-dev`
- Evidence reports in `docs/evidence/`

**Deferred** (see `knowledge_taxonomy.yaml:deferred_optional`):
- Fabric IQ knowledge grounding (pending Fabric deployment)
- Work IQ / M365 Copilot integration (not in MVP scope)
- Databricks Unity Catalog as live knowledge source (future)

**Excluded**:
- Supabase (fully deprecated 2026-03-26)
- Cloudflare Workers AI (deprecated 2026-04-07)
- Any non-Azure AI Search vector store
- Direct MCP calls from scripts (requires agent runtime — use refresh script for manifest validation only)

---

## Infrastructure References

| Resource | Value |
|----------|-------|
| Azure AI Search | `srch-ipai-dev`, index `ipai-knowledge-index` |
| Foundry project | `ipai-copilot` |
| Foundry resource | `ipai-copilot-resource` |
| Foundry region | `eastus2` |
| Key Vault | `kv-ipai-dev` |
| MCP endpoint | `https://learn.microsoft.com/api/mcp` |
