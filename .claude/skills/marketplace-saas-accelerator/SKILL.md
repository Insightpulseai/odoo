---
name: marketplace-saas-accelerator
description: Deploy and configure Microsoft's SaaS Accelerator for marketplace offers. Pre-built landing page, fulfillment webhook, subscription management — eliminates custom development for marketplace technical integration.
---

# SaaS Accelerator Deployment

## When to Use
- User needs to build marketplace landing page and webhook
- User asks about SaaS fulfillment API implementation
- User wants to speed up marketplace technical integration
- User asks about subscription management for marketplace offers

## What SaaS Accelerator Provides

```
Pre-built (no custom code needed):
├── Landing page (customer activation after purchase)
├── Webhook handler (all marketplace lifecycle events)
├── Publisher admin portal (manage subscriptions)
├── Customer self-service portal
├── Email notifications (subscription events)
├── SQL database (subscription state)
├── Azure AD SSO integration
└── All Azure-native (App Service + SQL + AD)
```

## Prerequisites

```
✅ Azure subscription (eba824fb for IPAI)
✅ Azure AD tenant (402de71a for IPAI)
✅ Partner Center offer created (offer ID needed)
✅ Azure CLI authenticated (az login)
```

## Deploy

### Option A: One-Click (Azure Portal)

```
1. Go to: github.com/Azure/Commercial-Marketplace-SaaS-Accelerator
2. Click "Deploy to Azure" button
3. Fill in parameters:
   - Subscription: Microsoft Azure Sponsorship
   - Resource Group: rg-ipai-dev-platform (or create new)
   - Region: Southeast Asia
   - App Name: ipai-marketplace-saas
   - SQL Admin Password: (generate, store in Key Vault)
   - Publisher AD Tenant: 402de71a-87ec-4302-a609-fb76098d1da7
4. Deploy (~10 minutes)
```

### Option B: CLI

```bash
az deployment group create \
  --resource-group rg-ipai-dev-platform \
  --template-uri https://raw.githubusercontent.com/Azure/Commercial-Marketplace-SaaS-Accelerator/main/deployment/Templates/deploy.json \
  --parameters \
    webAppNamePrefix=ipai-marketplace \
    sqlAdminLoginPassword=<from-key-vault> \
    publisherAdTenantId=402de71a-87ec-4302-a609-fb76098d1da7 \
    publisherAdApplicationId=<marketplace-app-registration-id>
```

## Post-Deploy Configuration

### 1. Register App in Azure AD
```
Azure Portal → Azure AD → App registrations → New
  Name: "Pulser Marketplace SaaS"
  Redirect URI: https://ipai-marketplace-saas.azurewebsites.net/
  API permissions: None needed (uses marketplace token)
  Client secret: generate, store in Key Vault
```

### 2. Configure in Partner Center
```
Partner Center → Pulser for Odoo offer → Technical configuration
  Landing page URL: https://ipai-marketplace-saas.azurewebsites.net/
  Connection webhook: https://ipai-marketplace-saas.azurewebsites.net/api/webhook
  Azure AD tenant: 402de71a-87ec-4302-a609-fb76098d1da7
  Azure AD app: <app-registration-id>
```

### 3. Configure Subscription Actions
In the SaaS Accelerator admin portal, define what happens for each event:

```
Subscribe → send email to jake@insightpulseai.com
            "New customer! Provision Odoo instance for {customer}"
            (manual initially, automate later)

Unsubscribe → send email
              "Customer leaving. Decommission within 30 days"

Suspend → disable Odoo access for tenant

Reinstate → re-enable Odoo access

ChangePlan → update subscription tier in Odoo
```

### 4. Customize Landing Page (Optional)
The default landing page works but is generic. Customize:
```
Clone repo → modify Views/Home/Index.cshtml
  Add: InsightPulseAI branding
  Add: "Welcome to Pulser for Odoo" messaging
  Add: Plan details display
  Deploy updated version
```

## Test the Flow

```
1. Partner Center → Offer → Preview
2. Click "Get it now" as test customer
3. Verify: redirected to landing page
4. Verify: subscription shows in admin portal
5. Verify: webhook fired (check App Service logs)
6. Verify: email notification received
7. Activate subscription in admin portal
8. Verify: customer can access Odoo
```

## Architecture

```
AppSource / Azure Marketplace
  → Customer clicks "Get it now"
    → Microsoft provisions subscription
      → Redirects to SaaS Accelerator landing page
        → Landing page resolves marketplace token
          → Shows activation UI to customer
            → Calls Marketplace Fulfillment API to activate
              → Webhook notifies you of all lifecycle events
                → You provision/manage Odoo tenant
```

## Cost

SaaS Accelerator runs on:
- App Service (Basic B1): ~$13/month
- SQL Database (Basic): ~$5/month
- Total: ~$18/month

Negligible compared to the weeks of development it saves.

## Reference
- Source: github.com/Azure/Commercial-Marketplace-SaaS-Accelerator
- Video course: github.com/microsoft/Mastering-the-Marketplace (SaaS Accelerator section)
- API docs: learn.microsoft.com/en-us/partner-center/marketplace-offers/partner-center-portal/pc-saas-fulfillment-api-v2
