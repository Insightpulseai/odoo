# Tasks — Odoo Copilot on Azure Runtime

## Epic 1 — Provider Contract

- [ ] Create `ssot/odoo/copilot-provider.yaml`
- [ ] Define Azure OpenAI env contract
- [ ] Define deployment-name requirement
- [ ] Define timeout/auth/persona requirements

**GATE: Provider SSOT exists and is machine-readable**

---

## Epic 2 — Runtime Documentation

- [ ] Create `docs/architecture/ODOO_COPILOT_AZURE_RUNTIME.md`
- [ ] Document canonical runtime path
- [ ] Document repo ownership split (`odoo` / `infra` / optional `ops-platform`)
- [ ] Document Azure-native secret/runtime assumptions

**GATE: Runtime document exists and matches provider SSOT**

---

## Epic 3 — Route / Bridge Validation

- [ ] Identify canonical Copilot controller/route
- [ ] Verify authenticated request path
- [ ] Verify Azure OpenAI provider bridge call path
- [ ] Verify deployment-name configuration is used at runtime

**GATE: Route/bridge contract is identified and validated**

---

## Epic 4 — Live Azure Response

- [ ] Configure runtime env inputs for Azure OpenAI
- [ ] Execute one authenticated end-to-end Copilot request
- [ ] Capture success or structured failure evidence
- [ ] Record validation output

**GATE: At least one Azure-backed Copilot response succeeds end-to-end**

---

## Epic 5 — Operational Hardening

- [ ] Verify `/web/health` remains healthy
- [ ] Verify `/web/login` remains healthy
- [ ] Verify logs distinguish route vs provider failures
- [ ] Add/update evidence or report artifact

**GATE: Copilot is operational without breaking core Odoo runtime surfaces**
