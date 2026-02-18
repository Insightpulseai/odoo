---
name: payment_providers
description: Online payment integration framework supporting 18+ providers with tokenization, manual capture, refunds, and express checkout.
metadata:
  author: Claude Agent
  version: "19.0"
  source: "Odoo 19.0 Official Documentation"
  extracted: "2026-02-18"
---

# payment_providers — Odoo 19.0 Skill Reference

## Overview

Odoo's payment providers framework enables customers to pay online via customer portals, eCommerce websites, sales orders, invoices, and subscriptions. It integrates with 18+ third-party payment services and supports bank payments (wire transfer, SEPA Direct Debit) and in-person payments (pay on site, cash on delivery). Sensitive card data is never stored in Odoo; all processing is delegated to PCI-compliant providers. Each provider links to configurable payment methods that can be enabled/disabled per provider.

## Key Concepts

- **Payment Provider**: Third-party service integration (Stripe, PayPal, Adyen, etc.) configured with API credentials and state (Disabled / Test Mode / Enabled).
- **Payment Method**: Specific payment instrument (credit card, bank transfer, etc.) linked to one or more providers. Can be activated/deactivated per provider.
- **Tokenization**: Saving customer payment method details as a token for future payments (subscriptions, repeat purchases). Provider must support it.
- **Manual Capture**: Two-step payment: authorize (reserve funds), then capture or void. Reduces refund fees for cancelled orders.
- **Express Checkout**: One-click payment via Google Pay / Apple Pay on eCommerce. Skips contact form, goes straight to confirmation.
- **Payment Journal**: Bank-type journal where provider payments are recorded. Default is the Bank journal; can set provider-specific outstanding accounts.
- **Payment Token**: Stored reference to a customer's payment method for recurring charges. Managed by customers via portal "Manage payment methods".

## Supported Providers

### Online Providers

| Provider | Payment Flow | Tokenization | Manual Capture | Refunds | Express Checkout |
|----------|-------------|--------------|----------------|---------|-----------------|
| Adyen | Odoo | Yes | Full & partial | Full & partial | No |
| Amazon Payment Services | Provider website | No | No | No | No |
| AsiaPay | Provider website | No | No | No | No |
| Authorize.Net | Odoo | Yes | Full only | Full only | No |
| Buckaroo | Provider website | No | No | No | No |
| DPO Pay | Provider website | No | No | No | No |
| Flutterwave | Provider website | Yes | No | No | No |
| Iyzico | Provider website | No | No | No | No |
| Mercado Pago | Provider website | No | No | No | No |
| Mollie | Provider website | No | No | No | No |
| Nuvei | Provider website | No | No | No | No |
| Paymob | Provider website | No | No | No | No |
| PayPal | Odoo | No | No | No | No |
| Razorpay | Odoo | Yes | Full only | Full & partial | No |
| Redsys | Provider website | No | No | No | No |
| Stripe | Odoo | Yes | Full only | Full & partial | Yes |
| Worldline | Provider website | Yes | No | No | No |
| Xendit | Odoo or provider | Yes* | No | No | No |

### Bank Payments
- **Wire Transfer**: Display payment info with reference; manual approval after bank receipt.
- **SEPA Direct Debit**: Customer registers mandate; account charged directly for future payments.

### In-Person Payments
- **Pay on Site**: Reserve online, pay at store pickup.
- **Cash on Delivery**: Pay upon delivery.

## Core Workflows

### 1. Enable a Payment Provider

1. Create account on provider's website; obtain API credentials.
2. Go to Accounting > Configuration > Payment Providers (or Website/Sales equivalent).
3. Select the provider card.
4. In Credentials tab, enter API keys (Publishable Key, Secret Key, etc.).
5. Set State to Enabled.
6. Provider is auto-published on website. Click Published button to unpublish if needed.

### 2. Configure Stripe (Most Common)

1. Ensure company email is configured in company settings.
2. Navigate to payment provider Stripe, click Connect Stripe.
3. Complete Stripe onboarding flow, confirm email.
4. For Odoo.sh/On-premise: enable developer mode, enter Publishable Key and Secret Key from Stripe dashboard (Developers > API Keys), click Generate your webhook.
5. Set State to Enabled.
6. To enable Apple Pay: Configuration tab > Allow Express Checkout > Enable Apple Pay.

### 3. Configure Payment Methods

1. On provider form, Configuration tab, click Enable Payment Methods.
2. Toggle methods on/off as needed.
3. Reorder methods via drag-and-drop (affects display order on website).
4. Advanced: enable developer mode, click method, go to Configuration tab for detailed settings.

### 4. Set Up Manual Capture

1. On provider form, Configuration tab, enable Capture Amount Manually.
2. Customer payment authorizes (reserves) funds but does not charge.
3. On related SO or invoice, click Capture Transaction to charge, or Void Transaction to release.

### 5. Process Refunds

1. Navigate to the customer payment record.
2. Click Refund button (no prior enablement needed, provider must support it).
3. Full or partial refund depending on provider capability.

## Technical Reference

### Key Models

| Model | Purpose |
|-------|---------|
| `payment.provider` | Provider configuration (credentials, state, features) |
| `payment.method` | Payment method definitions |
| `payment.token` | Stored customer payment tokens |
| `payment.transaction` | Individual payment transaction records |
| `account.payment` | Accounting payment linked to transaction |

### Key Fields on `payment.provider`

- `name`: Provider display name
- `code`: Provider technical identifier (e.g., `stripe`, `paypal`, `adyen`)
- `state`: `disabled`, `enabled`, `test`
- `company_id`: Company scope
- `journal_id`: Payment journal for accounting entries
- `allow_tokenization`: Boolean
- `capture_manually`: Boolean
- `allow_express_checkout`: Boolean
- `maximum_amount`: Max transaction amount (0 = unlimited)
- `available_currency_ids`, `available_country_ids`: Availability filters

### Key Fields on `payment.transaction`

- `state`: `draft`, `pending`, `authorized`, `done`, `cancel`, `error`
- `provider_id`, `payment_method_id`, `token_id`
- `amount`, `currency_id`, `partner_id`
- `provider_reference`: External transaction ID

### Configuration Paths

- Payment Providers: Accounting/Website/Sales > Configuration > Payment Providers
- Payment Methods: Accounting/Website/Sales > Configuration > Payment Methods
- Payment journal: Set on each provider's Configuration tab

## API / RPC Patterns

<!-- TODO: not found in docs — provider-specific API integration is handled internally by Odoo modules; no public JSON-RPC patterns documented for payment processing -->

## Version Notes (19.0)

- **Xendit**: New provider added, supports tokenization (with conditions), payment flow from Odoo or provider website.
- **Nuvei**: New provider added.
- **Paymob**: New provider added.
- **DPO Pay**: New provider added.
- **Iyzico**: New provider added.
- **Payment method brands**: Icons displayed on website are now driven by activated brands on each payment method, with drag-and-drop reordering.
- **Availability debug report**: In developer mode, a bug icon next to "Choose a payment method" shows a diagnostic report of provider/method availability.

## Common Pitfalls

- **Test mode should use a duplicate/test database** to avoid invoice numbering gaps. Test mode uses separate sandbox credentials, not production API keys.
- **Payment providers are auto-published** when enabled. If you do not want customers to see a provider yet, explicitly unpublish it after enabling.
- **Payment journal must be Bank type**. The same journal can serve multiple providers, but each provider must have one assigned. Only needed if Invoicing/Accounting app is installed.
- **Tokenization and express checkout** only work if both the provider and the payment method support the feature. Enabling it on an unsupported combination has no effect.
- **Manual capture reservations expire**: Providers release reserved funds after a provider-specific duration. Capture or void before the reservation lapses.
