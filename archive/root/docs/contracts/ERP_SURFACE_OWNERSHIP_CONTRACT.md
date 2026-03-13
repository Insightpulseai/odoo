# C-29 — ERP Surface Ownership Contract

> **Status**: Active
> **Created**: 2026-03-11
> **Source SSOT**: Org-level repo ownership model
> **Consumers**: All repos in `Insightpulseai` org

---

## Purpose

Define which repository owns which concern for the ERP surface
(`erp.insightpulseai.com`), login flow, authenticated workspace, and
supporting infrastructure.

---

## Ownership Table

| Concern | Owning Repo | Rationale |
|---------|-------------|-----------|
| Odoo login page (`/web/login`) | `odoo` | App behavior |
| Odoo authenticated workspace (`/odoo`, `/web`) | `odoo` | App behavior |
| Odoo session/auth flow | `odoo` | App behavior |
| Post-login workspace routing | `odoo` | App behavior |
| Odoo web/client JS behavior | `odoo` | App behavior |
| Odoo-specific ERP branding | `odoo` | App behavior |
| AI Copilot inside ERP workspace | `odoo` | App behavior (ipai_ai_copilot) |
| `erp.insightpulseai.com` DNS record | `infra` | Domain routing |
| Azure Front Door / Cloudflare edge | `infra` | Domain routing |
| ACA ingress / container networking | `infra` | Domain routing |
| WAF / edge security rules | `infra` | Domain routing |
| TLS certificates / domain wiring | `infra` | Domain routing |
| Environment hostname registry | `infra` | Domain routing |
| Origin cutover / blue-green switching | `infra` | Domain routing |
| Platform admin / control-plane views | `ops-platform` | Operator concern |
| Environment registry | `ops-platform` | Operator concern |
| Release / promotion metadata | `ops-platform` | Operator concern |
| Operational dashboards | `ops-platform` | Operator concern |
| Marketing site | `web` | Non-ERP public surface |
| Product landing pages | `web` | Non-ERP public surface |
| Documentation site | `web` | Non-ERP public surface |
| External app shells (non-Odoo) | `web` | Non-ERP public surface |

---

## Rules

```
ERP app behavior lives in `odoo`.
ERP public routing lives in `infra`.
Non-ERP public web lives in `web`.
Platform admin/control-plane views live in `ops-platform`.
```

---

## Invariants

1. **Login UI is never in `web` or `infra`.** The Odoo login page is owned by `odoo` via
   standard Odoo web client (`/web/login`). Custom branding uses `ipai_theme_*` modules in `odoo`.

2. **DNS/edge is never in `odoo`.** Domain records, CDN config, WAF rules, and ingress
   definitions live in `infra`. The `odoo` repo must not contain Cloudflare, Azure Front Door,
   or DNS configuration.

3. **No ERP UI in `ops-platform`.** The ops-platform repo handles operator/admin views
   (environment registry, promotion dashboards). It does not serve end-user ERP pages.

4. **No Odoo routes in `web`.** The `web` repo serves non-ERP surfaces (marketing, docs,
   landing pages). It must not duplicate or proxy Odoo login/workspace routes.

5. **Cross-repo changes require both PRs.** A change that affects both app behavior and
   routing (e.g., adding a new subdomain for a new Odoo instance) requires coordinated
   PRs in both `odoo` and `infra`.

---

## Validator

Structural validation: `repo-boundary-check.yml` ensures the `odoo` repo does not contain
infrastructure routing files (Cloudflare config, DNS records, ingress definitions).

Cross-repo validation is manual — coordinated PRs are reviewed by the owner of each repo.
