-- supabase/migrations/20260225000003_email_enqueue_trigger.sql
--
-- Trigger on ops.webhook_events: enqueue email notifications for finance task events.
--
-- How it wires:
--   Odoo → send_ipai_event() → webhook-ingest Edge Function
--   → INSERT into ops.webhook_events (payload = full Odoo event body)
--   → this trigger fires → INSERT into ops.email_notification_events
--
-- IMPORTANT: webhook-ingest stores the full Odoo event body in ops.webhook_events.payload.
-- The body shape is:
--   {
--     "event_type": "finance_task.created",
--     "aggregate_type": "finance_task",
--     "aggregate_id": "123",
--     "payload": {                  ← inner task payload
--       "task_id": 123,
--       "task_name": "...",
--       "project_name": "...",
--       "new_stage": "...",
--       "assignee_emails": ["a@b.com", "c@d.com"],
--       "write_date_unix": 1740000000,
--       ...
--     }
--   }
-- webhook-ingest infers event_type from payload.type (not payload.event_type),
-- so ops.webhook_events.event_type is NULL for Odoo events.
-- This trigger reads event_type from NEW.payload->>'event_type' instead.

create or replace function ops.enqueue_email_notifications()
returns trigger
language plpgsql
as $$
declare
  v_event_type    text;
  v_mapped_event  text;
  v_inner_payload jsonb;
  v_recipients    text[];
  v_email         text;
  v_ikey          text;
begin
  -- Read event_type from the JSONB body (webhook-ingest stores full event here)
  v_event_type := NEW.payload->>'event_type';

  -- Only handle finance task events
  if v_event_type not in (
    'finance_task.created',
    'finance_task.in_progress',
    'finance_task.submitted',
    'finance_task.approved',
    'finance_task.filed'
  ) then
    return NEW;
  end if;

  -- The inner task payload is nested under payload.payload
  v_inner_payload := NEW.payload->'payload';

  -- Require assignee_emails to be present (added by Odoo patch C1)
  if v_inner_payload is null
    or v_inner_payload->'assignee_emails' is null
    or jsonb_array_length(v_inner_payload->'assignee_emails') = 0
  then
    return NEW;
  end if;

  -- Map Odoo event type → email template name
  v_mapped_event := case v_event_type
    when 'finance_task.created'     then 'task_assigned'
    when 'finance_task.in_progress' then 'task_stage_changed'
    when 'finance_task.submitted'   then 'task_stage_changed'
    when 'finance_task.approved'    then 'task_stage_changed'
    when 'finance_task.filed'       then 'task_stage_changed'
    else null
  end;

  if v_mapped_event is null then
    return NEW;
  end if;

  -- Extract recipients
  select array_agg(e)
    into v_recipients
    from jsonb_array_elements_text(v_inner_payload->'assignee_emails') as e
   where e is not null and e <> '';

  if v_recipients is null or array_length(v_recipients, 1) = 0 then
    return NEW;
  end if;

  foreach v_email in array v_recipients loop
    -- Idempotency key: tied to this specific webhook event row + recipient
    -- Using NEW.id ensures no cross-event collisions even for same task
    v_ikey := concat_ws(':', 'email', v_mapped_event, NEW.id::text, v_email);

    insert into ops.email_notification_events
      (idempotency_key, source, event_type, payload, recipient_email, template)
    values
      (v_ikey, 'odoo_webhook', v_mapped_event, v_inner_payload, v_email, v_mapped_event)
    on conflict (idempotency_key) do nothing;
  end loop;

  return NEW;
end;
$$;

-- Drop existing trigger if present (idempotent migration)
drop trigger if exists enqueue_email_notifications_trigger on ops.webhook_events;

create trigger enqueue_email_notifications_trigger
  after insert on ops.webhook_events
  for each row execute function ops.enqueue_email_notifications();

comment on function ops.enqueue_email_notifications() is
  'Fires after INSERT on ops.webhook_events. '
  'Enqueues email notifications for finance task lifecycle events. '
  'Reads event_type from payload JSONB (not the event_type column, '
  'which is NULL for Odoo events due to webhook-ingest inferEventType).';
