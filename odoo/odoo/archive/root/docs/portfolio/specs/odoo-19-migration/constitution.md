# Odoo 19 Migration - Constitution
---
**Purpose**: Define the principles, constraints, and governance for the Odoo 19 migration project.
**Scope**: All migration activities from Odoo 18 CE to Odoo 19 CE
**Authority**: This document governs all technical decisions during migration.
---

## 1. Core Principles

### 1.1 Smart Delta Philosophy (MANDATORY)
```
CE + OCA + ipai_* = Enterprise Parity

Base Layer:     Odoo 19 CE (stable, upstream)
Extension:      OCA modules (community-vetted)
Customization:  ipai_* modules (business-specific)
```

**Rules:**
1. NEVER fork Odoo core or OCA modules
2. ALWAYS use `_inherit` to extend, never replace
3. PREFER configuration over code
4. DOCUMENT every deviation from standard patterns

### 1.2 Zero Data Loss (MANDATORY)
```
Every record in Odoo 18 MUST exist in Odoo 19 post-migration.

Validation:
- Pre-migration record counts stored
- Post-migration record counts compared
- Checksums on critical tables (account_move, hr_payslip)
- Audit trail preserved
```

### 1.3 Minimal Downtime (TARGET: <4 hours)
```
Production cutover window: Saturday 10 PM - Sunday 2 AM PHT
Rollback decision point: Sunday 12 AM (2 hours in)
Full rollback completion: Sunday 2 AM
```

### 1.4 BIR Compliance First (MANDATORY)
```
BIR compliance is NON-NEGOTIABLE.

Before declaring migration complete:
- [ ] 1601-C report generates correctly
- [ ] 2316 certificates generate correctly
- [ ] Alphalist exports correctly
- [ ] VAT reports accurate
- [ ] 10-year audit trail preserved
```

---

## 2. Technical Constraints

### 2.1 Infrastructure Boundaries

| Component | Allowed | Prohibited |
|-----------|---------|------------|
| Cloud | DigitalOcean | AWS, Azure, GCP |
| Database | PostgreSQL 16 | MySQL, SQLite |
| Container | Docker | Kubernetes (for now) |
| CI/CD | GitHub Actions | Jenkins, CircleCI |
| Monitoring | Sentry, Superset | Datadog, New Relic |

### 2.2 Code Standards

#### Python
```python
# REQUIRED: Type hints for all new code
def compute_sss_contribution(
    gross_salary: Decimal,
    year: int = 2025
) -> tuple[Decimal, Decimal]:
    """
    Compute SSS employee and employer contributions.

    Args:
        gross_salary: Monthly gross salary
        year: Contribution table year

    Returns:
        Tuple of (employee_share, employer_share)
    """
    ...

# REQUIRED: Docstrings for all public methods
# REQUIRED: Error handling with specific exceptions
# PROHIBITED: Bare except clauses
# PROHIBITED: Mutable default arguments
```

#### XML Views
```xml
<!-- REQUIRED: Use <list> not <tree> (Odoo 19 standard) -->
<list string="Payslips">
    <field name="employee_id"/>
    <field name="date_from"/>
    <field name="date_to"/>
    <field name="state"/>
</list>

<!-- PROHIBITED: Deprecated <tree> tag -->
<!-- <tree string="Payslips">...</tree> -->

<!-- REQUIRED: Explicit field permissions -->
<field name="salary" groups="hr_payroll.group_hr_payroll_manager"/>
```

#### JavaScript (OWL 2.x)
```javascript
// REQUIRED: Use OWL 2.x patterns
import { Component, useState } from "@odoo/owl";

export class PayslipWidget extends Component {
    static template = "ipai_hr_payroll_ph.PayslipWidget";

    setup() {
        this.state = useState({ loading: false });
    }
}

// PROHIBITED: OWL 1.x patterns
// const { Component } = owl;
// class PayslipWidget extends Component { ... }
```

### 2.3 Database Constraints

```sql
-- REQUIRED: All custom tables must have audit fields
CREATE TABLE ipai_custom_table (
    id SERIAL PRIMARY KEY,
    -- Business fields...
    create_uid INTEGER REFERENCES res_users(id),
    create_date TIMESTAMP DEFAULT NOW(),
    write_uid INTEGER REFERENCES res_users(id),
    write_date TIMESTAMP DEFAULT NOW()
);

-- REQUIRED: Foreign keys must have ON DELETE policy
FOREIGN KEY (employee_id) REFERENCES hr_employee(id) ON DELETE RESTRICT

-- PROHIBITED: Direct database modifications in production
-- Always use Odoo ORM or migrations
```

### 2.4 Module Naming Convention

```
ipai_<functional_area>[_<sub_area>]

Examples:
  ipai_hr_payroll_ph       # HR Payroll for Philippines
  ipai_bir_1601c           # BIR Form 1601-C
  ipai_connector_vercel    # Vercel integration
  ipai_approvals           # Approval workflows

Prohibited:
  custom_payroll           # No 'custom_' prefix
  payroll_ph               # Must have 'ipai_' prefix
  ipai_PayrollPH           # No CamelCase
```

---

## 3. Migration Rules

### 3.1 Module Migration Checklist

Every ipai_* module must complete this checklist before being marked "migrated":

```markdown
## Module: ipai_[name]

### Compatibility
- [ ] `__manifest__.py` version updated to 19.0
- [ ] All `<tree>` tags replaced with `<list>`
- [ ] OWL components migrated to 2.x
- [ ] Python 3.12 syntax validated
- [ ] No deprecated Odoo API calls

### Testing
- [ ] Unit tests pass (`odoo-bin --test-enable`)
- [ ] Integration tests pass
- [ ] Manual smoke test completed
- [ ] Performance benchmark recorded

### Documentation
- [ ] README.md updated
- [ ] CHANGELOG.md updated
- [ ] Migration notes documented

### Sign-off
- [ ] Code review approved
- [ ] QA sign-off
- [ ] Ready for staging
```

### 3.2 Breaking Change Protocol

When encountering a breaking change:

```
1. DOCUMENT the change in docs/BREAKING_CHANGES.md
2. CREATE a migration script if data transformation needed
3. UPDATE all affected modules atomically
4. TEST the full dependency chain
5. NOTIFY stakeholders if user-facing
```

### 3.3 Dependency Management

```
Dependency Update Order:
1. Odoo CE core (provided by upstream)
2. OCA modules (community releases)
3. ipai_* modules (our responsibility)

Rule: Never update ipai_* module to depend on unreleased OCA module.
```

---

## 4. Testing Requirements

### 4.1 Test Coverage Minimums

| Module Type | Unit Test | Integration | E2E |
|-------------|-----------|-------------|-----|
| Core (payroll, accounting) | 80% | 100% | 100% |
| Service (helpdesk, planning) | 70% | 80% | 50% |
| Connector (integrations) | 60% | 100% | 50% |
| Utility (helpers) | 90% | 50% | - |

### 4.2 Mandatory Test Scenarios

```python
# Every financial module MUST test:
class TestBIRCompliance:
    def test_1601c_generation(self):
        """BIR 1601-C must generate with correct totals."""

    def test_2316_generation(self):
        """BIR 2316 must include all required fields."""

    def test_withholding_tax_computation(self):
        """Tax computation must match BIR TRAIN tables."""

    def test_decimal_precision(self):
        """All amounts must have exactly 2 decimal places."""
```

### 4.3 Performance Baselines

```yaml
# Benchmarks must not regress more than 10%
operations:
  invoice_create: 200ms
  payslip_compute: 500ms
  bank_reconcile_100_lines: 5s
  trial_balance_10k_records: 10s
  report_export_pdf: 3s
```

---

## 5. Deployment Rules

### 5.1 Environment Progression

```
Development → Staging → UAT → Production

Rules:
- Code MUST pass CI in each environment before promotion
- Database MUST be snapshot before each deployment
- Rollback MUST be tested before production deployment
```

### 5.2 Production Deployment Checklist

```markdown
## Pre-Deployment (T-24h)
- [ ] All tests passing in staging
- [ ] UAT sign-off received
- [ ] Backup verified
- [ ] Rollback tested
- [ ] Communication sent to stakeholders

## Deployment (T-0)
- [ ] Maintenance mode enabled
- [ ] Database backup taken
- [ ] Deployment executed
- [ ] Smoke tests passed
- [ ] Monitoring verified

## Post-Deployment (T+1h)
- [ ] User acceptance confirmed
- [ ] Performance baseline verified
- [ ] No critical errors in logs
- [ ] Maintenance mode disabled
```

### 5.3 Rollback Triggers

Automatic rollback if ANY of these occur:
- Error rate >5% in first 30 minutes
- Response time >3x baseline
- Critical business function fails
- Data integrity check fails

---

## 6. Communication Protocol

### 6.1 Status Updates

| Frequency | Audience | Content |
|-----------|----------|---------|
| Daily | Dev team | Blockers, progress |
| Weekly | Stakeholders | Milestone status |
| Ad-hoc | All | Critical issues |

### 6.2 Escalation Path

```
Level 1: Development team (Slack #odoo19-migration)
Level 2: Technical Lead (Jake) - within 2 hours
Level 3: Finance Director (CKVC) - within 4 hours
Level 4: Emergency rollback - immediate
```

---

## 7. Documentation Requirements

### 7.1 Required Documentation

Every migration must produce:
1. **Migration Log**: What was changed, when, by whom
2. **Breaking Changes**: User-facing changes
3. **Rollback Procedure**: Tested rollback steps
4. **Post-Migration Validation**: Checklist with results

### 7.2 Knowledge Transfer

Before project close:
- [ ] All documentation in GitHub wiki
- [ ] Runbook for common issues
- [ ] Training session for Finance team
- [ ] Recorded demo of changes

---

## 8. Governance

### 8.1 Decision Authority

| Decision Type | Authority | Escalation |
|---------------|-----------|------------|
| Technical implementation | Dev team | Technical Lead |
| Timeline changes | Technical Lead | Stakeholders |
| Scope changes | Stakeholders | Project Sponsor |
| Emergency rollback | Technical Lead | N/A (immediate) |

### 8.2 Change Control

Any change to this Constitution requires:
1. Written proposal
2. Impact assessment
3. Stakeholder review (48h)
4. Majority approval

---

## 9. Acceptance

By participating in this migration, all team members agree to:
- Follow the principles and constraints defined herein
- Escalate blockers promptly
- Prioritize data integrity and compliance
- Document all decisions and changes

---

**Document Version**: 1.0.0
**Last Updated**: 2026-01-26
**Next Review**: Before Phase 2 kickoff
