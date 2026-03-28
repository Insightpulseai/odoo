# Changelog

> Dated entries for Odoo Copilot on Azure product documentation and capabilities.

## 2026-03-27

- **docs**: Created product documentation tree for Odoo Copilot on Azure
- **docs**: Added runtime overview (prompt-only vs hosted modes)
- **docs**: Added grounding and search architecture
- **docs**: Added action layer with guardrails and audit
- **docs**: Added operations guide (health, evals, tracing, rollout)
- **docs**: Added security and governance documentation
- **docs**: Added identity and access model (workforce/workload/agent)
- **docs**: Added authentication flow documentation (OIDC + MI + callback)
- **docs**: Added FAQ
- **arch**: Added runtime container contract (`docs/architecture/runtime-container-contract.md`)
- **arch**: Added addon taxonomy (`docs/architecture/addon-taxonomy.md`)
- **arch**: Added identity architecture (`docs/architecture/identity-architecture.md`)
- **ssot**: Added machine-readable runtime contract (`ssot/odoo/runtime_contract.yaml`)
- **runbook**: Added addon discovery debug runbook

## 2026-03-15

- **ssot**: Copilot benchmark scorecard V2 (`ssot/odoo/odoo_copilot_benchmark_v2.yaml`)
- **ssot**: Finance tool contract (`ssot/odoo/odoo_copilot_finance_tools.yaml`)
- **ssot**: Copilot provider configuration (`ssot/odoo/copilot-provider.yaml`)

## 2026-03-09

- **module**: `ipai_odoo_copilot` installed -- Odoo Copilot module with Azure AI Foundry backend
- **module**: `ipai_copilot_actions` installed -- Copilot action tools for Odoo operations
- **deprecated**: `ipai_ai_widget` replaced by native Odoo 19 Ask AI + `ipai_ai_copilot`
