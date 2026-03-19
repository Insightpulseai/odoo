#!/usr/bin/env python3
"""Replay canonical seeds to self-hosted target.

Reads ssot/migration/seed_canonical_map.yaml to determine which
seed sources are canonical and which are deprecated/excluded.

Usage:
    python replay_canonical_seeds.py \
        --mode dry-run \
        --output docs/evidence/migration/seeds \
        --manifest ssot/migration/seed_canonical_map.yaml
"""

import argparse
import json
import logging
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import psycopg2
import yaml

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("replay_canonical_seeds")


def load_seed_map(manifest_path: Path) -> dict:
    """Load seed_canonical_map.yaml and return parsed structure."""
    with open(manifest_path, "r") as fh:
        data = yaml.safe_load(fh) or {}
    logger.info("Loaded seed map with %d duplicate groups", len(data.get("duplicate_groups", [])))
    return data


def resolve_canonical_seeds(seed_map: dict) -> tuple[list[dict], list[dict]]:
    """Resolve which seeds are canonical and which are excluded.

    Returns (canonical_list, excluded_list) where each entry has
    name, path, group, and reason fields.
    """
    canonical: list[dict] = []
    excluded: list[dict] = []

    for group in seed_map.get("duplicate_groups", []):
        group_name = group.get("name", "unnamed")
        canonical_source = group.get("canonical")
        deprecated_sources = group.get("deprecated", [])

        if canonical_source:
            canonical.append({
                "name": canonical_source.get("name", ""),
                "path": canonical_source.get("path", ""),
                "group": group_name,
                "reason": "canonical source for group",
            })
            logger.info("Group '%s': canonical = %s", group_name, canonical_source.get("name", ""))

        for dep in deprecated_sources:
            excluded.append({
                "name": dep.get("name", ""),
                "path": dep.get("path", ""),
                "group": group_name,
                "reason": dep.get("reason", "deprecated"),
            })
            logger.info("Group '%s': excluded = %s (%s)", group_name, dep.get("name", ""), dep.get("reason", ""))

    return canonical, excluded


def get_replay_order(seed_map: dict) -> list[str]:
    """Extract ordered list of seed SQL files to replay."""
    return seed_map.get("supabase_seed_replay_order", [])


def replay_seed_file(sql_path: Path, target_dsn: str) -> dict:
    """Execute a single seed SQL file against the target database."""
    if not sql_path.exists():
        return {"file": str(sql_path), "status": "skipped", "reason": "file not found"}

    cmd = ["psql", target_dsn, "--single-transaction", "--set", "ON_ERROR_STOP=on", "-f", str(sql_path)]
    try:
        result = subprocess.run(cmd, capture_output=True, timeout=300)
        if result.returncode != 0:
            stderr = result.stderr.decode()[:500]
            logger.error("Seed replay failed for %s: %s", sql_path, stderr)
            return {"file": str(sql_path), "status": "failed", "error": stderr}
        return {"file": str(sql_path), "status": "success"}
    except subprocess.TimeoutExpired:
        return {"file": str(sql_path), "status": "failed", "error": "timeout"}
    except FileNotFoundError:
        return {"file": str(sql_path), "status": "failed", "error": "psql not found"}


def validate_seeds(
    conn: psycopg2.extensions.connection, seed_map: dict
) -> list[dict]:
    """Run post-replay validation queries defined in the seed map."""
    validations: list[dict] = []

    for group in seed_map.get("duplicate_groups", []):
        group_name = group.get("name", "unnamed")
        queries = group.get("validation_queries", [])

        for vq in queries:
            label = vq.get("label", group_name)
            query = vq.get("query", "")
            expected = vq.get("expected")

            if not query:
                continue

            try:
                with conn.cursor() as cur:
                    cur.execute(query)
                    result = cur.fetchone()
                    actual = result[0] if result else None

                passed = actual == expected if expected is not None else actual is not None
                validations.append({
                    "group": group_name,
                    "label": label,
                    "expected": expected,
                    "actual": actual,
                    "passed": passed,
                })
                level = logging.INFO if passed else logging.WARNING
                logger.log(level, "Validation '%s': expected=%s actual=%s passed=%s", label, expected, actual, passed)
            except psycopg2.Error as exc:
                validations.append({
                    "group": group_name,
                    "label": label,
                    "expected": expected,
                    "actual": None,
                    "passed": False,
                    "error": str(exc),
                })
                conn.rollback()

    return validations


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Replay canonical seeds to self-hosted target."
    )
    parser.add_argument("--mode", choices=["dry-run", "execute"], default="dry-run")
    parser.add_argument("--output", type=Path, default=Path("docs/evidence/migration/seeds"))
    parser.add_argument("--manifest", type=Path, default=Path("ssot/migration/seed_canonical_map.yaml"))
    parser.add_argument("--seed-root", type=Path, default=Path("supabase/seeds"), help="Root directory for seed SQL files")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    logger.info("Mode: %s | Output: %s | Manifest: %s", args.mode, args.output, args.manifest)

    if not args.manifest.exists():
        logger.error("Seed manifest not found: %s", args.manifest)
        return 1

    seed_map = load_seed_map(args.manifest)
    canonical, excluded = resolve_canonical_seeds(seed_map)
    replay_order = get_replay_order(seed_map)

    logger.info("Canonical seeds: %d | Excluded: %d | Replay order: %d files",
                len(canonical), len(excluded), len(replay_order))

    if args.mode == "dry-run":
        logger.info("[DRY-RUN] Canonical seeds to replay:")
        for seed in canonical:
            logger.info("[DRY-RUN]   + %s (%s)", seed["name"], seed["group"])
        logger.info("[DRY-RUN] Excluded/deprecated seeds:")
        for seed in excluded:
            logger.info("[DRY-RUN]   - %s (%s: %s)", seed["name"], seed["group"], seed["reason"])
        logger.info("[DRY-RUN] Replay order:")
        for i, sql_file in enumerate(replay_order, 1):
            exists = (args.seed_root / sql_file).exists()
            logger.info("[DRY-RUN]   %d. %s [%s]", i, sql_file, "exists" if exists else "MISSING")

        args.output.mkdir(parents=True, exist_ok=True)
        report = {
            "mode": "dry-run",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "canonical": canonical,
            "excluded": excluded,
            "replay_order": replay_order,
        }
        with open(args.output / "seed_replay_report.json", "w") as fh:
            json.dump(report, fh, indent=2)
        for seed in canonical:
            path = args.seed_root / seed.get("path", seed["name"])
            exists = path.exists() if seed.get("path") else False
            status = "PASS" if exists else "FAIL"
            print("STATUS: %s seed_file %s" % (status, seed["name"]))
        print("STATUS: PASS seed_manifest (%d canonical, %d excluded)" % (len(canonical), len(excluded)))
        return 0

    # Execute mode
    target_dsn = os.environ.get("TARGET_PG_DSN")
    if not target_dsn:
        logger.error("TARGET_PG_DSN must be set")
        return 1

    replay_results: list[dict] = []
    any_failed = False

    for sql_file in replay_order:
        sql_path = args.seed_root / sql_file

        # Check if this file is in the excluded list
        excluded_names = {e["path"] for e in excluded if e.get("path")}
        if str(sql_path) in excluded_names or sql_file in excluded_names:
            logger.info("Skipping deprecated seed: %s", sql_file)
            replay_results.append({"file": sql_file, "status": "skipped", "reason": "deprecated"})
            continue

        logger.info("Replaying seed: %s", sql_file)
        result = replay_seed_file(sql_path, target_dsn)
        replay_results.append(result)
        if result["status"] == "failed":
            any_failed = True
            logger.error("Seed failed: %s", sql_file)

    # Post-replay validation
    validations: list[dict] = []
    try:
        conn = psycopg2.connect(target_dsn)
        validations = validate_seeds(conn, seed_map)
        conn.close()
    except Exception as exc:
        logger.error("Post-replay validation connection failed: %s", exc)

    args.output.mkdir(parents=True, exist_ok=True)
    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "canonical": canonical,
        "excluded": excluded,
        "replay_results": replay_results,
        "validations": validations,
        "all_passed": not any_failed and all(v.get("passed", False) for v in validations),
    }
    with open(args.output / "seed_replay_report.json", "w") as fh:
        json.dump(report, fh, indent=2, default=str)

    # Print STATUS lines per seed group
    for result in replay_results:
        status = "PASS" if result["status"] == "success" else "FAIL"
        print("STATUS: %s seed_replay %s" % (status, result["file"]))

    for v in validations:
        status = "PASS" if v.get("passed") else "FAIL"
        print("STATUS: %s seed_validation %s" % (status, v["label"]))

    if any_failed:
        logger.error("Seed replay completed with failures")
        print("STATUS: FAIL seed_replay_overall")
        return 1

    print("STATUS: PASS seed_replay_overall (%d files, %d validations)" % (len(replay_results), len(validations)))
    logger.info("Seed replay complete: %d files replayed, %d validations", len(replay_results), len(validations))
    return 0


if __name__ == "__main__":
    sys.exit(main())
