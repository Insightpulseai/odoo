# Skill: BIR eServices — Philippine Tax Electronic Systems

## Metadata

| Field | Value |
|-------|-------|
| **id** | `bir-eservices` |
| **domain** | `finance_ops` |
| **source** | https://www.bir.gov.ph/eServices |
| **extracted** | 2026-03-15 |
| **applies_to** | odoo, agents, automations |
| **tags** | bir, eservices, efps, ebirforms, ereg, philippines, tax-filing, compliance |

---

## BIR Electronic Services Map

### Filing & Payment Systems

| System | URL | Purpose | Who Must Use | IPAI Integration |
|--------|-----|---------|-------------|-----------------|
| **eFPS** (Electronic Filing & Payment System) | `efps.bir.gov.ph` | Online filing + payment of tax returns | Large taxpayers, Top 20K corps, Top 5K individuals, eFPS-mandated entities | **Target**: Auto-submit via API/browser automation |
| **eBIRForms** (Electronic BIR Forms) | Offline software (downloadable) | Offline tax form preparation + submission | All taxpayers not mandated for eFPS | **Current**: TaxPulse generates eBIRForms-compatible output |
| **ePayment** | Via authorized agent banks (AABs) | Online tax payment | All taxpayers | Payment confirmation → Odoo `account.payment` |

### Registration Systems

| System | Purpose | IPAI Relevance |
|--------|---------|----------------|
| **eREG** (Online Registration and Update System) | New taxpayer registration, TIN issuance | One-time setup — not automated |
| **ORUS** (Online Registration and Update System v2) | Updated registration portal | Replaces eREG for some functions |
| **TIN Verification** | Validate TIN numbers | **Automate**: Vendor TIN validation in Odoo |

### Compliance & Reporting

| System | Purpose | IPAI Relevance |
|--------|---------|----------------|
| **eAFS** (Electronic Audited Financial Statements) | Submit annual audited financial statements | Annual submission — manual |
| **eSubmission** | Electronic submission of required documents | Attachments for ITR, AFS |
| **eSales** | Electronic Sales Reporting System | POS/invoice data reporting — future |
| **eAccReg** (Electronic Accreditation of CRM/POS) | Register cash register / POS machines | One-time per device |

### Information & Lookup

| System | Purpose | IPAI Relevance |
|--------|---------|----------------|
| **TIN Inquiry** | Look up own TIN | Employee onboarding verification |
| **eComplaint** | File tax-related complaints | Not applicable |
| **Tax Calculator** | Estimate tax computations | Reference — TaxPulse engine is more accurate |
| **RDO Locator** | Find Revenue District Office by address | Company setup reference |
| **Zonal Value Finder** | BIR zonal values for real property | Real estate transactions |

---

## eFPS Integration Architecture

### Current State

```
TaxPulse Engine (Odoo)
    ↓ generates form data (JSON)
Manual: User downloads → uploads to eFPS portal
```

### Target State

```
TaxPulse Engine (Odoo)
    ↓ generates form data
n8n workflow
    ↓ calls eFPS API or browser automation
eFPS Portal (bir.gov.ph)
    ↓ files return + initiates payment
Payment via AAB (authorized agent bank)
    ↓ confirmation
Odoo: update filing status + payment record
    ↓
ops.run_events: log filing event
    ↓
Slack: notify finance team
```

### eFPS Technical Details

| Detail | Value |
|--------|-------|
| Protocol | HTTPS (web portal — no public REST API) |
| Auth | Username + password + CAPTCHA |
| Sessions | Browser-based, session timeout ~30 min |
| File format | XML (eFPS-native) or eBIRForms format |
| Payment | Redirects to authorized agent bank (AAB) portal |
| Receipt | Electronic Filing Reference Number (EFRN) |

### Automation Approaches

| Approach | Complexity | Reliability | Recommendation |
|----------|-----------|-------------|----------------|
| **Browser automation** (Playwright/Selenium) | Medium | Fragile (UI changes break it) | Use for PoC only |
| **eFPS XML submission** | Low | Good (if XML spec stable) | **Preferred** — generate XML, submit |
| **eBIRForms offline + upload** | Low | Good | Current approach — works |
| **BIR API** (if/when available) | Low | Best | Monitor for API availability |

---

## eBIRForms Integration

### How TaxPulse Uses eBIRForms

```
1. TaxPulse computes tax from Odoo account.move
2. Generates eBIRForms-compatible data (JSON → XML)
3. User opens eBIRForms offline software
4. Imports generated data (or manual entry from TaxPulse output)
5. Validates in eBIRForms
6. Submits via eBIRForms → BIR server
7. Receives EFRN (Electronic Filing Reference Number)
8. Updates Odoo filing record with EFRN
```

### Supported eBIRForms (36 Total)

#### Monthly Returns
| Form | Description | Deadline |
|------|-------------|----------|
| 1601-C | Withholding tax on compensation | 10th of following month |
| 1601-E | Expanded withholding tax | 10th of following month |
| 1601-F | Final withholding tax | 10th of following month |
| 2550M | Monthly VAT declaration | 20th of following month |
| 2551M | Monthly percentage tax | 20th of following month |
| 0619-E | Monthly remittance (EWT) | 10th of following month |
| 0619-F | Monthly remittance (FWT) | 10th of following month |

#### Quarterly Returns
| Form | Description | Deadline |
|------|-------------|----------|
| 2550Q | Quarterly VAT return | 25th of month after quarter |
| 1601-EQ | Quarterly EWT return | Last day of month after quarter |
| 1601-FQ | Quarterly FWT return | Last day of month after quarter |
| 1702Q | Quarterly income tax return | 60 days after quarter end |

#### Annual Returns
| Form | Description | Deadline |
|------|-------------|----------|
| 1702-RT | Annual ITR (regular tax) | April 15 |
| 1702-MX | Annual ITR (mixed income) | April 15 |
| 1700 | Annual ITR (individuals) | April 15 |
| 1604-CF | Annual info return (compensation + final) | January 31 |
| 1604-E | Annual info return (EWT) | March 1 |

#### Certificates
| Form | Description | When Issued |
|------|-------------|-------------|
| 2307 | Certificate of Creditable Tax Withheld | With each payment |
| 2306 | Certificate of Final Tax Withheld | With each payment |
| 2316 | Certificate of Compensation Payment/Tax Withheld | Year-end (employees) |

---

## TIN Validation Integration

### Pattern for Odoo

```python
# In ipai_bir_tax_compliance module
class ResPartner(models.Model):
    _inherit = 'res.partner'

    tin = fields.Char(string='TIN', size=15)

    @api.constrains('tin')
    def _check_tin_format(self):
        """Validate Philippine TIN format: XXX-XXX-XXX-XXX"""
        for partner in self:
            if partner.tin:
                tin_clean = partner.tin.replace('-', '')
                if len(tin_clean) != 12 or not tin_clean.isdigit():
                    raise ValidationError(
                        _('Invalid TIN format. Must be 12 digits (XXX-XXX-XXX-XXX).')
                    )

    def action_verify_tin_bir(self):
        """Verify TIN against BIR TIN Inquiry system (manual trigger)"""
        self.ensure_one()
        # Open BIR TIN verification in browser
        return {
            'type': 'ir.actions.act_url',
            'url': 'https://www.bir.gov.ph/tin-inquiry',
            'target': 'new',
        }
```

---

## Filing Deadline Automation (Current)

### Assets Already Built

| Asset | Location | Status |
|-------|----------|--------|
| Deadline model | `ipai_bir_tax_compliance/models/bir_filing_deadline.py` | Active |
| Deadline data | `ipai_bir_tax_compliance/data/bir_filing_deadlines.xml` | Loaded |
| Email alerts | `ipai_bir_notifications/` | Not installed |
| Urgent alerts | `supabase/functions/bir-urgent-alert/` | Active |
| n8n deadline reminder | `automations/n8n/workflows/bir_deadline_reminder.json` | Active |
| n8n overdue nudge | `automations/n8n/workflows/bir_overdue_nudge_workflow.json` | Active |
| Plane sync | `ipai_bir_plane_sync/` | Not installed |
| Filing calendar KB | `knowledge-base/bir-compliance/bir-filing-calendar.md` | Reference |

### Monthly Compliance Checklist (Automated)

```
Day 1-5:   Prepare monthly returns (1601-C, 1601-E, 2550M)
Day 5-8:   Review + approve in Odoo
Day 9:     Final validation (TaxPulse AI review)
Day 10:    File withholding returns (1601-C, 1601-E, 0619-E/F)
Day 15-18: Prepare VAT return (2550M)
Day 20:    File VAT + percentage tax returns
Day 25:    Quarter-end: file 2550Q, 1601-EQ
```

---

## Penalties Reference

| Violation | Penalty |
|-----------|---------|
| Late filing | 25% surcharge on tax due |
| Failure to file | 50% surcharge on tax due |
| Deficiency interest | 12% per annum |
| Late payment | 12% interest + 25% surcharge |
| Fraudulent return | 50% surcharge + possible criminal |

---

## IPAI Automation Roadmap

| Phase | What | Tool | Priority |
|-------|------|------|----------|
| **Done** | Tax computation from `account.move` | TaxPulse engine | Complete |
| **Done** | Deadline tracking + alerts | Odoo model + n8n + Supabase | Complete |
| **Done** | AI compliance review | `finance-tax-pulse` Edge Function | Complete |
| **Next** | eBIRForms XML generation | TaxPulse → XML export | P0 |
| **Next** | TIN validation on vendor creation | Odoo `res.partner` constraint | P1 |
| **Next** | eFPS browser automation (PoC) | Playwright via n8n | P2 |
| **Future** | BIR API integration (when available) | Direct API calls | P3 |
| **Future** | eSales POS reporting | Odoo POS → BIR | P3 |

## Related Skills

- [taxpulse-ph-pack](../taxpulse-ph-pack/SKILL.md) — Core tax engine
- [bir-tax-filing](../../bir-tax-filing/SKILL.md) — Agent skill for BIR forms
- [odoo18-accounting-map](../odoo18-accounting-map/SKILL.md) — Accounting feature map
- [sap-concur-parity](../../industries/sap-concur-parity/SKILL.md) — Expense/tax parity
- [landing-ai-ade](../../inference/landing-ai-ade/SKILL.md) — ADE for BIR form extraction
- [azure-document-intelligence](../../azure-foundry/document-intelligence/SKILL.md) — Custom model for BIR forms
