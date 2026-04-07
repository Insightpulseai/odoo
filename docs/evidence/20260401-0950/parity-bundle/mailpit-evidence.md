# Mailpit Mail Catcher — Deployment Evidence

**Date**: 2026-04-01T09:48 UTC
**Gap**: Odoo.sh parity #9.3 (Built-in mail catcher)
**Verdict**: GAP → **PARITY**

## Before

- No mail catcher equivalent for non-prod environments
- Risk of real outbound mail from staging/dev

## Actions

1. Deployed `ipai-mailpit-dev` container app in `ipai-odoo-dev-env`
2. Image: `docker.io/axllent/mailpit:latest`
3. SMTP accepts any auth on port 1025 (internal)
4. Web UI on port 8025 (external ingress)

## After

| Property | Value |
|----------|-------|
| Container app | `ipai-mailpit-dev` |
| Revision | `ipai-mailpit-dev--pk217lu` |
| Status | Running |
| Web UI | `https://ipai-mailpit-dev.salmontree-b7d27e19.southeastasia.azurecontainerapps.io` |
| SMTP (internal) | `ipai-mailpit-dev:1025` |
| Resources | 0.25 vCPU / 0.5 GiB |
| Min replicas | 0 (scale to zero) |
| Max replicas | 1 |

## Odoo integration

To route non-prod Odoo mail to Mailpit, configure `ir.mail_server`:
- SMTP Server: `ipai-mailpit-dev` (ACA internal DNS)
- SMTP Port: `1025`
- No encryption, no authentication required

This replaces real SMTP (Zoho) in staging/dev environments.
