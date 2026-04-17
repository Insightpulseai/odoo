# MODULE_INTROSPECTION — ipai_doc_intel

## Why this module exists
Replace Odoo IAP document digitization with Azure Document Intelligence for zero per-scan cost and custom form support.

## Business problem
Finance teams manually enter vendor invoice data from PDFs. Odoo IAP charges per scan. Custom forms (TBWA Cash Advance, Expense Report) can't be processed by IAP at all.

## CE 18 coverage checked
Odoo CE 18 has `account.move` with attachment support. No native OCR/extraction — requires IAP subscription.

## Property-field assessment
Not applicable — this is a service integration, not metadata.

## OCA 18 same-domain coverage checked
No OCA module provides Azure DocAI integration.

## Adjacent OCA modules reviewed
- `account_invoice_import` (OCA) — imports structured data (XML/EDI), not PDF extraction
- No PDF-to-invoice OCA module exists for Azure DocAI

## Why CE + OCA composition was insufficient
Neither CE nor OCA provides PDF → structured invoice data extraction connected to Azure Document Intelligence.

## Why custom code is justified
This is a thin bridge between Azure DocAI REST API and Odoo `account.move`. Zero business logic duplication — CE handles accounting, DocAI handles extraction, this module maps between them.

## Module type
Bridge (Azure DocAI → Odoo account.move)

## Functional boundaries
- Calls DocAI prebuilt-invoice API
- Maps response fields to account.move
- Creates/updates invoice lines
- Does NOT handle posting, approval, or tax computation (those are CE/OCA)

## Extension points used
- `_inherit = "account.move"` — adds extraction action + status fields
- `AbstractModel` for service layer — no stored table

## Blast radius
Low — adds 3 fields to account.move, 1 button, 1 service model. No core method overrides.

## Upgrade risk
Low — depends only on `account.move` field names which are stable across Odoo versions.

## Owner
Platform / Finance Operations

## Retirement / replacement criteria
Retire if Odoo CE adds native Azure DocAI integration (unlikely) or if a superior OCA module emerges.
