# Finance PPM — Constitution

> **Spec bundle**: `spec/finance-ppm/`
> **Module**: Finance PPM (Project Portfolio Management)
> **Version**: 1.0.0
> **Date**: 2026-02-16

---

## Non-Negotiable Rules

### Rule 1: Parity Order (CE → OCA → Delta → Bridge)

Every capability in Finance PPM must be resolved by the **lowest layer possible**.
Step-ups require a decision record with evidence.

```
Layer 1: CE native / configuration
  ↓ (only if CE cannot express the capability)
Layer 2: OCA add-on (19.0 series, verified installable)
  ↓ (only if no OCA module covers it for Odoo 19)
Layer 3: Minimal ipai_* delta module
  ↓ (only if the gap is inherently service/platform-based, not module-based)
Layer 4: Platform bridge (n8n workflow, external API, infra substitute)
```

**Evidence requirement for step-ups**:

| Step-up | Required evidence |
|---------|-------------------|
| CE → OCA | CE config attempt + why it was insufficient |
| OCA → Delta | OCA module search result + why no 19.0 module covers it |
| Delta → Bridge | Explanation that the gap is platform/service-level, not module-level |

Decision records live in `spec/finance-ppm/decisions/` (ADR format).

### Rule 2: Module Replacements ≠ Platform Bridges

These are two distinct problem classes. Never conflate them.

| Problem class | Definition | Examples |
|--------------|------------|----------|
| **Module replacement** | EE add-on → CE config / OCA add-on / ipai_* delta | `project_task_dependency`, `project_timeline`, `purchase_requisition` |
| **Platform bridge** | EE platform service → external infra/workflow/API | Odoo.sh → DO+Docker, IAP OCR → external OCR+n8n, IAP AI → Claude API |

A platform bridge is **never** an OCA module. An OCA module is **never** a platform bridge.
The authoritative mapping lives in `spec/finance-ppm/parity_map.yaml`.

### Rule 3: No Unverified Capability Claims

Do not claim a capability is "solved" or "available" unless:

1. The module/bridge is **installed and tested** on Odoo 19 CE, or
2. The claim explicitly states the verification status (e.g., "unverified for 19.0")

Specific guardrails:

- **Gantt view**: OCA `project_timeline` provides a **timeline visualization**, not a full Gantt chart. Do not claim "Gantt" unless the module provides interactive Gantt with drag-and-drop resource allocation.
- **Critical path**: OCA `project_timeline_critical_path` is verified only for older series (≤14.0). Do not claim critical-path highlighting for Odoo 19 unless independently verified and evidenced.
- **Resource leveling**: Not available in any CE/OCA module. Do not claim availability.

### Rule 4: Team Directory Invariants

The 9-person finance team is immutable without a spec change:

- **Headcount**: exactly 9
- **Tier counts**: Director=1, Senior Manager=1, Manager=1, Analyst=6
- **JPAL**: must be Finance Analyst (never Finance Supervisor)
- **Uniqueness**: Code unique, Name unique
- **Cross-artifact parity**: `team_directory.csv` = EMPLOYEES dict in import scripts

Enforced by `scripts/finance/validate_team_directory.py` + CI gate.

### Rule 5: Seed Data SSOT

All seed data lives under `data/seed/finance_ppm/tbwa_smp/`.
Superseded variants go to `data/archive/finance_ppm/tbwa_smp/<YYYYMMDD>/` with `MANIFEST.md`.
No duplicate seed data may exist outside canonical/archive.

Enforced by `scripts/finance/validate_seed_ssot.py` + CI gate.

### Rule 6: Parity Map Is the Contract

`spec/finance-ppm/parity_map.yaml` is the machine-readable, diffable contract
for which layer solves each capability. Every delta or bridge entry must have:

1. A decision record in `spec/finance-ppm/decisions/`
2. An evidence pointer in `docs/evidence/` or inline verification

Enforced by `scripts/policy/validate_parity_map.py` + CI gate.

---

## Guardrails

### CE Extension vs OCA vs Delta vs Bridge

| Layer | What it is | What it is NOT |
|-------|-----------|----------------|
| **CE extension** | Built-in Odoo configuration, views, actions, server actions, automated actions | A custom Python module |
| **OCA add-on** | A community module from github.com/OCA, verified for 19.0 series | A fork, a personal repo module, an unported module |
| **ipai_* delta** | A custom module in `addons/ipai/` that fills a gap CE+OCA cannot | A reimplementation of an EE module; a bridge |
| **Platform bridge** | An infra/workflow/API substitute for a platform-level EE service | An Odoo module; an OCA add-on; anything installable via `ir.module.module` |

### Forbidden Claims

- "All EE modules have OCA equivalents" — false; some gaps are platform-level
- "Critical path analysis solved" — unverified for Odoo 19; use "timeline visualization available"
- "Full Gantt support" — OCA `project_timeline` is a timeline, not a full Gantt
- "Enterprise parity achieved" — parity is explicitly tiered (CE/OCA/Delta/Bridge), not binary
- ">=80% EE parity" — only valid with explicit denominator and exclusion list

### Bridge Directory

Platform bridges live in `platform/bridges/<bridge-name>/`, **not** in `addons/`.
Each bridge folder contains:

```
platform/bridges/<bridge-name>/
├── README.md          # Contract: inputs, outputs, failure modes
├── workflow.json      # n8n workflow (if applicable)
├── env.example        # Required env vars (no secrets)
├── schemas/           # Payload contracts (JSON Schema)
└── evidence.md        # Links to docs/evidence/...
```

---

## Constraints Catalog

### Environment: Claude Code Web

- No Docker/containers, apt/brew, systemctl, sudo
- File edits, git operations, CI workflow generation, remote API calls: allowed
- Capabilities verified in `agents/capabilities/manifest.json`

### Odoo

- CE 19.0 only — no Enterprise modules, no odoo.com IAP
- Databases: `odoo` (prod), `odoo_dev` (local) — only 2
- Prefer `addons/` modules + `scripts/odoo_*.sh` wrappers
- Every task produces: (1) module changes, (2) install/update script, (3) health check

### Naming

- Custom modules: `ipai_<domain>_<feature>` (e.g., `ipai_finance_ppm`)
- Platform bridges: `platform/bridges/<kebab-case-name>/`
- Spec bundles: `spec/<feature-slug>/`

---

*Constitution v1.0.0 — 2026-02-16*
