# Organization Structure & Repo Layout (SSOT)

> **Status**: Enforced by CI (`.github/workflows/org-structure-gate.yml`)
> **Owner**: Platform Engineering
> **Last Updated**: 2026-02-15

This document is the **Single Source of Truth (SSOT)** for the Insightpulseai organization structure and the `odoo` repository layout. All changes to the directory structure must be reflected here first.

---

## 1. Organization Tree

The high-level structure of the `Insightpulseai` GitHub organization:

```text
Insightpulseai/
├── odoo/               # [MONOREPO] Core Odoo Platform (CE + custom modules)
│   ├── addons/         # Custom & Vendored Odoo Addons
│   ├── config/         # Environment Configurations (bases + overlays)
│   ├── docker/         # Container definitions
│   ├── scripts/        # Automation & Tooling
│   ├── tests/          # End-to-end & Integration Tests
│   ├── docs/           # Documentation & Knowledge Base
│   └── spec/           # Functional Specifications
├── platform/           # [FUTURE] Infrastructure as Code (Terraform/K8s)
├── web/                # [FUTURE] Next.js frontend apps (if separated)
└── .github/            # [SHARED] Org-wide workflow templates & policy
```

## 2. Odoo Repository Layout (`Insightpulseai/odoo`)

The `odoo` repository follows a strict monorepo structure.

### Top-Level Directories (Enforced)

| Directory    | Purpose            | Allowed Content                                                        |
| :----------- | :----------------- | :--------------------------------------------------------------------- |
| `addons/`    | Odoo modules       | `ipai_*` (custom), `oca/*` (vendored), `ks_*` (purchased)              |
| `config/`    | Odoo configuration | `odoo.conf` templates, environment overlays (`dev`, `staging`, `prod`) |
| `docker/`    | Docker artifacts   | `Dockerfile`, `entrypoint.sh`, `nginx/`                                |
| `scripts/`   | Automation         | Python/Shell scripts, `dev/`, `ci/`, `ops/` subdirs                    |
| `tests/`     | QA & Testing       | `e2e/` (Playwright), `load/` (Locust), `integration/`                  |
| `docs/`      | Knowledge Base     | `kb/`, `architecture/`, `guides/`, `evidence/`                         |
| `spec/`      | Product Specs      | Functional specs, wireframes, data models                              |
| `agents/`    | AI Agent Config    | `skills/`, `workflows/`, `knowledge/`                                  |
| `templates/` | Scaffolding        | Cookiecutter templates, sample code                                    |
| `.github/`   | CI/CD              | Workflows, actions, issue templates                                    |

### Forbidden Patterns

- ❌ **No Secrets**: `.env` files, `.pem` keys, or credentials in root or subdirs.
- ❌ **No Miscellaneous**: `misc/`, `tmp/`, `temp/`, `old/` at top level.
- ❌ **No Build Artifacts**: `*.pyc`, `__pycache__`, `filestore/`, `dump.sql`.
- ❌ **No Mixed Addons**: `addons/` must be flat or categorized by vendor (OCA/IPAI). No loose files in `addons/`.

## 3. Cross-Repo Contracts

| Contract          | Description                               | Mechanism                |
| :---------------- | :---------------------------------------- | :----------------------- |
| **Org Structure** | This document matches repo state          | `org-structure-gate.yml` |
| **Documentation** | `docs/kb/` is the single source of truth  | `refesh-odoo19-kb` skill |
| **CI/CD**         | `.github/workflows` drives all automation | Branch protection rules  |

## 4. Ownership

| Path          | Owner                | Contact         |
| :------------ | :------------------- | :-------------- |
| `addons/ipai` | Product Engineering  | @product-leads  |
| `addons/oca`  | Platform Engineering | @platform-leads |
| `config/`     | DevOps               | @devops         |
| `docker/`     | DevOps               | @devops         |
| `docs/`       | Tech Writers / AI    | @docs-team      |
| `scripts/`    | Platform Engineering | @platform-leads |

## 5. OKRs / Success Criteria

- **100% Structural Compliance**: CI fails immediately on unapproved top-level directories.
- **Zero Secret Lean**: No secrets committed to main branch (enforced by `trufflehog` or similar).
- **Deterministic CI**: All structure checks run in < 30 seconds.
