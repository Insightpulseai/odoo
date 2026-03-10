# INTEGRATIONS_POLICY.md — Supabase Integration Acceptance Policy

> **Rule**: The integrations matrix (`reports/supabase_feature_integration_matrix.json`)
> is **script-populated**. Do not hand-edit `integrations.*` or `machine_autodetection`.
> Use `scripts/audit_supabase_integrations.py` to reflect integration changes.

---

## 1. Integration Lanes

| Lane ID | Lane Name | Description | Approved Integrations |
|---------|-----------|-------------|----------------------|
| `deployment_hosting` | Deployment / Hosting | Services that host or serve the application | Vercel (ops-console, ai-control-plane) |
| `automation_workflows` | Automation / Workflows | Event-driven orchestration and job queues | n8n (canonical automation engine) |
| `auth_providers` | Auth Providers | Identity and session management | Supabase Auth (primary); OIDC via `ipai_auth_oidc` |
| `data_ops_sync` | Data Ops / Sync | ETL, CDC, and data pipeline integrations | GitHub Actions (CI-driven sync) |
| `cms_admin` | CMS / Admin | Content management and back-office UI | None (Odoo backend serves this role) |
| `observability` | Observability | Metrics, traces, logs, alerting | DigitalOcean monitoring (DO droplet) |
| `templates` | Templates / Accelerators | Starter templates and boilerplate | None active |

---

## 2. Acceptance Criteria

A PR adding an integration to any lane **MUST** include all of the following:

1. **Lane classification**: Declare which lane the integration belongs to.
2. **Purpose + scope**: One sentence describing the integration and what it replaces or augments.
3. **Data contract**: Which Supabase tables are read/written; RLS implications; new tables needed.
4. **Secret handling**: Where credentials live (Supabase Vault key name, GitHub Actions secret name).
   Values must **never** appear in committed files.
5. **Exit plan**: How to remove the integration if it no longer provides value (cleanup steps).
6. **Evidence signal**: Add a file, workflow name, or `package.json` dep so that
   `scripts/audit_supabase_integrations.py --repo` detects the integration automatically.
   **Do not hand-edit the matrix** — the detection script will populate it on next run.
7. **Primitive gap justification**: Reference the threshold in `MAXIMIZE_FEATURES.md §1`
   that this integration crosses.

---

## 3. Forbidden Patterns

| Pattern | Reason |
|---------|--------|
| Direct Cloudflare/Supabase dashboard schema edits | Bypasses migration history; breaks `supabase db push` |
| Hardcoding credentials in n8n workflow JSON | Secrets would be committed to repo |
| Bypassing Edge Function adapter layer for Supabase mutations | Creates undocumented write paths |
| Hand-editing `reports/supabase_feature_integration_matrix.json` `integrations.*` | Must be script-populated; manual edits are overwritten on next audit run |
| Adding `supabase.com` IAP calls | CE-only invariant; violates `docs/architecture/REPO_MAP.md` §9 rule 1 |
| Re-introducing deprecated integrations (Mailgun, Mattermost, Affine) | See `docs/architecture/INDEX.json` deprecated section |

---

## 4. Approved Integrations (Active)

### Vercel — `deployment_hosting`
- **Purpose**: Hosts Next.js apps (ops-console, ai-control-plane, odoo-frontend-shell)
- **Secret handling**: `VERCEL_TOKEN` in GitHub Actions secrets; `vercel.json` has no values
- **Evidence signal**: `vercel.json` at app roots + `.github/workflows/*vercel*.yml`

### n8n — `automation_workflows`
- **Purpose**: Canonical automation engine; webhook bridges between Supabase/Odoo/Slack
- **Secret handling**: n8n credentials store (not in repo); `N8N_*` env vars in DO droplet
- **Evidence signal**: `automations/n8n/workflows/` directory + `infra/*/n8n*`

### GitHub Actions — `data_ops_sync`
- **Purpose**: CI/CD pipelines, Supabase migration push, schema drift checks
- **Secret handling**: GitHub Actions repository secrets (`SUPABASE_ACCESS_TOKEN`, etc.)
- **Evidence signal**: `.github/workflows/supabase-*.yml`

### Supabase Auth / OIDC — `auth_providers`
- **Purpose**: User identity; OIDC relay to Odoo via `ipai_auth_oidc`
- **Secret handling**: Supabase JWT secret managed by Supabase; `SUPABASE_SERVICE_ROLE_KEY` in CI
- **Evidence signal**: `addons/ipai/ipai_auth_oidc/`

---

## 5. Evaluation Queue

Integrations under consideration before approval:

| Integration | Lane | Status | Owner | Notes |
|-------------|------|--------|-------|-------|
| (none active) | — | — | — | — |

To propose an integration, open a PR adding a row here with `Status: proposed` and
include a draft of the acceptance criteria checklist (§2).

---

## 6. Autodetection Refresh

```bash
# Reflect integration changes in the matrix
python scripts/audit_supabase_integrations.py --repo

# Also detect machine-level tools/services
python scripts/audit_supabase_integrations.py --machine
```

Outputs:
- `docs/supabase/integrations_detected.json` — repo evidence (CI-safe, commit-worthy)
- `docs/supabase/machine_integrations_detected.json` — machine evidence (local only; gitignored)
- `reports/supabase_feature_integration_matrix.json` — updated `integrations.*` and `machine_autodetection`

---

*Last updated: 2026-02-23 | See `docs/supabase/MAXIMIZE_FEATURES.md` for primitive utilization.*
