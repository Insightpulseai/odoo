# Enterprise ERP Architecture Patterns

## Pattern 1: Layered Separation

### Problem
Business logic, presentation, integration, and data access get entangled, making changes risky and testing hard.

### SAP Approach
Strict ABAP layers: presentation (Dynpro/Fiori) → application (BAPI/Function Modules) → persistence (tables).

### Odoo Implementation
```
Presentation Layer:  XML views, Owl components, QWeb templates
─────────────────────────────────────────────────────────────
Business Logic:      Python models, compute methods, workflows
─────────────────────────────────────────────────────────────
Data Access:         ORM (models.Model), SQL views for reporting
─────────────────────────────────────────────────────────────
Integration:         Controllers, XML-RPC, queue_job
─────────────────────────────────────────────────────────────
Infrastructure:      PostgreSQL, Redis (sessions), file storage
```

### Rules
- Never put business logic in views (no complex `attrs` expressions)
- Never put SQL in controllers
- Never put presentation concerns in models (no HTML generation in Python)

---

## Pattern 2: Config → OCA → Delta

### Problem
Custom code is expensive to maintain and upgrade. Every custom line increases technical debt.

### SAP Approach
Configuration (IMG) → Enhancement spots → Custom development (Z-programs).

### Odoo Implementation
```
1. Configuration   → Odoo settings, system parameters, data records
2. OCA modules     → Vetted community modules (pre-commit, CI, peer review)
3. ipai_* modules  → Custom only when 1 and 2 are insufficient
```

### Decision Tree
```
Can it be done with Odoo configuration?
  YES → Configure it. Done.
  NO  → Does an OCA 18.0 module exist?
    YES → Is it stable? CI green? No EE deps?
      YES → Install it. Done.
      NO  → Can it be ported/fixed?
        YES → Port it, contribute upstream. Done.
        NO  → Build ipai_* module.
    NO  → Is this truly custom to our business?
      YES → Build ipai_* module.
      NO  → Keep outside Odoo (Azure service, n8n, external).
```

---

## Pattern 3: Multi-Company Isolation

### Problem
Multiple legal entities share one Odoo instance but must have strict data isolation for compliance.

### SAP Approach
Company code (BUKRS) with authorization objects restricting cross-company access.

### Odoo Implementation
- `company_id` field on all transactional models
- Record rules with `company_ids` for row-level filtering
- `res.company` hierarchy for parent-child relationships
- Intercompany modules for cross-entity transactions

### Rules
- Every transactional model MUST have `company_id`
- Record rules MUST use `('company_id', 'in', company_ids)` pattern
- Intercompany transactions create mirror documents (not shared records)
- Report generation must respect company filter

---

## Pattern 4: Approval Tier Validation

### Problem
Enterprise processes require multi-level approval with delegation, escalation, and audit trail.

### SAP Approach
Release strategy with release codes, authorization groups, and workflow.

### Odoo Implementation (OCA)
```
base_tier_validation
├── Defines TierValidation mixin
├── Tier definitions: model, field, reviewer, sequence
├── States: pending → approved → rejected
└── Audit: who approved, when, comments

purchase_tier_validation
├── Applies tiers to purchase.order
└── Example: amount > 50K → requires CFO approval

sale_tier_validation
├── Applies tiers to sale.order
└── Example: discount > 15% → requires sales director approval
```

### Rules
- Tier definitions stored as data, not code
- Approver cannot be the same as requestor (SoD)
- Delegation rules for absence coverage
- Full audit trail on approval actions

---

## Pattern 5: Document Lifecycle

### Problem
Business documents (invoices, POs, contracts) need state management with controls at each transition.

### SAP Approach
Document status with authorization checks at each status change.

### Odoo Implementation
```python
state = fields.Selection([
    ("draft", "Draft"),         # Editable, no posting
    ("confirmed", "Confirmed"), # Locked, pending approval
    ("approved", "Approved"),   # Ready for processing
    ("done", "Done"),           # Completed, archived
    ("cancelled", "Cancelled"), # Soft delete
], default="draft")
```

### Rules
- Draft → Confirmed: validation checks (required fields, amounts, dates)
- Confirmed → Approved: tier validation (approval workflow)
- Approved → Done: business completion (posting, delivery, payment)
- Any → Cancelled: reversal entry if already posted (never delete)
- Done → Draft: NEVER (create new document instead)

---

## Pattern 6: Async Processing with Queue

### Problem
Long-running operations (report generation, bulk updates, external API calls) block the web worker.

### SAP Approach
Background jobs (SM36/SM37), RFC queues, process chains.

### Odoo Implementation (OCA queue_job)
```python
from odoo.addons.queue_job.job import job

class MyModel(models.Model):
    _name = "ipai.my.model"

    @job(default_channel="root.heavy")
    def _process_heavy_task(self, data):
        # Long-running logic here
        pass

    def action_trigger(self):
        self.with_delay()._process_heavy_task(data)
```

### Rules
- Jobs must be idempotent (safe to retry)
- Set appropriate retry count and delay
- Monitor failed jobs via queue.job model
- Channel configuration controls concurrency

---

## Pattern 7: Master Data Governance

### Problem
Poor master data quality cascades into every business process. Duplicate partners, inconsistent products, wrong tax codes.

### SAP Approach
MDG workflows with staging, approval, replication.

### Odoo Implementation
- Partner deduplication: OCA partner_deduplicate_acl, partner_deduplicate_filter
- Product lifecycle: product_state for lifecycle tracking
- Change approval: base_tier_validation on partner/product changes
- Data quality: constraints, computed fields, server actions for cleanup

### Rules
- Partner creation requires minimum fields (name, tax ID, type)
- Product creation requires category, UoM, accounting mapping
- Bulk imports must pass validation before committing
- Deduplication runs on schedule, reviewed by data steward

---

## Pattern 8: Event-Driven Integration

### Problem
Tight coupling between systems creates fragile integrations that fail cascading.

### SAP Approach
ALE/IDoc, Event Mesh, Integration Suite.

### Odoo Implementation
```
Odoo event (create/write) → queue_job → external API call
External event → webhook controller → queue_job → Odoo model update
```

### Rules
- Always async via queue_job (never synchronous external calls in ORM methods)
- Idempotent processing (same message processed twice = same result)
- Dead letter handling for permanently failed messages
- Monitoring and alerting on queue depth and failure rate
