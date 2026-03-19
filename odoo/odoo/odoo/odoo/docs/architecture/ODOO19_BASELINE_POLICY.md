# Odoo 19 Baseline Policy

> Platform target, module placement rules, OCA migration policy, and dev environment expectations.
> This document is the Odoo-specific implementation policy, subordinate to the platform target state.

## Authority and Scope

This document is the Odoo-specific implementation policy for the platform.

Higher-order platform architecture, resource ownership, DNS target state, identity model, SSOT/SOR doctrine, CI/CD contract, and hard constraints are defined in:

- `ssot/azure/PLATFORM_TARGET_STATE.md`

If any rule in this document conflicts with the platform target-state document, the platform target-state document prevails.

---

## 1. Platform Target

| Item | Value |
|------|-------|
| Odoo version | 19.0 (Community Edition) |
| Python | 3.12+ |
| PostgreSQL | 16 |
| Node.js | 18+ (frontend assets only) |
| Enterprise modules | Forbidden |
| Odoo.sh / IAP | Forbidden |

Odoo 19 is the sole target. No dual-version support for 18.0. Modules MUST declare `19.0.x.y.z` in their manifest version field.

---

## 2. Operator Workspace Doctrine

### Primary Development Surfaces

| Tool | Purpose | Usage |
|------|---------|-------|
| Claude Code (CLI/Web) | AI-assisted development, code generation, task execution | Primary agent surface |
| VS Code + Devcontainer | Interactive development, debugging, manual exploration | Primary IDE |
| Databricks VS Code | Data engineering, notebook development | Data workloads only |

### Rules

- All Odoo development runs inside `.devcontainer/` — never on the host machine
- Claude Code operates as an execution agent (see `CLAUDE.md` operating contract)
- VS Code extensions are declared in `devcontainer.json` — not manually installed
- No IDE-specific configuration is committed to the repo (`.idea/`, `.vscode/settings.json` are gitignored)

---

## 3. Module Placement Rules

### Three-Layer Addon Model

```
addons/
├── oca/        # OCA community modules (git-aggregated, not tracked)
├── ipai/       # IPAI custom modules (tracked, ship-ready)
└── local/      # Local development modules (tracked, experimental)
```

### Layer Rules

| Layer | Path | Tracked | Modifiable | Purpose |
|-------|------|---------|------------|---------|
| OCA | `addons/oca/` | No (gitignored) | Never modify source | Community modules, hydrated via git-aggregator |
| IPAI | `addons/ipai/` | Yes | Yes | Custom modules with `ipai_*` prefix |
| Local | `addons/local/` | Yes | Yes | Experimental/dev modules, not production |

### Decision Framework

```
Need a capability?
  ├── Built into Odoo CE? → Use config. Done.
  ├── OCA module exists for 19.0? → Add to oca.lock.json. Done.
  ├── OCA module exists for 18.0? → Classify as migration gap. Wait or contribute port.
  └── No OCA module? → Create ipai_* module in addons/ipai/.
```

### IPAI Module Naming

```
ipai_<domain>_<feature>
```

| Domain | Prefix | Examples |
|--------|--------|----------|
| AI | `ipai_ai_*` | `ipai_ai_core`, `ipai_ai_copilot`, `ipai_ai_rag` |
| Finance | `ipai_finance_*` | `ipai_finance_ppm` |
| HR | `ipai_hr_*` | `ipai_hr_payroll_ph` |
| BIR | `ipai_bir_*` | `ipai_bir_tax_compliance` |
| Platform | `ipai_platform_*` | `ipai_platform_workflow` |
| Connectors | `ipai_*_connector` | `ipai_slack_connector` |

---

## 4. OCA Migration Policy

### Status Categories

| Status | Manifest Version | Action |
|--------|-----------------|--------|
| **19.0 ready** | `19.0.x.y.z` | Install and use |
| **18.0 only** | `18.0.x.y.z` | Classify as migration gap — do NOT install |
| **No port** | Not in repo | Track in manifest as desired, wait for community |

### Migration Gap Protocol

When an OCA module is needed but only available for 18.0:

1. Record in `config/addons.manifest.yaml` with status `migration_gap`
2. Do NOT fork and patch the module locally
3. Do NOT copy OCA source into `addons/ipai/`
4. Options:
   - Wait for community port
   - Contribute a port upstream to OCA (preferred)
   - Build a minimal `ipai_*` module that covers the specific gap (last resort)

### OCA AI Modules — Special Policy

The `OCA/ai` repository is non-baseline on 19.0. As of 2026-03-11:

- All 5 OCA AI modules (`ai_oca_bridge`, `ai_oca_bridge_extra_parameters`, `ai_oca_bridge_chatter`, `ai_oca_bridge_document_page`, `ai_oca_native_generate_ollama`) are 18.0 only
- `ipai_ai_core` + `ipai_ai_oca_bridge` (custom) handle provider routing without OCA dependency
- OCA AI modules remain in the manifest for tracking — install when 19.0 ports arrive

---

## 5. Minimum OCA Baseline Modules

These OCA modules are required for the platform baseline (Batch 0):

### 19.0 Ready (Installed)

| Module | Repo | Version | Purpose |
|--------|------|---------|---------|
| `queue_job` | OCA/queue | 19.0.1.1.0 | Background job processing |
| `disable_odoo_online` | OCA/server-brand | 19.0.1.0.0 | Remove Odoo Online references |
| `remove_odoo_enterprise` | OCA/server-brand | 19.0.1.0.0 | Remove EE upsell |
| `mail_debranding` | OCA/server-brand | 19.0.1.0.0 | Remove Odoo branding from mail |

### 18.0 Only (Migration Gap)

| Module | Repo | Version | Purpose |
|--------|------|---------|---------|
| `password_security` | OCA/server-auth | 18.0.1.0.0 | Password policy |
| `auditlog` | OCA/server-tools | 18.0.2.0.7 | Audit trail |
| `base_name_search_improved` | OCA/server-tools | 18.0.1.1.1 | Better name search |
| `date_range` | OCA/server-ux | 18.0.5.0.1 | Reusable date ranges |
| `web_dialog_size` | OCA/web | 18.0.1.0.1 | Dialog sizing |
| `web_environment_ribbon` | OCA/web | 18.0.1.0.3 | Environment indicator |
| `web_m2x_options` | OCA/web | 18.0.1.0.1 | M2x field options |
| `web_responsive` | OCA/web | 18.0.1.0.3 | Responsive backend |
| `report_xlsx` | OCA/reporting-engine | 18.0.1.1.2 | Excel export |

---

## 6. AI-Specific Policy

### Module Hierarchy

```
Layer 0 (no IPAI deps):  ipai_ai_core
Layer 1 (single dep):    ipai_ai_rag → ipai_ai_core
                          ipai_ai_copilot → ipai_ai_widget
Layer 2 (bridge):         ipai_ai_oca_bridge → ipai_ai_core
```

### Rules

- `ipai_ai_core` is the foundation — all AI modules depend on it
- Provider routing goes through `ipai_ai_core`, not direct API calls
- RAG uses Supabase pgvector (external) — Odoo module is a thin adapter
- Copilot tools are Odoo-side declarations — orchestration stays in n8n
- No LLM API calls from Odoo Python code — use bridge/Edge Function pattern

### Odoo 19 AI Compatibility Notes

| Odoo 19 Change | Impact | Resolution |
|----------------|--------|------------|
| `<tree>` → `<list>` | View XML | Use `<list>` in all views |
| `numbercall` removed from `ir.cron` | Cron XML data | Remove field from XML |
| `expand` removed from search `<group>` | Search views | Remove attribute |
| `type="json"` deprecated | Controllers | Use `type="jsonrpc"` |

---

## 7. Dev Container Expectations

### Topology

- **Compose-based** devcontainer with Postgres sidecar
- **Source-mounted** at `/workspaces/odoo`
- **Non-root** user (`vscode`)
- **Cache-persistent** (pip, npm via named volumes)
- **DB-persistent** (Postgres data via named volume)

### Paths

| Path | Purpose |
|------|---------|
| `/workspaces/odoo` | Workspace root |
| `/workspaces/odoo/addons/oca` | OCA modules |
| `/workspaces/odoo/addons/ipai` | IPAI modules |
| `/workspaces/odoo/addons/local` | Local modules |
| `/workspaces/odoo/config/dev/odoo.conf` | Dev runtime config |
| `/workspaces/odoo/scripts/dev/` | Dev scripts |

### What the devcontainer is NOT

- Not a production image
- Not a CI runner
- Not a demo environment
- Not an installer for Odoo source (source is bind-mounted)

---

## 8. Compliance Checks

### Before committing any Odoo module:

```bash
# Manifest version is 19.0.x.y.z
grep -q '"version": "19.0' addons/ipai/<module>/__manifest__.py

# No Enterprise module dependencies
! grep -q 'enterprise' addons/ipai/<module>/__manifest__.py

# No <tree> tags (use <list>)
! grep -rq '<tree' addons/ipai/<module>/views/

# No numbercall in cron data
! grep -rq 'numbercall' addons/ipai/<module>/data/

# Security file exists
test -f addons/ipai/<module>/security/ir.model.access.csv
```

### CI Gate

These checks should be enforced in `.github/workflows/ci-odoo-ce.yml` as part of the standard Odoo CI pipeline.

---

*Last updated: 2026-03-11*
