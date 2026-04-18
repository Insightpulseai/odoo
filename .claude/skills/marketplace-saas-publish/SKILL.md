---
name: marketplace-saas-publish
description: End-to-end guide for publishing a SaaS offer on Microsoft AppSource/Azure Marketplace. Covers Partner Center setup, offer creation, technical integration, listing content, and certification. Based on Microsoft's Mastering the Marketplace curriculum.
---

# Marketplace SaaS Offer Publishing

## When to Use
- User asks to create, publish, or configure a marketplace offer
- User asks about SaaS fulfillment API, landing pages, or webhooks
- User asks about Partner Center offer configuration
- User asks about marketplace certification or review process

## Prerequisites Check
Before starting, verify:
```
✅ Partner Center account (verified, enrolled in Marketplace program)
✅ D-U-N-S number (verified)
✅ Payout profile configured (bank account + W-8BEN-E)
✅ Azure subscription (for SaaS Accelerator deployment)
✅ Product ready for listing
```

IPAI Status:
- Partner Center: Authorized (MPN 7097326)
- D-U-N-S: 719209694
- Payout: NOT YET CONFIGURED — must do before publishing

## Step 1: Create Offer in Partner Center

```
Partner Center → Marketplace offers → + New offer
→ Select: "Software as a Service (SaaS)"
→ Offer ID: "pulser-for-odoo" (cannot change after creation)
→ Offer alias: "Pulser for Odoo"
→ Create
```

## Step 2: Offer Setup

### Properties
- Categories: select up to 2 primary + 2 subcategories
- Recommended: "Business Applications" → "ERP" and "AI + Machine Learning" → "AI Solutions"
- Industries: select relevant (Financial Services, Professional Services, Media)

### Offer Listing
- **Name:** Pulser for Odoo
- **Search summary (100 chars max):** AI-powered operations platform for Odoo CE — finance, projects, compliance
- **Description (3000 chars):** Use marketplace HTML formatting
- **Privacy policy URL:** https://insightpulseai.com/privacy
- **Support URL:** https://insightpulseai.com/support
- **Screenshots:** 5 required (1280x720 or 1920x1080)
- **Videos:** optional but recommended (YouTube or Vimeo link)

### Pricing and Availability
- **Markets:** Select countries (start with Philippines, expand later)
- **Pricing model:** Flat rate per user/month
- **Plans:** Create Starter ($29), Growth ($49), Scale ($39)
- **Free trial:** Enable 14-day free trial

### Technical Configuration
- **Landing page URL:** https://insightpulseai.com/marketplace/activate
- **Connection webhook:** https://insightpulseai.com/api/marketplace/webhook
- **Azure AD tenant ID:** 402de71a-87ec-4302-a609-fb76098d1da7
- **Azure AD app ID:** (create app registration for marketplace)

### Legal
- **Use Microsoft Standard Contract:** YES (simplest — no custom EULA needed)
- **Amendment:** optional, add if needed

## Step 3: Technical Integration

### SaaS Fulfillment API v2
Microsoft requires your app to implement these webhook endpoints:

```
POST /api/marketplace/webhook
  Actions to handle:
  ├── Subscribe      → provision new tenant
  ├── Unsubscribe    → decommission tenant
  ├── Suspend        → pause access
  ├── Reinstate      → resume access
  ├── ChangePlan     → upgrade/downgrade
  └── ChangeQuantity → adjust seat count
```

### Landing Page Flow
```
Customer clicks "Get it now" on AppSource
  → Microsoft redirects to YOUR landing page with marketplace token
  → Your page calls Marketplace API to resolve the token
  → Shows: "Welcome! Setting up your Pulser instance"
  → You provision their Odoo instance (manual initially, automate later)
  → Activate subscription via Marketplace API
  → Customer gets access
```

### Shortcut: SaaS Accelerator
Instead of building from scratch, deploy Microsoft's pre-built solution:
```
github.com/Azure/Commercial-Marketplace-SaaS-Accelerator
```
One-click deploy to Azure. Provides landing page + webhook + admin portal.

## Step 4: Certification Submission

### Pre-submission checklist
- [ ] All listing fields completed
- [ ] 5+ screenshots uploaded
- [ ] Privacy policy URL accessible
- [ ] Support URL accessible
- [ ] Landing page functional
- [ ] Webhook responds to all lifecycle events
- [ ] SSO via Azure AD works
- [ ] Test purchase flow end-to-end

### Submit
Partner Center → Offer overview → Review and publish → Publish

### Review timeline
- Automated validation: minutes
- Certification review: 5-10 business days
- If issues found: fix and resubmit (adds 3-5 days)

## Step 5: Post-Publication

- [ ] Verify offer appears on AppSource/Azure Marketplace
- [ ] Test customer purchase flow
- [ ] Monitor Partner Center analytics
- [ ] Plan for 6-month recertification
- [ ] Enable Marketplace Rewards when eligible

## Reference
- Mastering the Marketplace: github.com/microsoft/Mastering-the-Marketplace
- SaaS Accelerator: github.com/Azure/Commercial-Marketplace-SaaS-Accelerator
- SaaS Fulfillment API v2: learn.microsoft.com/en-us/partner-center/marketplace-offers/partner-center-portal/pc-saas-fulfillment-api-v2
- Azure Skills: github.com/microsoft/azure-skills
