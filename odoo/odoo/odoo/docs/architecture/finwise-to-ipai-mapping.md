# Finwise to IPAI UI Mapping

This document maps the high-fidelity UI sections from the **Finwise** template to the live services and features of the **Insightpulseai (IPAI)** ecosystem.

## UI Mapping Table

| Finwise Section | IPAI Feature / Component   | Data Source                           |
| :-------------- | :------------------------- | :------------------------------------ |
| **Hero**        | **OdooOps Command Center** | Supabase Auth + Odoo Meta API         |
| **Partners**    | **Platform Integrations**  | GitHub, Azure, Supabase, DigitalOcean |
| **Features**    | **Agent Skill Registry**   | `agents/registry/odoo_skills.yaml`    |
| **Statistics**  | **Infra Health Metrics**   | DO Managed Metrics / Loki             |
| **Pricing**     | **Cost Pillar Assessment** | WAF Cost Optimization Skill           |
| **FAQ**         | **Odoo19 Knowledge Base**  | `docs/kb/odoo19/`                     |
| **CTA**         | **Console Access**         | `odooops-console` login               |

## Implementation Strategy

1.  **Component Scaffolding**: Use the `finwise` Tailwind/TypeScript structures as the base for the OdooOps landing page.
2.  **State Management**: Replace static JSON in `finwise` with real-time fetches from the **Supabase** backend.
3.  **Animation Integration**: Retain **Framer Motion** for high-fidelity transitions while ensuring compatibility with **shadcn/ui** components.
4.  **Deployment**: Target **Vercel** or **DigitalOcean App Platform** for the standalone landing page.
