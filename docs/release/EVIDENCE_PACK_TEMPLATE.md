# Evidence Pack Template

## Purpose

Use this template to capture the evidence required to close the final deployment-readiness gates for:

- `odoo`
- `agent-platform`
- `infra`

This pack is for **real environment-backed smoke runs**, not local-only execution.

---

## 1. Run metadata

- **Run ID:**
- **Date / Time (UTC):**
- **Operator:**
- **Environment:**
- **Azure subscription:**
- **Resource group(s):**
- **Revision / deployment label:**
- **Commit SHA(s):**
  - `odoo`:
  - `agent-platform`:
  - `infra`:
- **Triggered by:** manual / CI / scheduled
- **Workflow URL:**
- **PR / release reference:**

---

## 2. Scope of this evidence run

Mark all that apply.

- [ ] Odoo lane confirmation
- [ ] agent-platform live smoke
- [ ] infra live smoke
- [ ] staging revision verification
- [ ] pre-cutover verification
- [ ] post-cutover verification
- [ ] rollback verification

---

## 3. Odoo lane evidence

### 3.1 Test results
- `TransactionCase` result:
- `HttpCase` result:
- standalone validator/eval result:
- total counts:

### 3.2 Negative fixture result
Attachment / fixture:
- Dataverse invoice mismatch fixture

Expected:
- `status = needs_review`
- finding includes `PRINTED_TOTAL_DUE_MISMATCH`
- auto-post blocked

Actual:
- status:
- findings:
- blocker enforced: yes / no

### 3.3 Evidence links
- test log:
- screenshot(s):
- artifact path:

---

## 4. Agent-platform live smoke evidence

### 4.1 Environment variables present
- [ ] `FOUNDRY_PROJECT_ENDPOINT`
- [ ] `FOUNDRY_MODEL`
- [ ] `DOCINTEL_ENDPOINT`
- [ ] `DOCINTEL_KEY`
- [ ] `TEST_INVOICE_PATH` or equivalent fixture path

### 4.2 Foundry smoke
Expected:
- `AIProjectClient` initializes
- `get_openai_client()` succeeds
- minimal response request succeeds

Actual:
- pass / fail
- response summary:
- error summary (if any):

### 4.3 Document Intelligence smoke
Expected:
- `prebuilt-invoice` extraction returns usable content/documents

Actual:
- pass / fail
- extracted top-level fields:
- confidence notes:
- error summary (if any):

### 4.4 Live negative invoice path
Expected:
- `status = needs_review`
- `expected_payable = 95408.16`
- `printed_total_due = 85000.00`
- finding includes `PRINTED_TOTAL_DUE_MISMATCH`

Actual:
- status:
- expected_payable:
- printed_total_due:
- findings:
- pass / fail:

### 4.5 API contract evidence
Expected:
- Odoo bridge contract accepted
- no schema/contract break

Actual:
- pass / fail
- contract version:
- notes:

### 4.6 Evidence links
- smoke logs:
- JSON responses:
- screenshots:
- artifact path:

---

## 5. Infra live smoke evidence

### 5.1 Azure Container Apps
Expected:
- health endpoint responds successfully
- login endpoint responds successfully
- probes/revision are healthy

Actual:
- health endpoint:
- login endpoint:
- revision status:
- pass / fail:

Evidence:
- ACA URL:
- revision label:
- logs:
- screenshots:

### 5.2 Front Door
Expected:
- origin reachable through Front Door
- health path succeeds
- login path succeeds

Actual:
- health path:
- login path:
- pass / fail:

Evidence:
- Front Door URL:
- logs:
- screenshots:

### 5.3 Managed identity / RBAC
Expected:
- managed identity principal is bound
- required roles present
- denied path behaves correctly when tested

Actual:
- principal ID:
- required roles:
- denied-path result:
- pass / fail:

Evidence:
- CLI output:
- logs:
- screenshots:

### 5.4 PostgreSQL
Expected:
- server reachable
- SSL connection works
- HA mode present if required
- reconnect smoke succeeds

Actual:
- connectivity:
- SSL:
- HA mode:
- reconnect:
- pass / fail:

Evidence:
- CLI / SQL output:
- logs:
- screenshots:

---

## 6. Release safety evidence

### 6.1 Revision / staging verification
- staging or labeled revision used: yes / no
- smoke run executed against non-production revision first: yes / no

### 6.2 Cutover / rollback
- traffic shift tested: yes / no
- rollback path tested: yes / no
- outcome:

### 6.3 Known exceptions reviewed
- [ ] pre-existing exceptions reviewed
- [ ] no new blocker introduced by current patch

Notes:
- `odoorpc` pre-existing issue reviewed: yes / no
- blocker for this release: yes / no

---

## 7. Final decision

### Summary
- Odoo lane: pass / fail
- agent-platform lane: pass / fail
- infra lane: pass / fail

### Go / No-Go
- **Decision:** GO / NO-GO
- **Decision owner:**
- **Timestamp:**
- **Reason:**

---

## 8. Artifact index

Attach or link every generated artifact here.

### Logs
-
-

### Screenshots
-
-

### JSON outputs
-
-

### CI workflow links
-
-

### Related docs
- `docs/release/DEPLOYMENT_READINESS_CHECKLIST.md`
- `docs/quality/AZURE_NATIVE_TEST_STRATEGY.md`
- `ssot/testing/repo-test-matrix.yaml`
