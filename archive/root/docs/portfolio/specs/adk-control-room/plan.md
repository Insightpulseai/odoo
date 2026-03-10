# ADK Control Room — Implementation Plan

## Overview

4-phase implementation spanning 8 weeks, targeting MVP completion by Q4 2025.

## Phase 1 — Foundation (Week 1–2)

### Objectives
- Establish core infrastructure
- Define tool contracts
- Set up catalog + lineage schema
- Implement basic job API

### Deliverables

#### 1.1 Supabase Schema
**Tables**:
```sql
-- Job runs table
CREATE TABLE cr_runs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  job_type TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('queued', 'running', 'success', 'failed', 'cancelled')),
  params JSONB NOT NULL,
  idempotency_key TEXT UNIQUE NOT NULL,
  started_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ,
  error TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  created_by TEXT NOT NULL
);

-- Job definitions
CREATE TABLE cr_jobs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT UNIQUE NOT NULL,
  description TEXT,
  tool_contracts JSONB NOT NULL,
  agent_config JSONB NOT NULL,
  approval_required BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Lineage graph
CREATE TABLE cr_lineage (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  run_id UUID REFERENCES cr_runs(id) NOT NULL,
  source_type TEXT NOT NULL, -- 'table', 'file', 'api'
  source_name TEXT NOT NULL,
  target_type TEXT NOT NULL,
  target_name TEXT NOT NULL,
  transformation TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Artifacts
CREATE TABLE cr_artifacts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  run_id UUID REFERENCES cr_runs(id) NOT NULL,
  artifact_type TEXT NOT NULL, -- 'pdf', 'csv', 'json', 'log'
  storage_url TEXT NOT NULL,
  metadata JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_runs_status ON cr_runs(status);
CREATE INDEX idx_runs_idempotency ON cr_runs(idempotency_key);
CREATE INDEX idx_lineage_run ON cr_lineage(run_id);
CREATE INDEX idx_artifacts_run ON cr_artifacts(run_id);
```

**RLS Policies**:
```sql
-- cr_runs: Users can see their own runs
CREATE POLICY runs_select ON cr_runs
  FOR SELECT USING (
    auth.uid() = created_by::UUID OR
    auth.jwt() ->> 'role' IN ('admin', 'auditor')
  );

-- cr_runs: Users can insert runs
CREATE POLICY runs_insert ON cr_runs
  FOR INSERT WITH CHECK (auth.uid() = created_by::UUID);

-- cr_lineage: Read-only for all authenticated users
CREATE POLICY lineage_select ON cr_lineage
  FOR SELECT USING (auth.role() = 'authenticated');

-- cr_artifacts: Read-only for all authenticated users
CREATE POLICY artifacts_select ON cr_artifacts
  FOR SELECT USING (auth.role() = 'authenticated');
```

#### 1.2 ADK-TS Runtime

**Tool Contracts**:
```typescript
// tools/contracts.ts
export interface Tool {
  name: string;
  description: string;
  inputSchema: JSONSchema;
  outputSchema: JSONSchema;
  execute: (input: unknown) => Promise<unknown>;
}

export interface RunJobTool extends Tool {
  name: 'runJob';
  execute: (input: {
    jobType: string;
    params: Record<string, unknown>;
    idempotencyKey: string;
  }) => Promise<{ runId: string; status: string }>;
}

export interface CatalogLookupTool extends Tool {
  name: 'catalogLookup';
  execute: (input: {
    query: string;
    filters?: Record<string, unknown>;
  }) => Promise<{ results: CatalogEntry[] }>;
}

export interface WriteLineageTool extends Tool {
  name: 'writeLineage';
  execute: (input: {
    runId: string;
    source: { type: string; name: string };
    target: { type: string; name: string };
    transformation?: string;
  }) => Promise<{ lineageId: string }>;
}

export interface UploadArtifactTool extends Tool {
  name: 'uploadArtifact';
  execute: (input: {
    runId: string;
    artifactType: string;
    content: Buffer | string;
    metadata?: Record<string, unknown>;
  }) => Promise<{ artifactId: string; url: string }>;
}
```

**Agent Registry**:
```typescript
// agents/registry.ts
export interface Agent {
  id: string;
  name: string;
  version: string;
  tools: Tool[];
  execute: (input: AgentInput) => Promise<AgentOutput>;
}

export interface AgentInput {
  task: string;
  context: Record<string, unknown>;
}

export interface AgentOutput {
  result: unknown;
  artifacts: string[];
  lineage: LineageEntry[];
}
```

#### 1.3 Job API

**Endpoint**: `POST /api/jobs/run`

**Implementation**:
```typescript
// api/jobs.ts
import { supabase } from '@/lib/supabase';
import { AgentRegistry } from '@/agents/registry';

export async function POST(req: Request) {
  const { jobType, params, idempotencyKey } = await req.json();

  // Check idempotency
  const { data: existing } = await supabase
    .from('cr_runs')
    .select('id, status')
    .eq('idempotency_key', idempotencyKey)
    .single();

  if (existing) {
    return Response.json({ runId: existing.id, status: existing.status });
  }

  // Create run record
  const { data: run } = await supabase
    .from('cr_runs')
    .insert({
      job_type: jobType,
      status: 'queued',
      params,
      idempotency_key: idempotencyKey,
      created_by: req.headers.get('x-user-id') || 'system'
    })
    .select()
    .single();

  // Queue job execution
  await queueJob(run.id, jobType, params);

  return Response.json({ runId: run.id, status: 'queued' });
}
```

### Acceptance Criteria
- ✅ Supabase schema deployed
- ✅ Tool contracts defined with TypeScript
- ✅ Agent registry implemented
- ✅ Job API returns run ID
- ✅ Idempotency working (duplicate submissions return same run ID)

---

## Phase 2 — Docs → Code (Week 3–4)

### Objectives
- Integrate Continue headless worker
- Implement spec validation gate
- Automate PR generation
- Capture artifacts from agent runs

### Deliverables

#### 2.1 Continue Headless Worker

**Service**: `services/continue-worker/`

**Configuration**:
```yaml
# services/continue-worker/config.yaml
watch:
  - path: /spec/**/*.md
    trigger: spec_change
  - path: /docs/**/*.md
    trigger: docs_change
  - path: addons/*/__manifest__.py
    trigger: module_change

agents:
  spec_validator:
    model: claude-3-5-sonnet-20241022
    tools:
      - validateSpecBundle
      - checkToolContracts

  pr_generator:
    model: claude-3-5-sonnet-20241022
    tools:
      - readSpec
      - generateCode
      - createPR
```

**Watcher Implementation**:
```typescript
// services/continue-worker/watcher.ts
import { watch } from 'chokidar';
import { ContinueAgent } from './agent';

const watcher = watch(['/spec/**/*.md', '/docs/**/*.md'], {
  persistent: true,
  ignoreInitial: true
});

watcher.on('change', async (path) => {
  console.log(`Spec changed: ${path}`);

  const agent = new ContinueAgent('spec_validator');
  const result = await agent.execute({
    task: `Validate spec bundle at ${path}`,
    context: { path }
  });

  if (result.valid) {
    const prAgent = new ContinueAgent('pr_generator');
    await prAgent.execute({
      task: `Generate PR for spec changes at ${path}`,
      context: { path, validation: result }
    });
  }
});
```

#### 2.2 Spec Validation Gate

**Validation Rules**:
```typescript
// tools/spec-validator.ts
export interface SpecBundle {
  constitution: string;
  prd: string;
  plan: string;
  tasks: string;
}

export async function validateSpecBundle(path: string): Promise<ValidationResult> {
  const bundle = await loadSpecBundle(path);

  const checks = [
    checkConstitutionExists(bundle),
    checkPRDExists(bundle),
    checkPlanExists(bundle),
    checkTasksExist(bundle),
    checkToolContractsValid(bundle),
    checkNoHardcodedSecrets(bundle),
    checkNoDirectDBMutation(bundle)
  ];

  const results = await Promise.all(checks);
  const passed = results.every(r => r.passed);

  return {
    passed,
    errors: results.filter(r => !r.passed).map(r => r.error)
  };
}
```

**CI Integration**:
```yaml
# .github/workflows/spec-validation.yml
name: Spec Validation

on:
  pull_request:
    paths:
      - 'spec/**/*.md'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Validate Spec Bundle
        run: |
          npm run spec:validate

      - name: Check Tool Contracts
        run: |
          npm run tools:check

      - name: Block if invalid
        if: failure()
        run: |
          echo "❌ Spec validation failed"
          exit 1
```

#### 2.3 PR Automation

**PR Template**:
```markdown
## Spec-Driven Changes

**Spec Bundle**: spec/[bundle-name]/

**Changes**:
- [ ] Code generated from spec
- [ ] Tool contracts validated
- [ ] Agent tests added
- [ ] Lineage tracking implemented

**Validation**:
- ✅ Spec bundle complete
- ✅ Tool contracts valid
- ✅ No security violations

**Review Checklist**:
- [ ] Spec aligns with constitution
- [ ] Code matches spec intent
- [ ] Tests cover edge cases
- [ ] Lineage correctly tracked

---
*Auto-generated by Continue Agent*
```

#### 2.4 Artifact Capture

**Storage Strategy**:
```typescript
// tools/artifact-uploader.ts
import { supabase } from '@/lib/supabase';

export async function uploadArtifact(input: {
  runId: string;
  artifactType: string;
  content: Buffer | string;
  metadata?: Record<string, unknown>;
}): Promise<{ artifactId: string; url: string }> {
  // Upload to Supabase Storage
  const { data: file, error: uploadError } = await supabase
    .storage
    .from('artifacts')
    .upload(`runs/${input.runId}/${Date.now()}-${input.artifactType}`, input.content);

  if (uploadError) throw uploadError;

  // Get public URL
  const { data: { publicUrl } } = supabase
    .storage
    .from('artifacts')
    .getPublicUrl(file.path);

  // Record artifact in catalog
  const { data: artifact } = await supabase
    .from('cr_artifacts')
    .insert({
      run_id: input.runId,
      artifact_type: input.artifactType,
      storage_url: publicUrl,
      metadata: input.metadata
    })
    .select()
    .single();

  return { artifactId: artifact.id, url: publicUrl };
}
```

### Acceptance Criteria
- ✅ Continue headless worker running
- ✅ Spec changes trigger validation
- ✅ Valid specs generate PRs
- ✅ PRs include tests
- ✅ Artifacts uploaded to Supabase Storage

---

## Phase 3 — Business Gating (Week 5–6)

### Objectives
- Integrate Odoo approval workflows
- Respect finance period locks
- Implement SLA + escalation hooks
- Write results back to Odoo

### Deliverables

#### 3.1 Odoo Approval Hooks

**Approval Check**:
```python
# addons/ipai_control_room/models/approval.py
from odoo import models, fields, api

class ControlRoomApproval(models.Model):
    _name = 'ipai.control_room.approval'
    _description = 'Control Room Job Approval'

    job_id = fields.Char(required=True)
    job_type = fields.Char(required=True)
    params = fields.Text()
    requester_id = fields.Many2one('res.users', required=True)
    approver_id = fields.Many2one('res.users')
    state = fields.Selection([
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], default='pending')
    approved_at = fields.Datetime()

    @api.model
    def check_approval(self, job_id):
        approval = self.search([('job_id', '=', job_id)], limit=1)
        if not approval:
            return {'required': False}

        return {
            'required': True,
            'approved': approval.state == 'approved',
            'approver': approval.approver_id.name if approval.approver_id else None
        }
```

**API Integration**:
```typescript
// lib/odoo-approvals.ts
export async function checkApproval(runId: string): Promise<ApprovalStatus> {
  const response = await fetch('http://odoo:8071/xmlrpc/2/object', {
    method: 'POST',
    body: JSON.stringify({
      service: 'object',
      method: 'execute_kw',
      args: [
        'odoo_accounting',
        uid,
        password,
        'ipai.control_room.approval',
        'check_approval',
        [runId]
      ]
    })
  });

  const { required, approved, approver } = await response.json();

  if (required && !approved) {
    throw new ApprovalRequiredError(`Approval required from ${approver}`);
  }

  return { approved, approver };
}
```

#### 3.2 Period Locks

**Period Lock Check**:
```python
# addons/ipai_finance_ppm/models/period_lock.py
class FinancePeriodLock(models.Model):
    _name = 'ipai.finance.period_lock'
    _description = 'Finance Period Lock'

    period = fields.Char(required=True)  # '2025-11'
    locked = fields.Boolean(default=False)
    locked_by = fields.Many2one('res.users')
    locked_at = fields.Datetime()

    @api.model
    def check_period_lock(self, period):
        lock = self.search([('period', '=', period)], limit=1)
        if lock and lock.locked:
            return {
                'locked': True,
                'locked_by': lock.locked_by.name,
                'locked_at': lock.locked_at.isoformat()
            }
        return {'locked': False}
```

**Control Room Integration**:
```typescript
// lib/period-locks.ts
export async function checkPeriodLock(period: string): Promise<void> {
  const response = await odooXMLRPC('ipai.finance.period_lock', 'check_period_lock', [period]);

  if (response.locked) {
    throw new PeriodLockedError(
      `Period ${period} locked by ${response.locked_by} at ${response.locked_at}`
    );
  }
}
```

#### 3.3 SLA + Escalation

**SLA Configuration**:
```yaml
# config/sla.yaml
job_types:
  month_end_close:
    sla: 5 business days
    escalate_after: 3 business days
    escalate_to: finance.director@tbwa.com

  bir_filing:
    sla: 1 business day
    escalate_after: 4 hours
    escalate_to: finance.supervisor@tbwa.com
```

**Escalation Logic**:
```typescript
// lib/sla-monitor.ts
import { supabase } from '@/lib/supabase';

export async function checkSLA() {
  const { data: runs } = await supabase
    .from('cr_runs')
    .select('*')
    .eq('status', 'running')
    .lt('created_at', new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString());

  for (const run of runs) {
    const sla = getSLA(run.job_type);
    const elapsed = Date.now() - new Date(run.created_at).getTime();

    if (elapsed > sla.escalate_after) {
      await sendEscalation(run, sla.escalate_to);
    }
  }
}
```

#### 3.4 Results Write-Back

**Odoo Attachment**:
```python
# addons/ipai_control_room/models/result.py
class ControlRoomResult(models.Model):
    _name = 'ipai.control_room.result'
    _description = 'Control Room Job Result'

    run_id = fields.Char(required=True)
    job_type = fields.Char(required=True)
    status = fields.Selection([
        ('success', 'Success'),
        ('failed', 'Failed')
    ])
    artifact_ids = fields.One2many('ir.attachment', 'res_id')

    @api.model
    def write_result(self, run_id, status, artifacts):
        result = self.create({
            'run_id': run_id,
            'job_type': params['job_type'],
            'status': status
        })

        for artifact in artifacts:
            self.env['ir.attachment'].create({
                'name': artifact['name'],
                'type': 'url',
                'url': artifact['url'],
                'res_model': 'ipai.control_room.result',
                'res_id': result.id
            })

        return result.id
```

### Acceptance Criteria
- ✅ Jobs requiring approval are blocked until approved
- ✅ Jobs for locked periods are rejected
- ✅ SLA violations trigger escalations
- ✅ Job results written to Odoo as attachments

---

## Phase 4 — Production Hardening (Week 7–8)

### Objectives
- Build visual lineage UI
- Implement retry policies
- Add RBAC / RLS
- Set up observability

### Deliverables

#### 4.1 Visual Lineage UI

**Technology**: D3.js force-directed graph

**Component**:
```typescript
// components/LineageGraph.tsx
import * as d3 from 'd3';

export function LineageGraph({ runId }: { runId: string }) {
  const { data: lineage } = useQuery(['lineage', runId], () =>
    fetch(`/api/lineage/graph?runId=${runId}`).then(r => r.json())
  );

  useEffect(() => {
    if (!lineage) return;

    const svg = d3.select('#lineage-graph');
    const simulation = d3.forceSimulation(lineage.nodes)
      .force('link', d3.forceLink(lineage.edges))
      .force('charge', d3.forceManyBody())
      .force('center', d3.forceCenter(400, 300));

    // Render nodes and edges
    svg.selectAll('line')
      .data(lineage.edges)
      .enter().append('line')
      .attr('stroke', '#999');

    svg.selectAll('circle')
      .data(lineage.nodes)
      .enter().append('circle')
      .attr('r', 10)
      .attr('fill', d => d.type === 'source' ? '#4CAF50' : '#2196F3');

    simulation.on('tick', () => {
      svg.selectAll('line')
        .attr('x1', d => d.source.x)
        .attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x)
        .attr('y2', d => d.target.y);

      svg.selectAll('circle')
        .attr('cx', d => d.x)
        .attr('cy', d => d.y);
    });
  }, [lineage]);

  return <svg id="lineage-graph" width="800" height="600" />;
}
```

#### 4.2 Retry Policies

**Configuration**:
```yaml
# config/retry.yaml
retry_policies:
  default:
    max_attempts: 3
    backoff: exponential
    initial_delay: 1000ms
    max_delay: 30000ms

  critical:
    max_attempts: 5
    backoff: exponential
    initial_delay: 500ms
    max_delay: 60000ms
```

**Implementation**:
```typescript
// lib/retry.ts
export async function retryWithBackoff<T>(
  fn: () => Promise<T>,
  policy: RetryPolicy
): Promise<T> {
  let attempt = 0;
  let delay = policy.initial_delay;

  while (attempt < policy.max_attempts) {
    try {
      return await fn();
    } catch (error) {
      attempt++;

      if (attempt >= policy.max_attempts) {
        throw error;
      }

      await sleep(delay);
      delay = Math.min(delay * 2, policy.max_delay);
    }
  }
}
```

#### 4.3 RBAC / RLS

**Roles**:
- **Admin**: Full access
- **Platform Engineer**: Manage jobs, view lineage
- **Finance Lead**: Submit finance jobs, view artifacts
- **Auditor**: Read-only access to all data
- **Agent**: Execute jobs, write artifacts

**RLS Policies**:
```sql
-- Finance leads can only see their own runs
CREATE POLICY finance_runs ON cr_runs
  FOR SELECT USING (
    auth.jwt() ->> 'role' = 'finance_lead' AND
    created_by = auth.uid()
  );

-- Auditors can see all runs
CREATE POLICY auditor_runs ON cr_runs
  FOR SELECT USING (auth.jwt() ->> 'role' = 'auditor');

-- Agents can insert runs
CREATE POLICY agent_insert ON cr_runs
  FOR INSERT WITH CHECK (auth.jwt() ->> 'role' = 'agent');
```

#### 4.4 Observability

**Metrics** (Prometheus):
```typescript
// lib/metrics.ts
import { Counter, Histogram } from 'prom-client';

export const jobSubmissions = new Counter({
  name: 'control_room_job_submissions_total',
  help: 'Total job submissions',
  labelNames: ['job_type', 'status']
});

export const jobDuration = new Histogram({
  name: 'control_room_job_duration_seconds',
  help: 'Job execution duration',
  labelNames: ['job_type'],
  buckets: [1, 5, 10, 30, 60, 300, 600]
});
```

**Dashboards** (Grafana):
```yaml
# dashboards/control-room.json
{
  "dashboard": {
    "title": "Control Room Overview",
    "panels": [
      {
        "title": "Job Submissions",
        "targets": ["control_room_job_submissions_total"]
      },
      {
        "title": "Job Success Rate",
        "targets": ["rate(control_room_job_submissions_total{status='success'}[5m])"]
      },
      {
        "title": "Job Duration (P95)",
        "targets": ["histogram_quantile(0.95, control_room_job_duration_seconds)"]
      }
    ]
  }
}
```

### Acceptance Criteria
- ✅ Lineage graph renders correctly
- ✅ Failed jobs automatically retry
- ✅ RBAC enforced (finance leads cannot see other users' runs)
- ✅ Metrics exported to Prometheus
- ✅ Grafana dashboards deployed

---

## Deployment Strategy

### Environment Progression
1. **Development** (local Docker Compose)
2. **Staging** (DigitalOcean droplet 159.223.75.148)
3. **Production** (DigitalOcean App Platform)

### Rollout Plan
- **Week 1-2**: Deploy to development
- **Week 3-4**: Deploy to staging
- **Week 5-6**: Beta testing in staging
- **Week 7-8**: Production deployment

### Rollback Strategy
- Keep previous deployment tagged
- Blue-green deployment for zero downtime
- Database migrations reversible
- Feature flags for gradual rollout

## Success Criteria

### Technical
- ✅ All 4 phases complete
- ✅ Test coverage ≥80%
- ✅ No security violations
- ✅ Lineage coverage 100%

### Business
- ✅ Month-end close automated
- ✅ BIR compliance 100% on-time
- ✅ Manual interventions <5%
- ✅ Audit queries <1 hour

## Version History

- **v1.0.0** (2025-11-24): Initial implementation plan
  - 4-phase roadmap defined
  - 8-week timeline set
  - Acceptance criteria specified
