# Tasks — IPAI Odoo SaaS Platform

## Milestone 1: Platform Core

- [ ] Initialize K8s cluster and namespaces.
- [ ] Configure PostgreSQL high availability (CloudNativePG).
- [ ] Build Odoo 19 "Golden Image" with pre-cached OCA modules.

## Milestone 2: Provisioning & Portal

- [ ] Create Supabase schema for Tenant management.
- [ ] Implement `create-tenant` Edge Function.
- [ ] Build landing page and customer login in `apps/platform-kit`.

## Milestone 3: Odoo.sh Parity

- [ ] Implement automated backup cron jobs.
- [ ] Set up Prometheus/Grafana dashboards for tenant health.
- [ ] Configure GitHub Webhooks for branch-based deployment.

## Milestone 4: Billing & Go-Live

- [ ] Integrate Stripe webhook for plan activation.
- [ ] Finalize "Sovereignty Export" tool (one-click DB dump).
- [ ] Perform Tier-0 Parity audit.
