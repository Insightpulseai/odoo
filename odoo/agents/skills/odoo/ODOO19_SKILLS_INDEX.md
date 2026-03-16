# Odoo 19 Developer Skills Index

> **Extracted**: 2026-02-17
> **Source**: [odoo/documentation](https://github.com/odoo/documentation) branch `19.0`
> **Total Skills**: 19
> **Total Lines**: ~16,500

---

## Overview

These skills are distilled from the official Odoo 19 developer documentation into
agent-consumable SKILL.md files. Each file contains key APIs, patterns, code examples,
and conventions for a specific domain.

## Skills by Category

### Backend Development

| Skill | Lines | Focus |
|-------|-------|-------|
| [odoo19-orm](odoo19-orm/SKILL.md) | 1259 | Models, Fields, Recordsets, CRUD, Inheritance, Domains, Environment |
| [odoo19-security](odoo19-security/SKILL.md) | 799 | ACL, Record Rules, Field Access, Groups, Injection Prevention |
| [odoo19-data-files](odoo19-data-files/SKILL.md) | 950 | XML/CSV Records, External IDs, Templates, Shortcuts |
| [odoo19-actions](odoo19-actions/SKILL.md) | 861 | Window, Server, Report, Client, URL, Scheduled Actions |
| [odoo19-testing](odoo19-testing/SKILL.md) | 1363 | Python Tests, HOOT JS Framework, Tours, Performance |
| [odoo19-http-controllers](odoo19-http-controllers/SKILL.md) | 605 | Controllers, Routing, Request/Response, JsonRPC |
| [odoo19-performance](odoo19-performance/SKILL.md) | 517 | Profiling, Batch Operations, Indexes, Optimization |
| [odoo19-reports](odoo19-reports/SKILL.md) | 710 | QWeb Reports, PDF, Paper Formats, Custom Reports |
| [odoo19-module](odoo19-module/SKILL.md) | 673 | Module Structure, Manifest, Dependencies, Hooks |
| [odoo19-mixins](odoo19-mixins/SKILL.md) | 1061 | mail.thread, Activities, Website, UTM, Rating |

### Frontend Development

| Skill | Lines | Focus |
|-------|-------|-------|
| [odoo19-frontend](odoo19-frontend/SKILL.md) | 1265 | Framework Architecture, Registries, Services, Hooks, Patching |
| [odoo19-owl-components](odoo19-owl-components/SKILL.md) | 918 | Dropdown, SelectMenu, Notebook, Pager, TagsList |
| [odoo19-qweb](odoo19-qweb/SKILL.md) | 897 | Template Directives, Inheritance, Python vs JS |
| [odoo19-assets](odoo19-assets/SKILL.md) | 594 | Bundles, Lazy Loading, ir.asset, Operations |

### DevOps & Infrastructure

| Skill | Lines | Focus |
|-------|-------|-------|
| [odoo19-cli](odoo19-cli/SKILL.md) | 845 | odoo-bin Commands, DB/Module/i18n Management |
| [odoo19-external-api](odoo19-external-api/SKILL.md) | 670 | JSON-2 API, Authentication, Transactions |
| [odoo19-upgrade](odoo19-upgrade/SKILL.md) | 776 | Migration Scripts, Phases, Upgrade Utils |

### Contributing & Conventions

| Skill | Lines | Focus |
|-------|-------|-------|
| [odoo19-coding-guidelines](odoo19-coding-guidelines/SKILL.md) | 1095 | Python/XML/JS/SCSS Conventions, File Naming |
| [odoo19-git-guidelines](odoo19-git-guidelines/SKILL.md) | 621 | Commit Tags, Message Format, Branch Naming |

---

## Usage

Each SKILL.md has YAML frontmatter with:
- `name` — skill identifier
- `description` — one-line description for agent matching
- `metadata.version` — always `"19.0"`
- `metadata.source` — path to source RST file(s)
- `metadata.extracted` — extraction date

## Source Mapping

| RST Path | Skill |
|----------|-------|
| `developer/reference/backend/orm.rst` | odoo19-orm |
| `developer/reference/backend/security.rst` | odoo19-security |
| `developer/reference/backend/data.rst` | odoo19-data-files |
| `developer/reference/backend/actions.rst` | odoo19-actions |
| `developer/reference/backend/testing.rst` | odoo19-testing |
| `developer/reference/backend/http.rst` | odoo19-http-controllers |
| `developer/reference/backend/performance.rst` | odoo19-performance |
| `developer/reference/backend/reports.rst` | odoo19-reports |
| `developer/reference/backend/module.rst` | odoo19-module |
| `developer/reference/backend/mixins.rst` | odoo19-mixins |
| `developer/reference/frontend/framework_overview.rst` | odoo19-frontend |
| `developer/reference/frontend/owl_components.rst` | odoo19-owl-components |
| `developer/reference/frontend/qweb.rst` | odoo19-qweb |
| `developer/reference/frontend/assets.rst` | odoo19-assets |
| `developer/reference/frontend/unit_testing.rst` | odoo19-testing |
| `developer/reference/frontend/unit_testing/hoot.rst` | odoo19-testing |
| `developer/reference/cli.rst` | odoo19-cli |
| `developer/reference/external_api.rst` | odoo19-external-api |
| `developer/reference/upgrades/upgrade_scripts.rst` | odoo19-upgrade |
| `developer/reference/upgrades/upgrade_utils.rst` | odoo19-upgrade |
| `contributing/development/coding_guidelines.rst` | odoo19-coding-guidelines |
| `contributing/development/git_guidelines.rst` | odoo19-git-guidelines |

---

*Generated from odoo/documentation@19.0 — see `spec/skill-intake-anthropic/` for governance.*
