-- supabase/migrations/20260223000004_odoo_sync_queue.sql

-- Define the queue table for background jobs/Odoo events
create table public.sync_queue (
  id uuid default uuid_generate_v4() primary key,
  idempotency_key text unique not null,
  event_type text not null,       -- e.g., 'odoo.partner.created', 'crm.lead.updated'
  payload jsonb not null,
  status text check (status in ('pending', 'processing', 'completed', 'failed')) default 'pending' not null,
  error_message text,
  retry_count integer default 0 not null,
  created_at timestamptz default now() not null,
  updated_at timestamptz default now() not null,
  processed_at timestamptz
);

-- Index for worker polling
create index idx_sync_queue_pending on public.sync_queue(status, created_at) where status = 'pending';

-- RLS
alter table public.sync_queue enable row level security;

-- Policies
create policy "Agents and admins can manage the sync queue"
  on public.sync_queue for all
  using (public.has_role('admin') or public.has_role('agent'))
  with check (public.has_role('admin') or public.has_role('agent'));

-- Trigger
create trigger queue_updated_at
  before update on public.sync_queue
  for each row execute function public.handle_updated_at();
