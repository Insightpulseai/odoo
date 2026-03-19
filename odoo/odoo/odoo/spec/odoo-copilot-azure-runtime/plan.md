# Plan — Odoo Copilot on Azure Runtime

## 1. Strategy

Implement the smallest viable Azure-backed Copilot runtime path first:

1. define provider SSOT
2. verify route/controller contract
3. wire Azure OpenAI runtime config
4. validate end-to-end from Odoo
5. document deployment/runtime contract

---

## 2. Deliverables

### Machine-readable
- `ssot/odoo/copilot-provider.yaml`

### Human-readable
- `docs/architecture/ODOO_COPILOT_AZURE_RUNTIME.md`

### Runtime implementation review/update
- Copilot controller/bridge code in the appropriate Odoo addon(s)

### Evidence
- live runtime validation output or report

---

## 3. Provider model

The first supported provider is:

- `azure_openai`

Minimum fields:
- provider
- mode
- base_url_env
- api_key_env
- deployment_env
- timeout_seconds
- requires_auth
- requires_persona_context

---

## 4. Runtime placement

Default placement:
- Copilot runs inside the Odoo runtime surface

Do not split into a separate microservice unless a later scale/isolation decision requires it.

---

## 5. Validation phases

### Phase 1 — Static/runtime contract
- provider SSOT exists
- doc exists
- route/controller path identified
- environment variable contract defined

### Phase 2 — Live route validation
- authenticated route call succeeds
- Azure OpenAI responds successfully
- structured failure path works if provider call fails

### Phase 3 — Operationalization
- logs are usable
- health/login are unaffected
- benchmark/live execution can target this runtime

---

## 6. Open implementation points

The implementation must confirm:
- exact controller path
- exact addon owner(s)
- exact env var names used at runtime
- whether request context includes citations/tools/audit metadata already

---

## 7. Acceptance criteria

Accepted when:
- route is live
- Azure-backed response is proven
- provider SSOT is committed
- runtime doc is committed
- one evidence artifact confirms success
