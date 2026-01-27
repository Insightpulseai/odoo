# Constitution: Azure DevOps + Odoo CE 19 ICA Integration

**Spec Bundle:** `azdo-odoo-ica`
**Created:** 2026-01-27
**Status:** Draft
**Scope:** Internal Control Architecture (ICA) for Azure-native SDLC with Odoo CE 19 control plane

---

## 1. NON-NEGOTIABLE RULES

### 1.1 Control Plane Authority

**RULE:** Odoo CE 19 + OCA is the **authoritative control plane** for all Azure DevOps deployments.

**Enforcement:**
- No deployment proceeds without ICA approval record in Odoo
- All Azure Pipeline runs logged to Odoo run ledger
- RBAC enforced via Odoo roles (not Azure AD groups alone)
- Audit trail immutable (append-only ledger in Odoo)

**Rationale:** Regulated industries (finance, healthcare, government) require audit trails that survive cloud vendor churn. Odoo provides vendor-neutral compliance layer.

---

### 1.2 Azure-Native SDLC Stack

**RULE:** Use Azure-native services where they exist; Odoo integrates via APIs.

**Stack:**
- **Source Control:** GitHub Enterprise (Azure-integrated) OR Azure Repos
- **CI/CD:** Azure Pipelines (primary) + GitHub Actions (optional)
- **Container Registry:** Azure Container Registry (ACR)
- **Compute:** Azure Kubernetes Service (AKS) OR Azure Container Apps
- **Identity:** Azure AD + Managed Identities + OIDC
- **Monitoring:** Azure Monitor + Application Insights
- **Control Plane:** Odoo CE 19 + OCA modules

**Prohibited:**
- Hardcoded credentials (use Azure Key Vault + Managed Identity)
- Direct Azure CLI in pipelines (wrap in ICA-aware scripts)
- Bypassing Odoo approval gates (no emergency "skip approval" flags)

---

### 1.3 Run Ledger Completeness

**RULE:** Every Azure Pipeline run writes to Odoo run ledger at 3 phases:

1. **Start:** `POST /api/azdev/run/start` → Creates `azdev.pipeline.run` record
2. **Events:** `POST /api/azdev/run/event` → Appends phase markers (build, test, deploy)
3. **Finish:** `POST /api/azdev/run/finish` → Closes run with status (success/failed/cancelled)

**Ledger Schema (Odoo model):**
```python
class AzDevPipelineRun(models.Model):
    _name = 'azdev.pipeline.run'
    _description = 'Azure DevOps Pipeline Run Ledger'

    pipeline_name = fields.Char(required=True)
    run_id = fields.Char(required=True, index=True)  # Azure Build.BuildId
    branch = fields.Char()
    commit = fields.Char()
    status = fields.Selection([
        ('running', 'Running'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled')
    ])
    start_time = fields.Datetime(required=True)
    end_time = fields.Datetime()
    events = fields.One2many('azdev.pipeline.event', 'run_id')
    approval_id = fields.Many2one('azdev.approval', string='Approval Record')
```

**Enforcement:** Azure Pipelines template mandates ledger hooks (no bypass).

---

### 1.4 Approval Gates

**RULE:** Production deployments require **dual approval** via Odoo ICA:

1. **Technical Approval:** DevOps engineer confirms deployment readiness
2. **Business Approval:** Finance Director (for cost impact) OR Compliance Officer (for regulatory)

**Approval Workflow:**
```
Pipeline reaches pre-prod → Creates azdev.approval record → Status: pending
→ Technical approver reviews → Signs via Odoo → Status: technical_approved
→ Business approver reviews → Signs via Odoo → Status: approved
→ Pipeline polls /api/azdev/approval/<id> → Proceeds if approved=true
```

**Timeout:** 4-hour approval SLA (escalate to Finance Director if expired).

**Enforcement:** Azure Pipeline stage gates check Odoo approval API before deploy steps.

---

### 1.5 Immutable Audit Trail

**RULE:** All ICA actions append-only; no deletions, no edits.

**Actions Logged:**
- Pipeline run start/end
- Approval requests
- Approval signatures (technical + business)
- Deployment events (Azure → production namespace)
- Rollback events
- Emergency overrides (require CEO signature)

**Retention:** 7 years (regulatory compliance: SOX, GDPR, BIR).

**Storage:** Odoo PostgreSQL (primary) + Azure Blob archival (yearly snapshots).

---

## 2. SECURITY CONSTRAINTS

### 2.1 Identity & Access

**Azure AD Integration:**
- Odoo users federated via Azure AD SSO (SAML 2.0 OR OAuth2)
- Azure Managed Identity authenticates pipelines → Odoo API
- No service account passwords (Azure Key Vault + Managed Identity only)

**RBAC Matrix:**
| Role | Odoo Group | Azure AD Group | Permissions |
|------|------------|----------------|-------------|
| DevOps Engineer | `azdev_devops` | `sg-devops-engineers` | Run pipelines, request approvals |
| Technical Approver | `azdev_approver_tech` | `sg-technical-approvers` | Approve technical changes |
| Business Approver | `azdev_approver_biz` | `sg-business-approvers` | Approve cost/compliance impact |
| Auditor | `azdev_auditor` | `sg-auditors` | Read-only access to run ledger |
| Admin | `base.group_system` | `sg-ica-admins` | Configure ICA, emergency overrides |

**Enforcement:** Odoo RLS policies + Azure AD Conditional Access.

---

### 2.2 Network Security

**Required:**
- Odoo API exposed via Azure Front Door (WAF enabled)
- ACR behind Azure Private Link (no public pull)
- AKS cluster private endpoint (no public Kubernetes API)
- Azure Pipelines agents in Azure VNET (managed identities)

**Prohibited:**
- Public IP on Odoo instance
- Unencrypted traffic (TLS 1.3 minimum)
- Shared credentials across environments

---

## 3. ARCHITECTURAL CONSTRAINTS

### 3.1 Deployment Topology

**Reference Architecture:**
```
┌────────────────────────────────────────────────────────────┐
│                 Azure Subscription                          │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐      ┌──────────────┐                   │
│  │ GitHub Repos │◄────►│ Azure Repos  │ (optional)         │
│  └──────────────┘      └──────────────┘                   │
│         │                      │                            │
│         └──────────┬───────────┘                            │
│                    ▼                                        │
│         ┌─────────────────────┐                            │
│         │ Azure Pipelines     │                            │
│         │ (CI/CD Orchestrator)│                            │
│         └─────────────────────┘                            │
│                    │                                        │
│      ┌─────────────┼─────────────┐                        │
│      ▼             ▼             ▼                         │
│  ┌─────┐      ┌─────┐      ┌─────────┐                   │
│  │ ACR │      │ AKS │      │ Odoo CE │ (Control Plane)    │
│  └─────┘      └─────┘      │ 19 + ICA│                    │
│                             └─────────┘                    │
│                                  │                          │
│                             ┌────┴────┐                    │
│                             │ Postgres│                    │
│                             │ 15 DB   │                    │
│                             └─────────┘                    │
└────────────────────────────────────────────────────────────┘
```

**Constraints:**
- Odoo CE 19 runs in AKS (HA mode: 2+ replicas)
- Postgres 15 via Azure Database for PostgreSQL (Flexible Server)
- ACR replication across 2+ regions (DR requirement)
- Azure Front Door → Odoo (global load balancing)

---

### 3.2 API Contract

**Odoo ICA API Endpoints (mandatory):**

| Endpoint | Method | Purpose | Auth |
|----------|--------|---------|------|
| `/api/azdev/run/start` | POST | Create run ledger entry | Bearer token (Managed Identity) |
| `/api/azdev/run/event` | POST | Append phase event | Bearer token |
| `/api/azdev/run/finish` | POST | Close run ledger | Bearer token |
| `/api/azdev/approval/<id>` | GET | Poll approval status | Bearer token |
| `/api/azdev/approval/<id>/sign` | POST | Submit approval signature | OAuth2 user token |
| `/api/azdev/audit/query` | POST | Query audit trail | OAuth2 user token + auditor role |

**API Spec:** OpenAPI 3.1 schema in `api/azdev-ica-openapi.yaml`

**Versioning:** `/api/v1/azdev/*` (v2 when breaking changes)

---

## 4. COMPLIANCE REQUIREMENTS

### 4.1 Regulatory Frameworks

**Applicable Standards:**
- **SOX (Sarbanes-Oxley):** Audit trail completeness, dual approval, immutable logs
- **GDPR (EU):** Data retention policies, audit log encryption, right to audit
- **BIR (Philippines):** 7-year retention, tamper-proof audit trails
- **ISO 27001:** Access control, encryption, incident response

**Evidence Requirements:**
- Annual audit export: `odoo.cli azdev-audit-export --year 2026`
- Monthly compliance report: `azdev.audit.monthly.report` Odoo automated action
- Quarterly DR drill: Restore Odoo ICA from Azure Blob backup

---

### 4.2 Data Retention

| Data Type | Retention Period | Storage Location | Archive Medium |
|-----------|------------------|------------------|----------------|
| Run ledger | 7 years | Postgres (Odoo) | Azure Blob (yearly snapshots) |
| Approval signatures | 7 years | Postgres (Odoo) | Azure Blob |
| Audit trail | 7 years | Postgres + Azure Monitor | Azure Archive Storage |
| Pipeline logs | 2 years | Azure Pipelines | Azure Log Analytics |

**Enforcement:** Odoo scheduled action: `archive_old_runs` (monthly cron).

---

## 5. QUALITY GATES

### 5.1 Pre-Deployment Checklist

**Azure Pipeline must pass:**
- ✅ Build successful (ACR image pushed)
- ✅ Unit tests ≥80% coverage
- ✅ Security scan (Azure Defender for Containers) passes
- ✅ Odoo run ledger entry created
- ✅ Odoo approval received (technical + business)

**Odoo ICA validates:**
- ✅ Deployment target matches approval scope (e.g., production namespace)
- ✅ No concurrent deployments (deployment lock in Odoo)
- ✅ Cost impact ≤ approved budget threshold
- ✅ Compliance check (no unapproved dependencies)

**Enforcement:** Azure Pipeline template + Odoo API validation.

---

### 5.2 Post-Deployment Verification

**Automatic Checks:**
1. Kubernetes health check: `kubectl get pods -n production`
2. Smoke test: `curl https://odoo.example.com/web/health`
3. Azure Monitor alert: No critical errors in 5 minutes
4. Odoo run ledger: Status updated to `success`

**Manual Verification (optional):**
- Business stakeholder UAT within 24 hours
- Rollback if UAT fails (tracked in Odoo)

---

## 6. FAILURE & ROLLBACK

### 6.1 Rollback Triggers

**Automatic:**
- Azure Monitor critical alert (5xx errors >5%)
- Kubernetes pod crash loop (3 consecutive failures)
- Odoo API unreachable (control plane outage)

**Manual:**
- Business approver requests rollback via Odoo
- CEO emergency override (requires CEO signature in Odoo)

**Rollback Procedure:**
```bash
# 1. Tag last good commit
git tag rollback/$(date +%Y%m%d-%H%M%S)

# 2. Revert Azure Pipeline to last good deployment
az pipelines run --name <PIPELINE> --branch rollback/<TAG>

# 3. Log rollback in Odoo
curl -X POST "$ODOO_API_RUN_EVENT" \
  -d '{"run_id":"<RUN_ID>","event":"rollback_initiated"}'

# 4. Verify rollback success
kubectl rollout status deployment/odoo -n production
```

**Rollback SLA:** <15 minutes (critical), <1 hour (high), <4 hours (medium).

---

### 6.2 Post-Incident Actions

**Mandatory:**
- Root cause analysis (RCA) document in Odoo `azdev.incident` model
- Odoo automated action: Email stakeholders + create follow-up tasks
- Update runbooks in Odoo Knowledge Base
- Quarterly incident review (Compliance Officer)

---

## 7. MONITORING & OBSERVABILITY

### 7.1 Metrics

**Azure Monitor Metrics:**
- Pipeline success rate (target: ≥95%)
- Deployment frequency (DORA metric)
- Lead time for changes (DORA metric)
- Mean time to recovery (MTTR) (target: <1 hour)

**Odoo ICA Metrics:**
- Approval SLA compliance (target: ≥98% within 4 hours)
- Audit trail completeness (target: 100% no gaps)
- Emergency override frequency (target: ≤2 per quarter)

**Dashboards:**
- Azure Monitor: Real-time deployment health
- Odoo: ICA compliance dashboard (ECharts widgets)

---

### 7.2 Alerting

**Critical Alerts (PagerDuty + Mattermost):**
- Pipeline failure (3 consecutive runs)
- Odoo API unreachable (>5 minutes)
- Approval timeout (>4 hours)
- Security scan critical vulnerability

**Warning Alerts (Mattermost only):**
- Approval pending >2 hours
- Deployment queue >5 pending
- Cost threshold exceeded (80% of budget)

---

## 8. CHANGE MANAGEMENT

### 8.1 ICA Module Updates

**Process:**
1. Odoo module changes follow OCA contribution guidelines
2. PR review (2+ approvers: DevOps + Compliance)
3. Deploy to staging Odoo instance
4. Smoke test ICA APIs
5. Deploy to production Odoo (off-hours)
6. Monitor Azure Pipelines for 24 hours

**Rollback:** Odoo module rollback via `odoo -d production -u ipai_azdev_ica --rollback`

---

### 8.2 Azure Pipeline Template Updates

**Process:**
1. Update `azure-pipelines-template.yml`
2. Validate: `az pipelines validate --yaml-path <FILE>`
3. Test in sandbox pipeline
4. Roll out to 10% of pipelines (canary)
5. Full rollout after 48 hours no incidents

**Emergency Rollback:** Revert Git commit + force re-run pipelines.

---

## 9. DISASTER RECOVERY

### 9.1 Odoo ICA Backup

**Backup Strategy:**
- **Postgres:** Azure Backup (daily, 7-day retention)
- **Odoo filestore:** Azure Blob (hourly sync)
- **Audit trail:** Azure Archive Storage (yearly snapshots)

**RPO:** 1 hour (Recovery Point Objective)
**RTO:** 4 hours (Recovery Time Objective)

**DR Drill:** Quarterly restore test + stakeholder notification.

---

### 9.2 Azure Outage Fallback

**Scenario:** Azure region outage (East US)

**Fallback:**
1. Azure Traffic Manager → failover to West US region
2. Odoo CE 19 replica in West US (active-active)
3. ACR geo-replication (images available in West US)
4. Azure Pipelines → GitHub Actions (backup CI/CD)

**Odoo ICA Continuity:**
- Multi-region Postgres (Flexible Server with read replicas)
- Azure Front Door (global load balancing)
- Manual approval via Odoo mobile app (if web UI down)

---

## 10. SUCCESS CRITERIA

### 10.1 Phase 1 (MVP) - 6 Weeks

**Deliverables:**
- ✅ Odoo CE 19 + `ipai_azdev_ica` module deployed on AKS
- ✅ Azure Pipeline template with ICA hooks
- ✅ Run ledger operational (start/event/finish)
- ✅ Approval gate functional (technical + business)
- ✅ Audit trail completeness ≥99%

**Acceptance Criteria:**
- 10 test deployments with full ICA approval flow
- Zero audit trail gaps
- Approval SLA <2 hours (target: <4 hours)

---

### 10.2 Phase 2 (Production) - 12 Weeks

**Deliverables:**
- ✅ 50+ production deployments via ICA
- ✅ Azure Monitor + Odoo dashboards operational
- ✅ DR drill successful (RTO <4 hours)
- ✅ Compliance audit passed (SOX + GDPR)

**Success Metrics:**
- Pipeline success rate ≥95%
- Approval SLA compliance ≥98%
- Zero security incidents
- MTTR <1 hour

---

## 11. OUT OF SCOPE

**Explicitly NOT included:**
- Azure DevOps Boards integration (use Odoo Project instead)
- Multi-cloud orchestration (focus on Azure-native)
- Legacy Azure Classic resources (ARM templates only)
- Non-Odoo approval tools (ServiceNow, Jira)

---

## 12. REFERENCES

- [Azure DevOps Documentation](https://docs.microsoft.com/azure/devops)
- [Odoo CE 19 Documentation](https://www.odoo.com/documentation/19.0)
- [OCA Guidelines](https://github.com/OCA/maintainer-tools/wiki)
- [Azure Pipelines YAML Schema](https://docs.microsoft.com/azure/devops/pipelines/yaml-schema)
- [OpenAPI 3.1 Spec](https://spec.openapis.org/oas/v3.1.0)

---

**Version:** 1.0
**Last Updated:** 2026-01-27
**Status:** Draft → Review → Approved → Implemented
