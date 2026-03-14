# Constitution — ipai-odoo-copilot-azure

## Non-Negotiable Rules

1. **One physical Foundry agent**: `ipai-odoo-copilot-azure` in project `data-intel-ph` (East US 2). No second agent.
2. **Odoo is the policy boundary**: All configuration, access control, and audit happen in Odoo. Foundry executes.
3. **No secrets in Odoo DB**: Azure auth via environment variable (`AZURE_FOUNDRY_API_KEY`) or managed identity (`id-ipai-aca-dev`). Never `ir.config_parameter`.
4. **Read-first / draft-first posture**: The agent does not perform uncontrolled writes. All mutations surface as drafts for human approval.
5. **Memory off by default**: Foundry thread memory is disabled unless explicitly enabled by admin.
6. **Knowledge grounding preferred**: Use Azure AI Search for retrieval. Cite sources when retrieval is used. Never fabricate citations.
7. **CE + OCA first**: The addon depends only on `base`. OCA baseline modules (disable_odoo_online, remove_odoo_enterprise, mail_debrand, auditlog, password_security) are recommended but not hard dependencies.
8. **No uncontrolled resource creation**: `ensure_agent()` is a bounded stub in v1. It logs intent but does not create Azure resources.
9. **Evaluations required**: v1 acceptance requires Foundry evaluation runs demonstrating grounded, citation-backed responses.
10. **No repo-root scaffolding**: All code lives under `addons/ipai/ipai_odoo_copilot/`, spec under `spec/ipai-odoo-copilot-azure/`, SSOT under `ssot/ai/`.
