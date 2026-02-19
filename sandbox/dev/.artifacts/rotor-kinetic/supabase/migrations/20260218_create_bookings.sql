-- W9 Studio bookings table
-- Run in Supabase SQL Editor or via `supabase db push`

create extension if not exists "btree_gist";

create table if not exists public.bookings (
  id           uuid primary key default gen_random_uuid(),
  name         text not null,
  email        text not null,
  phone        text,
  message      text,
  studio_type  text not null check (studio_type in ('video','photo','event','rental')),
  booking_date date not null,
  time_slot    text not null,
  status       text not null default 'pending'
                 check (status in ('pending','confirmed','cancelled')),
  created_at   timestamptz not null default now(),

  -- Prevent double-booking: same date + time slot = conflict
  constraint no_double_booking
    exclude using gist (
      booking_date with =,
      time_slot    with =
    ) where (status != 'cancelled')
);

-- Indexes
create index if not exists bookings_date_idx   on public.bookings (booking_date);
create index if not exists bookings_email_idx  on public.bookings (email);
create index if not exists bookings_status_idx on public.bookings (status);

-- RLS
alter table public.bookings enable row level security;

-- Anon users can INSERT (submit bookings) — no SELECT on others' data
create policy "insert_booking"
  on public.bookings
  for insert
  to anon
  with check (true);

-- Authenticated admin can read/update/delete all bookings
create policy "admin_all"
  on public.bookings
  for all
  to authenticated
  using (true)
  with check (true);
