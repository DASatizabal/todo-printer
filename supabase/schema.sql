-- Remote task queue for GitHub Pages forms
-- Run this in the Supabase SQL Editor (Dashboard > SQL Editor > New Query)

create table remote_tasks (
  id         uuid primary key default gen_random_uuid(),
  title      text not null,
  category   text not null default 'personal'
             check (category in ('work', 'school', 'personal')),
  priority   int not null default 2
             check (priority in (1, 2, 3)),
  source     text not null default 'lisa'
             check (source in ('self', 'lisa', 'calendar')),
  notes      text,
  due_date   text,
  due_time   text,
  synced     boolean not null default false,
  created_at timestamptz not null default now()
);

-- Fast lookup for unsynced rows
create index idx_remote_tasks_unsynced
  on remote_tasks(synced) where synced = false;

-- RLS policies: allow anon key to insert, read, and mark synced
alter table remote_tasks enable row level security;

create policy "anon_insert" on remote_tasks
  for insert to anon
  with check (true);

create policy "anon_select" on remote_tasks
  for select to anon
  using (true);

create policy "anon_update_synced" on remote_tasks
  for update to anon
  using (true)
  with check (true);
