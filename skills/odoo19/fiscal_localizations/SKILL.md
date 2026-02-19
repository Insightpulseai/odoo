---
name: fiscal_localizations
description: Country-specific fiscal compliance packages providing charts of accounts, taxes, reports, and legal requirements for 100+ countries.
metadata:
  author: Claude Agent
  version: "19.0"
  source: "Odoo 19.0 Official Documentation"
  extracted: "2026-02-18"
---

# fiscal_localizations — Odoo 19.0 Skill Reference

## Overview

Fiscal localizations are country-specific Odoo modules that ensure compliance with local fiscal regulations. They primarily serve the Accounting app but may also affect Point of Sale, eCommerce, and other apps depending on country requirements. Each localization package provides a pre-configured chart of accounts, taxes, tax reports, fiscal positions, and any legally mandated features (e.g., electronic invoicing, tax certifications). Odoo auto-installs the core localization module based on the company's country; additional modules can be installed manually. Each company in a multi-company environment can use a different localization.

## Key Concepts

- **Fiscal Localization Package**: Bundle of modules for a specific country. Includes chart of accounts, default taxes, tax return structure, and country-specific reports.
- **Chart of Accounts**: Country-standard account structure auto-configured by the localization. Provides the correct account codes, names, and types for regulatory compliance.
- **Tax Configuration**: Pre-configured sales and purchase taxes matching local VAT/GST rates. Only the main rate is active by default; others can be activated.
- **Tax Return Format**: Localization defines the tax report structure matching the country's official tax declaration form. Some localizations support XML export for direct upload to tax authority platforms.
- **Electronic Invoicing**: Country-specific e-invoicing implementations (e.g., CFDI for Mexico, FatturaPA for Italy, SII for Spain). Configured per localization.
- **Fiscal Position**: Country-standard fiscal positions for common scenarios (domestic, EU intra-community, export, etc.).

## Configuration

1. Localization is auto-installed based on company country at database/company creation.
2. Verify correct package: Accounting > Configuration > Settings > Fiscal Localization > Package.
3. To switch packages: only possible if **no journal entry has been posted**.
4. Fine-tune: activate additional taxes, configure chart of accounts, set up country-specific statements and certifications.

## Supported Countries

### Countries with Detailed Documentation

Argentina, Australia, Austria, Belgium, Brazil, Canada, Chile, Colombia, Denmark, Ecuador, Egypt, France, Germany, Guatemala, Hong Kong, India, Indonesia, Italy, Jordan, Kenya, Luxembourg, Malaysia, Mexico, Netherlands, New Zealand, Oman, Peru, Philippines, Romania, Saudi Arabia, Singapore, Spain, Switzerland, Thailand, Turkiye, United Arab Emirates, United Kingdom, United States, Uruguay, Vietnam.

### Countries with Basic Localization (No Dedicated Doc Page)

Algeria, Bangladesh, Benin, Bolivia, Bulgaria, Burkina Faso, Cameroon, Central African Republic, Chad, China, Comoros, Congo, Costa Rica, Croatia, Cyprus, Czech Republic, Democratic Republic of the Congo, Dominican Republic, Equatorial Guinea, Estonia, Ethiopia, Finland, Gabon, Greece, Guinea, Guinea-Bissau, Honduras, Hungary, Ivory Coast, Japan, Kazakhstan, Kuwait, Latvia, Lithuania, Mali, Malta, Mauritius, Mongolia, Morocco, Mozambique, Niger, Nigeria, Norway, Pakistan, Panama, Poland, Portugal, Qatar, Rwanda, Senegal, Serbia, Slovakia, Slovenia, South Africa, Sweden, Taiwan, Tanzania, Tunisia, Uganda, Ukraine, Venezuela, Zambia.

## Technical Reference

### Module Naming Convention

Country localization modules follow the pattern `l10n_<country_code>` (e.g., `l10n_us`, `l10n_fr`, `l10n_de`).

### Key Models Affected by Localizations

| Model | What Localization Configures |
|-------|------------------------------|
| `account.account` | Chart of accounts (codes, names, types) |
| `account.tax` | Tax rates, computation methods, tax grids |
| `account.tax.group` | Tax group display names |
| `account.fiscal.position` | Default fiscal positions with tax/account mappings |
| `account.report` | Tax return report structure and lines |
| `account.journal` | Default journal configurations |

### Localization-Specific Features (Examples)

| Country | Notable Features |
|---------|-----------------|
| Mexico | CFDI electronic invoicing, PAC integration |
| Italy | FatturaPA e-invoicing, SDI integration |
| Spain | SII real-time tax reporting |
| France | FEC export, data inalterability |
| Germany | DATEV export, XRechnung |
| Brazil | NFe electronic invoicing |
| India | GST compliance, e-Way bills |
| US | 1099 reporting, NACHA payments |
| Belgium | CODA import, Soda import |
| Switzerland | ISR/QR-bill payment slips |

### Important Settings Path

- Fiscal Localization Package: Accounting > Configuration > Settings > Fiscal Localization > Package
- Installed modules: Settings > General Settings > Apps

## API / RPC Patterns

<!-- TODO: not found in docs -->

## Version Notes (19.0)

- New countries are frequently added; the list expands with each release.
- Localization documentation is continuously improved with more detailed country-specific guides.
- Electronic invoicing support expanded to additional countries (see accounting/customer_invoices/electronic_invoicing/ for full list: Argentina, Austria, Belgium, Basque Country, Brazil, Chile, Colombia, Croatia, Ecuador, Estonia, Finland, Guatemala, Hungary, Ireland, Italy, Latvia, Lithuania, Luxembourg, Mexico, Netherlands, Norway, Peru, Romania, Spain, Uruguay).
- **Cannot change localization after posting**: Once any journal entry is posted, the fiscal localization package cannot be switched.

## Common Pitfalls

- **Localization lock-in**: Selecting the wrong country or package at database creation is effectively permanent once entries are posted. Verify before posting any transactions.
- **Multi-company localization**: Each company can have its own localization, but branches inherit the parent company's localization package.
- **Tax activation required**: Localizations create taxes for most rates but only activate the main rate by default. Manually activate additional rates as needed.
- **Country-specific modules may need manual install**: The core localization installs automatically, but supplementary modules (e.g., electronic invoicing, specific report exports) may require manual installation.
- **Payroll localizations are separate**: HR/Payroll localizations are documented and managed independently from fiscal/accounting localizations.
