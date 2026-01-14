# InsightPulse AI - Hello World Module

Sample `ipai_*` module demonstrating the **Smart Delta** pattern for Odoo 18 CE.

## Features

- Extends `res.partner` with AI analysis fields
- Uses `_inherit` (not replace) - Smart Delta compliant
- Follows OCA conventions for marketplace readiness

## Fields Added

| Field | Type | Description |
|-------|------|-------------|
| `ipai_customer_score` | Float | Customer engagement score (0-100) |
| `ipai_segment` | Selection | Customer segment classification |
| `ipai_notes` | Text | AI-generated notes |
| `ipai_last_analysis` | Datetime | Timestamp of last analysis |
| `ipai_score_category` | Selection | Computed from score (low/medium/high) |

## Installation

```bash
# In dev environment
docker compose exec odoo odoo -d odoo_dev -i ipai_hello --stop-after-init

# Or via UI: Apps → Update Apps List → Search "InsightPulse" → Install
```

## Usage

1. Go to Contacts
2. Open any partner
3. Click "InsightPulse AI" tab
4. Click "Run AI Analysis" button

## License

AGPL-3 (OCA standard)
