-- supabase/migrations/0001_extensions.sql

-- Foundational extensions
create extension if not exists "uuid-ossp";
create extension if not exists "pgcrypto";
create extension if not exists "citext";

-- Telemetry / Insights
create extension if not exists "pg_stat_statements";

-- AI / Vectors
create extension if not exists "vector" schema extensions;

-- APIs / Async
create extension if not exists "pg_graphql" schema graphql;
create extension if not exists "pg_net" schema extensions;
