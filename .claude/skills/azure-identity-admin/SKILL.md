---
name: azure-identity-admin
description: Microsoft Identity and Access Administrator (SC-300) grounded skill. Covers Entra ID tenant management, user/group/device identities, hybrid identity, authentication methods (MFA, passkeys, FIDO2, certificate-based), Conditional Access, ID Protection, Global Secure Access, workload identities (managed identities, service principals, app registrations), enterprise app integration, identity governance (PIM, access reviews, entitlement management), and monitoring (KQL, workbooks, Identity Secure Score). Use when configuring Entra ID, managing authentication, setting up Conditional Access, implementing managed identities, reviewing access, or troubleshooting identity issues.
---

# Azure Identity and Access Administration (SC-300)

## When to Use
- Configuring Entra ID tenant settings, roles, or administrative units
- Managing users, groups, devices, or licenses
- Setting up authentication methods (MFA, passkeys, FIDO2, certificate-based)
- Creating or troubleshooting Conditional Access policies
- Implementing managed identities for Azure resources
- Configuring app registrations or enterprise app SSO
- Setting up PIM (Privileged Identity Management)
- Configuring identity governance (access reviews, entitlement management)
- Troubleshooting sign-in issues using logs and KQL
- Implementing hybrid identity (Entra Connect, Cloud Sync)

Triggers: SC-300, Entra ID, identity admin, Conditional Access, MFA, managed identity, service principal, app registration, PIM, access review, SSO, FIDO2, passkeys, hybrid identity, Entra Connect, identity governance, Identity Secure Score, Global Secure Access

## Domain 1: Implement and Manage User Identities (20-25%)

### Configure and Manage Entra Tenant
- **Built-in roles**: Global Admin, User Admin, Application Admin, Security Admin, Conditional Access Admin
- **Custom roles**: Create when built-in roles are too broad. Scope to administrative units for delegation
- **Administrative units**: Restrict admin scope to specific users/groups/devices. Use for delegated management (e.g., per-department admin)
- **Effective permissions**: Role assignments are additive. Check with `Get-MgRoleManagementDirectoryRoleAssignment`
- **Company branding**: Configure sign-in page branding per tenant and per language
- **Tenant settings**: User settings (guest access, app consent), group settings (naming policy, expiration), device settings (join/registration limits)

### Create and Manage Identities
- **Users**: Internal (member), External (guest), Synced (from AD DS)
- **Groups**: Security groups, Microsoft 365 groups, Dynamic membership rules
- **Custom security attributes**: Classify users/apps with custom metadata (e.g., department, cost center)
- **Bulk operations**: PowerShell (`New-MgUser`), CSV import, Microsoft Graph API
- **Device management**: Entra joined (cloud-only), Entra registered (BYOD), Hybrid joined (domain + Entra)
- **Licensing**: Direct assignment, Group-based licensing (recommended), License reconciliation

### External Users and Tenants
- **B2B collaboration**: Invite guests via email, bulk invite, self-service sign-up
- **Cross-tenant access**: Configure inbound/outbound trust settings per partner organization
- **Cross-tenant sync**: Sync users between Entra tenants (for multi-tenant organizations)
- **External identity providers**: SAML/WS-Fed federation, Google, Facebook (for B2C)

### Hybrid Identity
- **Entra Connect Sync**: Sync AD DS to Entra ID (users, groups, devices, passwords)
- **Entra Cloud Sync**: Lightweight agent-based sync (multi-forest, disconnected forests)
- **Password Hash Sync (PHS)**: Recommended — syncs password hashes to Entra ID
- **Pass-Through Auth (PTA)**: Validates passwords against on-prem AD in real-time
- **Seamless SSO**: Auto sign-in from domain-joined devices on corporate network
- **AD FS migration**: Move from ADFS to PHS+Seamless SSO or PTA (Microsoft recommended)

### IPAI Application
```
IPAI tenant: 402de71a-87ec-4302-a609-fb76098d1da7
Domain: insightpulseai.com

Users:
├── Jake Tolentino (Global Admin) — jake.tolentino@insightpulseai.com
├── admin@insightpulseai.com (Platform Admin)
└── W9 Studio users (Google Workspace — w9studio.net)

TBWA integration:
├── TBWA staff → Entra ID SSO (TBWA's own Omnicom tenant)
│   └── Cross-tenant access settings needed
├── TBWA clients → Entra External ID (B2C) for portal access
└── Odoo auth_oauth → configured for Entra ID
```

## Domain 2: Implement Authentication and Access Management (25-30%)

### Authentication Methods
- **MFA methods**: Microsoft Authenticator (push/passwordless), FIDO2 security keys, passkeys, SMS, voice, OATH tokens, certificate-based
- **Passwordless**: Passkeys (FIDO2), Windows Hello for Business, Microsoft Authenticator passwordless
- **Certificate-based auth (CBA)**: X.509 certificates against Entra ID — no ADFS needed
- **Temporary Access Pass (TAP)**: Time-limited passcode for onboarding or recovery
- **Self-service password reset (SSPR)**: Users reset own passwords, requires registration
- **Password protection**: Custom banned password lists, smart lockout

### Conditional Access
- **Assignments**: Users/groups, cloud apps, conditions (location, device, risk, client app)
- **Controls**: Grant (require MFA, compliant device, app protection), Session (sign-in frequency, persistent browser, app enforced restrictions)
- **Common policies**:
  - Require MFA for all users
  - Require MFA for admins
  - Block legacy authentication
  - Require compliant device for Office apps
  - Require MFA for Azure management
- **Named locations**: Define trusted IPs/countries for location-based conditions
- **Authentication context**: Tag sensitive actions (e.g., "require step-up auth for financial transactions")
- **Protected actions**: Require additional auth for admin operations

### ID Protection
- **User risk**: Leaked credentials, anomalous behavior → require password change or block
- **Sign-in risk**: Unfamiliar location, anonymous IP, impossible travel → require MFA or block
- **Risk remediation**: Self-remediation (MFA, password change) or admin-driven
- **Risky workload identities**: Monitor service principals for anomalous activity

### Global Secure Access
- **Private Access**: ZTNA replacement for VPN — access on-prem apps without VPN
- **Internet Access**: Secure web gateway for outbound internet traffic
- **Microsoft 365 Access**: Protect M365 traffic with identity-aware policies

### IPAI Application
```
Recommended Conditional Access policies for IPAI:
├── Require MFA for all admin accounts
├── Block legacy authentication protocols
├── Require MFA for Azure portal access
├── Require managed device for Odoo access (when Intune adopted)
└── Location-based: allow PH + TBWA office IPs only for admin operations

Odoo SSO flow:
  User → Entra ID login → MFA → Conditional Access evaluated →
  OAuth token issued → Odoo auth_oauth validates → session created
```

## Domain 3: Plan and Implement Workload Identities (20-25%)

### Application and Azure Workload Identities
- **Managed identities**: System-assigned (tied to resource lifecycle) or User-assigned (independent, reusable)
- **Service principals**: App identity in Entra ID — created automatically with app registration
- **When to use what**:
  - Managed identity: Azure resource → Azure resource (no credentials)
  - Service principal: External app → Azure resource (with secret or certificate)
  - User account: Never for automated workloads

### Enterprise Applications
- **SSO configuration**: SAML, OIDC, password-based, linked
- **User/group assignment**: Control who can access the app
- **Consent framework**: User consent vs admin consent, consent policies
- **Application Proxy**: Publish on-prem web apps externally without VPN
- **App collections**: Organize apps in My Apps portal

### App Registrations
- **Authentication**: Configure redirect URIs, platform settings, implicit/auth code flows
- **API permissions**: Delegated (on behalf of user) vs Application (daemon/service)
- **App roles**: Define custom roles for RBAC within your app
- **Secrets and certificates**: Manage client secrets (expire) and certificates (more secure)

### IPAI Application
```
IPAI managed identities (5 in rg-ipai-dev-security-sea):
├── id-ipai-dev          → platform runtime identity
├── id-ipai-dev-agent    → agent/Foundry identity
├── id-ipai-dev-data     → data plane identity
├── id-ipai-dev-pipeline → CI/CD pipeline identity
└── id-ipai-dev-runtime  → ACA runtime identity

App registrations needed:
├── "Odoo Login OAuth" → Entra SSO for Odoo (auth_oauth)
├── "Pulser Marketplace SaaS" → marketplace fulfillment
└── "Pulser M365 Agent" → M365 Copilot integration (Wave 2)

Each follows least-privilege: only permissions needed for specific function
```

## Domain 4: Plan and Automate Identity Governance (20-25%)

### Entitlement Management
- **Access packages**: Bundle resources (groups, apps, SharePoint sites) into requestable packages
- **Catalogs**: Organize access packages by department or project
- **Access requests**: Users request access, approvers review, time-limited access
- **Connected organizations**: Allow external organizations to request access packages
- **Terms of use**: Require acceptance before granting access

### Access Reviews
- **Purpose**: Periodically verify users still need access
- **Reviewers**: Self-review, manager, group owner, specific reviewers
- **Scope**: Group memberships, app assignments, Entra roles, Azure resource roles
- **Auto-apply**: Automatically remove access for non-responsive reviews

### Privileged Access (PIM)
- **Just-in-time access**: Activate roles only when needed (time-limited)
- **Approval workflow**: Require approval for sensitive role activation
- **Entra roles in PIM**: Global Admin, User Admin, etc. — eligible vs active
- **Azure resource roles**: Owner, Contributor — eligible vs active
- **PIM for Groups**: Apply JIT to security group membership
- **Break-glass accounts**: Emergency access accounts excluded from Conditional Access, monitored via alerts

### Monitoring
- **Sign-in logs**: Success/failure, MFA details, Conditional Access results, location
- **Audit logs**: Changes to directory objects (users, groups, apps, roles)
- **Provisioning logs**: App provisioning activity (SCIM)
- **Log Analytics**: Send logs to Log Analytics workspace for KQL queries
- **Workbooks**: Pre-built and custom dashboards for identity insights
- **Identity Secure Score**: Measure and improve identity security posture

### IPAI Application
```
Priority identity governance actions:
├── Enable PIM for Global Admin role (Jake only activates when needed)
├── Create break-glass account (emergency access, excluded from CA)
├── Configure sign-in log export to log-ipai-dev-sea (Log Analytics)
├── Set up access review for TBWA portal users (quarterly)
└── Monitor Identity Secure Score (target: >80%)

KQL example — failed sign-ins to Odoo:
SigninLogs
| where AppDisplayName == "Odoo Login OAuth"
| where ResultType != 0
| project TimeGenerated, UserPrincipalName, ResultType, ResultDescription,
          Location, DeviceDetail, ConditionalAccessStatus
| order by TimeGenerated desc
```

## Decision Trees

### Choose Authentication Method
```
Cloud-only users?
├── Yes → Password Hash Sync + MFA + Passwordless (passkeys/FIDO2)
└── No (hybrid) →
    ├── Can sync password hashes? → PHS + Seamless SSO + MFA
    └── Must validate on-prem? → Pass-Through Auth + MFA
```

### Choose Workload Identity
```
Azure resource calling Azure resource?
├── Yes → Managed Identity (system or user-assigned)
└── No →
    ├── External app/service? → Service Principal with certificate
    ├── CI/CD pipeline? → Workload Identity Federation (no secrets)
    └── Human user running scripts? → User identity with MFA
```

### Choose External Identity Approach
```
External users accessing your apps?
├── Business partners (B2B) → Entra External ID (B2B collaboration)
├── Customers/consumers (B2C) → Entra External ID (B2C/CIAM)
└── Multi-tenant org → Cross-tenant synchronization
```

## Reference
- SC-300 Study Guide: learn.microsoft.com/en-us/credentials/certifications/resources/study-guides/sc-300
- Entra ID Documentation: learn.microsoft.com/en-us/entra/identity/
- Practice Assessment: learn.microsoft.com/en-us/credentials/certifications/exams/sc-300/practice/assessment
- IPAI Identity Architecture: docs/architecture/identity-architecture.md
- IPAI Entra Governance Skill: .claude/skills/entra-identity-governance/
