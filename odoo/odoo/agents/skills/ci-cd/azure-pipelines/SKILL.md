# Skill: Azure Pipelines — CI/CD Reference

source: https://learn.microsoft.com/en-us/azure/devops/pipelines/
extracted: 2026-03-15
applies-to: .github, infra, automations, agents

## Decision: Azure Pipelines vs GitHub Actions
- IPAI primary CI/CD = GitHub Actions (already in `.github/`)
- Azure Pipelines = use ONLY for workloads needing Azure DevOps integration
  or existing ADO org pipelines
- Do NOT duplicate pipeline definitions across both systems

## Key concepts (for YAML authoring)
- Stages → Jobs → Steps (hierarchical)
- Environments: named targets with approval gates (dev → staging → prod)
- Service connections: how pipelines auth to Azure, ACR, AKS
- Variable groups: secret management (backed by Key Vault)
- Templates: reusable YAML fragments (equivalent to GHA reusable workflows)
- Agents: Microsoft-hosted (`ubuntu-latest`) or self-hosted

## IPAI-specific patterns

### ACA deploy stage (maps to `infra/` Bicep)
- Trigger: PR merge to main
- Stages: build → push ACR → deploy ACA revision → smoke test → promote
- Environment gates: manual approval before prod

### Secrets pattern (SSOT-compliant)
- Variable groups backed by Azure Key Vault
- Never commit secrets; reference `$(MY_SECRET)` syntax
- Key Vault = secrets plane; Supabase Vault = app secrets SSOT

### Self-hosted agent (if needed)
- Deploy as ACA job in `rg-ipai-dev`
- Runs in SEA region, same VNet as `ipai-odoo-dev-pg`
- Use for workloads needing private network access to Odoo/Supabase

## Determinism principle
- CI/CD pipelines are deterministic — agents call them, not the reverse
- Pipeline NEVER makes agentic decisions (no LLM in deploy path)
- Agents produce artifacts → pipeline deploys them predictably
