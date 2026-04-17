# Runbook — Claude Code on Microsoft Foundry

> Operate Claude Code (CLI + Agent SDK) against the IPAI canonical Microsoft Foundry resource.
> Authoritative doctrine anchor: `CLAUDE.md` §"Cross-Repo Invariants" + `feedback_foundry_reuse_doctrine`.

---

## 0. Scope

Applies to:
- Claude Code CLI (`claude`)
- Claude Agent SDK (Python + TypeScript)
- Any ACA/Azure Pipelines workload that invokes Claude via the Anthropic SDK

Does NOT apply to:
- Pulser custom-engine runtime (separate plane — uses Foundry Agents, not Claude Code)
- Agents authored inside Foundry UI (use Azure AI Projects SDK 2.x directly)

---

## 1. Canonical Foundry Resource

| Field | Value |
|---|---|
| Resource name | `ipai-copilot-resource` |
| Resource kind | Microsoft Foundry (AIServices) |
| Region | East US 2 |
| Subscription | `Microsoft Azure Sponsorship` |
| Resource group | `rg-data-intel-ph` |
| Project | `ipai-copilot` |

**Rule:** reuse this resource. Do NOT spin up a parallel Anthropic-only Foundry. See `feedback_foundry_reuse_doctrine`.

New Foundry resources are allowed ONLY for product-isolated lanes (data-intel, market-intel, tenant-isolated), never for a duplicate Claude Code path.

---

## 1.1. Three-endpoint runtime map (ONE resource, THREE base URLs)

The single Foundry resource exposes three distinct runtime endpoints. **Use the correct one per SDK.** SSOT: `ssot/foundry/runtime-contract.yaml`.

| Runtime | Base URL | Use for |
|---|---|---|
| **Anthropic Foundry** | `https://ipai-copilot-resource.services.ai.azure.com/anthropic` | Claude Code CLI, Claude Agent SDK, anything speaking the Anthropic Messages API |
| **Foundry Projects** | `https://ipai-copilot-resource.services.ai.azure.com/api/projects/ipai-copilot` | Azure AI Projects SDK 2.x (`AIProjectClient`), Microsoft Agent Framework, Foundry-native agents/evaluations/tracing |
| **Azure OpenAI** | `https://ipai-copilot-resource.openai.azure.com/openai/v1` | OpenAI SDK clients targeting the OpenAI-compatible surface (GPT-4.1, embeddings, DALL-E) |

**Rules:**
- Do NOT point the OpenAI SDK at the Anthropic base or vice versa — each base is a separate shim and will reject cross-protocol traffic.
- Claude Code in Foundry mode derives the Anthropic base from `ANTHROPIC_FOUNDRY_RESOURCE` automatically. Set `ANTHROPIC_FOUNDRY_BASE_URL` only if you need to override (e.g., regional endpoint test).
- The project endpoint is the surface for `agents.create_version`, `responses.create` with `agent_reference`, and evaluations — this is where Foundry-native agent code lives.
- All three bases accept the same `DefaultAzureCredential` bearer token on the `cognitiveservices.azure.com` scope — auth is shared; protocol is not.

---

## 2. Canonical Environment Contract

Minimum required to activate Foundry mode:

```bash
export CLAUDE_CODE_USE_FOUNDRY=1
export ANTHROPIC_FOUNDRY_RESOURCE=ipai-copilot-resource
export ANTHROPIC_DEFAULT_OPUS_MODEL='<pinned-opus-deployment>'
export ANTHROPIC_DEFAULT_SONNET_MODEL='<pinned-sonnet-deployment>'
export ANTHROPIC_DEFAULT_HAIKU_MODEL='<pinned-haiku-deployment>'
```

Optional — explicit URL form (mutually exclusive with `ANTHROPIC_FOUNDRY_RESOURCE`):

```bash
export ANTHROPIC_FOUNDRY_BASE_URL=https://ipai-copilot-resource.services.ai.azure.com/anthropic
```

Optional — API key fallback / bootstrap only (NOT the default auth):

```bash
export ANTHROPIC_FOUNDRY_API_KEY=<key-from-kv-ipai-dev>
```

**Rules:**
1. `CLAUDE_CODE_USE_FOUNDRY=1` is the hard toggle. Without it, Claude Code ignores every other Foundry variable.
2. Never commit `ANTHROPIC_FOUNDRY_API_KEY` to git. Resolve at runtime from Azure Key Vault (`kv-ipai-dev`).
3. Pinned deployment names are mandatory (see §4).

---

## 3. Preferred Auth Path — Managed Identity / Entra First

Order of preference:

1. **Managed identity (ACA, Azure Pipelines agent)** — default, no secret material
2. **Entra user credential (developer workstation)** — via `az login` + `DefaultAzureCredential`
3. **Service principal + federated credential** — for GitHub-hosted CI bridges
4. **`ANTHROPIC_FOUNDRY_API_KEY`** — fallback only; document the reason when used

When `ANTHROPIC_FOUNDRY_API_KEY` is unset, Claude Code resolves auth through `DefaultAzureCredential` automatically. `/login` and `/logout` are disabled in Foundry mode — attempts to use them are no-ops.

**Forbidden:**
- OpenAI/Anthropic console API keys routed through Claude Code (use Foundry path or nothing)
- Hardcoded client secrets
- Long-lived service principal passwords for CI

---

## 4. Pinned Model Deployments

**Rule:** every Claude Code invocation against Foundry MUST use a pinned deployment name. Floating aliases (`claude-opus-latest`, etc.) are banned.

Naming convention for deployments on `ipai-copilot-resource`:

```
<base-model>-<release-date-yyyymmdd>
```

Examples:

| Env var | Deployment name pattern | Purpose |
|---|---|---|
| `ANTHROPIC_DEFAULT_OPUS_MODEL` | `claude-opus-4-6-20260401` | Architecture, SSOT, complex planning |
| `ANTHROPIC_DEFAULT_SONNET_MODEL` | `claude-sonnet-4-6-20260401` | Default subagent model |
| `ANTHROPIC_DEFAULT_HAIKU_MODEL` | `claude-haiku-4-5-20260401` | Log parsing, grep-and-summarize |

Cut-over protocol when Anthropic releases a new version:
1. Deploy new version on Foundry with fresh date suffix
2. Smoke-test against a disposable agent
3. Update the env var in the canonical contract file (`ssot/foundry/claude-code-deployments.yaml`)
4. Roll ACA container revisions; leave old deployment live for 7 days for rollback
5. Tombstone the old deployment on day 8

---

## 5. RBAC Requirements

Default roles sufficient for Claude Code on Foundry:

| Principal | Role | Scope |
|---|---|---|
| Developer (Entra user) | **Azure AI User** | `ipai-copilot-resource` |
| ACA managed identity | **Azure AI User** | `ipai-copilot-resource` |
| Azure Pipelines service connection | **Azure AI User** | `ipai-copilot-resource` |
| Read-only auditor | **Cognitive Services User** | `ipai-copilot-resource` |

No custom role needed unless narrowing further. Do NOT grant `Cognitive Services Contributor` to runtime principals — that permits deployment mutation.

Grant example (one-liner for a new ACA app managed identity):

```bash
az role assignment create \
  --assignee-object-id "$(az containerapp identity show -n <app> -g <rg> --query principalId -o tsv)" \
  --assignee-principal-type ServicePrincipal \
  --role "Azure AI User" \
  --scope "$(az cognitiveservices account show -n ipai-copilot-resource -g rg-data-intel-ph --query id -o tsv)"
```

---

## 6. Deployment Naming Convention Summary

| Artifact | Pattern | Example |
|---|---|---|
| Foundry resource | `<org>-<product>-resource` | `ipai-copilot-resource` |
| Foundry project | `<org>-<product>` | `ipai-copilot` |
| Model deployment | `<base>-<yyyymmdd>` | `claude-opus-4-6-20260401` |
| Env var (Opus default) | `ANTHROPIC_DEFAULT_OPUS_MODEL` | — |
| KV secret (api key fallback) | `anthropic-foundry-api-key` | — |

---

## 7. Troubleshooting

### 7.1 `ChainedTokenCredential authentication failed`

**Symptoms:** Claude Code exits immediately after first request; stderr shows the error above.

**Causes (in descending likelihood):**
1. `az login` session expired on developer workstation → run `az login --tenant <ipai-tenant-id>`
2. ACA managed identity not assigned to the Foundry resource → check §5 role assignment
3. Azure Pipelines service connection missing federated credential → re-authorize the connection
4. `AZURE_TENANT_ID` / `AZURE_CLIENT_ID` env vars set to stale values → `unset` and retry

**Verification:**

```bash
az account get-access-token \
  --resource https://cognitiveservices.azure.com \
  --query expiresOn -o tsv
```

If that succeeds, `DefaultAzureCredential` will also succeed.

### 7.2 `401 Unauthorized` from Foundry anthropic endpoint

Principal lacks `Azure AI User` on the resource. Run §5 role assignment one-liner.

### 7.3 `404 deployment not found`

The pinned deployment name does not exist on `ipai-copilot-resource`. Either:
- Deploy it via New Foundry UI, OR
- Update `ANTHROPIC_DEFAULT_*_MODEL` to match an existing deployment (`az cognitiveservices account deployment list -n ipai-copilot-resource -g rg-data-intel-ph -o table`)

Current state (2026-04-14): resource has **0 deployments** — Claude Code against Foundry will 404 until models are deployed. See `project_foundry_zero_deployments`.

### 7.4 `/login` / `/logout` disabled

Expected in Foundry mode. Auth flows through Azure; the Anthropic console login is irrelevant. This is documented behavior, not a defect.

### 7.5 Rate-limit 429 at high concurrency

Foundry enforces per-deployment TPM/RPM. Remediate by:
1. Raising the deployment's capacity units in Foundry UI, OR
2. Splitting Opus/Sonnet/Haiku across distinct deployments (already the default pattern)

---

## 8. Pinned Model Version Policy

| Rule | Status |
|---|---|
| Floating model aliases in env vars | **Forbidden** |
| Date-suffixed deployment names | **Required** |
| Rollback deployment retained ≥7 days after cut-over | **Required** |
| Deployment changes land via SSOT file `ssot/foundry/claude-code-deployments.yaml` | **Required** |
| Deployment mutations via Foundry UI without PR | **Forbidden for prod lanes** |
| Dev lane UI mutation | Allowed with retroactive SSOT update within 24h |

---

## 9. Verification Checklist

Run before declaring Claude Code + Foundry wiring operational:

```bash
# 1. Toggle set
[ "$CLAUDE_CODE_USE_FOUNDRY" = "1" ] || echo FAIL: toggle off

# 2. Resource resolves
az cognitiveservices account show \
  -n ipai-copilot-resource -g rg-data-intel-ph \
  --query "{name:name, endpoint:properties.endpoint}" -o table

# 3. Token acquires
az account get-access-token \
  --resource https://cognitiveservices.azure.com >/dev/null && echo OK

# 4. Deployments exist
az cognitiveservices account deployment list \
  -n ipai-copilot-resource -g rg-data-intel-ph -o table

# 5. Anthropic endpoint reachable (with token)
TOKEN=$(az account get-access-token --resource https://cognitiveservices.azure.com --query accessToken -o tsv)
curl -sS -o /dev/null -w "%{http_code}\n" \
  -H "Authorization: Bearer $TOKEN" \
  https://ipai-copilot-resource.services.ai.azure.com/anthropic/v1/models
```

Expected HTTP code: `200` (or `404` on the path if models endpoint is unsupported in your Foundry tier — confirm auth with `401` vs non-`401`).

---

## 10. Related

- `CLAUDE.md` — Cross-Repo Invariants #1 (secrets), #10 (MCP first), #11 (SaaS authority)
- `docs/architecture/SSOT_BOUNDARIES.md`
- `.claude/rules/security-baseline.md`
- Memory: `feedback_foundry_reuse_doctrine`, `project_foundry_zero_deployments`, `reference_foundry_sdk_2x`, `project_foundry_managed_identity`

---

*Created 2026-04-14.*
