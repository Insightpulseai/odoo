# Security and Governance

> Identity boundaries, secrets management, tenant isolation, and data governance.

## Tenant Boundary

| Boundary | Enforcement |
|----------|-------------|
| Entra tenant | `402de71a-87ec-4302-a609-fb76098d1da7` -- all tokens must originate from this tenant |
| Odoo database | Single-tenant (`list_db=False`) -- no cross-database access |
| Foundry project | `data-intel-ph` -- agent definitions, evals, tracing scoped to project |
| Azure AI Search | Index-level isolation -- copilot index is separate from other workloads |
| Network | ACA environment `ipai-odoo-dev-env` with internal-only service mesh |

## Secrets Management

### Secret Storage

| Secret | Store | Access method |
|--------|-------|--------------|
| Azure OpenAI API key | Azure Key Vault (`kv-ipai-dev`) | Managed identity -> env var |
| Entra client secret | Azure Key Vault (`kv-ipai-dev`) | Managed identity -> env var |
| Odoo DB password | Azure Key Vault (`kv-ipai-dev`) | Managed identity -> env var |
| Search admin key | Azure Key Vault (`kv-ipai-dev`) | Managed identity -> env var |

### Secret Flow

```
Azure Key Vault (kv-ipai-dev)
  -> Managed Identity (ACA system-assigned)
    -> Container App env var binding
      -> Odoo ir.config_parameter (seeded at init, non-secret reference only)
```

### Secret Rules

1. No secrets in git (enforced by `.gitignore` and GHAS secret scanning)
2. No secrets in Odoo `ir.config_parameter` (only non-secret config like base URLs)
3. No secrets in copilot audit logs (inputs are sanitized before logging)
4. No secrets in Foundry traces (tool inputs are redacted)
5. No secrets in search index content

## Identity Boundaries

See [Identity & Access](identity-access.md) for the full identity model.

Summary:

| Subject | Identity type | Auth method |
|---------|--------------|-------------|
| Human user | Workforce (Entra ID) | OIDC -> Odoo session |
| Copilot backend | Workload (Managed Identity) | Token -> Foundry API |
| Copilot tool callbacks | Workload (Managed Identity) | Token -> Odoo FastAPI |
| Agent (future) | Agent identity (Foundry) | Foundry-managed -> tool endpoints |

## Data Classification

| Data type | Classification | Copilot access |
|-----------|---------------|---------------|
| Odoo transactional records | Business confidential | Via ORM, respects ACLs |
| Financial reports | Business confidential | Via read tools only |
| Employee PII (HR) | Sensitive PII | Restricted to HR group users |
| Indexed documents | Per-document classification | Filtered by department/source_type |
| Copilot audit logs | Internal operational | Platform team only |
| Model prompts/responses | Transient | Not persisted beyond audit log |

## Compliance Controls

| Control | Implementation |
|---------|---------------|
| Data residency | Southeast Asia region for all Azure resources |
| Encryption at rest | Azure-managed keys (ACA, PG, Search, Key Vault) |
| Encryption in transit | TLS 1.2+ (Azure Front Door -> ACA, ACA -> Foundry) |
| Access logging | Azure Monitor + Odoo audit log |
| Content safety | Azure AI Content Safety on all model endpoints |
| Retention | Audit logs retained per organizational retention policy |

## Governance Gates

| Gate | When | Owner |
|------|------|-------|
| Tool registration review | Before adding new copilot tool | Platform team |
| Prompt template review | Before modifying system prompts | Platform team + domain owner |
| Search index schema change | Before modifying index fields | Platform team |
| Model deployment change | Before switching model version | Platform team |
| Evaluation pass | Before any rollout stage advancement | Platform team |
| Red-team review | Before GA release | Security team |
