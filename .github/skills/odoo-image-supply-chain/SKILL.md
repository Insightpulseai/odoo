# odoo-image-supply-chain

**Impact tier**: P1 -- Operational Readiness

## Purpose

Close the container image supply-chain gap. The benchmark audit found: no ACR
build pipeline, no vulnerability scanning on container images, no image signing,
and no provenance trail from Dockerfile to deployed image. The Odoo container
image is built locally or ad-hoc and pushed to ACR without automated gates.

## When to Use

- Setting up automated container image builds for Odoo.
- Adding vulnerability scanning to the container pipeline.
- Implementing image signing for supply-chain integrity.
- Preparing for a security review of the deployment pipeline.

## Required Evidence (inspect these repo paths first)

| Path | What to look for |
|------|-----------------|
| `infra/azure/main.bicep` | ACR resource definition |
| `infra/ssot/azure/resources.yaml` | ACR entries (`cripaidev`, `ipaiodoodevacr`) |
| `infra/ssot/azure/service-matrix.yaml` | Odoo service -- image reference |
| `docs/runbooks/ODOO18_GO_LIVE_CHECKLIST.md` | Image build/scan line items |
| `docs/audits/ODOO_AZURE_ENTERPRISE_BENCHMARK.md` | Supply chain gap row |
| Docker files in repo root or `docker/` | Dockerfile(s) for Odoo image |

## Microsoft Learn MCP Usage

Run at least these three queries:

1. `microsoft_docs_search("Azure Container Registry ACR Tasks automated build")`
   -- retrieves ACR Tasks for automated image builds on git push.
2. `microsoft_docs_search("Azure Container Registry vulnerability scanning Defender")`
   -- retrieves Microsoft Defender for Containers image scanning.
3. `microsoft_docs_search("Azure Container Registry image signing notation")`
   -- retrieves Notation (CNCF) image signing with ACR.

Optional:

4. `microsoft_code_sample_search("ACR task build push yaml", language="yaml")`
5. `microsoft_docs_fetch("https://learn.microsoft.com/en-us/azure/container-registry/container-registry-tutorial-build-task")`

## Workflow

1. **Inspect repo** -- Locate all Dockerfiles. Check ACR Bicep definitions.
   Determine current build process (manual `docker build` + `az acr login` +
   `docker push`, or ACR Tasks, or CI pipeline).
2. **Query MCP** -- Run the three searches. Capture ACR Tasks YAML syntax,
   Defender scanning enablement, Notation signing workflow.
3. **Compare** -- Identify: (a) Is there an automated build trigger? (b) Is
   scanning enabled on ACR? (c) Is image signing in place? (d) Is there a
   provenance record linking git SHA to image tag?
4. **Patch** -- Create or update:
   - ACR Task definition (YAML or Bicep) that builds on push to `main`.
   - Enable Defender for Containers on the ACR (Bicep property or CLI).
   - Add image tag convention: `<acr>.azurecr.io/odoo:19.0-<git-sha-short>`.
   - Document the build-scan-sign-deploy pipeline in a runbook.
5. **Verify** -- ACR Task definition is syntactically valid. Defender scanning
   property is set. Image tag convention is documented. Runbook exists.

## Outputs

| File | Change |
|------|--------|
| `infra/azure/modules/acr.bicep` | ACR with Defender scanning enabled |
| `infra/azure/acr-task.yaml` | ACR Task for automated builds (new) |
| `docs/runbooks/ODOO_IMAGE_BUILD_PIPELINE.md` | Build-scan-deploy procedure (new) |
| `docs/runbooks/ODOO18_GO_LIVE_CHECKLIST.md` | Image supply chain line items |
| `infra/ssot/azure/resources.yaml` | ACR entries updated with scanning metadata |
| `docs/evidence/<stamp>/odoo-image-supply-chain/` | ACR Task def, MCP excerpts |

## Completion Criteria

- [ ] ACR Task or CI pipeline exists that builds Odoo image on push to `main`.
- [ ] Image tags include the git SHA (e.g., `19.0-abc1234`).
- [ ] Defender for Containers is enabled on at least one ACR.
- [ ] A runbook documents the full build-scan-deploy pipeline.
- [ ] Go-live checklist includes image scanning verification.
- [ ] Evidence directory contains the ACR Task definition and MCP excerpts.
