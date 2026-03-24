# Pulser Minimal Runtime

> Defines the minimum Azure-native services required to run the Pulser assistant family.
> Cross-referenced by: `ACTIVE_PLATFORM_BOUNDARIES.md`, `ssot/agents/assistant_surfaces.yaml`
> Updated: 2026-03-25

---

## Pulser Family

| Surface | Product Name | Role | Runtime Needs |
|---------|-------------|------|---------------|
| Pulser | Pulser for Odoo | ERP transactional assistant | Odoo + Foundry |
| Pulser Diva | Pulser Diva | Orchestration & schema assistant | Foundry + Databricks |
| Pulser Studio | Pulser Studio | Creative finishing & media ops | Foundry + Gemini + fal |
| Pulser Genie | Pulser Genie | Conversational analytics | Foundry + Databricks + Power BI |
| Pulser Docs | Pulser Docs | Document review & extraction | Foundry + Document Intelligence |
| Ask Pulser | Ask Pulser | Public product assistant | ACA (static) + Foundry |

## Minimal Runtime Stack

```
┌──────────────────────────────────────────────────┐
│                 Pulser Surfaces                   │
│  (Diva, Studio, Genie, Docs, Ask Pulser, ERP)   │
└──────────────────────┬───────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────┐
│              Azure AI Foundry                     │
│  Agent runtime, MCP tools, skill orchestration    │
│  Identity: Entra Agent ID (managed identity)      │
└──────────┬───────────┬───────────┬───────────────┘
           │           │           │
    ┌──────▼───┐ ┌─────▼────┐ ┌───▼──────────────┐
    │ Odoo CE  │ │Databricks│ │ AI Services       │
    │ (SoR)    │ │(Lakehouse│ │ - OpenAI (eval)   │
    │          │ │ + Unity) │ │ - Gemini (create)  │
    └──────────┘ └──────────┘ │ - Doc Intel (OCR)  │
                              │ - fal (media)      │
                              └────────────────────┘
```

## Service Dependencies per Surface

| Surface | Foundry | Odoo | Databricks | OpenAI | Gemini | Doc Intel | fal | Power BI |
|---------|---------|------|------------|--------|--------|-----------|-----|----------|
| Pulser (ERP) | Yes | **Yes** | No | Yes | No | No | No | No |
| Pulser Diva | **Yes** | Yes | Yes | Yes | No | No | No | No |
| Pulser Studio | **Yes** | No | No | Yes (eval) | **Yes** (gen) | No | Yes | No |
| Pulser Genie | **Yes** | No | **Yes** | Yes | No | No | No | Yes |
| Pulser Docs | **Yes** | No | No | Yes | No | **Yes** | No | No |
| Ask Pulser | **Yes** | No | No | Yes | No | No | No | No |

**Bold** = primary dependency. All surfaces require Foundry as the agent runtime.

## Creative Generation Routing (Pulser Studio)

Per `ssot/creative/provider_policy.yaml`:

| Task | Provider | Model |
|------|----------|-------|
| Fast stills / concepting | Gemini (direct) | `nano-banana-2-preview` (Gemini 3.1 Flash Image) |
| Standard stills / ad mockups | Gemini (direct) | `nano-banana-pro-preview` (Gemini 3 Pro Image) |
| Premium brand photography | Imagen | `imagen-4` |
| Video | Gemini (direct) | `veo-3.1-preview` (Veo 3.1) |
| Mixed media (video, audio, SFX) | fal | Kling, LTX, audio models |
| Understanding / evaluation | OpenAI | `gpt-4.1` (judge only, not generator) |

## Infrastructure Requirements

| Resource | Type | Min Spec | Purpose |
|----------|------|----------|---------|
| ACA Environment | Container Apps | `ipai-odoo-dev-env` | All Pulser containers |
| Foundry Hub | AI Foundry | `aifoundry-ipai-dev` | Agent runtime |
| OpenAI | Azure OpenAI | `oai-ipai-dev` | LLM inference + eval judges |
| Key Vault | Key Vault | `kv-ipai-dev` | API keys (Gemini, fal, OpenAI) |
| Entra ID | Identity | Tenant | Agent identity + user SSO |
| Front Door | CDN/WAF | `ipai-fd-dev` | Edge routing for all surfaces |

## What Pulser Does NOT Need

These services are **not required** for Pulser to function:

- Supabase (auth handled by Entra, data by Odoo/Databricks)
- n8n (automation handled by Foundry agents)
- Plane (project tracking in DevOps Boards)
- Shelf (knowledge in Odoo Knowledge module)
- Keycloak (identity in Entra)
- Standalone CRM container (CRM in Odoo)

## Agent Identity Model

```
Entra Tenant
├── App Registration: pulser-diva-agent
│   └── Managed Identity → Key Vault access
├── App Registration: pulser-studio-agent
│   └── Managed Identity → Gemini/fal API keys
├── App Registration: pulser-genie-agent
│   └── Managed Identity → Databricks token
├── App Registration: pulser-docs-agent
│   └── Managed Identity → Doc Intel endpoint
└── App Registration: ask-pulser-agent
    └── Managed Identity → OpenAI only (public, no PII)
```

Each Pulser surface runs as a distinct Entra agent identity with least-privilege access to only the services it needs.

---

*This document defines what Pulser needs. `ACTIVE_PLATFORM_BOUNDARIES.md` defines what the platform provides.*
