# Documentation Information Architecture

**Status**: Active | **Last Updated**: 2026-02-12
**Owner**: Engineering Platform Team
**Authority**: Canonical documentation structure for `Insightpulseai/odoo`

---

## Executive Summary

This document defines the **single source of truth** documentation architecture for the InsightPulse Odoo platform. It establishes:
1. **Canonical file locations** for all documentation categories
2. **Deprecation policy** for outdated documentation
3. **Naming conventions** to prevent duplication
4. **CI enforcement** of documentation standards

**Current State**: 712 total docs, 38 deployment docs, 27 READMEs — consolidation required.

---

## Documentation Hierarchy

```
docs/
├── governance/              # Platform policies and standards (NEW)
│   └── ODOOSH_GRADE_PARITY_GATING.md
├── architecture/            # System design and decisions (CANONICAL)
│   ├── PROD_RUNTIME_SNAPSHOT.md
│   ├── runtime_identifiers.json
│   └── DOCS_INFORMATION_ARCHITECTURE.md (this file)
├── guides/                  # User-facing guides (CANONICAL)
│   ├── deployment/
│   │   └── DEPLOYMENT_GUIDE.md (consolidates 38 deployment docs)
│   ├── email/
│   │   └── EMAIL_SETUP_ZOHO.md (replaces Mailgun docs)
│   └── development/
│       └── ODOO_DEVELOPMENT_GUIDE.md
├── reference/               # Technical reference (CANONICAL)
│   ├── cli/
│   │   └── ODOO_CLI_REFERENCE.md
│   └── api/
│       └── IPAI_MODULE_API.md
├── runbooks/                # Operational procedures (CANONICAL)
│   ├── finance-ppm/
│   │   └── FINANCE_PPM_OPERATIONS.md
│   └── deployment/
│       └── DEPLOYMENT_RUNBOOK.md
├── evidence/                # Implementation evidence (timestamped)
│   └── YYYYMMDD-HHMM/
│       └── <scope>/
│           └── IMPLEMENTATION.md
├── deprecated/              # Deprecated documentation (ARCHIVE)
│   ├── MAILGUN_INTEGRATION_DEPRECATED.md
│   ├── PLANE_DOCUMENTATION_DEPRECATED.md
│   └── ODOO_18_MIGRATION_DEPRECATED.md
├── pages/                   # MkDocs source (GitHub Pages)
│   ├── index.md
│   ├── getting-started.md
│   ├── architecture.md
│   └── ...
└── DEPRECATED_DOCS.md       # Deprecation mapping table (NEW)
```

---

## Canonical Documentation Locations

### 1. Platform Governance
**Location**: `docs/governance/`
**Purpose**: Platform-wide policies, standards, and quality gates
**Naming**: `<TOPIC>_<TYPE>.md` (e.g., `ODOOSH_GRADE_PARITY_GATING.md`)

**Canonical Files**:
- `ODOOSH_GRADE_PARITY_GATING.md` - Quality gate framework
- `MODULE_NAMING_POLICY.md` - IPAI module naming standards
- `DEPRECATION_POLICY.md` - How to deprecate features/docs

### 2. Architecture & Design
**Location**: `docs/arch/`
**Purpose**: System architecture, ADRs, deployment topology
**Naming**: `<COMPONENT>_<TYPE>.md` or `<TOPIC>.md`

**Canonical Files**:
- `PROD_RUNTIME_SNAPSHOT.md` - Production infrastructure state
- `runtime_identifiers.json` - Machine-readable runtime config
- `DOCS_INFORMATION_ARCHITECTURE.md` - This file
- `ODOO_ARCHITECTURE.md` - Platform architecture overview

**Deprecated Locations**:
- ❌ `docs/ARCHITECTURE.md` → Use `docs/arch/ODOO_ARCHITECTURE.md`
- ❌ Scattered diagrams → Use `docs/arch/diagrams/`

### 3. Deployment Documentation
**Location**: `docs/guides/deployment/`
**Purpose**: How to deploy the platform
**Naming**: `DEPLOYMENT_GUIDE.md` (single canonical file)

**Consolidation Target**: Merge 38 deployment docs into single guide with sections:
1. Quick Start (local dev)
2. Production Deployment (DigitalOcean)
3. Database Migrations
4. Email Setup (Zoho Mail)
5. Monitoring & Health Checks
6. Rollback Procedures

**Files to Deprecate**:
```bash
docs/OFFLINE_TARBALL_DEPLOYMENT.md           → Section in DEPLOYMENT_GUIDE.md
docs/ODOO_MODULE_DEPLOYMENT.md               → Section in DEPLOYMENT_GUIDE.md
docs/DOKS_DEPLOYMENT_SUCCESS_CRITERIA.md     → Section in DEPLOYMENT_GUIDE.md
docs/v0.9.1_DEPLOYMENT_GUIDE.md              → Deprecated (version-specific)
docs/evidence/*/DEPLOYMENT_*.md               → Keep (timestamped evidence)
```

### 4. Email Integration
**Location**: `docs/guides/email/`
**Purpose**: Email system setup and configuration
**Naming**: `EMAIL_SETUP_ZOHO.md` (canonical)

**Current State**: 11 email docs, majority referencing deprecated Mailgun

**Canonical File**: `EMAIL_SETUP_ZOHO.md` with sections:
1. Zoho Mail SMTP Configuration
2. Odoo Email Server Setup
3. Inbound Email Processing
4. Troubleshooting

**Files to Deprecate**:
```bash
docs/MAILGUN_DEPLOYMENT.md                   → docs/deprecated/MAILGUN_INTEGRATION_DEPRECATED.md
docs/EMAIL_INTEGRATION.md                    → Update to reference Zoho Mail
docs/infra/MAILGUN_INTEGRATION.md            → docs/deprecated/
docs/DIGITALOCEAN_EMAIL_SETUP.md             → Merge into EMAIL_SETUP_ZOHO.md
```

### 5. Development Guides
**Location**: `docs/guides/development/`
**Purpose**: How to develop custom modules and contribute
**Naming**: `ODOO_DEVELOPMENT_GUIDE.md` (canonical)

**Canonical Files**:
- `ODOO_DEVELOPMENT_GUIDE.md` - Module development workflow
- `ODOO_EXECUTION.md` - Odoo execution patterns (already exists)
- `TESTING_GUIDE.md` - Testing procedures

### 6. Runbooks
**Location**: `docs/runbooks/`
**Purpose**: Operational procedures for specific tasks
**Naming**: `<domain>/<OPERATION>_RUNBOOK.md`

**Structure**:
```
docs/runbooks/
├── finance-ppm/
│   ├── FINANCE_PPM_OPERATIONS.md
│   └── SEED_REGENERATION.md
├── deployment/
│   ├── DEPLOYMENT_RUNBOOK.md
│   └── ROLLBACK_RUNBOOK.md
└── monitoring/
    └── HEALTH_CHECK_RUNBOOK.md
```

### 7. Evidence Documentation
**Location**: `docs/evidence/YYYYMMDD-HHMM/<scope>/`
**Purpose**: Timestamped implementation evidence
**Naming**: `IMPLEMENTATION.md`, `STATUS.txt`, `VERIFICATION.md`

**Policy**: Evidence docs are **immutable** and **timestamped** — never edit, only create new.

### 8. Deprecated Documentation
**Location**: `docs/deprecated/`
**Purpose**: Archive of deprecated documentation with clear deprecation notices
**Naming**: `<ORIGINAL_NAME>_DEPRECATED.md`

**Template**:
```markdown
# [Original Title] (DEPRECATED)

**⚠️ DEPRECATION NOTICE**

This document is **deprecated** as of YYYY-MM-DD.

**Reason**: [e.g., "Mailgun replaced by Zoho Mail SMTP"]

**Replacement**: See [canonical_doc.md](../guides/email/EMAIL_SETUP_ZOHO.md)

**Last Valid Version**: [Odoo 18.0 / 2025-01-15]

---

[Original content preserved for historical reference...]
```

---

## Naming Conventions

### File Naming Rules
1. **Use SCREAMING_SNAKE_CASE** for documentation files: `DEPLOYMENT_GUIDE.md`
2. **Use lowercase-with-hyphens** for MkDocs pages: `getting-started.md`
3. **Prefix with domain** for runbooks: `finance-ppm/OPERATIONS.md`
4. **Suffix with type** for governance: `MODULE_NAMING_POLICY.md`
5. **No version numbers** in canonical docs: ❌ `v0.9.1_DEPLOYMENT_GUIDE.md`

### Directory Naming Rules
1. **Use lowercase** for category directories: `docs/guides/`, `docs/runbooks/`
2. **Use UPPERCASE** for timestamped directories: `docs/evidence/20260212-1830/`
3. **No plural** for single-file categories: `docs/arch/` (not `architectures/`)
4. **Use plural** for collections: `docs/guides/`, `docs/runbooks/`

---

## Deprecation Policy

### When to Deprecate
- Content is factually incorrect and cannot be updated (e.g., Mailgun docs when Zoho is canonical)
- Document superseded by newer canonical version
- Feature/system no longer supported (e.g., Plane)
- Version-specific docs for EOL versions (e.g., Odoo 18 after migrating to 19)

### Deprecation Process
1. **Move** file to `docs/deprecated/<ORIGINAL_NAME>_DEPRECATED.md`
2. **Add** deprecation notice at top (see template above)
3. **Update** `docs/DEPRECATED_DOCS.md` mapping table
4. **Create** redirect stub at original location:
```markdown
# [Original Title]

**⚠️ This document has been deprecated.**

See: [new_location.md](../guides/canonical/NEW_LOCATION.md)
```
5. **Add** to `.github/workflows/forbidden-patterns-gate.yml` if pattern should be blocked

### Never Delete
- Evidence documentation (`docs/evidence/`)
- Deployment proofs (`docs/releases/`)
- Historical runbooks (move to `docs/deprecated/` instead)

---

## MkDocs Integration

### GitHub Pages Configuration
**Site URL**: `https://insightpulseai.github.io/odoo/` (UPDATE: correct org)
**Source**: `docs/pages/` directory
**Build**: `mkdocs build --strict --site-dir artifacts/docs_site`

### mkdocs.yml Updates Required
```yaml
site_name: Odoo Documentation
site_url: https://insightpulseai.github.io/odoo/  # Updated from jgtolentino
site_description: Documentation for the Odoo platform — InsightPulse AI platform built on Odoo 19 CE  # Updated from Odoo 18
site_author: InsightPulse AI Team

repo_name: Insightpulseai/odoo  # Updated from jgtolentino/odoo
repo_url: https://github.com/Insightpulseai/odoo  # Updated
edit_uri: edit/main/docs/pages/

theme:
  name: material
  custom_dir: docs/overrides  # Primer CSS overrides
  # ... rest of config
```

### Primer CSS Integration
**Override Directory**: `docs/overrides/`
**Purpose**: Apply Primer design system without breaking Material theme

**Implementation**:
```
docs/overrides/
├── main.html                # Base template extension
└── stylesheets/
    └── primer-overrides.css  # Primer CSS customizations
```

**Example Override** (`docs/overrides/stylesheets/primer-overrides.css`):
```css
/* Primer-inspired typography */
.md-typeset h1 {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
  font-weight: 600;
  border-bottom: 1px solid var(--md-default-fg-color--lightest);
  padding-bottom: 0.3em;
}

/* Primer-inspired code blocks */
.md-typeset code {
  background-color: rgba(175, 184, 193, 0.2);
  border-radius: 6px;
  padding: 0.2em 0.4em;
}
```

**Add to mkdocs.yml**:
```yaml
theme:
  custom_dir: docs/overrides
extra_css:
  - stylesheets/primer-overrides.css
```

---

## CI Enforcement

### Documentation Gates
**Workflow**: `.github/workflows/docs-build.yml`
**Enforcement**:
1. **Strict Build**: `mkdocs build --strict` (zero warnings)
2. **Link Validation**: All internal links resolve
3. **Forbidden Patterns**: Detect outdated references (see `ODOOSH_GRADE_PARITY_GATING.md`)

### Deprecation Tracking
**Workflow**: `.github/workflows/deprecation-tracker.yml` (NEW)
**Purpose**: Ensure `docs/DEPRECATED_DOCS.md` is updated when files moved to `docs/deprecated/`

**Implementation**:
```yaml
name: Deprecation Tracker

on:
  pull_request:
    paths:
      - "docs/deprecated/**"
      - "docs/DEPRECATED_DOCS.md"

jobs:
  validate-deprecation-mapping:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Check deprecation mapping
        run: |
          # Verify all files in docs/deprecated/ are listed in DEPRECATED_DOCS.md
          for file in docs/deprecated/*.md; do
            basename=$(basename "$file")
            if ! grep -q "$basename" docs/DEPRECATED_DOCS.md; then
              echo "ERROR: $basename not listed in DEPRECATED_DOCS.md"
              exit 1
            fi
          done
```

---

## README.md Truth Update

**Canonical Truths** (from `CLAUDE.md` and architecture docs):

| Current (Incorrect) | Correct | Evidence |
|---------------------|---------|----------|
| Odoo 18 Community Edition | Odoo 19 Community Edition | `CLAUDE.md` line "Stack: Odoo CE 19.0" |
| jgtolentino/odoo repo | Insightpulseai/odoo | `CLAUDE.md` line "Repo: Insightpulseai/odoo" |
| Mailgun SMTP | Zoho Mail SMTP (`smtp.zoho.com:587`) | `CLAUDE.md` line "Email: Zoho Mail" |
| mg.insightpulseai.com | mail.insightpulseai.com | Zoho Mail domain |
| jgtolentino.github.io/odoo | insightpulseai.github.io/odoo | GitHub Pages org update |
| python odoo-bin (WRONG) | ./odoo-bin or python -m odoo | `README.md` line 42 (already correct) |
| Plane integration | Deprecated (remove section) | `CLAUDE.md` line "Deprecated: Plane (all)" |

**Sections to Update**:
1. Title/Description (line 1-5): Change "Odoo 18" → "Odoo 19"
2. Badges (line 3): Change `jgtolentino/odoo` → `Insightpulseai/odoo`
3. Documentation URL (line 12): Change `jgtolentino.github.io` → `insightpulseai.github.io`
4. Email Integration section (lines 296-394): Replace Mailgun docs with Zoho Mail
5. Plane section (lines 352-394): Move to `docs/deprecated/PLANE_INTEGRATION_DEPRECATED.md`

---

## Migration Checklist

**Phase 1: Consolidation** (Priority: High)
- [ ] Create `docs/guides/deployment/DEPLOYMENT_GUIDE.md` (consolidate 38 files)
- [ ] Create `docs/guides/email/EMAIL_SETUP_ZOHO.md` (replace Mailgun docs)
- [ ] Create `docs/DEPRECATED_DOCS.md` (mapping table)
- [ ] Move Mailgun docs to `docs/deprecated/`
- [ ] Move Plane docs to `docs/deprecated/`

**Phase 2: README Truth** (Priority: High)
- [ ] Update README.md Odoo 18 → Odoo 19 references (715 instances!)
- [ ] Update mkdocs.yml repo URLs and site description
- [ ] Update README.md email section (remove Mailgun, add Zoho)
- [ ] Remove or archive Plane section

**Phase 3: CI Enforcement** (Priority: Medium)
- [ ] Update `docs-build.yml` to enforce strict mode
- [ ] Create `deprecation-tracker.yml` workflow
- [ ] Add Primer CSS overrides to MkDocs theme
- [ ] Create `forbidden-patterns-gate.yml` (Tier-0 gate)

**Phase 4: Link Updates** (Priority: Low)
- [ ] Update all internal docs links to use canonical locations
- [ ] Run link checker and fix broken references
- [ ] Update external references (if any) to new GitHub Pages URL

---

## Appendix: Evidence-Based Claims

| Claim | Evidence File | Line Numbers |
|-------|---------------|--------------|
| 712 total docs | Inventory script output | Line "Total docs: 712" |
| 38 deployment docs | Inventory script output | Line "Deployment docs: 38" |
| 27 READMEs | Inventory script output | Line "README files: 27" |
| 469 Mailgun references | Inventory script output | Line "Mailgun references: 469" |
| 715 Odoo 18 references | Inventory script output | Line "Odoo 18 references: 715" |
| Zoho Mail canonical | `CLAUDE.md` | Quick Reference table |
| insightpulseai.com canonical | `CLAUDE.md` | "Domain: insightpulseai.com (.net deprecated)" |

---

**Changelog**:
- **2026-02-12**: Initial information architecture based on repo inventory analysis
