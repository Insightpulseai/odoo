# Tasks — insightpulseai.com

## P0 (must ship)

- [x] Create/confirm SSOT file for canonical URLs (`infra/dns/subdomain-registry.yaml`)
- [x] Add Spec Kit bundle (`spec/insightpulseai-com/`)
- [x] Fix all `.net` references in non-archive active files
- [x] Fix all `ipa.insightpulseai.com` references → `n8n.insightpulseai.com`
- [x] Define redirect policy: `www` → 301 → apex (documented in CANONICAL_URLS.md)
- [x] Publish `docs/architecture/CANONICAL_URLS.md` and link from README
- [x] Create `reports/url_inventory.json` (machine-readable inventory)
- [ ] Enforce `.com`-only reference gate (`.github/workflows/domain-lint.yml`)

## P1

- [ ] Extend `scripts/verify-service-health.sh` with marketing surface entries:
  - `insightpulseai.com` (apex) — HTTP reachable, content signature
  - `www.insightpulseai.com` — redirects to apex (301)
- [ ] Add content signature check (verify correct app on correct domain)
- [ ] Add CI gate for DNS IaC validation + drift detection (already exists: `dns-sync-check.yml`)
- [ ] Verify Cloudflare page rule enforces www → apex redirect

## P2

- [ ] Token-gated Sentry/Netdata checks (skip when missing)
- [ ] Scheduled healthcheck cron workflow (optional)
- [ ] Alert routing to Slack on failures (optional)

## Evidence

- [x] URL inventory: `reports/url_inventory.json`
- [x] Canonical URLs doc: `docs/architecture/CANONICAL_URLS.md`
- [ ] Healthcheck report artifacts (JSON/MD) in CI
- [ ] DNS IaC apply evidence (outputs/logs) in `docs/evidence/`

## AI Marketing Canvas Epics

Source: AI Marketing Canvas (PDF)

- [ ] Epic: Data Foundation & Identity (Stable keys, consent enforcement, schema).
- [ ] Epic: Experimentation Harness (Segments v1, A/B assignment, measurement).
- [ ] Epic: Scoring & Next Best Action (Propensity models, Odoo activity connectors).
- [ ] Epic: Closed Loop + Autopilot Guardrails (Outcome capture, frequency capping).
- [ ] Epic: Productization + SLAs (Templates, client reporting, pipeline reliability).
