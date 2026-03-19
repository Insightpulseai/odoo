# Organization Documentation Source Inventory

> Generated: 2026-03-15
> Scope: Insightpulseai/odoo repository
> Machine-readable counterpart: `ssot/docs/source_inventory.yaml`

---

## Summary Statistics

| Metric | Count |
|--------|-------|
| Total .md files (excluding node_modules, .git, archive, vendor) | 8,254 |
| docs/ directory files | 3,073 |
| spec/ bundles (files) | 108 |
| ssot/ files | 62 |
| agents/ files (non-cache) | 587 |
| ssot/ files (infra) | 183 |
| config/ files | 16 |
| .claude/ .md files | 52 |
| docs/contracts/ .md files | 38 |
| docs/architecture/ .md files | 196 |
| docs/evidence/ directories (depth 2) | 201 |
| CLAUDE.md files (all levels) | 3 |
| addons/ipai/ modules | 84 |

---

## Classification Breakdown

### By Doc Type

| Doc Type | Count | Locations |
|----------|-------|-----------|
| Architecture | ~196 | `docs/architecture/`, `docs/ai/ARCHITECTURE.md` |
| Contracts | 38 | `docs/contracts/` |
| Specs | ~108 files across ~22 bundles | `spec/` |
| Runbooks | ~1 + scripts | `docs/runbooks/`, `scripts/` |
| Config | 16 | `config/` |
| Reference (AI) | 62 | `docs/ai/` |
| Evidence | ~201 bundles | `docs/evidence/` |
| Modules | ~204 | `docs/modules/` |
| Guides | ~122 | `docs/guides/` |
| Governance | ~45 | `docs/governance/` |
| Integrations | ~49 | `docs/integrations/` |
| KB (knowledge base) | ~1,170 | `docs/kb/` |
| Deployment | ~48 | `docs/deployment/` |
| Operations | ~106 | `docs/operations/` |
| Security | ~15 | `docs/security/` |
| Design | ~47 | `docs/design/` |
| Product | ~63 | `docs/product/` |
| Portfolio | ~303 | `docs/portfolio/` |
| Releases | ~20 | `docs/releases/` |
| Agent skills | ~100+ SKILL.md | `agents/skills/` |
| SSOT manifests | ~62 + ~183 | `ssot/` |

### By Classification

| Classification | Count | Description |
|----------------|-------|-------------|
| Canonical internal | ~800 | Authoritative, maintained, should be indexed |
| Generated/derived | ~50 | Auto-generated (ERDs, runtime identifiers, settings catalog) |
| Stale/legacy | ~200+ | Archive content, deprecated references, old infra docs |
| External reference | ~15 | Source.yaml files pointing to external docs |
| Evidence | ~201 bundles | Proof artifacts, not source of truth |

### By Indexing Priority

| Priority | Count | Description |
|----------|-------|-------------|
| P0 (must index) | ~350 | CLAUDE.md, contracts, architecture, SSOT manifests, specs, config |
| P1 (should index) | ~400 | AI reference docs, agent skills, guides, modules, governance |
| P2 (nice to have) | ~600 | KB articles, design docs, portfolio, product docs |
| P3 (skip) | ~6,900+ | Evidence bundles, OCA readme fragments, node_modules, archive |

---

## Source Inventory by Area

### 1. CLAUDE.md Files (P0 -- Agent Policy)

| Path | Classification | Freshness | Notes |
|------|---------------|-----------|-------|
| `CLAUDE.md` | canonical internal | active | Root project SSOT, updated 2026-03-08 |
| `odoo/CLAUDE.md` | canonical internal | active | Odoo subproject context |
| `archive/root-cleanup-20260224/sandbox/dev/CLAUDE.md` | stale/legacy | deprecated | Archived, superseded |

### 2. docs/ai/ (P0/P1 -- AI Reference)

62 markdown files. Key documents:

| Path | Doc Type | Priority | Notes |
|------|----------|----------|-------|
| `docs/ai/ARCHITECTURE.md` | architecture | P0 | Stack architecture reference |
| `docs/ai/CI_WORKFLOWS.md` | reference | P0 | CI pipeline docs |
| `docs/ai/EE_PARITY.md` | reference | P0 | Enterprise parity tracking |
| `docs/ai/INTEGRATIONS.md` | reference | P0 | Integration map |
| `docs/ai/IPAI_MODULES.md` | reference | P0 | Module naming conventions |
| `docs/ai/MCP_SYSTEM.md` | reference | P0 | MCP server docs |
| `docs/ai/OCA_WORKFLOW.md` | reference | P0 | OCA adoption workflow |
| `docs/ai/REPO_STRUCTURE.md` | reference | P0 | Repo layout docs |
| `docs/ai/TESTING.md` | reference | P1 | Testing strategy |
| `docs/ai/DOCKER.md` | reference | P1 | Docker setup |
| `docs/ai/TROUBLESHOOTING.md` | reference | P1 | Troubleshooting guide |
| `docs/ai/BIR_COMPLIANCE.md` | reference | P1 | BIR tax compliance |
| `docs/ai/external/` | external reference | P2 | 14 files, mostly FETCH_FAILED stubs |

### 3. docs/contracts/ (P0 -- Platform Contracts)

38 contract documents. All classified as canonical internal, active, P0.

Key contracts:
- `PLATFORM_CONTRACTS_INDEX.md` -- master index
- `COPILOT_RUNTIME_CONTRACT.md` -- copilot runtime
- `COPILOT_CAPABILITY_EVAL_CONTRACT.md` -- eval framework
- `DOCS_AUTHORITY_BOUNDARIES.md` -- doc authority mapping
- `DATA_AUTHORITY_CONTRACT.md` -- data ownership
- `API_*` contracts (4 files) -- API boundaries
- `SUPABASE_*` contracts (5 files) -- Supabase integrations
- `C-*` contracts (8 files) -- cross-domain contracts

### 4. docs/architecture/ (P0/P1 -- Architecture)

196 markdown files. Very large surface. Key documents:

| Path | Priority | Notes |
|------|----------|-------|
| `docs/architecture/ADDONS_PATH_INVARIANTS.md` | P0 | Odoo addons path rules |
| `docs/architecture/AGENTIC_CODING_CONTRACT.md` | P0 | Agent coding rules |
| `docs/architecture/AI_OPERATING_MODEL.md` | P0 | AI operations model |
| `docs/architecture/ASK_AI_CONTRACT.md` | P0 | Ask AI feature contract |
| `docs/architecture/AUTH_ARCHITECTURE.md` | P0 | Auth architecture |
| `docs/architecture/AZURE_ODOOSH_EQUIVALENT_TARGET_STATE.md` | P1 | Azure target state |
| `docs/architecture/SSOT_BOUNDARIES.md` | P0 | SSOT domain mapping |
| `docs/architecture/PLATFORM_REPO_TREE.md` | P0 | Canonical repo tree |

### 5. spec/ Bundles (P0 -- Specifications)

22 spec bundles with ~108 files. Each bundle contains: constitution.md, prd.md, plan.md, tasks.md.

| Bundle | Priority | Status |
|--------|----------|--------|
| `spec/docs-platform/` | P0 | Active -- this project |
| `spec/enterprise-target-state/` | P0 | Active |
| `spec/odoo-copilot/` | P0 | Active |
| `spec/odoo-copilot-benchmark/` | P0 | Active (includes YAML scenarios) |
| `spec/finance-unified/` | P1 | Active |
| `spec/lakehouse/` | P1 | Active |
| `spec/azure-selfhost-migration/` | P1 | Active |
| `spec/platform-auth/` | P1 | Active |
| `spec/unified-api-gateway/` | P1 | Active |
| `spec/odoo-erp-saas/` | P1 | Active |
| `spec/adls-etl-reverse-etl/` | P2 | Active |
| `spec/sap-joule-concur-odoo-azure/` | P2 | Active |
| `spec/well-architected/` | P1 | Active (JSON lens) |

### 6. ssot/ (P0 -- Machine-Readable SSOT)

62 files in `ssot/` root, 183 files consolidated from `infra/ssot/` into `ssot/`.

Key SSOT files:

| Path | Doc Type | Priority |
|------|----------|----------|
| `ssot/docs/docs-platform-canonical-map.yaml` | config | P0 |
| `ssot/docs/docs-content-build-manifest.yaml` | config | P0 |
| `ssot/parity_targets.yaml` | config | P0 |
| `ssot/odoo/copilot_runtime_contract.yaml` | contract | P0 |
| `ssot/agents/rules-manifest.yaml` | config | P0 |
| `ssot/ai/sources.yaml` | config | P0 |
| `ssot/integrations/_index.yaml` | config | P0 |
| `ssot/runtime/environments.inventory.yaml` | config | P0 |
| `ssot/azure/service-matrix.yaml` | config | P0 |
| `ssot/azure/resources.yaml` | config | P0 |
| `ssot/odoo/oca_repos.yaml` | config | P0 |
| `ssot/parity/ee_to_oca_matrix.yaml` | config | P0 |
| `ssot/knowledge/corpus_registry.yaml` | config | P0 |
| `ssot/integrations/*.yaml` (30+ files) | config | P1 |

### 7. agents/ (P1 -- Agent Framework)

587 files. Key areas:

| Area | Files | Priority | Notes |
|------|-------|----------|-------|
| `agents/skills/odoo19/` | 60+ SKILL.md | P1 | Odoo 19 functional skills |
| `agents/skills/odoo/` | 20+ SKILL.md | P1 | Odoo development skills |
| `agents/knowledge/` | 10+ files | P0 | KB contracts (source.yaml, chunking.yaml) |
| `agents/evals/` | 2 YAML | P0 | Capability evaluation framework |
| `agents/registry/` | 4 files | P1 | Agent/skill registries |
| `agents/mcp/` | 30+ files | P1 | MCP server implementations |
| `agents/library-pack/` | 15+ files | P2 | Prompt library |
| `agents/studio/` | 20+ files | P2 | Agent personas |

### 8. config/ (P0 -- Configuration)

| Path | Doc Type | Priority | Notes |
|------|----------|----------|-------|
| `config/addons.manifest.yaml` | config | P0 | Addons installation manifest |
| `config/odoo/settings.yaml` | config | P0 | Odoo settings |
| `config/odoo/mail_settings.yaml` | config | P0 | Mail configuration |
| `config/dev/odoo.conf` | config | P0 | Dev environment config |
| `config/prod/odoo.conf` | config | P0 | Prod environment config |
| `config/ENVIRONMENTS.md` | reference | P0 | Environment documentation |

### 9. infra/ (P1 -- Infrastructure)

Key areas (excluding vendor):

| Area | Priority | Notes |
|------|----------|-------|
| `infra/dns/subdomain-registry.yaml` | P0 | DNS SSOT |
| `infra/azure/` | P1 | Azure configuration |
| `infra/cloudflare/` | P1 | Cloudflare/DNS |
| `infra/databricks/` | P1 | Databricks config |
| `infra/deploy/` | P1 | K8s/deployment manifests |
| `infra/ops-control/` | P2 | Ops control room (50+ docs, partially stale) |
| `ssot/` | P0 | SSOT manifests (consolidated, 183+ files) |

### 10. packages/odoo-docs-kb/ (P0 -- Reusable Components)

| File | Purpose | Priority |
|------|---------|----------|
| `chunker.py` | RST heading-aware chunker | P0 |
| `md_chunker.py` | Markdown heading-aware chunker | P0 |
| `embed.py` | Azure OpenAI embedder | P0 |
| `index.py` | Azure AI Search indexer | P0 |
| `loader.py` | Document loader | P0 |
| `web_loader.py` | Web document loader | P0 |
| `eval.py` | Retrieval evaluation | P0 |

### 11. apps/odoo-docs-kb/ (P0 -- RAG Service)

| File | Purpose | Priority |
|------|---------|----------|
| `service.py` | FastAPI RAG search service | P0 |
| `Dockerfile` | Container definition | P0 |
| `requirements.txt` | Python dependencies | P0 |

### 12. addons/ipai/ Module READMEs (P1)

~40 README.md files across ipai modules. Each is a module-level reference. Classified as canonical internal, P1.

### 13. docs/evidence/ (P3 -- Evidence Bundles)

~201 evidence directories. These are derived proof artifacts, not source of truth. Skip for indexing per SSOT rules.

### 14. docs/kb/ (P2 -- Knowledge Base Articles)

~1,170 files. Large volume, likely auto-generated or crawled content. Classify as P2.

### 15. scripts/ (P1 -- Runbook-Like Scripts)

~25 shell scripts with embedded documentation. Key scripts:
- `scripts/odoo/install-oca-modules.sh`
- `scripts/azure/deploy-bot-service.sh`
- `scripts/ci/*` (CI scripts)

### 16. .github/workflows/ (P1 -- CI Workflows)

~85 workflow YAML files. Key workflows documented in CLAUDE.md.

---

## Duplication Analysis

| Duplicate Area | Locations | Resolution |
|---------------|-----------|------------|
| SSOT manifests | `ssot/` | Consolidated under `ssot/` (previously split across `ssot/` and `infra/ssot/`). |
| Parity tracking | `ssot/parity_targets.yaml` AND `ssot/parity/` | Consolidated under `ssot/`. |
| Agent registries | `agents/registry/` AND `ssot/agents/` | Two registry locations. |
| GitHub config | `ssot/github/` | Consolidated under `ssot/`. |
| Knowledge source | `agents/knowledge/KNOWLEDGE_BASE_INDEX.yaml` | Contains outdated paths (e.g., `/home/user/odoo/`) and v18 references. Stale. |
| Docs canonical map | `ssot/docs/docs-platform-canonical-map.yaml` AND `ssot/docs/plane-docs-canonical-map.yaml` | Two overlapping canonical maps. |
| Integration SSOT | `ssot/integrations/` | Consolidated under `ssot/`. |

## Drift Analysis

| Area | CLAUDE.md Says | Actual State | Severity |
|------|---------------|--------------|----------|
| Mail | Global CLAUDE.md: Zoho SMTP | Repo CLAUDE.md: Mailgun SMTP (deprecated text remains in some sections) | Medium |
| Hosting | Global: Azure Container Apps | Repo CLAUDE.md: mixed Azure + DigitalOcean refs (DO deprecated 2026-03-15) | Medium |
| Knowledge index | References `v18.0` and `/home/user/odoo/` paths | Repo is v19, paths are `/workspaces/odoo/` | High -- stale |
| Module count | CLAUDE.md: "69 verified" | `addons/ipai/`: 84 directories | Low -- outdated count |
| External docs | `docs/ai/external/` | 13 of 14 files are FETCH_FAILED stubs | High -- never populated |

## Missing Coverage

| Topic | Expected Location | Status |
|-------|-------------------|--------|
| Org-wide doc platform architecture | `docs/contracts/ORG_DOC_PLATFORM_CONTRACT.md` | Missing (this deliverable) |
| Metadata schema for docs | `ssot/docs/metadata_schema.yaml` | Missing (this deliverable) |
| Citation contract | `ssot/docs/citation_contract.yaml` | Missing (this deliverable) |
| Access policy for docs | `ssot/docs/access_policy_contract.yaml` | Missing (this deliverable) |
| Doc platform architecture (machine) | `ssot/docs/doc_platform_architecture.yaml` | Missing (this deliverable) |
| Onboarding guide | `docs/guides/ONBOARDING.md` | Missing |
| Disaster recovery runbook | `docs/runbooks/DR_RUNBOOK.md` | Only 1 file in runbooks/ |
| API documentation (OpenAPI) | `docs/api/` | Minimal |

---

*End of inventory. See `ssot/docs/source_inventory.yaml` for machine-readable version.*
