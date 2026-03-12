# PRD — Odoo Copilot on Azure Foundry

## 1. Problem

The platform needs a controlled AI copilot capability inside Odoo that:

- uses Azure Foundry as the model runtime
- keeps Odoo as the configuration and policy boundary
- avoids uncontrolled agent writes
- provides knowledge-grounded responses with citations
- supports multiple logical interaction modes from one physical agent

Without this, AI copilot features either bypass Odoo governance or require
standalone agent apps that drift from the ERP control plane.

---

## 2. Goal

Implement a thin Odoo addon (`ipai_odoo_copilot`) that configures and manages
one physical Azure Foundry agent, with Odoo as the admin/policy/audit surface.

---

## 3. Users

### Primary
- Odoo administrator configuring copilot behavior
- Odoo users interacting with copilot (via Foundry-backed surfaces)

### Secondary
- platform operator monitoring copilot health
- evaluator running Foundry evaluation suites

---

## 4. User stories

- As an admin, I want to configure the Foundry copilot endpoint, project, agent name, and model from Odoo Settings.
- As an admin, I want to test the Foundry connection without leaving Odoo.
- As an admin, I want to enable/disable memory and set read-only/draft-only mode.
- As an operator, I want bounded sync actions that log intent without uncontrolled resource creation.
- As a user, I want copilot responses grounded in knowledge with citations.

---

## 5. Functional requirements

### FR-1 Settings UI
A `res.config.settings` section for Azure Foundry Copilot configuration.

### FR-2 Persistent config
Non-secret settings stored in `ir.config_parameter`.

### FR-3 Connection test
`action_test_foundry_connection` validates config shape and reports status.

### FR-4 Agent ensure (bounded stub)
`action_ensure_foundry_agent` is a controlled sync stub that logs intent.

### FR-5 Portal link
`action_open_foundry_portal` opens Azure Foundry portal for the configured project.

### FR-6 Backend sync action
One `ir.actions.server` for bounded backend sync operations.

### FR-7 Optional healthcheck cron
Daily cron to validate Foundry config health (optional for v1).

---

## 6. Non-functional requirements

### NFR-1 No secrets in DB
Azure credentials resolved via env vars / managed identity only.

### NFR-2 Memory off by default
Foundry memory must default to disabled.

### NFR-3 Read-only posture
v1 operates in read-first / draft-first mode.

### NFR-4 Thin addon
Minimal dependencies; OCA modules are not hard manifest dependencies unless technically required.

### NFR-5 Odoo 19 compatible
Use `<list>` (not `<tree>`), current API conventions.

---

## 7. Acceptance criteria

- Odoo addon installs without error
- Settings UI renders and persists config
- Connection test action works
- Agent ensure action logs intent
- Portal link action opens correct URL
- Memory defaults to off
- Read-only/draft-only mode is configurable
- SSOT AI manifests are aligned
- No repo-root scaffold files created

---

## 8. Risks

- Azure Foundry SDK not available in Odoo runtime → mitigated by stub pattern
- Managed identity wiring incomplete → mitigated by env var fallback assumption
- Foundry API surface changes → mitigated by thin bounded service layer

---

## 9. Release slices

### Slice 1 — Config + SSOT
- Odoo addon with settings
- SSOT AI manifests
- Foundry instructions artifact

### Slice 2 — Bounded actions
- Connection test
- Agent ensure stub
- Portal link

### Slice 3 — Validation
- Foundry evaluations
- End-to-end grounded response
