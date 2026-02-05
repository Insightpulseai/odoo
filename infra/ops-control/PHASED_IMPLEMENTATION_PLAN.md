# 🎯 Ops Control Room - Phased Implementation Plan

**Vision:** Transform the Ops Control Room into a production-grade, deterministic agent runtime that compiles specs/docs into executable, verifiable plans with MCP-native tools, deployed across Vercel/DigitalOcean/Supabase, with GitHub-enforced gates.

**Current State:** ✅ Parallel execution engine (sessions + lanes), Runboard UI, basic runbook system, Supabase backend with public schema.

**Target State:** Full "Pulser SDK" architecture - compiler + runtime protocol with MCP tools, skill system, verification steps, doc→code pipelines, and production deployment patterns for Odoo CE/OCA + Vercel + DigitalOcean.

---

## 📊 Implementation Phases Overview

| Phase | Focus | Duration | Status |
|-------|-------|----------|--------|
| **Phase 0** | Foundation Hardening | 1-2 weeks | 🟢 Mostly Complete |
| **Phase 1** | Core Execution Engine | 2-3 weeks | 🟡 In Progress |
| **Phase 2** | MCP Tool Integration | 2-3 weeks | ⚪ Not Started |
| **Phase 3** | Skill System + Compiler | 3-4 weeks | ⚪ Not Started |
| **Phase 4** | Verification + Proofs | 2-3 weeks | ⚪ Not Started |
| **Phase 5** | Doc→Code Pipelines | 3-4 weeks | ⚪ Not Started |
| **Phase 6** | Odoo Extender (IPAI) | 4-5 weeks | ⚪ Not Started |
| **Phase 7** | CI/CD + GitHub Gates | 2-3 weeks | ⚪ Not Started |
| **Phase 8** | Production Hardening | 2-3 weeks | ⚪ Not Started |

**Total Estimated Time:** 21-30 weeks (5-7 months)

---

## Phase 0: Foundation Hardening ✅ (90% Complete)

**Goal:** Stabilize current parallel execution system, fix schema issues, ensure robust run claiming.

### ✅ Completed
- [x] Migrate from `ops` schema to `public` schema (PostgREST compatibility)
- [x] Sessions table with intent tracking
- [x] Runs table with lanes (A/B/C/D), claiming, heartbeat
- [x] Atomic run claiming via `SKIP LOCKED` pattern
- [x] Runboard UI with session management
- [x] Real-time subscriptions for run events
- [x] Run steps table for granular execution tracking
- [x] Edge function executor with heartbeat loop
- [x] Basic templates system

### ⚠️ Remaining (1-2 days)
- [ ] Fix Runboard realtime subscription (still using `ops` schema reference)
- [ ] Add run cancellation UI feedback (toast notifications)
- [ ] Add lane priority controls (allow user to set priority per run)
- [ ] Add session archiving (archive completed sessions to reduce clutter)
- [ ] Add run filtering by status/lane/session
- [ ] Add basic error recovery (auto-retry failed runs with backoff)

### 📦 Deliverables
- Stable multi-lane execution
- No schema errors
- Reliable claiming/heartbeat
- Clean Runboard UX

---

## Phase 1: Core Execution Engine 🟡 (Current Focus)

**Goal:** Build the "Pulser IR" (intermediate representation) - structured plans with steps, inputs, outputs, verifiers.

### Tasks (2-3 weeks)

#### 1.1 Define Pulser IR Types (2-3 days)
Create `/src/core/pulser-types.ts`:
```typescript
// Core Pulser primitives
export interface Tool {
  id: string;
  kind: 'mcp' | 'http' | 'shell' | 'sql';
  name: string;
  description: string;
  inputSchema: JsonSchema;
  outputSchema: JsonSchema;
  preconditions?: string[]; // e.g., "docker_running", "github_token_set"
  verifiers?: string[]; // e.g., "check_http_200", "validate_json_schema"
}

export interface Skill {
  id: string;
  slug: string;
  name: string;
  description: string;
  tools: string[]; // tool IDs
  constraints: Record<string, any>; // e.g., max_runtime, allowed_envs
  inputSchema: JsonSchema;
  outputSchema: JsonSchema;
  verifiers: Verifier[];
}

export interface Plan {
  id: string;
  version: string; // e.g., "1.0.0"
  created_at: string;
  kind: string; // deploy, spec, incident, etc.
  title: string;
  description: string;
  steps: Step[];
  inputs: Record<string, any>;
  expectedOutputs: Record<string, any>;
  metadata: {
    source?: string; // e.g., "doc:prd.md", "template:deploy-vercel"
    author?: string;
    tags?: string[];
  };
}

export interface Step {
  id: string;
  idx: number;
  title: string;
  description?: string;
  kind: 'tool' | 'skill' | 'system';
  tool?: string; // tool ID if kind=tool
  skill?: string; // skill ID if kind=skill
  action: string;
  args: Record<string, any>;
  preconditions: string[]; // must pass before execution
  verifiers: Verifier[]; // must pass after execution
  retryPolicy?: RetryPolicy;
  timeoutMs?: number;
  dependsOn?: string[]; // step IDs
}

export interface Verifier {
  id: string;
  kind: 'http' | 'shell' | 'sql' | 'json_schema' | 'custom';
  description: string;
  config: Record<string, any>;
  required: boolean; // if false, log warning but don't fail
}

export interface RetryPolicy {
  maxAttempts: number;
  backoffMs: number;
  backoffMultiplier: number;
}

export interface RunProof {
  run_id: string;
  step_id: string;
  verifier_id: string;
  passed: boolean;
  timestamp: string;
  evidence: any; // logs, HTTP responses, etc.
}
```

#### 1.2 Upgrade Database Schema (1 day)
Create `/supabase/migrations/20250109000000_pulser_ir.sql`:
```sql
-- Tools registry
create table if not exists public.tools (
  id uuid primary key default gen_random_uuid(),
  slug text not null unique,
  kind text not null check (kind in ('mcp','http','shell','sql')),
  name text not null,
  description text not null,
  input_schema jsonb not null,
  output_schema jsonb not null,
  preconditions jsonb not null default '[]'::jsonb,
  verifiers jsonb not null default '[]'::jsonb,
  created_at timestamptz not null default now()
);

-- Skills registry
create table if not exists public.skills (
  id uuid primary key default gen_random_uuid(),
  slug text not null unique,
  name text not null,
  description text not null,
  tools jsonb not null default '[]'::jsonb, -- array of tool IDs
  constraints jsonb not null default '{}'::jsonb,
  input_schema jsonb not null,
  output_schema jsonb not null,
  verifiers jsonb not null default '[]'::jsonb,
  created_at timestamptz not null default now()
);

-- Plans (compiled from docs/specs/templates)
create table if not exists public.plans (
  id uuid primary key default gen_random_uuid(),
  version text not null default '1.0.0',
  kind text not null,
  title text not null,
  description text not null,
  steps jsonb not null, -- array of Step objects
  inputs jsonb not null default '{}'::jsonb,
  expected_outputs jsonb not null default '{}'::jsonb,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

-- Run proofs (verification evidence)
create table if not exists public.run_proofs (
  id uuid primary key default gen_random_uuid(),
  run_id uuid not null references public.runs(id) on delete cascade,
  step_id text not null,
  verifier_id text not null,
  passed boolean not null,
  evidence jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create index idx_run_proofs_run_id on public.run_proofs(run_id);
create index idx_run_proofs_passed on public.run_proofs(passed);

-- Add plan_id reference to runs
alter table public.runs add column if not exists plan_id uuid references public.plans(id) on delete set null;

-- RLS policies
alter table public.tools enable row level security;
alter table public.skills enable row level security;
alter table public.plans enable row level security;
alter table public.run_proofs enable row level security;

create policy tools_select_anon on public.tools for select to anon using (true);
create policy skills_select_anon on public.skills for select to anon using (true);
create policy plans_select_anon on public.plans for select to anon using (true);
create policy proofs_select_anon on public.run_proofs for select to anon using (true);
create policy proofs_insert_anon on public.run_proofs for insert to anon with check (true);
```

#### 1.3 Upgrade Executor to Use Plans (3-4 days)
- Modify `/supabase/functions/ops-executor/index.ts`:
  - Load plan from `plans` table (if plan_id set) or generate from template
  - Execute steps in DAG order (respect `dependsOn`)
  - Run preconditions before each step (fail fast if precondition fails)
  - Execute step (tool call / skill invocation / system action)
  - Run verifiers after each step (record proofs)
  - Generate provenance artifacts with full proof chain

#### 1.4 Add Plan Compiler Stub (2-3 days)
Create `/src/core/compiler.ts`:
```typescript
/**
 * Compiler: Doc/Spec/Template → Plan
 * 
 * Phase 1: Simple template-based compilation
 * Phase 3: Full doc→code AI-powered compilation
 */

export interface CompilerInput {
  kind: 'template' | 'spec' | 'doc';
  source: string; // template slug, spec path, or doc URL
  context?: Record<string, any>;
}

export async function compilePlan(input: CompilerInput): Promise<Plan> {
  if (input.kind === 'template') {
    return compileFromTemplate(input.source, input.context);
  } else if (input.kind === 'spec') {
    // Phase 3: parse spec files → plan
    throw new Error('Spec compilation not yet implemented');
  } else {
    // Phase 5: doc → spec → plan
    throw new Error('Doc compilation not yet implemented');
  }
}

async function compileFromTemplate(slug: string, context: any): Promise<Plan> {
  // Load template from DB
  // Interpolate context variables
  // Return structured Plan object
}
```

#### 1.5 UI Updates (2-3 days)
- Add "Plan Viewer" component (shows step DAG, preconditions, verifiers)
- Add "Proof Viewer" component (shows verification results per step)
- Update RunbookCard to show plan structure
- Add "Compile" button to Templates tab (template → plan → run)

### 📦 Deliverables
- Structured Plan/Step/Tool/Skill types
- Database tables for plans, tools, skills, proofs
- Executor runs plans with verifiers
- UI shows plan structure and verification results

---

## Phase 2: MCP Tool Integration ⚪

**Goal:** Make MCP servers "native" - discover, invoke, and verify MCP tools as first-class primitives.

### Tasks (2-3 weeks)

#### 2.1 MCP Client Library (3-4 days)
Create `/src/lib/mcp-client.ts`:
```typescript
/**
 * MCP Client for Ops Control Room
 * Connects to MCP servers (Desktop Commander, GitHub, Docker, K8s, etc.)
 */

export interface McpServer {
  id: string;
  name: string;
  transport: 'stdio' | 'sse' | 'websocket';
  command?: string; // for stdio
  url?: string; // for sse/websocket
  env?: Record<string, string>;
}

export interface McpTool {
  server_id: string;
  name: string;
  description: string;
  inputSchema: JsonSchema;
}

export class McpClient {
  async connect(server: McpServer): Promise<void>;
  async listTools(serverId: string): Promise<McpTool[]>;
  async invokeTool(serverId: string, toolName: string, args: any): Promise<any>;
  async disconnect(serverId: string): Promise<void>;
}
```

#### 2.2 MCP Server Registry (2 days)
- Add `mcp_servers` table to database
- Seed with standard servers:
  - Desktop Commander (shell/desktop automation)
  - GitHub Official (repos, PRs, actions)
  - Docker (containers, images, compose)
  - Kubernetes (deployments, pods, services)
- Add UI for managing MCP servers (Settings tab)

#### 2.3 Tool Discovery Pipeline (3-4 days)
- Background job that connects to each MCP server
- Fetches tool list via `tools/list`
- Syncs to `tools` table (mark kind='mcp', store server_id)
- Run on startup + periodic refresh (every 5 mins)

#### 2.4 Executor MCP Bridge (3-4 days)
Modify executor to handle `kind='mcp'` tools:
```typescript
if (step.kind === 'tool' && tool.kind === 'mcp') {
  const server = await getServerForTool(tool.id);
  const result = await mcpClient.invokeTool(
    server.id,
    tool.name,
    step.args
  );
  
  // Store result as event + artifact
  await emitEvent(sb, run_id, 'info', phase, 'MCP tool result', { result });
  
  // Run verifiers
  for (const verifier of step.verifiers) {
    const proof = await runVerifier(verifier, result);
    await insertProof(sb, run_id, step.id, verifier.id, proof);
  }
}
```

#### 2.5 Sandboxing + Allowlists (2 days)
- Add `allowed_tools` field to runs/sessions
- Enforce tool allowlist in executor (fail if tool not in list)
- Add UI for setting tool allowlists per session

### 📦 Deliverables
- MCP client library
- MCP server registry
- Tool discovery sync
- Executor invokes MCP tools
- Tool sandboxing/allowlists

---

## Phase 3: Skill System + Compiler ⚪

**Goal:** Define reusable "skills" (bundles of tools + constraints + verifiers) and compile docs/specs into plans.

### Tasks (3-4 weeks)

#### 3.1 Skill Archetypes (1 week)
Create stock skills in `/src/core/skills/`:

**`repo_mutation.ts`** - Patch files + open PR + CI proofs
```typescript
export const repoMutationSkill: Skill = {
  id: 'skill:repo_mutation',
  slug: 'repo-mutation',
  name: 'Repository Mutation',
  description: 'Clone repo, apply patches, run tests, open PR',
  tools: ['mcp:github:clone', 'mcp:github:create_pr', 'shell:git'],
  constraints: {
    max_runtime_ms: 300000, // 5 mins
    allowed_envs: ['dev', 'staging'],
  },
  inputSchema: {
    type: 'object',
    required: ['repo', 'branch', 'patches'],
    properties: {
      repo: { type: 'string' },
      branch: { type: 'string' },
      patches: { type: 'array', items: { type: 'string' } },
    },
  },
  outputSchema: {
    type: 'object',
    properties: {
      pr_url: { type: 'string' },
      pr_number: { type: 'number' },
      ci_status: { type: 'string', enum: ['pending', 'success', 'failure'] },
    },
  },
  verifiers: [
    {
      id: 'verify_pr_created',
      kind: 'http',
      description: 'Verify PR was created',
      config: { url: '{{outputs.pr_url}}', expectedStatus: 200 },
      required: true,
    },
    {
      id: 'verify_ci_green',
      kind: 'custom',
      description: 'Wait for CI to pass',
      config: { timeout_ms: 120000 },
      required: false,
    },
  ],
};
```

Create 5-7 standard skills:
1. `repo_mutation` (above)
2. `infra_deploy` (build + push + deploy + health checks)
3. `db_migration` (generate + apply migrations + RLS checks)
4. `odoo_addon` (scaffold + upgrade + install + view validation)
5. `doc_to_code` (extract requirements + generate spec + compile plan)
6. `reverse_engineer` (capability map + token extraction + component inventory)
7. `eval_qa` (TestSprite-style gates + regression checks)

#### 3.2 Skill Executor (3-4 days)
When step `kind='skill'`:
- Load skill definition
- Check constraints (runtime, allowed envs)
- Execute skill's internal steps (orchestration)
- Aggregate verifiers
- Return structured output

#### 3.3 Spec Kit Parser (1 week)
Create `/src/core/spec-parser.ts`:
```typescript
/**
 * Parse Spec Kit bundle:
 * - spec/<slug>/constitution.md
 * - spec/<slug>/prd.md
 * - spec/<slug>/plan.md
 * - spec/<slug>/tasks.md
 * 
 * Output: Plan with steps
 */

export interface SpecBundle {
  slug: string;
  constitution: string;
  prd: string;
  plan: string;
  tasks: string;
}

export async function parseSpecBundle(bundle: SpecBundle): Promise<Plan> {
  // Extract domain objects from PRD
  const entities = extractEntities(bundle.prd);
  
  // Extract workflow steps from plan
  const steps = extractSteps(bundle.plan);
  
  // Extract tasks from tasks.md
  const tasks = extractTasks(bundle.tasks);
  
  // Map to Plan structure
  return compilePlanFromSpec({ entities, steps, tasks });
}
```

#### 3.4 AI-Powered Compiler (1 week)
Integrate LLM to compile natural language → Plan:
```typescript
export async function compileFromDoc(doc: string, context: any): Promise<Plan> {
  // Use Claude/GPT to parse doc
  const prompt = `
You are a runbook compiler. Given this document, generate a structured execution plan.

Document:
${doc}

Context:
${JSON.stringify(context)}

Output a JSON Plan with steps, tools, verifiers.
`;

  const response = await callLLM(prompt);
  const plan = JSON.parse(response);
  
  // Validate plan structure
  validatePlan(plan);
  
  return plan;
}
```

### 📦 Deliverables
- 5-7 stock skill definitions
- Skill executor
- Spec Kit parser
- AI-powered compiler (doc → plan)

---

## Phase 4: Verification + Proofs ⚪

**Goal:** Make verification mandatory and artifact-backed. Every step must prove it worked.

### Tasks (2-3 weeks)

#### 4.1 Verifier Types (1 week)
Implement verifiers in `/src/core/verifiers/`:

1. **HTTP Verifier** - Check HTTP endpoint returns expected status/body
2. **Shell Verifier** - Run shell command, check exit code
3. **SQL Verifier** - Run SQL query, check result
4. **JSON Schema Verifier** - Validate output matches schema
5. **Checksum Verifier** - Verify file/artifact hash
6. **Custom Verifier** - User-defined verification logic

#### 4.2 Proof Chain (3-4 days)
- Every step execution generates proof records
- Proofs include: timestamp, passed/failed, evidence (logs/responses)
- Aggregate proofs into "proof bundle" artifact
- Add "Proof Viewer" UI component

#### 4.3 Rollback Support (3-4 days)
- Add `rollback()` method to destructive steps
- Track rollback steps in plan
- If verification fails, run rollback chain
- Example: if deploy fails health check, rollback to previous version

#### 4.4 CI Gates (2-3 days)
- Add "CI Gate" verifier type
- Waits for GitHub Actions workflow to complete
- Fetches CI logs/status
- Fails step if CI fails

### 📦 Deliverables
- 6+ verifier types implemented
- Proof chain generation
- Rollback support
- CI gate integration

---

## Phase 5: Doc→Code Pipelines ⚪

**Goal:** Full "doc → spec → plan → code → PR → CI → deploy" automation.

### Tasks (3-4 weeks)

#### 5.1 Document Ingestion (1 week)
- Support multiple doc formats: Markdown, PDF, DOCX, URLs, screenshots
- OCR for images (already have `/workers/ocr-worker.ts`)
- Store in `documents` table

#### 5.2 Requirement Extraction (1 week)
Use LLM to extract:
- Domain objects (entities, fields, relationships)
- Workflows (user stories, screens, actions)
- Integrations (APIs, databases, external systems)
- Constraints (security, performance, compliance)

#### 5.3 Code Generation (1 week)
- Odoo: models/views/actions/security
- Supabase: tables/RLS/edge functions
- Vercel/Next.js: pages/components/API routes
- Generate GitHub PR with all artifacts

#### 5.4 Deployment Pipeline (3-4 days)
- Run CI (lint, test, build)
- Deploy to staging
- Run health checks
- Tag for production if successful

### 📦 Deliverables
- Doc ingestion (markdown/PDF/URL/screenshots)
- Requirement extraction
- Code generation for Odoo/Supabase/Vercel
- Full deployment pipeline

---

## Phase 6: Odoo Extender (IPAI) ⚪

**Goal:** Implement the full "IPAI Odoo CE/OCA Extender + Doc→Code Reverse Engineer" skill spec.

### Tasks (4-5 weeks)

#### 6.1 Odoo Module Scaffold (1 week)
Skill: Generate complete Odoo addon structure:
- `__manifest__.py` with correct deps, data, assets, security
- `models/` (Python classes)
- `views/` (XML - list/form, actions)
- `security/` (ir.model.access.csv, record rules)
- `static/` (icons, JS/CSS assets)

#### 6.2 Odoo 18/19 Compatibility (3-4 days)
- Enforce `<list>` instead of `<tree>`
- Enforce `view_mode="list,form"`
- Validate XML against Odoo 18/19 schema

#### 6.3 OCA Dependency Manager (3-4 days)
- Detect OCA modules needed
- Generate install order
- Add to `__manifest__.py` dependencies

#### 6.4 Docker Compose Generator (1 week)
Generate `/docker/odoo/docker-compose.yml`:
```yaml
version: '3.8'
services:
  odoo:
    image: odoo:18
    ports:
      - "8069:8069"
    volumes:
      - ./addons/ipai:/mnt/extra-addons
      - odoo-data:/var/lib/odoo
    environment:
      - POSTGRES_HOST=postgres
      - POSTGRES_USER=odoo
      - POSTGRES_PASSWORD=odoo
  postgres:
    image: postgres:15
    volumes:
      - postgres-data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=odoo
      - POSTGRES_USER=odoo
      - POSTGRES_PASSWORD=odoo
volumes:
  odoo-data:
  postgres-data:
```

#### 6.5 DigitalOcean Deploy (1 week)
- Generate SSH deploy script
- Support droplet + DOKS (Kubernetes)
- Health checks (verify Odoo container running, modules installed)

#### 6.6 Reverse Engineering (1 week)
Given competitor URL/screenshots/docs:
1. Extract capability map (features → workflows → permissions → data objects)
2. Extract design tokens (colors/typography/spacing)
3. Generate Odoo models/views
4. Generate Supabase schema (if needed)
5. Generate web UI (if needed)
6. Generate Spec Kit docs

### 📦 Deliverables
- Odoo addon generator
- OCA dependency manager
- Docker Compose generator
- DigitalOcean deploy scripts
- Reverse engineering pipeline

---

## Phase 7: CI/CD + GitHub Gates ⚪

**Goal:** Enforce "no merge without CI green" and deterministic verification.

### Tasks (2-3 weeks)

#### 7.1 GitHub Actions Templates (1 week)
Generate workflow files:

**`.github/workflows/ci.yml`** - Web app CI
**`.github/workflows/odoo-module-gates.yml`** - Odoo validation
**`.github/workflows/supabase-check.yml`** - Migration lint
**`.github/workflows/do-deploy.yml`** - Deploy to droplet

#### 7.2 PR Creation Skill (3-4 days)
- Create branch
- Commit artifacts (code, migrations, workflows)
- Open PR with description
- Request reviews
- Link to runbook run (provenance)

#### 7.3 Status Checks Integration (3-4 days)
- Fetch CI status from GitHub API
- Display in Runboard UI
- Block merge if CI fails
- Auto-merge if CI passes (optional)

#### 7.4 Deployment Hooks (2-3 days)
- Trigger Vercel deploy on merge
- Trigger Supabase migration on merge
- Trigger DigitalOcean deploy via SSH

### 📦 Deliverables
- GitHub Actions workflow generators
- PR creation skill
- CI status integration
- Auto-deploy hooks

---

## Phase 8: Production Hardening ⚪

**Goal:** Make the system production-ready with auth, multi-tenancy, observability, and resilience.

### Tasks (2-3 weeks)

#### 8.1 Authentication (3-4 days)
- Add Supabase Auth (email/password, OAuth)
- Replace anon policies with authenticated RLS
- Add user_id to runs/sessions/plans

#### 8.2 Multi-Tenancy (3-4 days)
- Add `organizations` table
- Add `org_id` to all tables
- RLS policies scoped to org
- Invite/team management UI

#### 8.3 Observability (3-4 days)
- Centralized logging (send to external service)
- Metrics dashboard (run success rate, latency, tool usage)
- Alerting (Slack/Discord webhooks for failures)

#### 8.4 Secrets Management (2 days)
- Store API keys in Supabase Vault
- Reference secrets in plans (not hardcoded)
- Add secrets UI (Settings tab)

#### 8.5 Rate Limiting (2 days)
- Prevent runaway runs (max 10 concurrent per user)
- Tool call rate limits (per MCP server)
- Edge function throttling

#### 8.6 Audit Logs (2 days)
- Append-only audit log table
- Record all mutations (runs, plans, tools)
- Export to CSV/JSON

### 📦 Deliverables
- Auth + multi-tenancy
- Observability dashboard
- Secrets management
- Rate limiting
- Audit logs

---

## 🎯 Success Metrics

### Phase Completion Criteria
Each phase is complete when:
1. ✅ All tasks implemented and tested
2. ✅ Database migrations applied
3. ✅ UI components working
4. ✅ Edge functions deployed
5. ✅ Documentation updated
6. ✅ Demo video recorded

### System Health Metrics
- **Uptime:** >99.5%
- **Run Success Rate:** >90%
- **Median Run Time:** <2 minutes (for typical deploy)
- **P95 Run Time:** <10 minutes
- **Tool Availability:** >95%
- **Verifier Pass Rate:** >95%

---

## 🛠️ Tech Stack Summary

### Frontend (Figma Make)
- React 18 + TypeScript
- Tailwind CSS v4
- Shadcn UI components
- Recharts (for metrics)
- Lucide React (icons)
- Supabase JS client

### Backend (Supabase)
- PostgreSQL 15 (public schema)
- Row Level Security (RLS)
- Edge Functions (Deno)
- Realtime subscriptions
- Storage (for artifacts)

### Integrations
- **MCP Servers:** Desktop Commander, GitHub, Docker, Kubernetes
- **Deployment Targets:** Vercel, DigitalOcean (droplets + DOKS), Supabase
- **CI/CD:** GitHub Actions
- **Odoo:** CE 18/19 + OCA modules
- **Observability:** Logs, metrics, alerts

---

## 📚 Documentation Structure

```
/docs
├── architecture/
│   ├── pulser-ir.md          # Intermediate representation spec
│   ├── execution-model.md    # How runs are executed
│   ├── verification.md       # Verifier patterns
│   └── mcp-integration.md    # MCP tool usage
├── skills/
│   ├── repo-mutation.md
│   ├── infra-deploy.md
│   ├── odoo-addon.md
│   └── reverse-engineer.md
├── deployment/
│   ├── vercel.md
│   ├── digitalocean.md
│   ├── supabase.md
│   └── github-actions.md
├── api/
│   ├── supabase-functions.md
│   ├── mcp-client.md
│   └── compiler-api.md
└── guides/
    ├── quickstart.md
    ├── creating-skills.md
    ├── writing-verifiers.md
    └── troubleshooting.md
```

---

## 🚀 Quick Start (After Phase 8)

```bash
# 1. Clone repo
git clone <repo> && cd ops-control-room

# 2. Install dependencies
npm install

# 3. Set up environment
cp .env.example .env
# Edit .env with your credentials

# 4. Deploy to Supabase
supabase db push
supabase functions deploy

# 5. Start dev server
npm run dev

# 6. Create your first runbook
# Open UI → Templates → Select "Deploy Vercel App" → Run

# 7. Watch execution in Runboard
# Switch to Runboard tab → See lanes A/B/C/D → Real-time logs
```

---

## 🎓 Learning Path (For Team Onboarding)

### Week 1: Core Concepts
- Read: Pulser IR spec
- Read: Execution model
- Read: MCP integration guide
- Exercise: Run a template, inspect logs

### Week 2: Creating Skills
- Read: Skill archetypes
- Read: Writing verifiers
- Exercise: Create a custom skill for your use case

### Week 3: Doc→Code Pipelines
- Read: Compiler API
- Read: Spec Kit format
- Exercise: Generate Odoo addon from PRD

### Week 4: Production Operations
- Read: Deployment guides
- Read: Troubleshooting
- Exercise: Deploy to DigitalOcean + Vercel

---

## 📞 Support & Resources

### Internal Documentation
- **Architecture Docs:** `/docs/architecture/`
- **API Reference:** `/docs/api/`
- **Guides:** `/docs/guides/`

### External Resources
- **Supabase Docs:** https://supabase.com/docs
- **MCP Spec:** https://spec.modelcontextprotocol.io
- **Odoo Docs:** https://www.odoo.com/documentation/18.0/developer.html
- **Vercel Docs:** https://vercel.com/docs
- **DigitalOcean Docs:** https://docs.digitalocean.com

### Community
- **Discord:** [link to server]
- **GitHub Discussions:** [link to discussions]
- **Office Hours:** Weekly Thursdays 2pm PT

---

## 🎉 Vision Recap

By the end of Phase 8, the Ops Control Room will be:

✅ **Deterministic** - Every run is replayable from plan
✅ **Verifiable** - Every step proves it worked
✅ **Portable** - Runs on Codex CLI, Claude Code, Supabase
✅ **MCP-Native** - First-class tool integration
✅ **Doc→Code** - Natural language → production code
✅ **Multi-Platform** - Deploy to Vercel, DO, Supabase, Odoo
✅ **CI-Enforced** - GitHub gates prevent bad merges
✅ **Audit-Ready** - Full provenance chain
✅ **Production-Grade** - Auth, multi-tenancy, observability

**The result:** A "secure delegated executor" that turns messy user intents into deterministic, tool-backed, verified workflows - deployable across your entire stack.

---

**Next Step:** Review this plan, prioritize phases, and let's start building! 🚀
