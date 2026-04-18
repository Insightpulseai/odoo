# BIR Document Decision Matrix — Which form, which trade name, when

> Operational reference. Three lanes: client billing (BIR Service Invoice),
> tax identity (BIR 2303 COR), internal expense (TBWA forms). Do not mix.
>
> **No actual TINs, serial numbers, or control numbers in this repo.**
> Store those in Odoo `res.company` / `res.partner` records with masked
> display in UI.

---

## Established registrations (as of 2026-04-14)

| Registration | Taxpayer / entity | Trade name(s) | Address | Type | Document authorized |
|---|---|---|---|---|---|
| **ATP Form 1921 — W9** | Tolentino, Jake Guevarra | W9 Content Multimedia Production | Warehouse 9, La Fuerza Plaza, 2241 Don Chino Roces Ave, Bangkal, Makati | **Non-VAT** | Service Invoice (serial 001–1000), branch ...0001 |
| **ATP Form 1921 — PrismLab** | Tolentino, Jake Guevarra | PrismLab Research and Development on Medical Sciences | Pasig | **Non-VAT** | Service Invoice (serial 0001–1000), branch ...0002 |
| **2303 COR — W9** | Professional (Licensed) | Dataverse IT Consultancy + W9 Content Multimedia Production | Warehouse 9, La Fuerza Plaza, Makati | — | Registration identity |
| **Legacy VAT consulting** (pre-W9) | Prior setup | Consulting (implied Dataverse IT Consultancy) | — | **VAT** | In-use for TBWA Mar 16–30, 2026 invoice |

## Decision matrix — which document for which situation

### 1. Client billing (external, tax-compliant)

```
Billing engagement type                    → Use this invoice / trade name
─────────────────────────────────────────────────────────────────────────
Studio / production work                   → W9 Content Multimedia Production
  (TVC, photography, content, venue)         (W9 Non-VAT Service Invoice)

Medical / R&D / scientific services        → PrismLab R&D on Medical Sciences
                                             (PrismLab Non-VAT Service Invoice)

IT consulting / software / platform work   → Legacy VAT consulting booklet
  (TBWA, Pulser, Odoo, marketplace work)     until VAT registration migrates
                                             to a new trade name
                                             (Dataverse IT Consultancy is
                                              recognized in W9's 2303 COR —
                                              confirm with accountant whether
                                              consulting rides on W9 branch or
                                              keeps separate registration)

Generic "advisory" / mixed                 → Ask accountant before issuing
```

### 2. Tax identity / registration support

```
Need                                       → Use this document
─────────────────────────────────────────────────────────────────────────
Prove registered business to supplier      → BIR 2303 COR (matching entity)
Submit to customer finance on onboarding   → BIR 2303 COR + ATP Form 1921
                                             (for the correct branch)
BIR audit                                  → All: 2303 COR + ATP + booklets
Open supplier account                      → 2303 COR + TIN + ATP
Register with new platform / marketplace   → 2303 COR
```

### 3. Internal TBWA engagement (non-BIR, TBWA-supplied forms)

```
Scenario                                   → Use this TBWA form
─────────────────────────────────────────────────────────────────────────
Need cash advance for travel / event       → Cash Advance Request Form
Liquidate a cash advance                   → Itemized Expense Report
Petty cash liquidation                     → Itemized Expense Report
Expense reimbursement (no advance)         → Itemized Expense Report
```

**These are internal TBWA process forms. They are NOT substitutes for BIR invoices or official receipts. Never bill a client using these forms.**

## Hard rules

1. **Non-VAT W9/PrismLab serial numbers may not be used on VAT invoices.** Booklets are entity-specific; swapping is a BIR violation.
2. **Do not back-date invoices** to match old VAT-series sequences.
3. **TIN + branch code on every Service Invoice** — W9 branch ends `...0001`, PrismLab branch ends `...0002`. Branch mismatch = invoice void.
4. **Legacy VAT consulting booklet stays active** until formally withdrawn via BIR. Do not toss the booklets even if transitioning — archive per retention policy.
5. **Store supporting PDFs in Odoo DMS** per `ssot/demo/100-system-shared/dms-taxonomy.yaml` folders (Finance/2307, Legal/CorporateDocs). Do **not** commit actual ATP PDFs to git.

## Transition scenarios

| Scenario | Old setup | New setup | Action |
|---|---|---|---|
| Studio rental billed in March 2026 | VAT consulting | W9 Non-VAT Service Invoice | **Use old VAT if invoice already issued & accepted** (Mar 16–30 TBWA case). Going forward, studio work moves to W9. |
| New TBWA project April 2026+ | VAT consulting | Depends on scope | Studio/production → W9. Software/consulting → confirm entity with accountant. |
| New PrismaLab medical engagement | N/A | PrismLab Non-VAT | Use PrismLab booklet, PrismLab address, PrismLab branch code. |
| Multi-service engagement | Split billing | Split billing | One invoice per entity per serial. Never combine scopes across two trade names. |

## Record-keeping in Odoo (recommended company structure)

```
res.company hierarchy:
  ├── Jake Guevarra Tolentino (parent sole-prop identity)
  │     ├── Branch 0001: W9 Content Multimedia Production (Makati)
  │     │     Non-VAT · Service Invoice series 001–1000 · VAT=no
  │     └── Branch 0002: PrismLab R&D (Pasig)
  │           Non-VAT · Service Invoice series 0001–1000 · VAT=no
  │
  └── Dataverse IT Consultancy (referenced in W9 2303)
        Legacy VAT consulting series (active until BIR withdrawal)
```

Each sequence defined in Odoo `ir.sequence` scoped per branch/entity with the BIR-assigned serial range. Prefix matches trade name code.

## Pulser automation guardrails

When `pulser-finance` or `ipai-ap-invoice` agents propose an invoice:

1. **Trade name check** — agent must resolve `company_id` → registered trade name → matches engagement scope (studio / R&D / consulting)
2. **VAT flag check** — Non-VAT booklet cannot carry VAT lines
3. **Serial sequence check** — next unused serial in the assigned range; no skips
4. **Branch code check** — TIN branch suffix matches the trade name's branch
5. **Entity mismatch = block release** — cannot cross-bill entities

These checks belong in `addons/ipai/ipai_ph_2307/` or `ipai_ph_bir_invoice_guards/` (new thin module).

## Tie-in with seed-pack system

`ssot/demo/225-ph-compliance/` now has real-world anchoring from these registrations:

- `bir2307-scenarios.yaml` → replace placeholder landlord with **W9 studio rental** scenario when piloting (anonymized serials only)
- `tin-atc-fixtures.yaml` → add a **Non-VAT trade name** fixture pair (valid branch-code pattern, invalid cross-entity pattern)
- Consider adding `260-branch-entity-routing/` as a new seed pack covering trade-name × scope × serial routing scenarios

## Do NOT commit to repo

- Actual TINs
- Actual BIR control numbers
- Actual ATP permit numbers
- Actual serial number ranges (only placeholder like "001–1000" format is OK)
- Photocopies / scans of ATP or 2303 PDFs

Store those in Odoo DMS (`Finance/2307`, `Legal/CorporateDocs`) with RBAC, or in Azure Key Vault / Blob storage. Reference from Odoo records, never from git.

## When in doubt

Ask the registered accountant. Tax errors in PH can result in penalty + 25% surcharge + 12% interest + compromise penalties. The cost of asking once is always less.
