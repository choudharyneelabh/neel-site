create table public.misc_stats (
  id smallint primary key default 1,
  days_since_last_subscriber integer not null,
  updated_at timestamptz not null default now(),
  constraint single_row check (id = 1)
);

grant select, insert, update on public.misc_stats to service_role;
