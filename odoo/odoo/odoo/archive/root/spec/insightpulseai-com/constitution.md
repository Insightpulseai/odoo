# Constitution — insightpulseai.com

## Non-negotiables

1. **Canonical domain is `.com` only**
   - No `.net` URLs in UI, docs, code, DNS, emails, or redirects.
   - `https://insightpulseai.com` is canonical; `https://www.insightpulseai.com` must 301-redirect to canonical.
   - CI gate blocks `.net` references outside `archive/`.

2. **Automation-first operations**
   - No manual UI steps required to deploy, update DNS, rotate content, or verify health.
   - Changes land via PRs + CI gates + repeatable scripts/workflows.

3. **Single Source of Truth (SSOT)**
   - DNS records are SSOT in `infra/dns/subdomain-registry.yaml`.
   - Cloudflare IaC lives under `infra/cloudflare/`.
   - Canonical URL registry is `docs/architecture/CANONICAL_URLS.md` (generated from SSOT).
   - Runtime identifiers: `docs/arch/runtime_identifiers.json` (generated).
   - CI validates sync: `.github/workflows/dns-sync-check.yml`.

4. **Performance + reliability baseline**
   - 99.9% availability target for the marketing surface.
   - Core pages must render without errors and without empty states.
   - Must be cache-friendly (CDN) and resilient to backend outages.
   - LCP target < 2.5s on typical broadband.

5. **Security + integrity**
   - HTTPS only; HSTS enabled; Cloudflare Full (strict) TLS.
   - No secrets in repo; env-only configuration.
   - Supply-chain safe: locked deps and CI scans (as already practiced).

6. **Observability is mandatory**
   - Healthcheck must be machine-readable (JSON + Markdown) and CI-friendly.
   - `scripts/verify-service-health.sh` covers marketing surface.
   - Content signature check detects misrouting (wrong app served on domain).
   - Token-gated Sentry/Netdata hooks: skip when tokens absent, don't hard-fail.

## Definition of "done"

A user can reach the site on the canonical `.com` domain, see correct content,
`www` 301-redirects to apex, and CI can automatically verify it via health checks.
