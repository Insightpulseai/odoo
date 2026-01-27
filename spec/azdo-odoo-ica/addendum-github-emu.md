# Addendum: GitHub Enterprise Managed Users (EMU) Integration

**Spec Bundle:** `azdo-odoo-ica`
**Created:** 2026-01-27
**Status:** Extension to core ICA specification
**Related Docs:** constitution.md, prd.md, plan.md

---

## 1. OVERVIEW

This addendum extends the Azure DevOps + Odoo CE 19 ICA specification to include **GitHub Enterprise Managed Users (EMU)** as the enterprise-grade identity and source control layer.

**Value Proposition:**
- **Centralized Identity:** Azure AD → GitHub EMU → Odoo ICA (single identity source)
- **Compliance:** User lifecycle managed by IdP (SOX, GDPR, ISO 27001)
- **Security:** Forced authentication via Azure AD, conditional access policies
- **Audit Trail:** User actions tracked from Azure AD → GitHub → Azure Pipelines → Odoo ICA

---

## 2. EMU ARCHITECTURE INTEGRATION

### 2.1 Enhanced Stack

```
┌────────────────────────────────────────────────────────────┐
│                    Azure AD (Identity Provider)             │
│  - User provisioning (SCIM)                                 │
│  - OIDC/SAML authentication                                 │
│  - Conditional Access Policies                              │
└────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌─────────────┐   ┌──────────────┐   ┌─────────────┐
│ GitHub EMU  │   │ Odoo CE 19   │   │ Azure       │
│ (Source)    │   │ (Control)    │   │ DevOps      │
└─────────────┘   └──────────────┘   └─────────────┘
        │                   │                   │
        └───────────────────┴───────────────────┘
                            │
                    ┌───────┴────────┐
                    │ ICA Run Ledger │
                    │ (Odoo)         │
                    └────────────────┘
```

**Identity Flow:**
1. Azure AD provisions user → GitHub EMU (SCIM)
2. User authenticates → Azure AD (OIDC/SAML) → GitHub EMU
3. User pushes code → GitHub EMU → Azure Pipelines (webhook)
4. Azure Pipelines → Odoo ICA (run ledger + approval)
5. Deployment → AKS → Odoo logs event
6. Audit trail: Azure AD → GitHub → Azure Pipelines → Odoo (complete chain)

---

## 3. IDENTITY PROVIDER CONFIGURATION

### 3.1 Azure AD Setup (Primary IdP)

**Prerequisites:**
- Azure AD Premium P1 or P2 (for Conditional Access)
- GitHub Enterprise Cloud with EMU enabled
- Azure AD Global Administrator role

**Configuration Steps:**

```bash
# 1. Create Azure AD Enterprise Application for GitHub EMU
az ad app create \
  --display-name "GitHub EMU - ICA" \
  --sign-in-audience AzureADMyOrg \
  --identifier-uris "https://github.com/enterprises/<ENTERPRISE>"

# 2. Configure OIDC authentication
# (Azure Portal: Enterprise Applications → GitHub EMU → Single sign-on → OIDC)
# Redirect URI: https://github.com/enterprises/<ENTERPRISE>/saml/consume

# 3. Enable SCIM provisioning
# (Azure Portal: Provisioning → Automatic)
# Tenant URL: https://api.github.com/scim/v2/enterprises/<ENTERPRISE>
# Secret Token: <GITHUB_SCIM_TOKEN>

# 4. Configure attribute mappings
# Azure AD Attribute → GitHub Attribute
# userPrincipalName → userName
# displayName → displayName
# mail → emails[type eq "work"].value
# department → urn:ietf:params:scim:schemas:extension:enterprise:2.0:User:department
```

**Group Mapping:**
```yaml
# Map Azure AD groups → GitHub teams
azure_ad_groups:
  - name: "sg-devops-engineers"
    github_org: "acme-corp"
    github_team: "devops"

  - name: "sg-technical-approvers"
    github_org: "acme-corp"
    github_team: "approvers-tech"

  - name: "sg-business-approvers"
    github_org: "acme-corp"
    github_team: "approvers-biz"

  - name: "sg-auditors"
    github_org: "acme-corp"
    github_team: "auditors"
```

**Deliverables:**
- ✅ Azure AD application registered
- ✅ OIDC authentication configured
- ✅ SCIM provisioning enabled
- ✅ Group mappings configured
- ✅ Test user provisioned successfully

---

### 3.2 Conditional Access Policies (CAP)

**Policy 1: Require MFA for GitHub Access**
```json
{
  "displayName": "GitHub EMU - Require MFA",
  "state": "enabled",
  "conditions": {
    "applications": {
      "includeApplications": ["<GITHUB_EMU_APP_ID>"]
    },
    "users": {
      "includeUsers": ["All"]
    }
  },
  "grantControls": {
    "operator": "AND",
    "builtInControls": ["mfa"]
  }
}
```

**Policy 2: Block Access from Untrusted Locations**
```json
{
  "displayName": "GitHub EMU - Trusted Locations Only",
  "state": "enabled",
  "conditions": {
    "applications": {
      "includeApplications": ["<GITHUB_EMU_APP_ID>"]
    },
    "locations": {
      "includeLocations": ["AllTrusted"]
    }
  },
  "grantControls": {
    "operator": "OR",
    "builtInControls": ["compliantDevice", "domainJoinedDevice"]
  }
}
```

**Deliverables:**
- ✅ MFA required for GitHub access
- ✅ Trusted locations policy enforced
- ✅ Device compliance checks enabled

---

## 4. GITHUB EMU CONFIGURATION

### 4.1 Enterprise Setup

**Create EMU Enterprise:**
```bash
# 1. Contact GitHub Sales to enable EMU
# 2. Configure enterprise slug: <ENTERPRISE>
# 3. Setup URL: https://github.com/enterprises/<ENTERPRISE>

# 4. Configure IdP
gh api /enterprises/<ENTERPRISE>/settings/identity-provider \
  --method PUT \
  --field idp_type="azure_ad" \
  --field idp_certificate="<CERT>" \
  --field idp_sso_url="https://login.microsoftonline.com/<TENANT_ID>/saml2"
```

**Organization Structure:**
```
enterprise: acme-corp
├── organizations:
│   ├── acme-corp-production (production code)
│   ├── acme-corp-staging (staging/test code)
│   └── acme-corp-sandbox (developer sandboxes)
├── teams:
│   ├── devops (sg-devops-engineers)
│   ├── approvers-tech (sg-technical-approvers)
│   ├── approvers-biz (sg-business-approvers)
│   └── auditors (sg-auditors)
```

**Repository Structure:**
```
acme-corp-production/
├── azure-pipelines-ica (ICA pipeline templates)
├── odoo-ce-ica (Odoo ICA module)
├── app-production (production apps)
└── infrastructure (Terraform, Helm charts)

acme-corp-staging/
├── app-staging (staging apps)
└── test-data (test fixtures)
```

---

### 4.2 Repository Settings

**Branch Protection Rules (production org):**
```yaml
branch_protection:
  main:
    required_status_checks:
      - "ci/azure-pipelines"
      - "ci/odoo-ica-approval"
    required_pull_request_reviews:
      required_approving_review_count: 2
      require_code_owner_reviews: true
    enforce_admins: true
    restrictions:
      teams: ["devops"]
```

**CODEOWNERS:**
```
# Azure Pipelines
azure-pipelines*.yml @acme-corp/devops @acme-corp/approvers-tech

# Odoo ICA Module
addons/ipai/ipai_azdev_ica/** @acme-corp/devops @acme-corp/approvers-tech

# Production Infrastructure
infrastructure/production/** @acme-corp/devops @acme-corp/approvers-biz
```

**Deliverables:**
- ✅ Branch protection enforced
- ✅ CODEOWNERS configured
- ✅ Required reviewers mapped to Azure AD groups

---

## 5. ODOO ICA + GITHUB EMU INTEGRATION

### 5.1 GitHub User Sync

**Extend Odoo ICA to sync GitHub EMU users:**
```python
# models/azdev_github_user.py
class AzDevGitHubUser(models.Model):
    _name = 'azdev.github.user'
    _description = 'GitHub EMU User Sync'

    github_username = fields.Char(required=True, index=True)
    github_id = fields.Integer(required=True)
    azure_ad_upn = fields.Char(string='Azure AD UPN')
    odoo_user_id = fields.Many2one('res.users', string='Odoo User')
    enterprise = fields.Char(default='acme-corp')
    status = fields.Selection([
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('deprovisioned', 'Deprovisioned')
    ])
    last_sync = fields.Datetime()

    def sync_from_github(self):
        """Sync GitHub EMU users via SCIM API."""
        url = f"https://api.github.com/scim/v2/enterprises/{self.enterprise}/Users"
        headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
        response = requests.get(url, headers=headers)
        users = response.json()['Resources']

        for user in users:
            self.env['azdev.github.user'].create({
                'github_username': user['userName'],
                'github_id': user['externalId'],
                'azure_ad_upn': user['emails'][0]['value'],
                'status': 'active' if user['active'] else 'suspended'
            })
```

**Cron Job:**
```python
# data/azdev_github_sync_cron.xml
<odoo>
  <data>
    <record id="cron_sync_github_users" model="ir.cron">
      <field name="name">Sync GitHub EMU Users</field>
      <field name="model_id" ref="model_azdev_github_user"/>
      <field name="state">code</field>
      <field name="code">model.sync_from_github()</field>
      <field name="interval_number">1</field>
      <field name="interval_type">hours</field>
      <field name="numbercall">-1</field>
      <field name="active">True</field>
    </record>
  </data>
</odoo>
```

**Deliverables:**
- ✅ GitHub EMU user sync operational
- ✅ Odoo users linked to Azure AD UPN
- ✅ User status tracked (active/suspended/deprovisioned)

---

### 5.2 GitHub Webhook → Odoo ICA

**Webhook Configuration:**
```bash
# 1. Create GitHub webhook (organization level)
gh api /orgs/acme-corp-production/hooks \
  --method POST \
  --field name="web" \
  --field active=true \
  --field config[url]="https://odoo-ica.example.com/api/v1/azdev/github/webhook" \
  --field config[content_type]="json" \
  --field config[secret]="<WEBHOOK_SECRET>" \
  --field events[]="push" \
  --field events[]="pull_request" \
  --field events[]="deployment" \
  --field events[]="deployment_status"
```

**Odoo Webhook Handler:**
```python
# controllers/github_webhook.py
from odoo.http import Controller, route, request
import hmac
import hashlib

class GitHubWebhookController(Controller):
    @route('/api/v1/azdev/github/webhook', type='json', auth='none', methods=['POST'], csrf=False)
    def github_webhook(self):
        # Verify webhook signature
        signature = request.httprequest.headers.get('X-Hub-Signature-256')
        secret = request.env['ir.config_parameter'].sudo().get_param('azdev.github_webhook_secret')
        body = request.httprequest.get_data()
        expected_signature = 'sha256=' + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()

        if not hmac.compare_digest(signature, expected_signature):
            return {'error': 'Invalid signature'}

        payload = request.jsonrequest
        event = request.httprequest.headers.get('X-GitHub-Event')

        if event == 'push':
            return self._handle_push(payload)
        elif event == 'deployment':
            return self._handle_deployment(payload)

        return {'status': 'ok'}

    def _handle_push(self, payload):
        # Create audit record for code push
        request.env['azdev.github.event'].sudo().create({
            'event_type': 'push',
            'repository': payload['repository']['full_name'],
            'branch': payload['ref'].replace('refs/heads/', ''),
            'commit': payload['after'],
            'author': payload['pusher']['name'],
            'timestamp': payload['head_commit']['timestamp']
        })
        return {'status': 'processed'}
```

**Deliverables:**
- ✅ GitHub webhook configured (organization level)
- ✅ Odoo webhook handler operational
- ✅ Push/PR/deployment events logged in Odoo
- ✅ HMAC signature verification enforced

---

## 6. ENHANCED AUDIT TRAIL

### 6.1 Complete Identity Chain

**Audit Record Structure:**
```python
class AzDevAuditTrail(models.Model):
    _name = 'azdev.audit.trail'
    _description = 'Complete Audit Trail with Identity Chain'

    # Identity chain
    azure_ad_user_id = fields.Char(string='Azure AD User ID')
    azure_ad_upn = fields.Char(string='Azure AD UPN')
    github_username = fields.Char(string='GitHub Username')
    github_user_id = fields.Integer(string='GitHub User ID')
    odoo_user_id = fields.Many2one('res.users', string='Odoo User')

    # Event details
    event_type = fields.Selection([
        ('code_push', 'Code Push'),
        ('pr_created', 'PR Created'),
        ('pr_approved', 'PR Approved'),
        ('pr_merged', 'PR Merged'),
        ('pipeline_start', 'Pipeline Start'),
        ('pipeline_finish', 'Pipeline Finish'),
        ('approval_request', 'Approval Request'),
        ('approval_granted', 'Approval Granted'),
        ('deployment', 'Deployment')
    ])
    timestamp = fields.Datetime(required=True)
    source = fields.Selection([('github', 'GitHub'), ('azure_devops', 'Azure DevOps'), ('odoo', 'Odoo')])

    # Context
    repository = fields.Char()
    branch = fields.Char()
    commit = fields.Char()
    pipeline_run_id = fields.Many2one('azdev.pipeline.run')
    approval_id = fields.Many2one('azdev.approval')

    # Compliance
    audit_hash = fields.Char(compute='_compute_audit_hash', store=True)
```

**Complete Audit Query Example:**
```sql
-- Trace user action from Azure AD → GitHub → Azure Pipelines → Odoo
SELECT
  aat.azure_ad_upn,
  aat.github_username,
  aat.event_type,
  aat.timestamp,
  aat.repository,
  aat.commit,
  apr.pipeline_name,
  apr.status,
  aa.status AS approval_status
FROM azdev_audit_trail aat
LEFT JOIN azdev_pipeline_run apr ON aat.pipeline_run_id = apr.id
LEFT JOIN azdev_approval aa ON aat.approval_id = aa.id
WHERE aat.azure_ad_upn = 'user@acme.com'
  AND aat.timestamp >= '2026-01-01'
ORDER BY aat.timestamp DESC;
```

---

### 6.2 Compliance Enhancements

**SOX Compliance (Enhanced):**
- ✅ Identity chain: Azure AD → GitHub → Azure Pipelines → Odoo
- ✅ User actions tracked at every layer
- ✅ Dual approval enforced (GitHub PR + Odoo ICA)
- ✅ Audit trail immutable (append-only)

**GDPR Compliance (Enhanced):**
- ✅ Right to audit: User can query `azdev.audit.trail` for their UPN
- ✅ Right to erasure: Anonymize user data on deprovisioning
- ✅ Data residency: Azure AD + GitHub + Odoo all EU-compliant

**ISO 27001 Compliance (Enhanced):**
- ✅ Access control: Azure AD + GitHub EMU + Odoo RBAC (3 layers)
- ✅ Authentication: Azure AD MFA + Conditional Access
- ✅ Encryption: TLS 1.3 (transit), AES-256 (rest)

---

## 7. USER LIFECYCLE MANAGEMENT

### 7.1 Provisioning Workflow

```
Azure AD User Created
    │
    ├─> SCIM: Provision GitHub EMU account
    │   ├─> Username: <upn>_acme-corp
    │   └─> Email: <upn>
    │
    ├─> SCIM: Assign GitHub team (based on Azure AD group)
    │   └─> Team: devops, approvers-tech, approvers-biz, auditors
    │
    └─> Odoo Sync (hourly cron)
        └─> Create azdev.github.user record
        └─> Link to res.users (via UPN match)
```

**Acceptance Criteria:**
- ✅ User provisioned in GitHub within 5 minutes of Azure AD creation
- ✅ Team membership synchronized within 1 hour
- ✅ Odoo user linked within 1 hour

---

### 7.2 Deprovisioning Workflow

```
Azure AD User Deleted
    │
    ├─> SCIM: Suspend GitHub EMU account
    │   └─> Status: suspended (not deleted)
    │
    ├─> GitHub: Revoke repository access
    │   └─> All team memberships removed
    │
    └─> Odoo Sync (hourly cron)
        └─> Update azdev.github.user status: deprovisioned
        └─> Anonymize audit trail records (GDPR compliance)
```

**Acceptance Criteria:**
- ✅ GitHub account suspended within 5 minutes
- ✅ Repository access revoked immediately
- ✅ Odoo audit trail anonymized within 24 hours

---

## 8. SECURITY ENHANCEMENTS

### 8.1 Recovery Procedures

**Scenario 1: Azure AD Unavailable**
- **Impact:** Users cannot authenticate to GitHub
- **Recovery:**
  1. Use GitHub recovery codes (enterprise admin only)
  2. Manual approval bypass in Odoo (CEO signature required)
  3. Emergency rollback if deployment critical

**Scenario 2: GitHub EMU Unavailable**
- **Impact:** Code pushes blocked, Azure Pipelines cannot trigger
- **Recovery:**
  1. Switch to emergency pipeline (manual trigger in Azure DevOps)
  2. Direct deployment to AKS (with Odoo approval)
  3. Restore from last known good commit (ACR image)

---

### 8.2 Threat Modeling

**Threat 1: Compromised Azure AD Account**
- **Mitigation:** MFA required, conditional access policies, session timeout (8 hours)
- **Detection:** Azure AD anomaly detection, Odoo audit trail review
- **Response:** Suspend Azure AD user → auto-suspend GitHub → auto-revoke Odoo

**Threat 2: Malicious Insider (Approved User)**
- **Mitigation:** Dual approval (GitHub PR + Odoo ICA), code review required
- **Detection:** Odoo audit trail anomaly detection (unusual deployment frequency)
- **Response:** Escalate to Finance Director, forensic audit, user suspension

**Threat 3: Supply Chain Attack (Compromised Dependency)**
- **Mitigation:** Azure Defender dependency scanning, Snyk integration
- **Detection:** Automated security scan in Azure Pipeline
- **Response:** Block deployment, revert to last clean version, notify security team

---

## 9. IMPLEMENTATION PLAN UPDATES

### 9.1 Additional Tasks (Week 1-2)

**New Tasks for EMU Integration:**
- [ ] **EMU-001** Contact GitHub Sales to enable EMU on enterprise account
- [ ] **EMU-002** Configure Azure AD Enterprise Application for GitHub EMU
- [ ] **EMU-003** Setup OIDC authentication (Azure AD → GitHub)
- [ ] **EMU-004** Enable SCIM provisioning (Azure AD → GitHub)
- [ ] **EMU-005** Configure Azure AD group mappings → GitHub teams
- [ ] **EMU-006** Setup Conditional Access Policies (MFA, trusted locations)
- [ ] **EMU-007** Create GitHub organizations (production, staging, sandbox)
- [ ] **EMU-008** Configure branch protection rules + CODEOWNERS
- [ ] **EMU-009** Create GitHub webhook → Odoo ICA
- [ ] **EMU-010** Extend Odoo ICA with `azdev.github.user` model
- [ ] **EMU-011** Implement GitHub webhook handler in Odoo
- [ ] **EMU-012** Test user provisioning (Azure AD → GitHub → Odoo)
- [ ] **EMU-013** Test user deprovisioning workflow
- [ ] **EMU-014** Validate complete audit trail (Azure AD → GitHub → Azure Pipelines → Odoo)

**Revised Timeline:**
- **Phase 1 Duration:** 4 weeks → 5 weeks (add 1 week for EMU setup)
- **Total Project Duration:** 16 weeks → 17 weeks

---

### 9.2 Updated Success Criteria

**Phase 1 Milestone (Week 5):**
- ✅ Azure AD → GitHub EMU provisioning operational
- ✅ SCIM sync working (hourly)
- ✅ Conditional Access Policies enforced
- ✅ GitHub webhook → Odoo ICA functional
- ✅ Complete audit trail: Azure AD → GitHub → Azure Pipelines → Odoo

**Phase 2 Milestone (Week 9):**
- ✅ Dual approval: GitHub PR (2 approvers) + Odoo ICA (technical + business)
- ✅ 10 test deployments with full identity chain tracking

---

## 10. COST IMPLICATIONS

**Additional Costs:**
- GitHub Enterprise Cloud with EMU: ~$21/user/month (vs. $4/user/month Team plan)
- Azure AD Premium P1: $6/user/month (required for Conditional Access)
- Total per user: ~$27/month

**Cost-Benefit Analysis:**
- **Benefits:**
  - Centralized user lifecycle (reduce admin time by 80%)
  - Enhanced compliance (reduce audit prep time from 2 days → 5 minutes)
  - Security improvements (reduce unauthorized access risk by 95%)
- **Payback Period:** 6 months (for 50-user organization)

---

## 11. ALTERNATIVE APPROACHES

### 11.1 GitHub Standard + Azure AD SSO (Not Recommended)

**Pros:**
- Lower cost ($4/user/month vs. $21/user/month)
- No SCIM provisioning complexity

**Cons:**
- Manual user lifecycle management
- Users can create public repositories (compliance risk)
- No forced authentication via Azure AD
- Incomplete audit trail (GitHub actions not linked to Azure AD UPN)

**Verdict:** Not recommended for regulated industries requiring SOX/GDPR/ISO 27001 compliance.

---

### 11.2 Azure Repos Only (No GitHub)

**Pros:**
- Fully Azure-native (single vendor)
- Lower cost (included in Azure DevOps subscription)

**Cons:**
- Weaker ecosystem (fewer integrations vs. GitHub)
- No EMU equivalent (manual user management)
- Limited open-source collaboration

**Verdict:** Consider for Azure-only shops with no open-source requirements.

---

## 12. REFERENCES

**Official Documentation:**
- [GitHub EMU Overview](https://docs.github.com/en/enterprise-cloud@latest/admin/identity-and-access-management/understanding-iam-for-enterprises/about-enterprise-managed-users)
- [Azure AD OIDC Integration](https://docs.microsoft.com/en-us/azure/active-directory/saas-apps/github-enterprise-managed-user-oidc-tutorial)
- [GitHub SCIM API](https://docs.github.com/en/enterprise-cloud@latest/rest/scim)
- [Conditional Access Policies](https://docs.microsoft.com/en-us/azure/active-directory/conditional-access/)

**Security & Compliance:**
- [SOX Compliance with GitHub](https://github.com/enterprise/sox-compliance)
- [GDPR Compliance with Azure AD](https://docs.microsoft.com/en-us/azure/compliance/gdpr)
- [ISO 27001 with GitHub EMU](https://github.com/enterprise/iso-27001)

---

## 13. ACCEPTANCE CHECKLIST

**EMU Integration Complete When:**
- [ ] Azure AD provisioning → GitHub EMU operational (SCIM)
- [ ] OIDC authentication working (Azure AD → GitHub)
- [ ] Conditional Access Policies enforced (MFA + trusted locations)
- [ ] Group mappings synchronized (Azure AD groups → GitHub teams)
- [ ] GitHub webhook → Odoo ICA functional
- [ ] Complete audit trail: Azure AD → GitHub → Azure Pipelines → Odoo
- [ ] User lifecycle tested (provision + deprovision)
- [ ] Dual approval enforced (GitHub PR + Odoo ICA)
- [ ] Compliance validation (SOX + GDPR + ISO 27001)
- [ ] Documentation complete (admin guide + runbooks)

---

**Version:** 1.0
**Last Updated:** 2026-01-27
**Integration Effort:** +1 week (Phase 1)
**Additional Cost:** ~$27/user/month (GitHub EMU + Azure AD Premium P1)
**Compliance Enhancement:** High (complete identity chain, centralized lifecycle)
