---
name: bir_tax_compliance
description: Philippine BIR tax compliance skill for Pulser Finance (Tax Guru agent). Generates BIR 2307 / 2550M / 2550Q / SAWT / QAP / SLSP DAT files and PDFs via Foundry Code Interpreter; reads Odoo account.move via PG MCP; outputs artifacts to stipaidevagent storage; tracks filing state in Postgres ops schema.
type: rigid
---

# SKILL: bir_tax_compliance

Tax Guru agent (`id-ipai-agent-tax-guru-dev`) invokes this skill when the user mentions any of the trigger phrases below or when the system detects a period-close event.

---

## Required Foundry Tools

| Tool | Purpose |
|---|---|
| `azure_database_postgresql` (PG MCP → `pg-ipai-odoo`) | Read `account.move`, `account.move.line`, `res.partner`, `account.tax` |
| `code_interpreter` (Foundry built-in) | Execute `bir_2307_dat_generator.py` + `bir_2307_pdf_renderer.py` |
| `browser_automation` (Foundry built-in) | Phase 2 — submit DAT to eBIRForms / eFPS portals |
| `document_intelligence` (`docai-ipai-dev`) | Validate uploaded BIR forms for Content Understanding Layout parsing |
| `azure_ai_search` (`srch-ipai-dev-sea`, index `pulser-bir-rulings`) | Ground answers about which ATC code applies |
| `file_search` (Foundry built-in) | BIR form templates (uploaded PDFs) |
| `foundry_mcp_server` | Eval access + agent introspection |

## Required Storage

- `stipaidevagent` — output: BIR PDF + DAT files under `bir-filings/<period>/<form-type>/`
  - Path pattern: `bir-filings/2026-Q1/2307/2307-<company-tin>-2026-Q1.dat`
  - Path pattern: `bir-filings/2026-Q1/2307/2307-<company-tin>-2026-Q1.pdf`

## Required Connections

- `appi-ipai-dev-agent-sea` — OTEL traces per agent run

## State Machine

Filing runs tracked in Postgres `ops.bir_filing_runs` (migration `migrations/odoo/20260415_bir_filing_runs.sql`):

```
draft
  ↓ (agent reads account.move for period)
generated (DAT + PDF artifacts in stipaidevagent)
  ↓ (human approval — mail.activity on ipai_bir_filing_run record)
approved
  ↓ (Phase 2: Browser Automation submits; Phase 1: human submits via portal)
submitted
  ↓ (BIR receipt received + recorded)
confirmed | rejected
```

## Trigger conditions

Agent activates when any of:

- User mentions: `"2307"`, `"2550M"`, `"2550Q"`, `"SAWT"`, `"QAP"`, `"SLSP"`, `"1601-C"`, `"1601-E"`, `"1702"`, `"BIR filing"`, `"withholding tax"`, `"creditable tax"`, `"alphalist"`
- Scheduled period-close event fires (cron on `account.fiscal.period`)
- Odoo `account.move` posted with non-zero `tax_line_id` matching a PH ATC code
- User asks: `"What do I need to file for <period>?"`

## Slash commands (Pulser Teams bot surface)

| Command | Action | Writes to |
|---|---|---|
| `/bir-generate <form> <period>` | Generate DAT + PDF for the form | `stipaidevagent/bir-filings/<period>/<form>/` |
| `/bir-status <period>` | Show filing state for all forms in period | reads `ops.bir_filing_runs` |
| `/bir-preview <artifact_id>` | Return signed URL to PDF preview | 15-min SAS link |
| `/bir-2307 <vendor_tin> <period>` | Generate single-vendor 2307 | — |
| `/bir-submit <artifact_id>` (Phase 2) | Submit to eBIRForms via Browser Automation | updates state |

## Phase 1 scope — ship Q2 2026

Limited to **DAT + PDF generation**:

1. `BIR 2307` — Certificate of Creditable Tax Withheld (per-vendor-per-period)
2. `SAWT` — Summary Alphalist of Withholding Taxes (all-vendors-per-period)
3. `QAP` — Quarterly Alphalist of Payees
4. `SLSP` — Summary List of Sales and Purchases
5. `2550M / 2550Q` — Monthly/Quarterly VAT Declaration

NOT in Phase 1:
- eBIRForms / eFPS submission (Phase 2 — Issue 16)
- 1601-C (compensation withholding monthly) — (Phase 3 — Issue 24)
- 1702 (annual ITR) — (Phase 3 — Issue 24)

## Tool invocation pattern (Phase 1)

```python
# Inside Foundry Code Interpreter (invoked by Tax Guru agent)
from ipai_bir_tax_compliance.tools import generate_2307_dat_from_dicts
from ipai_bir_tax_compliance.tools.bir_2307_pdf_renderer import render_2307_pdf

# 1. PG MCP query (agent-issued)
#    SELECT * FROM account_move_line
#    WHERE company_id = :c AND date BETWEEN :p_start AND :p_end
#      AND tax_line_id IN (SELECT id FROM account_tax WHERE atc_code IS NOT NULL)

# 2. Shape payment rows into dicts
header = {
  "withholding_agent_tin": "123-456-789-000",
  "withholding_agent_name": "INSIGHTPULSE AI INC",
  "withholding_agent_address": "Makati City, Philippines",
  "period_from": "2026-01-01",
  "period_to": "2026-03-31",
}
details = [
  {"payee_tin": "987-654-321-000", "payee_name": "ACME", "payee_address": "BGC",
   "atc_code": "WC160", "nature_of_income_payment": "Professional fees",
   "amount_of_payment": "100000.00", "tax_rate": "0.10", "tax_withheld": "10000.00"},
]

# 3. Generate DAT
dat_text = generate_2307_dat_from_dicts(header, details)

# 4. Render PDF
pdf_bytes = render_2307_pdf(header_obj, detail_objs, output_path="/tmp/2307.pdf")

# 5. Upload artifacts to stipaidevagent via agent's managed identity
#    POST to stipaidevagent/bir-filings/2026-Q1/2307/...

# 6. Transition ops.bir_filing_runs state: draft → generated
```

## Evaluation

See `spec/pulser-evals/pulser-finance-evals.md` §2.1 (BIR 2307 generation) + §3 (adversarial — doctrine + PII).

Pass criteria:
- DAT passes BIR validator (schema + totals)
- PDF has all required fields populated
- `ops.bir_filing_runs` row created
- NO Supabase / Vercel / n8n references in any reasoning trace (doctrine)

## Forbidden behaviors

- Submitting DAT without human approval (Phase 1 is generate-only; Phase 2 adds submit with approval gate)
- Writing to `account.move` directly (read-only; Tax Guru doesn't mutate ledger)
- Including non-ASCII characters in DAT (BIR validator rejects — generator auto-sanitizes)
- Hallucinating ATC codes — always lookup from `account.tax.atc_code` in Odoo or `pulser-bir-rulings` index

## Related

- `addons/ipai/ipai_bir_tax_compliance/tools/bir_2307_dat_generator.py`
- `addons/ipai/ipai_bir_tax_compliance/tools/bir_2307_pdf_renderer.py`
- `addons/ipai/ipai_bir_tax_compliance/tests/test_bir_2307_dat.py`
- `spec/pulser-evals/pulser-finance-evals.md` §2.1
- Migration: `migrations/odoo/20260415_bir_filing_runs.sql` (to be written)

---

*Skill locked 2026-04-15 per Issue 9.*
