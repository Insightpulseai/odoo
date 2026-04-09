# Plan: Odoo Knowledge Surfaces

> Implementation architecture and delivery phases.

---

## Architecture Decision

**Three-surface design.** Retrieval, judgment, and runtime inspection are separated into independent surfaces with distinct tool contracts, security postures, and evolution paths. This mirrors the Microsoft Learn MCP pattern (retrieval) while adding skills (judgment) and runtime (live state) as orthogonal capabilities.

---

## Component Model

### Corpus Adapters

Each source type has a dedicated adapter responsible for extraction, normalization, and versioning.

| Source | Adapter | Scope | Update Frequency |
|--------|---------|-------|-----------------|
| Odoo 18 official docs | `odoo_docs_adapter` | Full official doc tree (developer + user) | Per Odoo release |
| Curated OCA repos | `oca_module_adapter` | Modules listed in `corpus_manifest.yaml` only | Per manifest update |
| Internal SSOT docs | `internal_docs_adapter` | `docs/`, `spec/`, `ssot/`, `agents/knowledge/`, CLAUDE.md chain | On commit to main |
| Internal runbooks | `internal_docs_adapter` | `docs/operations/`, `docs/runbooks/` | On commit to main |

### Normalization Layer

Raw source content is normalized into a common schema before indexing.

| Normalization Step | Input | Output |
|--------------------|-------|--------|
| Module metadata extraction | `__manifest__.py` files | Structured metadata: name, version, deps, maturity, license, description |
| Manifest parsing | OCA repo manifests | Dependency graph edges, version constraints |
| Dependency graph extraction | Module metadata set | Directed acyclic graph with transitive closure |
| Parity tagging | Module metadata + EE feature mapping | Tags: `replaces_ee:<feature>`, `partial_parity`, `full_parity` |
| Doc sectioning | HTML/RST/MD doc pages | Titled sections with source URL, version tag, content hash |

### Retrieval Layer (Surface A)

| Component | Implementation |
|-----------|---------------|
| Index backend | Local vector store (FAISS or similar) with BM25 fallback |
| Search strategy | Hybrid: semantic similarity + keyword matching, re-ranked |
| Source tagging | Every result tagged with `source_type` (official/oca/internal), `version`, `url` |
| Version filtering | Results filterable by Odoo version (default: 19.0) |
| Freshness | Corpus version tracked in manifest; stale results flagged |

### Skills Layer (Surface B)

Skills are promptable playbooks stored as structured YAML/MD files. Each skill declares:

```yaml
name: odoo_debugging
version: "1.0"
description: Structured troubleshooting for common Odoo errors
tools_required:
  - search_odoo_docs
  - explain_module_dependencies
decision_tree:
  - step: Identify error category
    branches:
      - condition: ImportError / ModuleNotFoundError
        action: Check addons path and module dependencies
      - condition: AccessError
        action: Check ACL and record rules
      # ...
```

Skills reference retrieval tools by name. They do not embed retrieved content. This ensures skills stay current as the corpus updates.

### Runtime MCP Layer (Surface C)

| Component | Implementation |
|-----------|---------------|
| Transport | JSON-RPC 2.0 over Odoo external API (XML-RPC or JSON-RPC) |
| Auth | API key or service account with read-only Odoo user profile |
| Method allowlist | Explicit list of permitted `model.method` pairs |
| Audit | Every call logged with timestamp, caller, model, method, arguments |
| Rate limiting | Per-caller, per-minute limits to prevent scan abuse |

**V1 Allowlisted Methods:**

| Model Pattern | Allowed Methods |
|---------------|----------------|
| `ir.module.module` | `search_read`, `read` |
| `ir.model` | `search_read`, `read` |
| `ir.model.fields` | `search_read`, `read` |
| `ir.ui.view` | `search_read`, `read` |
| `ir.actions.*` | `search_read`, `read` |
| `ir.config_parameter` | `search_read`, `get_param` |
| `ir.model.access` | `search_read`, `read` |
| `ir.rule` | `search_read`, `read` |
| Any model | `fields_get`, `check_access_rights` (read only) |

All other model/method combinations are denied by default.

---

## Source-of-Truth Rules

| Question | Canonical Source | Surface |
|----------|-----------------|---------|
| How does Odoo feature X work? | Odoo 18 official docs | A |
| Which OCA module replaces EE feature Y? | Curated OCA corpus + parity tags | A |
| What is our local architecture decision for Z? | Internal SSOT docs | A |
| Should I use module X or module Y? | Skills pack (oca_selection) | B |
| How do I debug error E? | Skills pack (odoo_debugging) | B |
| What modules are installed on instance I? | Runtime MCP | C |
| What fields does model M have on the live instance? | Runtime MCP | C |

---

## Delivery Phases

### Phase 1: Spec + Source Curation + Retrieval Contract

**Deliverables:**
- This spec bundle (constitution, PRD, plan, tasks)
- `agents/knowledge/odoo18_docs/corpus_manifest.yaml` defining curated sources
- Retrieval tool contract (input/output schemas for all 6 Docs MCP tools)
- Source tagging and versioning schema

**Exit criteria:** Manifest reviewed, tool contracts defined, no implementation yet.

### Phase 2: Docs MCP + Basic Corpus Indexing

**Deliverables:**
- Corpus adapters for all three source types
- Normalization pipeline producing indexed corpus
- Docs MCP server implementing 6 retrieval tools
- Integration test: golden questions return relevant results

**Exit criteria:** All 6 tools functional against indexed corpus. Golden question eval passes baseline.

### Phase 3: Skills Pack

**Deliverables:**
- 4 skill definitions (odoo_debugging, oca_selection, migration_18_to_19, ce_oca_parity)
- Skills reference Docs MCP tools, not hardcoded content
- Skill invocation contract (how agents load and execute skills)

**Exit criteria:** Each skill produces actionable output when invoked with a representative scenario.

### Phase 4: Runtime MCP Read-Only

**Deliverables:**
- Runtime MCP server with JSON-RPC transport
- Method allowlist enforcement
- Audit logging
- Per-environment access configuration (dev/staging/prod)
- Integration test: inspect commands return accurate live state

**Exit criteria:** All read-only tools functional. No write methods accessible. Audit log captures all calls.

### Phase 5: Optional Policy-Gated Write Actions (Post-V1)

**Deliverables (deferred):**
- Write action policy document
- Maker-checker approval workflow
- Write method allowlist with per-action approval requirements
- Rollback capability for write actions

**Exit criteria:** Separate spec amendment required before implementation begins.

---

## Security and Policy

| Control | Implementation |
|---------|---------------|
| Model/method allowlists | Explicit allowlist file; deny-by-default |
| Per-environment access policy | Config file mapping environment to allowed surfaces and tools |
| Audit logging | All Surface C calls logged; Surface A/B queries logged at aggregate level |
| No prod writes in V1 | Allowlist contains zero write methods; enforced at MCP server level |
| Approval architecture for writes | Deferred to Phase 5; requires separate spec amendment |
| Corpus integrity | Corpus manifest is version-controlled; unsigned sources rejected |
| Secret handling | Runtime MCP credentials via env vars / Key Vault; never in corpus or skill files |

---

## File Layout

```
agents/
  knowledge/
    odoo18_docs/
      corpus_manifest.yaml      # Curated source list
      adapters/                  # Source-specific extraction
    registry.yaml               # Updated with new knowledge sources
  skills/
    odoo/
      odoo_debugging/SKILL.md
      oca_selection/SKILL.md
      migration_18_to_19/SKILL.md
      ce_oca_parity/SKILL.md
  contracts/
    odoo-knowledge-surfaces/
      docs_mcp_contract.yaml    # Tool input/output schemas (Surface A)
      runtime_mcp_contract.yaml # Tool input/output schemas (Surface C)
      allowlist.yaml            # Runtime MCP method allowlist
spec/
  odoo-knowledge-surfaces/
    constitution.md
    prd.md
    plan.md
    tasks.md
```

---

*Spec bundle: `spec/odoo-knowledge-surfaces/`*
*Created: 2026-03-23*
