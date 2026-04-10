---
title: "Odoo on Cloud — Platform Overview"
kb_scope: "general-kb"
group_ids: ["group-guid-placeholder"]
last_updated: "2026-03-15"
---

# Odoo on Cloud — Platform Overview

## What Is Odoo on Cloud?

Odoo on Cloud is InsightPulse AI's managed deployment of **Odoo Community Edition 18.0**, hosted on Azure Container Apps and designed for small-to-medium enterprises in the Philippines and Southeast Asia. It delivers a fully integrated ERP suite without the licensing costs of Odoo Enterprise, augmented by OCA (Odoo Community Association) modules and custom InsightPulse AI extensions.

### Key Differentiators

- **Zero Enterprise License Fees**: Built entirely on Odoo CE 18.0 with OCA modules to close feature gaps.
- **Managed Infrastructure**: Azure Container Apps with Azure Front Door for global edge routing, TLS termination, and WAF protection.
- **AI-Augmented Operations**: Integrated Copilot for advisory and action modes within the Odoo interface.
- **Philippine Compliance Built-In**: BIR tax forms, VAT handling, withholding tax automation, and localized chart of accounts.
- **Automation Layer**: n8n workflow engine for cross-system integrations with Slack, email, and external APIs.

---

## Included Modules

### Core Business Modules

| Module | Description | Status |
|--------|-------------|--------|
| **Accounting** | Full double-entry accounting, journal entries, bank reconciliation, financial reports | Production |
| **Invoicing** | Customer invoices, vendor bills, payment tracking, credit notes | Production |
| **Sales** | Quotations, sales orders, order-to-invoice workflow, pricing rules | Production |
| **Purchase** | Purchase orders, vendor management, procurement rules, RFQs | Production |
| **Inventory** | Warehouse management, stock moves, barcode support, multi-location | Production |
| **CRM** | Lead and opportunity management, pipeline stages, activity scheduling | Production |
| **Project** | Project management, task tracking, timesheets, Gantt views | Production |
| **HR** | Employee records, departments, job positions, org chart | Production |
| **Website** | CMS, product catalog, contact forms, SEO tools | Production |
| **Manufacturing** | Bill of materials, manufacturing orders, work orders, routing | Production |

### OCA Enhancement Modules

The platform includes curated OCA modules that bring the system to near Enterprise-level capability:

#### Base & UX Enhancements
- **web_responsive** — Mobile-friendly responsive backend interface
- **web_dialog_size** — Resizable dialog windows for better form editing
- **mail_debrand** — Removes Odoo branding from outbound emails
- **report_xlsx** — Excel export capability for all reports
- **web_environment_ribbon** — Visual environment indicator (dev/staging/production)
- **password_security** — Enhanced password policies and complexity requirements
- **disable_odoo_online** — Removes Enterprise upgrade prompts
- **remove_odoo_enterprise** — Cleans Enterprise-only menu items from CE

#### Accounting Enhancements
- **account_reconcile_oca** — Advanced bank reconciliation with matching rules
- **account_financial_report** — Trial balance, general ledger, partner ledger, aged reports
- **mis_builder** — Management Information System report builder
- **account_asset_management** — Fixed asset depreciation tracking
- **currency_rate_update** — Automatic exchange rate updates from BSP/ECB
- **account_move_budget** — Budget management and variance reporting
- **account_tax_balance** — Tax balance reporting per period

#### Sales Enhancements
- **sale_order_type** — Sales order categorization (standard, blanket, consignment)
- **sale_cancel_reason** — Track cancellation reasons for analytics
- **sale_delivery_state** — Delivery status tracking on sales orders
- **sale_order_line_price_history** — Price history for informed quoting

#### Security & Audit
- **auditlog** — Comprehensive audit trail for compliance
- **auth_totp_ip_check** — IP-restricted two-factor authentication
- **base_user_role** — Role-based access control management
- **sentry** — Error tracking and performance monitoring integration

### Custom InsightPulse AI Modules (ipai_*)

These modules address gaps not covered by Odoo CE or OCA:

- **ipai_ai_copilot** — AI assistant integration within the Odoo interface
- **ipai_finance_ppm** — Philippine Payment Method handling (GCash, Maya, bank transfers)
- **ipai_slack_connector** — Slack integration for notifications and approvals
- **ipai_ai_tools** — AI-powered document processing and data extraction

---

## Deployment Architecture

### Infrastructure Stack

```
User Request
    |
    v
Azure Front Door (TLS, WAF, CDN)
    |
    v
Azure Container Apps (cae-ipai-dev)
    |
    +-- ipai-odoo-dev-web (Odoo CE 18.0, port 8069)
    +-- ipai-auth-dev (Keycloak SSO)
    +-- ipai-mcp-dev (MCP coordination)
    +-- ipai-ocr-dev (Document OCR)
    +-- ipai-superset-dev (Apache Superset BI)
    |
    v
Azure Database for PostgreSQL 16
    |
    v
Azure Key Vault (secrets management)
```

### Access Points

| Service | URL | Purpose |
|---------|-----|---------|
| ERP | `erp.insightpulseai.com` | Odoo CE 18.0 web interface |
| SSO | `auth.insightpulseai.com` | Keycloak single sign-on |
| BI | `superset.insightpulseai.com` | Apache Superset dashboards |
| OCR | `ocr.insightpulseai.com` | Document processing API |
| Automation | `n8n.insightpulseai.com` | n8n workflow engine |

### Security Model

- **TLS Everywhere**: All traffic encrypted via Azure Front Door managed certificates.
- **WAF Protection**: Azure Web Application Firewall with OWASP 3.2 ruleset.
- **SSO**: Keycloak with OIDC for centralized authentication.
- **RBAC**: Odoo's built-in access control plus OCA `base_user_role` for role management.
- **Audit Trail**: OCA `auditlog` module tracks all data modifications.
- **Secret Management**: Azure Key Vault with managed identity binding. No hardcoded credentials.

---

## Multi-Company Support

Odoo on Cloud supports multiple companies within a single instance:

- **Shared User Base**: Users can belong to multiple companies with different roles.
- **Company-Specific Data**: Chart of accounts, tax configurations, and fiscal positions per company.
- **Inter-Company Transactions**: Automated journal entries for inter-company operations.
- **Consolidated Reporting**: Cross-company financial reports via MIS Builder.

---

## Data and Backup

- **Database**: PostgreSQL 16 with point-in-time recovery (PITR) enabled.
- **Backup Schedule**: Automated daily backups with 30-day retention.
- **File Storage**: Azure Blob Storage for attachments and documents.
- **Export**: Full data export available via Odoo's built-in export or direct database access.

---

## Supported Industries

The platform is pre-configured with templates and workflows for:

1. **Professional Services** — Time tracking, project billing, resource allocation
2. **Retail & Distribution** — Inventory management, POS integration, multi-warehouse
3. **Manufacturing** — BOM management, production planning, quality control
4. **Real Estate** — Property management, tenant billing, lease tracking
5. **Healthcare** — Patient records, appointment scheduling, billing
6. **Education** — Student management, fee collection, course scheduling

---

## System Requirements

### For End Users
- Modern web browser (Chrome, Firefox, Edge, Safari — latest 2 versions)
- Minimum 1024x768 screen resolution (responsive design supports mobile)
- Stable internet connection (minimum 2 Mbps)

### For Administrators
- SSH access for server management (via Azure Bastion)
- Azure CLI for infrastructure operations
- Git for configuration management

---

## Licensing

- **Odoo CE 18.0**: LGPL-3.0 (free, open source)
- **OCA Modules**: AGPL-3.0 or LGPL-3.0 (free, open source)
- **InsightPulse AI Modules**: Proprietary (included in subscription)
- **Infrastructure**: Pay-as-you-go Azure consumption

---

## Version and Update Policy

- **Odoo Core**: Follows Odoo CE 18.0 stable branch. Security patches applied within 48 hours.
- **OCA Modules**: Pinned to tested commits. Updated monthly after regression testing.
- **IPAI Modules**: Continuous delivery via CI/CD pipeline with automated testing.
- **Infrastructure**: Azure Container Apps with blue-green deployment for zero-downtime updates.

---

## Getting Help

- **Documentation**: Available within the Odoo interface via the Help menu
- **Copilot**: AI assistant accessible from any Odoo screen
- **Support**: Email support@insightpulseai.com or Slack channel #support
- **Status Page**: status.insightpulseai.com for service health

---

## Frequently Asked Questions

**Q: Is this the same as Odoo Enterprise?**
A: No. This is Odoo Community Edition enhanced with OCA modules and custom extensions. It achieves approximately 80% feature parity with Enterprise at zero license cost.

**Q: Can I migrate from Odoo Enterprise to this platform?**
A: Yes, with caveats. Enterprise-specific modules (Studio, Marketing Automation, IoT) have no direct equivalent. Data migration is supported for standard modules.

**Q: What about Odoo.sh?**
A: Odoo on Cloud is an alternative to Odoo.sh. It runs on Azure infrastructure with full control over the deployment, without Odoo S.A. hosting fees.

**Q: Is my data safe?**
A: Data is stored in Azure PostgreSQL with encryption at rest, daily backups, and 30-day retention. All traffic is encrypted in transit. Access is controlled via RBAC and SSO.

**Q: Can I install additional Odoo modules?**
A: Yes. Additional OCA modules can be requested and will be evaluated against our quality gates. Custom module development is available as a service.
