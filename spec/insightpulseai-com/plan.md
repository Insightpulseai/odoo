# Plan — insightpulseai.com

## Phase 0 — Inventory + SSOT wiring (DONE)

- [x] Identify current canonical URLs and ensure `.com` only
- [x] Confirm SSOT locations:
  - `infra/dns/subdomain-registry.yaml` (DNS SSOT)
  - `infra/cloudflare/envs/prod/subdomains.auto.tfvars` (generated Terraform)
  - `docs/arch/runtime_identifiers.json` (generated runtime config)
  - `docs/architecture/CANONICAL_URLS.md` (human-readable reference)
- [x] Ensure docs reference SSOT, not the other way around
- [x] Fix stale `.net` + `ipa.insightpulseai.com` references (21 files)
- [x] Create `reports/url_inventory.json` (machine-readable with drift)

## Phase 1 — DNS IaC + redirect policy

- [x] Apex + www records defined in `subdomain-registry.yaml`
- [x] Redirect policy documented: `www` → 301 → apex
- [x] DNS sync check CI gate: `.github/workflows/dns-sync-check.yml`
- [ ] Verify Cloudflare page rule / redirect rule enforces www → apex

## Phase 2 — Health checks + reporting

- [x] `scripts/verify-service-health.sh` covers all prod + staging services
- [ ] Extend healthcheck to add marketing surface entries:
  - `insightpulseai.com` (apex) — HTTP 200, content signature
  - `www.insightpulseai.com` — HTTP 301 to apex
- [ ] Emit JSON + Markdown reports as CI artifacts
- [ ] Content signature check detects misrouting

## Phase 3 — `.net` regression gate

- [ ] Add `.github/workflows/domain-lint.yml`
  - Runs on all PRs
  - Greps for `.net` references in non-archive paths
  - Fails with helpful message listing offending files
- [ ] Test with intentional `.net` reference to verify gate

## Phase 4 — Observability + ops integration

- [ ] Token-gated Netdata/Sentry checks (skip when missing)
- [ ] Canonical URLs list published in docs and referenced by README
- [x] `docs/architecture/CANONICAL_URLS.md` created and linked from README

## Phase 5 — Hardening

- [ ] Regression tests for:
  - `.net` leakage (grep gate in CI)
  - Redirect regressions (www → apex)
  - Misrouting signature failures
- [ ] Scheduled healthcheck run (cron workflow, optional)
- [ ] Alert routing to Slack (optional)
