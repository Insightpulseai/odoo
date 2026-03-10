#!/usr/bin/env python3
"""
OPS Mirror Worker
Drains Odoo outbox and posts events to Supabase ops-ingest Edge Function.
Features: exponential backoff, DLQ, jitter, concurrency-safe.
"""
import hashlib
import hmac
import json
import os
import random
import time
from typing import Tuple

import psycopg
import requests

POLL_SECONDS = int(os.getenv("POLL_SECONDS", "5"))
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "25"))
MAX_ATTEMPTS = int(os.getenv("MAX_ATTEMPTS", "10"))
LOCK_ID = os.getenv("WORKER_ID", f"worker-{random.randint(1000, 9999)}")

ODOO_DSN = os.getenv("ODOO_DSN")
SUPABASE_INGEST_URL = os.getenv("SUPABASE_INGEST_URL")
OPS_INGEST_HMAC_SECRET = os.getenv("OPS_INGEST_HMAC_SECRET")

if not (ODOO_DSN and SUPABASE_INGEST_URL and OPS_INGEST_HMAC_SECRET):
    raise SystemExit("Missing env: ODOO_DSN, SUPABASE_INGEST_URL, OPS_INGEST_HMAC_SECRET")


def sign(body: str) -> str:
    """Generate HMAC-SHA256 signature for the body."""
    return hmac.new(
        OPS_INGEST_HMAC_SECRET.encode("utf-8"),
        body.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()


def backoff_seconds(attempts: int) -> int:
    """Calculate exponential backoff with jitter, capped at 5 minutes."""
    base = min(300, (2 ** min(attempts, 8)))
    jitter = random.randint(0, 5)
    return base + jitter


def ensure_table(conn: psycopg.Connection) -> None:
    """Create outbox table if not exists."""
    conn.execute("""
    CREATE TABLE IF NOT EXISTS ipai_outbox_event (
        id BIGSERIAL PRIMARY KEY,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        delivered_at TIMESTAMPTZ,
        attempts INT NOT NULL DEFAULT 0,
        next_attempt_at TIMESTAMPTZ,
        last_error TEXT,
        locked_at TIMESTAMPTZ,
        locked_by TEXT,
        topic TEXT NOT NULL,
        action TEXT NOT NULL,
        actor TEXT,
        payload JSONB NOT NULL
    );
    """)
    conn.execute("""
    CREATE INDEX IF NOT EXISTS idx_outbox_pending
    ON ipai_outbox_event(delivered_at, next_attempt_at, id);
    """)
    conn.commit()


def fetch_batch(conn: psycopg.Connection) -> list:
    """
    Fetch and lock a batch of undelivered events.
    Uses SKIP LOCKED for safe concurrent processing.
    """
    cur = conn.cursor()
    cur.execute("""
        WITH cte AS (
            SELECT id
            FROM ipai_outbox_event
            WHERE delivered_at IS NULL
              AND (next_attempt_at IS NULL OR next_attempt_at <= NOW())
              AND attempts < %s
            ORDER BY id ASC
            FOR UPDATE SKIP LOCKED
            LIMIT %s
        )
        UPDATE ipai_outbox_event e
        SET locked_at = NOW(), locked_by = %s
        FROM cte
        WHERE e.id = cte.id
        RETURNING e.id, e.topic, e.action, e.actor, e.payload, e.attempts;
    """, (MAX_ATTEMPTS, BATCH_SIZE, LOCK_ID))
    return cur.fetchall()


def mark_delivered(conn: psycopg.Connection, eid: int) -> None:
    """Mark event as successfully delivered."""
    conn.execute("""
        UPDATE ipai_outbox_event
        SET delivered_at = NOW(), locked_at = NULL, locked_by = NULL, last_error = NULL
        WHERE id = %s;
    """, (eid,))
    conn.commit()


def mark_failed(conn: psycopg.Connection, eid: int, attempts: int, err: str) -> None:
    """Mark event as failed with backoff."""
    wait = backoff_seconds(attempts)
    conn.execute("""
        UPDATE ipai_outbox_event
        SET attempts = attempts + 1,
            last_error = %s,
            next_attempt_at = NOW() + (%s || ' seconds')::INTERVAL,
            locked_at = NULL,
            locked_by = NULL
        WHERE id = %s;
    """, (err[:2000], str(wait), eid))
    conn.commit()


def send_event(
    eid: int,
    topic: str,
    action: str,
    actor: str,
    payload: dict
) -> Tuple[int, str]:
    """Send event to Supabase ops-ingest Edge Function."""
    body_obj = {
        "event_id": eid,
        "topic": topic,
        "action": action,
        "actor": actor or "odoo-worker",
        **(payload if isinstance(payload, dict) else {}),
        "payload": payload,
    }
    body = json.dumps(body_obj, separators=(",", ":"), sort_keys=True)
    headers = {
        "content-type": "application/json",
        "x-ops-signature": sign(body),
    }
    r = requests.post(SUPABASE_INGEST_URL, data=body, headers=headers, timeout=20)
    return r.status_code, r.text


def main() -> None:
    """Main worker loop."""
    print(f"[{LOCK_ID}] Starting ops-mirror-worker...")
    print(f"[{LOCK_ID}] Connecting to Odoo database...")

    with psycopg.connect(ODOO_DSN) as conn:
        ensure_table(conn)
        print(f"[{LOCK_ID}] Outbox table ready. Polling every {POLL_SECONDS}s...")

        while True:
            rows = fetch_batch(conn)
            if not rows:
                time.sleep(POLL_SECONDS)
                continue

            print(f"[{LOCK_ID}] Processing {len(rows)} events...")

            for (eid, topic, action, actor, payload, attempts) in rows:
                try:
                    sc, txt = send_event(eid, topic, action, actor, payload)
                    if sc == 200:
                        mark_delivered(conn, eid)
                        print(f"[{LOCK_ID}] eid={eid} delivered")
                    else:
                        mark_failed(conn, eid, attempts, f"http_{sc}:{txt[:500]}")
                        print(f"[{LOCK_ID}] ERROR eid={eid} status={sc} body={txt[:200]}")
                except Exception as e:
                    mark_failed(conn, eid, attempts, str(e))
                    print(f"[{LOCK_ID}] EXC eid={eid} err={e}")


if __name__ == "__main__":
    main()
