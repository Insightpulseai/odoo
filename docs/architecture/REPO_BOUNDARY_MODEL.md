# Repo Boundary Model

> SSOT: `platform/ssot/domain/domain-site-map.yaml`
> Rationalization plan: `platform/ssot/org/repo-rationalization-plan.yaml`

---

## Domain site map baseline

Public domains are mapped as follows:

| Domain | Repo | Role |
|---|---|---|
| `insightpulseai.com` | `web` | Company/product shell |
| `prismalab.insightpulseai.com` | `web` | Demo/lab surface |
| `w9studio.net` | `web` | W9 public brand site |
| `erp.insightpulseai.com` | `odoo` | ERP runtime only |

## Retired

- `landing.io` — redirect-shell repo, replaced by `web` repo owning all public surfaces

## Deleted

- `demo-repository` — no domain or surface boundary ownership

## Rules

1. One public domain maps to one canonical surface
2. `erp.insightpulseai.com` is reserved for Odoo ERP only — no marketing, no lab, no mixed shell
3. All public sites (`insightpulseai.com`, `prismalab.*`, `w9studio.net`) are owned by `web`
4. No new redirect-only repos
