# Microsoft Entra Knowledge Base — InsightPulseAI Reference

> Last updated: 2026-03-19
> Sources: Microsoft Learn (learn.microsoft.com/en-us/entra/)

## 1. Microsoft Entra Product Family

Microsoft Entra is the unified identity and network access platform. It encompasses:

| Product | Purpose | Status @ IPAI |
|---------|---------|---------------|
| **Entra ID** (formerly Azure AD) | Cloud identity & access management | Active — primary IdP |
| **Entra External ID** | Customer/partner CIAM | Planned for marketplace |
| **Entra Verified ID** | Decentralized verifiable credentials | Not yet adopted |
| **Entra Permissions Management** | Multi-cloud CIEM | Evaluation |
| **Entra Workload ID** | Service/app/container identity | Active — MI + federation |
| **Entra Internet Access** | SWG/SSE for internet traffic | Not yet adopted |
| **Entra Private Access** | ZTNA replacing VPN | Not yet adopted |
| **Entra Domain Services** | Managed AD DS | Not needed |
| **Entra Global Secure Access** | Unified SSE gateway | Not yet adopted |
| **Entra Agent ID** (Preview) | AI agent identity governance | **Target for IPAI agents** |

---

## 2. Entra ID Core Concepts

### 2.1 Identity Objects

| Object | Description | IPAI Usage |
|--------|-------------|------------|
| **User** | Human identity with UPN | Team members, admins |
| **Group** | Collection for bulk RBAC | Role-based security groups |
| **App Registration** | Global app identity template | InsightPulseAI app registration |
| **Service Principal** | Local instance of app registration | Per-tenant representation |
| **Managed Identity** | Azure-managed secretless identity | Container Apps, CI/CD |
| **Agent Identity** | AI agent identity (Preview) | Copilot, Pulser agents |

### 2.2 Authentication Protocols

- **OAuth 2.0** — Authorization framework for delegated/app-only access
- **OpenID Connect (OIDC)** — Authentication layer on OAuth 2.0
- **SAML 2.0** — Enterprise SSO (legacy apps)
- **FIDO2/WebAuthn** — Passwordless hardware keys
- **Windows Hello for Business** — Biometric/PIN passwordless
- **Certificate-based Auth (CBA)** — X.509 certificate authentication

### 2.3 Token Types

| Token | Issued By | Contains | Used For |
|-------|-----------|----------|----------|
| **ID Token** | Entra ID | User identity claims | Authentication |
| **Access Token** | Entra ID | Permissions/scopes/roles | API authorization |
| **Refresh Token** | Entra ID | Long-lived session | Token renewal |
| **Primary Refresh Token (PRT)** | Entra ID | Device + user session | SSO across apps |

---

## 3. Managed Identities

### 3.1 System-Assigned vs User-Assigned

| Feature | System-Assigned | User-Assigned |
|---------|----------------|---------------|
| Lifecycle | Tied to resource | Independent |
| Sharing | 1:1 with resource | 1:many resources |
| Creation | Enabled on resource | Created separately |
| Federation | Not supported | Supported |
| Container Apps create | Not available at create time | Available |
| **IPAI recommendation** | For single-purpose services | **For Container Apps + CI/CD** |

### 3.2 IPAI Managed Identity Architecture

```
User-Assigned MI: mi-ipai-odoo-{env}
├── Key Vault Secrets User     → ipai-odoo-{env}-kv
├── AcrPull                    → ipaiodoo{env}acr
└── Azure Container Apps scope → cae-ipai-odoo-{env}

System-Assigned MI: per Container App
├── Diagnostics access
└── Environment-specific permissions
```

### 3.3 Key Vault Access Pattern

```python
# Python — DefaultAzureCredential automatically uses managed identity
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

credential = DefaultAzureCredential()
client = SecretClient(
    vault_url="https://ipai-odoo-dev-kv.vault.azure.net/",
    credential=credential
)
secret = client.get_secret("pg-admin-password")
```

```typescript
// TypeScript — @azure/identity
import { DefaultAzureCredential } from "@azure/identity";
import { SecretClient } from "@azure/keyvault-secrets";

const credential = new DefaultAzureCredential();
const client = new SecretClient(
  "https://ipai-odoo-dev-kv.vault.azure.net/",
  credential
);
const secret = await client.getSecret("pg-admin-password");
```

---

## 4. Workload Identity Federation

### 4.1 How It Works

External IdPs (GitHub, GCP, AWS) issue tokens. Entra ID trusts those tokens via federated identity credentials, exchanging them for Entra access tokens. No secrets stored.

```
GitHub Actions OIDC Token
        │
        ▼
  Entra ID Federation
  (issuer + subject match)
        │
        ▼
  Entra Access Token
        │
        ▼
  Azure Resources (Key Vault, ACR, ACA)
```

### 4.2 GitHub Actions Configuration

```yaml
# .github/workflows/deploy.yml
permissions:
  id-token: write   # Required for OIDC
  contents: read

steps:
  - uses: azure/login@v2
    with:
      client-id: ${{ secrets.AZURE_CLIENT_ID }}
      tenant-id: ${{ secrets.AZURE_TENANT_ID }}
      subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
```

Federated credential configuration:
- **Issuer**: `https://token.actions.githubusercontent.com`
- **Subject**: `repo:Insightpulseai/odoo:ref:refs/heads/main`
- **Audience**: `api://AzureADTokenExchange`

### 4.3 Important Constraints

- Max **20 federated credentials** per app/MI
- Create credentials **sequentially** (concurrent creates → 409 Conflict)
- Only **RS256-signed tokens** supported
- Propagation delay after creation (allow ~5 minutes)
- Case-sensitive matching on issuer, subject, audience

---

## 5. Conditional Access

### 5.1 Policy Framework

| Policy Type | Applies To | IPAI Status |
|-------------|-----------|-------------|
| User-based CA | Human users | Active |
| Device-based CA | Managed/compliant devices | Planned |
| Workload identity CA | Service principals | **Target** |
| Agent identity CA | AI agents (Preview) | **Target** |
| Risk-based CA | Users/workloads with risk signals | Planned |

### 5.2 Recommended Policies for IPAI

1. **Block legacy auth** — Disable basic authentication protocols
2. **Require MFA** — All admin roles, phishing-resistant for Global Admin
3. **Named locations** — Allow CI/CD from GitHub Actions IPs only
4. **Workload identity CA** — Block service principals outside Azure IPs
5. **Session controls** — Sign-in frequency for sensitive roles (finance)
6. **App protection** — Require compliant devices for Odoo access

### 5.3 Continuous Access Evaluation (CAE)

CAE enables near real-time token revocation for:
- User disabled/deleted
- Password changed
- Admin-initiated revocation
- Network location change

---

## 6. Entra Agent ID (Preview)

### 6.1 Core Concepts

| Concept | Description |
|---------|-------------|
| **Agent Identity** | First-class identity for AI agents in Entra |
| **Agent Blueprint** | Reusable template defining agent type/class |
| **Agent Registry** | Centralized metadata store of all deployed agents |
| **Sponsor** | Human user accountable for agent lifecycle/access |
| **Attended Mode** | Agent acts on behalf of user (delegated/OBO) |
| **Unattended Mode** | Agent acts under its own authority (autonomous) |

### 6.2 IPAI Agent Identity Map

| Agent | Type | Auth Mode | Sponsor | Blueprint |
|-------|------|-----------|---------|-----------|
| Copilot (Odoo) | Internal | Attended | Product Lead | copilot-advisory |
| Copilot (Action) | Internal | Attended | Engineering Lead | copilot-action |
| Pulser CI | Automation | Unattended | DevOps Lead | ci-automation |
| Claude Code | Development | Attended | Engineering Lead | dev-assistant |
| n8n Workflows | Integration | Unattended | Integration Lead | workflow-engine |

### 6.3 Agent Governance Lifecycle

```
Registration → Sponsor Assignment → Access Package Request
      │                                        │
      ▼                                        ▼
Blueprint Creation → Permissions Scoped → Conditional Access
      │                                        │
      ▼                                        ▼
Monitoring (ID Protection) → Risk Detection → Remediation
      │
      ▼
Lifecycle Workflows → Sponsor Change Notification → Deprovisioning
```

### 6.4 Agent Identity API (Microsoft Graph Beta)

```http
# List agent identities
GET https://graph.microsoft.com/beta/agentIdentities

# Create agent identity from blueprint
POST https://graph.microsoft.com/beta/agentIdentities
{
  "displayName": "IPAI Copilot Advisory",
  "blueprintId": "{blueprint-id}",
  "sponsorId": "{user-object-id}",
  "authenticationMode": "attended"
}

# Detect agent risk
GET https://graph.microsoft.com/beta/identityProtection/riskyAgents
```

---

## 7. Key Vault Best Practices

### 7.1 Architecture Rules

1. **One vault per application per environment** (dev, staging, prod)
2. **RBAC authorization only** — never legacy access policies
3. **Soft delete + purge protection** — always enabled, 90-day retention
4. **Diagnostic settings** — audit logs to Log Analytics
5. **Network restrictions** — private endpoints in prod, `AzureServices` bypass
6. **No config storage** — Key Vault is for secrets/keys/certs, not app config
7. **Certificate auto-rotation** — store service certs as KV certificates, not secrets

### 7.2 Secret Naming Convention (IPAI)

```
{service}-{purpose}[-{qualifier}]

Examples:
  pg-admin-password
  zoho-smtp-password
  supabase-service-role-key
  anthropic-api-key
  acr-password
  front-door-origin-secret
  odoo-admin-password-{env}
```

### 7.3 Rotation Policy

| Secret Category | Rotation Period | Method |
|----------------|----------------|--------|
| Database passwords | 90 days | Automated (Key Vault + Azure Function) |
| API keys (external) | 180 days | Manual with notification |
| Service certificates | Auto-renew 30 days before expiry | Key Vault auto-rotation |
| SMTP credentials | 365 days | Manual |
| ACR passwords | Never (use MI instead) | Migrate to managed identity |

---

## 8. Zero Trust Alignment

### 8.1 Principles Applied to IPAI

| Principle | Implementation |
|-----------|----------------|
| **Verify explicitly** | All access via Entra tokens, no shared secrets |
| **Least privilege** | App roles scoped per domain (see role-tool-mapping.yaml) |
| **Assume breach** | Soft delete, audit logging, identity protection, CAE |

### 8.2 Identity Security Checklist

- [ ] MFA enforced for all users
- [ ] Passwordless for admin accounts
- [ ] Emergency access accounts configured (2+, excluded from CA)
- [ ] PIM activated for privileged roles
- [ ] Access reviews scheduled quarterly
- [ ] Self-service password reset enabled
- [ ] Legacy authentication blocked
- [ ] Risk-based conditional access active
- [ ] Workload identity conditional access configured
- [ ] Agent identities registered with sponsors

---

## 9. CLI Quick Reference

### az CLI — Entra & Key Vault

```bash
# List users
az ad user list --query "[].{UPN:userPrincipalName,Id:id}" -o table

# Create app registration
az ad app create --display-name "InsightPulseAI" --sign-in-audience AzureADMyOrg

# Create user-assigned managed identity
az identity create -g rg-ipai-shared-dev -n mi-ipai-odoo-dev

# Assign Key Vault Secrets User to MI
az role assignment create \
  --assignee-object-id $(az identity show -g rg-ipai-shared-dev -n mi-ipai-odoo-dev --query principalId -o tsv) \
  --role "Key Vault Secrets User" \
  --scope /subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.KeyVault/vaults/{kv}

# Add federated credential for GitHub Actions
az ad app federated-credential create --id {app-id} --parameters '{
  "name": "github-actions-main",
  "issuer": "https://token.actions.githubusercontent.com",
  "subject": "repo:Insightpulseai/odoo:ref:refs/heads/main",
  "audiences": ["api://AzureADTokenExchange"]
}'

# Set Key Vault secret
az keyvault secret set --vault-name ipai-odoo-dev-kv --name pg-admin-password --value "{value}"

# Get Key Vault secret (verify)
az keyvault secret show --vault-name ipai-odoo-dev-kv --name pg-admin-password --query value -o tsv
```

### Microsoft Graph — Entra Agent ID (Beta)

```bash
# List agent identities
az rest --method GET --url "https://graph.microsoft.com/beta/agentIdentities"

# List risky agents
az rest --method GET --url "https://graph.microsoft.com/beta/identityProtection/riskyAgents"
```

---

## 10. Licensing Requirements

| Feature | Required License |
|---------|-----------------|
| Entra ID (basic SSO, MFA) | Free / Microsoft 365 |
| Conditional Access | Entra ID P1 |
| Identity Protection | Entra ID P2 |
| PIM | Entra ID P2 |
| Access Reviews | Entra ID P2 |
| Workload Identity CA | Workload Identities Premium |
| Entra Agent ID | Microsoft 365 Copilot + Frontier |
| Entra Permissions Management | Standalone license |
| Entra Verified ID | Free (preview) |

---

## Sources

- [Microsoft Entra documentation](https://learn.microsoft.com/en-us/entra/)
- [Managed identities overview](https://learn.microsoft.com/en-us/entra/identity/managed-identities-azure-resources/overview)
- [Workload Identity Federation](https://learn.microsoft.com/en-us/entra/workload-id/workload-identity-federation)
- [Key Vault authentication](https://learn.microsoft.com/en-us/azure/key-vault/general/authentication)
- [Key Vault RBAC guide](https://learn.microsoft.com/en-us/azure/key-vault/general/rbac-guide)
- [Container Apps managed identity](https://learn.microsoft.com/en-us/azure/container-apps/managed-identity)
- [Container Apps secrets](https://learn.microsoft.com/en-us/azure/container-apps/manage-secrets)
- [Entra Agent ID overview](https://learn.microsoft.com/en-us/entra/agent-id/identity-platform/what-is-agent-id)
- [Agent identity governance](https://learn.microsoft.com/en-us/entra/id-governance/agent-id-governance-overview)
- [Conditional Access for workloads](https://learn.microsoft.com/en-us/entra/identity/conditional-access/workload-identity)
- [Entra best practices](https://learn.microsoft.com/en-us/entra/architecture/secure-best-practices)
- [Key Vault security](https://learn.microsoft.com/en-us/azure/key-vault/general/secure-key-vault)
