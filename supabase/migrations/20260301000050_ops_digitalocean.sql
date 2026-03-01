-- ============================================================================
-- Migration: ops.do_* tables — DigitalOcean provider inventory
-- Contract:  docs/contracts/C-DO-01-digitalocean-api.md (C-18)
-- SSOT:      ssot/providers/digitalocean/provider.yaml
-- Author:    ops-console platform
-- Date:      2026-03-01
-- ============================================================================
--
-- Tables created:
--   ops.do_droplets      — Compute droplets (VMs)
--   ops.do_databases     — Managed database clusters
--   ops.do_firewalls     — Cloud firewall policies
--   ops.do_actions       — Action dispatch audit log (future: post-MVP writes)
--   ops.do_ingest_runs   — Ingestion run audit trail
--
-- Append-only rule (Rule 5, ssot-platform.md):
--   DROP TABLE / TRUNCATE are forbidden for ops.* tables.
--   Only ADD COLUMN IF NOT EXISTS is allowed after initial creation.
-- ============================================================================

-- ── Shared trigger function (idempotent) ──────────────────────────────────────
CREATE OR REPLACE FUNCTION ops.set_updated_at()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$;

-- ── ops.do_droplets ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS ops.do_droplets (
  id            BIGSERIAL PRIMARY KEY,
  do_id         BIGINT     NOT NULL UNIQUE,  -- DigitalOcean droplet ID
  name          TEXT       NOT NULL,
  region        TEXT       NOT NULL,         -- e.g. "sgp1"
  size_slug     TEXT,                        -- e.g. "s-2vcpu-4gb"
  ipv4_public   INET,
  ipv4_private  INET,
  status        TEXT       NOT NULL          -- new | active | off | archive
                  CHECK (status IN ('new','active','off','archive')),
  tags          TEXT[]     NOT NULL DEFAULT '{}',
  image_slug    TEXT,                        -- e.g. "ubuntu-22-04-x64"
  vcpus         INT,
  memory_mb     INT,
  disk_gb       INT,
  created_at_do TIMESTAMPTZ,                 -- DO-reported creation time
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  raw           JSONB       NOT NULL DEFAULT '{}'  -- full DO API response
);

CREATE INDEX IF NOT EXISTS do_droplets_status_idx  ON ops.do_droplets (status);
CREATE INDEX IF NOT EXISTS do_droplets_region_idx  ON ops.do_droplets (region);
CREATE INDEX IF NOT EXISTS do_droplets_updated_idx ON ops.do_droplets (updated_at DESC);

CREATE OR REPLACE TRIGGER do_droplets_updated_at
  BEFORE UPDATE ON ops.do_droplets
  FOR EACH ROW EXECUTE FUNCTION ops.set_updated_at();

-- ── ops.do_databases ───────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS ops.do_databases (
  id            BIGSERIAL PRIMARY KEY,
  do_id         TEXT       NOT NULL UNIQUE,  -- DigitalOcean cluster UUID
  name          TEXT       NOT NULL,
  engine        TEXT       NOT NULL          -- pg | mysql | redis | mongodb
                  CHECK (engine IN ('pg','mysql','redis','mongodb','kafka')),
  version       TEXT,                        -- e.g. "16"
  region        TEXT       NOT NULL,
  status        TEXT       NOT NULL          -- creating | online | resizing | migrating | forking | degraded | error | unknown
                  CHECK (status IN ('creating','online','resizing','migrating','forking','degraded','error','unknown')),
  size_slug     TEXT,                        -- e.g. "db-s-1vcpu-1gb"
  num_nodes     INT        NOT NULL DEFAULT 1,
  endpoint_host TEXT,
  endpoint_port INT,
  ssl_required  BOOLEAN    NOT NULL DEFAULT TRUE,
  tags          TEXT[]     NOT NULL DEFAULT '{}',
  created_at_do TIMESTAMPTZ,
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  raw           JSONB       NOT NULL DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS do_databases_status_idx  ON ops.do_databases (status);
CREATE INDEX IF NOT EXISTS do_databases_engine_idx  ON ops.do_databases (engine);
CREATE INDEX IF NOT EXISTS do_databases_updated_idx ON ops.do_databases (updated_at DESC);

CREATE OR REPLACE TRIGGER do_databases_updated_at
  BEFORE UPDATE ON ops.do_databases
  FOR EACH ROW EXECUTE FUNCTION ops.set_updated_at();

-- ── ops.do_firewalls ───────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS ops.do_firewalls (
  id              BIGSERIAL PRIMARY KEY,
  do_id           TEXT       NOT NULL UNIQUE,  -- DigitalOcean firewall UUID
  name            TEXT       NOT NULL,
  status          TEXT       NOT NULL          -- waiting | succeeded | failed
                    CHECK (status IN ('waiting','succeeded','failed')),
  inbound_rules   JSONB      NOT NULL DEFAULT '[]',
  outbound_rules  JSONB      NOT NULL DEFAULT '[]',
  droplet_ids     BIGINT[]   NOT NULL DEFAULT '{}',
  tags            TEXT[]     NOT NULL DEFAULT '{}',
  created_at_do   TIMESTAMPTZ,
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  raw             JSONB       NOT NULL DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS do_firewalls_status_idx  ON ops.do_firewalls (status);
CREATE INDEX IF NOT EXISTS do_firewalls_updated_idx ON ops.do_firewalls (updated_at DESC);

CREATE OR REPLACE TRIGGER do_firewalls_updated_at
  BEFORE UPDATE ON ops.do_firewalls
  FOR EACH ROW EXECUTE FUNCTION ops.set_updated_at();

-- ── ops.do_actions ─────────────────────────────────────────────────────────────
-- Audit log for DO API action dispatch (post-MVP writes).
-- Ingest reads also log here for high-water-mark tracking.
CREATE TABLE IF NOT EXISTS ops.do_actions (
  id              BIGSERIAL  PRIMARY KEY,
  do_action_id    BIGINT,                    -- DO-returned action ID (null for read-only)
  resource_type   TEXT       NOT NULL,       -- droplet | database | firewall
  resource_id     TEXT       NOT NULL,       -- do_id of the target resource
  kind            TEXT       NOT NULL,       -- ingest_read | restart | resize | firewall_patch
  status          TEXT       NOT NULL        -- pending | in-progress | completed | errored
                    CHECK (status IN ('pending','in-progress','completed','errored')),
  requested_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  completed_at    TIMESTAMPTZ,
  last_error      TEXT,
  metadata        JSONB       NOT NULL DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS do_actions_resource_idx    ON ops.do_actions (resource_type, resource_id);
CREATE INDEX IF NOT EXISTS do_actions_status_idx      ON ops.do_actions (status);
CREATE INDEX IF NOT EXISTS do_actions_requested_idx   ON ops.do_actions (requested_at DESC);

-- ── ops.do_ingest_runs ─────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS ops.do_ingest_runs (
  id           BIGSERIAL  PRIMARY KEY,
  run_id       UUID       NOT NULL DEFAULT gen_random_uuid() UNIQUE,
  started_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  finished_at  TIMESTAMPTZ,
  status       TEXT       NOT NULL DEFAULT 'running'
                 CHECK (status IN ('running','success','partial','error')),
  counts       JSONB       NOT NULL DEFAULT '{}',
  -- e.g. {"droplets": 3, "databases": 2, "firewalls": 5, "errors": 0}
  last_error   TEXT,
  triggered_by TEXT        NOT NULL DEFAULT 'cron'
                 CHECK (triggered_by IN ('cron','manual','webhook'))
);

CREATE INDEX IF NOT EXISTS do_ingest_runs_status_idx  ON ops.do_ingest_runs (status);
CREATE INDEX IF NOT EXISTS do_ingest_runs_started_idx ON ops.do_ingest_runs (started_at DESC);

-- ── RLS policies ──────────────────────────────────────────────────────────────
ALTER TABLE ops.do_droplets      ENABLE ROW LEVEL SECURITY;
ALTER TABLE ops.do_databases     ENABLE ROW LEVEL SECURITY;
ALTER TABLE ops.do_firewalls     ENABLE ROW LEVEL SECURITY;
ALTER TABLE ops.do_actions       ENABLE ROW LEVEL SECURITY;
ALTER TABLE ops.do_ingest_runs   ENABLE ROW LEVEL SECURITY;

-- Authenticated users can read inventory (ops-console pages)
CREATE POLICY "authenticated can read do_droplets"
  ON ops.do_droplets FOR SELECT TO authenticated USING (true);

CREATE POLICY "authenticated can read do_databases"
  ON ops.do_databases FOR SELECT TO authenticated USING (true);

CREATE POLICY "authenticated can read do_firewalls"
  ON ops.do_firewalls FOR SELECT TO authenticated USING (true);

CREATE POLICY "authenticated can read do_actions"
  ON ops.do_actions FOR SELECT TO authenticated USING (true);

CREATE POLICY "authenticated can read do_ingest_runs"
  ON ops.do_ingest_runs FOR SELECT TO authenticated USING (true);

-- Service role (Edge Function ops-do-ingest) has full write access
CREATE POLICY "service_role full access do_droplets"
  ON ops.do_droplets FOR ALL TO service_role USING (true);

CREATE POLICY "service_role full access do_databases"
  ON ops.do_databases FOR ALL TO service_role USING (true);

CREATE POLICY "service_role full access do_firewalls"
  ON ops.do_firewalls FOR ALL TO service_role USING (true);

CREATE POLICY "service_role full access do_actions"
  ON ops.do_actions FOR ALL TO service_role USING (true);

CREATE POLICY "service_role full access do_ingest_runs"
  ON ops.do_ingest_runs FOR ALL TO service_role USING (true);

-- ── Seed: known production inventory (from CLAUDE.md infrastructure section) ──
-- These are the known live resources as of 2026-03-01.
-- The ingest worker will overwrite/update these on first run.
INSERT INTO ops.do_droplets (do_id, name, region, size_slug, ipv4_public, status, tags, image_slug)
VALUES
  (0, 'odoo-production', 'sgp1', 's-4vcpu-8gb', '178.128.112.214'::INET, 'active',
   ARRAY['production','erp','n8n','ocr','auth'], 'ubuntu-22-04-x64')
ON CONFLICT (do_id) DO UPDATE SET
  name       = EXCLUDED.name,
  region     = EXCLUDED.region,
  ipv4_public = EXCLUDED.ipv4_public,
  status     = EXCLUDED.status,
  tags       = EXCLUDED.tags,
  updated_at = now();

-- Note: do_id=0 is a placeholder. The ingest worker will replace it with the real DO ID.
-- This seed ensures the Overview page shows a node count before first ingest completes.

-- ── Comments for documentation ────────────────────────────────────────────────
COMMENT ON TABLE ops.do_droplets    IS 'DigitalOcean Droplet inventory — upserted hourly by ops-do-ingest';
COMMENT ON TABLE ops.do_databases   IS 'DigitalOcean Managed Database clusters — upserted hourly by ops-do-ingest';
COMMENT ON TABLE ops.do_firewalls   IS 'DigitalOcean Cloud Firewalls — upserted hourly by ops-do-ingest';
COMMENT ON TABLE ops.do_actions     IS 'Audit log for all DO API interactions (reads + writes)';
COMMENT ON TABLE ops.do_ingest_runs IS 'Run-level audit trail for ops-do-ingest worker';
