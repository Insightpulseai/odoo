# Tasks — DocFlow v2

## A. Odoo 19 Module: ipai_docflow_review

- [ ] Add doc_type=bank_statement
- [ ] Add models: docflow.bank.statement, docflow.bank.statement.line
- [ ] Add models: docflow.recon.session, docflow.recon.candidate
- [ ] Add SLA fields and scheduled action
- [ ] Add reconciliation UI + smart actions
- [ ] Extend ingest controller to accept statement extraction_json schema

## B. Python Daemon

- [ ] Add bank statement classifier + extractor
- [ ] Add CSV parser + schema normalizer
- [ ] Implement matching candidate generation (optional: in Odoo server-side)
- [ ] Push statements + candidates into Odoo via ingest endpoint
- [ ] Add tests and golden fixtures

## C. Validation & Ops

- [ ] Integration tests (ingest → statement created → candidates → reconcile)
- [ ] Health checks and logging
- [ ] CI smoke test
