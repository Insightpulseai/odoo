# Smoke Verification Evidence — ipai_odoo_copilot

> Date: 2026-03-14
> Module: ipai_odoo_copilot (19.0.1.0.0)
> Scope: Compile + structure + security checks (no live runtime)

## Compile Verification

| File | Result |
|------|--------|
| `models/foundry_service.py` | PASS |
| `models/copilot_bot.py` | PASS |
| `models/copilot_audit.py` | PASS |
| `models/res_config_settings.py` | PASS |
| `controllers/main.py` | PASS |

Method: `python3 -m py_compile <file>` — all exit 0.

## Module Structure Verification

| Component | Present | File |
|-----------|---------|------|
| Manifest | Yes | `__manifest__.py` (v19.0.1.0.0) |
| Models init | Yes | `models/__init__.py` (4 imports) |
| Controllers init | Yes | `controllers/__init__.py` |
| Security ACL | Yes | `security/ir.model.access.csv` (3 rows) |
| Settings views | Yes | `views/res_config_settings_views.xml` |
| Audit views | Yes | `views/copilot_audit_views.xml` |
| Partner data | Yes | `data/copilot_partner_data.xml` |
| Config params | Yes | `data/ir_config_parameter.xml` (8 params) |
| Cron job | Yes | `data/ir_cron.xml` (nightly healthcheck) |
| Server action | Yes | `data/ir_actions_server.xml` |
| Tests | Yes | `tests/test_foundry_service.py` (12 cases), `tests/test_res_config_settings.py` (9 cases) |

## Security Verification

| Check | Result |
|-------|--------|
| No hardcoded API keys | PASS — auth via IMDS or env var |
| No client-side credentials | PASS — server-side only |
| HMAC service key validation | PASS — `compare_digest` in controller |
| Read-only mode default | PASS — `foundry_read_only_mode = True` |
| Audit logging | PASS — all paths write `ipai.copilot.audit` |

## Docs Widget Verification

| Check | Result |
|-------|--------|
| Build clean (`vite build`) | PASS |
| TypeScript lint (`tsc --noEmit`) | PASS |
| No API keys in dist/ | PASS |
| No Gemini references in dist/ | PASS |
| Server-side auth only | PASS |

## What This Does NOT Verify

- Live Odoo install (`-i ipai_odoo_copilot --stop-after-init`) — requires devcontainer
- Live Foundry API connectivity — requires Azure credentials
- End-to-end chat flow — requires running Odoo + Foundry
- Evaluation results — no evals have been run yet

## Conclusion

The module is structurally complete, compiles cleanly, and follows security best practices. Full runtime verification requires the devcontainer environment with PostgreSQL and Azure credentials.
