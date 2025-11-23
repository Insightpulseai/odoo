-- schema: monitoring
CREATE SCHEMA IF NOT EXISTS monitoring;

CREATE TABLE IF NOT EXISTS monitoring.service_health_checks (
    id              bigserial PRIMARY KEY,
    service_name    text        NOT NULL,
    checked_at      timestamptz NOT NULL DEFAULT now(),
    is_up           boolean     NOT NULL,
    http_code       integer     NOT NULL,
    latency_ms      integer     NOT NULL,
    source          text        NOT NULL DEFAULT 'cron',
    raw_payload     jsonb       NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_service_health_checks_service_time
    ON monitoring.service_health_checks (service_name, checked_at DESC);

CREATE TABLE IF NOT EXISTS monitoring.backup_verifications (
    id              bigserial PRIMARY KEY,
    source_db       text        NOT NULL,
    verify_db       text        NOT NULL,
    verified_at     timestamptz NOT NULL DEFAULT now(),
    success         boolean     NOT NULL,
    backup_file     text        NOT NULL,
    message         text        NOT NULL,
    raw_payload     jsonb       NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_backup_verifications_time
    ON monitoring.backup_verifications (verified_at DESC);
