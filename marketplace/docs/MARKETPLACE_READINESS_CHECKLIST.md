# Marketplace Readiness Checklist

> **Scope**: This checklist applies to all Marketplace offers under `marketplace/offers/`, with per-offer readiness captured in each offer's local `READINESS.md`.

## Readiness Levels

| Level | Name | Gate |
|-------|------|------|
| 0 | Scaffolded | Offer directory + READINESS.md exist |
| 1 | Alpha | Sections A–C pass (Identity, Technical, Security baseline) |
| 2 | Beta | Sections A–F pass + internal dogfooding |
| 3 | GA-Ready | All sections A–J pass + external beta feedback |
| 4 | Listed | Published on target marketplace(s) |

---

## A. Offer Identity & Metadata

- [ ] Offer has a unique slug (`marketplace/offers/<slug>/`)
- [ ] `READINESS.md` exists with offer name, description, and target marketplace(s)
- [ ] Logo / icon assets exist (SVG preferred, PNG fallback at 512×512)
- [ ] One-liner description (≤ 120 chars)
- [ ] Long description / value proposition (≤ 500 words)
- [ ] Category / tags defined
- [ ] Pricing model documented (free / freemium / paid / custom)
- [ ] Target audience identified

## B. Technical Completeness

- [ ] Core functionality implemented and working
- [ ] All critical user flows tested end-to-end
- [ ] API documentation exists (OpenAPI / AsyncAPI / GraphQL schema)
- [ ] Configuration is externalized (env vars, not hardcoded)
- [ ] Health check endpoint exists and returns structured response
- [ ] Versioning strategy defined (SemVer recommended)
- [ ] Dependency inventory complete (no phantom deps)
- [ ] Build reproducibility verified (deterministic builds)

## C. Security Baseline

- [ ] No secrets in source code (verified by CI scanner)
- [ ] Authentication mechanism documented and tested
- [ ] Authorization model defined (RBAC / ABAC / API keys)
- [ ] Input validation on all external-facing endpoints
- [ ] OWASP Top 10 review completed
- [ ] Dependency vulnerability scan clean (critical/high = 0)
- [ ] TLS enforced on all external communication
- [ ] Rate limiting configured on public endpoints

## D. Observability & Operations

- [ ] Structured logging (JSON) with correlation IDs
- [ ] Metrics endpoint exposed (Prometheus-compatible preferred)
- [ ] Error tracking integrated (Sentry / equivalent)
- [ ] Runbook exists for top-5 failure modes
- [ ] Backup and restore procedure documented and tested
- [ ] Graceful shutdown handles in-flight requests
- [ ] Resource limits defined (CPU, memory, storage)
- [ ] Scaling strategy documented (horizontal / vertical / auto)

## E. Documentation

- [ ] Installation / setup guide (< 15 minutes to first success)
- [ ] Configuration reference (all env vars / settings)
- [ ] User guide with screenshots or screen recordings
- [ ] API reference (auto-generated from spec preferred)
- [ ] Troubleshooting FAQ (≥ 5 common issues)
- [ ] Changelog maintained (CHANGELOG.md or GitHub Releases)
- [ ] Architecture decision records for major choices

## F. Testing & Quality

- [ ] Unit test coverage ≥ 70%
- [ ] Integration tests cover critical paths
- [ ] E2E smoke test exists and runs in CI
- [ ] Performance baseline established (p50, p95, p99 latencies)
- [ ] Load test validates stated capacity
- [ ] Accessibility audit passed (WCAG 2.1 AA for web UI)
- [ ] Cross-browser / cross-platform testing (if applicable)

## G. Compliance & Legal

- [ ] License file exists (SPDX identifier)
- [ ] Third-party license audit complete (no GPL in proprietary offers)
- [ ] Privacy policy reviewed (GDPR / CCPA if handling PII)
- [ ] Data processing agreement template available (if applicable)
- [ ] Export control classification (if applicable)
- [ ] Terms of service drafted

## H. Marketplace-Specific Requirements

- [ ] Target marketplace(s) identified (e.g., Odoo Apps Store, GitHub Marketplace, AWS Marketplace)
- [ ] Marketplace-specific metadata prepared (screenshots, categories, pricing tiers)
- [ ] Listing copy reviewed for marketplace guidelines
- [ ] Submission process documented
- [ ] Review / approval timeline estimated
- [ ] Post-listing update process documented

## I. Support & SLA

- [ ] Support channel defined (email, Slack, GitHub Issues, etc.)
- [ ] Response time targets documented
- [ ] Escalation path defined
- [ ] SLA document exists (uptime target, maintenance windows)
- [ ] Incident response playbook exists
- [ ] Customer feedback mechanism in place

## J. Launch Readiness

- [ ] Internal dogfooding completed (≥ 2 weeks)
- [ ] External beta feedback collected (≥ 3 users)
- [ ] Launch announcement drafted
- [ ] Monitoring dashboards configured for launch day
- [ ] Rollback plan documented and tested
- [ ] Success metrics defined (adoption, retention, revenue)
- [ ] Post-launch review scheduled (T+7d, T+30d)
