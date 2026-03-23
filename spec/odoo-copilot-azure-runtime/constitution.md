# Odoo Copilot on Azure Runtime — Constitution

## 1. Purpose

Define the canonical runtime contract for making Odoo Copilot operational on Azure.

This spec governs:

- Odoo-side Copilot route/controller behavior
- Azure OpenAI provider configuration
- Azure-native secret handling
- runtime placement and health expectations
- permission, audit, and deployment boundaries

This spec is runtime-focused. It does not redefine the benchmark framework or platform-wide Azure architecture.

---

## 2. Scope

In scope:

- authenticated Copilot request/response flow inside Odoo
- provider bridge configuration for Azure OpenAI
- Azure-native secret and identity wiring assumptions
- operational health checks
- minimal production-safe error handling
- machine-readable provider SSOT

Out of scope:

- full multi-provider routing marketplace
- advanced agent orchestration outside Odoo
- non-Odoo chat surfaces
- deep UI redesign
- model evaluation framework design

---

## 3. Canonical architecture

The canonical runtime path is:

Browser
→ `erp.insightpulseai.com`
→ Odoo web/client
→ Odoo Copilot controller
→ provider bridge
→ Azure OpenAI deployment

Copilot should run in the Odoo runtime first, not as a separate microservice by default.

---

## 4. Ownership boundaries

### `odoo`
Owns:
- Copilot UI entry in ERP workspace
- route/controller behavior
- persona and permission checks
- request shaping and response handling
- runtime docs and provider SSOT

### `infra`
Owns:
- ACA / Front Door / DNS / Key Vault / managed identity
- Azure runtime/service inventory
- domain routing and health topology

### `platform`
Optional owner for:
- control-plane metadata if provider settings are tracked there

---

## 5. Non-negotiable runtime rules

### 5.1 Canonical public surface
The public ERP/Copilot hostname is:

- `https://erp.insightpulseai.com`

ACA-generated hostnames are implementation details only.

### 5.2 Authenticated use only
Copilot requests must run in authenticated Odoo context.

### 5.3 Permission-aware context
Copilot must not bypass Odoo permission boundaries.

### 5.4 Azure deployment name addressing
Azure OpenAI requests must use the configured Azure deployment name, not only the base model family name.

### 5.5 Secret discipline
Secrets must not be hardcoded in repo config. Azure-native secret flow should use Key Vault-backed secret references where possible.

### 5.6 Health safety
Copilot enablement must not break core Odoo health endpoints or login surface.

---

## 6. Provider contract

The provider contract must include at least:

- provider type
- API mode
- base URL env var name
- API key env var name
- deployment env var name
- timeout
- auth requirement
- persona requirement

This must be represented in machine-readable SSOT.

---

## 7. Operational minimum

Copilot is only considered operational when:

- Odoo login works
- Copilot route responds successfully
- Azure OpenAI provider call succeeds
- secrets are wired correctly
- logs show successful request handling
- at least one authenticated persona can complete end-to-end chat

---

## 8. Anti-goals

This work must not:

- introduce a second canonical ERP public hostname
- move ERP auth out of Odoo without an explicit platform decision
- hardcode secrets in repo files
- create a separate Copilot microservice prematurely
- bypass CI/runtime validation

---

## 9. Success doctrine

This work succeeds when a real user can authenticate to Odoo at `erp.insightpulseai.com`, submit a Copilot prompt, receive an Azure OpenAI-backed response, and do so with reproducible Azure-native runtime configuration.
