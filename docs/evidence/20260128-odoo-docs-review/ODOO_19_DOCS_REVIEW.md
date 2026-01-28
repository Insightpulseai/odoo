# Odoo 19.0 Documentation Review

**Date**: 2026-01-28
**Branch**: claude/review-odoo-docs-dVixq
**Scope**: Developer documentation, Odoo.sh features, contributing guidelines

---

## Executive Summary

Reviewed Odoo 19.0 official documentation across six key areas. Key findings relevant to our self-hosted CE + OCA + ipai_* stack:

| Area | Relevance | Action Required |
|------|-----------|-----------------|
| Developer Howtos | HIGH | CSS debt guide applicable to ipai_theme_* |
| Odoo.sh Features | LOW | We self-host; document parity differences |
| Developer Tutorials | HIGH | Server Framework 101 for onboarding |
| Reference/ORM API | CRITICAL | Odoo 19.0 API changes affect ipai_* modules |
| Contributing/Development | HIGH | Coding guidelines apply to all ipai_* code |
| Contributing/Documentation | MEDIUM | RST standards for module docs |

---

## 1. Developer How-to Guides

**Source**: [How-to guides - Odoo 19.0](https://www.odoo.com/documentation/19.0/developer/howtos.html)

### Key Guides Available

1. **CSS Technical Debt Control**
   - Directly applicable to `ipai_theme_tbwa_backend` and web modules
   - Use SCSS variables from design tokens
   - Avoid inline styles

2. **Field Component Customization**
   - Web framework field widget customization
   - Relevant for `ipai_ui_*` modules

### Applicability to Our Stack

```
ipai_theme_tbwa_backend/  → Apply CSS debt guide
ipai_ui_brand_tokens/     → Follow field component patterns
ipai_web_*/               → Web framework howtos
```

---

## 2. Odoo.sh Features (For Reference Only)

**Source**: [Odoo.sh Features](https://www.odoo.sh/features)

### Odoo.sh Capabilities (We Self-Host Instead)

| Odoo.sh Feature | Our Self-Hosted Equivalent |
|-----------------|---------------------------|
| GitHub CI/CD | GitHub Actions + self-hosted runners |
| Staging environments | Docker Compose profiles |
| Production deployment | DO droplet + nginx |
| Daily backups | pg_dump cron + off-site sync |
| Email servers | Mailpit (dev) / SMTP relay (prod) |
| DNS management | DigitalOcean DNS |
| Monitoring | Self-hosted + n8n alerts |

### Odoo.sh Limitations We Avoid

- Shared hosting (20-25 DBs/server)
- GitHub-only integration
- Enterprise-only support
- Limited outgoing email quotas
- No GitLab/Bitbucket support

### Our Self-Hosted Advantages

- Full resource control
- Multi-VCS support
- Unlimited databases
- Custom job runners
- No per-seat platform costs

---

## 3. Developer Tutorials

**Source**: [Tutorials - Odoo 19.0](https://www.odoo.com/documentation/19.0/developer/tutorials.html)

### Recommended Learning Path

1. **Setup Guide** (prerequisites)
   - Source install preferred
   - Chrome/Firefox dev tools
   - Debug mode activation

2. **Server Framework 101** (foundational)
   - Model definitions
   - ORM basics
   - Views and actions

3. **Advanced Tutorials** (specialization)
   - Web framework
   - Reports
   - Testing

### Onboarding Checklist for ipai_* Contributors

```markdown
## New Developer Onboarding

- [ ] Complete Odoo Setup Guide
- [ ] Complete Server Framework 101
- [ ] Read CLAUDE.md thoroughly
- [ ] Review OCA coding standards
- [ ] Build test ipai_* module locally
- [ ] Submit first PR with passing CI
```

---

## 4. Reference Documentation - ORM API

**Source**: [ORM API - Odoo 19.0](https://www.odoo.com/documentation/19.0/developer/reference/backend/orm.html)

### Critical Odoo 19.0 ORM Changes

| Change | Impact | Migration Action |
|--------|--------|------------------|
| `read_group` deprecated | HIGH | Use `_read_group` (backend) or `formatted_read_group` (public API) |
| `@api.private` decorator | MEDIUM | Mark internal methods for RPC exclusion |
| `odoo.domain` / `odoo.Domain` API | MEDIUM | Use new domain manipulation API |
| Cron batch commit notifications | LOW | Update long-running crons |

### Required Updates for ipai_* Modules

```python
# DEPRECATED (Odoo 18 and earlier)
result = self.env['model'].read_group(
    domain, fields, groupby
)

# NEW (Odoo 19)
result = self.env['model']._read_group(
    domain, groupby, aggregates
)

# Or for formatted public API
result = self.env['model'].formatted_read_group(
    domain, fields, groupby
)
```

### Reference Sections Covered

- Models
- Fields
- Constraints and indexes
- Recordsets
- Method decorators
- Environment
- Common ORM methods
- Inheritance and extension
- Error management

### External API Notes

External JSON-2 API available at `/json/2` endpoint.
**Limitation**: Only available on Custom Odoo pricing plans (not relevant to our CE deployment).

---

## 5. Contributing - Development Guidelines

**Source**: [Development Guidelines - Odoo 19.0](https://www.odoo.com/documentation/19.0/contributing/development.html)

### Branch Naming Convention

```
19.0-<feature-description>
```

For our repo, combined with CLAUDE.md rules:
```
claude/<feature>-<session-id>    # Claude Code branches
19.0-ipai-<feature>              # Direct Odoo-style branches
```

### Coding Guidelines Summary

**Source**: [Coding Guidelines - Odoo 19.0](https://www.odoo.com/documentation/19.0/contributing/development/coding_guidelines.html)

#### Python Standards (PEP8+)

```python
# Import order (3 groups, alphabetically sorted within each)
import os                           # 1. Python stdlib
import sys

from odoo import api, fields, models  # 2. Odoo imports
from odoo.exceptions import UserError

from odoo.addons.base import something  # 3. Odoo addons imports
```

#### Module Structure

```
ipai_<module_name>/
├── __init__.py
├── __manifest__.py
├── models/                 # Business logic
│   ├── __init__.py
│   └── <model>.py
├── views/                  # UI definitions
│   └── <model>_views.xml
├── security/               # Access rights
│   └── ir.model.access.csv
├── data/                   # Default data
├── wizard/                 # Transient models (optional)
├── report/                 # Reports (optional)
└── static/                 # Web assets (optional)
```

#### Commit Message Tags

| Tag | Purpose |
|-----|---------|
| `[IMP]` | Improvement |
| `[FIX]` | Bug fix |
| `[REF]` | Refactoring |
| `[ADD]` | New feature |
| `[REM]` | Removal |
| `[MOV]` | Moving files |
| `[REL]` | Release |
| `[MERGE]` | Merge commit |

**Rule**: Explain WHY, not just what.

#### Documentation Requirements

- Docstrings on all public methods
- Comments only for tricky logic
- Avoid generators/decorators (use Odoo API provided ones)
- Use `filtered`, `mapped`, `sorted` methods

---

## 6. Contributing - Documentation Guidelines

**Source**: [Documentation Guidelines - Odoo 19.0](https://www.odoo.com/documentation/19.0/contributing/documentation.html)

### RST Formatting Standards

For ipai_* module documentation:

```rst
Module Title
============

Introduction paragraph.

Configuration
-------------

Steps to configure.

Usage
-----

How to use the module.

Technical Notes
---------------

Implementation details.
```

### Our Documentation Locations

| Content Type | Location |
|--------------|----------|
| Module docs | `addons/ipai/<module>/doc/` |
| Architecture | `docs/architecture/` |
| Evidence | `docs/evidence/` |
| Data models | `docs/data-model/` |
| Specs | `spec/<feature>/` |

---

## Action Items

### Immediate (Before Next Release)

1. **Audit `read_group` usage** in all ipai_* modules
   ```bash
   grep -r "\.read_group(" addons/ipai/
   ```

2. **Add `@api.private`** to internal methods not intended for RPC

3. **Verify import order** in all Python files

### Documentation Updates

1. Add Odoo 19.0 ORM migration notes to developer onboarding
2. Link official tutorials in contributor guide
3. Document self-hosted parity with Odoo.sh features

### CI Enhancements

1. Add linter check for deprecated `read_group` usage
2. Enforce import order with isort
3. Add docstring coverage check

---

## Sources

- [Developer - Odoo 19.0](https://www.odoo.com/documentation/19.0/developer.html)
- [How-to guides - Odoo 19.0](https://www.odoo.com/documentation/19.0/developer/howtos.html)
- [Tutorials - Odoo 19.0](https://www.odoo.com/documentation/19.0/developer/tutorials.html)
- [Reference - Odoo 19.0](https://www.odoo.com/documentation/19.0/developer/reference.html)
- [ORM API - Odoo 19.0](https://www.odoo.com/documentation/19.0/developer/reference/backend/orm.html)
- [Development - Odoo 19.0](https://www.odoo.com/documentation/19.0/contributing/development.html)
- [Coding Guidelines - Odoo 19.0](https://www.odoo.com/documentation/19.0/contributing/development/coding_guidelines.html)
- [Documentation - Odoo 19.0](https://www.odoo.com/documentation/19.0/contributing/documentation.html)
- [Odoo.sh Features](https://www.odoo.sh/features)
- [OCA Contributing Guide](https://github.com/OCA/odoo-community.org/blob/master/website/Contribution/CONTRIBUTING.rst)
