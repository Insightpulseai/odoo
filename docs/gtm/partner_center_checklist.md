# Checklist: Microsoft Commercial Marketplace Submission
**Target**: Pulser for Odoo (Q3 2026 GTM)
**Status**: TECHNICAL READY — PENDING ADMINISTRATIVE SUBMISSION

This checklist maps the engineering and identity artifacts synchronized during the **Ignition Phase** to the specific tabs in the Microsoft Partner Center.

## 1. Technical Configuration Tab
- [ ] **SaaS Fulfillment URL**: Use `https://erp.insightpulseai.com/api/marketplace/webhook`
- [ ] **Technical Contact**: verified engineering lead (tbwa@insightpulseai.com)
- [ ] **Entra ID Tenant ID**: `ceoinsightpulseai.onmicrosoft.com`
- [ ] **Entra ID App ID**: Use the ID registered for `ipai-marketplace-fulfillment-bot-prod` (See [app_registrations.azure_native.yaml](../../ssot/entra/app_registrations.azure_native.yaml))

## 2. Offer Listing Tab (Marketing)
- [ ] **Offer Name**: Pulser for Odoo
- [ ] **Offer Summary**: "Intelligent AI-on-Azure wrapper for Odoo 18.0 CE." (See [one_pager.md](one_pager.md))
- [ ] **Landing Page**: `https://w9studio.net/onboarding/marketplace`
- [ ] **Demo Storyboard**: Reference [demo_storyboard.md](demo_storyboard.md) for screenshots and flow.

## 3. Plan Configuration (Transactable)
- [ ] **Foundational Plan**: $49.00/mo (SKU: `pulser-odoo-foundational`)
- [ ] **Growth Plan**: $199.00/mo (SKU: `pulser-odoo-pro`)
- [ ] **Enterprise Plan**: $999.00/mo (SKU: `pulser-odoo-enterprise`)
- Refer to [marketplace_plans.yaml](../../platform/ssot/gtm/marketplace_plans.yaml) for full entitlement list per tier.

## 4. CSP Engagement (Co-sell)
- [ ] **Solution Area**: AI Business Solutions
- [ ] **Sales One-Pager**: Attach [one_pager.md](one_pager.md) as the primary PDF document.
- [ ] **Customer Case Study**: Use the "Retail Expansion ROI" scene from the [demo_storyboard.md](demo_storyboard.md) as the narrative template.

---
🛡️ **Engineering Sign-off**: All technical endpoints, webhooks, and identity registrations were verified on 2026-04-18.
