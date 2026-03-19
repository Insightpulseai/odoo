# SaaS Landing Page Configuration

> **DRAFT** — Fulfillment URLs are not live. Webhook and SSO endpoints require implementation.

## Fulfillment URLs

| URL | Purpose |
|-----|---------|
| Landing page | https://insightpulseai.com/marketplace/activate |
| Webhook | https://n8n.insightpulseai.com/webhook/marketplace-subscription |
| SSO | https://auth.insightpulseai.com/saml/marketplace |

## Subscription lifecycle

| Event | Handler |
|-------|---------|
| Subscribe | Provision tenant, create Odoo database, send welcome email |
| Unsubscribe | Deactivate tenant, retain data 30 days, then purge |
| Suspend | Disable login, pause automation, retain data |
| Reinstate | Re-enable login, resume automation |
| ChangePlan | Adjust limits, update modules, notify admin |
| ChangeQuantity | Update user seat count |

## Technical requirements

- Tenant isolation: separate Odoo database per customer
- SSO: SAML 2.0 or OIDC via Microsoft Entra ID
- Data residency: SGP1 (Singapore) default, configurable
- Backup: Daily automated, 30-day retention
- SLA: 99.9% for Enterprise plan
