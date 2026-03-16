# Skill: Philippine Payment Gateways — DragonPay + GCash for BIR & Odoo

## Metadata

| Field | Value |
|-------|-------|
| **id** | `ph-payment-gateways` |
| **domain** | `integration` |
| **source** | https://www.dragonpay.ph/ , https://www.gcash.com/ |
| **extracted** | 2026-03-16 |
| **applies_to** | odoo, automations, agents |
| **tags** | payment, dragonpay, gcash, bir, philippines, gateway, disbursement |
| **secrets_required** | `DRAGONPAY_MERCHANT_ID`, `DRAGONPAY_PASSWORD`, `GCASH_APP_ID`, `GCASH_APP_SECRET` |

---

## Why Two Gateways

| Gateway | Strength | Use For |
|---------|----------|---------|
| **DragonPay** | Multi-channel aggregator (40+ channels, single API) | BIR tax payments, vendor payments, bank transfers |
| **GCash** | Largest mobile wallet in PH (66M+ users) | Employee reimbursements, petty cash, field collections |

Together they cover every PH payment scenario: bank, wallet, OTC, and credit card.

---

## DragonPay Integration

### Overview

| Detail | Value |
|--------|-------|
| Regulated by | Bangko Sentral ng Pilipinas (BSP) |
| Merchants | 400K+ |
| Monthly transactions | 200M+ |
| Payment channels | 40+ |
| Integration | Single REST API for all channels |

### Supported Channels

| Channel Type | Examples |
|-------------|---------|
| Online banking | BDO, BPI, UnionBank, Metrobank, LBP, PNB, RCBC, Security Bank |
| E-wallets | GCash, Maya, ShopeePay, Coins.ph |
| Credit/debit cards | Visa, Mastercard, JCB |
| Over-the-counter | 7-Eleven, SM Bills Payment, Bayad Center, Cebuana, LBC |
| QR Ph | InstaPay QR, PESONet |

### API Flow (Payment Collection)

```
1. Odoo creates payment request
    POST https://gw.dragonpay.ph/api/collect/v1/{txnId}/post
    {
        "Amount": 12500.00,
        "Currency": "PHP",
        "Description": "BIR Form 1601-C - March 2026",
        "Email": "finance@insightpulseai.com",
        "ProcId": "BOG"  // Bank channel code
    }

2. DragonPay returns payment URL or reference number
    → User completes payment via chosen channel

3. DragonPay sends webhook (postback) to n8n
    POST https://n8n.insightpulseai.com/webhook/dragonpay-callback
    {
        "txnid": "BIR-1601C-202603",
        "refno": "XXXXXXXXXXXX",
        "status": "S",  // S=Success, P=Pending, F=Failed
        "message": "Payment successful",
        "amount": 12500.00,
        "ccy": "PHP",
        "procid": "BOG",
        "digest": "<HMAC-SHA1>"
    }

4. n8n processes callback:
    → Verify HMAC digest
    → Create account.payment in Odoo
    → Update BIR filing status to "paid"
    → Log to ops.run_events
    → Notify Slack
```

### API Authentication

```
# HMAC-SHA1 digest for request verification
import hmac, hashlib

digest = hmac.new(
    DRAGONPAY_PASSWORD.encode(),
    f"{txnid}:{status}:{message}:{amount}".encode(),
    hashlib.sha1
).hexdigest()
```

### DragonPay Payment Modes (procId)

| Code | Channel | Type |
|------|---------|------|
| `BOG` | BDO Online | Online banking |
| `BPIB` | BPI Online | Online banking |
| `UBPB` | UnionBank | Online banking |
| `LBPA` | LandBank | Online banking |
| `MBTC` | Metrobank | Online banking |
| `GCSH` | GCash | E-wallet |
| `PYMY` | Maya/PayMaya | E-wallet |
| `711` | 7-Eleven | OTC |
| `BAYD` | Bayad Center | OTC |
| `CEBL` | Cebuana Lhuillier | OTC |
| `MLH` | M Lhuillier | OTC |
| `CC` | Credit Card | Card |

### Mass Payout API (Disbursement)

```
# For vendor payments, employee reimbursements
POST https://gw.dragonpay.ph/api/disburse/v1/payout
{
    "TxnId": "REIMB-EXP-2026-001",
    "Amount": 5000.00,
    "Currency": "PHP",
    "Description": "Expense reimbursement - John Doe",
    "BeneficiaryName": "JOHN DOE",
    "BeneficiaryAccount": "1234567890",
    "BankCode": "BDO",
    "Email": "john@insightpulseai.com"
}
```

---

## GCash Integration

### Overview

| Detail | Value |
|--------|-------|
| Users | 66M+ (largest PH mobile wallet) |
| Merchant network | 6M+ |
| Parent company | Mynt (Globe Fintech) |
| Regulated by | BSP |

### GCash Business Solutions

| Solution | Purpose | API? |
|----------|---------|------|
| **GCash Merchant QR** | Accept in-store payments | QR-based, no API needed |
| **GCash Online Payment** | Accept website/app payments | Yes — Checkout API |
| **GCash Express Send** | Disburse to GCash wallets | Yes — Disbursement API |
| **GCash Bill Payment** | Accept bill payments | Yes — Biller API |
| **GCash Webpay** | Payment gateway (via Webpay partner) | Yes |

### API Flow (Online Payment)

```
1. Odoo creates payment request
    POST https://api.gcash.com/v1/checkout
    Headers:
        X-App-Id: {GCASH_APP_ID}
        X-App-Secret: {GCASH_APP_SECRET}
    Body:
    {
        "amount": 5000.00,
        "currency": "PHP",
        "description": "Expense reimbursement",
        "reference_id": "REIMB-EXP-2026-001",
        "success_url": "https://erp.insightpulseai.com/payment/success",
        "failure_url": "https://erp.insightpulseai.com/payment/failure",
        "callback_url": "https://n8n.insightpulseai.com/webhook/gcash-callback"
    }

2. GCash returns checkout URL
    → User opens GCash app → confirms payment

3. GCash sends webhook to n8n
    POST https://n8n.insightpulseai.com/webhook/gcash-callback
    {
        "reference_id": "REIMB-EXP-2026-001",
        "status": "COMPLETED",
        "amount": 5000.00,
        "gcash_reference": "GCASH-XXXXX"
    }

4. n8n → Odoo account.payment → Slack notification
```

### GCash Express Send (Disbursement)

```
# For employee reimbursements directly to GCash wallet
POST https://api.gcash.com/v1/express-send
{
    "amount": 3500.00,
    "recipient_mobile": "09171234567",
    "reference_id": "REIMB-HR-2026-042",
    "description": "March expense reimbursement"
}
```

---

## Odoo Integration Architecture

### Payment Module: `ipai_payment_ph`

```python
# models/payment_provider_dragonpay.py
class PaymentProviderDragonpay(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(
        selection_add=[('dragonpay', 'DragonPay')],
        ondelete={'dragonpay': 'set default'},
    )
    dragonpay_merchant_id = fields.Char('Merchant ID')
    dragonpay_password = fields.Char('Password')

    def _dragonpay_create_transaction(self, amount, description, proc_id='BOG'):
        """Create DragonPay payment transaction."""
        # API call to DragonPay
        ...

# models/payment_provider_gcash.py
class PaymentProviderGcash(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(
        selection_add=[('gcash', 'GCash')],
        ondelete={'gcash': 'set default'},
    )
    gcash_app_id = fields.Char('App ID')
    gcash_app_secret = fields.Char('App Secret')
```

### n8n Workflows

| Workflow | Trigger | Actions |
|----------|---------|---------|
| `dragonpay-bir-payment.json` | Odoo BIR form posted | Create DragonPay txn → track status → update Odoo |
| `dragonpay-callback.json` | DragonPay webhook | Verify HMAC → create `account.payment` → update BIR status |
| `gcash-reimbursement.json` | Expense report approved | GCash Express Send → employee wallet → log payment |
| `gcash-callback.json` | GCash webhook | Verify → create `account.payment` → notify Slack |

### Payment Flow Routing

```
Payment request from Odoo
    ↓
Route by payment type:
    ├── BIR tax payment (>₱10,000)
    │   → DragonPay → online banking (LBP/BDO/BPI)
    │   → Reason: bank transfer for large tax payments
    │
    ├── Vendor payment (any amount)
    │   → DragonPay Mass Payout → vendor bank account
    │   → Reason: multi-bank disbursement
    │
    ├── Employee reimbursement (<₱50,000)
    │   → GCash Express Send → employee wallet
    │   → Reason: instant, no bank details needed
    │
    ├── Employee reimbursement (>₱50,000)
    │   → DragonPay Payout → employee bank account
    │   → Reason: GCash has transaction limits
    │
    └── Customer collection
        → DragonPay Checkout → multi-channel
        → Reason: customer chooses their preferred channel
```

---

## BIR Tax Payment Flow (Complete)

```
1. TaxPulse computes tax from Odoo journal entries
2. ipai_bir_tax_compliance generates form data
3. Finance reviews + approves in Odoo
4. Export eBIRForms XML → submit to BIR (manual)
5. BIR returns assessment / confirmation
6. Odoo creates payment request:
   → DragonPay API (LandBank channel for BIR)
   → Amount: computed tax due
   → Reference: "BIR-1601C-202603"
7. Finance completes bank payment via DragonPay redirect
8. DragonPay webhook → n8n:
   → Create account.payment in Odoo
   → Link to BIR form record
   → Update filing status: "filed" → "paid"
   → Log evidence to ops.run_events
   → Notify #finance Slack channel
9. Monthly reconciliation: match BIR payments to bank statement
```

---

## Secrets (Azure Key Vault)

```yaml
# Add to kv-ipai-dev
dragonpay-merchant-id: <from DragonPay merchant portal>
dragonpay-password: <from DragonPay merchant portal>
gcash-app-id: <from GCash Business portal>
gcash-app-secret: <from GCash Business portal>
```

---

## Estimated Integration Effort

| Component | Effort | Priority |
|-----------|--------|----------|
| DragonPay collection API (BIR payments) | 3 days | P0 |
| DragonPay webhook handler (n8n) | 1 day | P0 |
| GCash Express Send (reimbursements) | 2 days | P1 |
| GCash webhook handler (n8n) | 1 day | P1 |
| Odoo `ipai_payment_ph` module | 1 week | P1 |
| Payment routing logic | 2 days | P2 |
| Reconciliation workflow | 2 days | P2 |

**Total: ~3 weeks for both gateways end-to-end.**

---

---

## Inbound Payment Collection (Customer → IPAI)

### Supported Gateways

| Gateway | Type | API | Use Case | Odoo CE Support |
|---------|------|-----|----------|-----------------|
| **Stripe** | Global card + wallet | Stripe API (best-in-class) | International payments, subscriptions, SaaS billing | Native `payment_stripe` module |
| **PayPal** | Global wallet + card | PayPal REST API | International B2B/B2C, freelancer payments | Native `payment_paypal` module |
| **GCash** | PH mobile wallet | GCash Checkout API | Domestic PH collections | Via DragonPay (`GCSH` channel) or direct |
| **Maya** | PH mobile wallet + card | Maya Checkout API | Domestic PH collections + cards | Via DragonPay (`PYMY` channel) or direct |
| **DragonPay** | PH aggregator | DragonPay API | All PH channels via single integration | Custom `ipai_payment_ph` module |

### Odoo Native Payment Providers (CE — no EE needed)

```bash
# These are built into Odoo CE 19:
payment_paypal      # PayPal integration
payment_stripe      # Stripe integration
payment_custom      # Custom payment instructions (bank transfer, etc.)
```

### Stripe Integration (International + SaaS)

```python
# Already in Odoo CE — just configure:
# Settings → Payment Providers → Stripe
# Keys from https://dashboard.stripe.com/apikeys

# Stripe handles:
# - Credit/debit cards (Visa, MC, Amex, JCB)
# - Google Pay, Apple Pay
# - SEPA, iDEAL (EU)
# - Subscriptions + recurring billing
# - 3D Secure authentication
# - Webhook notifications
```

| Stripe Feature | Odoo CE Support | Use Case |
|---------------|----------------|----------|
| One-time payments | Native | Invoice payments, product purchases |
| Subscriptions | Native (Odoo subscriptions) | SaaS monthly/annual billing |
| Payment links | Native | Send payment link via email |
| Webhooks | Native | Auto-confirm payments in Odoo |
| Multi-currency | Native | USD, EUR, PHP, etc. |
| Refunds | Native | Credit note → refund via Stripe |

### PayPal Integration (International B2B)

```python
# Already in Odoo CE — just configure:
# Settings → Payment Providers → PayPal
# Credentials from https://developer.paypal.com/

# PayPal handles:
# - PayPal wallet payments
# - Credit/debit cards via PayPal
# - PayPal Business invoicing
# - International transfers
# - Buyer/seller protection
```

### Maya Integration (PH Cards + Wallet)

```
# Maya (formerly PayMaya) options:

# Option A: Via DragonPay (recommended — already integrated)
DragonPay procId = "PYMY"
# Covers Maya wallet + Maya-processed cards

# Option B: Direct Maya Checkout API
POST https://pg.maya.ph/checkout/v1/checkouts
Headers:
    Authorization: Basic {base64(secret_key + ':')}
Body:
{
    "totalAmount": {"value": 5000, "currency": "PHP"},
    "buyer": {"firstName": "John", "lastName": "Doe"},
    "redirectUrl": {
        "success": "https://erp.insightpulseai.com/payment/success",
        "failure": "https://erp.insightpulseai.com/payment/failure",
        "cancel": "https://erp.insightpulseai.com/payment/cancel"
    },
    "requestReferenceNumber": "INV-2026-001"
}
```

### Complete Payment Matrix

| Direction | Channel | Gateway | Priority |
|-----------|---------|---------|----------|
| **Outbound: BIR tax** | Bank transfer | DragonPay (LBP/BDO) | P0 |
| **Outbound: Vendor** | Bank transfer | DragonPay Mass Payout | P1 |
| **Outbound: Employee reimburse** | Mobile wallet | GCash Express Send | P1 |
| **Outbound: Employee reimburse (large)** | Bank transfer | DragonPay Payout | P2 |
| **Inbound: Customer (international)** | Card + wallet | **Stripe** (native Odoo) | P0 |
| **Inbound: Customer (international B2B)** | PayPal | **PayPal** (native Odoo) | P1 |
| **Inbound: Customer (PH wallet)** | GCash | DragonPay (`GCSH`) | P1 |
| **Inbound: Customer (PH cards)** | Maya | DragonPay (`PYMY`) or direct | P1 |
| **Inbound: Customer (PH bank)** | Online banking | DragonPay (multi-bank) | P2 |
| **Inbound: Customer (PH OTC)** | 7-Eleven, Bayad | DragonPay (OTC) | P2 |
| **SaaS billing** | Subscription | **Stripe** (recurring) | P0 |

### Modules to Install on Prod

| Module | Source | Purpose | Status |
|--------|--------|---------|--------|
| `payment_stripe` | Odoo CE (native) | Stripe payments | **Install now** |
| `payment_paypal` | Odoo CE (native) | PayPal payments | **Install now** |
| `payment_custom` | Odoo CE (native) | Bank transfer instructions | **Install now** |
| `ipai_payment_ph` | IPAI (to build) | DragonPay + GCash integration | **Build** (~3 weeks) |

### Configuration Steps (Stripe + PayPal)

```
1. Stripe:
   Settings → Payment Providers → Stripe → Activate
   - Publishable Key: from Stripe Dashboard
   - Secret Key: from Stripe Dashboard (store in Key Vault)
   - Webhook Secret: configure at Stripe → Developers → Webhooks
   - Webhook URL: https://erp.insightpulseai.com/payment/stripe/webhook

2. PayPal:
   Settings → Payment Providers → PayPal → Activate
   - Client ID: from PayPal Developer Portal
   - Client Secret: store in Key Vault
   - Webhook URL: auto-configured by Odoo

3. DragonPay (custom):
   - Register at dragonpay.ph
   - Get Merchant ID + Password
   - Store in Key Vault: dragonpay-merchant-id, dragonpay-password
   - Configure webhook: n8n.insightpulseai.com/webhook/dragonpay-callback

4. GCash (custom):
   - Register at GCash Business portal
   - Get App ID + App Secret
   - Store in Key Vault: gcash-app-id, gcash-app-secret
   - Configure webhook: n8n.insightpulseai.com/webhook/gcash-callback
```

### Concur Parity Impact

| Concur Feature | IPAI Equivalent | After Payment Integration |
|---------------|-----------------|--------------------------|
| Concur Pay | DragonPay + GCash + Stripe | **Full parity** |
| Expense reimbursement | GCash Express Send (instant) | **Better than Concur** (instant to wallet) |
| Vendor payment | DragonPay Mass Payout | **Parity** |
| Customer collection | Stripe + PayPal + DragonPay | **Better than Concur** (more channels) |
| BIR tax payment | DragonPay → LBP/BDO | **Unique to IPAI** (Concur has no BIR) |
| SaaS billing | Stripe subscriptions | **Parity** |

---

---

## Security Bank Business Account — Payment & Collection

### Why Security Bank Matters for IPAI

Security Bank's BusinessPlus Corporate Account provides **free BIR/SSS/PhilHealth/Pag-IBIG payments** through DigiBanker — making it the most cost-effective channel for government remittances. Combined with API-first architecture (Kong-powered), it's the best-positioned PH bank for Odoo integration.

### Account: BusinessPlus Corporate Account

| Feature | Detail |
|---------|--------|
| **eGov payments** | BIR, SSS, PhilHealth, Pag-IBIG — **FREE** |
| **ACPM (AutoCredit)** | Vendor/supplier payments — ₱5.00/txn |
| **InstaPay** | Real-time transfer to other banks — ₱20.00/txn (24/7) |
| **PESONet** | Batch transfer to other banks — ₱15.00/txn (same-day) |
| **Check Payments** | Manager's check issuance — via DigiBanker |
| **Payroll** | Employee payroll disbursement — bulk processing |
| **Remittance Manager** | Foreign + local telegraphic transfers |

### DigiBanker Cash Management Platform

| Service | Purpose | IPAI Use |
|---------|---------|----------|
| **eGov Facility** | Pay BIR/SSS/PhilHealth/Pag-IBIG online | **Primary BIR tax payment channel** |
| **EFPS RealTime** | File corporate taxes in advance via eFPS | **Direct BIR filing integration** |
| **SSS RealTime** | Employee SSS contributions + loan repayments | Payroll compliance |
| **PhilHealth EPRS** | Monthly PhilHealth premium remittance | Payroll compliance |
| **AutoCredit Payments Manager** | Automated vendor payments + multi-auth | Vendor AP automation |
| **Receivables Manager** | Payment collection from customers | AR collection |
| **Check Payments Manager** | Request + release manager's checks | Check payments |
| **Payroll Solutions** | Employee salary disbursement | HR payroll |
| **Liquidity Management** | Cash position monitoring | Treasury |
| **Corporate Utility ePayment** | Utility bill payments | Ops cost management |

### API Integration

Security Bank has invested in **API-first architecture** (powered by Kong) for SME and corporate offerings. API-based clients can access fund transfer services through their own front-end systems.

| API Capability | Status | Integration Method |
|---------------|--------|-------------------|
| Fund transfers (InstaPay/PESONet) | Available | API-based front-end access |
| eGov payments (BIR/SSS) | Available via DigiBanker | Portal + potential API |
| AutoCredit (vendor payments) | Available | API or DigiBanker portal |
| Payment status/notifications | Available | Webhook or polling |
| Account balance inquiry | Available | API |

**Note**: Security Bank's API access requires corporate onboarding and NDA. Not a public developer portal like Stripe. Contact: relationship manager or digital banking team.

### Transaction Fees (BusinessPlus)

| Transaction | Fee | Note |
|------------|-----|------|
| BIR payment | **FREE** | Via eGov facility |
| SSS payment | **FREE** | Via SSS RealTime |
| PhilHealth payment | **FREE** | Via PhilHealth EPRS |
| Pag-IBIG payment | **FREE** | Via eGov facility |
| AutoCredit (vendor) | ₱5.00 | Per transaction |
| InstaPay (real-time) | ₱20.00 | 24/7, to any bank |
| PESONet (batch) | ₱15.00 | Same-day credit |
| eGC (gift card) | ₱50.00 | Per transaction |

### Security Bank vs DragonPay for BIR Payments

| Criteria | Security Bank eGov | DragonPay → LBP/BDO |
|----------|-------------------|---------------------|
| BIR payment fee | **FREE** | DragonPay fee applies |
| eFPS integration | **Direct** (EFPS RealTime) | Indirect (bank redirect) |
| Automation | Portal-based (API for transfers) | Full API |
| Multi-bank routing | Security Bank only | 40+ channels |
| Government compliance | DigiBanker is BSP-preferred | Aggregator |

**Recommendation**: Use **Security Bank eGov** as the **primary** BIR/SSS/PhilHealth payment channel (free). Use **DragonPay** as the fallback and for multi-channel customer collections.

### Revised Payment Routing

```
Payment request from Odoo
    ↓
Route by payment type:
    ├── BIR tax payment
    │   → Security Bank eGov (FREE, direct eFPS)
    │   → Fallback: DragonPay → LBP/BDO
    │
    ├── SSS / PhilHealth / Pag-IBIG
    │   → Security Bank eGov (FREE)
    │
    ├── Vendor payment (domestic)
    │   → Security Bank AutoCredit (₱5/txn)
    │   → Bulk: Security Bank PESONet (₱15/txn)
    │
    ├── Employee reimbursement (<₱50K)
    │   → GCash Express Send (instant to wallet)
    │   → Security Bank InstaPay (₱20/txn, to any bank)
    │
    ├── Employee payroll
    │   → Security Bank Payroll Solutions (bulk)
    │
    ├── Customer collection (international)
    │   → Stripe (native Odoo)
    │
    ├── Customer collection (PH)
    │   → DragonPay (multi-channel)
    │   → Security Bank Collect (receivables)
    │
    └── SaaS subscription billing
        → Stripe (recurring)
```

### Odoo ↔ Security Bank Integration

```
Tier 1 (Now — manual but free):
  Odoo computes BIR tax → Finance logs into DigiBanker → pays via eGov → records in Odoo

Tier 2 (Next — semi-automated):
  Odoo computes → n8n generates payment instruction file → uploads to DigiBanker → callback → Odoo records

Tier 3 (Target — API-automated):
  Odoo computes → API call to Security Bank → auto-payment → webhook → Odoo records
  (requires corporate API onboarding with Security Bank)
```

### Security Bank Secrets (Azure Key Vault)

```yaml
# Add to kv-ipai-dev when API access is onboarded
secbank-company-id: <corporate ID>
secbank-api-key: <API key from SB digital banking>
secbank-api-secret: <API secret>
secbank-digibanker-user: <authorized DigiBanker user>
```

---

## Complete Payment Stack Summary

| Channel | Direction | Use For | Fee | Priority |
|---------|-----------|---------|-----|----------|
| **Security Bank eGov** | Out | BIR/SSS/PhilHealth/Pag-IBIG | **FREE** | **P0** |
| **Security Bank ACPM** | Out | Vendor payments | ₱5/txn | P1 |
| **Security Bank Payroll** | Out | Employee salaries | Bulk rate | P1 |
| **GCash Express Send** | Out | Employee reimbursements | Per txn | P1 |
| **DragonPay Payout** | Out | Multi-bank disbursement | Per txn | P2 |
| **Stripe** | In | International cards + SaaS billing | 2.9% + ₱15 | **P0** |
| **PayPal** | In | International B2B | 3.9% + fixed | P1 |
| **DragonPay Collect** | In | PH multi-channel (banks, wallets, OTC) | Per txn | P1 |
| **Security Bank Collect** | In | PH receivables | Bulk rate | P2 |

---

## Related Skills

Sources:
- [DigiBanker Features](https://www.securitybank.com/business/digibanker-cash-management/features/)
- [BusinessPlus Corporate Account](https://www.securitybank.com/business/accounts/)
- [Security Bank Collect](https://www.securitybank.com/business/collect/)
- [DigiBanker Cash Management](https://www.securitybank.com/business/digibanker-cash-management/)
- [Security Bank API-First Innovation](https://konghq.com/customer-stories/security-bank-customer-story)
- [Security Bank + ACI Payments Platform](https://investor.aciworldwide.com/news-releases/news-release-details/security-bank-teams-aci-worldwide-revolutionize-real-time)
- [Corporate Utility ePayment](https://www.securitybank.com/business/digibanker-cash-management/features/corporate-utility-epayment/)

- [bir-eservices](../../odoo/bir-eservices/SKILL.md) — BIR electronic filing systems
- [taxpulse-ph-pack](../../odoo/taxpulse-ph-pack/SKILL.md) — Tax computation engine
- [sap-concur-parity](../../industries/sap-concur-parity/SKILL.md) — Expense/payment parity
- [n8n-odoo-supabase-etl](../n8n-odoo-supabase-etl/SKILL.md) — Workflow orchestration
- [odoo19-expenses](../../odoo/odoo19-expenses/SKILL.md) — Expense workflow
