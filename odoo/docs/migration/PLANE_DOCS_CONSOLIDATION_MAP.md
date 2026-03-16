# Plane Docs Consolidation Map

> Spec bundle: `spec/plane-unified-docs/`
> Machine-readable SSOT: `ssot/docs/plane-docs-canonical-map.yaml`
> Status: Active
> Created: 2026-03-13

---

## Purpose

This document maps every documentation source in the InsightPulseAI repo to its target surface under the three-layer Plane unified docs architecture. It governs what migrates, what stays, what gets archived, and what gets deleted.

---

## Consolidation Rules

### Stays in Repo (L1: Machine-Readable SSOT)

- Machine-readable config: YAML, JSON, DBML, SQL schemas
- Code-adjacent docs: `CLAUDE.md`, module `__manifest__.py`, inline code docs
- CI-enforced contracts: workflows, schemas, lock files
- Evidence bundles: `docs/evidence/` (CI-generated, append-only)
- Agent configs: `.claude/`, `.claude/rules/`, `.claude/commands/`
- Spec bundle constitutions: `spec/*/constitution.md` (CI-enforced invariants)
- Docker/IaC: `docker/`, `deploy/`, `infra/`

### Migrates to Plane Wiki (L2: Human-Readable)

- Architecture overviews and strategy documents
- PRDs and delivery plans (human narrative; spec bundle link preserved)
- Runbooks and operational procedures
- Integration specs (human-readable portions)
- Decision records (ADRs)
- Onboarding guides
- Module catalogs and decision rubrics
- Governance and process docs

### Archives Then Deletes

- Duplicate content (same doc in multiple locations)
- Stale content referencing deprecated systems
- Draft documents with no review in 180+ days
- Legacy migration artifacts from completed migrations

---

## Consolidation Table

### docs/architecture/*.md

| Current Location | Content Type | Target Surface | Migration Action | Owner | Priority | Status |
|------------------|-------------|----------------|-----------------|-------|----------|--------|
| `docs/architecture/INSIGHTPULSEAI_TECHNICAL_ARCHITECTURE.md` | Architecture overview | Plane Wiki | Migrate | Platform Architect | P0 | Planned |
| `docs/architecture/IPAI_TARGET_ARCHITECTURE.md` | Architecture overview | Plane Wiki | Migrate | Platform Architect | P0 | Planned |
| `docs/architecture/AUTH_ARCHITECTURE.md` | Architecture overview | Plane Wiki | Migrate | Platform Architect | P0 | Planned |
| `docs/architecture/AUTH_MODEL.md` | Architecture overview | Plane Wiki | Migrate | Platform Architect | P1 | Planned |
| `docs/architecture/DATABRICKS_ARCHITECTURE.md` | Architecture overview | Plane Wiki | Migrate | Data Lead | P0 | Planned |
| `docs/architecture/GOLDEN_PATH.md` | Runbook | Plane Wiki | Migrate | Ops Lead | P0 | Planned |
| `docs/architecture/DEPLOY_TARGET_MATRIX.md` | Runbook | Plane Wiki | Migrate | Infrastructure Lead | P0 | Planned |
| `docs/architecture/INTEGRATIONS_SURFACE.md` | Integration spec | Plane Wiki | Migrate | Integration Owner | P1 | Planned |
| `docs/architecture/N8N_AUTOMATION_CONTRACT.md` | Integration spec | Plane Wiki | Migrate | Integration Owner | P1 | Planned |
| `docs/architecture/SLACK_AGENT_CONTRACT.md` | Integration spec | Plane Wiki | Migrate | Integration Owner | P1 | Planned |
| `docs/architecture/SUPERSET.md` | Architecture overview | Plane Wiki | Migrate | Data Lead | P1 | Planned |
| `docs/architecture/ODOO_EDITIONS_SSOT.md` | Policy doc | Plane Wiki | Migrate | Odoo Lead | P1 | Planned |
| `docs/architecture/EE_PARITY_MATRIX.md` | Policy doc | Plane Wiki | Migrate | Odoo Lead | P1 | Planned |
| `docs/architecture/EE_PARITY_POLICY.md` | Policy doc | Plane Wiki | Migrate (merge with matrix) | Odoo Lead | P1 | Planned |
| `docs/architecture/MODULE_DECISION_RUBRIC.md` | Policy doc | Plane Wiki | Migrate | Odoo Lead | P1 | Planned |
| `docs/architecture/ECOSYSTEM_GUIDE.md` | Onboarding guide | Plane Wiki | Migrate | Team Lead | P2 | Planned |
| `docs/architecture/GOVERNANCE_BRANCH_PROTECTION.md` | Governance doc | Plane Wiki | Migrate | Governance Lead | P2 | Planned |
| `docs/architecture/GOVERNANCE_HARDENING_2026-03-05.md` | Governance doc | Plane Wiki | Migrate | Governance Lead | P2 | Planned |
| `docs/architecture/PLANE_APP_CONNECTOR.md` | Integration spec | Plane Wiki | Migrate | Integration Owner | P1 | Planned |
| `docs/architecture/PLANE_MARKETPLACE_INTEGRATIONS.md` | Integration spec | Plane Wiki | Migrate | Integration Owner | P2 | Planned |
| `docs/architecture/PLANE_UNIFIED_DOCS_TARGET_STATE.md` | Architecture overview | Repo SSOT | Stay (this spec bundle) | Platform Architect | -- | Active |
| `docs/architecture/schema.dbml` | Schema definition | Repo SSOT | Stay | Data Lead | -- | Active |
| `docs/architecture/schema.prisma` | Schema definition | Repo SSOT | Stay | Data Lead | -- | Active |
| `docs/architecture/INDEX.json` | Machine-readable index | Repo SSOT | Stay | Agent | -- | Active |
| `docs/architecture/REPO_SNAPSHOT.json` | Machine-readable snapshot | Repo SSOT | Stay | Agent | -- | Active |
| `docs/architecture/runtime_identifiers.json` | Generated artifact | Repo SSOT | Stay (generated) | Agent | -- | Active |
| `docs/architecture/adr/` | Decision records | Plane Wiki | Migrate | Platform Architect | P2 | Planned |
| `docs/architecture/CANONICAL_ENTITY_MAP.yaml` | Machine-readable map | Repo SSOT | Stay | Agent | -- | Active |
| `docs/architecture/doc-placement-matrix.yaml` | Machine-readable map | Repo SSOT | Stay | Agent | -- | Active |
| `docs/architecture/PLACEMENT_AUDIT.yaml` | Machine-readable audit | Repo SSOT | Stay | Agent | -- | Active |
| `docs/architecture/ODOO_CANONICAL_SCHEMA.dbml` | Schema definition | Repo SSOT | Stay | Data Lead | -- | Active |
| `docs/architecture/ODOO_ERD.mmd` | Schema definition | Repo SSOT | Stay | Data Lead | -- | Active |
| `docs/architecture/REPO_TREE.generated.md` | Generated artifact | Repo SSOT | Stay (generated) | Agent | -- | Active |
| `docs/architecture/SECRETS_POLICY.md` | Policy doc | Repo SSOT | Stay (CI-enforced) | Governance Lead | -- | Active |
| `docs/architecture/MONOREPO_CONTRACT.md` | Contract | Repo SSOT | Stay (CI-enforced) | Platform Architect | -- | Active |
| `docs/architecture/DNS_AUTHORITY_CONTRACT.md` | Contract | Repo SSOT | Stay (CI-enforced) | Infrastructure Lead | -- | Active |
| `docs/architecture/SOW_BOUNDARY.md` | Contract | Repo SSOT | Stay (CI-enforced) | Governance Lead | -- | Active |

### docs/ai/*.md

| Current Location | Content Type | Target Surface | Migration Action | Owner | Priority | Status |
|------------------|-------------|----------------|-----------------|-------|----------|--------|
| `docs/ai/ARCHITECTURE.md` | Architecture overview | Plane Wiki | Migrate (if not duplicate of main arch doc) | AI Lead | P1 | Planned |
| `docs/ai/REPO_STRUCTURE.md` | Reference doc | Repo SSOT | Stay (code-adjacent) | Agent | -- | Active |
| `docs/ai/IPAI_MODULES.md` | Reference doc | Repo SSOT | Stay (code-adjacent) | Agent | -- | Active |
| `docs/ai/EE_PARITY.md` | Policy doc | Plane Wiki | Migrate (merge with main parity doc) | Odoo Lead | P1 | Planned |
| `docs/ai/CI_WORKFLOWS.md` | Reference doc | Repo SSOT | Stay (CI-adjacent) | Agent | -- | Active |
| `docs/ai/MCP_SYSTEM.md` | Reference doc | Repo SSOT | Stay (code-adjacent) | Agent | -- | Active |
| `docs/ai/INTEGRATIONS.md` | Reference doc | Plane Wiki | Migrate (if human-oriented) | Integration Owner | P2 | Planned |
| `docs/ai/BIR_COMPLIANCE.md` | Compliance doc | Plane Wiki | Migrate | Compliance Lead | P1 | Planned |
| `docs/ai/OCA_WORKFLOW.md` | Workflow doc | Repo SSOT | Stay (code-adjacent) | Agent | -- | Active |
| `docs/ai/TESTING.md` | Reference doc | Repo SSOT | Stay (code-adjacent) | Agent | -- | Active |
| `docs/ai/DOCKER.md` | Reference doc | Repo SSOT | Stay (code-adjacent) | Agent | -- | Active |
| `docs/ai/TROUBLESHOOTING.md` | Runbook | Plane Wiki | Migrate | Ops Lead | P1 | Planned |

### docs/evidence/

| Current Location | Content Type | Target Surface | Migration Action | Owner | Priority | Status |
|------------------|-------------|----------------|-----------------|-------|----------|--------|
| `docs/evidence/*/` | CI-generated evidence | Repo SSOT | Stay (CI-generated, append-only) | Agent | -- | Active |

### docs/contracts/

| Current Location | Content Type | Target Surface | Migration Action | Owner | Priority | Status |
|------------------|-------------|----------------|-----------------|-------|----------|--------|
| `docs/contracts/*.md` | CI-enforced contracts | Repo SSOT | Stay (CI-enforced) | Contract owners | -- | Active |

### docs/integrations/

| Current Location | Content Type | Target Surface | Migration Action | Owner | Priority | Status |
|------------------|-------------|----------------|-----------------|-------|----------|--------|
| `docs/integrations/*.md` | Integration specs | Plane Wiki | Migrate (human-readable portions) | Integration Owner | P1 | Planned |

### docs/guides/

| Current Location | Content Type | Target Surface | Migration Action | Owner | Priority | Status |
|------------------|-------------|----------------|-----------------|-------|----------|--------|
| `docs/guides/*.md` | Onboarding/how-to guides | Plane Wiki | Migrate | Team Lead | P2 | Planned |

### spec/*/

| Current Location | Content Type | Target Surface | Migration Action | Owner | Priority | Status |
|------------------|-------------|----------------|-----------------|-------|----------|--------|
| `spec/*/constitution.md` | CI-enforced rules | Repo SSOT | Stay | Spec owner | -- | Active |
| `spec/*/prd.md` | Product requirements | Both Linked | PRD summary -> Plane Wiki; full PRD stays in repo | Product Owner | P1 | Planned |
| `spec/*/plan.md` | Implementation plan | Both Linked | Plan summary -> Plane Wiki; full plan stays in repo | Delivery Lead | P1 | Planned |
| `spec/*/tasks.md` | Task checklist | Plane Execution | Migrate tasks to Plane work items; keep repo file as reference | Agent | P1 | Planned |

### ssot/**/*.yaml

| Current Location | Content Type | Target Surface | Migration Action | Owner | Priority | Status |
|------------------|-------------|----------------|-----------------|-------|----------|--------|
| `ssot/**/*.yaml` | Machine-readable configs | Repo SSOT | Stay | Domain owners | -- | Active |
| `ssot/docs/plane-docs-canonical-map.yaml` | Documentation map | Repo SSOT | Stay (this is the SSOT for doc ownership) | Platform Architect | -- | Active |

### .claude/

| Current Location | Content Type | Target Surface | Migration Action | Owner | Priority | Status |
|------------------|-------------|----------------|-----------------|-------|----------|--------|
| `.claude/prompts/` | Agent prompts | Repo SSOT | Stay (code-adjacent) | Agent | -- | Active |
| `.claude/rules/` | Agent rules | Repo SSOT | Stay (code-adjacent) | Agent | -- | Active |
| `.claude/commands/` | Agent commands | Repo SSOT | Stay (code-adjacent) | Agent | -- | Active |
| `.claude/settings.json` | Agent config | Repo SSOT | Stay | Agent | -- | Active |

### CLAUDE.md Files

| Current Location | Content Type | Target Surface | Migration Action | Owner | Priority | Status |
|------------------|-------------|----------------|-----------------|-------|----------|--------|
| `CLAUDE.md` (root) | Agent operating contract | Repo SSOT | Stay (code-adjacent, CI-enforced) | Platform Architect | -- | Active |
| `**/CLAUDE.md` (nested) | Agent config refinements | Repo SSOT | Stay (code-adjacent) | Module owners | -- | Active |

### docs/plane/

| Current Location | Content Type | Target Surface | Migration Action | Owner | Priority | Status |
|------------------|-------------|----------------|-----------------|-------|----------|--------|
| `docs/plane/PLANE_COMMERCIAL_TARGET_STATE.md` | Strategy doc | Plane Wiki | Migrate | Product Owner | P1 | Planned |
| `docs/plane/PLANE_PROD_AUTH_EMAIL_INTEGRATIONS.md` | Integration spec | Plane Wiki | Migrate | Infrastructure Lead | P1 | Planned |
| `docs/plane/PLANE_SEED_AND_ROADMAP_MODEL.md` | Strategy doc | Plane Wiki | Migrate | Product Owner | P2 | Planned |

### Other docs/ Subdirectories

| Current Location | Content Type | Target Surface | Migration Action | Owner | Priority | Status |
|------------------|-------------|----------------|-----------------|-------|----------|--------|
| `docs/governance/*.md` | Governance docs | Plane Wiki | Migrate | Governance Lead | P2 | Planned |
| `docs/operations/*.md` | Operations docs | Plane Wiki | Migrate | Ops Lead | P1 | Planned |
| `docs/deployment/*.md` | Deployment runbooks | Plane Wiki | Migrate | Infrastructure Lead | P0 | Planned |
| `docs/releases/*.md` | Release notes | Plane Wiki | Migrate | Release Manager | P2 | Planned |
| `docs/releases/*.json` | Machine-readable release data | Repo SSOT | Stay | Agent | -- | Active |
| `docs/security/*.md` | Security docs | Plane Wiki | Migrate | Security Lead | P1 | Planned |
| `docs/testing/*.md` | Test docs | Repo SSOT | Stay (code-adjacent) | QA Lead | -- | Active |
| `docs/ci/*.md` | CI reference | Repo SSOT | Stay (CI-adjacent) | Agent | -- | Active |
| `docs/modules/*.md` | Module docs | Repo SSOT | Stay (code-adjacent) | Module owners | -- | Active |
| `docs/troubleshooting/*.md` | Troubleshooting guides | Plane Wiki | Migrate | Ops Lead | P1 | Planned |
| `docs/workflows/*.md` | Workflow docs | Plane Wiki | Migrate | Automation Lead | P2 | Planned |
| `docs/analytics/*.md` | Analytics docs | Plane Wiki | Migrate | Data Lead | P2 | Planned |
| `docs/product/*.md` | Product docs | Plane Wiki | Migrate | Product Owner | P1 | Planned |
| `docs/design/*.md` | Design docs | Plane Wiki | Migrate | Design Lead | P2 | Planned |
| `docs/research/*.md` | Research docs | Plane Wiki | Migrate | AI Lead | P3 | Planned |
| `docs/archive/*.md` | Archived content | Archive | Archive (already archived) | -- | P3 | Planned |
| `docs/odoo/*.md` | Odoo reference | Repo SSOT | Stay (code-adjacent) | Odoo Lead | -- | Active |
| `docs/oca/*.md` | OCA reference | Repo SSOT | Stay (code-adjacent) | Odoo Lead | -- | Active |
| `docs/infra/*.md` | Infrastructure docs | Plane Wiki | Migrate | Infrastructure Lead | P1 | Planned |
| `docs/auth/*.md` | Auth docs | Plane Wiki | Migrate | Platform Architect | P1 | Planned |
| `docs/api/*.md` | API reference | Repo SSOT | Stay (code-adjacent) | API owners | -- | Active |
| `docs/kb/*.md` | Knowledge base articles | Plane Wiki | Migrate | Various | P2 | Planned |
| `docs/portfolio/*.md` | Portfolio docs | Plane Wiki | Migrate | Product Owner | P2 | Planned |
| `docs/okr/*.md` | OKR docs | Plane Wiki | Migrate | Governance Lead | P2 | Planned |
| `docs/github/*.md` | GitHub reference | Repo SSOT | Stay (code-adjacent) | Agent | -- | Active |
| `docs/agents/*.md` | Agent docs | Repo SSOT | Stay (code-adjacent) | Agent | -- | Active |

---

## Duplicate Content Clusters (Known)

| Cluster | Locations | Canonical Source | Action |
|---------|-----------|-----------------|--------|
| EE Parity | `docs/architecture/EE_PARITY_MATRIX.md`, `docs/architecture/EE_PARITY_POLICY.md`, `docs/ai/EE_PARITY.md`, `CLAUDE.md` (inline) | `CLAUDE.md` (L1) + Plane Wiki (L2) | Merge into one Plane page, link from CLAUDE.md |
| Architecture overview | `docs/architecture/INSIGHTPULSEAI_TECHNICAL_ARCHITECTURE.md`, `docs/ai/ARCHITECTURE.md` | Plane Wiki | Merge into one Plane page |
| Secrets policy | `docs/architecture/SECRETS_POLICY.md`, `.claude/rules/secrets-policy.md`, `CLAUDE.md` (inline) | `.claude/rules/secrets-policy.md` (L1) | Keep L1 only, remove duplicates |
| Module naming | `docs/ai/IPAI_MODULES.md`, `CLAUDE.md` (inline) | `CLAUDE.md` (L1) | Keep in CLAUDE.md, archive separate file |
| Repo structure | `docs/architecture/REPO_LAYOUT.md`, `docs/architecture/REPOSITORY_STRUCTURE.md`, `docs/architecture/MONOREPO_STRUCTURE.md`, `docs/ai/REPO_STRUCTURE.md` | `docs/ai/REPO_STRUCTURE.md` (L1, code-adjacent) | Archive duplicates |
| Deployment docs | `docs/architecture/DEPLOY_TARGET_MATRIX.md`, `docs/deployment/*.md` | Plane Wiki | Merge into one runbook |

---

## Migration Statistics (Projected)

| Target Surface | Estimated File Count | Percentage |
|---------------|---------------------|------------|
| Stays in Repo (L1) | ~120 files | ~40% |
| Migrates to Plane Wiki (L2) | ~80 files | ~27% |
| Both Linked (L1+L2) | ~30 files | ~10% |
| Archive then Delete | ~70 files | ~23% |
| **Total** | **~300 files** | **100%** |
