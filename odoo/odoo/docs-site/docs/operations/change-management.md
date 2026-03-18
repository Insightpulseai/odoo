# Change management

Governance framework for changes to financial systems, accounting policies, and operational procedures. Covers change categories, risk assessment, UAT, production deployment, and period unlock.

---

## Change categories

| Category | Description | Approval level | Examples |
|----------|-------------|----------------|----------|
| **Administrative** | Low-risk changes to non-financial configuration | Department Manager | User access updates, report formatting |
| **Operational** | Process changes that affect daily workflows | Accounting Manager | New reconciliation rules, payment approval thresholds |
| **Control** | Changes to internal controls or segregation of duties | Controller + CFO | Approval matrix changes, new control points |
| **System** | Technical changes to Odoo modules, integrations, or infrastructure | IT Manager + Controller | Module upgrades, API integrations, database changes |
| **Emergency** | Unplanned changes to resolve critical issues | CFO (retroactive) | Data corrections, period unlock for error fixing |

---

## Change request lifecycle

Every change follows 7 phases:

```
1. Request → 2. Assessment → 3. Approval → 4. Planning → 5. Execution → 6. Verification → 7. Closure
```

### Phase details

??? abstract "1. Request"
    - Submit change request with business justification.
    - Include: scope, affected modules/processes, expected outcome, urgency.
    - Assign a change owner.

??? abstract "2. Assessment"
    - Classify the change category (see table above).
    - Perform risk assessment (see [risk scoring](#risk-assessment) below).
    - Identify affected stakeholders and downstream impacts.
    - Estimate effort and timeline.

??? abstract "3. Approval"
    - Route to the appropriate approver based on category.
    - For Control and System changes: require Change Management Committee review.
    - Document approval with date and approver name.

??? abstract "4. Planning"
    - Define implementation steps.
    - Identify rollback procedure.
    - Schedule execution window (see [deployment windows](#production-deployment)).
    - Prepare UAT plan (see [UAT framework](#uat-framework)).

??? abstract "5. Execution"
    - Execute in staging environment first.
    - Run UAT.
    - Deploy to production during allowed window.
    - Communicate to affected users.

??? abstract "6. Verification"
    - Verify the change achieves its stated objective.
    - Run post-deployment checks.
    - Confirm no regressions.

??? abstract "7. Closure"
    - Document lessons learned.
    - Archive change request and supporting evidence.
    - Update process documentation if applicable.

---

## Risk assessment

### Scoring formula

```
Risk score = (Likelihood × Impact) / 2
```

### Likelihood scale

| Score | Likelihood | Description |
|:-----:|------------|-------------|
| 1 | Rare | Unlikely to cause issues |
| 2 | Unlikely | Could cause issues under unusual conditions |
| 3 | Possible | May cause issues under normal conditions |
| 4 | Likely | Will probably cause issues |
| 5 | Almost certain | Will cause issues |

### Impact scale

| Score | Impact | Description |
|:-----:|--------|-------------|
| 1 | Negligible | No financial impact, cosmetic only |
| 2 | Minor | < PHP 10,000 or minor inconvenience |
| 3 | Moderate | PHP 10,000–100,000 or workflow disruption |
| 4 | Major | PHP 100,000–1,000,000 or compliance risk |
| 5 | Critical | > PHP 1,000,000 or regulatory violation |

### Risk matrix

| Risk score | Level | Required approval |
|:----------:|-------|-------------------|
| 1.0–2.5 | Low | Department Manager |
| 3.0–5.0 | Medium | Accounting Manager |
| 5.5–7.5 | High | Controller |
| 8.0–12.5 | Critical | CFO + Change Management Committee |

??? example "Risk scoring example"
    **Change**: Modify the WHT auto-calculation logic in `ipai_bir_filing`.

    - Likelihood of issues: 4 (likely — tax calculations are sensitive)
    - Impact: 4 (major — incorrect WHT causes BIR penalties)
    - Risk score: (4 × 4) / 2 = **8.0 — Critical**
    - Required approval: CFO + Change Management Committee

---

## UAT framework

User acceptance testing follows 4 phases.

### Phase 1 — Test planning

| Item | Description |
|------|-------------|
| Test scope | Define what is being tested (module, workflow, integration) |
| Test data | Prepare test data in `odoo_dev` database — never use production data |
| Test cases | Write test cases covering happy path, edge cases, and error handling |
| Acceptance criteria | Define pass/fail criteria before testing begins |

### Phase 2 — Test execution

- Execute all test cases in the staging environment.
- Record results: pass, fail, or blocked.
- Log defects with steps to reproduce.

### Phase 3 — Defect resolution

- Prioritize defects: critical (blocks go-live), major (workaround exists), minor (cosmetic).
- Fix critical and major defects before proceeding.
- Re-test fixed defects.

### Phase 4 — Sign-off

- Business owner reviews test results.
- Sign-off confirms the change meets acceptance criteria.
- No go-live without written sign-off.

!!! warning "No sign-off, no deployment"
    Never deploy a Control or System change to production without documented UAT sign-off.

---

## Production deployment

### Allowed windows

| Window | Schedule | Use case |
|--------|----------|----------|
| **Standard** | Saturdays, 06:00–12:00 PHT | System and Control changes |
| **Minor** | Weekdays, 18:00–20:00 PHT | Administrative and Operational changes |
| **Emergency** | Any time | Emergency changes only (CFO approval required) |

### Prohibited windows

| Period | Reason |
|--------|--------|
| Days 1–5 of financial close | Close cycle in progress |
| BIR filing deadline ± 2 days | Risk of filing disruption |
| External audit fieldwork | Auditor reliance on system stability |
| Payroll processing window | Risk of payroll errors |

### Deployment checklist

- [ ] UAT sign-off obtained
- [ ] Rollback plan documented and tested
- [ ] Database backup completed
- [ ] Affected users notified
- [ ] Deployment executed in allowed window
- [ ] Post-deployment verification passed
- [ ] Change record updated

### Rollback procedure

1. Stop the Odoo service.
2. Restore the database from the pre-deployment backup.
3. Revert module code to the prior version (`git revert` or `git checkout`).
4. Restart the Odoo service.
5. Verify system functionality.
6. Notify affected users.

```bash
# Rollback example
systemctl stop odoo
pg_restore -Fc -d odoo /backups/odoo_pre_deploy.dump
cd /workspaces/odoo && git revert HEAD
systemctl start odoo
```

---

## Period unlock

### When to unlock

Unlock a locked accounting period only when a material error requires correction. Routine adjustments go into the current period — do not unlock for convenience.

### Authorization hierarchy

| Scenario | Authorizer |
|----------|------------|
| Current month unlock | Accounting Manager |
| Prior quarter unlock | Controller |
| Prior year unlock | CFO |
| Audited year unlock | CFO + External Auditor consent |

### 5-step unlock process

1. **Request**: Submit a period unlock request with:
    - Period to unlock
    - Specific entries to post (journal entry drafts attached)
    - Business justification
    - Impact assessment (which reports/filings are affected)

2. **Approval**: Obtain authorization per the hierarchy above. Document approver, date, and scope.

3. **Unlock**: Change the lock date in Odoo to allow posting.

    ```
    Accounting > Configuration > Settings > Fiscal Period Lock Date
    ```

    !!! danger "Scope limitation"
        Only unlock the specific period needed. Never remove the lock date entirely.

4. **Post entries**: Post only the approved entries. No other modifications are permitted during the unlock window.

    ```sql
    -- Verify only approved entries were posted during the unlock window
    SELECT id, name, date, ref, create_date
    FROM account_move
    WHERE date BETWEEN '2026-02-01' AND '2026-02-28'
      AND create_date > '2026-03-10'
    ORDER BY create_date;
    ```

5. **Re-lock**: Immediately re-lock the period after posting. Verify the lock is effective.

!!! warning "Audit trail"
    Every period unlock creates an audit trail. The `account.move` `create_date` will show entries posted after the original close date. External auditors review these as subsequent events.

---

## Governance

### Change Management Committee

| Role | Member |
|------|--------|
| Chair | CFO |
| Members | Controller, IT Manager, Tax Manager, Accounting Manager |
| Secretary | Senior Accountant |

**Meeting cadence**: Monthly (or ad hoc for critical changes).

**Responsibilities**:

- Review and approve high/critical risk changes
- Review post-implementation reports
- Update change management policies
- Quarterly review of all changes and their outcomes

### Quarterly review

Each quarter, the Change Management Committee reviews:

1. **Change volume**: Total changes by category and risk level.
2. **Success rate**: Percentage of changes deployed without rollback.
3. **Incident correlation**: Changes linked to incidents or errors.
4. **Process improvements**: Opportunities to streamline the change process.
5. **Policy updates**: Adjustments to risk thresholds, approval matrix, or deployment windows.
