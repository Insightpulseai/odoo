-- Migration: Agent Memory & Skills System
-- Purpose: Canonical agent memory, skills registry, and cross-agent coordination
-- Database: Supabase PostgreSQL (spdtwktxdalcfigzeqrz)
-- Created: 2026-01-19
-- Author: DevOps/Odoo Deployment Agent

-- ============================================================================
-- SCHEMA: agent_mem
-- ============================================================================

create schema if not exists agent_mem;

-- ============================================================================
-- TABLE: sessions
-- Purpose: High-level conversation/job tracking across all agents
-- ============================================================================

create table if not exists agent_mem.sessions (
    id              uuid primary key default gen_random_uuid(),
    agent_name      text not null,               -- 'Pulser', 'WrenAI', 'Arkie', 'odoo_developer'
    user_id         text null,                   -- external user id / anon id
    source          text not null,               -- 'claude-code', 'web', 'odoo', 'n8n', 'mattermost'
    started_at      timestamptz not null default now(),
    ended_at        timestamptz null,
    status          text not null default 'active', -- 'active', 'completed', 'failed', 'abandoned'
    meta            jsonb default '{}'::jsonb,   -- arbitrary metadata (project context, etc.)

    -- Indexes
    constraint sessions_status_check check (status in ('active', 'completed', 'failed', 'abandoned'))
);

create index if not exists idx_agent_mem_sessions_agent_status
    on agent_mem.sessions (agent_name, status);

create index if not exists idx_agent_mem_sessions_source
    on agent_mem.sessions (source);

create index if not exists idx_agent_mem_sessions_started_at
    on agent_mem.sessions (started_at desc);

-- ============================================================================
-- TABLE: events
-- Purpose: Fine-grained memory items (messages, tool calls, observations)
-- ============================================================================

create table if not exists agent_mem.events (
    id              uuid primary key default gen_random_uuid(),
    session_id      uuid not null references agent_mem.sessions(id) on delete cascade,
    ts              timestamptz not null default now(),
    role            text not null,              -- 'user', 'assistant', 'tool', 'system', 'observation'
    event_type      text not null,              -- 'message', 'tool_call', 'tool_result', 'summary', 'decision'
    content         text not null,              -- raw text content
    embedding       vector(1536),               -- pgvector embedding (OpenAI text-embedding-3-small compatible)
    importance      real default 0.5,           -- 0–1, relevance/importance score for retrieval
    tags            text[] default '{}',        -- ['mailgun', 'odoo', 'deployment', 'error', etc.]
    meta            jsonb default '{}'::jsonb,  -- structured metadata (file paths, commit SHAs, etc.)

    -- Constraints
    constraint events_role_check check (role in ('user', 'assistant', 'tool', 'system', 'observation')),
    constraint events_importance_check check (importance between 0 and 1)
);

create index if not exists idx_agent_mem_events_session_ts
    on agent_mem.events (session_id, ts desc);

create index if not exists idx_agent_mem_events_role_type
    on agent_mem.events (role, event_type);

create index if not exists idx_agent_mem_events_tags
    on agent_mem.events using gin (tags);

create index if not exists idx_agent_mem_events_importance
    on agent_mem.events (importance desc) where importance > 0.7;

-- Note: embedding index requires pgvector extension
-- Run separately: create extension if not exists vector;
-- create index if not exists idx_agent_mem_events_embedding
--     on agent_mem.events using ivfflat (embedding vector_cosine_ops)
--     with (lists = 100);

-- ============================================================================
-- TABLE: skills
-- Purpose: Skills registry (tools, capabilities, integrations)
-- ============================================================================

create table if not exists agent_mem.skills (
    id              uuid primary key default gen_random_uuid(),
    skill_name      text not null unique,       -- 'mailgun_send', 'odoo_mailgate', 'scout_query', 'bir_compliance'
    description     text not null,              -- human-readable description
    category        text not null default 'general', -- 'integration', 'analysis', 'deployment', 'compliance'
    version         text not null default '1.0.0',
    spec            jsonb not null,             -- JSON spec / tool definition (MCP format compatible)
    dependencies    text[] default '{}',        -- ['odoo', 'mailgun', 'supabase', etc.]
    is_active       boolean not null default true,
    created_at      timestamptz not null default now(),
    updated_at      timestamptz not null default now()
);

create index if not exists idx_agent_mem_skills_category
    on agent_mem.skills (category) where is_active = true;

create index if not exists idx_agent_mem_skills_name
    on agent_mem.skills (skill_name) where is_active = true;

-- ============================================================================
-- TABLE: agent_skill_bindings
-- Purpose: Which agents have access to which skills (permissions + config)
-- ============================================================================

create table if not exists agent_mem.agent_skill_bindings (
    id              uuid primary key default gen_random_uuid(),
    agent_name      text not null,              -- 'Pulser', 'Doer', 'WrenAI', 'Arkie', 'odoo_developer'
    skill_id        uuid not null references agent_mem.skills(id) on delete cascade,
    enabled         boolean not null default true,
    priority        int not null default 100,   -- lower = higher priority (execution order)
    config          jsonb default '{}'::jsonb,  -- agent-specific skill config overrides
    created_at      timestamptz not null default now(),
    updated_at      timestamptz not null default now(),

    unique (agent_name, skill_id)
);

create index if not exists idx_agent_mem_bindings_agent
    on agent_mem.agent_skill_bindings (agent_name) where enabled = true;

create index if not exists idx_agent_mem_bindings_skill
    on agent_mem.agent_skill_bindings (skill_id) where enabled = true;

create index if not exists idx_agent_mem_bindings_priority
    on agent_mem.agent_skill_bindings (agent_name, priority);

-- ============================================================================
-- TABLE: memory_sync_log
-- Purpose: Track SQLite → Supabase sync operations
-- ============================================================================

create table if not exists agent_mem.memory_sync_log (
    id              uuid primary key default gen_random_uuid(),
    sync_source     text not null,              -- 'claude-code', 'local-sqlite', 'odoo-worker'
    session_id      uuid references agent_mem.sessions(id) on delete cascade,
    events_synced   int not null default 0,
    sync_started_at timestamptz not null default now(),
    sync_ended_at   timestamptz null,
    status          text not null default 'running', -- 'running', 'completed', 'failed'
    error_message   text null,
    meta            jsonb default '{}'::jsonb,

    constraint sync_status_check check (status in ('running', 'completed', 'failed'))
);

create index if not exists idx_agent_mem_sync_log_source_status
    on agent_mem.memory_sync_log (sync_source, status);

-- ============================================================================
-- VIEWS: Analytics & Observability
-- ============================================================================

-- Agent performance summary
create or replace view agent_mem.agent_performance_summary as
select
    s.agent_name,
    count(distinct s.id) as total_sessions,
    count(distinct s.id) filter (where s.status = 'completed') as completed_sessions,
    count(distinct s.id) filter (where s.status = 'failed') as failed_sessions,
    count(e.id) as total_events,
    avg(e.importance) filter (where e.importance > 0) as avg_importance,
    max(s.started_at) as last_active,
    extract(epoch from avg(s.ended_at - s.started_at)) / 60 as avg_session_duration_minutes
from agent_mem.sessions s
left join agent_mem.events e on e.session_id = s.id
group by s.agent_name;

-- Skill usage analytics
create or replace view agent_mem.skill_usage_summary as
select
    sk.skill_name,
    sk.category,
    sk.version,
    count(distinct b.agent_name) as bound_agents,
    count(*) filter (where b.enabled = true) as active_bindings,
    jsonb_agg(
        jsonb_build_object(
            'agent', b.agent_name,
            'enabled', b.enabled,
            'priority', b.priority
        ) order by b.priority
    ) as bindings
from agent_mem.skills sk
left join agent_mem.agent_skill_bindings b on b.skill_id = sk.id
group by sk.id, sk.skill_name, sk.category, sk.version;

-- Recent high-importance events
create or replace view agent_mem.important_events_recent as
select
    e.id,
    e.ts,
    s.agent_name,
    e.role,
    e.event_type,
    e.importance,
    e.tags,
    left(e.content, 200) as content_preview
from agent_mem.events e
join agent_mem.sessions s on s.id = e.session_id
where e.importance > 0.7
  and e.ts > now() - interval '7 days'
order by e.ts desc
limit 100;

-- ============================================================================
-- RLS POLICIES (Optional - enable if multi-tenant)
-- ============================================================================

-- Enable RLS on all tables (commented out by default)
-- alter table agent_mem.sessions enable row level security;
-- alter table agent_mem.events enable row level security;
-- alter table agent_mem.skills enable row level security;
-- alter table agent_mem.agent_skill_bindings enable row level security;

-- Example policy: allow service role full access
-- create policy "Service role full access" on agent_mem.sessions
--     for all to service_role using (true);

-- ============================================================================
-- SEED DATA: Initial Skills Registry
-- ============================================================================

insert into agent_mem.skills (skill_name, description, category, version, spec, dependencies)
values
    (
        'odoo_mailgate',
        'Process inbound emails from Mailgun webhooks into Odoo mail.message records',
        'integration',
        '1.0.0',
        '{
            "endpoint": "/mailgate/mailgun",
            "method": "POST",
            "auth": "public",
            "params": ["sender", "recipient", "subject", "body-plain"]
        }'::jsonb,
        array['odoo', 'mailgun']
    ),
    (
        'mailgun_send',
        'Send outbound emails via Mailgun API',
        'integration',
        '1.0.0',
        '{
            "api": "https://api.mailgun.net/v3",
            "domain": "mg.insightpulseai.net",
            "params": ["to", "subject", "text", "html"]
        }'::jsonb,
        array['mailgun']
    ),
    (
        'scout_query',
        'Query Scout transaction data from Supabase',
        'analysis',
        '1.0.0',
        '{
            "schema": "scout",
            "tables": ["transactions", "agencies", "brands"],
            "methods": ["query", "aggregate", "report"]
        }'::jsonb,
        array['supabase', 'postgresql']
    ),
    (
        'bir_compliance',
        'BIR tax compliance calculations and form generation',
        'compliance',
        '1.0.0',
        '{
            "forms": ["1601-C", "2550Q", "1702-RT"],
            "validations": ["whc_computation", "quarterly_filing", "annual_filing"],
            "outputs": ["pdf", "json", "csv"]
        }'::jsonb,
        array['odoo', 'philippine_tax']
    ),
    (
        'docker_operations',
        'Docker container management and health checks',
        'deployment',
        '1.0.0',
        '{
            "operations": ["inspect", "logs", "restart", "exec"],
            "targets": ["containers", "networks", "volumes"]
        }'::jsonb,
        array['docker']
    ),
    (
        'nginx_config',
        'Nginx configuration validation and reload',
        'deployment',
        '1.0.0',
        '{
            "operations": ["validate", "reload", "test", "inspect"],
            "config_paths": ["/etc/nginx/nginx.conf", "/etc/nginx/conf.d/"]
        }'::jsonb,
        array['nginx']
    ),
    (
        'odoo_module_operations',
        'Odoo module installation, upgrade, and validation',
        'deployment',
        '1.0.0',
        '{
            "operations": ["install", "upgrade", "uninstall", "validate"],
            "cli": "odoo -d {db} -i {module} --stop-after-init"
        }'::jsonb,
        array['odoo', 'postgresql']
    ),
    (
        'git_operations',
        'Git repository management and deployment',
        'deployment',
        '1.0.0',
        '{
            "operations": ["pull", "status", "commit", "tag", "rollback"],
            "paths": ["/opt/odoo-ce/repo"]
        }'::jsonb,
        array['git']
    )
on conflict (skill_name) do nothing;

-- ============================================================================
-- SEED DATA: Initial Agent Skill Bindings
-- ============================================================================

-- Bind skills to odoo_developer agent
insert into agent_mem.agent_skill_bindings (agent_name, skill_id, enabled, priority)
select
    'odoo_developer',
    id,
    true,
    case skill_name
        when 'odoo_mailgate' then 10
        when 'odoo_module_operations' then 20
        when 'docker_operations' then 30
        when 'nginx_config' then 40
        when 'git_operations' then 50
        when 'bir_compliance' then 60
        else 100
    end as priority
from agent_mem.skills
where skill_name in ('odoo_mailgate', 'odoo_module_operations', 'docker_operations', 'nginx_config', 'git_operations', 'bir_compliance')
on conflict (agent_name, skill_id) do nothing;

-- Bind skills to finance_ssc_expert agent
insert into agent_mem.agent_skill_bindings (agent_name, skill_id, enabled, priority)
select
    'finance_ssc_expert',
    id,
    true,
    case skill_name
        when 'bir_compliance' then 10
        when 'scout_query' then 20
        when 'odoo_module_operations' then 30
        else 100
    end as priority
from agent_mem.skills
where skill_name in ('bir_compliance', 'scout_query', 'odoo_module_operations')
on conflict (agent_name, skill_id) do nothing;

-- Bind skills to devops_engineer agent
insert into agent_mem.agent_skill_bindings (agent_name, skill_id, enabled, priority)
select
    'devops_engineer',
    id,
    true,
    case skill_name
        when 'docker_operations' then 10
        when 'nginx_config' then 20
        when 'git_operations' then 30
        when 'odoo_module_operations' then 40
        else 100
    end as priority
from agent_mem.skills
where skill_name in ('docker_operations', 'nginx_config', 'git_operations', 'odoo_module_operations')
on conflict (agent_name, skill_id) do nothing;

-- ============================================================================
-- GRANTS (Adjust based on your Supabase auth setup)
-- ============================================================================

-- Grant usage on schema to authenticated role
grant usage on schema agent_mem to authenticated;
grant usage on schema agent_mem to anon;
grant usage on schema agent_mem to service_role;

-- Grant table permissions
grant all on all tables in schema agent_mem to service_role;
grant select on all tables in schema agent_mem to authenticated;

-- Grant sequence permissions
grant usage, select on all sequences in schema agent_mem to service_role;

-- ============================================================================
-- COMMENTS (Documentation)
-- ============================================================================

comment on schema agent_mem is 'Agent memory, skills registry, and cross-agent coordination system';
comment on table agent_mem.sessions is 'High-level conversation/job tracking across all agents';
comment on table agent_mem.events is 'Fine-grained memory items (messages, tool calls, observations)';
comment on table agent_mem.skills is 'Skills registry (tools, capabilities, integrations)';
comment on table agent_mem.agent_skill_bindings is 'Agent-skill bindings with permissions and configuration';
comment on table agent_mem.memory_sync_log is 'SQLite → Supabase sync operation tracking';

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================

-- Verify installation
select 'Agent Memory Schema Created' as status,
       count(*) filter (where table_schema = 'agent_mem') as tables_created
from information_schema.tables
where table_schema = 'agent_mem';
