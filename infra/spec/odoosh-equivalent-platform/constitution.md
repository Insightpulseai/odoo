# Odoo.sh-Equivalent Platform — Constitution

**Version**: 1.0.0
**Status**: Draft
**Last Updated**: 2026-03-11
**Owner**: InsightPulse AI Platform Team

---

## Purpose

This spec defines the **non-negotiable rules and capability boundaries** for a self-hosted platform that replaces Odoo.sh functionality. It governs personas, capability taxonomy, environment promotion, and governance boundaries for platform operations.

### What This Is

- A **platform capability doctrine** for Odoo.sh-equivalent operations
- A **persona-based governance model** defining who can do what
- A **capability taxonomy** consumed by implementation specs in `odoo/`

### What This Is Not

- Not the Odoo runtime implementation (that lives in `odoo/` spec bundles)
- Not a clone of Odoo.sh UI or UX (adapted for self-hosted + CLI-first)
- Not an Azure-specific benchmark (that lives in `azure-platform-maturity-benchmark/`)

---

## Non-Negotiables

### 1. Platform Doctrine Owns Capabilities, Odoo Consumes Them

This spec defines **what capabilities must exist**. The `odoo/` spec bundles define **how they are implemented** in the Odoo runtime. This boundary is permanent.

### 2. Four Canonical Personas

The platform recognizes exactly four operator personas. All capability packs are scoped to these personas. New personas require a constitution amendment.

| Persona | Primary Concern | Governance Scope |
|---------|----------------|-----------------|
| Developer | Ship features fast with confidence | Code, branches, feature envs, logs, shell |
| Tester (QA) | Validate behavior matches spec | Staging access, test execution, diff review |
| Project Manager | Track readiness and release gates | Dashboards, deployment history, promotion visibility |
| System Administrator | Maintain platform health and security | Full access, backups, DNS, monitoring, secrets |

### 3. Environment Tiers Are Fixed

| Tier | Git Trigger | Persistence | Access |
|------|------------|-------------|--------|
| Development | Feature branch push | Ephemeral (auto-cleanup after 7d idle) | Developer, Tester |
| Staging | PR to main | Semi-persistent (lives with PR) | All personas |
| Production | Merge to main + promotion gate | Permanent | SysAdmin (write), all (read) |

### 4. CLI/API-First, UI-Second

Every platform operation must be executable via CLI or API. A web UI may exist for convenience but must never be the only path to any operation.

### 5. No Odoo.sh Vendor Lock-in

The platform must run on any container-capable infrastructure. Current target: Azure ACA + Cloudflare + GitHub Actions. Previous target: DigitalOcean. The architecture must not hard-depend on a single cloud provider.

### 6. Capability Packs Are Additive

New capabilities may be added to persona packs. Existing capabilities may not be removed without a constitution amendment. Capability deprecation requires a 30-day notice period.

### 7. Secrets Never in Platform Config

Platform configuration files (YAML, JSON, Terraform) may reference secret **names** but never secret **values**. Runtime secret injection only.

---

## Governance

- Owned by `infra/` as upstream platform doctrine
- Consumed by `odoo/` for ERP-specific implementation
- Changes require constitution amendment PR with explicit rationale
- Persona definitions are frozen until v2.0
