# Strategic Finance & Portfolio Command Center: MVP Go-Live Checklist (v1.0)

The minimum viable product is validated by running the core workflows that prove the platform can securely control spend and manage the financial close. The system is operational only when all four pillars below are functioning in production.

## Pillars & Required Validations

| # | Pillar / Component | Required Validation | Owner |
| --- | --- | --- | --- |
| 1 | Identity & Access | Users log into Odoo (`erp.insightpulseai.net`) via Keycloak SSO. | CKVC (Khalil) |
| 2 | Spend Control | Internal procurement flow creates a `purchase.request` (not `sale.order`) when an employee submits a cart request on the Website. | BOM (Beng) |
| 3 | Core PPM Logic | Finance dashboard shows the Month-End Close project with calculated RAG status; WBS codes (1.1, 1.2) auto-number correctly on create/re-sequence. | RIM (Rey) |
| 4 | Deployment | A merge to `main` triggers GitHub Actions to build the custom Docker image and automatically update the Odoo server (no manual SSH). | DevOps |

## Feature Bundle Included in This MVP

- WBS Auto-Numbering (Work Breakdown Structure) — `ipai_ppm_advanced`
- Budget Control Interface (Procure-to-Pay) — `ipai_internal_shop`
- Email/Mobile Alerts (Communications Management) — `ipai_finance_ppm` (Alerts)
- External Auth — `auth_oidc` (Keycloak)
- Image Deployment — `deploy.yml` (image-based CD)

## Production Image Activation (Next Action)

The latest production image (`ghcr.io/jgtolentino/odoo-ce:latest`) contains all merged features. Run these commands on the DigitalOcean VPS (`159.223.75.148`) to pull and start it:

```bash
# From ~/odoo-prod with docker-compose.prod.yml pointing to ghcr.io/jgtolentino/odoo-ce:latest
docker compose -f docker-compose.prod.yml pull odoo

docker compose -f docker-compose.prod.yml up -d
```

## Branch Discipline for Release

- Do **not** rename or mark the technical feature branch (`codex/implement-ipai_ppm_advanced-module-in-odoo`) as `main`.
- Merge PR #25 (Runbook docs) into the aggregation branch (for example, `feature/add-expense-equipment-prd`).
- Merge the stable aggregation branch into `main` to trigger the production CD pipeline.
- Only the clean, stable `main` branch should deploy to the live server.
