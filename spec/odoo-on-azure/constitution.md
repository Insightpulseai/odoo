# Constitution — Odoo on Azure: Best Practices Reference Platform

## Non-negotiable rules

1. **Benchmark is Azure best practices, not SAP.** The reference platform derives its
   control objectives from Azure Well-Architected, Foundry, Container Apps, and Pipelines
   guidance — never from SAP deployment topology or naming.

2. **Odoo is the transactional SoR.** The platform orchestrates around Odoo but never
   replaces its business logic or transactional authority.

3. **YAML is pipeline truth.** All delivery automation is repo-defined YAML. Azure DevOps
   pipeline state is a control surface, not the definition surface.

4. **Foundry is AI truth.** All AI/agent/grounding capabilities route through Microsoft
   Foundry. No parallel AI runtime.

5. **Managed controls over embedded credentials.** Entra ID, Key Vault, managed identities,
   and private endpoints are the default. Application-embedded credentials are not acceptable.

6. **Monitoring is not optional.** Runtime health, deployment events, AI telemetry, and
   quality checks are required production properties.

7. **Internal by default.** Services are private unless explicitly justified for public access.
