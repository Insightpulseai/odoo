# Azure CLI vs azd — Decision Benchmark

> **Doctrine**: azd first for app bootstrap/deployment. Azure CLI for granular admin/control.
> Use the `azd-vs-azure-cli-decision` judge skill when tool selection is ambiguous.

---

## Source

- [Azure Developer CLI Overview](https://learn.microsoft.com/en-us/azure/developer/azure-developer-cli/azd-overview)
- [Azure CLI Overview](https://learn.microsoft.com/en-us/cli/azure/)

---

## Fundamental Distinction

| Dimension | azd | Azure CLI |
|-----------|-----|-----------|
| **Abstraction** | Application-level | Resource-level |
| **User** | Developer | Operator/Admin |
| **Scope** | Full app lifecycle | Individual resource ops |
| **Config** | azure.yaml (declarative) | Commands (imperative) |
| **Provisioning** | Template-driven IaC | Manual or scripted |
| **Deployment** | Packaged app deploy | Container/code push |
| **CI/CD** | Built-in pipeline config | Manual workflow |
| **Environments** | First-class concept | Not native |

---

## Decision Matrix

### Use azd when:

| Task | Command | Why azd |
|------|---------|---------|
| New project setup | `azd init` | Template-driven, reproducible |
| Infrastructure provisioning | `azd provision` | Declarative, version-controlled |
| Application deployment | `azd deploy` | Packaged, environment-aware |
| Full deploy (infra + code) | `azd up` | Single command, consistent |
| CI/CD pipeline setup | `azd pipeline config` | Federated credentials, integrated |
| Template browsing | `azd template list` | Curated catalog |
| Environment management | `azd env new/set/select` | First-class environments |
| Monitoring dashboard | `azd monitor` | Quick access to App Insights |
| Resource cleanup | `azd down` | Clean teardown of all resources |

### Use Azure CLI when:

| Task | Command | Why Azure CLI |
|------|---------|---------------|
| Resource inventory | `az resource list` | Granular queries |
| Resource Graph queries | `az graph query` | Cross-resource queries |
| Container App logs | `az containerapp logs show` | Real-time diagnostics |
| Scaling changes | `az containerapp update --min-replicas` | Operational adjustment |
| Key Vault operations | `az keyvault secret list` | Secret management |
| Certificate management | `az containerapp ssl` | Admin operation |
| DNS configuration | `az network dns` | Infrastructure admin |
| Front Door configuration | `az afd` | Edge routing changes |
| Load testing | `az load` | Performance testing |
| Role assignments | `az role assignment` | IAM configuration |
| Monitor queries | `az monitor log-analytics query` | Log analytics |
| Resource health | `az resource show` | Status checking |

### Use BOTH when:

| Task | azd portion | Azure CLI portion |
|------|-------------|-------------------|
| Deploy + verify health | `azd up` | `az containerapp show --query probes` |
| Provision + configure DNS | `azd provision` | `az network dns record-set` |
| Deploy + check logs | `azd deploy` | `az containerapp logs show` |
| Initial setup + fine-tune | `azd up` | `az containerapp update` for specific settings |

---

## Anti-Patterns

### Using Azure CLI for app bootstrap (WRONG)

```bash
# WRONG — imperative, not reproducible
az group create -n rg-ipai-dev -l southeastasia
az containerapp env create -n cae-ipai-dev -g rg-ipai-dev
az containerapp create -n my-app -g rg-ipai-dev --environment cae-ipai-dev ...
az containerapp ingress enable ...
az containerapp identity assign ...
```

```bash
# CORRECT — declarative, reproducible, template-driven
azd init --template azure-samples/my-template
azd env new dev
azd up
```

### Using azd for diagnostics (WRONG)

```bash
# WRONG — azd doesn't have granular log queries
azd monitor  # Only opens dashboard, can't query logs

# CORRECT — Azure CLI for diagnostics
az containerapp logs show -n my-app -g rg-ipai-dev --tail 100
az monitor log-analytics query -w <workspace-id> --analytics-query "ContainerAppLogs | take 100"
```

### Using Azure CLI for CI/CD setup (WRONG)

```bash
# WRONG — manual pipeline creation
# Creating GitHub Actions workflow by hand with az CLI commands

# CORRECT — azd generates pipeline with federated credentials
azd pipeline config --provider github
```

---

## Decision Flowchart

```
Is this an app lifecycle task?
├── YES → Is it bootstrap, provision, deploy, or CI/CD?
│         ├── YES → Use azd
│         └── NO → What is it?
│                   ├── Monitoring dashboard → azd monitor
│                   └── Other → Check Azure CLI
└── NO → Is it a resource-level operation?
         ├── YES → Use Azure CLI
         │         ├── Inventory/query → az resource, az graph
         │         ├── Diagnostics → az monitor, az containerapp logs
         │         ├── Configuration → az <resource> update
         │         ├── Maintenance → az <resource> restart/rotate
         │         └── Load testing → az load
         └── NO → Clarify the task
```

---

## Platform-Specific Rules

1. **Odoo deployment** → azd (ACA template, azure.yaml with web + worker + cron services)
2. **Odoo log debugging** → Azure CLI (`az containerapp logs show`)
3. **New service addition** → azd (add service to azure.yaml, `azd up`)
4. **Scaling Odoo replicas** → Azure CLI (`az containerapp update --min-replicas`)
5. **Key Vault secret rotation** → Azure CLI (`az keyvault secret set`)
6. **CI/CD pipeline** → azd (`azd pipeline config`)
7. **Front Door routing** → Azure CLI (`az afd route update`)
8. **SSL certificate** → Azure CLI (`az containerapp ssl upload`)

---

## Cross-references

- `agents/personas/azd-deployment-judge.md`
- `agents/skills/azd-vs-azure-cli-decision/`
- `agents/knowledge/benchmarks/azure-developer-cli.md`
