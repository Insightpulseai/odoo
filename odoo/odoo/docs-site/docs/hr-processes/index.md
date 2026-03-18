# HR processes

HR process documentation for InsightPulse AI covering the hire-to-retire lifecycle, final pay computation, clearance workflows, and COE generation. All processes target Philippine labor compliance (DOLE, BIR, SSS, PhilHealth, Pag-IBIG).

## Coverage

| Process | Description | SLA |
|---------|-------------|-----|
| [Hire-to-retire](hire-to-retire.md) | Full employee lifecycle from hiring through separation | Varies by phase |
| [Final pay calculation](final-pay.md) | Statutory final pay computation with Philippine tax and contribution rules | 7 days internal / 30 days DOLE |
| [Clearance workflow](clearance-workflow.md) | 4-department parallel clearance with SLA monitoring | 5 business days |
| [COE generation](coe-generation.md) | Certificate of employment request, generation, and release | 3 days statutory |

## Odoo modules

These processes rely on the following module stack:

- **Core**: `hr`, `hr_contract`, `hr_holidays`, `hr_payroll`
- **OCA**: `hr_employee_document`, `hr_contract_reference`
- **Custom**: `ipai_hr_clearance`, `ipai_hr_coe`, `ipai_hr_final_pay`

## Regulatory framework

| Regulation | Requirement |
|------------|-------------|
| Labor Code of the Philippines | Employment terms, separation, COE |
| DOLE Labor Advisory 06-20 | Final pay within 30 days of separation |
| Labor Code Article 285 | COE within 3 days of request |
| PD 851 | 13th month pay |
| BIR RR 11-2018 | Tax annualization on separation |
| RA 11199 / RA 11223 / RA 9679 | SSS, PhilHealth, Pag-IBIG contributions |
