# Documentation Consolidation Audit

> **Date**: 2026-03-28
> **Scope**: InsightPulseAI monorepo (`Insightpulseai/`)
> **Status**: Audit complete — action plan ready

---

## 1. Executive Summary

The InsightPulseAI monorepo has **critical documentation sprawl** that undermines the SSOT operating model.

| Metric | Value | Severity |
|--------|-------|----------|
| Total markdown files | 37,653 (excl. worktrees) | — |
| Recursive `odoo/` nesting | 6 levels deep, 13 GB | **Critical** |
| Stale repo clones inside monorepo | 3 (`documentaion/`, `web-site/`, `docs-site/`) | **Critical** |
| Architecture docs (flat directory) | 153 files | **High** |
| "Target state" documents | 20+ with heavy overlap | **High** |
| Duplicate SSOT registries | `ssot/` vs `infra/ssot/` (both active) | **High** |
| Deprecated term references in active docs | 1,000+ Supabase, 224 Cloudflare DNS, 217 deprecated (Vercel/DO/Mailgun/MM), 7 `.net` | **High** |
| Azure AI Foundry → Microsoft Foundry | 301 occurrences across 164 files (70% stale) | **High** |
| GitHub Actions refs (deprecated CI/CD) | 119 occurrences across 42 files | **Medium** |
| Agent docs surface area | 1,062 files | **Medium** |
| Spec bundles | 52 directories (40 active, 9 placeholder, 7 with stale CI refs) | **Medium** |

### Top 5 Actions (by impact)

1. **Delete recursive `odoo/` nesting** — recover 12+ GB and eliminate 27K phantom duplicates
2. **Remove stale repo clones** — `documentaion/`, `web-site/`, `docs-site/`
3. **Merge `ssot/` and `infra/ssot/`** into one canonical SSOT root
4. **Consolidate 20+ target-state docs** into 5 canonical documents
5. **Restructure `docs/architecture/`** from 153-file flat directory into hierarchical topic folders

---

## 2. Documentation Inventory

### 2.1 Canonical Documentation Surfaces

| Surface | Path | File Count | Type | Status |
|---------|------|-----------|------|--------|
| Architecture docs | `docs/architecture/` | 153 | Architecture/ADR | **Active — needs hierarchy** |
| Governance docs | `docs/governance/` | 18 | Policy | Active |
| Contract docs | `docs/contracts/` | 19 | Cross-boundary contracts | Active |
| Runbook docs | `docs/runbooks/` | 19 | Operations | Active |
| Audit docs | `docs/audits/` | 13 | Evidence | Active |
| Evidence bundles | `docs/evidence/` | 31 | Proof packs | Active (append-only) |
| Skills docs | `docs/skills/` | 9 | Skill definitions | Active |
| Delivery docs | `docs/delivery/` | 3 | Release evidence | Active |
| Research docs | `docs/research/` | 3 | Investigation | Active |
| Spec bundles | `spec/` | 49 dirs | Feature specs | Mixed (active + stale) |
| SSOT registry (root) | `ssot/` | 175 files | Intended state | Active |
| SSOT registry (infra) | `infra/ssot/` | 202 files | Intended state | Active — **duplicates root** |
| Infra docs | `infra/docs/` | 14 | Infra architecture | Active |
| Agent docs | `agents/` | 1,062 | Personas/skills/knowledge | Active — **bloated** |
| Platform docs | `platform/` | 42 | Platform control-plane | Active |
| Template docs | `templates/` | 13 | Spec kit templates | Active |
| Claude rules | `.claude/rules/` | 11 | Agent behavior rules | Active |
| Top-level READMEs | Various | ~15 | Entry points | Mixed |

### 2.2 Non-Canonical / Stale Surfaces

| Surface | Path | Size | Status | Action |
|---------|------|------|--------|--------|
| Recursive odoo nesting | `odoo/odoo/odoo/...` (6 levels) | 13 GB | **Broken** — recursive git clone | **Delete** all `odoo/odoo/` and deeper |
| Stale `documentaion/` clone | `documentaion/` | 187 MB | **Stale** — personal fork (`jgtolentino/documentaion.git`) | **Delete** |
| Stale `web-site/` clone | `web-site/` | 1.4 GB | **Stale** — clone of `Insightpulseai/web.git` | **Delete** |
| MkDocs build artifact | `docs-site/` | 256 KB | **Stale** — no `.git`, build output | **Delete** |
| Archive | `archive/` | 3,430 files | Archive — intentionally frozen | **Keep** (no action) |
| `web/saas-landing/node_modules/` | Various | Large | Package manager output | `.gitignore` if not already |

---

## 3. Duplicate / Overlap Clusters

### Cluster 1: Target State Documents (CRITICAL)

**20+ documents** with heavy topical overlap. No single canonical target-state document.

| File | Topics | Keep/Merge/Archive |
|------|--------|--------------------|
| `docs/architecture/INSIGHTPULSEAI_TARGET_STATE_ARCHITECTURE.md` (33KB) | Full platform target state | **KEEP — promote to canonical** |
| `docs/architecture/PLATFORM_TARGET_STATE.md` (40KB) | Platform target state | **MERGE** into canonical |
| `docs/architecture/AZURE_NATIVE_TARGET_STATE.md` (11KB) | Azure-specific target state | **MERGE** into canonical |
| `docs/architecture/AZURE_ODOOSH_EQUIVALENT_TARGET_STATE.md` | Odoo.sh parity on Azure | **MERGE** or archive |
| `docs/architecture/AZURE_OPERATOR_VIEW_TARGET_STATE.md` | Operator view | **MERGE** into canonical |
| `docs/architecture/AZURE_OPERATOR_VIEW_ACTUAL_VS_TARGET.md` | Actual vs target | **MERGE** into canonical |
| `docs/architecture/UNIFIED_TARGET_ARCHITECTURE.md` (21KB) | Another unified target | **MERGE** into canonical |
| `docs/architecture/COPILOT_TARGET_STATE.md` (18KB) | Copilot/agent target | **KEEP — topic-specific** |
| `docs/architecture/COPILOT_AGENTS_TARGET_STATE_2026.md` | Agent target state | **MERGE** with above |
| `docs/architecture/ENTRA_TARGET_STATE_2026.md` | Identity target state | **KEEP — topic-specific** |
| `docs/architecture/ANALYTICS_TARGET_STATE.md` | Analytics target state | **KEEP — topic-specific** |
| `docs/architecture/DOCS_PLATFORM_TARGET_STATE.md` | Docs platform | **ARCHIVE** |
| `docs/architecture/PLANE_UNIFIED_DOCS_TARGET_STATE.md` | Plane docs | **ARCHIVE** |
| `docs/architecture/ROADMAP_TARGET_STATE.md` | Roadmap | **ARCHIVE** |
| `docs/architecture/DIVA_GOALS_TARGET_STATE.md` | DiVA/copilot goals | **MERGE** into copilot target |
| `docs/architecture/W9_STUDIO_WEBSITE_TARGET_STATE.md` | W9 Studio | **KEEP — project-specific** |
| `infra/ssot/azure/PLATFORM_TARGET_STATE.md` | Duplicate of docs/ version | **DELETE** — points to canonical |
| `docs/governance/DEV_TOOLING_TARGET_STATE.md` | Dev tooling | **KEEP — topic-specific** |
| `docs/governance/ENTERPRISE_TARGET_STATE_MATRIX.md` | Enterprise matrix | **MERGE** into canonical |
| `docs/governance/TEST_STRATEGY_TARGET_STATE.md` | Test strategy | **KEEP — topic-specific** |
| `docs/governance/VSCODE_TOOLING_TARGET_STATE.md` | VS Code tooling | **MERGE** into dev tooling |

**Target**: Consolidate from 20+ to **5 canonical target-state documents**:
1. `docs/architecture/target-state/PLATFORM.md` — master target state
2. `docs/architecture/target-state/IDENTITY.md` — Entra/identity
3. `docs/architecture/target-state/AGENTS.md` — copilot/agent
4. `docs/architecture/target-state/ANALYTICS.md` — data/analytics
5. `docs/architecture/target-state/DEV_TOOLING.md` — dev experience

### Cluster 2: SSOT Split (`ssot/` vs `infra/ssot/`)

Two active SSOT registries with overlapping domains:

| Domain | `ssot/` files | `infra/ssot/` files | Canonical? |
|--------|--------------|-------------------|------------|
| agents | 30 files | 11 files | **Split — must merge** |
| azure | 0 | 30+ files | `infra/ssot/azure/` |
| architecture | 0 | 8 files | `infra/ssot/architecture/` |
| identity | 2 files | 0 | `ssot/identity/` |
| governance | 3 files | 0 | `ssot/governance/` |
| odoo | 8 files | 0 | `ssot/odoo/` |
| agent-platform | 7 files | 0 | `ssot/agent-platform/` |

**Decision required**: Merge into one root. Recommendation: **`ssot/`** as canonical root, move `infra/ssot/` contents into `ssot/` with domain-based subdirectories.

### Cluster 3: Agent Factory / Agent Platform Docs

| File | Location | Topics |
|------|----------|--------|
| `docs/architecture/AGENT_PLATFORM.md` | docs | Agent platform overview |
| `docs/architecture/AGENT_FACTORY_V2_REDESIGN.md` | docs | Factory v2 |
| `docs/architecture/AGENT_FACTORY_HYBRID_MCP_GOVERNANCE.md` | docs | Factory MCP |
| `docs/architecture/AGENT_FACTORY_VS_*.md` (4 files) | docs | Competitive benchmarks |
| `docs/architecture/AGENT_PRODUCTION_REALITY.md` | docs | Production status |
| `docs/architecture/AGENT_SKILLS_KNOWLEDGE_BASE.md` | docs | Skills/KB |
| `docs/architecture/AGENT_DEPLOYMENTS_HARDENING.md` | docs | Hardening (431 bytes — stub) |
| `docs/architecture/AGENTOPS_DOCTRINE.md` | docs | AgentOps |
| `agent-platform/docs/architecture/` | agent-platform | Platform-specific |
| `agents/docs/architecture/` | agents | Agent-specific |

**Target**: Consolidate into `docs/architecture/agents/` with:
- `OVERVIEW.md` — single agent platform overview
- `PRODUCTION_STATUS.md` — current reality
- `BENCHMARKS.md` — all competitive analysis merged
- `SKILLS_AND_KNOWLEDGE.md` — skills/KB design

### Cluster 4: Odoo Architecture Docs

| File | Topics | Status |
|------|--------|--------|
| `docs/architecture/ODOO_RUNTIME.md` | Odoo runtime | Active |
| `docs/architecture/ODOO18_BASELINE_POLICY.md` | Odoo 18 baseline | Active |
| `docs/architecture/ODOO_RUNTIME_VERIFICATION_MATRIX.md` | Runtime verification | Active |
| `docs/architecture/ODOO_LOCAL_VS_AZURE_PROD.md` | Local vs prod | Active |
| `docs/architecture/ODOO_UPSTREAM_REFERENCE_SURFACES.md` | Upstream refs | Active |
| `docs/architecture/ODOO_UPSTREAM_ADOPTION_BACKLOG.md` | Upstream backlog | Active |
| `docs/architecture/ODOO_UPSTREAM_TO_AZDO_TRANSLATION.md` | AzDO translation | Active |
| `docs/architecture/ODOO_COPILOT_*.md` (3 files) | Copilot | Active |
| `docs/architecture/ODOO_ON_AZURE_PLANNING_GUIDE.md` | Planning | Active |
| `docs/architecture/INSIGHTPULSEAI_ODOO_ON_AZURE_TARGET_STATE.md` | Target state | Overlaps cluster 1 |
| `docs/architecture/ODOO_DOCS_BUILD_BENCHMARK.md` | Docs build | Active |
| `docs/architecture/OUR_ODOOSH_AZURE_VS_CLOUDPEPPER.md` | Competitive | Active |

**Target**: Move to `docs/architecture/odoo/` with hierarchy.

### Cluster 5: Tax/BIR Documents

| File | Size | Status |
|------|------|--------|
| `docs/architecture/TAX_BIR_BENCHMARK_MIGRATION_PLAN.md` | 11KB | Active |
| `docs/architecture/TAX_BIR_KNOWLEDGE_MAP.md` | 15KB | Active |
| `docs/architecture/TAX_BIR_CONSOLIDATION_REPORT.md` | 23KB | Active |
| `docs/architecture/TAX_BIR_BENCHMARK_TEST_CONSOLIDATION.md` | 9.6KB | Active |
| `docs/architecture/TAXPULSE_MIGRATION_PLAN.md` | 8.2KB | Active |
| `docs/architecture/TAXPULSE_SALVAGE_MAP.md` | 1.7KB | Active |

**Target**: Move to `docs/architecture/tax/` — 6 files, may merge migration plans.

### Cluster 6: W9 Studio Documents

| File | Size |
|------|------|
| `docs/architecture/W9_STUDIO_WEBSITE_TARGET_STATE.md` | 5.1KB |
| `docs/architecture/W9_STUDIO_WIX_AUDIT.md` | 15KB |
| `docs/architecture/W9_STUDIO_WIX_DESIGN_SYSTEM_AUDIT.md` | 4.6KB |
| `docs/architecture/WIX_GIT_INTEGRATION_RESEARCH.md` | 21KB |

**Target**: Move to `docs/architecture/w9-studio/` or `spec/w9-studio-*/`.

---

## 4. Canonical Terminology Table

| Canonical Term | Deprecated Variants | Count (files) | Replacement Rule |
|---------------|-------------------|---------------|-----------------|
| `insightpulseai.com` | `insightpulseai.net` | 7 occurrences | Find/replace all `.net` references |
| `pg-ipai-odoo` | `ipai-odoo-dev-pg` | 0 in markdown (clean) | Infrastructure-level only |
| Azure DevOps Pipelines | GitHub Actions (fully deprecated as CI/CD, 2026-03-21) | 80 refs / 42 files | All non-archive refs are cleanup targets; `.github/workflows/` itself is deprecated |
| Azure DNS | Cloudflare | **224 refs / 121 files** (170 Cloudflare, 54 Azure DNS) | **Resolve contradiction** — see Appendix C |
| Microsoft Foundry | Azure AI Foundry | **301 refs / 164 files** (~216 old, ~85 new) | Systematic rename deferred until SDK guidance |
| Pulser | Copilot (public-facing) | 100+ files mixed | Pulser = public brand, Copilot = internal only (per PULSER_NAMING_DOCTRINE.md) |
| `connector_mode` | `ingestion_ownership_model` | Templates (updated this session) | Clean — no stale refs remain |
| `platform_managed.runtime_bound` | `platform_managed` (bare) | Templates (updated this session) | Clean — no stale refs remain |
| Azure Container Apps | Vercel | ~75 refs / 80+ files | Remove from non-archive deployment docs |
| Azure Container Apps | DigitalOcean | ~45 refs / 80+ files | Remove from non-archive deployment docs |
| Zoho SMTP | Mailgun | ~40 refs / 80+ files | Remove from non-archive docs |
| Slack | Mattermost | ~50 refs / 80+ files | Remove from non-archive docs |
| `odoo` (repo name) | `odoo-ce` | 2 refs (clean) | Minimal — rename was thorough |
| Azure-native services | Supabase (fully deprecated 2026-03-26, including self-hosted VM) | **1,000+ refs / 200+ files** | Bulk cleanup — exclude archive only; self-host migration docs are also historical |

### DNS Authority Contradiction

**`~/.claude/CLAUDE.md`** says: `DNS: Cloudflare (delegated from Spacesquare)`
**`./CLAUDE.md`** says: `DNS: Azure DNS (authoritative, delegated from Squarespace)`

These contradict. One must be corrected. Check: which is the actual authoritative DNS?

---

## 5. Target-State Information Architecture

### 5.1 Org-Wide Structure

```
docs/
├── architecture/
│   ├── OVERVIEW.md                    # Platform architecture overview (single)
│   ├── target-state/                  # All target-state docs (consolidated)
│   │   ├── PLATFORM.md
│   │   ├── IDENTITY.md
│   │   ├── AGENTS.md
│   │   ├── ANALYTICS.md
│   │   └── DEV_TOOLING.md
│   ├── agents/                        # Agent/copilot architecture
│   │   ├── OVERVIEW.md
│   │   ├── PRODUCTION_STATUS.md
│   │   ├── BENCHMARKS.md
│   │   └── SKILLS_AND_KNOWLEDGE.md
│   ├── azure/                         # Azure platform architecture
│   │   ├── COMPUTE.md
│   │   ├── IDENTITY.md
│   │   ├── NETWORKING.md
│   │   ├── DATA.md
│   │   └── DECOMMISSION_MATRIX.md
│   ├── odoo/                          # Odoo-specific architecture
│   │   ├── RUNTIME.md
│   │   ├── BASELINE_POLICY.md
│   │   ├── UPSTREAM_ADOPTION.md
│   │   └── COPILOT.md
│   ├── data/                          # Data/analytics architecture
│   │   ├── MEDALLION.md
│   │   ├── DATABRICKS.md
│   │   ├── LAKEHOUSE.md
│   │   └── FABRIC.md
│   ├── connectors/                    # Connector onboarding
│   │   ├── STANDARD.md
│   │   └── MODES.md
│   ├── tax/                           # Tax/BIR architecture
│   ├── integration/                   # Integration patterns
│   ├── security/                      # Security architecture
│   └── adr/                           # Architecture Decision Records
├── governance/                        # Policies (keep as-is, well-structured)
├── contracts/                         # Cross-boundary contracts (keep as-is)
├── runbooks/                          # Operations (keep as-is)
├── audits/                            # Audit evidence (keep as-is)
├── evidence/                          # Proof packs (append-only, keep as-is)
├── skills/                            # Skill definitions (keep as-is)
└── delivery/                          # Release evidence (keep as-is)

ssot/                                  # MERGED canonical SSOT root
├── agents/                            # Merged from ssot/ + infra/ssot/agents/
├── azure/                             # Moved from infra/ssot/azure/
├── architecture/                      # Moved from infra/ssot/architecture/
├── auth/                              # Moved from infra/ssot/auth/
├── odoo/                              # Keep from ssot/odoo/
├── identity/                          # Keep from ssot/identity/
├── governance/                        # Merge from both roots
├── agent-platform/                    # Keep from ssot/agent-platform/
├── ai/                                # Moved from infra/ssot/ai/
├── automations/                       # Moved from infra/ssot/automations/
└── github/                            # Moved from infra/ssot/github/

spec/                                  # Spec bundles (keep structure)
templates/                             # Spec kit templates (keep structure)
```

### 5.2 Doc Type Placement Rules

| Doc Type | Canonical Path | Rule |
|----------|---------------|------|
| Architecture overview | `docs/architecture/<topic>/OVERVIEW.md` | One per topic |
| Target state | `docs/architecture/target-state/<DOMAIN>.md` | Max 5 canonical docs |
| ADR | `docs/architecture/adr/ADR_<NUMBER>_<TITLE>.md` | Numbered, append-only |
| Competitive benchmark | `docs/architecture/<topic>/BENCHMARKS.md` | One per topic, not standalone |
| Governance policy | `docs/governance/<POLICY_NAME>.md` | Flat — keep current structure |
| Cross-boundary contract | `docs/contracts/<CONTRACT_NAME>.md` | One per boundary |
| Runbook | `docs/runbooks/<RUNBOOK_NAME>.md` | Flat — keep current structure |
| Audit | `docs/audits/<audit-name>/<timestamp>/` | Timestamped bundles |
| Evidence | `docs/evidence/<YYYYMMDD-HHMM>/<scope>/` | Timestamped bundles |
| Spec bundle | `spec/<feature-slug>/{constitution,prd,plan,tasks}.md` | 4-file standard |
| SSOT registry | `ssot/<domain>/<file>.yaml` | Machine-readable intended state |
| Skill definition | `docs/skills/<skill-name>.md` | One per skill |

---

## 6. Rewrite / Merge / Archive Plan

### Phase 1: Critical Cleanup (immediate)

| # | Action | Target | Impact |
|---|--------|--------|--------|
| 1.1 | **Delete `odoo/odoo/`** and all deeper nesting | Recover 12+ GB, eliminate 27K phantom files | Critical |
| 1.2 | **Delete `documentaion/`** | Remove stale personal fork | Critical |
| 1.3 | **Delete `web-site/`** | Remove stale org web clone | Critical |
| 1.4 | **Delete `docs-site/`** | Remove MkDocs build artifact | Critical |
| 1.5 | Add `.gitignore` entries for recursive clones | Prevent recurrence | Critical |

### Phase 2: SSOT Consolidation (week 1)

| # | Action | From → To |
|---|--------|-----------|
| 2.1 | Merge `infra/ssot/agents/` → `ssot/agents/` | Deduplicate agent registries |
| 2.2 | Move `infra/ssot/azure/` → `ssot/azure/` | Single SSOT root |
| 2.3 | Move `infra/ssot/architecture/` → `ssot/architecture/` | Single SSOT root |
| 2.4 | Move `infra/ssot/auth/` → `ssot/auth/` | Single SSOT root |
| 2.5 | Move `infra/ssot/ai/` → `ssot/ai/` | Single SSOT root |
| 2.6 | Move `infra/ssot/automations/` → `ssot/automations/` | Single SSOT root |
| 2.7 | Update all references from `infra/ssot/` → `ssot/` | Repo-wide |
| 2.8 | Redirect `infra/ssot/README.md` to `ssot/README.md` | Keep pointer until CI updated |

### Phase 3: Architecture Hierarchy (week 2)

| # | Action | Files |
|---|--------|-------|
| 3.1 | Create `docs/architecture/target-state/` | Consolidate 20+ → 5 files |
| 3.2 | Create `docs/architecture/agents/` | Move 10+ agent docs |
| 3.3 | Create `docs/architecture/azure/` | Move 12+ Azure docs |
| 3.4 | Create `docs/architecture/odoo/` | Move 12+ Odoo docs |
| 3.5 | Create `docs/architecture/data/` | Move 5+ data/analytics docs |
| 3.6 | Create `docs/architecture/tax/` | Move 6 tax/BIR docs |
| 3.7 | Create `docs/architecture/adr/` | Move ADR docs |
| 3.8 | Create `docs/architecture/connectors/` | Move 2 connector docs |
| 3.9 | Create `docs/architecture/integration/` | Move integration docs |
| 3.10 | Create `docs/architecture/security/` | Move security docs |
| 3.11 | Archive stubs (< 500 bytes with no substance) | 3 files identified |

### Phase 4: Terminology Cleanup (week 2-3)

| # | Action | Scope |
|---|--------|-------|
| 4.1 | Resolve DNS authority contradiction | `~/.claude/CLAUDE.md` vs `./CLAUDE.md` |
| 4.2 | Replace 84 Supabase references | Active docs only (not archive/evidence) |
| 4.3 | Replace DigitalOcean references | Active docs only |
| 4.4 | Replace Vercel references | Active docs only |
| 4.5 | Replace `insightpulseai.net` | 3 files |
| 4.6 | Replace `ipai-odoo-dev-pg` → `pg-ipai-odoo` | All active docs |
| 4.7 | Replace bare `platform_managed` | Templates/connectors (done this session) |

### Phase 5: Spec Bundle Cleanup (week 3)

| # | Action | Scope |
|---|--------|-------|
| 5.1 | Audit 49 spec bundles for completeness | All must have 4 files |
| 5.2 | Archive stale/placeholder specs | Specs with no plan or tasks |
| 5.3 | Flag specs referencing deprecated items | Supabase, Vercel, etc. |

---

## 7. Governance / CI Recommendations

### 7.1 Doc Lint CI Pipeline

Add an Azure DevOps pipeline or pre-commit hook that enforces:

- [ ] No markdown files outside canonical paths (see §5.2)
- [ ] No bare `platform_managed` in connector specs (must be dot-qualified)
- [ ] No deprecated terms in non-archive docs: `insightpulseai.net`, `Mattermost`, `DigitalOcean`, `Vercel`, `Mailgun`
- [ ] No files in `infra/ssot/` after SSOT merge (redirect check)
- [ ] No new target-state documents outside `docs/architecture/target-state/`
- [ ] Architecture docs must be in a topic subdirectory (no new files in flat `docs/architecture/`)

### 7.2 Doc Ownership

| Path | Owner | Review Required |
|------|-------|-----------------|
| `docs/architecture/` | Platform architect | Any new file |
| `docs/governance/` | Governance owner | Policy changes |
| `docs/contracts/` | Cross-boundary contract parties | Both sides |
| `docs/runbooks/` | Ops team | Incident-driven |
| `ssot/` | SSOT domain owner | Schema/registry changes |
| `spec/` | Feature owner | Spec kit review skill |
| `templates/` | Platform architect | Template changes |

### 7.3 Stale Doc Detection

Quarterly CI check:
- Flag docs not modified in 90 days
- Flag docs referencing non-existent files or URLs
- Flag docs with deprecated terminology
- Flag SSOT files that contradict live Azure Resource Graph

---

## 8. Phased Migration Roadmap

```
Week 0 (now):   Phase 1 — Delete recursive nesting + stale clones
Week 1:         Phase 2 — SSOT consolidation (ssot/ + infra/ssot/ merge)
Week 2:         Phase 3 — Architecture hierarchy (topic subdirectories)
Week 2-3:       Phase 4 — Terminology cleanup (84 Supabase refs, etc.)
Week 3:         Phase 5 — Spec bundle audit + archival
Week 4:         Phase 6 — CI lint pipeline for doc governance
Week 5+:        Phase 7 — Content merges (target-state consolidation)
```

**Invariant**: No content is deleted during merges — only moved, consolidated, or archived. Archive path: `archive/docs/<YYYYMMDD>/`.

---

## Appendix A: Architecture Doc Classification (153 files)

### Proposed Topic Assignment

| Topic Folder | Files to Move | Count |
|-------------|--------------|-------|
| `target-state/` | PLATFORM_TARGET_STATE, AZURE_NATIVE_TARGET_STATE, UNIFIED_TARGET_ARCHITECTURE, INSIGHTPULSEAI_TARGET_STATE_ARCHITECTURE, AZURE_ODOOSH_EQUIVALENT_TARGET_STATE, AZURE_OPERATOR_VIEW_TARGET_STATE, REPO_ACTUAL_VS_TARGET_STATE, + merges | 8→5 |
| `agents/` | AGENT_PLATFORM, AGENT_FACTORY_*, AGENT_PRODUCTION_REALITY, AGENT_SKILLS_KNOWLEDGE_BASE, AGENTOPS_DOCTRINE, COPILOT_TARGET_STATE, COPILOT_AGENTS_TARGET_STATE_2026, COPILOT_AGENT_GAP_ANALYSIS, DIVA_GOALS_TARGET_STATE, ASSISTANT_SURFACES | 12 |
| `azure/` | AZURE_BILL_OF_MATERIALS, AZURE_DECOMMISSION_MATRIX, AZURE_DEVOPS_OPERATING_MODEL, AZURE_OPERATOR_VIEW_ACTUAL_VS_TARGET, AZURE_PLATFORM_OVERVIEW, AZURE_SERVICE_MAPPING, AZURE_WORKSPACE_TARGET_GROUPING, RUNTIME_CONTRACT_AZURE_ODOO | 8 |
| `odoo/` | ODOO_RUNTIME, ODOO19_BASELINE_POLICY, ODOO_RUNTIME_VERIFICATION_MATRIX, ODOO_LOCAL_VS_AZURE_PROD, ODOO_UPSTREAM_*, ODOO_COPILOT_*, ODOO_ON_AZURE_*, EXPENSE_LIQUIDATION_INSTALL_MATRIX, OUR_ODOOSH_AZURE_VS_CLOUDPEPPER | 12 |
| `data/` | MEDALLION_ARCH, ADLS_ETL_REVERSE_ETL_ARCHITECTURE, ANALYTICS_TARGET_STATE, enterprise_data_platform, SCHEMA_GOVERNANCE_REVIEW, DATABRICKS_BUNDLES_BASELINE, SEED_DATA_INVENTORY, FINANCE_DOMAIN_TARGET_STATE | 8 |
| `tax/` | TAX_BIR_*, TAXPULSE_* | 6 |
| `connectors/` | CONNECTOR_ONBOARDING_STANDARD, CONNECTOR_ONBOARDING_MODES | 2 |
| `identity/` | ENTRA_TARGET_STATE_2026, ENTRA_GOVERNANCE_BASELINE, identity_and_secrets, ODOO_19_AZURE_OAUTH_REFERENCE | 4 |
| `integration/` | CLOUD_INTEGRATION_STATUS, A2A_INTEROP, N8N_*, FAL_INTEGRATION_STRATEGY, DEVTOOLS_MCP_INTEGRATION | 6 |
| `security/` | runtime_security, AI_RUNTIME_AUTHORITY, RETRIEVAL_AND_MEMORY_POLICY | 3 |
| `adr/` | ADR_ERP_PLATFORM_ROLE_SPLIT, ADR_VSCODE_* | 3 |
| `operations/` | reliability_operating_model, observability_model, devsecops_operating_model, quality_engineering_model, release_management_model, platform_delivery_contract, idea-to-release-pipeline | 7 |
| `governance/` | REPO_BOUNDARIES, REPO_OWNERSHIP_DOCTRINE, GITHUB_ORG_TOPOLOGY, GITHUB_*, FILE_TAXONOMY_AND_NAMING_POLICY, ORG_TARGET_STATE_2026, ORG_REFACTOR_REVIEW, ADO_GITHUB_AUTHORITY_MAP_2026 | 8 |
| `saas/` | WHOLESALE_SAAS_ERP_ON_AZURE, saas_billing_metering, TENANCY_MODEL, MULTITENANCY_MODEL, OFFERING_ARTIFACT_MODEL, DOMAIN_INTELLIGENCE_SHELLS | 6 |
| `marketing/` | MARKETING_ASSISTANT_DOCTRINE, marketing_analytics_reference_model, marketing-agency-*, CREATIVE_PROVIDER_POLICY | 5 |
| `w9-studio/` | W9_STUDIO_*, WIX_GIT_INTEGRATION_RESEARCH | 4 |
| `docs-platform/` | DOCS_PLATFORM_ARCHITECTURE, DOCS_PLATFORM_TARGET_STATE, PLANE_UNIFIED_DOCS_TARGET_STATE, ODOO_DOCS_BUILD_BENCHMARK | 4 |
| `ai/` | AI_CONSOLIDATION_FOUNDRY, AI_FOUNDRY_STAGE3_CHECKLIST, AI_OPERATING_MODEL, foundry_*, document_intelligence_processing | 6 |
| Remaining (misc) | reference-benchmarks, diagram-conventions, domain-workbench-map, target-capability-map, plane-boundaries, GO_LIVE_*, ROADMAP_*, microsoft_collection_alignment, CONVERGENCE_REPORT, SAMPLE_ADOPTION_POLICY, etc. | ~20 |
| Stubs (< 500 bytes) | AGENT_DEPLOYMENTS_HARDENING (431B), EVAL_ENGINE_HARDENING (448B), TASK_ROUTER_HARDENING (522B) | 3 → archive |

### Files Remaining at `docs/architecture/` Root

After topic moves, only cross-cutting docs should remain at root:
- `GO_LIVE_CHECKLIST.md`
- `GO_LIVE_MATRIX.md`
- `APPROVED_MICROSOFT_SAMPLES.md`
- `SAMPLE_ADOPTION_POLICY.md`
- `CONVERGENCE_REPORT.md`
- `reference-benchmarks.md`
- `target-capability-map.md`
- `diagram-conventions.md`

---

## Appendix B: Stale Repo Clones (Delete Immediately)

| Path | Origin | Size | Action |
|------|--------|------|--------|
| `documentaion/` | `jgtolentino/documentaion.git` (personal) | 187 MB | `rm -rf documentaion/` |
| `web-site/` | `Insightpulseai/web.git` (org clone) | 1.4 GB | `rm -rf web-site/` |
| `docs-site/` | No git — MkDocs build artifact | 256 KB | `rm -rf docs-site/` |
| `odoo/odoo/` (and deeper) | Recursive self-clone | 12+ GB | `rm -rf odoo/odoo/` |

**Total recoverable**: ~14.8 GB

---

## Appendix C: DNS Authority Resolution

The two CLAUDE.md files disagree on DNS:

| File | DNS Statement |
|------|---------------|
| `~/.claude/CLAUDE.md` | Cloudflare (delegated from Spacesquare) |
| `./CLAUDE.md` | Azure DNS (authoritative, delegated from Squarespace) |

**Also**: `.claude/rules/infrastructure.md` says "Cloudflare (authoritative DNS-only mode)"

This must be resolved. If Azure DNS is now authoritative, update `~/.claude/CLAUDE.md` and `.claude/rules/infrastructure.md`. If Cloudflare is still authoritative, update `./CLAUDE.md`.

---

## Appendix D: Spec Bundle Inventory (52 bundles)

### Status Summary

| Status | Count | Notes |
|--------|-------|-------|
| Active | 40 | Full 4-file spec kits |
| Draft/Proposed | 2 | `gmail-inbox-addon`, `unified-api-gateway` |
| Ready | 1 | `ipai-odoo-copilot` |
| Placeholder | 9 | Minimal files — no constitution |

### Placeholder Specs (archive or complete)

| Spec | Files | Action |
|------|-------|--------|
| `document-intelligence` | No core files | Archive or complete |
| `gmail-mail-plugin` | prd only | Merge into `gmail-inbox-addon` |
| `landing-ai` | Minimal | Archive |
| `microsoft-marketplace-go-to-market` | prd only | Complete or archive |
| `odoo-sh-equivalent-staging` | prd only | Merge into `odoo-sh-azure-equivalent` |
| `ugc-mediaops-kit` | prd only | Archive |

### Specs with Deprecated CI/CD References

7 spec bundles still reference GitHub Actions (deprecated 2026-03-21):
- `agent-deployments-hardening`
- `agent-platform`
- `ipai-odoo-copilot-azure`
- `odoo-copilot-agent-framework`
- `odoo-copilot-azure-runtime`
- `odoo-ios-mobile`
- `release-gates-hardening`

### Supabase Specs (all historical — Supabase fully deprecated)

Supabase is fully deprecated (2026-03-26) including the self-hosted VM. All 3 specs are historical:
- `adls-etl-reverse-etl` — data flow documentation (Supabase lane removed)
- `azure-selfhost-migration` — **archive** (migration complete, then deprecated)
- `supabase-self-host-cutover` — **archive** (cutover done, then fully deprecated)

---

## Appendix E: Terminology Remediation Priority Matrix

| Terminology | Severity | Files Affected | Effort | Recommendation |
|-------------|----------|---------------|--------|----------------|
| Azure AI Foundry → Microsoft Foundry | Critical | 164 | High | Systematic rename (deferred until SDK guidance) |
| Cloudflare DNS → Azure DNS | Critical | 121 | Medium | Update TARGET_STATE docs + remove `infra/cloudflare/` |
| Supabase → Azure-native (fully deprecated incl. self-hosted) | High | 200+ | High | Audit non-archive files; bulk replace; archive self-host migration specs |
| Vercel/DO/Mailgun/Mattermost | High | 80+ | Medium | Filter to non-archive; update deployment/ops docs |
| Pulser vs Copilot naming | High | 100+ | Medium | Align with PULSER_NAMING_DOCTRINE.md |
| GitHub Actions → Azure DevOps (fully deprecated) | High | 42 | Medium | All non-archive refs are cleanup targets; `.github/workflows/` deprecated |
| InsightPulse capitalization | Low | 6,000+ | Very high | Establish single form; defer (lowest ROI) |

---

## Appendix F: Documentation Surface Counts

| Surface | Files | Lines (est.) |
|---------|-------|-------------|
| `docs/` total | 347 | ~50K |
| `docs/architecture/` | 163 | ~25K |
| `docs/governance/` | 18 | ~3K |
| `docs/contracts/` | 19 | ~4K |
| `docs/runbooks/` | 19 | ~3K |
| `docs/audits/` | 13 | ~2K |
| `docs/evidence/` | 31 | ~5K |
| `ssot/` (root) | 158 | ~15K (YAML) |
| `infra/ssot/` | 202 | ~20K (YAML) |
| `infra/docs/` | 14 | ~2K |
| `spec/` | 52 dirs / ~200 files | ~20K |
| `.claude/rules/` | 11 | ~2K |
| `agents/` docs | 1,062 | ~100K |
| `platform/` docs | 42 | ~5K |
| `templates/` | 13 | ~2K |
| **Total canonical docs** | **~2,100** | **~258K lines** |
