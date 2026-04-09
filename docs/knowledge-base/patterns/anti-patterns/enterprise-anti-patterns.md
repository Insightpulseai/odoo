# Enterprise ERP Anti-Patterns

## Anti-Pattern 1: The God Module

**Symptom**: One `ipai_*` module with 20+ models, 50+ views, and dependencies on everything.

**Why it happens**: Easier to add to an existing module than create a new one.

**SAP equivalent**: Z-programs that grow into unmaintainable monoliths.

**Impact**: Impossible to test in isolation, upgrade breaks everything, every change is high-risk.

**Fix**: Split by bounded context. One module = one business capability. Use `_inherit` for cross-module extensions.

---

## Anti-Pattern 2: sudo() Driven Development

**Symptom**: `sudo()` used to "make things work" instead of fixing access control.

**Why it happens**: Developer hits an access error, adds sudo() to bypass it.

**Impact**: Bypasses all security, breaks audit trail, creates privilege escalation vulnerabilities.

**Fix**: Design proper groups, ACLs, and record rules. Use sudo() ONLY for system operations (cron jobs, automated sequences) with documented justification.

---

## Anti-Pattern 3: Spreadsheet as Database

**Symptom**: Business-critical data lives in Excel/Google Sheets outside Odoo. Users export, modify, re-import.

**Why it happens**: Odoo doesn't have the exact report or view the user needs.

**SAP equivalent**: Shadow IT spreadsheets undermining the ERP system of record.

**Impact**: Data inconsistency, no audit trail, no access control, manual errors.

**Fix**: Build the missing view/report in Odoo (MIS Builder, pivot views, dashboard). If the workflow genuinely doesn't fit, create a proper Odoo model.

---

## Anti-Pattern 4: Configuration as Code

**Symptom**: Tax rates, approval thresholds, and business rules hardcoded in Python.

**Why it happens**: Faster to code than to build a configuration UI.

**Impact**: Every business rule change requires a code release. Non-technical users cannot adjust.

**Fix**: Use `ir.config_parameter`, data records, or dedicated configuration models. Expose via Settings menu.

---

## Anti-Pattern 5: The Mega-View

**Symptom**: A single form view with 50+ fields, multiple notebooks, deeply nested groups.

**Why it happens**: Every stakeholder adds "just one more field" to the main form.

**SAP equivalent**: Transaction screens with hundreds of fields across tabs.

**Impact**: Slow rendering, overwhelming UX, hard to maintain view inheritance.

**Fix**: Use related models and smart buttons. Show summary on main form, detail on linked records. Use `invisible` to show fields only when relevant.

---

## Anti-Pattern 6: Synchronous External Calls

**Symptom**: ORM method calls an external API during create/write. If the API is slow or down, Odoo hangs.

**Why it happens**: Simplest implementation — call the API directly in the model method.

**Impact**: User-facing latency, transaction timeouts, cascading failures.

**Fix**: Use `queue_job` for all external calls. Return immediately, process async, notify on completion/failure.

---

## Anti-Pattern 7: Testing on Production Data

**Symptom**: New features tested on `odoo_dev` with copies of production data, or worse, directly on production.

**Why it happens**: "We need real data to test properly."

**Impact**: Data corruption, privacy violations, false confidence in test results.

**Fix**: Use disposable `test_<module>` databases. Create realistic seed data. Never use `odoo_dev`/`odoo_staging`/`odoo` for automated tests.

---

## Anti-Pattern 8: OCA Module Forking

**Symptom**: OCA module source code copied into `addons/ipai/` and modified directly.

**Why it happens**: "We need just one small change to this OCA module."

**Impact**: Cannot update to newer OCA versions, duplicated code, divergent behavior.

**Fix**: Create an `ipai_*` override module that inherits from the OCA module. Use `_inherit` for model changes, `xpath` for view changes.

---

## Anti-Pattern 9: Missing Audit Trail

**Symptom**: Business-critical records can be modified without any tracking of who changed what and when.

**Why it happens**: Developer doesn't add `mail.thread` mixin or tracking on fields.

**SAP equivalent**: Missing change documents on master data.

**Impact**: Compliance failure, inability to investigate discrepancies, no accountability.

**Fix**: Add `_inherit = ['mail.thread', 'mail.activity.mixin']` to all transactional models. Use `tracking=True` on critical fields.

---

## Anti-Pattern 10: UI as Security

**Symptom**: Sensitive fields hidden with `invisible` but no backend access control.

**Why it happens**: "Users can't see it so they can't access it."

**Impact**: API access bypasses UI hiding. Any XML-RPC/JSON-RPC call can read/write the field.

**Fix**: Use `groups` attribute on fields for field-level security. Combine with proper ACLs and record rules.

---

## Anti-Pattern 11: Ignoring Multi-Company

**Symptom**: Custom models work in single-company but break in multi-company because `company_id` is missing.

**Why it happens**: Development starts with single company; multi-company is "later."

**Impact**: Data leaks between companies, incorrect financial reporting, compliance violations.

**Fix**: Add `company_id` to every transactional model from day one. Add record rules immediately. Test with multi-company from the start.

---

## Anti-Pattern 12: Raw SQL in Business Logic

**Symptom**: `self.env.cr.execute("SELECT ...")` scattered through model methods.

**Why it happens**: Developer assumes ORM is too slow or doesn't know the ORM method.

**Impact**: Bypasses access control, breaks ORM cache, vulnerable to SQL injection, hard to maintain.

**Fix**: Use ORM methods (search, read, mapped, filtered). Only use raw SQL for complex reports via `_auto = False` SQL views, and even then, use parameterized queries.
