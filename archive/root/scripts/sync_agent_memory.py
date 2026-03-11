#!/usr/bin/env python3
"""
Agent Memory Sync: SQLite → Supabase

Purpose:
    Periodically sync agent memory from local SQLite (claude-mem style)
    to Supabase PostgreSQL (canonical source of truth).

Architecture:
    - SQLite: Fast local cache for Claude Code IDE sessions
    - Supabase: Canonical agent memory, skills, cross-agent coordination

Usage:
    # One-time sync
    python scripts/sync_agent_memory.py

    # Continuous sync (every 5 minutes)
    python scripts/sync_agent_memory.py --daemon --interval 300

    # Sync specific session
    python scripts/sync_agent_memory.py --session-id abc123

Environment Variables:
    SUPABASE_URL - Supabase project URL
    SUPABASE_SERVICE_ROLE_KEY - Service role key (full access)
    CLAUDE_MEM_DB_PATH - Path to local SQLite database (default: ~/.claude/project_memory.db)
"""

import argparse
import json
import logging
import os
import sqlite3
import sys
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from uuid import UUID, uuid4

try:
    from supabase import create_client, Client
except ImportError:
    print(
        "ERROR: supabase-py not installed. Run: pip install supabase", file=sys.stderr
    )
    sys.exit(1)

# ============================================================================
# Configuration
# ============================================================================

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://spdtwktxdalcfigzeqrz.supabase.co")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
CLAUDE_MEM_DB_PATH = os.getenv(
    "CLAUDE_MEM_DB_PATH", os.path.expanduser("~/.claude/project_memory.db")
)

# Default to odoo_developer agent if not specified
DEFAULT_AGENT_NAME = "odoo_developer"
DEFAULT_SOURCE = "claude-code"

# Importance thresholds for sync
MIN_IMPORTANCE_THRESHOLD = 0.3  # Only sync events with importance > 0.3

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ============================================================================
# SQLite Memory Reader
# ============================================================================


class SQLiteMemoryReader:
    """Read agent memory from local SQLite database."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = None

    def connect(self):
        """Connect to SQLite database."""
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"SQLite database not found: {self.db_path}")

        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        logger.info(f"Connected to SQLite: {self.db_path}")

    def close(self):
        """Close SQLite connection."""
        if self.conn:
            self.conn.close()
            logger.info("SQLite connection closed")

    def get_sessions(self, since: Optional[datetime] = None) -> List[Dict]:
        """Get sessions from SQLite (if sessions table exists)."""
        if not self.conn:
            self.connect()

        cursor = self.conn.cursor()

        # Check if sessions table exists
        cursor.execute(
            """
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='sessions'
        """
        )
        if not cursor.fetchone():
            logger.warning(
                "No sessions table in SQLite - will create synthetic sessions"
            )
            return []

        query = "SELECT * FROM sessions"
        params = []

        if since:
            query += " WHERE started_at > ?"
            params.append(since.isoformat())

        cursor.execute(query, params)
        sessions = [dict(row) for row in cursor.fetchall()]

        logger.info(f"Found {len(sessions)} sessions in SQLite")
        return sessions

    def get_memories(
        self, session_id: Optional[str] = None, since: Optional[datetime] = None
    ) -> List[Dict]:
        """Get memory entries from SQLite."""
        if not self.conn:
            self.connect()

        cursor = self.conn.cursor()

        # Adapt to various SQLite memory schemas (claude-mem, project_memory, etc.)
        # Try common table names
        for table_name in ["memories", "events", "messages", "interactions"]:
            cursor.execute(
                f"""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name='{table_name}'
            """
            )
            if cursor.fetchone():
                break
        else:
            logger.error(
                "No memory table found in SQLite (tried: memories, events, messages, interactions)"
            )
            return []

        query = f"SELECT * FROM {table_name}"
        params = []
        conditions = []

        if session_id:
            conditions.append("session_id = ?")
            params.append(session_id)

        if since:
            conditions.append("timestamp > ? OR created_at > ?")
            params.extend([since.isoformat(), since.isoformat()])

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        cursor.execute(query, params)
        memories = [dict(row) for row in cursor.fetchall()]

        logger.info(f"Found {len(memories)} memory entries in SQLite")
        return memories


# ============================================================================
# Supabase Memory Writer
# ============================================================================


class SupabaseMemoryWriter:
    """Write agent memory to Supabase PostgreSQL."""

    def __init__(self, url: str, service_key: str):
        self.url = url
        self.service_key = service_key
        self.client: Optional[Client] = None

    def connect(self):
        """Connect to Supabase."""
        self.client = create_client(self.url, self.service_key)
        logger.info(f"Connected to Supabase: {self.url}")

    def create_session(
        self, agent_name: str, source: str = DEFAULT_SOURCE, meta: Optional[Dict] = None
    ) -> str:
        """Create a new session in Supabase."""
        if not self.client:
            self.connect()

        session_data = {
            "agent_name": agent_name,
            "source": source,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "status": "active",
            "meta": meta or {},
        }

        result = self.client.table("agent_mem.sessions").insert(session_data).execute()

        if result.data:
            session_id = result.data[0]["id"]
            logger.info(f"Created session {session_id} for agent {agent_name}")
            return session_id
        else:
            raise Exception(f"Failed to create session: {result}")

    def upsert_session(self, session: Dict) -> str:
        """Upsert session (create or update)."""
        if not self.client:
            self.connect()

        # Check if session exists
        session_id = session.get("id") or str(uuid4())

        session_data = {
            "id": session_id,
            "agent_name": session.get("agent_name", DEFAULT_AGENT_NAME),
            "source": session.get("source", DEFAULT_SOURCE),
            "started_at": session.get(
                "started_at", datetime.now(timezone.utc).isoformat()
            ),
            "ended_at": session.get("ended_at"),
            "status": session.get("status", "active"),
            "meta": session.get("meta", {}),
        }

        result = self.client.table("agent_mem.sessions").upsert(session_data).execute()

        if result.data:
            logger.info(f"Upserted session {session_id}")
            return session_id
        else:
            raise Exception(f"Failed to upsert session: {result}")

    def insert_event(self, session_id: str, event: Dict) -> str:
        """Insert event into Supabase."""
        if not self.client:
            self.connect()

        event_data = {
            "session_id": session_id,
            "ts": event.get("timestamp")
            or event.get("created_at")
            or datetime.now(timezone.utc).isoformat(),
            "role": event.get("role", "system"),
            "event_type": event.get("event_type", "message"),
            "content": event.get("content", ""),
            "importance": event.get("importance", 0.5),
            "tags": event.get("tags", []),
            "meta": event.get("meta", {}),
        }

        # Skip events below importance threshold
        if event_data["importance"] < MIN_IMPORTANCE_THRESHOLD:
            return None

        result = self.client.table("agent_mem.events").insert(event_data).execute()

        if result.data:
            event_id = result.data[0]["id"]
            return event_id
        else:
            raise Exception(f"Failed to insert event: {result}")

    def start_sync_log(self, source: str, session_id: Optional[str] = None) -> str:
        """Start a sync operation log."""
        if not self.client:
            self.connect()

        log_data = {
            "sync_source": source,
            "session_id": session_id,
            "sync_started_at": datetime.now(timezone.utc).isoformat(),
            "status": "running",
        }

        result = (
            self.client.table("agent_mem.memory_sync_log").insert(log_data).execute()
        )

        if result.data:
            log_id = result.data[0]["id"]
            logger.info(f"Started sync log {log_id}")
            return log_id
        else:
            raise Exception(f"Failed to start sync log: {result}")

    def complete_sync_log(
        self,
        log_id: str,
        events_synced: int,
        status: str = "completed",
        error_message: Optional[str] = None,
    ):
        """Complete a sync operation log."""
        if not self.client:
            self.connect()

        log_data = {
            "events_synced": events_synced,
            "sync_ended_at": datetime.now(timezone.utc).isoformat(),
            "status": status,
            "error_message": error_message,
        }

        result = (
            self.client.table("agent_mem.memory_sync_log")
            .update(log_data)
            .eq("id", log_id)
            .execute()
        )

        if result.data:
            logger.info(
                f"Completed sync log {log_id}: {events_synced} events, status={status}"
            )
        else:
            logger.error(f"Failed to complete sync log: {result}")


# ============================================================================
# Sync Orchestrator
# ============================================================================


class MemorySyncOrchestrator:
    """Orchestrate SQLite → Supabase memory sync."""

    def __init__(self, sqlite_path: str, supabase_url: str, supabase_key: str):
        self.sqlite_reader = SQLiteMemoryReader(sqlite_path)
        self.supabase_writer = SupabaseMemoryWriter(supabase_url, supabase_key)

    def sync_once(
        self, session_id: Optional[str] = None, since: Optional[datetime] = None
    ) -> Tuple[int, int]:
        """Perform a single sync operation.

        Returns:
            Tuple of (sessions_synced, events_synced)
        """
        logger.info("Starting memory sync...")

        # Start sync log
        log_id = self.supabase_writer.start_sync_log(DEFAULT_SOURCE, session_id)

        try:
            # Connect to both databases
            self.sqlite_reader.connect()
            self.supabase_writer.connect()

            # Get sessions from SQLite
            sessions = self.sqlite_reader.get_sessions(since)

            sessions_synced = 0
            events_synced = 0

            if sessions:
                # Sync sessions
                for session in sessions:
                    try:
                        supabase_session_id = self.supabase_writer.upsert_session(
                            session
                        )
                        sessions_synced += 1

                        # Sync events for this session
                        memories = self.sqlite_reader.get_memories(
                            session_id=session.get("id")
                        )

                        for memory in memories:
                            try:
                                event_id = self.supabase_writer.insert_event(
                                    supabase_session_id, memory
                                )
                                if event_id:
                                    events_synced += 1
                            except Exception as e:
                                logger.error(f"Failed to insert event: {e}")
                                continue

                    except Exception as e:
                        logger.error(f"Failed to sync session: {e}")
                        continue
            else:
                # No sessions table - create synthetic session and sync all memories
                logger.info("Creating synthetic session for memory sync")

                supabase_session_id = self.supabase_writer.create_session(
                    agent_name=DEFAULT_AGENT_NAME,
                    source=DEFAULT_SOURCE,
                    meta={"synthetic": True, "source_db": self.sqlite_reader.db_path},
                )
                sessions_synced = 1

                # Sync all memories
                memories = self.sqlite_reader.get_memories(since=since)

                for memory in memories:
                    try:
                        event_id = self.supabase_writer.insert_event(
                            supabase_session_id, memory
                        )
                        if event_id:
                            events_synced += 1
                    except Exception as e:
                        logger.error(f"Failed to insert event: {e}")
                        continue

            # Complete sync log
            self.supabase_writer.complete_sync_log(
                log_id, events_synced, status="completed"
            )

            logger.info(
                f"Sync complete: {sessions_synced} sessions, {events_synced} events"
            )
            return sessions_synced, events_synced

        except Exception as e:
            logger.error(f"Sync failed: {e}")
            self.supabase_writer.complete_sync_log(
                log_id, 0, status="failed", error_message=str(e)
            )
            raise

        finally:
            self.sqlite_reader.close()

    def sync_daemon(self, interval_seconds: int = 300):
        """Run continuous sync daemon."""
        logger.info(f"Starting sync daemon (interval: {interval_seconds}s)")

        while True:
            try:
                # Only sync events from last sync + 10 seconds buffer
                since = datetime.now(timezone.utc)
                since = since.replace(second=since.second - interval_seconds - 10)

                sessions, events = self.sync_once(since=since)

                if sessions > 0 or events > 0:
                    logger.info(f"Synced {sessions} sessions, {events} events")
                else:
                    logger.debug("No new data to sync")

            except Exception as e:
                logger.error(f"Sync daemon error: {e}")

            time.sleep(interval_seconds)


# ============================================================================
# CLI
# ============================================================================


def main():
    parser = argparse.ArgumentParser(
        description="Sync agent memory from SQLite to Supabase"
    )
    parser.add_argument(
        "--daemon", action="store_true", help="Run as continuous sync daemon"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=300,
        help="Sync interval in seconds (default: 300)",
    )
    parser.add_argument("--session-id", help="Sync specific session only")
    parser.add_argument("--since", help="Sync events since timestamp (ISO format)")
    parser.add_argument(
        "--sqlite-db", default=CLAUDE_MEM_DB_PATH, help="Path to SQLite database"
    )

    args = parser.parse_args()

    # Validate environment
    if not SUPABASE_SERVICE_KEY:
        logger.error("SUPABASE_SERVICE_ROLE_KEY environment variable not set")
        sys.exit(1)

    # Parse since timestamp
    since = None
    if args.since:
        try:
            since = datetime.fromisoformat(args.since)
        except ValueError:
            logger.error(f"Invalid --since timestamp: {args.since}")
            sys.exit(1)

    # Create orchestrator
    orchestrator = MemorySyncOrchestrator(
        sqlite_path=args.sqlite_db,
        supabase_url=SUPABASE_URL,
        supabase_key=SUPABASE_SERVICE_KEY,
    )

    # Run sync
    if args.daemon:
        orchestrator.sync_daemon(interval_seconds=args.interval)
    else:
        sessions, events = orchestrator.sync_once(
            session_id=args.session_id, since=since
        )
        print(f"✅ Sync complete: {sessions} sessions, {events} events")


if __name__ == "__main__":
    main()
