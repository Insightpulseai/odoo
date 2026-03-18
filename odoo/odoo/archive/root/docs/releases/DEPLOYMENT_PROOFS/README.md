# Deployment Proofs

This directory contains evidence artifacts for the production deployment.

## Release: prod-20260106-1741

| File | Description | Source |
|------|-------------|--------|
| `deploy_run_166.json` | Full workflow run metadata | GitHub Actions API |
| `deploy_run_166_jobs.json` | Job and step details | GitHub Actions API |
| `release_tag_prod-20260106-1741.json` | Release tag metadata | GitHub Releases API |

## Verification

All artifacts were fetched from the GitHub API at generation time (2026-01-06T18:07:00Z).

### Key Evidence Points

1. **Workflow Conclusion**: `success`
2. **All Jobs Passed**: Pre-flight, Deploy, Smoke Test, Auto-Tag
3. **Release Tag Created**: `prod-20260106-1741`
4. **Head SHA**: `782fea9a7a4656d6ba225fcbea132908978d1522`

## API Endpoints Used

```
GET /repos/jgtolentino/odoo-ce/actions/runs/20756736863
GET /repos/jgtolentino/odoo-ce/actions/runs/20756736863/jobs
GET /repos/jgtolentino/odoo-ce/releases/tags/prod-20260106-1741
```

## Provenance

| Artifact | URL |
|----------|-----|
| Workflow Run | https://github.com/jgtolentino/odoo-ce/actions/runs/20756736863 |
| Release | https://github.com/jgtolentino/odoo-ce/releases/tag/prod-20260106-1741 |
| Commit | https://github.com/jgtolentino/odoo-ce/commit/782fea9a7a4656d6ba225fcbea132908978d1522 |
