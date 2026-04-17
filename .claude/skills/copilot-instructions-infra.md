# Copilot instructions — IPAI infra repo

<!-- Copilot reads this file like Claude Code reads CLAUDE.md.
     Keep in sync with CLAUDE.md. -->

## Stack
- Azure Bicep, Azure SEA, Sub eba824fb
- Resource groups: `rg-ipai-*`
- ACA + PG Flex + Key Vault + ADLS + AI Foundry

## Commands
- Validate: `az deployment group validate ...`
- What-if: `az deployment group what-if ...`
- Lint: `az bicep lint --file infra/azure/stamp.bicep`

## Rules
- Every resource must embed `stampId` in its name
- Required tags: `Environment`, `StampId`, `Workload`, `CostCenter`, `ManagedBy`
- One PG Flex per stamp — never shared
- Key Vault: `enableSoftDelete: true`, `enablePurgeProtection: true`
- No `--mode Complete` — Incremental only
- No secrets in Bicep files — `@secure()` params from Key Vault only
- ACA ingress: direct binding — no AFD as primary ingress

## Forbidden
- `az deployment group create` (what-if only in dev)
- Portal changes
- Sharing PG servers across stamps
