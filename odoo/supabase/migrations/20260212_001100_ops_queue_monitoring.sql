-- ============================================================================
-- ops.* Queue + Monitoring Schema
-- ============================================================================
-- Purpose: Build queue, metrics, advisories, upgrades
-- Spec: /spec/odooops-platform/odooops-console-PRD.md
-- Created: 2026-02-12
-- ============================================================================

-- ============================================================================
-- ops.run_queue - Build execution queue
-- ============================================================================
create table ops.run_queue (
  id uuid primary key default gen_random_uuid(),
  build_id uuid not null references ops.builds(id) on delete cascade,
  status text not null default 'queued' check (status in ('queued', 'claimed', 'running', 'done', 'failed')),
  priority int not null default 5,
  claimed_by text,
  claimed_at timestamptz,
  attempts int not null default 0,
  max_attempts int not null default 3,
  next_attempt_at timestamptz,
  error_message text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),

  constraint valid_priority check (priority between 1 and 10)
);

create index ops_run_queue_status_idx on ops.run_queue(status);
create index ops_run_queue_next_attempt_idx on ops.run_queue(coalesce(next_attempt_at, created_at)) where status in ('queued', 'claimed');
create index ops_run_queue_build_id_idx on ops.run_queue(build_id);

comment on table ops.run_queue is 'Build execution queue (FIFO with priority)';
comment on column ops.run_queue.priority is '1=highest, 10=lowest';

-- ============================================================================
-- ops.metrics - Timeseries metrics
-- ============================================================================
create table ops.metrics (
  id bigserial primary key,
  project_id uuid not null references ops.projects(id) on delete cascade,
  branch_id uuid references ops.branches(id) on delete set null,
  ts timestamptz not null,
  metric text not null check (metric in ('cpu_pct', 'mem_mb', 'req_rate', 'err_rate', 'p95_ms', 'db_conn', 'queue_depth', 'disk_mb')),
  value numeric not null,
  dims jsonb not null default '{}'::jsonb,

  constraint valid_metric_value check (value >= 0)
);

create index ops_metrics_proj_metric_ts_idx on ops.metrics(project_id, metric, ts desc);
create index ops_metrics_branch_idx on ops.metrics(branch_id) where branch_id is not null;

comment on table ops.metrics is 'Timeseries performance metrics';
comment on column ops.metrics.dims is 'Dimensions (e.g., {"host": "worker-1"})';

-- ============================================================================
-- ops.monitoring - Current monitoring snapshot
-- ============================================================================
create table ops.monitoring (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references ops.projects(id) on delete cascade,
  branch_id uuid not null references ops.branches(id) on delete cascade,
  status text not null check (status in ('healthy', 'warning', 'critical', 'unknown')),
  cpu_usage_pct numeric,
  memory_usage_mb numeric,
  disk_usage_mb numeric,
  request_rate numeric,
  error_rate numeric,
  last_health_check timestamptz,
  alerts jsonb not null default '[]'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),

  constraint unique_branch_monitoring unique(branch_id)
);

create index ops_monitoring_project_id_idx on ops.monitoring(project_id);
create index ops_monitoring_status_idx on ops.monitoring(status);

comment on table ops.monitoring is 'Current monitoring state per branch';
comment on column ops.monitoring.alerts is 'Active alert array';

-- ============================================================================
-- ops.advisories - Azure Advisor-like recommendations
-- ============================================================================
create table ops.advisories (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references ops.projects(id) on delete cascade,
  severity text not null check (severity in ('info', 'warning', 'critical')),
  category text not null check (category in ('security', 'performance', 'reliability', 'cost', 'upgrade', 'best-practice')),
  title text not null,
  recommendation text not null,
  evidence jsonb not null default '{}'::jsonb,
  status text not null default 'open' check (status in ('open', 'snoozed', 'resolved', 'dismissed')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  resolved_at timestamptz,
  snoozed_until timestamptz,
  resolved_by uuid references auth.users(id) on delete set null
);

create index ops_advisories_project_id_status_idx on ops.advisories(project_id, status);
create index ops_advisories_severity_idx on ops.advisories(severity);
create index ops_advisories_category_idx on ops.advisories(category);

comment on table ops.advisories is 'Automated recommendations (Azure Advisor-like)';
comment on column ops.advisories.evidence is 'Supporting data for recommendation';

-- ============================================================================
-- ops.upgrades - Version upgrade tracking
-- ============================================================================
create table ops.upgrades (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references ops.projects(id) on delete cascade,
  from_version text not null,
  to_version text not null,
  status text not null default 'planned' check (status in ('planned', 'in_progress', 'completed', 'failed', 'rolled_back')),
  started_at timestamptz,
  completed_at timestamptz,
  error_message text,
  rollback_plan jsonb,
  created_by uuid references auth.users(id) on delete set null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index ops_upgrades_project_id_idx on ops.upgrades(project_id);
create index ops_upgrades_status_idx on ops.upgrades(status);

comment on table ops.upgrades is 'Odoo version upgrade tracking';

-- ============================================================================
-- Triggers
-- ============================================================================
create trigger ops_run_queue_updated_at
  before update on ops.run_queue
  for each row
  execute function ops.set_updated_at();

create trigger ops_monitoring_updated_at
  before update on ops.monitoring
  for each row
  execute function ops.set_updated_at();

create trigger ops_advisories_updated_at
  before update on ops.advisories
  for each row
  execute function ops.set_updated_at();

create trigger ops_upgrades_updated_at
  before update on ops.upgrades
  for each row
  execute function ops.set_updated_at();

-- ============================================================================
-- Grants
-- ============================================================================
grant all on all tables in schema ops to authenticated;
grant all on all sequences in schema ops to authenticated;
