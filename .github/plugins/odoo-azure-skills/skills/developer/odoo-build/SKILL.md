---
name: odoo-build
category: developer
scope: odoo-on-azure
authority: docs/architecture/ODOO_SH_EQUIVALENCE_MATRIX.md
odoo_sh_equivalent: "GitHub Integration — every commit/PR/merge triggers build"
---

# odoo-build — Build Odoo Docker Image + Push to ACR

## When to use

Use this skill when:
- Code changes land in `addons/ipai/**`, `addons/oca/**`, `docker/Dockerfile.unified`, `config/**`
- A new module is added or updated
- Python dependencies change (`requirements.txt`)
- You need to deploy a new revision to any environment

## Decision workflow

```
1. Is this a code change to Odoo addons, config, or Dockerfile?
   YES → proceed to build
   NO  → this skill does not apply

2. Which Dockerfile?
   ALWAYS: docker/Dockerfile.unified
   NEVER:  docker/Dockerfile.prod (legacy, superseded)

3. Image naming (per infra/ssot/odoo/image-naming-policy.yaml):
   Registry: acripaiodoo.azurecr.io
   Image:    ipai-odoo
   Tags:     18.0-<BuildId>, sha-<gitsha>, 18.0 (rolling)
   NEVER:    environment in tag, role in tag, "latest" alone

4. Build method:
   CI:    Azure Pipelines (infra/ci/azure-pipelines-odoo-deploy.yml)
   Local: az acr build --registry acripaiodoo --image ipai-odoo:18.0-local --file docker/Dockerfile.unified .
   NEVER: docker build + docker push from laptop

5. After build:
   → CVE scan with Docker Scout (critical+high = block)
   → Push to ACR with immutable tag
   → Pipeline continues to test stage
```

## Guardrails

- Do NOT build from `Dockerfile.prod` — superseded by `Dockerfile.unified`
- Do NOT encode environment (dev/staging/prod) in the image tag
- Do NOT skip the CVE scan
- Do NOT push images from local Docker — use ACR Tasks or Azure Pipelines
- Do NOT modify upstream Odoo source in the image — use addon overrides
- Do NOT use `latest` as the only production tag

## Tools

- `az acr build` (Azure MCP)
- `docker scout cves` (Docker Scout CLI)
- Azure Pipelines `Docker@2` task

## Related

- `odoo-ci` — full CI validation
- `odoo-addons` — addon path management
- `judge-deploy-readiness` — validates build is deployable
