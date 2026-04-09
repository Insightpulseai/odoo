# PRD — TaxPulse PH for Odoo 18

## 1. Product Name

**TaxPulse PH for Odoo 18**

## 2. Reverse Benchmark

Benchmark product: **Avalara AvaTax**.

AvaTax is a strong benchmark for real-time tax calculation and broad ERP/commercial integrations. However, Odoo's official AvaTax documentation states that AvaTax integration is only available for databases/companies with locations in the United States, Canada, and Brazil. That makes AvaTax a useful capability benchmark, but not a direct solution for an Odoo 18 deployment centered on Philippine tax operations.

## 3. Problem

Philippine businesses running Odoo 18 need more than generic tax computation. They need:
- local VAT and withholding-aware calculations
- deterministic AP/AR document validation
- structured attachment ingestion
- review workflows inside Odoo
- BIR-oriented reporting and export readiness
- agent-assisted explanation without surrendering compliance decisions to AI

The uploaded Dataverse invoice illustrates the failure mode to avoid: the printed figures on the document imply a payable that does not match the printed total due, so the system should flag the invoice for review instead of silently accepting it.

## 4. Vision

Build the Philippines-first, Odoo-native equivalent of an agentic tax and compliance engine:
- fast like a tax engine
- local like a fiscal localization
- explainable like an audit tool
- embedded like an ERP workflow
- extensible like a service platform

## 5. Goals

### 5.1 Business goals
- reduce tax computation and payable validation errors before posting
- reduce accountant review time on AP/AR tax exceptions
- make Odoo 18 viable as the core compliance-aware finance system for Philippine entities
- create a productizable compliance layer that can be sold as an Odoo-native tax/compliance solution

### 5.2 Product goals
- real-time tax computation for Odoo transactions in scope
- deterministic validation of invoices and vendor bills
- agent-assisted explanation and exception handling
- BIR-oriented reporting/export readiness
- multi-company / multi-branch support

## 6. Non-Goals

- global tax content parity with AvaTax
- support for all countries in v1
- replacing Odoo accounting itself
- letting AI determine accounting correctness
- full automation of every BIR filing workflow in v1

## 7. Users

### Primary users
- finance managers
- accountants
- AP analysts
- AR/billing staff
- ERP administrators

### Secondary users
- external accountants and auditors
- compliance approvers
- operations managers approving tax-sensitive transactions

## 8. Core User Stories

1. As a billing user, I want Odoo to compute tax correctly on draft sales documents before confirmation or invoicing.
2. As an AP analyst, I want supplier invoices to be ingested and validated automatically before posting.
3. As a finance approver, I want the system to explain exactly why a document passed or failed.
4. As a compliance user, I want withholding-aware payable checks and exception routing.
5. As an ERP administrator, I want all review states to live inside Odoo rather than spreadsheets and email.

## 9. Functional Requirements

### FR-1: Philippine tax determination
The system must compute tax outcomes for in-scope Odoo transactions, including:
- VATable
- zero-rated
- VAT-exempt
- withholding-aware scenarios
- configurable tax profiles by company, branch, partner type, document type, and product/service classification

### FR-2: Deterministic invoice math validation
The system must:
- ingest attachments
- normalize extracted data into a strict schema
- recompute line totals, VAT, withholding, gross, and expected payable
- compare printed values to computed values
- return `validated`, `needs_review`, or `rejected`

### FR-3: Agentic extraction and explanation
The system must use AI to:
- classify documents
- extract candidate fields
- explain findings
- suggest likely causes and resolution paths
- draft reviewer notes

### FR-4: Odoo transaction coverage
The system must support, at minimum:
- quotations / sale orders for tax preview
- customer invoices / credit notes
- vendor bills / debit notes
- purchase orders for tax estimation
- review records linked to accounting documents

### FR-5: Attachment ingestion
The system must process:
- PDFs
- image-based invoices/receipts
- supported office documents where useful
- email attachment-derived documents through an external ingestion path

### FR-6: Review workflow
The system must support:
- draft review
- flagged exceptions
- reviewer comments
- approve / reject / override
- audit trails for every change in state

### FR-7: Reporting and export readiness
The system must produce:
- structured transaction exports
- compliance-oriented datasets
- BIR-oriented reporting support and submission-prep outputs for future automation

### FR-8: API-first services
The system must expose services for:
- tax computation
- invoice validation
- explanation generation
- compliance payload generation
- audit retrieval

## 10. Non-Functional Requirements

### NFR-1: Deterministic correctness
Tax math and approval logic must be reproducible and fixture-testable.

### NFR-2: Auditability
Every finding must trace back to source fields and source documents.

### NFR-3: Interactive performance
The product should support interactive draft validation and review, not overnight-only batch behavior.

### NFR-4: Odoo-native UX
The primary workflow should feel native to Odoo 18.

### NFR-5: Secure service boundaries
Secrets, model access, and service credentials must not be embedded in Odoo business records.

## 11. Product Principles vs. AvaTax Benchmark

TaxPulse PH should beat the benchmark in this target segment by being:
- Philippines-first instead of globally broad but locally shallow
- Odoo-native instead of ERP-generic
- deterministic on AP/AR validation instead of tax lookup alone
- agent-assisted inside the ERP instead of portal-first
- BIR-oriented instead of generalized for non-PH jurisdictions

## 12. Success Metrics

- 95%+ of standard invoice attachments normalized into a usable schema
- 99%+ deterministic reproduction of tax math on golden fixtures
- material reduction in manual spreadsheet-based tax checking
- median flagged-review handling time under 5 minutes for common AP/AR scenarios
- no auto-posting of documents with arithmetic or tax-rule failures
