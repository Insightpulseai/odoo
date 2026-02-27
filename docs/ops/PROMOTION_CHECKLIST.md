# Promotion Checklist (Stage → Prod)

Before promoting a release to production, ensure the following criteria are met:

- [ ] **Preflight Success**: The latest GitHub Action run for the release tag must be 100% green.
- [ ] **Staging Verified**: The candidate version has been running in Staging for at least 2 hours without errors.
- [ ] **Health Check**: `curl /web/health` returns 200 OK on Staging.
- [ ] **Allowlist Audit**: No unaudited OCA modules are present in the `addons/oca/selected` path.
- [ ] **Backup Verified**: Automated snapshot of `odoo-db-sgp1` was successful within the last 24 hours.
- [ ] **Diagram Sync**: No architectural drift detected in `docs/architecture/`.

## Approval Process

1. GitHub Environment Protection will notify the **Platform Lead**.
2. Approver must link to this checklist in the approval comment.
