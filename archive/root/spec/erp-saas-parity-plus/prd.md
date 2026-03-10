# ERP SaaS Parity Plus PRD

## Executive Summary

Deliver a full ERP SaaS parity platform that matches or exceeds traditional SaaS ERPs (like Odoo Enterprise, NetSuite) by combining the Odoo CE transaction engine with a Supabase control plane, modern Vercel UIs, and agentic workflows.

## Objectives

- Achieve 80-90% functional ERP parity organically via Odoo CE and OCA.
- Deliver the missing 10-20% (Enterprise features like advanced integrations, document automation, advanced auth, and scale) by delegating non-transactional workloads to dedicated external services (Supabase, Vercel, n8n).
- Empower "Agentic Ops" to act as system administrators, proactively triaging job queues and assisting with business workflows.

## Key Deliverables (The 7-Layer Plan)

1. **ERP Parity Matrix**: `docs/parity/ERP_SAAS_PARITY_MATRIX.md` defining feature coverage gaps vs EE.
2. **Identity/Tenancy**: `docs/architecture/TENANCY_MODEL.md` defining SSO, user syncing, and multi-tenant DB structure.
3. **Integration Bus**: The currently established Supabase `ops.*` backbone linking Odoo to Vercel/n8n/Slack/Stripe/Resend.
4. **Observability**: `docs/ops/OBSERVABILITY.md` detailing how logs and metrics surface to the Ops Console and Slack.
5. **Release Train**: `docs/ops/RELEASE_TRAIN.md` defining the staging and drift-control CI/CD processes.
6. **Billing & Entitlements**: `docs/product/BILLING_ENTITLEMENTS.md` outlining the SaaS business model and Stripe integration.
7. **Agentic Ops**: `docs/plus/AGENTIC_OPS.md` covering GraphRAG and MCP usage for AI triage.

## External Drivers (IDC-aligned)

- **AI everywhere**: Assistants and agents becoming native to the flow of work.
- **Architecture modernization**: Strangler pattern incremental decoupling is the default modernization method.
- **Compliance services edge**: Unification via e-invoicing exchange and compliance mandates.
- **KPI redefinition**: Baselining standard metrics, then splitting into "employee-in-loop AI" vs "autonomous workflows".

## ERP-as-Platform Contract

- **Odoo CE+OCA**: The system-of-record and core workflow substrate.
- **Supabase**: The platform control plane and extension runtime.
- **Agents**: First-class workflow actors.
- **Strangler Pattern**: The required modernization and migration method (no big rewrites).

## Metrics & ROI

- **KPI Baselining**: Measure existing operational baselines before AI introduction.
- **Split Metrics**: Track "employee-in-loop" vs "autonomous" workflow efficiency.
- **ROI Framing**: Measure hard ROI (time saved) plus new value creation (revenue/capacity enablement).

## AI Strategy Playbook Principles (MIT TR Insights)

- **The Scaling Gap**: Moving from pilot to enterprise requires shifts in infrastructure, governance, supplier ecosystems, and ROI methods.
- **Data Core Requirements**: Success relies on data quality, data lineage, metadata, and data liquidity.
- **Unstructured-First Posture**: Treat unstructured data assimilation (OCR, docs, emails) as a primary capability, not an afterthought.
- **Vendor Posture**: Embrace a multi-AI ecosystem; avoid building custom foundation models.
- **ROI Posture**: Emphasize exact hard ROI (time-to-complete tasks) over abstract model evaluations.

## Out of Scope

- Re-writing Odoo core logic in Node.js.
- Building custom modules for things OCA already handles.
