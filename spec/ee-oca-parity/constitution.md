# EE-OCA Parity Constitution

> **Version**: 1.1.0
> **Ratified**: 2026-02-17
> **Last Amended**: 2026-02-17

---

## Governing Principles

### Principle 1: Strict Taxonomy — Module vs Bridge vs Connector

**Statement**: Every component that closes an EE gap must be classified into
exactly one of three categories. No component may blur these boundaries.

**Definitions**:

| Category | What it is | Lives in | Has `__manifest__.py` | On `addons_path` |
|----------|-----------|----------|----------------------|-------------------|
| **Parity Addon** | OCA module replacing an EE-only *module* | `addons/oca/<repo>/` | Yes | Yes |
| **Integration Bridge** | Non-module service closing an EE-only *capability* gap | `bridges/` or `services/` | No | No |
| **Thin Connector** | Minimal Odoo addon wiring Odoo ↔ a bridge service | `addons/ipai/<name>/` | Yes | Yes |

**Rules**:
- A **Parity Addon** is always an OCA module. Never custom code claiming EE parity.
- An **Integration Bridge** is never installed via Odoo Apps. It runs as an external service.
- A **Thin Connector** is <1000 LOC, has no business logic, only API client/webhook sink/auth handoff.
- A Thin Connector is **never** called a "parity module". It is an adapter.

**Enforcement**:
- CI gate `scripts/ci/check_parity_boundaries.sh` rejects PRs that violate placement rules.
- Any `addons/ipai/*` module >1000 LOC Python triggers a review flag.

---

### Principle 2: Evidence Tiers — Mapping ≠ Parity

**Statement**: A mapping (module X replaces EE module Y) is evidence, not proof
of functional parity. Parity claims must progress through four tiers.

**Evidence Tiers**:

| Tier | Name | Meaning | Proof Required |
|------|------|---------|----------------|
| T0 | **Unmapped** | No replacement identified | — |
| T1 | **Mapped** | OCA/bridge replacement identified and OCA repo verified to exist | OCA repo exists on GitHub, module name documented |
| T2 | **Installable** | Replacement installs on our Odoo 19 CE baseline without errors | `odoo-bin -i <module> --stop-after-init` exits 0 |
| T3 | **Functional** | Replacement covers ≥80% of EE feature surface for our workflows | QA checklist signed off per domain |
| T4 | **Verified** | Production-tested, monitored, with rollback plan | 30-day soak in staging + production deploy |

**Current state**: The 151-module mapping is **Tier 1** (Mapped). It proves a
replacement *exists* for every EE module. It does not prove installability, UX
parity, or production readiness.

**Enforcement**:
- `reports/ee_oca_parity_proof.json` tracks tier per module.
- CI blocks any PR that claims tier > T1 without matching evidence artifacts.
- Tier promotions require evidence in `docs/evidence/<date>/parity/`.

---

### Principle 3: OCA First — Config → OCA → Bridge → Delta

**Statement**: The replacement strategy hierarchy is strict and non-negotiable.

**Hierarchy** (try each before the next):

```
1. Config        — Built-in Odoo CE configuration
2. OCA           — Vetted OCA community module
3. Bridge        — External service + thin connector
4. Delta (ipai)  — Custom ipai_* module (LAST RESORT)
```

**Rules**:
- No `ipai_*` module may be created if an OCA module covers ≥70% of the need.
- No custom Odoo module may be created to achieve "EE module parity". That is OCA's job.
- `ipai_*` modules are thin connectors or localization glue. Never feature modules.
- Every `ipai_*` module must reference the OCA gap it fills in its `__manifest__.py` description.

**Enforcement**:
- New `addons/ipai/*` directories require approval in PR description citing OCA gap.
- `scripts/ci/check_parity_boundaries.sh` verifies naming and placement.

---

### Principle 4: Directory Boundaries Are Law

**Statement**: File placement determines component classification. There are no
exceptions. If something is in the wrong directory, it is wrong.

**Directory Rules**:

```
addons/
├── oca/                    # OCA modules ONLY (parity addons)
│   └── <oca-repo-name>/   # e.g., account-financial-tools/
│       └── <module>/       # e.g., account_asset_management/
├── ipai/                   # IPAI thin connectors ONLY
│   └── ipai_<name>/       # e.g., ipai_doc_ocr_bridge/
├── _deprecated/            # Archived modules pending removal
└── (CE addons here if not using upstream subtree)

bridges/                    # Integration bridges — NON-module services
├── ocr/                    # Document digitization / OCR
├── deploy/                 # Build/deploy runners (Odoo.sh replacement)
├── sms/                    # SMS gateway (Twilio, etc.)
└── <service>/              # Any external service adapter

services/                   # Alternative name for bridges/ (alias)
```

**What must NOT be in `addons/`**:
- Docker/compose files
- n8n workflow definitions
- Infrastructure/Terraform
- Scripts that are not Odoo modules
- Any directory without `__manifest__.py`

**What must NOT be in `bridges/` or `services/`**:
- Anything with `__manifest__.py`
- Anything that extends `odoo.models.Model`

**Enforcement**:
- CI gate checks every `addons/*` directory has `__manifest__.py`.
- CI gate checks no `bridges/*` directory has `__manifest__.py`.

---

### Principle 5: Parity Scope — Modules vs Capabilities

**Statement**: The EE gap has two parts. They are addressed differently.

| EE Gap Type | Examples | Replacement Via | Directory |
|-------------|----------|-----------------|-----------|
| **EE-only modules** | `helpdesk`, `account_asset`, `planning` | OCA parity addons | `addons/oca/` |
| **EE-only capabilities** | Odoo.sh hosting, IAP OCR, IAP SMS | Integration bridges | `bridges/` |

**Rules**:
- An EE-only *module* is replaced by an OCA addon. Period.
- An EE-only *capability* (non-module) is replaced by an integration bridge. Period.
- A thin connector may exist in `addons/ipai/` to wire Odoo ↔ bridge, but it is
  never the replacement itself — the bridge is.
- The parity report must track modules and capabilities separately.

---

### Principle 6: Merge-to-Main Policy — Installable, Not Activated

**Statement**: Merging OCA parity modules to `main` requires T2 (installable)
status. Merge does not imply activation. Modules are activated explicitly via
environment-specific bundle modules.

**Merge Policy Matrix**:

| Stage | Tier Required | Activation | Who Decides |
|-------|--------------|------------|-------------|
| **PR branch** | T1 (Mapped) | Not installed | CI gate validates mapping |
| **main** | T2 (Installable) | Not installed by default | PR reviewer validates install proof |
| **Staging** | T3 (Functional) | Activated via bundle module | QA validates functional checklist |
| **Production** | T4 (Verified) | Activated via bundle module | Maintainer approves deploy |

**Rules**:
- Merging to `main` proves the module installs cleanly (`odoo-bin -i <module> --stop-after-init` exits 0).
- Merging to `main` does NOT activate the module in any running environment.
- Activation is controlled by **bundle modules**: meta-modules that declare `depends` on a set of OCA modules for a specific environment.
- Auto-upgrade (`-u`) applies ONLY to already-installed modules. New modules are never auto-installed on deploy.
- A module may exist on `main` at T2 indefinitely. There is no pressure to activate.

**Bundle Module Taxonomy**:

```
addons/ipai/
├── ipai_bundle_base/         # Core: contacts, company, base config
├── ipai_bundle_finance/      # Accounting, invoicing, assets, budget
├── ipai_bundle_hr/           # Payroll, expenses, attendance, planning
├── ipai_bundle_projects/     # Project, timesheet, helpdesk
└── ipai_bundle_docs/         # Document management, sign, OCR
```

Bundle modules:
- Are thin `__manifest__.py` files with only `depends` lists
- Contain zero Python code (only `__init__.py` + `__manifest__.py`)
- Are environment-specific: staging may install `ipai_bundle_finance`, production may not yet
- Are the ONLY mechanism for activating OCA parity modules

**Enforcement**:
- CI blocks merge to `main` if any new OCA module lacks T2 install evidence.
- CI blocks any `ipai_bundle_*` module with Python code beyond `__init__.py`.

---

### Principle 7: Staging Contract — T3 Proving Ground

**Statement**: Staging is the exclusive proving ground for T3 (Functional) claims.
No module may claim T3 without passing staging validation. Staging mirrors
production topology.

**Staging Roles**:

| Role | What It Proves |
|------|---------------|
| **Integration checkpoint** | OCA modules, bridges, and connectors work together |
| **Production-like data rehearsal** | Module behaves correctly with realistic (anonymized) data |
| **Upgrade rehearsal** | `odoo-bin -u <module>` succeeds against existing database |
| **Release candidate gate** | Bundle module activates without regression |
| **Rollback confidence** | Deactivation/uninstall path verified |

**Evidence Tier Mapping**:

```
CI Pipeline    → T2 (Installable)     — module installs in isolation
Staging        → T3 (Functional)      — module works in integrated environment
Production     → T4 (Verified)        — module survives 30-day soak
```

**Staging Requirements**:
- Staging runs the same Odoo 19 CE + PostgreSQL 16 stack as production.
- Staging database is a sanitized copy of production (no real credentials, PII anonymized).
- Staging activates modules via the same bundle modules used in production.
- Staging runs the full OCA + bridge + connector stack, not isolated modules.
- Every T3 promotion requires a staging deploy log + functional checklist sign-off.

**Anti-Drift Rules**:
- Staging topology must match production (same Docker images, same `addons_path`, same PostgreSQL version).
- Configuration drift is checked by `scripts/ci/check_staging_drift.sh` (compares staging vs production compose/config).
- Any staging/production divergence blocks T3 promotion.

**Enforcement**:
- No module may be promoted to T3 without staging evidence in `docs/evidence/<date>/parity/<domain>_functional.md`.
- Staging deploy failures are logged and block the corresponding T4 promotion.
- Staging is refreshed from production data at least monthly.

---

## Constraints & Security

| Constraint | Policy |
|------------|--------|
| **Odoo version** | 19.0 CE only. No Enterprise source code. |
| **License** | All addons: LGPL-3.0 or AGPL-3.0. No proprietary. |
| **IAP** | No Odoo IAP dependencies. All replaced by direct API calls. |
| **OCA version** | Must target 19.0 branch (or latest available). |
| **ipai_ naming** | `ipai_<domain>_<feature>` (e.g., `ipai_doc_ocr_bridge`). |
| **Bridge naming** | `bridges/<service>/` (e.g., `bridges/ocr/`). |

---

## Workflow & Quality Gates

1. **Tier promotion**: Requires evidence artifact + PR review.
2. **New ipai_ module**: Requires OCA gap citation in PR description.
3. **Parity report**: Auto-generated weekly by CI; tier tracked per module.
4. **Directory audit**: `scripts/ci/check_parity_boundaries.sh` runs on every PR.

---

## Governance

- **Amendments**: Require PR with rationale; approved by repo maintainer.
- **Dispute resolution**: Refer to `spec/agent/constitution.md` for agent constraints.
- **Enforcement**: CI gates are non-negotiable. Manual overrides require `# parity-override: <reason>` in commit message.

---

## Amendment History

| Version | Date | Change | Author |
|---------|------|--------|--------|
| 1.0.0 | 2026-02-17 | Initial ratification — module/bridge/connector taxonomy, evidence tiers, directory boundaries | claude/agent |
| 1.1.0 | 2026-02-17 | Added Principle 6 (merge-to-main policy, bundle modules) and Principle 7 (staging contract, anti-drift) | claude/agent |
