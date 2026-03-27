# Cloud Integration Status — Agent Platform

> Scanned: 2026-03-19
> Purpose: Document Azure AI resource availability for Odoo Copilot precursor

---

## Azure AI Foundry / Cognitive Services

| Field | Value |
|-------|-------|
| Resource name | `data-intel-ph-resource` |
| Resource group | `rg-data-intel-ph` |
| Kind | AIServices |
| SKU | S0 |
| Location | East US 2 |
| Endpoint | `https://data-intel-ph-resource.cognitiveservices.azure.com/` |

### Model Deployments

| Deployment | Status |
|-----------|--------|
| `gpt-4.1` | Deployed |
| `text-embedding-3-small` | Deployed |

### Required Env Vars for agent-platform

```
AZURE_AI_FOUNDRY_ENDPOINT=https://data-intel-ph-resource.cognitiveservices.azure.com/
MODEL_DEPLOYMENT_NAME=gpt-4.1
EMBEDDING_DEPLOYMENT_NAME=text-embedding-3-small
```

### Note on naming

The infrastructure rules reference `aifoundry-ipai-dev` and `oai-ipai-dev` as Foundry/OpenAI resources. The actual discovered resource is `data-intel-ph-resource` in `rg-data-intel-ph`. This may be a newer provisioning or a different project. The infrastructure SSOT should be updated to reflect the actual resource name.

---

## Azure AI Search

**Status: PROVISIONED AND SEEDED**

| Field | Value |
|-------|-------|
| Resource name | `srch-ipai-dev` |
| Resource group | `rg-ipai-ai-dev` |
| SKU | Basic |
| Location | Southeast Asia |
| Endpoint | `https://srch-ipai-dev.search.windows.net` |
| Index name | `ipai-knowledge-base` |
| Documents indexed | 331 chunks from 19 files |
| Seeded | 2026-03-19 |

### Knowledge base content indexed

19 markdown files from `agents/knowledge-base/` across 8 categories:
- anthropic-engineering (1 file)
- bir-compliance (4 files)
- finance-close-kb (3 files)
- general-kb (4 files)
- industry-reports (1 file)
- marketing-playbooks (2 files)
- ops-kb (2 files)
- sdlc (2 files)

### Index schema

Defined in `agents/knowledge-base/index-schema.json`. Fields: `id`, `title`, `content`, `kb_scope`, `group_ids`, `source_file`, `chunk_index`, `last_updated`.

### Re-seeding

To re-seed after adding new knowledge base files:

```bash
python3 agents/knowledge-base/seed_search_index.py
```

### Admin key

Stored in Azure Key Vault `ipai-odoo-dev-kv` as secret `search-admin-key`. To refresh:

```bash
az keyvault secret set --vault-name ipai-odoo-dev-kv --name search-admin-key \
  --value "$(az search admin-key show --service-name srch-ipai-dev --resource-group rg-ipai-ai-dev --query primaryKey -o tsv)"
```

---

## Summary

| Capability | Status | Blocker |
|-----------|--------|---------|
| Foundry endpoint | **Available** | None — resource exists with gpt-4.1 deployed |
| Model inference | **Available** | Set env vars on agent-platform |
| Embeddings | **Available** | text-embedding-3-small deployed |
| AI Search | **Provisioned + seeded** | None — 331 chunks indexed from 19 files |
| Grounded retrieval | **Available** | Connect agent-platform to search endpoint |
| App Insights | **Not checked** | Separate investigation needed |

---

## Next steps

1. Set `AZURE_AI_FOUNDRY_ENDPOINT` on agent-platform to connect real inference
2. ~~Provision AI Search service~~ **Done** (2026-03-19)
3. ~~Seed knowledge index from `agents/knowledge-base/`~~ **Done** (331 chunks, 2026-03-19)
4. Save search admin key to Key Vault: `az keyvault secret set --vault-name ipai-odoo-dev-kv --name search-admin-key --value "$(az search admin-key show --service-name srch-ipai-dev --resource-group rg-ipai-ai-dev --query primaryKey -o tsv)"`
5. Connect App Insights for production tracing

---

*Scanned: 2026-03-19 | AI Search seeded: 2026-03-19*
