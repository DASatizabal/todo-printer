-- Run this in Supabase SQL Editor AFTER the initial schema.sql
-- Adds columns for syncing task status back to Lisa's dashboard

ALTER TABLE remote_tasks ADD COLUMN local_status text;
ALTER TABLE remote_tasks ADD COLUMN printed_at timestamptz;
ALTER TABLE remote_tasks ADD COLUMN archived_at timestamptz;
