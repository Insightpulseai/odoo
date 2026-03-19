# Org Doc Platform Deployment

> Deployment contract for the org-wide documentation knowledge base service.
> Runtime: Azure Container Apps. Image registry: Azure Container Registry.

---

## Container Image

**Dockerfile**: `apps/org-docs-kb/Dockerfile`
**Base**: `python:3.12-slim`
**Port**: 8000 (uvicorn/FastAPI)

```bash
# Local build
cd apps/org-docs-kb
docker build -t org-docs-kb:local .

# Local run
docker run -p 8000:8000 \
  -e AZURE_SEARCH_SERVICE_NAME=<value> \
  -e AZURE_SEARCH_INDEX_NAME=org-docs \
  -e AZURE_SEARCH_API_KEY=<value> \
  -e AZURE_OPENAI_ENDPOINT=<value> \
  -e AZURE_OPENAI_API_KEY=<value> \
  -e AZURE_OPENAI_DEPLOYMENT=text-embedding-ada-002 \
  org-docs-kb:local
```

---

## ACR Publish

**Registry**: `cripaidev.azurecr.io`
**Image**: `cripaidev.azurecr.io/org-docs-kb`
**Pipeline**: `.github/workflows/publish-agent-services.yml`

The publish pipeline builds and pushes the image on merge to `main` when files in `apps/org-docs-kb/` change. Image is tagged with:
- `latest`
- Git SHA (`sha-<short>`)
- Date tag (`YYYYMMDD`)

---

## ACA Deployment

**Container App**: `ipai-org-docs-kb`
**Environment**: `cae-ipai-dev`
**Resource Group**: `rg-ipai-dev`
**Region**: `southeastasia`

```bash
# Deploy or update container app
az containerapp update \
  --name ipai-org-docs-kb \
  --resource-group rg-ipai-dev \
  --image cripaidev.azurecr.io/org-docs-kb:latest

# Create container app (first time)
az containerapp create \
  --name ipai-org-docs-kb \
  --resource-group rg-ipai-dev \
  --environment cae-ipai-dev \
  --image cripaidev.azurecr.io/org-docs-kb:latest \
  --target-port 8000 \
  --ingress external \
  --min-replicas 0 \
  --max-replicas 2 \
  --cpu 0.5 \
  --memory 1.0Gi
```

---

## Required Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `AZURE_SEARCH_SERVICE_NAME` | (required) | Azure AI Search service name |
| `AZURE_SEARCH_INDEX_NAME` | `org-docs` | Search index name |
| `AZURE_SEARCH_API_KEY` | (required) | Azure AI Search admin/query key |
| `AZURE_OPENAI_ENDPOINT` | (required) | Azure OpenAI endpoint URL |
| `AZURE_OPENAI_API_KEY` | (required) | Azure OpenAI API key |
| `AZURE_OPENAI_DEPLOYMENT` | `text-embedding-ada-002` | Embedding model deployment name |
| `LOG_LEVEL` | `INFO` | Python logging level |
| `PORT` | `8000` | Server port |

All secrets sourced from Azure Key Vault (`kv-ipai-dev`) via managed identity.

---

## Health Check

**Endpoint**: `GET /health`
**Expected response**: HTTP 200

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "index_name": "org-docs",
  "uptime_seconds": 3600
}
```

ACA health probe configuration:
```yaml
probes:
  - type: liveness
    httpGet:
      path: /health
      port: 8000
    initialDelaySeconds: 10
    periodSeconds: 30
  - type: readiness
    httpGet:
      path: /health
      port: 8000
    initialDelaySeconds: 5
    periodSeconds: 10
```

---

## Refresh Workflow

**Workflow**: `.github/workflows/org-docs-refresh.yml`
**Schedule**: Weekly, Monday 07:00 UTC
**Trigger**: Also available via `workflow_dispatch` for manual runs

The refresh workflow:
1. Checks out the repo
2. Runs the document loader to scan for new/changed docs
3. Generates embeddings via Azure OpenAI
4. Upserts documents into the Azure AI Search index
5. Reports refresh stats (added, updated, unchanged, errors)

---

## Rollback

To roll back to a previous version:

```bash
# List available revisions
az containerapp revision list \
  --name ipai-org-docs-kb \
  --resource-group rg-ipai-dev \
  --output table

# Activate a previous revision
az containerapp revision activate \
  --name ipai-org-docs-kb \
  --resource-group rg-ipai-dev \
  --revision <revision-name>

# Route 100% traffic to previous revision
az containerapp ingress traffic set \
  --name ipai-org-docs-kb \
  --resource-group rg-ipai-dev \
  --revision-weight <revision-name>=100
```

---

## Monitoring

- **Health**: ACA built-in health probes
- **Logs**: `az containerapp logs show --name ipai-org-docs-kb --resource-group rg-ipai-dev`
- **Metrics**: Azure Monitor (request count, latency, error rate)
- **Alerts**: Configure in Azure Monitor for consecutive health check failures

---

*Created: 2026-03-15*
*Owner: Platform Engineering*
