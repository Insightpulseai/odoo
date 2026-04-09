# Tasks: Odoo Knowledge Surfaces

> Actionable task breakdown across 5 tracks. Phases map to `plan.md` delivery phases.

---

## Track A — Spec and Source Curation (Phase 1)

### A1: Curated OCA Source List

- [ ] A1.1: Inventory OCA repos with confirmed 18.0 branches
- [ ] A1.2: Cross-reference against `config/addons.manifest.yaml` must-have list (56 modules)
- [ ] A1.3: Add parity-relevant OCA modules not in current must-have list
- [ ] A1.4: Exclude repos without `Stable` or `Mature` development_status
- [ ] A1.5: Write `agents/knowledge/odoo18_docs/corpus_manifest.yaml` with all curated sources
- [ ] A1.6: Define manifest schema (repo URL, branch, modules included, last verified date)

### A2: Source Tagging and Versioning Schema

- [ ] A2.1: Define `source_type` enum: `official`, `oca`, `internal_ssot`, `internal_runbook`
- [ ] A2.2: Define version tagging format (e.g., `odoo:18.0`, `oca:18.0`, `internal:HEAD`)
- [ ] A2.3: Define content hash strategy for change detection
- [ ] A2.4: Document schema in `agents/contracts/odoo-knowledge-surfaces/source_schema.yaml`

### A3: Module Metadata Fields

- [ ] A3.1: Define canonical metadata fields extracted from `__manifest__.py`
- [ ] A3.2: Define extended metadata fields (parity tags, quality tier, test coverage status)
- [ ] A3.3: Define dependency graph edge schema (module, depends_on, version_constraint)
- [ ] A3.4: Document in `agents/contracts/odoo-knowledge-surfaces/module_metadata_schema.yaml`

### A4: Parity Taxonomy

- [ ] A4.1: Define parity levels: `full_parity`, `partial_parity`, `no_parity`, `not_applicable`
- [ ] A4.2: Define EE feature-to-OCA module mapping format
- [ ] A4.3: Seed initial mapping from `docs/ai/EE_PARITY.md` and `.claude/rules/oca-governance.md`
- [ ] A4.4: Write `agents/knowledge/odoo18_docs/parity_mapping.yaml`

### A5: Internal SSOT Source List

- [ ] A5.1: Enumerate internal doc paths for corpus inclusion (`docs/`, `spec/`, `ssot/`, CLAUDE.md chain)
- [ ] A5.2: Define inclusion/exclusion rules (e.g., include `docs/architecture/`, exclude `docs/evidence/`)
- [ ] A5.3: Add internal sources to `corpus_manifest.yaml`

---

## Track B — Docs MCP (Phase 2)

### B1: Corpus Adapters

- [ ] B1.1: Implement `odoo_docs_adapter` — fetch and parse Odoo 18 official doc pages
- [ ] B1.2: Implement `oca_module_adapter` — clone curated repos, extract manifests and READMEs
- [ ] B1.3: Implement `internal_docs_adapter` — read local repo docs with path-based source tagging
- [ ] B1.4: Implement normalization pipeline — produce common schema from all adapters
- [ ] B1.5: Implement dependency graph builder — DAG from module metadata set

### B2: Index and Retrieval

- [ ] B2.1: Set up vector index (FAISS or equivalent) for semantic search
- [ ] B2.2: Set up BM25 index for keyword fallback
- [ ] B2.3: Implement hybrid search with re-ranking
- [ ] B2.4: Implement source and version tagging on all indexed documents
- [ ] B2.5: Implement version filtering (default: 18.0)

### B3: Docs MCP Tools

- [ ] B3.1: Implement `search_odoo_docs` — query string input, ranked passages output
- [ ] B3.2: Implement `get_odoo_doc_page` — doc path input, structured content output
- [ ] B3.3: Implement `find_oca_module` — functional description input, matching modules output
- [ ] B3.4: Implement `get_oca_manifest` — module name input, parsed manifest output
- [ ] B3.5: Implement `explain_module_dependencies` — module name input, dependency graph output
- [ ] B3.6: Implement `suggest_ce_oca_parity_path` — EE feature input, CE+OCA combination output

### B4: Docs MCP Server

- [ ] B4.1: Define MCP tool schemas (JSON Schema for each tool input/output)
- [ ] B4.2: Write `agents/contracts/odoo-knowledge-surfaces/docs_mcp_contract.yaml`
- [ ] B4.3: Implement MCP server exposing all 6 tools
- [ ] B4.4: Add error handling for missing corpus, stale index, unknown modules
- [ ] B4.5: Add logging for query volume and result quality signals

---

## Track C — Skills Pack (Phase 3)

### C1: Odoo Debugging Skill

- [ ] C1.1: Define error category taxonomy (ImportError, AccessError, ValidationError, XML parse, asset bundle, etc.)
- [ ] C1.2: Write decision tree with branching per error category
- [ ] C1.3: Wire retrieval tool references (`search_odoo_docs`, `explain_module_dependencies`)
- [ ] C1.4: Write `agents/skills/odoo/odoo_debugging/SKILL.md`
- [ ] C1.5: Add 5 representative test scenarios with expected outputs

### C2: OCA Module Selection Skill

- [ ] C2.1: Define selection criteria checklist (19.0 branch, maturity, test coverage, conflicts)
- [ ] C2.2: Write decision tree incorporating quality gates from `oca-governance.md`
- [ ] C2.3: Wire retrieval tool references (`find_oca_module`, `get_oca_manifest`)
- [ ] C2.4: Write `agents/skills/odoo/oca_selection/SKILL.md`
- [ ] C2.5: Add 5 representative test scenarios with expected outputs

### C3: Migration 18-to-19 Skill

- [ ] C3.1: Catalog Odoo 18 breaking changes (tree-to-list, groups_id-to-group_ids, Command API, etc.)
- [ ] C3.2: Write heuristic checklist for migration assessment
- [ ] C3.3: Wire retrieval tool references (`search_odoo_docs`, `get_oca_manifest`)
- [ ] C3.4: Write `agents/skills/odoo/migration_18_to_19/SKILL.md`
- [ ] C3.5: Add 5 representative test scenarios with expected outputs

### C4: CE/OCA Parity Skill

- [ ] C4.1: Define parity assessment framework (feature gap analysis, coverage scoring)
- [ ] C4.2: Write decision tree for replacement path selection
- [ ] C4.3: Wire retrieval tool references (`suggest_ce_oca_parity_path`, `find_oca_module`)
- [ ] C4.4: Write `agents/skills/odoo/ce_oca_parity/SKILL.md`
- [ ] C4.5: Add 5 representative test scenarios with expected outputs

---

## Track D — Runtime MCP (Phase 4)

### D1: Read-Only Tool Contract

- [ ] D1.1: Define method allowlist YAML (`agents/contracts/odoo-knowledge-surfaces/allowlist.yaml`)
- [ ] D1.2: Define tool input/output schemas for all 9 runtime tools
- [ ] D1.3: Write `agents/contracts/odoo-knowledge-surfaces/runtime_mcp_contract.yaml`
- [ ] D1.4: Define deny-by-default enforcement mechanism

### D2: Runtime MCP Tools

- [ ] D2.1: Implement `inspect_models` — list installed models with field counts
- [ ] D2.2: Implement `inspect_installed_modules` — module list with state and deps
- [ ] D2.3: Implement `inspect_fields` — field definitions for a given model
- [ ] D2.4: Implement `inspect_views` — view XML and inheritance chain for a model
- [ ] D2.5: Implement `inspect_actions` — server/window action definitions
- [ ] D2.6: Implement `read_record_metadata` — create/write dates, user, xmlid
- [ ] D2.7: Implement `read_sample_records` — limited record read with domain filter
- [ ] D2.8: Implement `validate_module_state` — installation state and dependency health
- [ ] D2.9: Implement `validate_config` — config parameter current value and source

### D3: Environment Allowlists

- [ ] D3.1: Define per-environment config (dev: all tools, staging: all tools, prod: restricted subset)
- [ ] D3.2: Implement environment detection and policy loading
- [ ] D3.3: Document environment access matrix

### D4: Audit Logging

- [ ] D4.1: Define audit log schema (timestamp, caller, environment, model, method, args hash, result status)
- [ ] D4.2: Implement audit logger for all Runtime MCP calls
- [ ] D4.3: Add log rotation and retention policy
- [ ] D4.4: Add alert threshold for unusual query patterns

### D5: Runtime MCP Server

- [ ] D5.1: Implement MCP server with JSON-RPC transport to Odoo
- [ ] D5.2: Implement allowlist enforcement layer
- [ ] D5.3: Implement rate limiting per caller
- [ ] D5.4: Add connection health check and reconnection logic
- [ ] D5.5: Add graceful degradation when Odoo instance is unreachable

---

## Track E — Evaluation (Continuous)

### E1: Docs Retrieval Evaluation

- [ ] E1.1: Write 20 golden questions for Odoo 18 doc retrieval (expected doc page, expected passage)
- [ ] E1.2: Write 10 golden questions for internal SSOT retrieval
- [ ] E1.3: Implement scoring script: precision@5, recall@5, MRR
- [ ] E1.4: Set baseline thresholds (MRR >= 0.6 for V1)
- [ ] E1.5: Add eval to CI as regression gate

### E2: OCA Module Discovery Evaluation

- [ ] E2.1: Write 15 golden queries for OCA module discovery (feature description -> expected module)
- [ ] E2.2: Write 10 golden queries for manifest metadata retrieval
- [ ] E2.3: Implement scoring script: exact match@1, match@3
- [ ] E2.4: Set baseline thresholds (exact match@3 >= 0.8 for V1)

### E3: Parity Recommendation Evaluation

- [ ] E3.1: Write 10 golden queries for CE+OCA parity paths (EE feature -> expected module set)
- [ ] E3.2: Validate recommendations against `docs/ai/EE_PARITY.md` known mappings
- [ ] E3.3: Score coverage accuracy and gap identification completeness

### E4: Runtime MCP Safety Tests

- [ ] E4.1: Write negative tests: attempt write methods, verify denial
- [ ] E4.2: Write negative tests: attempt access to non-allowlisted models, verify denial
- [ ] E4.3: Write negative tests: attempt access without auth, verify denial
- [ ] E4.4: Write positive tests: all 9 read-only tools return valid data
- [ ] E4.5: Write audit tests: verify all calls appear in audit log
- [ ] E4.6: Write rate limit tests: verify throttling at threshold

### E5: Regression Tests

- [ ] E5.1: Define curated module set for regression (10 OCA modules, 5 ipai modules)
- [ ] E5.2: Write end-to-end test: search -> discover -> inspect cycle for each module
- [ ] E5.3: Write skill regression: each skill produces valid output for its test scenarios
- [ ] E5.4: Add regression suite to CI pipeline

---

## Task Summary

| Track | Tasks | Phase |
|-------|-------|-------|
| A — Spec and Source Curation | 17 | 1 |
| B — Docs MCP | 16 | 2 |
| C — Skills Pack | 20 | 3 |
| D — Runtime MCP | 19 | 4 |
| E — Evaluation | 16 | Continuous |
| **Total** | **88** | |

---

*Spec bundle: `spec/odoo-knowledge-surfaces/`*
*Created: 2026-03-23*
