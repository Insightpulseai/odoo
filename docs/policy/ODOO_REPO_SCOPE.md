# Odoo Repository Scope Policy

> **Status**: Active | **Version**: 1.0.0 | **Last Updated**: 2026-02-15

## Purpose

This document defines what belongs in the `odoo` repository versus future organization-level repositories (`platform/`, `web/`, `agents/`).

## TLDR

**`odoo` repo = Odoo ERP runtime + custom modules + OCA layer + deployment config**

Everything else (standalone apps, agent frameworks, design systems) belongs in separate repos.

---

## Scope Definition

### ✅ What Belongs in `odoo/`

#### Core Odoo Runtime
- Odoo CE 19.0 configuration (`config/{dev,staging,prod}/`)
- Docker compose files for Odoo stack
- Database migrations and initialization scripts
- Odoo deployment infrastructure (`infra/deploy/`, `docker/`)

#### Odoo Custom Modules
- **IPAI modules**: `addons/ipai/ipai_*` — custom business logic modules
- **OCA integration**: `addons/oca/` — OCA module manifests and lockfiles
- **Module scaffolding**: Templates and generators for Odoo modules

#### Odoo-Specific Tooling
- Odoo CLI scripts (`scripts/odoo/`)
- OCA workflow automation (`scripts/oca/`)
- Module testing and quality gates (`scripts/ci/`, `.github/workflows/`)
- Odoo data importers and ETL scripts

#### Domain-Specific Configuration
- Finance SSC configuration (`config/finance/`)
- BIR compliance templates (`config/bir/`)
- Integration point configuration (n8n, Slack, Superset)

#### Specifications
- Odoo feature specs (`spec/odoo-*`, `spec/ipai-*`)
- OCA module selection criteria (`spec/oca-*`)
- Parity catalogs for EE equivalence (`catalog/`)

### ❌ What Does NOT Belong in `odoo/`

#### Standalone Web Applications
- Next.js apps → `web/` repo (future)
- React SPAs → `web/` repo (future)
- Static sites → `web/` repo (future)

**Rationale**: These apps have independent deployment lifecycles and don't require Odoo runtime.

**Current State**: `apps/web/` is marked for future extraction (see `FUTURE_SPLIT.md`).

#### AI Agent Framework
- Agent orchestration → `agents/` repo (future)
- MCP servers → `agents/` repo (future)
- Prompt libraries → `agents/` repo (future)

**Rationale**: Agent framework is platform-agnostic and used across multiple projects.

**Current State**: `agents/` is self-contained and ready for extraction.

#### Platform Tooling
- Design systems → `platform/` repo (future)
- Shared UI components → `platform/` repo (future)
- Cross-project utilities → `platform/` repo (future)

**Rationale**: Platform components serve multiple applications beyond Odoo.

**Current State**: `infra/platform-kit/` is marked for future extraction.

---

## Database Naming Policy

### Allowlist (Enforced by CI)

Only these database names are permitted in this repository:

- **`odoo_dev`** — Development environment
- **`odoo_staging`** — Staging environment
- **`odoo_prod`** — Production environment

### Enforcement

- **CI Gate**: `.github/workflows/db-naming-gate.yml`
- **Validator**: `scripts/ci/db_naming_gate.py`
- **Scanned Files**:
  - `docker-compose*.yml`
  - `config/**/odoo.conf`
  - `.env*` (excluding `.env.example`)

### Rationale

Deterministic database naming prevents:
- Shadow databases causing state drift
- Accidental production writes from local dev
- Unclear environment boundaries
- Odoo's multi-DB UI confusion (`list_db=False`)

---

## Environment Configuration Policy

### Single Source of Truth (SSOT)

Each environment has exactly ONE canonical configuration file:

\`\`\`
config/
├── dev/odoo.conf       # Development (local Docker Desktop)
├── staging/odoo.conf   # Staging (pre-production validation)
└── prod/odoo.conf      # Production (DigitalOcean / live traffic)
\`\`\`

### Environment Selection

Docker Compose uses \`\${ODOO_ENV:-dev}\` substitution:

\`\`\`yaml
volumes:
  - ./config/\${ODOO_ENV:-dev}/odoo.conf:/etc/odoo/odoo.conf:ro
\`\`\`

\`\`\`bash
# Development (default)
docker compose up

# Staging
ODOO_ENV=staging docker compose up

# Production
ODOO_ENV=prod docker compose up
\`\`\`

### Configuration Inheritance

Each environment config is self-contained (no inheritance or includes). This ensures:
- No hidden config dependencies
- Full environment portability
- Explicit configuration differences

---

## Repository Boundary Markers

### Identified Split Candidates

The following directories are candidates for future extraction to separate repositories:

1. **\`apps/web/\`** → \`web/\` repo
   - Status: Marked for extraction
   - Marker: \`apps/web/FUTURE_SPLIT.md\`
   - Reason: Independent deployment lifecycle

2. **\`infra/platform-kit/\`** → \`platform/\` repo
   - Status: Marked for extraction
   - Marker: \`infra/platform-kit/FUTURE_SPLIT.md\`
   - Reason: Cross-project platform utilities

3. **\`agents/\`** → \`agents/\` repo (already extracted)
   - Status: Self-contained, ready for extraction
   - Marker: \`agents/README.md\` (notes independence)
   - Reason: Platform-agnostic agent framework

### Migration Strategy

When extracting a split candidate:

1. Create new repository with canonical name
2. Move directory contents via \`git filter-repo\` (preserve history)
3. Add git submodule or package dependency in \`odoo/\`
4. Update CI workflows to reference new repo
5. Archive original directory: \`archive/root/<name>/\`

---

## Compliance Verification

### Automated Checks

The following CI gates enforce this policy:

- **\`repo-structure-guard.yml\`**: Prevents shadow Odoo roots
- **\`db-naming-gate.yml\`**: Enforces database naming allowlist
- **\`odoo-module-lint.yml\`**: Validates IPAI module naming (\`ipai_*\`)

### Manual Audits

Quarterly review checklist:

- [ ] No \`web/\` apps tightly coupled to Odoo runtime
- [ ] No \`agents/\` code dependent on Odoo internals
- [ ] All Odoo modules in \`addons/ipai/ipai_*\` (no root-level)
- [ ] No shadow databases (scan Docker volumes)
- [ ] Config files in canonical locations only

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-15 | Environment config split (\`config/{dev,staging,prod}/\`) | Deterministic environments, explicit config per env |
| 2026-02-15 | DB naming allowlist (odoo_dev/staging/prod) | Prevent multi-DB chaos, enforce single-DB pattern |
| 2026-02-15 | Archive \`infra/docker/\` (moved to \`archive/root/\`) | Consolidate to root \`docker/\`, remove duplicate |

---

## Escalation Path

**Question**: "Does this belong in \`odoo/\` repo?"

**Decision Tree**:

1. **Does it require Odoo runtime to function?**
   - Yes → \`odoo/\` repo
   - No → Go to 2

2. **Is it Odoo-specific configuration or business logic?**
   - Yes → \`odoo/\` repo
   - No → Go to 3

3. **Is it used exclusively by Odoo modules/workflows?**
   - Yes → \`odoo/\` repo
   - No → Separate repo (\`web/\`, \`platform/\`, \`agents/\`)

**Still Unsure?**
- Raise in GitHub Discussions: \`Insightpulseai/odoo/discussions\`
- Tag: \`question/repo-scope\`
- Default: Separate repo (easier to merge later than split)

---

## References

- **Target Enterprise Org Structure**: See \`/tmp/alignment_analysis.md\`
- **Current Repo Structure**: \`docs/architecture/REPO_SSOT_MAP.md\`
- **OCA Integration Workflow**: \`docs/ai/OCA_WORKFLOW.md\`
- **Database Naming Gate**: \`.github/workflows/db-naming-gate.yml\`
- **Config SSOT**: \`config/README.md\`

---

*This policy is part of the Odoo repository governance framework. For parent organization policies, see \`Insightpulseai/GOVERNANCE.md\` (future).*
