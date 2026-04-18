# Constitution: Microsoft Marketplace GTM

> Immutable architectural and business rules for the Pulser for Odoo commercial offer.

---

## 1. Distribution & Billing
1.1 **Transactable Only**: All commercial offers must be "Transactable" via the Azure Commercial Marketplace.
1.2 **SaaS Offer Type**: The primary listing is a SaaS Offer managed via Partner Center.
1.3 **Payout Authority**: Marketplace Payouts are the sole canonical revenue stream for external customer licenses.

## 2. Architectural Invariants
2.1 **Azure Native**: No external hosting dependencies (Supabase, DigitalOcean, Cloudflare, etc.). All components must run on Azure Container Apps (ACA), PostgreSQL Flexible Server, and **Azure AI Foundry**.
2.2 **Entra ID Priority**: Microsoft Entra ID is the mandatory and sole identity provider for Marketplace SSO, tenant fulfillment, and service-to-service authentication.
2.3 **Sovereign Compliance**: The initial target is the **Philippines** market; all data residency rules must be configurable via Azure region selections (East Asia / Southeast Asia).
2.4 **Workspace Standard**: All agentic modules (`ipai_*`) must adhere to the `.foundry/agent-metadata.yaml` workspace contract for configuration and model routing.

## 3. Launch Constraint
3.1 **Target Date**: Q3 2026 (August-September).
3.2 **MVP Guardrail**: The "Minimum Publishable version" must include Odoo Accounting, Pulser AI (Extraction + Guidance), and basic Power BI reporting.

---
*Last updated: 2026-04-18 — Rule 2.4 Compliance Audit Completed (Foundry Specialists Registered)*
