# Odoo 18 Developer Skills Index

> **Extracted**: 2026-02-17
> **Source**: [odoo/documentation](https://github.com/odoo/documentation) branch `18.0`
> **Total Skills**: 19
> **Total Lines**: ~16,500

---

## Overview

These skills are distilled from the official Odoo 18 developer documentation into
agent-consumable SKILL.md files. Each file contains key APIs, patterns, code examples,
and conventions for a specific domain.

## Skills by Category

### Backend Development

| Skill | Lines | Focus |
|-------|-------|-------|
| [odoo18-orm](odoo18-orm/SKILL.md) | 1259 | Models, Fields, Recordsets, CRUD, Inheritance, Domains, Environment |
| [odoo18-security](odoo18-security/SKILL.md) | 799 | ACL, Record Rules, Field Access, Groups, Injection Prevention |
| [odoo18-data-files](odoo18-data-files/SKILL.md) | 950 | XML/CSV Records, External IDs, Templates, Shortcuts |
| [odoo18-actions](odoo18-actions/SKILL.md) | 861 | Window, Server, Report, Client, URL, Scheduled Actions |
| [odoo18-testing](odoo18-testing/SKILL.md) | 1363 | Python Tests, HOOT JS Framework, Tours, Performance |
| [odoo18-http-controllers](odoo18-http-controllers/SKILL.md) | 605 | Controllers, Routing, Request/Response, JsonRPC |
| [odoo18-performance](odoo18-performance/SKILL.md) | 517 | Profiling, Batch Operations, Indexes, Optimization |
| [odoo18-reports](odoo18-reports/SKILL.md) | 710 | QWeb Reports, PDF, Paper Formats, Custom Reports |
| [odoo18-module](odoo18-module/SKILL.md) | 673 | Module Structure, Manifest, Dependencies, Hooks |
| [odoo18-mixins](odoo18-mixins/SKILL.md) | 1061 | mail.thread, Activities, Website, UTM, Rating |

### Frontend Development

| Skill | Lines | Focus |
|-------|-------|-------|
| [odoo18-frontend](odoo18-frontend/SKILL.md) | 1265 | Framework Architecture, Registries, Services, Hooks, Patching |
| [odoo18-owl-components](odoo18-owl-components/SKILL.md) | 918 | Dropdown, SelectMenu, Notebook, Pager, TagsList |
| [odoo18-qweb](odoo18-qweb/SKILL.md) | 897 | Template Directives, Inheritance, Python vs JS |
| [odoo18-assets](odoo18-assets/SKILL.md) | 594 | Bundles, Lazy Loading, ir.asset, Operations |

### DevOps & Infrastructure

| Skill | Lines | Focus |
|-------|-------|-------|
| [odoo18-cli](odoo18-cli/SKILL.md) | 845 | odoo-bin Commands, DB/Module/i18n Management |
| [odoo18-external-api](odoo18-external-api/SKILL.md) | 670 | JSON-2 API, Authentication, Transactions |
| [odoo18-upgrade](odoo18-upgrade/SKILL.md) | 776 | Migration Scripts, Phases, Upgrade Utils |

### Contributing & Conventions

| Skill | Lines | Focus |
|-------|-------|-------|
| [odoo18-coding-guidelines](odoo18-coding-guidelines/SKILL.md) | 1095 | Python/XML/JS/SCSS Conventions, File Naming |
| [odoo18-git-guidelines](odoo18-git-guidelines/SKILL.md) | 621 | Commit Tags, Message Format, Branch Naming |

---

## Usage

Each SKILL.md has YAML frontmatter with:
- `name` — skill identifier
- `description` — one-line description for agent matching
- `metadata.version` — always `"18.0"`
- `metadata.source` — path to source RST file(s)
- `metadata.extracted` — extraction date

## Source Mapping

| RST Path | Skill |
|----------|-------|
| `developer/reference/backend/orm.rst` | odoo18-orm |
| `developer/reference/backend/security.rst` | odoo18-security |
| `developer/reference/backend/data.rst` | odoo18-data-files |
| `developer/reference/backend/actions.rst` | odoo18-actions |
| `developer/reference/backend/testing.rst` | odoo18-testing |
| `developer/reference/backend/http.rst` | odoo18-http-controllers |
| `developer/reference/backend/performance.rst` | odoo18-performance |
| `developer/reference/backend/reports.rst` | odoo18-reports |
| `developer/reference/backend/module.rst` | odoo18-module |
| `developer/reference/backend/mixins.rst` | odoo18-mixins |
| `developer/reference/frontend/framework_overview.rst` | odoo18-frontend |
| `developer/reference/frontend/owl_components.rst` | odoo18-owl-components |
| `developer/reference/frontend/qweb.rst` | odoo18-qweb |
| `developer/reference/frontend/assets.rst` | odoo18-assets |
| `developer/reference/frontend/unit_testing.rst` | odoo18-testing |
| `developer/reference/frontend/unit_testing/hoot.rst` | odoo18-testing |
| `developer/reference/cli.rst` | odoo18-cli |
| `developer/reference/external_api.rst` | odoo18-external-api |
| `developer/reference/upgrades/upgrade_scripts.rst` | odoo18-upgrade |
| `developer/reference/upgrades/upgrade_utils.rst` | odoo18-upgrade |
| `contributing/development/coding_guidelines.rst` | odoo18-coding-guidelines |
| `contributing/development/git_guidelines.rst` | odoo18-git-guidelines |

---

*Generated from odoo/documentation@18.0 — see `spec/skill-intake-anthropic/` for governance.*
