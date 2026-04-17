---
title: System topology
description: The 12-system architecture of the InsightPulse AI platform.
---

# System topology

The InsightPulse AI platform connects 12 systems. Odoo CE 18 is the transactional core. Supabase is the control plane. Azure provides runtime, edge, storage, and AI compute.

## Architecture diagram

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                          EXTERNAL SERVICES                                   │
│                                                                              │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐     │
│  │  Microsoft   │   │    SAP      │   │    SAP      │   │   Slack     │     │
│  │  Entra ID    │   │   Concur    │   │   Joule     │   │   (SaaS)    │     │
│  │  (SSO/IdP)   │   │  (Expense)  │   │  (AI Agent) │   │  (ChatOps)  │     │
│  └──────┬───────┘   └──────┬──────┘   └──────┬──────┘   └──────┬──────┘     │
│         │                  │                  │                  │            │
└─────────┼──────────────────┼──────────────────┼──────────────────┼────────────┘
          │                  │                  │                  │
┌─────────┼──────────────────┼──────────────────┼──────────────────┼────────────┐
│         ▼                  ▼                  ▼                  ▼            │
│  ┌─────────────────────────────────────────────────────────────────────┐      │
│  │              Azure Container Apps (Southeast Asia)                  │      │
│  │  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐              │      │
│  │  │  Odoo CE 18  │   │     n8n     │   │   Relay     │              │      │
│  │  │  (ERP SoR)   │◄─►│ (Automation)│◄─►│  (Webhook)  │              │      │
│  │  │  Port 8069   │   │             │   │             │              │      │
│  │  └──────┬───────┘   └──────┬──────┘   └─────────────┘              │      │
│  │         │                  │                                       │      │
│  └─────────┼──────────────────┼───────────────────────────────────────┘      │
│            │                  │                                               │
│  ┌─────────▼──────────────────▼───────────────────────────────────────┐      │
│  │                        PostgreSQL 16                                │      │
│  │                     (Odoo transactional DB)                         │      │
│  └────────────────────────────────────────────────────────────────────┘      │
│                                                                              │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐     │
│  │  Supabase    │   │    ADLS     │   │  Azure AI   │   │  Tableau    │     │
│  │  (SSOT/      │   │   Gen2     │   │  Foundry    │   │   (BI)      │     │
│  │  Control     │   │  (Data     │   │  (AI/ML     │   │             │     │
│  │  Plane)      │   │   Lake)    │   │  Compute)   │   │             │     │
│  └─────────────┘   └─────────────┘   └─────────────┘   └─────────────┘     │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐    │
│  │                    Azure Front Door (Edge / TLS / WAF)                │    │
│  │              Endpoint: ipai-fd-dev-ep-*.azurefd.net                   │    │
│  └──────────────────────────────────────────────────────────────────────┘    │
│                          AZURE PLATFORM                                      │
└──────────────────────────────────────────────────────────────────────────────┘
```

## System inventory

| # | System | Role | Owns | Runtime |
|---|--------|------|------|---------|
| 1 | **Microsoft Entra ID** | Identity provider | SSO, user federation, conditional access | SaaS |
| 2 | **SAP Concur** | Expense management | Travel and expense data, receipts, approvals | SaaS |
| 3 | **SAP Joule** | AI agent | Conversational AI for SAP ecosystem queries | SaaS |
| 4 | **Slack** | Team communication | Channels, messages, ChatOps commands | SaaS |
| 5 | **Odoo CE 18** | ERP system of record | Accounting, HR, CRM, inventory, purchases, sales | Azure Container Apps |
| 6 | **n8n** | Workflow automation | Event routing, scheduled jobs, webhook processing | Azure Container Apps |
| 7 | **Relay** | Webhook gateway | Inbound webhook validation, routing, replay | Azure Container Apps |
| 8 | **Supabase** | Control plane / SSOT | Auth, platform events, AI indexes, analytics serving, Edge Functions | Managed (external) |
| 9 | **ADLS Gen2** | Analytical data lake | Bronze/silver/gold data copies for BI and ML | Azure Storage |
| 10 | **Azure AI Foundry** | AI/ML compute | Model inference, embeddings, fine-tuning | Azure |
| 11 | **Tableau** | Business intelligence | Dashboards, reports, ad-hoc analysis | SaaS |
| 12 | **Azure Front Door** | Edge / CDN / WAF | TLS termination, routing, DDoS protection | Azure |

## Azure Container Apps layout

| Container App | Public hostname | Port | Purpose |
|---------------|-----------------|------|---------|
| `ipai-odoo-dev-web` | `erp.insightpulseai.com` | 8069 | Odoo CE 18 ERP |
| `ipai-auth-dev` | `auth.insightpulseai.com` | -- | Keycloak SSO |
| `ipai-mcp-dev` | `mcp.insightpulseai.com` | -- | MCP coordination |
| `ipai-ocr-dev` | `ocr.insightpulseai.com` | -- | Document OCR |
| `ipai-superset-dev` | `superset.insightpulseai.com` | -- | Apache Superset BI |
| `ipai-plane-dev` | `plane.insightpulseai.com` | -- | Plane project management |

All container apps run in the `cae-ipai-dev` environment in `southeastasia` region, behind Azure Front Door (`ipai-fd-dev`) for TLS and WAF.

## DNS and routing

DNS is managed through Cloudflare (authoritative DNS-only mode). The SSOT for all DNS records is `infra/dns/subdomain-registry.yaml`. Changes follow a YAML-first workflow:

1. Edit `infra/dns/subdomain-registry.yaml`
2. Run `scripts/dns/generate-dns-artifacts.sh`
3. Commit all generated artifacts
4. CI applies via Terraform on merge to `main`

!!! warning "Never edit DNS directly"
    Do not add records through the Cloudflare dashboard. Terraform overwrites manual changes on every apply.
