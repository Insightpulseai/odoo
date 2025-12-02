# IPAI Expense & Travel (PH)

**Version**: 18.0.1.0.0
**Category**: Human Resources/Expenses
**License**: AGPL-3
**Author**: InsightPulseAI

PH-focused expense and travel workflows (SAP Concur-style) on Odoo CE 18.0 + OCA.

---

## Overview

The **IPAI Expense & Travel** module extends Odoo's standard expense management with Philippines-specific expense categories, travel request workflows, and enhanced project tracking. It provides a comprehensive expense management solution tailored for Philippine business operations.

## Features

### Core Capabilities

- **PH Expense Categories**: Pre-configured expense types common in Philippine businesses
- **Travel Request Workflow**: Multi-level approval for travel authorizations
- **Project Cost Tracking**: Link expenses to projects for cost allocation
- **Enhanced Validation**: Category-specific rules and requirements
- **Dedicated Journals**: Separate accounting journals for expenses and travel

### Pre-configured Expense Categories

| Category | Products |
|----------|----------|
| **Meals & Entertainment** | Meals & Client Entertainment |
| **Local Transportation** | Grab/Taxi Fare, Parking & Tolls, Fuel/Gas |
| **Travel & Accommodation** | Domestic Flights, Hotel Accommodation, Per Diem |
| **Office & Supplies** | Office Supplies, Internet/Mobile Data |
| **General** | Miscellaneous Expense |

### Travel Request Workflow

```
Draft → Submitted → Manager Approved → Finance Approved
           ↓              ↓                  ↓
       Rejected       Rejected          Rejected
```

- **Budget Tracking**: Estimated budget with currency support
- **Project Linkage**: Associate travel with specific projects
- **Purpose Documentation**: Detailed travel purpose tracking

---

## Installation

### Prerequisites

This module depends on:
- `hr` (Odoo HR)
- `hr_expense` (Odoo Expenses)
- `account` (Odoo Accounting)
- `project` (Odoo Project)

### Install

1. Place the module in your Odoo addons directory
2. Update the apps list: `Settings → Apps → Update Apps List`
3. Search for "IPAI Expense & Travel (PH)"
4. Click **Install**

### Post-Installation

The module automatically creates:
- PH expense product categories
- Pre-configured expense products
- Dedicated expense journals (EXPH, TVPH)

---

## Configuration

### Security Groups

Configure user access through standard Odoo expense security:
- **Expense User**: Create and submit own expenses
- **Expense Manager**: Approve team expenses
- **Finance**: Final approval and posting

### Expense Journals

Two dedicated journals are created on installation:

| Journal | Code | Purpose |
|---------|------|---------|
| PH Employee Expenses | EXPH | General employee reimbursements |
| PH Travel & Per Diem | TVPH | Travel-related expenses |

---

## Usage

### Creating Travel Requests

1. Navigate to: **Expenses → Travel Requests → Create**
2. Fill in request details:
   - Employee name
   - Destination
   - Travel dates (start/end)
   - Purpose description
   - Estimated budget
   - Related project (optional)
3. Click **Submit** to start approval workflow
4. Wait for Manager and Finance approvals

### Submitting Expenses

1. Navigate to: **Expenses → My Expenses → Create**
2. Select expense product (PH categories pre-configured)
3. Enter amount and date
4. Link to travel request (if travel-related)
5. Link to project (required for certain categories)
6. Attach receipt documentation
7. Submit for approval

### Project Requirements

Certain expense categories require project linkage for cost tracking:
- Meals & Entertainment
- Office Supplies
- Miscellaneous Expense

The system enforces this validation automatically.

---

## Data Model

### Travel Request (`ipai.travel.request`)

```python
Fields:
- name: Reference (auto-sequence)
- employee_id: Traveling employee
- project_id: Related project
- destination: Travel destination
- start_date: Travel start date
- end_date: Travel end date
- purpose: Trip purpose description
- estimated_budget: Budget estimate
- currency_id: Budget currency
- state: draft / submitted / manager_approved / finance_approved / rejected
- company_id: Multi-company support
```

### HR Expense Extension (`hr.expense`)

Additional fields on standard expense model:

```python
Fields:
- travel_request_id: Linked travel request
- project_id: Related project for cost tracking
- requires_project: Computed flag for project requirement
```

---

## PH-Specific Features

### Expense Categories Aligned with PH Business Practices

- **Grab/Taxi**: Common rideshare expense in Metro Manila
- **Parking & Tolls**: NLEX, SLEX, and other toll roads
- **Per Diem**: Daily allowance for travel
- **Internet/Mobile Data**: WFH internet reimbursement

### Accounting Journals

Separate journals ensure proper classification:
- Employee reimbursements (EXPH)
- Travel & Per Diem (TVPH)

---

## Technical Details

### File Structure

```
ipai_expense/
├── __init__.py
├── __manifest__.py
├── README.md
├── models/
│   ├── __init__.py
│   └── expense.py
├── data/
│   └── ipai_expense_categories.xml
├── views/
│   ├── ipai_expense_menus.xml
│   └── ipai_expense_views.xml
└── security/
    ├── ipai_expense_security.xml
    └── ir.model.access.csv
```

### Dependencies

- Python: Standard library only
- Odoo modules: `hr`, `hr_expense`, `account`, `project`

---

## Integration

### With IPAI OCR Expense

When installed with `ipai_ocr_expense`, expenses can be automatically created from scanned receipts using InsightPulse OCR service.

### With TBWA Spectra Integration

When installed with `tbwa_spectra_integration`, expenses flow into Spectra GL export with proper account mappings.

---

## Support

- **Author**: InsightPulseAI
- **Website**: https://insightpulseai.net
- **License**: AGPL-3

---

## Changelog

### Version 18.0.1.0.0

- Initial release
- PH-specific expense categories
- Travel request workflow
- Project cost tracking integration
- Expense validation rules
- Dedicated accounting journals
