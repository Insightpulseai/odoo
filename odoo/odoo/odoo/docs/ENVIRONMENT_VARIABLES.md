# Environment Variables — Canonical Reference

> SSOT: `ops-platform/.env.example` is the canonical superset.
> Subset files (`odoo/.env.example`, `agents/.env.example`) are strict subsets.

---

## Which variables belong to which system?

### Claude Code (sections 1 + 5)

These variables configure **Claude Code itself** when routed through Microsoft Foundry.
They have no effect on the Odoo application.

| Variable | Purpose |
|----------|---------|
| `CLAUDE_CODE_USE_FOUNDRY` | Enable Foundry integration (`1`) |
| `ANTHROPIC_FOUNDRY_RESOURCE` | Azure resource name (`data-intel-ph-resource`) |
| `ANTHROPIC_FOUNDRY_BASE_URL` | Full Anthropic base URL under the Foundry resource |
| `ANTHROPIC_FOUNDRY_API_KEY` | API key auth (leave blank for `az login`) |
| `ANTHROPIC_DEFAULT_OPUS_MODEL` | Pinned Opus deployment name |
| `ANTHROPIC_DEFAULT_SONNET_MODEL` | Pinned Sonnet deployment name |
| `ANTHROPIC_DEFAULT_HAIKU_MODEL` | Pinned Haiku deployment name |
| `HTTPS_PROXY` / `HTTP_PROXY` / `NO_PROXY` | Corporate proxy (leave blank if none) |
| `NODE_EXTRA_CA_CERTS` | Custom CA bundle path |
| `CLAUDE_CODE_CLIENT_CERT` / `_KEY` / `_PASSPHRASE` | mTLS client certificate |

**Auth options** — use one of:
- `ANTHROPIC_FOUNDRY_API_KEY` — explicit key from Azure portal
- `az login` — Azure CLI credential chain (no key needed)

### Odoo bridge / app (sections 2 + 3 + 4)

These variables configure the **Odoo addon / bridge service** that talks to Azure AI Foundry.
They have no effect on Claude Code.

| Variable | Purpose |
|----------|---------|
| `AZURE_AI_FOUNDRY_PROJECT_ENDPOINT` | Project-scoped endpoint (includes `/api/projects/`) |
| `AZURE_AI_FOUNDRY_ENDPOINT` | Parent resource endpoint |
| `AZURE_AI_FOUNDRY_AGENT_ID` / `_NAME` | Copilot agent identifier in Foundry |
| `AZURE_AI_FOUNDRY_API_KEY` | Resource API key |
| `AZURE_AI_FOUNDRY_PROJECT_NAME` | Project name (`data-intel-ph`) |
| `AZURE_AI_FOUNDRY_RESOURCE_NAME` | Resource name (`data-intel-ph-resource`) |
| `AZURE_AI_FOUNDRY_REGION` | Azure region (`eastus2`) |
| `AZURE_AI_FOUNDRY_CHAT_DEPLOYMENT` | Chat model deployment (`gpt-4.1`) |
| `AZURE_AI_FOUNDRY_EMBEDDING_DEPLOYMENT` | Embedding model deployment (`text-embedding-3-small`) |
| `AZURE_AI_FOUNDRY_AUTH_MODE` | Auth strategy for app code |
| `AZURE_AI_FOUNDRY_AUTH_AUDIENCE` | Azure SDK audience scope |
| `AZURE_AI_SEARCH_*` | Azure AI Search for knowledge grounding |
| `AZURE_APIM_*` | API Management (only if deployed) |

---

## Why are project endpoint and resource endpoint different?

Azure AI Foundry has two scopes:

- **Resource endpoint** (`https://<resource>.services.ai.azure.com/`)
  The parent container. Manages keys, deployments, and models.

- **Project endpoint** (`https://<resource>.services.ai.azure.com/api/projects/<project>`)
  A project-scoped surface within the resource. Agents, evaluations,
  and project-specific features are accessed here.

The Odoo bridge uses the **project endpoint** for agent operations (creating threads,
running agents) and the **resource endpoint** for model deployments (chat completions,
embeddings). Both share the same API key.

This is distinct from the Azure OpenAI endpoint (`https://<resource>.openai.azure.com/`),
which is a separate service surface and should **not** replace `AZURE_AI_FOUNDRY_PROJECT_ENDPOINT`.

---

## When should proxy fields remain empty?

Leave `HTTPS_PROXY`, `HTTP_PROXY`, `NO_PROXY`, `NODE_EXTRA_CA_CERTS`, and the
`CLAUDE_CODE_CLIENT_*` variables empty unless:

- You are behind a **corporate HTTP(S) proxy** that intercepts outbound traffic
- Your organization uses a **custom Certificate Authority** whose root cert
  is not in the system trust store
- Your environment requires **mTLS (mutual TLS)** client certificates

Claude Code supports standard HTTP(S) proxies and does **not** support SOCKS proxies.
If you are on a personal machine with direct internet access, none of these are needed.

---

## File ownership

| File | Contains | Sections |
|------|----------|----------|
| `ops-platform/.env.example` | Canonical superset | 1, 2, 3, 4, 5, 6 |
| `odoo/.env.example` | Odoo bridge subset + existing Odoo config | 2, 3, 4 |
| `agents/.env.example` | Claude Code / Foundry subset | 1, 5 |

All subset files are strict subsets of `ops-platform/.env.example`.
Variable names and default values must not conflict across files.
