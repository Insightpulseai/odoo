# Odoo 19 Repo Mirroring & Taxonomy

> **Date**: 2026-02-17
> **Spec**: `spec/ee-oca-parity/constitution.md`

---

## Official odoo/odoo Root Tree (19.0)

The upstream `odoo/odoo` repo (branch 19.0) has this root structure:

```
.github/
addons/          # ~608 CE-native modules
debian/
doc/cla/
odoo/            # Server source (runtime, CLI, ORM)
setup/
.gitignore
.weblate.json
CONTRIBUTING.md
COPYRIGHT
LICENSE
MANIFEST.in
README.md
SECURITY.md
odoo-bin         # Entry point
requirements.txt
ruff.toml
setup.cfg
setup.py
```

Our repo mirrors the Odoo-native directories (`addons/`, `odoo/`, `odoo-bin`) and adds
platform surfaces that do not exist upstream.

---

## Taxonomy

| Term | Definition | Directory | Has `__manifest__.py` |
|------|-----------|----------|----------------------|
| **Module / Addon** | Folder with `__manifest__.py` that Odoo loads via `addons_path` | `addons/` | Yes |
| **Parity Addon** | OCA addon replacing an EE-only module | `addons/oca/<repo>/` | Yes |
| **Meta-module** | Dependency-only addon for "install as one" bundling | `addons/ipai/ipai_bundle_*/` | Yes (deps only) |
| **Thin Connector** | Small Odoo addon (<1000 LOC) wiring Odoo ↔ Bridge | `addons/ipai/ipai_*/` | Yes |
| **Integration Bridge** | External service replacing an EE capability | `bridges/` or `services/` | No |

### Key Distinctions

- A **Parity Addon** is always an OCA module. Never custom `ipai_*` code claiming EE module parity.
- A **Meta-module** is allowed for single-install bundling. It is not a parity replacement;
  it is a packaging mechanism. Contains only `__init__.py` + `__manifest__.py` with `depends`.
- A **Bridge** is never an Odoo module. It runs as a separate container/service.
- A **Thin Connector** wires Odoo to a Bridge. It has no business logic, only API client /
  webhook sink / auth handoff. <1000 LOC Python.

---

## Addons Path Ordering

Odoo loads addons from `addons_path` in order. Override precedence goes last-wins.

```
addons_path = /odoo/addons,/addons/oca,/addons/ipai,/addons
```

| Priority | Path | Contents |
|----------|------|----------|
| 1 (base) | `/odoo/addons` | Odoo CE core addons (~608 modules) |
| 2 | `/addons/oca` | OCA parity addons (EE replacements) |
| 3 | `/addons/ipai` | IPAI thin connectors + meta-modules |
| 4 (override) | `/addons` | Any root-level addons (ipai_* currently here) |

---

## Container Layering

```
┌─────────────────────────────────────────────┐
│ [odoo-web] Odoo 19 CE server                │
│   ├─ loads: CE core addons                  │
│   ├─ loads: OCA parity addons               │
│   ├─ loads: IPAI thin connector addons      │
│   └─ talks to bridges via HTTP/RPC/webhooks │
├─────────────────────────────────────────────┤
│ [bridge-*] Non-module EE gaps (services)    │
│   ├─ bridge-ocr (document digitization)     │
│   ├─ bridge-runner (jobs/queues)            │
│   ├─ bridge-n8n (automation/orchestration)  │
│   └─ bridge-superset (BI/reporting)         │
├─────────────────────────────────────────────┤
│ [data] PostgreSQL 16, Redis, object storage │
└─────────────────────────────────────────────┘
```

---

## What Our Repo Adds (vs Upstream)

Our repo is a platform monorepo. These top-level directories do NOT exist in upstream
`odoo/odoo` and never will:

| Directory | Purpose | Odoo-related? |
|-----------|---------|---------------|
| `agents/` | Agent skills, capabilities, prompts | No |
| `bridges/` / `services/` | Integration bridges (non-module) | Indirect (wired via connectors) |
| `infra/` | Terraform, Docker, DNS, deploy | No |
| `automations/` | n8n workflow definitions | No |
| `apps/` / `api/` / `clients/` | App surfaces, SDKs | No |
| `.supabase/` / `db/` | Database configs (Supabase for non-Odoo) | No |
| `mcp/` / `memory/` | MCP servers, agent memory | No |
| `spec/` | Spec Kit bundles (governance) | Indirect |
| `docs/` | Documentation | Indirect |
| `scripts/` | Tooling, CI helpers | Indirect |

These directories are governed by their own SSOT rules and do not participate in
Odoo's `addons_path`.

---

## Merge-to-Main Policy

See `spec/ee-oca-parity/constitution.md` Principle 6 for the full policy.

| Stage | Tier Required | What Gets Activated |
|-------|--------------|---------------------|
| PR branch | T1 (Mapped) | Nothing installed |
| main | T2 (Installable) | Nothing activated by default |
| Staging | T3 (Functional) | Activated via `ipai_bundle_*` meta-modules |
| Production | T4 (Verified) | Same bundle modules as staging |

---

*Referenced by: `spec/ee-oca-parity/constitution.md`, `spec/ee-oca-parity/prd.md`*
