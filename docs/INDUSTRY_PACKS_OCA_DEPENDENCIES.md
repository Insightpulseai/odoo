# Odoo Industry Packs - OCA Dependencies Guide

This document describes the OCA (Odoo Community Association) modules required to achieve enterprise-level parity for the three industry pack modules implemented in this repository.

## Overview

The three industry packs implement CE/OCA-based alternatives to Odoo Enterprise industry solutions:

1. **ipai_partner_pack** - Odoo Partner implementation services
2. **ipai_marketing_agency_pack** - Marketing Agency operations
3. **ipai_accounting_firm_pack** - Accounting Firm engagements

## Core OCA Dependencies

### 1. OCA DMS (Document Management System)

**Repository:** https://github.com/OCA/dms

**Replaces:** Odoo Enterprise Documents app

**Key modules:**
- `dms` - Core document management
- `dms_field` - Document fields for other models
- `dms_attachment_link` - Link attachments to DMS

**Usage in Industry Packs:**
- Document storage for creative assets (Marketing Agency)
- Workpaper file management (Accounting Firm)
- Implementation deliverables (Partner Pack)

**Installation:**
```bash
git clone https://github.com/OCA/dms.git -b 18.0 oca-addons/dms
pip install -r oca-addons/dms/requirements.txt
```

### 2. OCA Contract (Subscription Management)

**Repository:** https://github.com/OCA/contract

**Replaces:** Odoo Enterprise Subscriptions app

**Key modules:**
- `contract` - Recurring contracts/subscriptions
- `contract_sale` - Create contracts from sales orders
- `contract_variable_quantity` - Variable billing

**Usage in Industry Packs:**
- Retainer agreements (Marketing Agency)
- Recurring engagement billing (Accounting Firm)
- Support/maintenance contracts (Partner Pack)

**Installation:**
```bash
git clone https://github.com/OCA/contract.git -b 18.0 oca-addons/contract
```

### 3. OCA Timesheet

**Repository:** https://github.com/OCA/timesheet

**Replaces:** Enhanced timesheet features from Enterprise

**Key modules:**
- `hr_timesheet_sheet` - Timesheet approval workflow
- `hr_timesheet_task_required` - Require task on timesheets
- `sale_timesheet_line_exclude` - Exclude timesheet lines from invoicing

**Usage in Industry Packs:**
- Implementation time tracking (Partner Pack)
- Campaign effort tracking (Marketing Agency)
- Engagement hour billing (Accounting Firm)

**Installation:**
```bash
git clone https://github.com/OCA/timesheet.git -b 18.0 oca-addons/timesheet
```

### 4. OCA Social

**Repository:** https://github.com/OCA/social

**Replaces:** Odoo Enterprise Social Marketing (partial)

**Key modules:**
- `mail_activity_board` - Activity dashboard
- `mail_tracking` - Email tracking
- `mass_mailing_custom_unsubscribe` - Unsubscribe management

**Usage in Industry Packs:**
- Campaign activity tracking (Marketing Agency)
- Client communication tracking (All packs)

**Installation:**
```bash
git clone https://github.com/OCA/social.git -b 18.0 oca-addons/social
```

## Enterprise Feature Gap Analysis

### Features with Full OCA Parity

| Enterprise Feature | OCA Alternative | Status |
|-------------------|-----------------|--------|
| Documents | OCA DMS | Full parity |
| Subscriptions | OCA Contract | Full parity |
| Timesheet grid | OCA Timesheet | Near parity |
| Email tracking | OCA Social | Full parity |

### Features with Partial OCA Parity

| Enterprise Feature | OCA Alternative | Gap |
|-------------------|-----------------|-----|
| Planning | No direct OCA equivalent | Custom development needed |
| e-Sign | No direct OCA equivalent | Third-party integration |
| Social Marketing | OCA Social (partial) | Limited scheduling features |
| Helpdesk | Various community modules | Feature subset |

### Recommended Custom Development

For features without OCA equivalents:

1. **Planning/Resource Scheduling**
   - Use `project.task` with custom date/resource fields
   - Consider `resource_booking` community modules
   - Build custom Gantt/calendar views

2. **E-Signature**
   - Integrate with DocuSign, HelloSign, or Adobe Sign APIs
   - Build simple approval workflow using `mail.activity`

3. **Social Media Scheduling**
   - Build custom `ipai.content.calendar` (included in Marketing Agency Pack)
   - Integrate with Buffer, Hootsuite, or platform-native APIs

## Installation Guide

### 1. Add OCA Repositories

Create or update your `oca-addons` directory:

```bash
cd /path/to/odoo-ce

# Create OCA addons directory
mkdir -p oca-addons

# Clone required OCA repos
git clone https://github.com/OCA/dms.git -b 18.0 oca-addons/dms
git clone https://github.com/OCA/contract.git -b 18.0 oca-addons/contract
git clone https://github.com/OCA/timesheet.git -b 18.0 oca-addons/timesheet
git clone https://github.com/OCA/social.git -b 18.0 oca-addons/social
```

### 2. Update Odoo Configuration

Add OCA paths to your `odoo.conf`:

```ini
[options]
addons_path = /path/to/odoo/addons,/path/to/odoo-ce/addons,/path/to/odoo-ce/oca-addons/dms,/path/to/odoo-ce/oca-addons/contract,/path/to/odoo-ce/oca-addons/timesheet,/path/to/odoo-ce/oca-addons/social
```

### 3. Install Python Dependencies

```bash
pip install -r oca-addons/dms/requirements.txt
# Repeat for other OCA modules with requirements.txt
```

### 4. Install Modules

Via Odoo UI or command line:

```bash
./odoo-bin -d your_database -i dms,contract,hr_timesheet_sheet --stop-after-init
```

## Module Dependencies Matrix

| Industry Pack | Required OCA | Optional OCA |
|--------------|--------------|--------------|
| ipai_partner_pack | contract | dms, hr_timesheet_sheet |
| ipai_marketing_agency_pack | dms | contract, mail_tracking |
| ipai_accounting_firm_pack | dms, hr_timesheet_sheet | contract |

## Version Compatibility

All modules in this repository are designed for **Odoo 18.0**.

When selecting OCA modules, ensure you checkout the `18.0` branch:

```bash
git checkout 18.0
```

## References

- [OCA GitHub Organization](https://github.com/OCA)
- [OCA Apps Store](https://odoo-community.org/)
- [Odoo CE Documentation](https://www.odoo.com/documentation/18.0/)

## Contributing

To extend these industry packs with additional OCA integrations:

1. Identify the OCA module that provides the needed functionality
2. Add it as a dependency in `__manifest__.py`
3. Extend models using `_inherit` pattern
4. Follow OCA coding standards (AGPL-3 license, proper versioning)
