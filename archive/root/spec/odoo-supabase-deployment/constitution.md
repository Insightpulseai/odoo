# Constitution: Odoo + Supabase Production Deployment

> Non-negotiable rules for this spec bundle.

---

## Hard Constraints

1. **Odoo database = DigitalOcean Managed PostgreSQL** — never Supabase
2. **Supabase = integration layer** — webhooks, auth, edge functions, RAG, realtime only
3. **CE + OCA only** — no Enterprise modules, no odoo.com IAP
4. **Secrets in `.env` only** — never hardcoded in git
5. **Domain: `insightpulseai.com`** — `.net` is deprecated
6. **Python 3.12+** — Odoo 19 requirement
7. **Cost-conscious** — optimize for $24–48/mo droplet tier
8. **Reproducible** — entire stack rebuildable from repo + secrets
9. **No UI clickpaths** — everything CLI/CI automatable
10. **Evidence-backed** — no recommendations without production evidence

## Research Constraints

1. Every claim requires a citation (URL, version, date)
2. Prefer benchmarks and case studies over opinion
3. Do not recommend tools that add more operational burden than they solve
4. Do not break the working deployment before the new one is verified
5. Pin all versions — no `latest` tags in recommendations

## Scope Boundaries

- **In scope**: Docker, DigitalOcean, Supabase, OCA, CI/CD, security, monitoring, backup, cost
- **Out of scope**: Kubernetes (unless cost-justified), cloud-native vendor lock-in, Enterprise features
