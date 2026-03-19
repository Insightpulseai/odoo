# BIR eServices + eBIRForms — Compliance Benchmark

## Sources

- https://bir.gov.ph/ebirforms
- https://bir.gov.ph/eServices

## Weight

1.0 (regulatory — non-negotiable for PH operations)

## eBIRForms

- Current version: v7.9.5 (RMC No. 49-2025, May 9 2025)
- Offline form preparation + online submission
- Fallback for eFPS filers when eFPS unavailable

### Filing tiers (CY2024 AITR)

| Tier | System |
|---|---|
| Mandated large taxpayers | eFPS |
| Non-eFPS businesses | eBIRForms v7.9.4.2+ |
| Micro/small individuals | BIR Form 1701-MS (manual) |
| PWD / Senior | BIR eLounge (RDO-assisted) |

## eServices suite

- **ORUS** — Online Registration and Update System (TIN, COR, updates)
- **eRegistration** — TIN registration, fee payment, COR online
- **eFPS** — Electronic Filing and Payment System (24/7, SSL, two-level auth)
- **eBIRForms** — Offline prep + online submission
- **eAFS** — Electronic Audited Financial Statements (ITR + AFS + attachments)
- **ePayment** — via Authorized Agent Banks (AABs)

## eFPS mandated users

TAMP taxpayers, Large Taxpayers, Top 20,000 Private Corporations, PEZA/BOI enterprises, government agencies, corporations with paid-up capital >= PHP 10M.

## IPAI integration targets

| BIR System | IPAI Touch Point | Integration Path |
|---|---|---|
| eBIRForms v7.9.5 | Pre-filled XML/form data from Odoo | Odoo → Edge Function → eBIRForms payload |
| eFPS | Large taxpayer filing (TBWA/SMP) | Odoo posted docs → eFPS submission |
| eAFS | ITR + AFS attachment submission | Supabase Storage → eAFS upload |
| ORUS | TIN validation, registration updates | ORUS API or Edge Function proxy |

## Allowed influence

- BIR compliance module design (`ipai_bir_tax_compliance`)
- Tax form generation and filing automation
- Edge Function integration architecture
- Supabase storage for AFS/evidence

## Must not influence

- Repo topology
- Platform architecture
- Non-PH compliance patterns
