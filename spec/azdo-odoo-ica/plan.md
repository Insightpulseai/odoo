# Implementation Plan: Azure DevOps + Odoo CE 19 ICA

**Spec Bundle:** `azdo-odoo-ica`
**Created:** 2026-01-27
**Duration:** 16 weeks
**Team:** 2 DevOps Engineers + 1 Odoo Developer + 1 QA Engineer

---

## PHASE 1: FOUNDATION (Weeks 1-4)

### Week 1: Infrastructure Setup

**Azure Resources:**
```bash
# 1. Create resource group
az group create --name rg-odoo-ica --location eastus

# 2. Create Azure Container Registry
az acr create --resource-group rg-odoo-ica --name acroodoica --sku Standard

# 3. Create AKS cluster
az aks create \
  --resource-group rg-odoo-ica \
  --name aks-odoo-ica \
  --node-count 3 \
  --enable-managed-identity \
  --generate-ssh-keys

# 4. Connect kubectl
az aks get-credentials --resource-group rg-odoo-ica --name aks-odoo-ica

# 5. Create Azure Database for PostgreSQL
az postgres flexible-server create \
  --resource-group rg-odoo-ica \
  --name psql-odoo-ica \
  --admin-user odoo \
  --admin-password <PASSWORD> \
  --sku-name Standard_D2s_v3 \
  --storage-size 128 \
  --version 15
```

**Deliverables:**
- ✅ AKS cluster operational
- ✅ ACR configured
- ✅ PostgreSQL 15 database created
- ✅ Kubectl context configured

---

### Week 2: Odoo CE 19 Base Deployment

**Deploy Odoo via Helm:**
```bash
# 1. Add Bitnami Helm repo
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# 2. Create values.yaml for Odoo CE 19
cat > odoo-values.yaml << 'YAML'
image:
  repository: acroodoica.azurecr.io/odoo-ce
  tag: "19.0"

postgresql:
  enabled: false  # Use Azure managed PostgreSQL

externalDatabase:
  host: psql-odoo-ica.postgres.database.azure.com
  port: 5432
  user: odoo
  password: <PASSWORD>
  database: odoo

replicaCount: 2

ingress:
  enabled: true
  hostname: odoo-ica.example.com
  tls: true

resources:
  requests:
    cpu: 500m
    memory: 1Gi
  limits:
    cpu: 2000m
    memory: 4Gi
YAML

# 3. Deploy Odoo
helm install odoo-ce bitnami/odoo -f odoo-values.yaml --namespace odoo --create-namespace

# 4. Wait for pods ready
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=odoo -n odoo --timeout=300s
```

**Deliverables:**
- ✅ Odoo CE 19 running on AKS
- ✅ PostgreSQL connection verified
- ✅ Ingress configured (TLS)
- ✅ Health check: `/web/health` returns 200

---

### Week 3: Odoo ICA Module Scaffold

**Create `ipai_azdev_ica` module:**
```bash
# 1. Clone Odoo repo
git clone https://github.com/odoo/odoo --branch 19.0 odoo-ce-19
cd odoo-ce-19/addons

# 2. Create module structure
mkdir -p ipai_azdev_ica
cd ipai_azdev_ica

# 3. Create __manifest__.py
cat > __manifest__.py << 'PYTHON'
{
    'name': 'Azure DevOps ICA',
    'version': '19.0.1.0.0',
    'category': 'Operations',
    'summary': 'Internal Control Architecture for Azure DevOps',
    'author': 'InsightPulse AI',
    'license': 'AGPL-3',
    'depends': ['base', 'base_rest', 'project', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/azdev_pipeline_run_views.xml',
        'views/azdev_approval_views.xml',
        'views/azdev_incident_views.xml',
        'views/azdev_dashboard_views.xml',
        'data/azdev_approval_template.xml',
    ],
    'installable': True,
    'application': True,
}
PYTHON

# 4. Create models
mkdir models
cat > models/__init__.py << 'PYTHON'
from . import azdev_pipeline_run
from . import azdev_approval
from . import azdev_incident
PYTHON

cat > models/azdev_pipeline_run.py << 'PYTHON'
from odoo import models, fields, api

class AzDevPipelineRun(models.Model):
    _name = 'azdev.pipeline.run'
    _description = 'Azure DevOps Pipeline Run Ledger'
    _order = 'start_time desc'

    pipeline_name = fields.Char(required=True, index=True)
    run_id = fields.Char(required=True, index=True)
    branch = fields.Char()
    commit = fields.Char()
    triggered_by = fields.Char()
    status = fields.Selection([
        ('running', 'Running'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled')
    ], default='running', required=True)
    start_time = fields.Datetime(required=True, default=fields.Datetime.now)
    end_time = fields.Datetime()
    duration_seconds = fields.Integer(compute='_compute_duration', store=True)
    events = fields.One2many('azdev.pipeline.event', 'run_id')
    approval_id = fields.Many2one('azdev.approval', string='Approval')
    cost_actual = fields.Float(string='Actual Cost')
    audit_hash = fields.Char(string='Audit Hash')

    @api.depends('start_time', 'end_time')
    def _compute_duration(self):
        for record in self:
            if record.start_time and record.end_time:
                delta = record.end_time - record.start_time
                record.duration_seconds = int(delta.total_seconds())
            else:
                record.duration_seconds = 0

    def action_finish(self, status):
        self.ensure_one()
        self.status = status
        self.end_time = fields.Datetime.now()
        self.audit_hash = self._generate_audit_hash()

    def _generate_audit_hash(self):
        import hashlib
        data = f"{self.run_id}{self.status}{self.end_time}".encode()
        return hashlib.sha256(data).hexdigest()
PYTHON
```

**Deliverables:**
- ✅ `ipai_azdev_ica` module structure created
- ✅ Core models defined (run, approval, incident)
- ✅ `__manifest__.py` configured
- ✅ Module installable via `odoo -d odoo -i ipai_azdev_ica`

---

### Week 4: REST API Implementation

**Install `base_rest` dependency:**
```bash
# 1. Clone OCA/rest-framework
git clone https://github.com/OCA/rest-framework --branch 19.0 addons/oca/rest-framework

# 2. Update __manifest__.py depends
'depends': ['base', 'base_rest', 'project', 'mail']
```

**Create REST services:**
```python
# services/__init__.py
from . import azdev_api_service

# services/azdev_api_service.py
from odoo.addons.base_rest.controllers.main import RestController
from odoo.addons.component.core import Component

class AzDevAPIController(RestController):
    _root_path = '/api/v1/azdev/'
    _collection_name = 'azdev.api.services'

class AzDevRunService(Component):
    _inherit = 'base.rest.service'
    _name = 'azdev.run.service'
    _usage = 'run'
    _collection = 'azdev.api.services'

    def start(self, pipeline_name, run_id, branch, commit, triggered_by):
        run = self.env['azdev.pipeline.run'].create({
            'pipeline_name': pipeline_name,
            'run_id': run_id,
            'branch': branch,
            'commit': commit,
            'triggered_by': triggered_by,
        })
        return {'success': True, 'odoo_record_id': run.id}

    def event(self, run_id, event_type, event_data):
        run = self.env['azdev.pipeline.run'].search([('run_id', '=', run_id)], limit=1)
        if not run:
            return {'success': False, 'error': 'Run not found'}
        event = self.env['azdev.pipeline.event'].create({
            'run_id': run.id,
            'event_type': event_type,
            'event_data': event_data,
        })
        return {'success': True, 'event_id': event.id}

    def finish(self, run_id, status, end_time):
        run = self.env['azdev.pipeline.run'].search([('run_id', '=', run_id)], limit=1)
        if not run:
            return {'success': False, 'error': 'Run not found'}
        run.action_finish(status)
        return {'success': True, 'audit_hash': run.audit_hash}

    def _validator_start(self):
        return {'pipeline_name': {'type': 'string', 'required': True}}
```

**Deliverables:**
- ✅ REST API endpoints operational
- ✅ Authentication via Bearer token
- ✅ OpenAPI schema generated
- ✅ Postman collection for testing

---

## PHASE 2: CORE FEATURES (Weeks 5-8)

### Week 5: Approval Workflow

**Implement approval logic:**
```python
# models/azdev_approval.py
class AzDevApproval(models.Model):
    _name = 'azdev.approval'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    approval_id = fields.Char(default=lambda self: self.env['ir.sequence'].next_by_code('azdev.approval'))
    run_id = fields.Many2one('azdev.pipeline.run', required=True)
    deployment_target = fields.Selection([('staging', 'Staging'), ('production', 'Production')])
    estimated_cost = fields.Float()
    status = fields.Selection([
        ('pending', 'Pending'),
        ('technical_approved', 'Technical Approved'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired')
    ], default='pending', tracking=True)

    def action_technical_approve(self):
        self.status = 'technical_approved'
        self.technical_approved_at = fields.Datetime.now()
        self._send_mattermost_notification('technical_approved')

    def action_business_approve(self):
        if self.status != 'technical_approved':
            raise UserError('Technical approval required first')
        self.status = 'approved'
        self.business_approved_at = fields.Datetime.now()
        self._send_mattermost_notification('approved')

    def _send_mattermost_notification(self, event):
        webhook_url = self.env['ir.config_parameter'].sudo().get_param('azdev.mattermost_webhook_url')
        # Implementation...
```

**Deliverables:**
- ✅ Approval workflow operational
- ✅ Dual approval (technical + business)
- ✅ Mattermost notifications
- ✅ Approval timeout handling (4 hours)

---

### Week 6: Azure Pipeline Integration

**Create `azure-pipelines-ica-template.yml`:**
```yaml
parameters:
  - name: deployment_target
    type: string
    default: production
  - name: estimated_cost
    type: number
    default: 0

stages:
  - stage: Build
    jobs:
      - job: BuildJob
        steps:
          - bash: |
              curl -X POST "$ODOO_API_RUN_START" \
                -H "Authorization: Bearer $MANAGED_IDENTITY_TOKEN" \
                -d '{
                  "pipeline_name":"$(Build.DefinitionName)",
                  "run_id":"$(Build.BuildId)",
                  "branch":"$(Build.SourceBranch)",
                  "commit":"$(Build.SourceVersion)",
                  "triggered_by":"$(Build.RequestedFor)"
                }'
            displayName: 'ICA: Run Start'

          - task: Docker@2
            inputs:
              containerRegistry: 'acroodoica'
              repository: 'myapp'
              command: 'buildAndPush'
              Dockerfile: 'Dockerfile'
              tags: '$(Build.BuildId)'

          - bash: |
              curl -X POST "$ODOO_API_RUN_EVENT" \
                -H "Authorization: Bearer $MANAGED_IDENTITY_TOKEN" \
                -d '{
                  "run_id":"$(Build.BuildId)",
                  "event_type":"build_success",
                  "event_data":{"image":"acroodoica.azurecr.io/myapp:$(Build.BuildId)"}
                }'
            displayName: 'ICA: Build Event'

  - stage: Approval
    dependsOn: Build
    jobs:
      - job: RequestApproval
        steps:
          - bash: |
              response=$(curl -X POST "$ODOO_API_APPROVAL" \
                -H "Authorization: Bearer $MANAGED_IDENTITY_TOKEN" \
                -d '{
                  "run_id":"$(Build.BuildId)",
                  "deployment_target":"${{ parameters.deployment_target }}",
                  "estimated_cost":${{ parameters.estimated_cost }}
                }')
              echo "##vso[task.setvariable variable=approval_id]$(echo $response | jq -r .approval_id)"
            displayName: 'ICA: Request Approval'

          - bash: |
              while true; do
                status=$(curl -s "$ODOO_API_APPROVAL/$(approval_id)" \
                  -H "Authorization: Bearer $MANAGED_IDENTITY_TOKEN" | jq -r .status)
                echo "Approval status: $status"
                if [ "$status" == "approved" ]; then
                  echo "Approval granted!"
                  exit 0
                elif [ "$status" == "rejected" ] || [ "$status" == "expired" ]; then
                  echo "Approval denied: $status"
                  exit 1
                fi
                sleep 30
              done
            displayName: 'ICA: Poll Approval'
            timeoutInMinutes: 240

  - stage: Deploy
    dependsOn: Approval
    condition: succeeded()
    jobs:
      - job: DeployJob
        steps:
          - task: KubernetesManifest@0
            inputs:
              action: 'deploy'
              manifests: 'k8s/deployment.yaml'

          - bash: |
              curl -X POST "$ODOO_API_RUN_FINISH" \
                -H "Authorization: Bearer $MANAGED_IDENTITY_TOKEN" \
                -d '{
                  "run_id":"$(Build.BuildId)",
                  "status":"success",
                  "end_time":"$(date -u +%Y-%m-%dT%H:%M:%SZ)"
                }'
            displayName: 'ICA: Run Finish'
```

**Deliverables:**
- ✅ Azure Pipeline template operational
- ✅ ICA hooks integrated (start/event/finish)
- ✅ Approval polling logic
- ✅ Managed Identity authentication

---

### Week 7: Cost Governance

**Implement cost tracking:**
```python
# models/azdev_cost.py
class AzDevCostActual(models.Model):
    _name = 'azdev.cost.actual'

    run_id = fields.Many2one('azdev.pipeline.run')
    resource_type = fields.Selection([('aks', 'AKS'), ('acr', 'ACR'), ('blob', 'Blob Storage')])
    cost_usd = fields.Float()
    billing_period = fields.Date()

    @api.model
    def sync_from_azure(self):
        # Call Azure Cost Management API
        # az cost management query --scope /subscriptions/{subscription_id}
        pass

# Add to approval validation
def _check_budget_threshold(self):
    current_month_cost = sum(self.env['azdev.cost.actual'].search([
        ('billing_period', '>=', fields.Date.today().replace(day=1))
    ]).mapped('cost_usd'))
    budget = float(self.env['ir.config_parameter'].sudo().get_param('azdev.monthly_budget', 10000))
    if (current_month_cost + self.estimated_cost) / budget > 0.95:
        raise UserError('Budget threshold exceeded (95%)')
```

**Deliverables:**
- ✅ Azure Cost Management API integration
- ✅ Budget threshold validation
- ✅ Cost dashboard (ECharts)
- ✅ Finance Director alerts (>$5,000)

---

### Week 8: Audit Trail Export

**Implement export wizard:**
```python
# wizards/azdev_audit_export.py
class AzDevAuditExport(models.TransientModel):
    _name = 'azdev.audit.export'

    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True)
    export_format = fields.Selection([('csv', 'CSV'), ('json', 'JSON'), ('pdf', 'PDF')])

    def action_export(self):
        runs = self.env['azdev.pipeline.run'].search([
            ('start_time', '>=', self.date_from),
            ('start_time', '<=', self.date_to)
        ])
        if self.export_format == 'csv':
            return self._export_csv(runs)
        # ... other formats

    def _export_csv(self, runs):
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Run ID', 'Pipeline', 'Status', 'Start', 'End', 'Audit Hash'])
        for run in runs:
            writer.writerow([run.run_id, run.pipeline_name, run.status, run.start_time, run.end_time, run.audit_hash])
        return {
            'type': 'ir.actions.act_url',
            'url': f'data:text/csv;base64,{base64.b64encode(output.getvalue().encode()).decode()}',
            'target': 'download'
        }
```

**Deliverables:**
- ✅ Audit export wizard
- ✅ CSV/JSON/PDF formats
- ✅ Cryptographic hash validation
- ✅ Azure Blob archival

---

## PHASE 3: INTEGRATION & TESTING (Weeks 9-12)

### Week 9: Mattermost Deep Integration

**Features:**
- ✅ Rich approval cards with buttons
- ✅ One-click approval via Mattermost
- ✅ Approval status updates (real-time)
- ✅ Alert routing (critical → PagerDuty, warning → Mattermost)

### Week 10: Azure Monitor Integration

**Features:**
- ✅ Alert webhook receiver (`POST /api/v1/azdev/alert`)
- ✅ Auto-create incidents from Azure Monitor
- ✅ Incident severity mapping
- ✅ Mattermost incident notifications

### Week 11: Load Testing

**Test Scenarios:**
- 1,000 pipeline runs/hour → Odoo stable
- 500 approval requests queued → No deadlocks
- 10,000 audit export → <5 minutes

### Week 12: Security & Compliance

**Activities:**
- ✅ Azure Defender security scan
- ✅ Penetration testing (OWASP Top 10)
- ✅ SOX compliance audit prep
- ✅ GDPR data residency validation

---

## PHASE 4: PRODUCTION & OPTIMIZATION (Weeks 13-16)

### Week 13: Production Deployment

**Steps:**
1. Final staging validation (50 test deployments)
2. Production cutover (off-hours)
3. 24-hour monitoring (DevOps on-call)
4. Rollback plan tested

### Week 14: User Training

**Sessions:**
- DevOps Engineers: Pipeline integration (2 hours)
- Technical Approvers: Approval workflow (1 hour)
- Business Approvers: Cost governance (1 hour)
- Auditors: Export & reporting (1 hour)

### Week 15: Performance Optimization

**Optimizations:**
- Odoo query optimization (sub-100ms)
- PostgreSQL index tuning
- AKS autoscaling rules
- CDN for static assets

### Week 16: Documentation & Handoff

**Deliverables:**
- ✅ Admin guide (Odoo module maintenance)
- ✅ User guide (approval workflows)
- ✅ Runbooks (incident response, DR)
- ✅ API documentation (OpenAPI schema)

---

## DEPLOYMENT CHECKLIST

### Pre-Deployment

- [ ] Azure resources provisioned (AKS, ACR, PostgreSQL)
- [ ] Odoo CE 19 deployed and healthy
- [ ] `ipai_azdev_ica` module installed
- [ ] REST API endpoints validated (Postman tests)
- [ ] Azure Pipeline template validated
- [ ] Managed Identity configured
- [ ] Mattermost webhook configured
- [ ] Azure Monitor alerts configured

### Deployment

- [ ] Backup production Odoo database
- [ ] Deploy updated module (`odoo -d production -u ipai_azdev_ica`)
- [ ] Run smoke tests (10 test deployments)
- [ ] Validate approval workflow (end-to-end)
- [ ] Verify Mattermost notifications
- [ ] Test cost governance (budget threshold)
- [ ] Export audit trail (sample)

### Post-Deployment

- [ ] 24-hour monitoring (no critical errors)
- [ ] Approval SLA <2 hours (target: <4 hours)
- [ ] Run ledger completeness 100%
- [ ] User training completed
- [ ] Documentation published
- [ ] DR drill scheduled (quarterly)

---

## ROLLBACK PLAN

**Trigger:** Critical failure (Odoo unavailable >5 minutes, approval workflow broken)

**Steps:**
1. Revert Odoo module: `odoo -d production -u ipai_azdev_ica --rollback`
2. Restore PostgreSQL backup: `az postgres flexible-server restore`
3. Switch Azure Pipelines to emergency bypass mode (manual approval)
4. Notify stakeholders (Mattermost + Email)
5. Root cause analysis (mandatory within 24 hours)

**RTO:** <15 minutes (critical), <1 hour (high)

---

**Version:** 1.0
**Last Updated:** 2026-01-27
**Next Review:** Every 2 weeks during implementation
