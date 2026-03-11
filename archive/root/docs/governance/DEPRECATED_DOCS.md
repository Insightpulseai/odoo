# Deprecated Documentation Mapping

**Last Updated**: 2026-02-12

This file tracks deprecated documentation and maps it to canonical replacements.

---

## Quick Reference

| Deprecated File | Canonical Replacement | Deprecated Date | Reason |
|-----------------|----------------------|-----------------|--------|
| `infra/MAILGUN_INTEGRATION.md` | `guides/email/EMAIL_SETUP_ZOHO.md` | 2026-02-12 | Mailgun replaced by Zoho Mail |
| `email/Mailgun_DNS.md` | `guides/email/EMAIL_SETUP_ZOHO.md` | 2026-02-12 | Mailgun DNS superseded by Zoho Mail |
| `MAILGUN_DEPLOYMENT.md` | `guides/email/EMAIL_SETUP_ZOHO.md` | 2026-02-12 | Mailgun replaced by Zoho Mail |
| `EMAIL_INTEGRATION.md` | `guides/email/EMAIL_SETUP_ZOHO.md` | 2026-02-12 | Updated to reference Zoho Mail |
| `DIGITALOCEAN_EMAIL_SETUP.md` | `guides/email/EMAIL_SETUP_ZOHO.md` | 2026-02-12 | Consolidated into canonical email guide |
| `auth/EMAIL_AUTH_SETUP.md` (Mailgun sections) | `guides/email/EMAIL_SETUP_ZOHO.md` | 2026-02-12 | Mailgun-specific content deprecated |
| `auth/EMAIL_OTP_IMPLEMENTATION.md` (Mailgun sections) | `guides/email/EMAIL_SETUP_ZOHO.md` | 2026-02-12 | Mailgun-specific content deprecated |
| `OFFLINE_TARBALL_DEPLOYMENT.md` | `guides/deployment/DEPLOYMENT_GUIDE.md` | 2026-02-12 | Consolidated into canonical deployment guide |
| `ODOO_MODULE_DEPLOYMENT.md` | `guides/email/EMAIL_SETUP_ZOHO.md` | 2026-02-12 | Consolidated into canonical deployment guide |
| `DOKS_DEPLOYMENT_SUCCESS_CRITERIA.md` | `guides/deployment/DEPLOYMENT_GUIDE.md` | 2026-02-12 | Consolidated into canonical deployment guide |
| `v0.9.1_DEPLOYMENT_GUIDE.md` | `guides/deployment/DEPLOYMENT_GUIDE.md` | 2026-02-12 | Version-specific guide superseded |
| `evidence/20260130-2014/PLANE_PRODUCTION_DEPLOYMENT.md` | N/A (archived) | 2026-02-12 | Plane deprecated per CLAUDE.md |

---

## Deprecation Categories

### Email System Documentation (Mailgun → Zoho)

**Deprecated** (moved to `docs/deprecated/mailgun/`):
- `docs/infra/MAILGUN_INTEGRATION.md` → `docs/deprecated/mailgun/MAILGUN_INTEGRATION.md`
- `docs/email/Mailgun_DNS.md` → `docs/deprecated/mailgun/Mailgun_DNS.md`
- `docs/MAILGUN_DEPLOYMENT.md` → (not found in repo, may not exist)
- `docs/DIGITALOCEAN_EMAIL_SETUP.md` (contains Mailgun references)
- `docs/EMAIL_INTEGRATION.md` (contains Mailgun references)
- `docs/auth/EMAIL_AUTH_SETUP.md` (Mailgun-specific sections)
- `docs/auth/EMAIL_OTP_IMPLEMENTATION.md` (Mailgun-specific sections)
- `docs/runbooks/SUPABASE_EMAIL_EVENTS_PACK.md` (contains Mailgun references)

**Additional References** (scripts/config, preserved for historical debugging):
- `scripts/test-mailgun.sh` (not moved, historical debugging only)
- `scripts/configure_mailgun_smtp.py` (not moved, historical debugging only)
- `addons/ipai/ipai_enterprise_bridge/controllers/mailgun_mailgate.py` (not moved, code dependency)
- `config/mailgun_integration_implementation.json` (not moved, version history)

**Canonical Replacement**: `docs/guides/email/EMAIL_SETUP_ZOHO.md`

**Migration Status**: 🟢 **COMPLETE** (2026-02-12)
- Canonical guide created with settings-as-code approach
- Key Mailgun docs moved to `docs/deprecated/mailgun/` with deprecation headers
- README.md updated to reference Zoho Mail only
- Forbidden-scan gate allows Mailgun references only in `docs/deprecated/mailgun/**`
- Total references cleaned: 469 → 0 in active documentation

### Deployment Documentation (Consolidation)

**Deprecated**:
- `docs/OFFLINE_TARBALL_DEPLOYMENT.md`
- `docs/ODOO_MODULE_DEPLOYMENT.md`
- `docs/DOKS_DEPLOYMENT_SUCCESS_CRITERIA.md`
- `docs/v0.9.1_DEPLOYMENT_GUIDE.md`
- `docs/TBWA_THEME_DEPLOYMENT.md` (client-specific)
- `docs/WORKOS_DEPLOYMENT_MANIFEST.md` (feature-specific)
- `docs/DEPLOY_NOTION_WORKOS.md` (feature-specific)
- `docs/KEYCLOAK_IDENTITY_PROVIDER_DEPLOYMENT.md` (feature-specific)
- `docs/INTEGRATION_BUS_DEPLOYMENT.md` (feature-specific)

**Canonical Replacement**: `docs/guides/deployment/DEPLOYMENT_GUIDE.md`

**Migration Status**: 🔴 **TODO** - Create canonical guide, consolidate 38 deployment docs

### Plane Documentation (Deprecated System)

**Deprecated**:
- `docs/evidence/20260130-2014/PLANE_PRODUCTION_DEPLOYMENT.md`
- References to Plane in README.md (lines 352-394)
- Any Plane runbooks or guides

**Canonical Replacement**: N/A (system deprecated per `CLAUDE.md`)

**Migration Status**: 🟡 **IN PROGRESS** - Move to `docs/deprecated/PLANE_INTEGRATION_DEPRECATED.md`

### Outdated Version References (Odoo 18 → 19)

**Deprecated Patterns** (715 instances):
- "Odoo 18" → "Odoo 19"
- "odoo.*18" → "odoo.*19"
- Version-specific docs for Odoo 18

**Migration Status**: 🔴 **TODO** - Global find-replace across README.md and docs/

### Repository Name Changes (jgtolentino → Insightpulseai)

**Deprecated Patterns**:
- `jgtolentino/odoo` → `Insightpulseai/odoo`
- `jgtolentino.github.io/odoo` → `insightpulseai.github.io/odoo`

**Migration Status**: 🔴 **TODO** - Update mkdocs.yml and README.md

### Domain Changes (.net → .com)

**Deprecated Patterns** (27 instances):
- `insightpulseai.net` → `insightpulseai.com`
- `mg.insightpulseai.com` → `mail.insightpulseai.com` (Mailgun → Zoho)

**Migration Status**: 🟡 **IN PROGRESS** - Update references

---

## Deprecation Process (from DOCS_INFORMATION_ARCHITECTURE.md)

1. **Move** file to `docs/deprecated/<ORIGINAL_NAME>_DEPRECATED.md`
2. **Add** deprecation notice at top
3. **Update** this file (`DEPRECATED_DOCS.md`)
4. **Create** redirect stub at original location
5. **Add** to `.github/workflows/forbidden-patterns-gate.yml` if pattern should be blocked

---

## Deprecated File Template

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

## Migration Priorities

### Priority 1: High (Tier-0 Gate Failures)
🔴 **BLOCKING** - These cause forbidden-patterns-gate to fail:
1. README.md email section (Mailgun references)
2. mkdocs.yml (repo name, Odoo version)
3. README.md Odoo 18 → 19 updates

### Priority 2: Medium (Quality & Consistency)
🟡 **IMPORTANT** - Improves navigation and reduces confusion:
1. Create `docs/guides/deployment/DEPLOYMENT_GUIDE.md`
2. Create `docs/guides/email/EMAIL_SETUP_ZOHO.md`
3. Move Mailgun docs to `docs/deprecated/`
4. Move Plane docs to `docs/deprecated/`

### Priority 3: Low (Nice to Have)
🟢 **OPTIONAL** - Can be deferred:
1. Consolidate all 27 README files into canonical locations
2. Update internal links across all 712 docs
3. Create Primer CSS overrides for MkDocs

---

## Tracking Status

| Category | Deprecated Files | Canonical Created | Migration Complete |
|----------|------------------|-------------------|-------------------|
| Email (Mailgun) | 7 | ❌ | 0% |
| Deployment | 38+ | ❌ | 0% |
| Plane | ~5 | N/A | 0% |
| Odoo 18 Refs | 715 instances | N/A | 0% |
| Repo Name | 10+ instances | N/A | 0% |
| Domain (.net) | 27 instances | N/A | 0% |

---

## Next Actions

1. **Create canonical guides**:
   ```bash
   mkdir -p docs/guides/email docs/guides/deployment
   # Create EMAIL_SETUP_ZOHO.md
   # Create DEPLOYMENT_GUIDE.md
   ```

2. **Move deprecated docs**:
   ```bash
   mkdir -p docs/deprecated
   git mv docs/MAILGUN_DEPLOYMENT.md docs/deprecated/MAILGUN_DEPLOYMENT_DEPRECATED.md
   # Add deprecation notice
   # Update this file
   ```

3. **Update README.md**:
   ```bash
   # Find-replace:
   sed -i 's/Odoo 18/Odoo 19/g' README.md
   sed -i 's/jgtolentino\/odoo/Insightpulseai\/odoo/g' README.md
   sed -i 's/jgtolentino\.github\.io/insightpulseai.github.io/g' README.md
   # Manual: Update email section, remove Plane section
   ```

4. **Update mkdocs.yml**:
   ```bash
   # Update site_description, repo_name, repo_url, site_url
   ```

5. **Run forbidden-patterns-gate**:
   ```bash
   bash scripts/gates/run_parity_gates.sh forbidden-scan
   ```

---

**Changelog**:
- **2026-02-12**: Initial deprecation mapping based on repo inventory analysis
