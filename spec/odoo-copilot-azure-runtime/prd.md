# PRD — Odoo Copilot on Azure Runtime

## 1. Problem

Odoo Copilot may already have partial routes, UI, or benchmark scaffolding, but it is not operational until the runtime path to Azure OpenAI is complete, authenticated, and reproducible on Azure.

Current risk areas typically include:

- provider bridge not configured
- wrong Azure model/deployment identifier
- secrets not wired correctly
- route works locally but not in Azure runtime
- no clear runtime SSOT for provider config
- no end-to-end production-safe validation

---

## 2. Goal

Make Odoo Copilot operational on Azure by implementing a working authenticated Odoo → Azure OpenAI runtime path with machine-readable provider configuration and Azure-native operational wiring.

---

## 3. Users

### Primary
- authenticated Odoo user
- platform operator
- ERP/runtime maintainer

### Secondary
- benchmark runner / QA
- support operator debugging Copilot failures

---

## 4. User stories

- As an authenticated Odoo user, I want to submit a Copilot prompt from the ERP workspace and receive a valid response.
- As a runtime maintainer, I want provider settings to be explicit and reproducible.
- As an operator, I want to know whether Copilot is broken because of route, auth, provider, or secret wiring.
- As a benchmark runner, I want a live target that can be exercised end-to-end.

---

## 5. Functional requirements

### FR-1 Odoo route
A working Odoo route/controller must accept Copilot requests and return structured responses.

### FR-2 Auth context
The route must run only for authenticated users and preserve persona/user context.

### FR-3 Provider bridge
The route must call Azure OpenAI using configured runtime inputs.

### FR-4 Azure deployment name
The provider call must use Azure deployment name configuration.

### FR-5 Structured errors
The system must return safe structured errors when provider calls fail.

### FR-6 Machine-readable provider config
Provider configuration must be represented in `ssot/odoo/copilot-provider.yaml`.

### FR-7 Runtime documentation
An architecture/runtime doc must describe the Azure-backed Copilot flow.

### FR-8 End-to-end validation
At least one end-to-end Azure-backed request must succeed.

---

## 6. Non-functional requirements

### NFR-1 No repo secrets
No live secrets may be committed.

### NFR-2 Azure-native alignment
Configuration must align with Azure-native runtime assumptions.

### NFR-3 Runtime safety
Copilot must not break Odoo health/login surfaces.

### NFR-4 Diagnosability
Logs and errors must make route/provider failures distinguishable.

### NFR-5 Reproducibility
The runtime contract must be redeployable from repo-managed config and docs.

---

## 7. Acceptance criteria

The feature is accepted when:

- `erp.insightpulseai.com` remains healthy
- an authenticated Odoo user can submit a Copilot prompt
- the Odoo route returns an Azure-backed response
- provider SSOT exists
- runtime doc exists
- deployment and validation evidence exists

---

## 8. Risks

- wrong Azure deployment name
- missing or miswired Key Vault secret
- auth/session mismatch in route
- timeout/latency problems
- production-safe route not yet hardened
- benchmark expects behavior not yet implemented

---

## 9. Release slices

### Slice 1
- provider SSOT
- runtime doc
- route/controller wiring review

### Slice 2
- Azure OpenAI-backed successful response from Odoo

### Slice 3
- production-safe error handling and validation evidence
