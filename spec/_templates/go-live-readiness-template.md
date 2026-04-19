# Go-Live Readiness Template

> Copy to `docs/evidence/<YYYYMMDD-HHMM>/go-live/<capability-slug>/readiness-review.md`
> Fill every section. Every `[ ]` must be closed with evidence before GO.

**Capability**: `<capability_slug>`
**Go-live target date**: `<YYYY-MM-DD>`
**Gate scope**: `first_gate | phase_1b | phase_2 | decide_now` (per [go-live-scope-matrix.yaml](../../ssot/release/go-live-scope-matrix.yaml))
**Review owner**: `<name>`
**Decision authority**: `<role/person — e.g., Khalil (FD) for finance; platform-architecture for runtime>`

---

## Summary

- **Recommendation**: `GO | NO-GO | DELAY`
- **Critical blockers remaining**: `<count>`
- **High-severity blockers remaining**: `<count>`
- **Hypercare window**: `48h | 72h | 96h`
- **Rollback drill date**: `<YYYY-MM-DD> (PASS | FAIL | NOT_RUN)`

## 1. Core readiness checklist

Per [ssot/release/go-live-readiness.yaml#core_readiness_checklist](../../ssot/release/go-live-readiness.yaml).

### Testing
- [ ] System integration testing (SIT) completed and signed off
- [ ] User acceptance testing (UAT) completed and signed off
- [ ] Performance testing completed and signed off

### Deployable artifacts
- [ ] Code finished
- [ ] Deployable packages built

### Data
- [ ] Data migration plan documented

### Cutover
- [ ] Cutover plan signed off
- [ ] Cutover window defined
- [ ] Rollback window defined

### People
- [ ] User training completed
- [ ] Security role assignments correct
- [ ] License allocation sufficient

### Support
- [ ] Production support plan signed off
- [ ] On-call coverage confirmed for cutover window
- [ ] Escalation contacts documented

### Risk
- [ ] Critical open issues from prior reviews mitigated

## 2. Go / No-Go matrix

### GO conditions (all required)

- [ ] Core readiness checklist complete
- [ ] Readiness review report published
- [ ] No unmitigated critical blockers
- [ ] Cutover plan signed off by stakeholders
- [ ] Production support on-call confirmed
- [ ] Rollback plan tested in preprod

### NO-GO triggers (any one disqualifies)

- [ ] Unmitigated critical blocker
- [ ] Cutover plan unsigned
- [ ] Support coverage gap during cutover window
- [ ] Rollback plan untested
- [ ] Environment drift between preprod and prod
- [ ] Licensing gap for active users

## 3. Blocker register

| ID | Severity | Category | Description | Surface affected | Mitigation | Owner | Target date | Status |
|---|---|---|---|---|---|---|---|---|
| BLOCKER-01 | critical / high / medium / low |   |   |   |   |   |   | open / closed |

## 4. Cutover plan

### Pre-cutover
- [ ] Final data export from source
- [ ] Source writes frozen (if applicable)
- [ ] Pre-flight smoke tests passed

### During cutover
- [ ] Data migration executed
- [ ] Code + config deployed
- [ ] Post-deploy smoke passed
- [ ] Monitoring active

### Post-cutover
- Hypercare window: `<hours>`
- [ ] Daily go-live status report
- [ ] Incident escalation ready
- [ ] Rollback criteria monitored

## 5. Rollback plan

- Rollback triggers:
- Rollback steps (numbered):
- Rollback time budget:
- Post-rollback communication plan:
- Drill date + result:

## 6. Surface-specific gates (if applicable)

### Mobile PWA-specific (if mobile surface in scope)

Per [pulser_expense_mobile_companion pwa_specific_readiness_gates](../../ssot/release/go-live-scope-matrix.yaml):

- [ ] Web App Manifest published
- [ ] Service Worker registered + passing Lighthouse PWA audit
- [ ] HTTPS + installability verified
- [ ] getUserMedia camera path verified
- [ ] Receipt upload path verified
- [ ] Foundry OCR extraction path verified
- [ ] Expense draft submit path verified
- [ ] Approval action path verified
- [ ] Web Push VAPID configured (Android + desktop)
- [ ] iOS Safari Web Push 16.4+ caveat documented
- [ ] Offline queue background sync tested
- [ ] Entra OAuth PKCE mobile flow verified
- [ ] Rollback path for PWA companion defined

### Asset Ops-specific (if asset ops surface in scope)

- [ ] Scan flow verified
- [ ] Mobile camera / scan UX verified
- [ ] Booking conflict logic verified
- [ ] Custody audit trail verified
- [ ] Room / resource permissions verified
- [ ] Return / damage workflow verified

## 7. Evidence pack contents

Per [ssot/release/go-live-readiness.yaml#evidence_requirements](../../ssot/release/go-live-readiness.yaml):

- [ ] `readiness_review_report.md` (this file)
- [ ] `core_readiness_checklist_completed.yaml`
- [ ] `cutover_plan_signed.md`
- [ ] `rollback_plan_tested.md`
- [ ] `support_plan_signed.md`
- [ ] `blocker_register.yaml`
- [ ] `go_no_go_decision.md`
- [ ] `post_cutover_hypercare_log.md` (added after cutover)

## 8. Decision

**Recommendation**: `GO | NO-GO | DELAY`
**Rationale**:

**Signatures**:

| Role | Name | Date | Signature |
|---|---|---|---|
| Platform architecture | | | |
| Security reviewer | | | |
| Business owner | | | |
| Finance approver (if finance touched) | | | |
| Data intelligence (if UC/semantic/OData touched) | | | |

---

## Related

- Unified template: [unified-capability-template.md](unified-capability-template.md)
- Boards mapping: [azure-boards-mapping.md](azure-boards-mapping.md)
- Go-live SSOT: [ssot/release/go-live-readiness.yaml](../../ssot/release/go-live-readiness.yaml)
- Scope matrix: [ssot/release/go-live-scope-matrix.yaml](../../ssot/release/go-live-scope-matrix.yaml)
- Example: [docs/evidence/20260419-1800/go-live-readiness-review/](../../docs/evidence/20260419-1800/go-live-readiness-review/)
