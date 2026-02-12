-- ============================================================================
-- ops.* RLS Policies
-- ============================================================================
-- Purpose: Row-Level Security for ops schema
-- Spec: /spec/odooops-platform/odooops-console-PRD.md
-- Created: 2026-02-12
-- ============================================================================

-- Enable RLS on all ops tables
alter table ops.projects enable row level security;
alter table ops.branches enable row level security;
alter table ops.builds enable row level security;
alter table ops.build_events enable row level security;
alter table ops.artifacts enable row level security;
alter table ops.run_queue enable row level security;
alter table ops.metrics enable row level security;
alter table ops.monitoring enable row level security;
alter table ops.advisories enable row level security;
alter table ops.upgrades enable row level security;

-- ============================================================================
-- Projects - org member visibility
-- ============================================================================
drop policy if exists projects_select on ops.projects;
create policy projects_select on ops.projects
for select using (
  org_id in (select ops.my_org_ids())
);

drop policy if exists projects_insert on ops.projects;
create policy projects_insert on ops.projects
for insert with check (
  org_id in (select ops.my_org_ids())
);

drop policy if exists projects_update on ops.projects;
create policy projects_update on ops.projects
for update using (
  org_id in (select ops.my_org_ids())
);

-- ============================================================================
-- Branches - via project org
-- ============================================================================
drop policy if exists branches_select on ops.branches;
create policy branches_select on ops.branches
for select using (
  exists (
    select 1
    from ops.projects p
    where p.id = ops.branches.project_id
      and p.org_id in (select ops.my_org_ids())
  )
);

drop policy if exists branches_insert on ops.branches;
create policy branches_insert on ops.branches
for insert with check (
  exists (
    select 1
    from ops.projects p
    where p.id = ops.branches.project_id
      and p.org_id in (select ops.my_org_ids())
  )
);

drop policy if exists branches_update on ops.branches;
create policy branches_update on ops.branches
for update using (
  exists (
    select 1
    from ops.projects p
    where p.id = ops.branches.project_id
      and p.org_id in (select ops.my_org_ids())
  )
);

-- ============================================================================
-- Builds - via project org
-- ============================================================================
drop policy if exists builds_select on ops.builds;
create policy builds_select on ops.builds
for select using (
  exists (
    select 1
    from ops.branches b
    join ops.projects p on b.project_id = p.id
    where b.id = ops.builds.branch_id
      and p.org_id in (select ops.my_org_ids())
  )
);

drop policy if exists builds_insert on ops.builds;
create policy builds_insert on ops.builds
for insert with check (
  exists (
    select 1
    from ops.branches b
    join ops.projects p on b.project_id = p.id
    where b.id = ops.builds.branch_id
      and p.org_id in (select ops.my_org_ids())
  )
);

drop policy if exists builds_update on ops.builds;
create policy builds_update on ops.builds
for update using (
  exists (
    select 1
    from ops.branches b
    join ops.projects p on b.project_id = p.id
    where b.id = ops.builds.branch_id
      and p.org_id in (select ops.my_org_ids())
  )
);

-- ============================================================================
-- Build Events - via build's project org
-- ============================================================================
drop policy if exists build_events_select on ops.build_events;
create policy build_events_select on ops.build_events
for select using (
  exists (
    select 1
    from ops.builds bu
    join ops.branches b on bu.branch_id = b.id
    join ops.projects p on b.project_id = p.id
    where bu.id = ops.build_events.build_id
      and p.org_id in (select ops.my_org_ids())
  )
);

-- Allow service_role to insert events (for build runners)
drop policy if exists build_events_insert_service on ops.build_events;
create policy build_events_insert_service on ops.build_events
for insert with check (
  auth.jwt()->>'role' = 'service_role'
  or exists (
    select 1
    from ops.builds bu
    join ops.branches b on bu.branch_id = b.id
    join ops.projects p on b.project_id = p.id
    where bu.id = ops.build_events.build_id
      and p.org_id in (select ops.my_org_ids())
  )
);

-- ============================================================================
-- Artifacts - via build's project org
-- ============================================================================
drop policy if exists artifacts_select on ops.artifacts;
create policy artifacts_select on ops.artifacts
for select using (
  exists (
    select 1
    from ops.builds bu
    join ops.branches b on bu.branch_id = b.id
    join ops.projects p on b.project_id = p.id
    where bu.id = ops.artifacts.build_id
      and p.org_id in (select ops.my_org_ids())
  )
);

drop policy if exists artifacts_insert on ops.artifacts;
create policy artifacts_insert on ops.artifacts
for insert with check (
  exists (
    select 1
    from ops.builds bu
    join ops.branches b on bu.branch_id = b.id
    join ops.projects p on b.project_id = p.id
    where bu.id = ops.artifacts.build_id
      and p.org_id in (select ops.my_org_ids())
  )
);

-- ============================================================================
-- Run Queue - service_role only (build runners)
-- ============================================================================
drop policy if exists run_queue_service_all on ops.run_queue;
create policy run_queue_service_all on ops.run_queue
for all using (
  auth.jwt()->>'role' = 'service_role'
);

-- ============================================================================
-- Metrics - project org visibility
-- ============================================================================
drop policy if exists metrics_select on ops.metrics;
create policy metrics_select on ops.metrics
for select using (
  exists (
    select 1
    from ops.projects p
    where p.id = ops.metrics.project_id
      and p.org_id in (select ops.my_org_ids())
  )
);

-- Allow service_role to insert metrics
drop policy if exists metrics_insert_service on ops.metrics;
create policy metrics_insert_service on ops.metrics
for insert with check (
  auth.jwt()->>'role' = 'service_role'
);

-- ============================================================================
-- Monitoring - project org visibility
-- ============================================================================
drop policy if exists monitoring_select on ops.monitoring;
create policy monitoring_select on ops.monitoring
for select using (
  exists (
    select 1
    from ops.projects p
    where p.id = ops.monitoring.project_id
      and p.org_id in (select ops.my_org_ids())
  )
);

drop policy if exists monitoring_update_service on ops.monitoring;
create policy monitoring_update_service on ops.monitoring
for update using (
  auth.jwt()->>'role' = 'service_role'
);

-- ============================================================================
-- Advisories - project org visibility
-- ============================================================================
drop policy if exists advisories_select on ops.advisories;
create policy advisories_select on ops.advisories
for select using (
  exists (
    select 1
    from ops.projects p
    where p.id = ops.advisories.project_id
      and p.org_id in (select ops.my_org_ids())
  )
);

drop policy if exists advisories_update on ops.advisories;
create policy advisories_update on ops.advisories
for update using (
  exists (
    select 1
    from ops.projects p
    where p.id = ops.advisories.project_id
      and p.org_id in (select ops.my_org_ids())
  )
);

-- Allow service_role to insert advisories
drop policy if exists advisories_insert_service on ops.advisories;
create policy advisories_insert_service on ops.advisories
for insert with check (
  auth.jwt()->>'role' = 'service_role'
);

-- ============================================================================
-- Upgrades - project org visibility
-- ============================================================================
drop policy if exists upgrades_select on ops.upgrades;
create policy upgrades_select on ops.upgrades
for select using (
  exists (
    select 1
    from ops.projects p
    where p.id = ops.upgrades.project_id
      and p.org_id in (select ops.my_org_ids())
  )
);

drop policy if exists upgrades_insert on ops.upgrades;
create policy upgrades_insert on ops.upgrades
for insert with check (
  exists (
    select 1
    from ops.projects p
    where p.id = ops.upgrades.project_id
      and p.org_id in (select ops.my_org_ids())
  )
);

drop policy if exists upgrades_update on ops.upgrades;
create policy upgrades_update on ops.upgrades
for update using (
  exists (
    select 1
    from ops.projects p
    where p.id = ops.upgrades.project_id
      and p.org_id in (select ops.my_org_ids())
  )
);

-- ============================================================================
-- Verification
-- ============================================================================
comment on schema ops is 'Odoo.sh-like operational platform - RLS enabled';
