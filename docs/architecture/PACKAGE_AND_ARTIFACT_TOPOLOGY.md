# Package and Artifact Topology

Canonical source:
- [`platform/ssot/org/package-and-artifact-topology.yaml`](../../platform/ssot/org/package-and-artifact-topology.yaml)

## Purpose

Define how GitHub Packages and GHCR are used across the InsightPulseAI operating org.

## Rules

- GitHub Packages is an internal package/artifact distribution layer.
- GHCR is the default registry for deployable container images.
- Public domains are application surfaces, not package endpoints.
- Azure runtime is the default deployment target for web/application surfaces.
- Shared packages should be reused across app surfaces where practical.

## Current domain mapping

- `www.insightpulseai.com` → flagship public site
- `www.w9studio.net` → business unit public site
- `prismalab.insightpulseai.com` → domain application

## Default package scope

- `@insightpulse-ai/*`

## Default image naming

- `ghcr.io/insightpulse-ai/<artifact-name>`

## Related

- [Clean chain](../../platform/ssot/architecture/github-azure-chain.yaml) — needs update to reflect GHCR shift (see migration_note in the topology SSOT)
- [App surface topology](../../platform/ssot/org/app-surface-and-mcp-topology.yaml)
- [Resource inventory](../../platform/ssot/azure/resource-inventory.dev.yaml)
- [GitHub integration model](../../ssot/governance/github-integration-model.yaml)
