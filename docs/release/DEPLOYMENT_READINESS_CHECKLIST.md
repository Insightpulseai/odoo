# Deployment Readiness Checklist

## Scope

This checklist is the single go/no-go gate for deploying the current Odoo + agent-platform + infra scope.

It merges:
- Odoo application evidence
- agent-platform live smoke implementation
- infra Azure-native smoke implementation
- known exceptions

---

## 1. Odoo application lane

- [x] `TransactionCase` suite passes
- [x] `HttpCase` suite passes
- [x] invoice negative fixture is enforced
- [x] validator blocks autoposting on mismatch
- [x] BIR eval → validator bridge passes
- [x] no new Odoo-lane failures introduced

**Current evidence**
- 30 `TransactionCase` tests: all pass
- 12 `HttpCase` tests: all pass
- standalone validator/eval suites: all pass
- total: 86 tests, 0 failures in the Odoo-side patch evidence

---

## 2. Agent-platform lane

- [x] Foundry project-client smoke tests exist
- [x] OpenAI-compatible client smoke tests exist
- [x] Document Intelligence smoke tests exist
- [x] live invoice negative fixture test exists
- [x] TypeScript-side client/API contract tests exist
- [ ] live environment variables/secrets supplied in target environment
- [ ] live smoke suite executed successfully against real Azure resources
- [ ] live smoke evidence captured and linked

**Required pass condition**
- live Foundry + Document Intelligence path returns `needs_review` for the Dataverse negative invoice fixture
- no contract break between Odoo bridge and agent-platform API

---

## 3. Infra / Azure-native lane

- [x] ACA health probe tests exist
- [x] Front Door origin health tests exist
- [x] managed identity tests exist
- [x] PostgreSQL connectivity / HA smoke tests exist
- [x] shell smoke scripts exist
- [x] CI workflow wiring exists
- [ ] Azure runtime smoke workflow executed with real env/secrets
- [ ] ACA health checks pass against deployed revision
- [ ] Front Door health checks pass against real ingress
- [ ] managed identity success path passes
- [ ] managed identity denied-path behavior verified
- [ ] PostgreSQL smoke passes against target server
- [ ] runtime smoke evidence captured and linked

**Required pass condition**
- infra smoke gate passes in a real Azure-backed run, not just local skip mode

---

## 4. Configuration and environment readiness

- [ ] Foundry project endpoint configured
- [ ] Foundry model deployment configured
- [ ] Document Intelligence endpoint configured
- [ ] Document Intelligence credential configured
- [ ] Container App base URL configured
- [ ] Front Door base URL configured
- [ ] managed identity role assignments applied
- [ ] PostgreSQL connection variables configured
- [ ] secrets stored outside repo
- [ ] all live tests skip cleanly when env vars are absent
- [ ] all live tests run when env vars are present

---

## 5. Release safety

- [ ] staging or labeled revision available
- [ ] smoke tests run against staging/labeled revision first
- [ ] rollback path defined
- [ ] known pre-existing failures reviewed
- [ ] no new failures attributable to current patch
- [ ] release owner sign-off recorded

---

## 6. Known exception register

### Pre-existing exception
- `odoorpc` not installed
- status: pre-existing
- impact on this patch: none
- release blocker: no, unless the release explicitly depends on that lane

---

## 7. Go / No-Go decision

### GO only if all are true
- [ ] Odoo lane remains green
- [ ] agent-platform live smoke passes with real Azure resources
- [ ] infra live smoke passes with real Azure resources
- [ ] no new blocking failures
- [ ] release owner approves

### NO-GO if any are true
- [ ] live Foundry / Document Intelligence smoke fails
- [ ] ACA / Front Door / MI / PostgreSQL live smoke fails
- [ ] invoice negative fixture does not return `needs_review`
- [ ] autopost blocker regresses
- [ ] new blocker introduced in current patch set

---

## 8. Current status snapshot

### Verified complete
- [x] Odoo lane complete
- [x] agent-platform smoke tests implemented
- [x] infra smoke tests implemented
- [x] local/static behavior correct
- [x] live tests correctly skip without env vars

### Still required before deployment-ready
- [ ] one real env-backed `agent-platform` smoke run
- [ ] one real env-backed `infra` smoke run
- [ ] evidence pack attached
- [ ] final go/no-go sign-off
