# PRD: Odoo Knowledge Surfaces

> Product requirements for the three-surface Odoo agent knowledge architecture.

---

## Problem

Current agents can ground on Microsoft documentation via the Learn MCP server, but there is no canonical, repo-governed Odoo 18 + curated OCA + internal SSOT knowledge surface. Agents operating in the Odoo domain lack:

- **Consistent retrieval semantics** for Odoo 18 CE documentation
- **Module discovery** across curated OCA repos with parity metadata
- **Parity guidance** for CE + OCA alternatives to Enterprise features
- **Live instance inspection** for debugging and validation
- **Separation** between retrieval (what docs say), judgment (what to do), and runtime state (what is deployed)

Without these surfaces, agents default to stale training data, hallucinate module names, or attempt unsafe runtime operations without policy gates.

---

## Goal

Provide a Learn-MCP-equivalent experience for the Odoo stack. Agents should be able to search docs, discover modules, reason about implementation paths, and inspect live state -- with each capability governed by a distinct surface with appropriate security posture.

---

## Users

| User Type | Primary Surfaces | Key Workflows |
|-----------|-----------------|---------------|
| Coding agents | A (Docs), B (Skills), C (Runtime) | Module development, debugging, dependency resolution |
| Architecture/judge agents | A (Docs), B (Skills) | Parity assessment, module selection review, migration planning |
| Odoo implementation agents | A (Docs), B (Skills), C (Runtime) | Module installation, configuration validation, upgrade planning |
| Support/triage agents | A (Docs), C (Runtime) | Issue diagnosis, installed-state verification |
| Internal operators | C (Runtime) | Health checks, module state audit, config validation |

---

## Functional Scope (V1)

### Surface A: Docs MCP Tools

| Tool | Input | Output |
|------|-------|--------|
| `search_odoo_docs` | Query string, optional version filter | Ranked doc passages with source URLs |
| `get_odoo_doc_page` | Doc path or URL | Full page content, structured sections |
| `find_oca_module` | Functional description or EE feature name | Matching curated OCA modules with metadata |
| `get_oca_manifest` | Module technical name | Parsed `__manifest__.py`: deps, version, maturity, license |
| `explain_module_dependencies` | Module technical name | Dependency graph (direct + transitive), conflict warnings |
| `suggest_ce_oca_parity_path` | Enterprise feature name | CE + OCA module combination with coverage estimate and gaps |

### Surface B: Skills Pack

| Skill | Purpose | Retrieval Dependency |
|-------|---------|---------------------|
| `odoo_debugging` | Structured troubleshooting for common Odoo errors | `search_odoo_docs`, `explain_module_dependencies` |
| `oca_selection` | Module selection decision tree with quality gates | `find_oca_module`, `get_oca_manifest` |
| `migration_18_to_19` | Heuristics for 18.0-to-19.0 migration issues | `search_odoo_docs`, `get_oca_manifest` |
| `ce_oca_parity` | Parity decisioning for Enterprise replacement paths | `suggest_ce_oca_parity_path`, `find_oca_module` |

### Surface C: Runtime MCP Tools

| Tool | Input | Output | Safety |
|------|-------|--------|--------|
| `inspect_models` | Optional model name filter | Installed model list with field counts | Read-only |
| `inspect_installed_modules` | Optional state filter | Module list with version, state, dependencies | Read-only |
| `inspect_fields` | Model name | Field definitions: type, relation, required, stored | Read-only |
| `inspect_views` | Model name, optional view type | View architecture XML, inheritance chain | Read-only |
| `inspect_actions` | Model name or action ID | Server action / window action definitions | Read-only |
| `read_record_metadata` | Model name, record ID | Create/write dates, user, xmlid, access metadata | Read-only |
| `read_sample_records` | Model name, domain filter, limit (max 10) | Field values for matching records | Read-only, limited |
| `validate_module_state` | Module technical name | Installation state, pending upgrades, dependency health | Read-only |
| `validate_config` | Config parameter name | Current value, default, source | Read-only |

---

## Non-Goals (V1)

| Excluded Capability | Rationale |
|---------------------|-----------|
| Create, write, update, or delete records | Requires policy-gated write architecture (see constitution) |
| Automated production remediation | Write actions against production require maker-checker approval |
| Unrestricted OCA access | Only curated, quality-gated modules are indexed |
| Generalized ERP copiloting | Scope is knowledge retrieval and inspection, not autonomous ERP operation |
| Business analytics workloads | BI/analytics is a Databricks/Power BI concern, not a knowledge surface |

---

## Acceptance Criteria

| # | Criterion | Verification |
|---|-----------|-------------|
| 1 | Spec separates three surfaces with distinct tool namespaces | Review `constitution.md` surface definitions |
| 2 | V1 runtime surface enforces read-only via method allowlist | Allowlist file exists; no write methods listed |
| 3 | Curated corpus is defined and versioned in a manifest file | `agents/knowledge/odoo18_docs/corpus_manifest.yaml` exists |
| 4 | Internal SSOT docs are included in corpus | Manifest references `docs/`, `spec/`, SSOT paths |
| 5 | Skills reference retrieval tools, not hardcoded doctrine | Skill definitions contain tool references, not inline doc content |
| 6 | PRD states write actions require policy gates | This document, Non-Goals section |
| 7 | Each surface has independent auth/audit boundary | Plan specifies per-surface access policy |

---

## Success Metrics

| Metric | Baseline | Target |
|--------|----------|--------|
| Implementation ambiguity (agent asks for clarification on module choice) | Frequent | Rare (skill-guided) |
| First-pass module selection accuracy | Uncontrolled | Measurable via eval golden questions |
| Debugging time (agent reaches root cause) | Uncontrolled | Measurable via eval golden questions |
| Uncontrolled production writes via agent | Possible | Zero (enforced by allowlist) |

---

*Spec bundle: `spec/odoo-knowledge-surfaces/`*
*Created: 2026-03-23*
