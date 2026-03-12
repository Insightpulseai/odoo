# Odoo Copilot on Azure Foundry — Constitution

## 1. Purpose

Define the governance contract for the Odoo Copilot configuration layer
that manages one physical Azure Foundry agent (`ipai-odoo-copilot-azure`)
from within the Odoo control plane.

Odoo owns configuration, policy, and audit boundaries.
Azure Foundry owns model runtime, instructions execution, knowledge/retrieval,
traces, monitoring, and evaluation surfaces.

---

## 2. Scope

In scope:

- one physical Azure Foundry agent in project `data-intel-ph`
- four logical agent modes: Ask, Authoring, Livechat, Transaction
- Odoo-side admin configuration and policy enforcement
- SSOT AI manifests for agents, models, topics, tools, policies, sources, prompts
- bounded sync/test actions from Odoo to Foundry
- Foundry instruction artifact tracked in repo

Out of scope:

- multi-provider routing
- non-Odoo chat surfaces for v1
- deep Foundry SDK integration (stubbed for v1)
- autonomous agent writes (v1 is read-first / draft-first)

---

## 3. Architecture

```
Browser → erp.insightpulseai.com → Odoo (config/policy/audit)
                                        ↓
                              Azure Foundry Runtime
                              ├── Agent: ipai-odoo-copilot-azure
                              ├── Model: gpt-4.1
                              ├── Knowledge: Azure Search index
                              └── Memory: disabled by default
```

One physical Foundry agent. Logical behavior (Ask, Authoring, Livechat,
Transaction) is modeled via instructions and topic routing, not separate
Foundry deployments.

---

## 4. Ownership boundaries

### Odoo

- admin configuration UI
- policy boundary (read-only/draft-only posture, memory toggle)
- audit boundary (sync intent logging, action tracking)
- bounded sync/test actions (connection test, agent ensure stub)

### Azure Foundry

- model runtime (gpt-4.1 deployment)
- instructions execution
- knowledge grounding (Azure Search)
- traces / monitor / evaluation surfaces
- memory runtime (when enabled)

---

## 5. Non-negotiable rules

1. **One physical agent.** Never create multiple Foundry agent deployments for logical modes.
2. **Memory off by default.** Foundry memory must be explicitly enabled via Odoo config.
3. **Read-first / draft-first.** No uncontrolled writes in v1.
4. **No secrets in repo.** Azure credentials use managed identity or env vars from Key Vault.
5. **OCA-first.** Use OCA modules as baseline; `ipai_*` addons are thin glue only.
6. **Odoo is control plane.** Foundry runtime config is authoritative only when synced from Odoo-managed policy.
7. **Evaluations required.** v1 acceptance requires Foundry evaluation runs.
8. **Citations required.** Retrieval-backed responses must include source citations.
9. **Bounded tools only.** If tools are present in v1, they must be tightly scoped and read-only.
10. **No fabricated completions.** Agent must ground responses or clearly state uncertainty.

---

## 6. OCA baseline assumptions

The following OCA modules form the assumed operational baseline:

- `disable_odoo_online`
- `remove_odoo_enterprise`
- `mail_debrand`
- `auditlog`
- `password_security`
- `queue_job`

Recommended UX/admin baseline:

- `base_name_search_improved`
- `web_environment_ribbon`
- `web_responsive`

---

## 7. Success doctrine

This work succeeds when:

- Odoo admin can configure the Foundry copilot from Settings
- connection test validates config shape
- agent ensure action is a bounded sync stub
- memory defaults to off
- read-only/draft-only posture is explicit in both Odoo config and Foundry instructions
- SSOT AI manifests are coherent and cross-validated
- no repo-root scaffolding is introduced
