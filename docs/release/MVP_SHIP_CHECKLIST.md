# Pulser for Odoo — MVP Ship Checklist

## Purpose

Use this checklist to decide whether **Pulser for Odoo** is ready to ship.

A feature is only ship-ready when it passes all five gates:
1. Product
2. Correctness
3. Runtime
4. Operational safety
5. Evidence

If any required gate is not satisfied, the feature is **implemented but not ship-ready**.

---

## 1. Feature metadata

- **Feature name:** Pulser for Odoo
- **Feature ID / spec slug:** pulser-odoo
- **Repo(s):** Insightpulseai
- **Environment target:** Azure Container Apps (ipai-odoo-dev-web)
- **Owner:** TBWA
- **Release candidate SHA(s):** 
- **Related PR(s):** 
- **Target release date:** 2026-04-10

---

## 2. Product gate

### Requirements clarity
- [ ] Acceptance criteria are explicit
- [ ] User-visible behavior matches the spec / PRD
- [ ] In-scope vs out-of-scope behavior is clear
- [ ] Edge cases are identified
- [ ] No unresolved ambiguity changes user-visible behavior

### Product sign-off
- [ ] Product/owner sign-off recorded
- [ ] Any known limitations are documented

**Gate result:** PASS / FAIL

---

## 3. Correctness gate

### Tests
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Browser / HTTP tests pass where relevant
- [ ] Negative fixtures pass
- [ ] No new blocking regressions introduced

### Feature-specific validation
- [ ] Main happy path verified
- [ ] Main failure path verified
- [ ] Data integrity / posting / workflow state transitions verified
- [ ] Query/performance regressions checked where relevant

### Current known issues
- [ ] No unresolved P0 defect
- [ ] No unresolved P1 defect without explicit waiver

**Gate result:** PASS / FAIL

---

## 4. Runtime gate

### Environment-backed validation
- [ ] Staging or revision-specific deployment available
- [ ] Live smoke tests executed against real environment
- [ ] Required external dependencies reachable
- [ ] Auth / identity works in deployed runtime
- [ ] DB connectivity works in deployed runtime
- [ ] Real ingress path works (not just direct internal URL)

### Azure-native checks
- [ ] Health probes pass
- [ ] Revision is healthy
- [ ] Front Door / edge path verified if applicable
- [ ] Managed identity / RBAC verified if applicable
- [ ] Storage / messaging / service dependencies verified if applicable

**Gate result:** PASS / FAIL

---

## 5. Operational safety gate

### Release safety
- [ ] Rollback path exists
- [ ] Rollback path has been verified or is known-good
- [ ] Blast radius is understood
- [ ] Feature flags / kill switch exist if needed

### Observability
- [ ] Logs are present
- [ ] Diagnostics are wired
- [ ] Error visibility is sufficient
- [ ] Alerts/monitors exist for material failure modes
- [ ] Audit trail exists where required

### Security / compliance
- [ ] No secrets in code or committed config
- [ ] Access control and permissions reviewed
- [ ] Compliance-sensitive behavior validated where relevant

**Gate result:** PASS / FAIL

---

## 6. Evidence gate

### Evidence pack
- [ ] Test evidence attached
- [ ] Smoke evidence attached
- [ ] Screenshots or logs attached where relevant
- [ ] Known exceptions documented
- [ ] Go / No-Go owner identified

### Documentation
- [ ] Relevant docs/specs updated
- [ ] Release notes / operator notes updated if needed
- [ ] Runbook changes documented if needed

**Gate result:** PASS / FAIL

---

## 7. Known exceptions

List all exceptions explicitly.

### Exception 1
- Description:
- Severity:
- Owner:
- Accepted for release: yes / no
- Reason:

### Exception 2
- Description:
- Severity:
- Owner:
- Accepted for release: yes / no
- Reason:

---

## 8. Final decision

### Gate summary

| Gate | Result |
|---|---|
| Product | PASS / FAIL |
| Correctness | PASS / FAIL |
| Runtime | PASS / FAIL |
| Operational safety | PASS / FAIL |
| Evidence | PASS / FAIL |

### Decision rule

Ship only if:
- [ ] Product gate = PASS
- [ ] Correctness gate = PASS
- [ ] Runtime gate = PASS
- [ ] Operational safety gate = PASS
- [ ] Evidence gate = PASS

### Final call
- **Decision:** GO / NO-GO
- **Decision owner:**  
- **Timestamp:**  
- **Notes:**  

---

## 9. Interpretation guide

### Implemented but not ship-ready
Use this when:
- code exists
- tests may pass
- but runtime validation, rollback, or evidence is incomplete

### Ship-ready
Use this only when:
- the feature works
- the deployed environment proves it works
- failure can be observed and managed
- evidence exists for later review

### Do not ship
Use this when:
- any blocker remains
- live smoke is missing for a feature that depends on runtime integrations
- rollback/observability is absent for a material-risk feature
