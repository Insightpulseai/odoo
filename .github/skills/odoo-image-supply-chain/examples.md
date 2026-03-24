# odoo-image-supply-chain -- Worked Examples

## Example 1: ACR with Defender Scanning (Bicep)

```bicep
resource acr 'Microsoft.ContainerRegistry/registries@2023-11-01-preview' = {
  name: 'ipaiodoodevacr'
  location: location
  sku: { name: 'Standard' }
  properties: {
    adminUserEnabled: false
    policies: {
      quarantinePolicy: { status: 'enabled' }
    }
  }
}

// Defender for Containers scanning is enabled at the subscription level
// via Microsoft Defender for Cloud, not per-ACR.
// Verify: az security pricing show --name Containers
```

## Example 2: ACR Task Definition (YAML)

```yaml
# infra/azure/acr-task.yaml
# Create with: az acr task create --registry ipaiodoodevacr --name build-odoo \
#   --file infra/azure/acr-task.yaml --context https://github.com/Insightpulseai/odoo.git#main
version: v1.1.0
steps:
  - build: >-
      -t {{.Run.Registry}}/odoo:19.0-{{.Run.ID}}
      -t {{.Run.Registry}}/odoo:latest
      -f docker/Dockerfile.unified
      .
  - push:
      - "{{.Run.Registry}}/odoo:19.0-{{.Run.ID}}"
      - "{{.Run.Registry}}/odoo:latest"
trigger:
  sourceTrigger:
    name: defaultSourceTrigger
    sourceRepository:
      repositoryUrl: "https://github.com/Insightpulseai/odoo.git"
      branch: main
      sourceControlType: Github
    sourceTriggerEvents:
      - commit
```

## Example 3: Image Tag Convention

```
Registry:   ipaiodoodevacr.azurecr.io
Repository: odoo
Tag format: 19.0-<7-char-git-sha>
Example:    ipaiodoodevacr.azurecr.io/odoo:19.0-abc1234

Mutable tag: latest (always points to most recent main build)
Immutable:   19.0-<sha> tags are never overwritten
```

## Example 4: MCP Query Sequence

```
Step 1: microsoft_docs_search("Azure Container Registry ACR Tasks automated build")
Result: ACR Tasks support multi-step builds triggered by git commit, base
        image update, or schedule. Define steps in YAML. Supports Dockerfile
        builds natively. Runs in Azure, no local Docker daemon needed.

Step 2: microsoft_docs_search("Azure Container Registry vulnerability scanning Defender")
Result: Microsoft Defender for Containers provides:
        - Push-time scanning (scan on push to ACR)
        - Continuous scanning (re-scan running images for new CVEs)
        - Findings in Defender for Cloud portal and ARG
        Enable at subscription level, not per-registry.

Step 3: microsoft_docs_search("Azure Container Registry image signing notation")
Result: Notation (CNCF project) signs OCI artifacts stored in ACR.
        Requires: notation CLI, AKV signing key, ACR with OCI 1.1 support.
        Verification at deploy time via policy (Gatekeeper/Ratify on AKS,
        or custom validation for ACA).
```

## Example 5: Build Pipeline Runbook Skeleton

```markdown
## Odoo Container Image Build Pipeline

### Trigger
- Automatic: push to `main` branch triggers ACR Task.
- Manual: `az acr task run --registry ipaiodoodevacr --name build-odoo`

### Build
1. ACR Task pulls source from GitHub.
2. Builds from `docker/Dockerfile.unified`.
3. Tags: `19.0-<run-id>` (immutable) + `latest` (mutable).

### Scan
1. Defender for Containers scans image on push.
2. Check results: `az security sub-assessment list --assessed-resource-id <acr-id>`
3. Gate: no Critical vulnerabilities. High vulnerabilities documented with timeline.

### Deploy
1. Update ACA revision with new image tag:
   `az containerapp update --name ipai-odoo-dev-web --image ipaiodoodevacr.azurecr.io/odoo:19.0-<sha>`
2. Verify health: `curl -sf https://erp.insightpulseai.com/web/health`

### Rollback
1. Set previous tag: `az containerapp update --name ipai-odoo-dev-web --image ipaiodoodevacr.azurecr.io/odoo:19.0-<prev-sha>`
```
