# Azure Developer CLI (azd) — Benchmark Knowledge Base

> **Doctrine**: azd is the developer-facing app bootstrap/deploy tool.
> Azure CLI is the admin-facing tool. azd first for app provisioning and deployment.

---

## Source

- [Azure Developer CLI Documentation](https://learn.microsoft.com/en-us/azure/developer/azure-developer-cli/)
- [azd Reference](https://learn.microsoft.com/en-us/azure/developer/azure-developer-cli/reference)
- [azd Templates](https://azure.github.io/awesome-azd/)

---

## What azd Is

Azure Developer CLI (`azd`) is a developer-centric command-line tool that:
- Bootstraps new projects from templates
- Provisions Azure infrastructure from declarative definitions
- Deploys application code to provisioned infrastructure
- Configures CI/CD pipelines with federated credentials
- Manages environment-specific configuration

**azd is NOT** a replacement for Azure CLI. It operates at a higher abstraction level — applications and environments, not individual resources.

---

## Key Commands

| Command | Purpose | When to use |
|---------|---------|-------------|
| `azd init` | Initialize project from template | New project setup |
| `azd init --template <url>` | Initialize from specific template | Known template |
| `azd env new <name>` | Create new environment | New env (dev/staging/prod) |
| `azd env set <key> <value>` | Set environment variable | Configure env |
| `azd env get-values` | Show all env values | Verify configuration |
| `azd provision` | Create/update infrastructure | Infrastructure changes |
| `azd deploy` | Deploy application code | Code changes |
| `azd up` | Provision + deploy (combined) | Full deployment |
| `azd down` | Delete all provisioned resources | Cleanup |
| `azd monitor` | Open monitoring dashboard | Observability |
| `azd pipeline config` | Set up CI/CD pipeline | CI/CD setup |
| `azd template list` | Browse available templates | Template discovery |
| `azd template show <name>` | Show template details | Template evaluation |

---

## azure.yaml Structure

The `azure.yaml` file is the project manifest that declares services and their Azure hosting targets.

```yaml
name: my-project
metadata:
  template: azure-samples/my-template@version
services:
  web:
    project: ./src/web
    host: containerapp          # ACA
    language: python
  api:
    project: ./src/api
    host: containerapp
    language: python
  worker:
    project: ./src/worker
    host: containerapp
    language: python
  func:
    project: ./src/functions
    host: function              # Azure Functions
    language: python
```

### Host types

| Host | Azure Service |
|------|---------------|
| `containerapp` | Azure Container Apps |
| `function` | Azure Functions |
| `appservice` | Azure App Service |
| `staticwebapp` | Azure Static Web Apps |
| `aks` | Azure Kubernetes Service |

---

## Environment Model

azd environments map to deployment targets (dev, staging, prod):

```bash
# Create environments
azd env new dev
azd env new staging
azd env new prod

# Switch active environment
azd env select dev

# Set per-environment values
azd env set AZURE_LOCATION southeastasia --env dev
azd env set AZURE_LOCATION southeastasia --env staging

# Deploy to specific environment
azd up --env staging
```

Environment values are stored locally in `.azure/<env-name>/.env` (gitignored).

---

## CI/CD Integration

### GitHub Actions

```bash
# Generate GitHub Actions workflow
azd pipeline config --provider github
```

Generates `.github/workflows/azure-dev.yml` with:
- Federated credentials (OIDC — no stored secrets)
- Provision and deploy steps
- Environment-specific deployment

### Azure Pipelines

```bash
# Generate Azure Pipelines configuration
azd pipeline config --provider azdo
```

---

## Template Model

Templates are starter projects that include:
- Application code (in one or more languages)
- Infrastructure as Code (Bicep or Terraform)
- `azure.yaml` project manifest
- CI/CD configuration
- Documentation

**Template discovery**:
```bash
azd template list                              # Browse all
azd template list --source awesome-azd         # Community templates
azd template show <name>                       # Details
```

**Template quality tiers**:
1. **Microsoft-published**: Highest quality, maintained by Azure team
2. **Community (awesome-azd)**: Variable quality, community-maintained
3. **Custom**: Organization-specific templates

---

## Platform Conventions for azd

| Convention | Value | Notes |
|-----------|-------|-------|
| Subscription | InsightPulse AI | Single subscription |
| Primary region | southeastasia | Compute, data |
| AI region | eastus | Azure OpenAI, AI services |
| Resource group pattern | rg-ipai-{env} | dev, staging, prod |
| ACA environment | cae-ipai-{env} | Container Apps env |
| Key Vault | kv-ipai-{env} | Secrets management |
| Container registry | cripaidev | Shared ACR |

---

## Guardrails

1. **azd first** for app bootstrap, provisioning, and deployment
2. **Azure CLI** when azd cannot accomplish the task (diagnostics, log queries, granular admin)
3. **Templates are fixtures** — extract patterns, adapt to platform
4. **Secure defaults** — managed identity, VNet, keyless access in all templates
5. **CI/CD via azd pipeline config** — not manual workflow creation
6. **Environment isolation** — separate azd environments for dev/staging/prod

---

## Cross-references

- `agents/personas/azure-bootstrap-engineer.md`
- `agents/skills/azd-template-selection/`
- `agents/skills/azd-environment-bootstrap/`
- `agents/skills/azd-secure-default-deployment/`
- `agents/knowledge/benchmarks/azure-cli-vs-azd.md`
