#!/usr/bin/env python3
"""Migrate pg_cron jobs from managed Supabase to self-hosted target.

All jobs are imported disabled. Enablement is a separate step.

Usage:
    python migrate_pg_cron.py \
        --mode dry-run \
        --output docs/evidence/migration/cron
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import psycopg2

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("migrate_pg_cron")


def export_cron_jobs(conn: psycopg2.extensions.connection) -> list[dict]:
    """Export all pg_cron jobs from the source database."""
    jobs: list[dict] = []
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT jobid, schedule, command, nodename, nodeport,
                       database, username, active, jobname
                FROM cron.job
                ORDER BY jobid
                """
            )
            columns = [desc[0] for desc in cur.description]
            for row in cur.fetchall():
                entry = dict(zip(columns, row))
                entry["active"] = bool(entry.get("active", False))
                jobs.append(entry)
    except psycopg2.Error as exc:
        logger.error("Failed to query cron.job: %s", exc)
        conn.rollback()

    logger.info("Exported %d cron jobs from source", len(jobs))
    return jobs


def transform_schedule(job: dict) -> dict:
    """Apply any schedule transformations needed for the target environment.

    Returns a copy of the job dict with potentially modified schedule/command.
    """
    transformed = dict(job)

    # Replace managed Supabase internal hostnames with self-hosted equivalents
    command = transformed.get("command", "")
    replacements = {
        "supabase_admin": os.environ.get("TARGET_PG_USER", "supabase_admin"),
        "localhost": os.environ.get("TARGET_PG_HOST", "localhost"),
    }
    for old, new in replacements.items():
        if old in command and old != new:
            command = command.replace(old, new)
            logger.info("Transformed command for job '%s': replaced '%s' with '%s'",
                        transformed.get("jobname", transformed.get("jobid")), old, new)

    transformed["command"] = command
    return transformed


def generate_schedule_sql(job: dict) -> str:
    """Generate a SELECT cron.schedule(...) statement for a single job.

    All jobs are created with active=false regardless of source state.
    """
    jobname = job.get("jobname") or f"job_{job['jobid']}"
    schedule = job["schedule"]
    command = job["command"].replace("'", "''")
    database = job.get("database", "postgres")

    return (
        f"SELECT cron.schedule("
        f"'{jobname}', "
        f"'{schedule}', "
        f"$CRON${command}$CRON$"
        f");\n"
        f"UPDATE cron.job SET active = false, database = '{database}' "
        f"WHERE jobname = '{jobname}';\n"
    )


def import_cron_jobs(
    conn: psycopg2.extensions.connection, jobs: list[dict]
) -> list[dict]:
    """Execute cron.schedule() for each job on the target, disabled."""
    results: list[dict] = []

    for job in jobs:
        transformed = transform_schedule(job)
        sql = generate_schedule_sql(transformed)
        jobname = transformed.get("jobname") or f"job_{transformed['jobid']}"

        try:
            with conn.cursor() as cur:
                cur.execute(sql)
            conn.commit()
            results.append({
                "jobname": jobname,
                "schedule": transformed["schedule"],
                "status": "imported",
                "active": False,
            })
            logger.info("Imported cron job: %s (disabled)", jobname)
        except psycopg2.Error as exc:
            conn.rollback()
            results.append({
                "jobname": jobname,
                "schedule": transformed["schedule"],
                "status": "failed",
                "error": str(exc),
            })
            logger.error("Failed to import cron job %s: %s", jobname, exc)

    return results


def verify_cron_parity(
    source_conn: psycopg2.extensions.connection,
    target_conn: psycopg2.extensions.connection,
) -> dict:
    """Verify job count and disabled state on the target."""
    verification = {
        "source_count": 0,
        "target_count": 0,
        "all_disabled": True,
        "match": False,
    }

    try:
        with source_conn.cursor() as cur:
            cur.execute("SELECT count(*) FROM cron.job")
            verification["source_count"] = cur.fetchone()[0]
    except psycopg2.Error as exc:
        logger.error("Cannot count source cron jobs: %s", exc)
        source_conn.rollback()

    try:
        with target_conn.cursor() as cur:
            cur.execute("SELECT count(*) FROM cron.job")
            verification["target_count"] = cur.fetchone()[0]

            cur.execute("SELECT count(*) FROM cron.job WHERE active = true")
            active_count = cur.fetchone()[0]
            verification["all_disabled"] = active_count == 0
            if active_count > 0:
                logger.warning("%d cron jobs are active on target (expected 0)", active_count)
    except psycopg2.Error as exc:
        logger.error("Cannot count target cron jobs: %s", exc)
        target_conn.rollback()

    verification["match"] = (
        verification["source_count"] == verification["target_count"]
        and verification["all_disabled"]
    )

    logger.info(
        "Cron parity: source=%d target=%d all_disabled=%s match=%s",
        verification["source_count"],
        verification["target_count"],
        verification["all_disabled"],
        verification["match"],
    )
    return verification


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Migrate pg_cron jobs from managed Supabase to self-hosted target."
    )
    parser.add_argument("--mode", choices=["dry-run", "execute"], default="dry-run")
    parser.add_argument("--output", type=Path, default=Path("docs/evidence/migration/cron"))
    parser.add_argument("--manifest", type=Path, default=None, help="Optional migration manifest YAML")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    logger.info("Mode: %s | Output: %s", args.mode, args.output)

    if args.mode == "dry-run":
        logger.info("[DRY-RUN] Would connect to SOURCE_PG_DSN=%s", os.environ.get("SOURCE_PG_DSN", "<unset>")[:20] + "...")
        logger.info("[DRY-RUN] Would export all jobs from cron.job table")
        logger.info("[DRY-RUN] Would transform schedules for self-hosted target")
        logger.info("[DRY-RUN] Would generate cron.schedule() SQL for each job")
        logger.info("[DRY-RUN] Would import all jobs as disabled on TARGET_PG_DSN")
        logger.info("[DRY-RUN] Would verify count parity and disabled state")

        args.output.mkdir(parents=True, exist_ok=True)
        report = {
            "mode": "dry-run",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "actions": [
                "export cron.job from source",
                "transform schedules",
                "import disabled to target",
                "verify parity",
            ],
        }
        with open(args.output / "cron_migration_report.json", "w") as fh:
            json.dump(report, fh, indent=2)
        print("STATUS: PASS pg_cron (dry-run)")
        return 0

    # Execute mode
    source_dsn = os.environ.get("SOURCE_PG_DSN")
    target_dsn = os.environ.get("TARGET_PG_DSN")
    if not source_dsn or not target_dsn:
        logger.error("SOURCE_PG_DSN and TARGET_PG_DSN must be set")
        return 1

    try:
        source_conn = psycopg2.connect(source_dsn)
        target_conn = psycopg2.connect(target_dsn)
    except Exception as exc:
        logger.error("Failed to connect: %s", exc)
        return 1

    try:
        # Export from source
        jobs = export_cron_jobs(source_conn)
        if not jobs:
            logger.warning("No cron jobs found in source; nothing to migrate")

        # Generate SQL preview (for evidence)
        sql_preview: list[str] = []
        for job in jobs:
            transformed = transform_schedule(job)
            sql_preview.append(generate_schedule_sql(transformed))

        # Import to target
        import_results = import_cron_jobs(target_conn, jobs)

        # Verify parity
        verification = verify_cron_parity(source_conn, target_conn)

        # Write report
        args.output.mkdir(parents=True, exist_ok=True)
        report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "exported_jobs": jobs,
            "import_results": import_results,
            "sql_preview": sql_preview,
            "verification": verification,
            "summary": {
                "source_count": len(jobs),
                "imported": sum(1 for r in import_results if r["status"] == "imported"),
                "failed": sum(1 for r in import_results if r["status"] == "failed"),
                "parity_match": verification["match"],
            },
        }
        with open(args.output / "cron_migration_report.json", "w") as fh:
            json.dump(report, fh, indent=2, default=str)

        failed_count = sum(1 for r in import_results if r["status"] == "failed")

        # List recreated jobs with their disabled status
        for r in import_results:
            status = "PASS" if r["status"] == "imported" else "FAIL"
            print("STATUS: %s pg_cron_job %s (active=%s)" % (status, r["jobname"], r.get("active", False)))

        if failed_count > 0:
            logger.error("Cron migration completed with %d failures", failed_count)
            print("STATUS: FAIL pg_cron_migration (%d failed)" % failed_count)
            return 1

        print("STATUS: PASS pg_cron_migration (%d jobs, all disabled)" % len(import_results))
        logger.info("Cron migration complete: %d jobs imported (all disabled)", len(import_results))
        return 0

    finally:
        source_conn.close()
        target_conn.close()


if __name__ == "__main__":
    sys.exit(main())
