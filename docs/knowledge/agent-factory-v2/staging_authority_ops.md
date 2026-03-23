# Knowledge Item: Staging Authority & PII Scrubbing

## 1. Architectural Split
The Agent Factory V2 correctly separates **ERP Transactional Truth** from **Platform Lifecycle Authority**.

### The Boundary
- **Odoo (ERP)**: Requests a staging refresh.
- **Platform Engine**: Performs the actual DB clone, data sanitization, and environment spin-up.
- **Evidence**: The Platform Engine publishes a "Sanitization Receipt" back to Odoo as proof of a safe rehearsal.

## 2. Sanitization Rules (The Blacklist)
To prevent leakage of production data into staging/dev environments:
- **Emails**: Mask all `res.partner` emails (e.g., `user@domain.com` -> `user@staging.test`).
- **VAT/TIN**: Anonymize VAT numbers while preserving format.
- **Mail Servers**: Disable all outbound SMTP servers upon clone.
- **API Keys**: Revoke or rotate production integration keys in the cloned environment.

## 3. Rollback Paths
Always maintain a "Last Known Good" (LKG) snapshot before any staging refresh to allow 1-click recovery if a release gate is tripped during rehearsal.
