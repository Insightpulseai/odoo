# Odoo Apps Parity Matrix

## Executive Summary

| Metric | Count | Strategy |
|--------|-------|----------|
| Total Apps | 55 | 100% coverage |
| CE-Native | 38 | Install directly |
| OCA Replacement | 9 | Community modules |
| Control Room | 7 | Custom build |
| Already Installed | 2 | mail, calendar |

**Timeline**: 21 days to full parity
**Cost**: $0 (all open-source)

## Tier 1: CE-Native Apps (38)

These apps are included in Odoo CE 18.0 and require no special handling.

### Core Transactional (7)
| App | Technical Name | Status |
|-----|----------------|--------|
| Sales | `sale_management` | Install |
| CRM | `crm` | Install |
| Invoicing | `account` | Install |
| Purchase | `purchase` | Install |
| Inventory | `stock` | Install |
| Contacts | `contacts` | Install |
| Manufacturing (MRP) | `mrp` | Install |

### HR & Recruitment (8)
| App | Technical Name | Status |
|-----|----------------|--------|
| Employees | `hr` | Install |
| Time Off | `hr_holidays` | Install |
| Attendances | `hr_attendance` | Install |
| Recruitment | `hr_recruitment` | Install |
| Employee Contracts | `hr_contract` | Install |
| Skills Management | `hr_skills` | Install |
| Expenses | `hr_expense` | Install |
| Fleet | `fleet` | Install |

### Web & E-Commerce (5)
| App | Technical Name | Status |
|-----|----------------|--------|
| Website | `website` | Install |
| eCommerce | `website_sale` | Install |
| Events | `website_event` | Install |
| eLearning | `website_slides` | Install |
| Live Chat | `im_livechat` | Install |

### Marketing (3)
| App | Technical Name | Status |
|-----|----------------|--------|
| Email Marketing | `mass_mailing` | Install |
| SMS Marketing | `mass_mailing_sms` | Install |
| Marketing Card | `marketing_card` | Install |

### Productivity (6)
| App | Technical Name | Status |
|-----|----------------|--------|
| Discuss | `mail` | ✅ Installed |
| Calendar | `calendar` | ✅ Installed |
| Surveys | `survey` | Install |
| To-Do | `project_todo` | Install |
| Lunch | `lunch` | Install |
| Project | `project` | Install |

### POS & Services (4)
| App | Technical Name | Status |
|-----|----------------|--------|
| Point of Sale | `point_of_sale` | Install |
| Restaurant (POS) | `pos_restaurant` | Install |
| Repairs | `repair` | Install |
| Maintenance | `maintenance` | Install |

### Admin & Compliance (1)
| App | Technical Name | Status |
|-----|----------------|--------|
| Data Recycle | `data_recycle` | Install |

## Tier 2: OCA Replacements (9)

Enterprise-only apps replaced with OCA (Odoo Community Association) modules.

| Enterprise App | OCA Replacement | Parity |
|----------------|-----------------|--------|
| Accounting | `account-financial-report`, `mis-builder` | 95% |
| MRP II | `mrp-multi-level`, `mrp-production-request` | 90% |
| Appraisal | `hr-appraisal` | 85% |
| Timesheets | `hr-timesheet-sheet`, `project-timesheet-time-control` | 90% |
| Subscriptions | `sale-subscription` | 80% |
| Helpdesk | `helpdesk-mgmt`, `helpdesk-mgmt-timesheet` | 85% |
| Planning | `project-timeline`, `project-task-dependency` | 75% |
| Quality Control | `quality-control`, `quality-control-stock` | 70% |
| Social Marketing | n8n workflows | 60% |

### Installation

```bash
# Install all OCA modules
pip install -r addons/oca/requirements.txt

# Or by category
./scripts/odoo/install-oca-modules.sh accounting
./scripts/odoo/install-oca-modules.sh helpdesk
```

## Tier 3: Control Room Custom (7)

Enterprise-only apps requiring custom Control Room modules.

| Enterprise App | Control Room Module | Schema |
|----------------|---------------------|--------|
| Knowledge | `control_room.kb` | `kb_*` tables |
| Studio | `control_room.studio` | `studio_*` tables |
| Sign | `control_room.sign` | `sign_*` tables |
| Appointments | `control_room.booking` | `booking_*` tables |
| Field Service | `control_room.fsm` | `fsm_*` tables |
| Barcode | `control_room.barcode` | `barcode_*` tables |
| Mobile | `control_room.mobile` | `mobile_*` tables |

### Supabase Migrations

```bash
# Apply all Control Room schemas
supabase db push

# Individual migrations
supabase migration up 20240101000001_kb_schema.sql
supabase migration up 20240101000002_studio_schema.sql
# ... etc
```

## Implementation Timeline

### Phase 1: CE-Native (Days 1-3)
- Day 1: Core Business (8 apps)
- Day 2: HR & Finance (8 apps)
- Day 3: Web, Marketing, Productivity (22 apps)

### Phase 2: OCA Modules (Days 4-7)
- Day 4: Finance & Accounting
- Day 5: Manufacturing & HR
- Day 6: Sales & Project
- Day 7: Integration Testing

### Phase 3: Control Room (Days 8-21)
- Days 8-10: Knowledge Base
- Days 11-12: Form Builder (Studio)
- Days 13-14: E-Signature
- Days 15-16: Appointments
- Days 17-18: Field Service
- Days 19-20: Barcode Scanner
- Day 21: Mobile API

## Verification Commands

```bash
# Verify CE apps installed
./scripts/odoo/verify-ce-apps.sh

# Verify OCA modules installed
./scripts/odoo/verify-oca-modules.sh

# Verify full 55-app parity
./scripts/odoo/verify-full-parity.sh
```

## Cost Comparison

| Solution | Monthly Cost |
|----------|--------------|
| Odoo Enterprise (10 users) | $240-720 |
| Our Stack (CE + OCA + CR) | $0 |
| **Savings** | **100%** |

## Supabase Integration

All Control Room modules use Supabase for:
- **Database**: PostgreSQL with RLS
- **Auth**: JWT + row-level security
- **Storage**: Document/diagram storage
- **Realtime**: Live dashboard updates
- **Edge Functions**: Webhook handlers

## Related Documentation

- [Spec Bundle](../spec/odoo-apps-inventory/) - Full requirements
- [OCA Manifest](../addons/oca/manifest.yaml) - Module mapping
- [Supabase Migrations](../supabase/migrations/) - Schema files
- [Scripts](../scripts/odoo/) - Installation automation
