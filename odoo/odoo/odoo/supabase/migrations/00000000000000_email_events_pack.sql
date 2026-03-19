-- Supabase Email Events Pack - schema
-- Purpose: Mirror Odoo EE-style email tracking with Supabase
-- Status: PRODUCTION-READY

create schema if not exists email_parity;

-- Table 1: Messages (one row per logical outbound message)
create table if not exists email_parity.messages (
    id              bigserial primary key,
    message_id      text not null unique,
    odoo_mail_id    integer,
    from_address    text not null,
    to_addresses    text[] not null default '{}',
    cc_addresses    text[] not null default '{}',
    bcc_addresses   text[] not null default '{}',
    subject         text,
    template_key    text,
    meta            jsonb not null default '{}'::jsonb,
    created_at      timestamptz not null default now()
);

create index if not exists idx_email_messages_message_id
    on email_parity.messages (message_id);

create index if not exists idx_email_messages_template_key
    on email_parity.messages (template_key)
    where template_key is not null;

create index if not exists idx_email_messages_created_at
    on email_parity.messages (created_at desc);

-- Table 2: Events (one row per email event)
create table if not exists email_parity.events (
    id                  bigserial primary key,
    message_id          text not null references email_parity.messages (message_id) on delete cascade,
    event_type          text not null,
    provider            text not null default 'mailgun',
    provider_event_id   text,
    event_payload       jsonb not null default '{}'::jsonb,
    recipient           text,
    endpoint            text,
    ip                  inet,
    user_agent          text,
    created_at          timestamptz not null default now(),
    occurred_at         timestamptz
);

create index if not exists idx_email_events_message_id
    on email_parity.events (message_id);

create index if not exists idx_email_events_event_type
    on email_parity.events (event_type);

create index if not exists idx_email_events_recipient
    on email_parity.events (recipient)
    where recipient is not null;

create index if not exists idx_email_events_occurred_at
    on email_parity.events (occurred_at desc);

-- Table 3: Webhook Logs (one row per webhook hit for troubleshooting)
create table if not exists email_parity.webhook_logs (
    id              bigserial primary key,
    endpoint        text not null,
    status_code     integer not null,
    request_headers jsonb not null default '{}'::jsonb,
    request_body    jsonb not null default '{}'::jsonb,
    error_message   text,
    received_at     timestamptz not null default now()
);

create index if not exists idx_webhook_logs_endpoint
    on email_parity.webhook_logs (endpoint);

create index if not exists idx_webhook_logs_status_code
    on email_parity.webhook_logs (status_code)
    where status_code >= 400;

create index if not exists idx_webhook_logs_received_at
    on email_parity.webhook_logs (received_at desc);

-- View 1: Message Summary (aggregated delivery/engagement metrics per message)
create or replace view email_parity.v_message_summary as
select
    m.message_id,
    m.subject,
    m.from_address,
    m.to_addresses,
    m.template_key,
    m.meta,
    m.created_at,
    min(e.occurred_at) filter (where e.event_type = 'delivered') as first_delivered_at,
    count(*) filter (where e.event_type = 'delivered') as delivered_count,
    count(*) filter (where e.event_type = 'opened') as opens,
    count(*) filter (where e.event_type = 'clicked') as clicks,
    count(*) filter (where e.event_type = 'bounced') as bounces,
    count(*) filter (where e.event_type = 'complained') as complaints,
    count(*) filter (where e.event_type = 'unsubscribed') as unsubscribes,
    max(e.occurred_at) as last_event_at,
    -- Engagement rate calculations
    case
        when count(*) filter (where e.event_type = 'delivered') > 0
        then round(
            100.0 * count(*) filter (where e.event_type = 'opened')
            / count(*) filter (where e.event_type = 'delivered'),
            2
        )
        else 0
    end as open_rate_pct,
    case
        when count(*) filter (where e.event_type = 'opened') > 0
        then round(
            100.0 * count(*) filter (where e.event_type = 'clicked')
            / count(*) filter (where e.event_type = 'opened'),
            2
        )
        else 0
    end as click_through_rate_pct
from email_parity.messages m
left join email_parity.events e
    on e.message_id = m.message_id
group by
    m.message_id,
    m.subject,
    m.from_address,
    m.to_addresses,
    m.template_key,
    m.meta,
    m.created_at;

-- View 2: Recipient Health (aggregated per-recipient status)
create or replace view email_parity.v_recipient_health as
select
    recipient,
    count(*) filter (where event_type = 'delivered') as delivered_count,
    count(*) filter (where event_type = 'opened') as opened_count,
    count(*) filter (where event_type = 'clicked') as clicked_count,
    count(*) filter (where event_type = 'bounced') as bounce_count,
    max(occurred_at) filter (where event_type = 'bounced') as last_bounce_at,
    count(*) filter (where event_type = 'complained') as complaint_count,
    max(occurred_at) filter (where event_type = 'complained') as last_complaint_at,
    count(*) filter (where event_type = 'unsubscribed') as unsubscribe_count,
    max(occurred_at) filter (where event_type = 'unsubscribed') as last_unsubscribe_at,
    max(occurred_at) as last_event_at,
    -- Health score (0-100, lower is worse)
    case
        when count(*) filter (where event_type = 'complained') > 0 then 0
        when count(*) filter (where event_type = 'unsubscribed') > 0 then 20
        when count(*) filter (where event_type = 'bounced') >= 3 then 40
        when count(*) filter (where event_type = 'bounced') >= 1 then 60
        when count(*) filter (where event_type = 'opened') > 0 then 100
        when count(*) filter (where event_type = 'delivered') > 0 then 80
        else 50
    end as health_score
from email_parity.events
where recipient is not null
group by recipient;

-- View 3: Template Performance (aggregated metrics by template)
create or replace view email_parity.v_template_performance as
select
    m.template_key,
    count(distinct m.message_id) as total_messages,
    count(distinct m.message_id) filter (
        where exists (
            select 1 from email_parity.events e
            where e.message_id = m.message_id
            and e.event_type = 'delivered'
        )
    ) as delivered_messages,
    count(distinct m.message_id) filter (
        where exists (
            select 1 from email_parity.events e
            where e.message_id = m.message_id
            and e.event_type = 'opened'
        )
    ) as opened_messages,
    count(distinct m.message_id) filter (
        where exists (
            select 1 from email_parity.events e
            where e.message_id = m.message_id
            and e.event_type = 'clicked'
        )
    ) as clicked_messages,
    count(distinct m.message_id) filter (
        where exists (
            select 1 from email_parity.events e
            where e.message_id = m.message_id
            and e.event_type = 'bounced'
        )
    ) as bounced_messages,
    count(distinct m.message_id) filter (
        where exists (
            select 1 from email_parity.events e
            where e.message_id = m.message_id
            and e.event_type = 'complained'
        )
    ) as complained_messages,
    -- Engagement rates
    case
        when count(distinct m.message_id) filter (
            where exists (
                select 1 from email_parity.events e
                where e.message_id = m.message_id
                and e.event_type = 'delivered'
            )
        ) > 0
        then round(
            100.0 * count(distinct m.message_id) filter (
                where exists (
                    select 1 from email_parity.events e
                    where e.message_id = m.message_id
                    and e.event_type = 'opened'
                )
            ) / count(distinct m.message_id) filter (
                where exists (
                    select 1 from email_parity.events e
                    where e.message_id = m.message_id
                    and e.event_type = 'delivered'
                )
            ),
            2
        )
        else 0
    end as open_rate_pct,
    min(m.created_at) as first_sent_at,
    max(m.created_at) as last_sent_at
from email_parity.messages m
where m.template_key is not null
group by m.template_key;

-- Grant read-only access to views (public schema)
-- Note: Adjust RLS policies as needed for your security requirements
grant usage on schema email_parity to anon, authenticated;
grant select on email_parity.v_message_summary to anon, authenticated;
grant select on email_parity.v_recipient_health to anon, authenticated;
grant select on email_parity.v_template_performance to anon, authenticated;

-- Comments for documentation
comment on schema email_parity is 'Odoo EE-style email tracking with Mailgun + Supabase';
comment on table email_parity.messages is 'One row per logical outbound message';
comment on table email_parity.events is 'One row per email event (delivered, opened, clicked, bounced, etc.)';
comment on table email_parity.webhook_logs is 'One row per webhook hit for troubleshooting';
comment on view email_parity.v_message_summary is 'Aggregated delivery/engagement metrics per message';
comment on view email_parity.v_recipient_health is 'Aggregated per-recipient health status (bounces, complaints, engagement)';
comment on view email_parity.v_template_performance is 'Aggregated metrics by email template';
