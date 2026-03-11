# Constitution — IPAI Odoo SaaS Platform

## 1) Purpose

To provide a secure, multi-tenant, and highly automated Odoo ERP experience that matches the Odoo.sh lifecycle while extending it with AI-native capabilities and sovereign data governance.

## 2) Non-negotiables (Tier-0)

1. **Tenant Isolation**: Strict DB-per-tenant isolation at the PostgreSQL level. No cross-tenant data leakage.
2. **Sovereignty**: Customers must be able to export their full database and filestore at any time (No vendor lock-in).
3. **Reproducibility**: Environment lifecycle (dev -> staging -> prod) must be driven by Git (GitOps).
4. **Security-First**: RLS by default at the platform layer; mandatory audit logging for all administrative actions.
5. **High Availability**: Automated failover for PostgreSQL and 99.9% uptime for the application layer.

## 3) Engineering Principles

1. **Capability over Modules**: Parity is measured by what a user can _do_ (e.g., "sign a document") rather than module presence.
2. **12-Factor Compliance**: Applications must be stateless; configuration via environment variables.
3. **Automated Governance**: Policy-as-code (Rego/CEL) gates all production deployments.
4. **AI-Native**: Platform operations (ops) and user assistance must be augmented by the IPAI agent framework.

## 4) Compliance & Performance

- **Compliance**: SOC2/GDPR readiness as a baseline.
- **Performance**: <200ms TTFB for global users; <2s for complex Odoo report generation.
