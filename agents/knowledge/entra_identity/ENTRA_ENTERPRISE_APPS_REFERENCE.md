# Microsoft Entra ID Enterprise Applications -- Agent Reference

> Comprehensive reference for programmatic management of Entra enterprise apps.
> Source: Microsoft Learn (crawled 2026-03-23, 20+ pages).
> Scope: SSO, provisioning, consent, governance, certificates, Graph API, PowerShell.

---

## 1. Enterprise App Management -- Fundamentals

### Key Concepts

- **Application object** (`application` in Graph): The global definition of an app, registered in one tenant. Holds credentials, permissions, redirect URIs, and metadata.
- **Service principal** (`servicePrincipal` in Graph): The per-tenant instance of an app. This is what shows up under "Enterprise applications" in the Entra admin center. Controls local SSO, user assignment, and consent grants.
- **App Registration vs Enterprise App**: App Registration = application object (developer-facing). Enterprise App = service principal (admin-facing). One application can have service principals in many tenants.

### App Types

| Type | Description | SSO Protocol |
|------|-------------|--------------|
| Gallery (pre-integrated) | 5000+ apps in Microsoft Entra gallery | SAML, OIDC, password |
| Non-gallery (custom SAML) | Any SAML 2.0 or WS-Fed app | SAML |
| Custom OIDC | Your own app registered via App Registrations | OIDC / OAuth 2.0 |
| On-premises (App Proxy) | Internal web apps published via Application Proxy | IWA, header, SAML, password |
| Linked | Just a link in My Apps portal; no SSO via Entra | None |

### Enterprise App Properties (servicePrincipal)

| Property | Graph Field | Effect |
|----------|-------------|--------|
| Enabled for sign-in | `accountEnabled` | `false` blocks all sign-in + token issuance |
| Assignment required | `appRoleAssignmentRequired` | `true` = only assigned users/apps can get tokens |
| Visible to users | `tags` contains `HideApp` | Controls My Apps and M365 launcher visibility |
| Name | `displayName` | Shown in My Apps |
| Homepage URL | `homepage` (on app object) | Launch URL from My Apps |
| Application ID | `appId` | Immutable app identifier |
| Object ID | `id` (on servicePrincipal) | Used in Graph API paths |

### Roles Required

| Role | Scope |
|------|-------|
| Cloud Application Administrator | Manage non-Microsoft Graph app roles |
| Application Administrator | Same as above + app proxy |
| Privileged Role Administrator | Grant consent for Microsoft Graph app roles |
| Global Administrator | Everything (use sparingly) |

### Graph API -- Application Lifecycle

```
# Register app from gallery
POST https://graph.microsoft.com/v1.0/applicationTemplates/{id}/instantiate
{ "displayName": "My App" }

# Create custom app registration
POST https://graph.microsoft.com/v1.0/applications
{ "displayName": "My App", "signInAudience": "AzureADMyOrg" }

# List enterprise apps (service principals)
GET https://graph.microsoft.com/v1.0/servicePrincipals?$filter=displayName eq 'My App'

# Update service principal properties
PATCH https://graph.microsoft.com/v1.0/servicePrincipals/{id}
{ "appRoleAssignmentRequired": true, "accountEnabled": true }

# Delete service principal (soft delete, 30-day recycle bin)
DELETE https://graph.microsoft.com/v1.0/servicePrincipals/{id}

# List deleted apps
GET https://graph.microsoft.com/v1.0/directory/deletedItems/microsoft.graph.servicePrincipal

# Restore deleted app
POST https://graph.microsoft.com/v1.0/directory/deletedItems/{id}/restore

# Permanently delete
DELETE https://graph.microsoft.com/v1.0/directory/deletedItems/{id}
```

### PowerShell

```powershell
# Microsoft Graph PowerShell
Connect-MgGraph -Scopes "Application.ReadWrite.All"

# List service principals
Get-MgServicePrincipal -Filter "displayName eq 'My App'"

# Update
Update-MgServicePrincipal -ServicePrincipalId $id -AppRoleAssignmentRequired:$true

# Delete
Remove-MgServicePrincipal -ServicePrincipalId $id

# Microsoft Entra PowerShell (newer)
Connect-Entra -Scopes "Application.ReadWrite.All"
Get-EntraServicePrincipal -Filter "displayName eq 'My App'"
Remove-EntraServicePrincipal -ObjectId $id
```

---

## 2. Single Sign-On (SSO)

### SSO Types

| Type | Protocol | Best For | Graph Config |
|------|----------|----------|-------------|
| Federated (SAML) | SAML 2.0 | SaaS apps with SAML support | `preferredSingleSignOnMode = "saml"` |
| Federated (OIDC) | OpenID Connect / OAuth 2.0 | Modern apps, SPAs | Configured via app registration |
| Password-based | Form fill / browser extension | Legacy apps with HTML login forms | `preferredSingleSignOnMode = "password"` |
| Linked | None (just a URL) | Migration period; deep links | `preferredSingleSignOnMode = "linkedSignOn"` |
| Disabled | None | Testing or intentionally no SSO | `preferredSingleSignOnMode = "notSupported"` |

### SAML SSO Configuration

**Key SAML parameters (Basic SAML Configuration):**

| Parameter | Graph Property | Description |
|-----------|---------------|-------------|
| Identifier (Entity ID) | `identifierUris` (app object) | Unique identifier for the app, usually a URI |
| Reply URL (ACS URL) | `replyUrls` (app) / `replyUrlsWithType` | Where Entra sends SAML assertions |
| Sign-on URL | `loginUrl` (SP) | SP-initiated SSO entry point |
| Logout URL | `logoutUrl` | Where to redirect after sign-out |
| Relay State | N/A (per-request) | Optional; deep-link within app after SSO |

**SAML Certificates:**
- Auto-generated self-signed cert valid for 3 years
- SHA-256 signing algorithm by default (SHA-1 available for legacy)
- Max signing cert lifetime: 3 years
- Expiration notifications sent at 60, 30, and 7 days before expiry
- Up to 5 notification email addresses configurable
- Certificate statuses: Active, Inactive
- Certificate formats: Raw (.cer), Base64, PEM, Federation Metadata XML

**Graph API for SAML cert:**
```
# Add a token signing certificate
POST https://graph.microsoft.com/v1.0/servicePrincipals/{id}/addTokenSigningCertificate
{ "displayName": "CN=MyCert", "endDateTime": "2027-01-01T00:00:00Z" }
```

**ISV cert rotation best practice:** Applications should poll the federation metadata URL (`https://login.microsoftonline.com/{tenant}/federationmetadata/2007-06/federationmetadata.xml?appid={appId}`) at least every 24 hours, support primary/secondary signing certificates, and auto-promote new certs.

### OIDC SSO Configuration

- Gallery OIDC apps: Added via consent flow ("Sign up" button in gallery)
- Custom OIDC apps: Registered via App Registrations then configured
- Key endpoints (per tenant):
  - Metadata: `https://login.microsoftonline.com/{tenant}/v2.0/.well-known/openid-configuration`
  - Authorization: `https://login.microsoftonline.com/{tenant}/oauth2/v2.0/authorize`
  - Token: `https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token`
  - JWKS: published in metadata
- Recommended flow: Authorization Code with PKCE (especially for SPAs)
- Implicit flow: NOT recommended for new apps (security risk)
- Supported account types: single-tenant, multi-tenant, personal accounts

### Common SAML SSO Gotchas

1. SAML SSO only configurable on single-tenant apps or gallery apps (multi-tenant shows greyed out)
2. If app registered via App Registrations using OIDC, the SSO option does not appear under Enterprise Apps
3. Reply URL must exactly match what the app sends
4. Certificate rotation requires coordination with the app vendor
5. SP-initiated vs IdP-initiated: disabling SSO mode does not prevent users from accessing app directly

---

## 3. Application Proxy (On-Premises Access)

### Architecture

```
User -> External URL -> Azure Front Door -> Application Proxy Service (cloud)
  -> Private Network Connector (on-prem agent, outbound only)
  -> Internal application server
```

### Key Components

| Component | Description |
|-----------|-------------|
| Application Proxy Service | Cloud service in Entra ID; terminates TLS, validates tokens |
| Private Network Connector | Lightweight Windows Server agent; outbound-only (ports 80/443) |
| Connector Groups | Logical groupings of connectors for different networks/apps |

### Authentication Methods Supported

- Integrated Windows Authentication (IWA) via Kerberos Constrained Delegation (KCD)
- Header-based authentication (via PingAccess partner)
- Form-based authentication
- SAML authentication
- Password vaulting
- Remote Desktop Gateway integration

### Security Benefits

- No inbound firewall ports needed (outbound-only connections)
- Preauthentication in the cloud before traffic reaches on-prem
- Conditional Access policies apply to on-prem apps
- DDoS protection (traffic terminates at cloud edge)
- Integration with Microsoft Entra ID Protection and Defender for Cloud Apps

### Licensing

- Requires Microsoft Entra ID P1 or P2
- Connector is free; the license covers the service

---

## 4. Provisioning (Automated User Lifecycle)

### SCIM (System for Cross-domain Identity Management)

- SCIM 2.0 is the standard protocol for provisioning
- Entra ID acts as SCIM client; the app exposes a SCIM endpoint
- Supports: create, update, disable/delete users; provision groups

### Provisioning Modes

| Mode | Description |
|------|-------------|
| Automatic | Entra ID provisions via SCIM connector (gallery or custom) |
| Manual | No automatic connector; admin manages user accounts manually |

### Supported Connectors

| Protocol | Use Case |
|----------|----------|
| SCIM 2.0 | SaaS apps (Salesforce, ServiceNow, Slack, etc.) |
| SCIM on-prem | On-premises apps via provisioning agent |
| LDAP | On-premises LDAP directories |
| SQL | On-premises SQL databases |
| REST/SOAP | Web services via ECMA connector |
| PowerShell | Custom provisioning scripts |
| Custom ECMA | Partner-built connectors |

### Provisioning Cycles

- **Initial cycle**: Full sync of all users in scope; can take hours
- **Incremental cycle**: Every 40 minutes by default; processes only changes
- **On-demand provisioning**: Provision a single user immediately for testing

### Key Graph API for Provisioning

```
# Get provisioning configuration
GET https://graph.microsoft.com/v1.0/servicePrincipals/{id}/synchronization/jobs

# Start provisioning
POST https://graph.microsoft.com/v1.0/servicePrincipals/{id}/synchronization/jobs/{jobId}/start

# Restart provisioning (clears state)
POST https://graph.microsoft.com/v1.0/servicePrincipals/{id}/synchronization/jobs/{jobId}/restart

# Provision on demand
POST https://graph.microsoft.com/v1.0/servicePrincipals/{id}/synchronization/jobs/{jobId}/provisionOnDemand
```

### Attribute Mappings

- Map Entra user attributes to target app attributes
- Support: direct mapping, constant, expression (custom transforms)
- Scoping filters: control which users are in-scope for provisioning
- Matching attributes: determine if a user already exists in the target app (e.g., match on email)

### Best Practices

- Always test with on-demand provisioning before enabling automatic
- Review provisioning logs regularly (`GET /auditLogs/provisioning`)
- Use scoping filters to limit initial sync scope
- Assign users/groups before enabling provisioning
- SAML JIT (Just-in-Time) provisioning is an alternative for simpler needs

---

## 5. Conditional Access (Per-App Policies)

### How It Works with Enterprise Apps

- CA policies can target specific cloud apps by their Application ID
- Enterprise apps appear as "Cloud apps or actions" in CA policy conditions
- CA applies at authentication time (token issuance)

### Common Per-App Controls

| Control | Description |
|---------|-------------|
| Require MFA | Enforce multi-factor for specific apps |
| Require compliant device | Only allow managed/compliant devices |
| Require approved client app | Only allow approved mobile apps |
| Block access | Completely block access to an app |
| Session controls | Enforce Defender for Cloud Apps monitoring, limited session lifetime |
| Sign-in frequency | Force re-authentication after N hours |

### Key Consideration

- Linked SSO apps: CA policies cannot be applied (no Entra authentication)
- Application Proxy apps: CA fully supported (preauthentication in cloud)
- CA evaluates before SSO completes; block = no token = no access

---

## 6. Consent and Permissions

### Consent Types

| Type | Who | When |
|------|-----|------|
| User consent | End user | When app requests delegated permissions user can grant |
| Admin consent | Admin | When app requests permissions requiring admin approval |
| Tenant-wide admin consent | Admin | Grants consent for all users in the organization |

### User Consent Policies (Built-in)

| Policy ID | Description |
|-----------|-------------|
| `microsoft-user-default-low` | Allow consent only for verified publishers, low-impact permissions |
| `microsoft-user-default-legacy` | Allow all user consent (legacy, less secure) |

### Graph API for Consent Configuration

```
# Get current authorization policy
GET https://graph.microsoft.com/v1.0/policies/authorizationPolicy

# Disable user consent (preserve other policies)
PATCH https://graph.microsoft.com/v1.0/policies/authorizationPolicy
{
  "defaultUserRolePermissions": {
    "permissionGrantPoliciesAssigned": [
      "managePermissionGrantsForOwnedResource.{existing-policies}"
    ]
  }
}

# Enable user consent with low-risk policy
PATCH https://graph.microsoft.com/v1.0/policies/authorizationPolicy
{
  "defaultUserRolePermissions": {
    "permissionGrantPoliciesAssigned": [
      "managePermissionGrantsForSelf.microsoft-user-default-low",
      "managePermissionGrantsForOwnedResource.{existing-policies}"
    ]
  }
}

# List permission grant policies
GET https://graph.microsoft.com/v1.0/policies/permissionGrantPolicies
```

### Admin Consent Workflow

- Enabled via: `Entra ID > Enterprise apps > Consent and permissions > Admin consent settings`
- Users can request admin consent for apps they cannot self-consent to
- Designated reviewers receive email notifications
- Requests expire after configurable number of days
- Only Global Administrators can approve requests for Microsoft Graph app roles

**Graph API:**
```
# Configure admin consent request policy
PATCH https://graph.microsoft.com/v1.0/policies/adminConsentRequestPolicy
```

### Granting Tenant-Wide Admin Consent

**Via URL (direct):**
```
https://login.microsoftonline.com/{tenant}/adminconsent?client_id={client-id}
```

**Via Graph -- Delegated Permissions:**
```
POST https://graph.microsoft.com/v1.0/oauth2PermissionGrants
{
  "clientId": "{service-principal-id}",
  "consentType": "AllPrincipals",
  "resourceId": "{resource-sp-id}",
  "scope": "User.Read.All Group.Read.All"
}
```

**Via Graph -- Application Permissions (App Roles):**
```
POST https://graph.microsoft.com/v1.0/servicePrincipals/{resource-sp-id}/appRoleAssignedTo
{
  "principalId": "{client-sp-id}",
  "resourceId": "{resource-sp-id}",
  "appRoleId": "{app-role-id}"
}
```

### Security Recommendations

- Restrict user consent to verified publishers + low-impact permissions
- Enable admin consent workflow for everything else
- Regularly review granted permissions (`Permissions` tab in Enterprise Apps)
- Permissions granted programmatically take effect immediately (no review gate)
- Always retrieve current `authorizationPolicy` before patching to avoid removing existing policies

---

## 7. Permission Classifications

### Overview

- Classify delegated permissions as "Low", "Medium" (preview), or "High" (preview)
- Only delegated permissions that don't require admin consent can be classified
- Used with consent policies: e.g., allow users to consent only to "Low" impact permissions
- Configured per-API (on the resource service principal)

### Minimum SSO Permissions (classify as Low)

- `openid` -- Required for OIDC
- `profile` -- User profile info
- `email` -- User email
- `offline_access` -- Refresh tokens
- `User.Read` -- Read signed-in user profile

### Graph API

```
# List classifications for Microsoft Graph
GET https://graph.microsoft.com/v1.0/servicePrincipals(appId='00000003-0000-0000-c000-000000000000')/delegatedPermissionClassifications

# Add a classification
POST https://graph.microsoft.com/v1.0/servicePrincipals(appId='00000003-0000-0000-c000-000000000000')/delegatedPermissionClassifications
{
  "permissionId": "{permission-guid}",
  "classification": "low"
}

# Remove a classification
DELETE https://graph.microsoft.com/v1.0/servicePrincipals(appId='...')/delegatedPermissionClassifications/{id}
```

### PowerShell

```powershell
Connect-MgGraph -Scopes "Policy.ReadWrite.PermissionGrant", "Application.Read.All"

# Get Microsoft Graph SP
$sp = Get-MgServicePrincipal -Filter "displayName eq 'Microsoft Graph'"

# List classifications
Get-MgServicePrincipalDelegatedPermissionClassification -ServicePrincipalId $sp.Id

# Add classification
$perm = $sp.Oauth2PermissionScopes | Where-Object { $_.Value -eq "openid" }
New-MgServicePrincipalDelegatedPermissionClassification -ServicePrincipalId $sp.Id -BodyParameter @{
  PermissionId = $perm.Id
  PermissionName = $perm.Value
  Classification = "Low"
}
```

---

## 8. User and Group Assignment

### Key Concepts

- Assignments control who can access the app (when `appRoleAssignmentRequired = true`)
- Each assignment maps a principal (user/group) to an app role
- Default app role ID: `00000000-0000-0000-0000-000000000000`
- Group-based assignment requires Entra ID P1/P2
- Nested group memberships NOT supported

### Graph API

```
# List app role assignments
GET https://graph.microsoft.com/v1.0/servicePrincipals/{sp-id}/appRoleAssignedTo

# Assign user to app
POST https://graph.microsoft.com/v1.0/servicePrincipals/{sp-id}/appRoleAssignedTo
{
  "principalId": "{user-or-group-id}",
  "resourceId": "{sp-id}",
  "appRoleId": "00000000-0000-0000-0000-000000000000"
}

# Remove assignment
DELETE https://graph.microsoft.com/v1.0/servicePrincipals/{sp-id}/appRoleAssignedTo/{assignment-id}
```

### PowerShell

```powershell
# Assign user
$params = @{
  PrincipalId = $userId
  ResourceId  = $sp.Id
  AppRoleId   = ($sp.AppRoles | Where-Object { $_.DisplayName -eq "Analyst" }).Id
}
New-MgUserAppRoleAssignment -UserId $userId -BodyParameter $params

# Assign group
New-MgGroupAppRoleAssignment -GroupId $groupId -BodyParameter $params

# Remove all assignments
$assignments = Get-MgServicePrincipalAppRoleAssignedTo -ServicePrincipalId $sp.Id -All
$assignments | ForEach-Object {
  Remove-MgServicePrincipalAppRoleAssignedTo -ServicePrincipalId $sp.Id -AppRoleAssignmentId $_.Id
}
```

---

## 9. Certificate Management

### SAML Signing Certificates

- Auto-generated: self-signed, 3-year validity
- Signing algorithm: SHA-256 (default), SHA-1 (legacy fallback)
- Can have multiple certs (Active + Inactive); only one active at a time
- Download formats: Raw (.cer), Base64, PEM, Federation Metadata XML

### Certificate Rotation Steps

1. Create new certificate (up to 3 years in future)
2. Save (status = Inactive)
3. Download in required format
4. Upload to application
5. Make certificate active in Entra
6. Remove old certificate

### SAML Token Encryption

- Requires Entra ID P1/P2
- Uses AES-256 to encrypt SAML assertions
- Public key (.cer) uploaded to Entra; private key held by the app
- Encryption cert stored in `keyCredentials` with `usage: "Encrypt"`
- Active encryption cert identified by `tokenEncryptionKeyId` on the application object

### Graph API

```
# Add token signing certificate
POST https://graph.microsoft.com/v1.0/servicePrincipals/{id}/addTokenSigningCertificate
{ "displayName": "CN=MyCert", "endDateTime": "2029-01-01T00:00:00Z" }

# Configure token encryption cert
PATCH https://graph.microsoft.com/beta/applications/{id}
{
  "keyCredentials": [{
    "type": "AsymmetricX509Cert",
    "usage": "Encrypt",
    "keyId": "{guid}",
    "key": "{base64-encoded-cert}"
  }],
  "tokenEncryptionKeyId": "{keyId-of-active-encryption-cert}"
}
```

### Expiration Notifications

- Sent at 60, 30, 7 days before expiry
- From: `azure-noreply@microsoft.com` (add to safe senders)
- Up to 5 email addresses configurable
- Use distribution lists for broader notification

---

## 10. Application Governance and Hygiene

### Reviewing Permissions

**Admin consent tab:** Shows permissions granted tenant-wide; can revoke in portal.
**User consent tab:** Shows per-user grants; revoke via Graph API or PowerShell only.

### Graph API for Permission Review

```
# List delegated permission grants for an app
GET https://graph.microsoft.com/v1.0/servicePrincipals/{id}/oauth2PermissionGrants

# Revoke delegated permissions
DELETE https://graph.microsoft.com/v1.0/oAuth2PermissionGrants/{grant-id}

# List application permissions (app role assignments where principal is a service principal)
GET https://graph.microsoft.com/v1.0/servicePrincipals/{id}/appRoleAssignments

# Revoke application permissions
DELETE https://graph.microsoft.com/v1.0/servicePrincipals/{resource-sp-id}/appRoleAssignedTo/{assignment-id}
```

### PowerShell for Revoking All Permissions

```powershell
Connect-MgGraph -Scopes "Application.ReadWrite.All", "DelegatedPermissionGrant.ReadWrite.All", "AppRoleAssignment.ReadWrite.All"

$sp = Get-MgServicePrincipal -ServicePrincipalId "{id}"

# Revoke all delegated permissions
Get-MgOauth2PermissionGrant -All | Where-Object { $_.ClientId -eq $sp.Id } | ForEach-Object {
  Remove-MgOauth2PermissionGrant -OAuth2PermissionGrantId $_.Id
}

# Revoke all application permissions
Get-MgServicePrincipalAppRoleAssignment -ServicePrincipalId $sp.Id -All |
  Where-Object { $_.PrincipalType -eq "ServicePrincipal" } | ForEach-Object {
  Remove-MgServicePrincipalAppRoleAssignedTo -ServicePrincipalId $sp.Id -AppRoleAssignmentId $_.Id
}
```

### Other Authorization Systems to Monitor

- Microsoft Entra built-in roles (RBAC)
- Exchange RBAC (Application RBAC)
- Teams resource-specific consent
- Revoking Entra permissions does not revoke these

### App Hygiene Practices

- Proactively monitor for ownerless applications (assign at least 2 owners)
- Review apps with no sign-in activity (unused apps)
- Audit apps with high-privilege permissions (Mail.ReadWrite, Files.ReadWrite.All, etc.)
- Revoke permissions for apps no longer in use
- Use app governance policies in Microsoft Defender for Cloud Apps

### Soft Delete and Recovery

- Deleted service principals go to recycle bin for 30 days
- Can be restored within 30 days
- After 30 days, permanently deleted
- Consider **deactivating** (`accountEnabled = false`) instead of deleting for investigation

---

## 11. Automation Quick Reference

### Graph API Permissions Required (by scenario)

| Scenario | Permissions |
|----------|------------|
| Read apps/SPs | `Application.Read.All` |
| Create/update/delete apps | `Application.ReadWrite.All` |
| Assign users/groups | `AppRoleAssignment.ReadWrite.All` |
| Grant delegated permissions | `DelegatedPermissionGrant.ReadWrite.All` |
| Grant app permissions | `AppRoleAssignment.ReadWrite.All` |
| Manage consent policies | `Policy.ReadWrite.PermissionGrant` |
| Manage authorization policy | `Policy.ReadWrite.Authorization` |
| Manage provisioning | `Synchronization.ReadWrite.All` |
| Read audit/sign-in logs | `AuditLog.Read.All`, `Directory.Read.All` |

### Key Graph Resource Types

| Resource | Endpoint | Description |
|----------|----------|-------------|
| `application` | `/applications` | App registrations |
| `servicePrincipal` | `/servicePrincipals` | Enterprise apps |
| `appRoleAssignment` | `/servicePrincipals/{id}/appRoleAssignedTo` | User/group/SP assignments |
| `oauth2PermissionGrant` | `/oauth2PermissionGrants` | Delegated permission grants |
| `applicationTemplate` | `/applicationTemplates` | Gallery app templates |
| `synchronizationJob` | `/servicePrincipals/{id}/synchronization/jobs` | Provisioning jobs |
| `delegatedPermissionClassification` | `/servicePrincipals/{id}/delegatedPermissionClassifications` | Permission classifications |
| `adminConsentRequestPolicy` | `/policies/adminConsentRequestPolicy` | Admin consent workflow config |
| `authorizationPolicy` | `/policies/authorizationPolicy` | Tenant-wide consent settings |
| `tokenIssuancePolicy` | `/policies/tokenIssuancePolicies` | SAML token policies |
| `tokenLifetimePolicy` | `/policies/tokenLifetimePolicies` | Token lifetime configuration |
| `claimsMappingPolicy` | `/policies/claimsMappingPolicies` | Claims customization |
| `homeRealmDiscoveryPolicy` | `/policies/homeRealmDiscoveryPolicies` | HRD configuration |

### PowerShell Module Matrix

| Module | Install | Use For |
|--------|---------|---------|
| Microsoft.Graph | `Install-Module Microsoft.Graph` | All Graph operations |
| Microsoft.Graph.Applications | (included) | App/SP CRUD |
| Microsoft.Graph.Identity.SignIns | (included) | Consent policies, permission grants |
| EntraExporter | `Install-Module EntraExporter` | Export tenant config for backup |

### az CLI (limited app management)

```bash
# List enterprise apps
az ad sp list --display-name "My App" --query "[].{id:id, appId:appId, displayName:displayName}"

# Create app registration
az ad app create --display-name "My App" --sign-in-audience "AzureADMyOrg"

# Create service principal for an app
az ad sp create --id {appId}

# Delete service principal
az ad sp delete --id {sp-object-id}

# Add password credential
az ad app credential reset --id {appId} --append

# Grant admin consent
az ad app permission admin-consent --id {appId}
```

---

## 12. Common Gotchas and Security Recommendations

### Gotchas

1. **Permissions granted programmatically take effect immediately** -- no review or confirmation prompt
2. **Patching authorizationPolicy can remove existing consent policies** -- always GET current state first
3. **Revoking consent does not prevent re-consent** -- disable user consent or disable the app to prevent
4. **Service principal deletion is soft** -- recoverable for 30 days, then permanent
5. **SAML SSO not available for multi-tenant apps** -- greyed out in portal
6. **OIDC apps registered via App Registrations** -- SSO blade does not appear under Enterprise Apps
7. **Group-based assignment requires P1/P2 license**
8. **Nested groups are NOT supported** for app role assignments
9. **Default AppRole ID is all zeros** (`00000000-0000-0000-0000-000000000000`) -- assigned when no specific role defined
10. **Certificate max lifetime is 3 years** for SAML signing certs

### Security Recommendations

1. **Restrict user consent** to verified publishers + low-impact permissions (`microsoft-user-default-low`)
2. **Enable admin consent workflow** so users can request access rather than being blocked
3. **Require user assignment** (`appRoleAssignmentRequired = true`) for sensitive apps
4. **Regularly review permissions** -- check for overprivileged apps quarterly
5. **Monitor sign-in and audit logs** for anomalous app behavior
6. **Use certificates over client secrets** for production apps
7. **Rotate SAML signing certs proactively** -- do not wait for expiration
8. **Assign at least 2 owners** to every enterprise app
9. **Use Conditional Access** for sensitive apps (require MFA, compliant device)
10. **Disable unused apps** (`accountEnabled = false`) rather than leaving them active

---

*Generated: 2026-03-23. Sources: learn.microsoft.com/en-us/entra/identity/enterprise-apps/*
