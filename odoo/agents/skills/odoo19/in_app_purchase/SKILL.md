---
name: in_app_purchase
description: Manage In-App Purchase (IAP) credits for optional Odoo services — SMS, OCR, lead mining, snailmail, and more.
metadata:
  author: Claude Agent
  version: "19.0"
  source: "Odoo 19.0 Official Documentation"
  extracted: "2026-02-18"
---

# in_app_purchase — Odoo 19.0 Skill Reference

## Overview

In-App Purchases (IAP) are optional, credit-based services that enhance an Odoo database. Services include SMS messaging, Documents Digitization (OCR/AI), Partner Autocomplete, Lead Generation, Snailmail (postal), and Signer Identification (itsme). IAP services are pre-integrated — no configuration is needed to start using them. Each service consumes prepaid credits purchased in packs from the Odoo IAP Catalog. Enterprise users with valid subscriptions receive free trial credits. Finance and operations teams manage credit balances and low-credit alerts.

## Key Concepts

- **IAP (In-App Purchase)**: Credit-based optional service provided by Odoo or third parties.
- **IAP credits**: Prepaid units consumed when an IAP service is used. Purchased in packs (Starter, Standard, Advanced, Expert).
- **IAP Catalog**: Marketplace at `iap.odoo.com/iap/all-in-app-services` listing all available IAP services.
- **Low-credit notification**: Email alert triggered when credit balance falls below a configured threshold.
- **IAP Account**: Per-service account record in Odoo tracking credit balance and alert settings.

## IAP Services (Odoo-provided)

| Service | Purpose |
|---------|---------|
| Documents Digitization | OCR + AI for vendor bills, expenses, resumes |
| Partner Autocomplete | Auto-populate contact records with corporate data |
| SMS | Send SMS text messages from the database |
| Lead Generation | Generate leads from criteria; convert web visitors to opportunities |
| Snailmail | Send invoices and follow-up reports by postal mail worldwide |
| Signer identification (itsme) | Identity verification for Odoo Sign signatories (Belgium, Netherlands) |

## Core Workflows

### 1. Use an IAP service

1. Navigate to the relevant feature (e.g., click the SMS icon next to a contact's phone number).
2. Use the service as prompted (compose SMS, digitize document, etc.).
3. Credits are automatically deducted.
4. If insufficient credits, Odoo prompts to purchase more.

### 2. Check credit balance and buy credits

1. Settings > Contacts section > **Odoo IAP** > click **View My Services**.
2. The IAP Account page lists all services with current balances.
3. Click a service > **Buy Credit**.
4. A new tab opens to the IAP Catalog. Select a credit pack and complete payment.

### 3. Set up low-credit email alerts

1. Settings > Contacts section > **Odoo IAP** > **View My Services**.
2. Click the desired IAP service.
3. On the Account Information page, set the **Email Alert Threshold** (credit amount).
4. In the **Email Alert Recipients** field, select which users receive the alert.

## Technical Reference

### Models

| Model | Purpose |
|-------|---------|
| `iap.account` | IAP service account with credit balance |

### Key Fields on `iap.account`

| Field | Purpose |
|-------|---------|
| `service_name` | IAP service identifier |
| `account_token` | Authentication token for IAP service |
| `balance` | Current credit balance |
| `warn_me` | Low-credit threshold |

### Menu Paths

- `Settings > Contacts > Odoo IAP > View My Services`
- IAP Account > Account Information > Buy Credit
- IAP Account > Account Information > Email Alert Threshold / Recipients

### Credit Pack Examples (SMS)

| Pack | Credits |
|------|---------|
| Starter | 10 |
| Standard | 100 |
| Advanced | 500 |
| Expert | 1,000 |

### External URLs

- IAP Catalog: `https://iap.odoo.com/iap/all-in-app-services`
- SMS Pricing FAQ: `https://iap-services.odoo.com/iap/sms/pricing`

## API / RPC Patterns

<!-- TODO: not found in docs -->

## Version Notes (19.0)

<!-- TODO: not found in docs — no explicit 18 vs 19 breaking changes listed in RST source -->

## Common Pitfalls

- **Credits are per-service**: Each IAP service has its own credit pool. SMS credits cannot be used for Lead Generation, etc.
- **Free trial credits**: Only available to Enterprise users with valid subscriptions (including demo/training/educational/one-app-free databases).
- **SMS cost varies by destination**: Credit consumption depends on message length and the recipient's country.
- **No refunds on credits**: Purchased IAP credits are non-refundable. Verify the service meets needs during the free trial period.
- **Service availability**: Third-party IAP services may have their own terms and limitations beyond Odoo's control.
