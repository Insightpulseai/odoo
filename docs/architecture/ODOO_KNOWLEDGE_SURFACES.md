# Odoo Knowledge Surfaces

> **Spec**: `spec/odoo-knowledge-surfaces/`
> **SSOT**: `ssot/agents/odoo_knowledge_surfaces.yaml`
> **Owner**: `agents` repo (current: monorepo `odoo/agents/`)
> **Date**: 2026-03-23

---

## Why This Is Not a Monolithic "Odoo Learn MCP"

A single "Odoo MCP" that mixes documentation retrieval, implementation judgment, and live instance operations would create three failure modes:

1. **Docs drift into control plane** — retrieval tools start mutating records.
2. **Uncurated corpus degrades precision** — broad OCA scraping drowns signal.
3. **Decision logic hides in prompts** — judgment that should be explicit skills becomes invisible embedded doctrine.

The architecture splits into three surfaces with distinct trust boundaries:

```text
Surface A: Docs MCP          → reads curated corpus (offline, versioned)
Surface B: Skills Pack        → promptable decision playbooks (offline, authored)
Surface C: Runtime MCP        → inspects live Odoo instance (online, read-only V1)
```

## Surface Boundaries

| Surface | Data source | Online? | Writes? | Trust level |
|---------|------------|---------|---------|-------------|
| Docs MCP | Curated corpus (Odoo 18 docs, selected OCA, internal SSOT) | No | No | High — versioned, reviewed |
| Skills Pack | Authored playbooks in repo | No | No | High — code-reviewed |
| Runtime MCP | Live Odoo ORM/RPC | Yes | **No (V1)** | Medium — allowlisted methods only |

## Curated Corpus Sources

| Source | Authority | Scope |
|--------|-----------|-------|
| Odoo 18 official docs | Canonical for core behavior | Full CE module reference |
| Curated OCA repos | Canonical for community replacement paths | Only repos in `addons.manifest.yaml` |
| Internal SSOT docs | Canonical for local architecture, policy, choices | `docs/`, `spec/`, `ssot/`, `CLAUDE.md` |
| Runtime instance | Canonical only for live installed-state | Inspection only, not retrieval |

**Explicitly excluded**: uncurated OCA repos, Odoo Enterprise docs, third-party module marketplaces, Stack Overflow scrapes.

## Repo Ownership

**Current**: all surfaces defined in `agents` (monorepo path: `odoo/agents/`).

**Future extraction path**: if shared ingestion/indexing infrastructure becomes multi-product, the corpus adapters and index pipeline may move to `platform`. The tool contracts and skills stay in `agents`.

## Relationship to Microsoft Learn MCP

| | Learn MCP | Odoo Knowledge Surfaces |
|-|-----------|------------------------|
| **Lane** | Developer/operator | Production business-agent |
| **Content** | Microsoft docs | Odoo/OCA/internal docs |
| **Consumer** | Human devs + Claude Code | Product copilots + implementation agents |
| **Runtime** | MCP server (stateless fetch) | Azure AI Search index + MCP tools |
| **Scope** | All Microsoft Learn | Curated Odoo + OCA + internal only |

Learn MCP stays in the dev-time tooling lane. Odoo Knowledge Surfaces serve production agents.

## Write-Capable Runtime (Future)

Write-capable runtime actions (create records, execute workflows, approve transactions) require:
- Separate follow-on spec
- Explicit model/method allowlists
- Per-environment access policy
- Approval architecture with audit trail
- Judge-gated execution (not autonomous)

This is not planned for V1.

---

*Cross-references: `spec/odoo-knowledge-surfaces/`, `ssot/agents/odoo_knowledge_surfaces.yaml`*
