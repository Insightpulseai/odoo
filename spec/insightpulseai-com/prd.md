# PRD — insightpulseai.com

## Goal

Provide a fast, reliable, canonical `.com` marketing surface for InsightPulseAI
that integrates cleanly with SSOT infrastructure and automated verification.

## Users

- Prospects evaluating products/platform
- Partners/integrators
- Internal stakeholders sharing public URLs
- Search engines/crawlers

## In-scope

- Canonical marketing site for `insightpulseai.com`
- Canonicalization rules (`www` → apex, 301 redirect)
- DNS + CDN posture (Cloudflare) as code
- Automated health checks and reporting
- Clear linkage to ops surfaces (docs, ops console, ERP) via canonical URLs list
- CI gate preventing `.net` domain regression

## Out-of-scope (for this bundle)

- Rebuilding product apps (ops-console, ERP)
- Deep content strategy copywriting
- SEO keyword research
- Paid marketing tracking implementation

## Functional requirements

### FR1 — Canonical URL policy

- Site served at `https://insightpulseai.com`
- `https://www.insightpulseai.com` → 301 redirect to apex
- All internal links must use canonical `.com` URLs only
- Documented in: `docs/architecture/CANONICAL_URLS.md`

### FR2 — DNS IaC (Cloudflare)

- DNS records for apex + `www` managed via `infra/dns/subdomain-registry.yaml`
- Cloudflare IaC under `infra/cloudflare/`
- DNS drift detectable; CI fails if SSOT deviates: `.github/workflows/dns-sync-check.yml`

### FR3 — Health checks

A health check runner validates:

- HTTP reachability (status 200–399)
- TLS validity
- Canonical redirect correctness (www → apex)
- Content signature (title or known marker) to detect misrouting
- Output: JSON + Markdown
- Non-zero exit code on failure

Runner: `scripts/verify-service-health.sh` (marketing surface entry added).

### FR4 — `.net` regression gate

- CI workflow: `.github/workflows/domain-lint.yml`
- Blocks PRs that introduce `.net` domain references in non-archive paths
- Allowlist: `archive/`, `.git/`, migration scripts explicitly dealing with `.net`

### FR5 — Observability hooks

- Monitoring endpoints (Sentry/Netdata) receive availability + error signals
- If tokens are absent, checks mark as "skipped" (not hard fail)

## Non-functional requirements

- Performance: LCP target < 2.5s on typical broadband; CDN caching enabled
- Security: HTTPS-only; HSTS enabled; no secrets in repo
- Reliability: 99.9% monthly availability target
- Maintainability: SSOT files clearly documented; changes are PR-driven

## Acceptance criteria

- [ ] Canonicalization: `www` → apex enforced with 301
- [ ] Healthcheck passes in CI when correct env vars are present
- [ ] DNS IaC exists in `infra/cloudflare/` and matches documented SSOT
- [ ] README references only `.com` canonical URLs
- [ ] CI gate prevents `.net` regressions outside `archive/`
- [ ] Content signature check catches misrouting

## Risks

- Mixed canonical policy (apex vs www) causing SEO + caching issues
- Cloudflare drift from SSOT if not gated
- Misrouting (e.g., serving wrong app) not detected without content signature checks

## Canvas-to-Capabilities Mapping

Source: AI Marketing Canvas (PDF)

- **Foundation** → Data/identity/consent rules (Odoo contacts + Supabase auth/RLS).
- **Experimentation** → Segments + measurement (Supabase queries + Vercel analytics).
- **Expansion** → Scoring + activation (Odoo Activities, Supabase Edge Functions).
- **Transformation** → Closed-loop + autopilot (Supabase webhooks, GraphRAG over assets).
- **Monetization** → Packaging + governance (Templates, SLOs, Billing/Metering via Stripe).
