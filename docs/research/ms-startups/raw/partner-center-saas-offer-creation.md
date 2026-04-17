---
url: https://learn.microsoft.com/en-us/partner-center/marketplace-offers/create-new-saas-offer
title: Create a SaaS offer in Microsoft Marketplace
last_updated: 2025-09-25
audience: partner / publisher
lifecycle_stage: scale
capability_category: marketplace | GTM
fetched: 2026-04-15
---

# Create a SaaS offer in Microsoft Marketplace

## Prerequisites
- **Microsoft Marketplace account** in Partner Center
- **Microsoft Marketplace program enrollment** on the publisher account (verification required)
- **Publisher account** (IPAI already enrolled — MpnId 7097325 per `project_partner_center_verification`)

## Offer types within SaaS
- **Transactable** (sold through Microsoft — Microsoft facilitates license + billing)
  - Option A: Microsoft manages customer licenses (requires Graph API integration for eligibility checks)
  - Option B: Partner manages licenses (less Microsoft integration)
- **Listing-only** (contact-me OR free trial URL OR get-it-now free URL)
  - Conversion rule: can convert listing → transactable later; CANNOT convert transactable → listing

## Technical requirements (for transactable / non-contact-me)
- SaaS app authentication via **Microsoft Entra ID** (one-click authentication pattern on landing URL)
- Microsoft Graph API integration if Microsoft-managed license mode
- Subscription webhook for transactable offers
- Test/dev environment separate from prod offer

## Lead management
- Leads land in Partner Center Referrals workspace by default
- Optional CRM connections: Azure Table, Dynamics 365 CE, HTTPS endpoint, Marketo, Salesforce
- No direct Odoo connection (IPAI must use HTTPS endpoint → `ipai-odoo-connector` → `crm.lead`)

## Key fields at creation
- **Offer ID** — max 50 chars, lowercase + digits + hyphens/underscores, immutable after Create
- **Offer alias** — Partner Center display name, immutable after Create
- **Publisher association** — must be Marketplace-program-enrolled publisher

## Microsoft 365 app integration (optional)
- Link published Office add-in / Teams app / SharePoint Framework solutions to SaaS offer
- Rank order controls display priority on listing page

## IPAI application
- IPAI is already Partner Center enrolled (per memory)
- For Issue 29 (`ipai_odoo_on_aca` Marketplace publish): start as **listing-only** (contact-me) for private offer with TBWA; convert to transactable once transactable pricing decision is made
- Lead management: wire HTTPS endpoint → `ipai-odoo-connector` POST → `crm.lead` creation in Odoo
- Entra ID SaaS auth: already canonical path per CLAUDE.md Cross-Repo Invariant #2
