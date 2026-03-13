---
title: Platform overview
description: What InsightPulse AI is, what it runs on, and how authority flows between systems.
---

# Platform overview

InsightPulse AI is an AI-first ERP platform purpose-built for the Philippine market. It runs on Odoo Community Edition 19 with OCA community modules and custom `ipai_*` extensions, deployed on Azure Container Apps in Southeast Asia.

## Key differentiators

| Differentiator | Detail |
|----------------|--------|
| **CE-only, no Enterprise licensing** | Zero Odoo EE license cost. Enterprise parity achieved through CE + OCA + custom `ipai_*` modules (target >= 80%). |
| **AI-native** | Claude Code agents, MCP servers, spec-kit methodology, and Azure AI Foundry provide AI assistance across development and operations. |
| **Azure-hosted** | Azure Container Apps with Azure Front Door for TLS termination, WAF, and global edge routing. |
| **BIR tax compliant** | Philippine Bureau of Internal Revenue compliance: TRAIN law withholding, SSS/PhilHealth/Pag-IBIG, BIR forms 1601-C, 2316, alphalist, and VAT returns. |
| **Medallion data architecture** | Bronze-Silver-Gold-Platinum data lake on Azure Data Lake Storage Gen2, with Supabase as the analytical serving layer. |

## Stack

```
Odoo CE 19.0         ERP system of record (accounting, HR, CRM, inventory)
OCA modules          Community-vetted extensions (reconciliation, financial reports, assets)
ipai_* modules       Custom InsightPulse AI modules (finance, AI, BIR compliance, connectors)
PostgreSQL 16        Odoo transactional database
Supabase             Control plane: Auth, Edge Functions, pgvector, Realtime, Vault
Azure Container Apps Runtime environment (Southeast Asia region)
Azure Front Door     Edge routing, TLS, WAF
Azure Data Lake Gen2 Analytical lake (medallion architecture)
Azure AI Foundry     AI model hosting and inference
n8n                  Workflow automation (self-hosted)
Slack                Team communication and ChatOps
```

## System authority model

Three systems share clear authority boundaries:

| System | Role | Owns |
|--------|------|------|
| **Supabase** | Single source of truth (SSOT) | Identity, auth, platform events, AI indexes, analytics serving layer, control plane metadata |
| **Odoo** | System of record (SoR) | Accounting entries, invoices, HR records, inventory, CRM, purchases, sales orders |
| **ADLS** | Analytical lake | Bronze/silver/gold data copies for BI and ML -- consumer-only, never writes back |

!!! warning "Hard rule"
    Supabase replicas of Odoo data are read-only. ADLS is consumer-only. Posted accounting entries in Odoo are immutable. External systems write to Odoo through controlled APIs using a draft-first pattern.

## Module philosophy

Apply this decision hierarchy when adding functionality:

```
1. Config    Use Odoo's built-in configuration and settings first.
2. OCA       Use a vetted OCA community module second.
3. Delta     Build a custom ipai_* module only for truly custom needs.
```

Custom modules follow the naming convention `ipai_<domain>_<feature>`:

- `ipai_finance_ppm` -- finance portfolio management
- `ipai_ai_core` -- AI framework and providers
- `ipai_bir_compliance` -- Philippine BIR tax compliance
- `ipai_slack_connector` -- Slack integration

All `ipai_*` modules use thin extensions that inherit existing Odoo models rather than creating parallel ones. Heavy analytics belong in Supabase and ADLS, not in Odoo.
