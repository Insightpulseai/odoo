# GitHub App Permission Audit — Insightpulseai Org

> **Generated**: 2026-03-05
> **Source**: `gh api orgs/Insightpulseai/installations` + `ssot/github/apps/*.yaml`
> **CI Guard**: `.github/workflows/github-app-ssot-guard.yml`

---

## Executive Summary

**10 third-party apps** + **1 custom app** (pulser-hub) installed on the Insightpulseai org.

| Risk Level | Count | Apps |
|------------|-------|------|
| Over-permissioned | 3 | cursor, figma, slack |
| Acceptable | 7 | claude, databricks, chatgpt-codex-connector, azure-boards, vercel, cloudflare-workers-and-pages, supabase |
| Custom (needs review) | 1 | pulser-hub |

**All apps** use `repository_selection: all` (installed on all repos). Consider restricting to `selected` for apps that only need access to specific repos.

---

## pulser-hub (Custom App)

**App ID**: 2191216 | **Owner**: Insightpulseai

### Current vs Recommended Permissions

| Permission | Current | Recommended | Rationale |
|------------|---------|-------------|-----------|
| `checks` | write | **write** | Needed for check_run evidence |
| `contents` | write | **read** | Push events don't need write. Downgrade. |
| `issues` | write | **write** | Issue sync and comment posting |
| `metadata` | read | **read** | Required by all apps |
| `pull_requests` | write | **write** | Agent PR creation |
| `repository_hooks` | write | **remove** | Webhook configured at App level, not needed |
| `workflows` | write | **remove** | Not triggering workflow_dispatch |

### Action Items
1. **Downgrade** `contents` from `write` to `read`
2. **Remove** `repository_hooks:write` and `workflows:write`
3. **Fix webhook URL** from deprecated `.net` to Supabase Edge Function
4. **Revoke** unused OAuth client secret (Nov 2025)

---

## Third-Party Apps — Permission Analysis

### Minimal Permissions (Acceptable)

**databricks** — 3 permissions, 0 events
- `contents:write`, `metadata:read`, `workflows:write`
- Assessment: Minimal for Git integration. Acceptable.

**supabase** — 6 permissions, 3 events
- `actions:write`, `checks:write`, `contents:read`, `metadata:read`, `pull_requests:write`, `workflows:write`
- Assessment: `contents:read` is good least-privilege. Acceptable.

### Standard Permissions (Acceptable)

**claude** — 8 permissions, 17 events
- Assessment: Standard for AI coding assistant. `workflows:write` needed for CI triggers.

**chatgpt-codex-connector** — 8 permissions, 12 events
- Assessment: `actions:write` broader than typical. Review if `read` suffices.

**azure-boards** — 9 permissions, 6 events
- Assessment: `actions:write`, `contents:write` broader than needed for board sync. Standard for Microsoft's app.

**vercel** — 10 permissions, 12 events
- Assessment: `administration:write`, `repository_hooks:write` needed for auto-deploy webhook setup.

**cloudflare-workers-and-pages** — 6 permissions, 2 events
- Assessment: `administration:write` needed for webhook setup on deploy. Minimal event subscription.

### Over-Permissioned (Review Recommended)

**cursor** — 13 permissions, 10 events
- Unnecessary: `members:read`, `packages:read`, `pages:read`, `discussions:write`
- Action: These permissions are set by Cursor Inc. Cannot be reduced without uninstalling.
- Mitigation: Monitor for scope changes via weekly drift check.

**figma** — 8 permissions, 1 event
- Unnecessary: `administration:write` is excessive for design-to-code sync
- Action: Cannot reduce third-party app permissions individually.
- Mitigation: Consider restricting `repository_selection` to specific repos.

**slack** — 12 permissions, 22 events
- Broadest scope: `deployments:write`, `actions:write`, `contents:write`
- Assessment: Standard for Slack's comprehensive GitHub integration.
- Mitigation: This is Slack's default scope. Cannot reduce without feature loss.

---

## Recommendations

### Immediate Actions
1. **Fix pulser-hub webhook URL** — Update from `.net` to Supabase Edge Function
2. **Downgrade pulser-hub `contents`** — `write` → `read`
3. **Remove unused pulser-hub permissions** — `repository_hooks:write`, `workflows:write`
4. **Revoke pulser-hub client secret** — Unused since Nov 2025

### Medium-Term
5. **Restrict repository selection** — Move apps from `all` to `selected` where only `odoo` repo is needed
6. **Enable weekly drift monitoring** — `.github/workflows/github-app-ssot-guard.yml` (schedule: Monday 09:00 UTC)

### Not Actionable
- Third-party app permissions cannot be individually reduced (set by the app publisher)
- Apps like Slack and Vercel require broad permissions by design

---

## SSOT Files

| File | Purpose |
|------|---------|
| `ssot/github/apps/pulser-hub.yaml` | Custom app contract (declared intent) |
| `ssot/github/apps/org-installed.yaml` | Third-party app inventory (live snapshot) |
| `ssot/secrets/registry.yaml` | Secret identifiers for all apps |
| `scripts/ci/check_github_app_ssot.py` | Drift verification script |
| `scripts/github_app/auth.py` | JWT + installation token helper |
| `.github/workflows/github-app-ssot-guard.yml` | CI drift guard |
