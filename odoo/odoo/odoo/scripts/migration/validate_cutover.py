#!/usr/bin/env python3
"""Comprehensive cutover readiness validation for self-hosted migration.

Validates parity between source (managed Supabase spdtwktxdalcfigzeqrz) and
target (self-hosted on Azure VM 4.193.100.31) across all migration dimensions:
table row counts, edge functions, consumers, n8n health, and pg_cron.

Usage:
    python validate_cutover.py \
        --mode dry-run \
        --output docs/evidence/migration/cutover
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests
import yaml

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("validate_cutover")

ROW_COUNT_TOLERANCE = 0.01  # <1% tolerance
EXPECTED_EDGE_FUNCTIONS = 39


def load_inventory(path: Path) -> dict:
    """Load an inventory JSON file."""
    if not path.exists():
        logger.warning("Inventory file not found: %s", path)
        return {}
    with open(path) as fh:
        return json.load(fh)


def validate_table_parity(source_inv: dict, target_inv: dict) -> list[dict]:
    """Compare table row counts between source and target (<1% tolerance)."""
    results: list[dict] = []
    source_tables = {
        f"{t['schema']}.{t['table']}": t.get("row_count", 0)
        for t in source_inv.get("tables", [])
    }
    target_tables = {
        f"{t['schema']}.{t['table']}": t.get("row_count", 0)
        for t in target_inv.get("tables", [])
    }

    all_tables = sorted(set(source_tables.keys()) | set(target_tables.keys()))
    for fqn in all_tables:
        src = source_tables.get(fqn, -1)
        tgt = target_tables.get(fqn, -1)

        if src < 0 or tgt < 0:
            passed = False
            reason = "missing from %s" % ("target" if tgt < 0 else "source")
        elif src == 0 and tgt == 0:
            passed = True
            reason = "both empty"
        else:
            diff_pct = abs(src - tgt) / max(src, 1)
            passed = diff_pct <= ROW_COUNT_TOLERANCE
            reason = "%.2f%% difference" % (diff_pct * 100)

        results.append({
            "table": fqn,
            "source_rows": src,
            "target_rows": tgt,
            "passed": passed,
            "reason": reason,
        })

    return results


def validate_edge_functions(target_url: str, source_inv: dict) -> list[dict]:
    """Health check edge functions (all 39 must respond 200)."""
    results: list[dict] = []

    if not target_url:
        logger.warning("TARGET_SUPABASE_URL not set; skipping edge function validation")
        return results

    function_names: list[str] = []
    for fn in source_inv.get("edge_functions", []):
        name = fn if isinstance(fn, str) else fn.get("name", "")
        if name:
            function_names.append(name)

    if not function_names:
        logger.warning("No edge function names in inventory")
        return [{"name": "unknown", "healthy": False, "reason": "no function list"}]

    for name in function_names:
        url = f"{target_url}/functions/v1/{name}"
        try:
            resp = requests.get(url, timeout=15)
            healthy = resp.status_code == 200
            results.append({
                "name": name,
                "url": url,
                "status_code": resp.status_code,
                "healthy": healthy,
            })
        except requests.RequestException as exc:
            results.append({
                "name": name,
                "url": url,
                "status_code": -1,
                "healthy": False,
                "error": str(exc),
            })

    return results


def validate_consumers(consumers_path: Path, target_url: str) -> list[dict]:
    """Run consumer smoke tests from consumers.yaml."""
    results: list[dict] = []

    if not consumers_path.exists():
        logger.warning("consumers.yaml not found at %s", consumers_path)
        return results

    with open(consumers_path) as fh:
        consumers = yaml.safe_load(fh) or {}

    for consumer in consumers.get("consumers", []):
        name = consumer.get("name", "unknown")
        endpoint = consumer.get("health_endpoint", consumer.get("endpoint", ""))
        if not endpoint:
            results.append({"name": name, "healthy": False, "reason": "no endpoint"})
            continue

        url = f"{target_url}{endpoint}" if endpoint.startswith("/") else endpoint
        try:
            resp = requests.get(url, timeout=15)
            healthy = 200 <= resp.status_code < 400
            results.append({
                "name": name, "url": url,
                "status_code": resp.status_code, "healthy": healthy,
            })
        except requests.RequestException as exc:
            results.append({
                "name": name, "url": url,
                "status_code": -1, "healthy": False, "error": str(exc),
            })

    return results


def validate_n8n_health(n8n_url: str) -> dict:
    """Check n8n instance health: GET /healthz."""
    if not n8n_url:
        return {"healthy": False, "reason": "TARGET_N8N_URL not set"}

    url = f"{n8n_url}/healthz"
    try:
        resp = requests.get(url, timeout=15)
        return {
            "url": url,
            "status_code": resp.status_code,
            "healthy": resp.status_code == 200,
            "body": resp.text[:200],
        }
    except requests.RequestException as exc:
        return {"url": url, "status_code": -1, "healthy": False, "error": str(exc)}


def validate_pg_cron_parity(source_inv: dict, target_inv: dict) -> dict:
    """Compare pg_cron job counts between source and target."""
    src_count = len(source_inv.get("cron_jobs", []))
    tgt_count = len(target_inv.get("cron_jobs", []))
    return {
        "source_count": src_count,
        "target_count": tgt_count,
        "match": src_count == tgt_count,
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Comprehensive cutover readiness validation."
    )
    parser.add_argument("--mode", choices=["dry-run", "execute"], default="dry-run")
    parser.add_argument("--output", type=Path,
                        default=Path("docs/evidence/migration/cutover"))
    parser.add_argument("--source-inventory", type=Path,
                        default=Path("docs/evidence/migration/inventory/inventory.json"),
                        help="Source Supabase inventory JSON")
    parser.add_argument("--target-inventory", type=Path,
                        default=Path("docs/evidence/migration/target/inventory.json"),
                        help="Target inventory JSON")
    parser.add_argument("--consumers", type=Path,
                        default=Path("ssot/migration/consumers.yaml"),
                        help="Path to consumers.yaml")
    parser.add_argument("--expected-functions", type=int, default=EXPECTED_EDGE_FUNCTIONS,
                        help="Expected number of edge functions (default: 39)")
    parser.add_argument("--target-url",
                        default=os.getenv("TARGET_SUPABASE_URL", ""),
                        help="Self-hosted Supabase base URL")
    parser.add_argument("--n8n-url",
                        default=os.getenv("TARGET_N8N_URL", ""),
                        help="Self-hosted n8n base URL")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    logger.info("Mode: %s | Output: %s", args.mode, args.output)

    if args.mode == "dry-run":
        logger.info("[DRY-RUN] Would compare source inventory: %s", args.source_inventory)
        logger.info("[DRY-RUN] Would compare target inventory: %s", args.target_inventory)
        logger.info("[DRY-RUN] Would health-check %d edge functions at %s",
                     args.expected_functions, args.target_url or "<unset>")
        logger.info("[DRY-RUN] Would run consumer smoke tests from %s", args.consumers)
        logger.info("[DRY-RUN] Would check n8n health at %s/healthz", args.n8n_url or "<unset>")
        logger.info("[DRY-RUN] Would compare pg_cron job counts")
        logger.info("[DRY-RUN] Would write readiness.json to %s", args.output)

        args.output.mkdir(parents=True, exist_ok=True)
        report = {
            "mode": "dry-run",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "checks_planned": [
                "table_row_count_parity",
                "edge_function_health",
                "consumer_smoke_tests",
                "n8n_health",
                "pg_cron_parity",
            ],
        }
        with open(args.output / "readiness.json", "w") as fh:
            json.dump(report, fh, indent=2)
        print("STATUS: PASS cutover_validation (dry-run)")
        print("CUTOVER_READY: NO (dry-run only)")
        return 0

    # Execute mode
    checks: dict[str, bool] = {}

    source_inv = load_inventory(args.source_inventory)
    target_inv = load_inventory(args.target_inventory)

    # 1. Table row count comparison (<1% tolerance)
    logger.info("=== Table Row Count Parity ===")
    table_results = validate_table_parity(source_inv, target_inv)
    table_pass = all(r["passed"] for r in table_results) if table_results else False
    checks["table_parity"] = table_pass
    failed_tables = [r for r in table_results if not r["passed"]]
    if failed_tables:
        for ft in failed_tables[:10]:
            logger.warning("  %s: src=%s tgt=%s (%s)",
                           ft["table"], ft["source_rows"], ft["target_rows"], ft["reason"])
    print("STATUS: %s table_parity (%d/%d tables match)" % (
        "PASS" if table_pass else "FAIL",
        sum(1 for r in table_results if r["passed"]),
        len(table_results)))

    # 2. Edge function health check (all 39 must respond 200)
    logger.info("=== Edge Function Health ===")
    ef_results = validate_edge_functions(args.target_url, source_inv)
    healthy_count = sum(1 for r in ef_results if r.get("healthy"))
    ef_pass = healthy_count == args.expected_functions
    checks["edge_functions"] = ef_pass
    print("STATUS: %s edge_functions (%d/%d healthy)" % (
        "PASS" if ef_pass else "FAIL", healthy_count, args.expected_functions))

    # 3. Consumer smoke tests
    logger.info("=== Consumer Smoke Tests ===")
    consumer_results = validate_consumers(args.consumers, args.target_url)
    consumer_pass = all(r.get("healthy") for r in consumer_results) if consumer_results else True
    checks["consumers"] = consumer_pass
    print("STATUS: %s consumers (%d/%d healthy)" % (
        "PASS" if consumer_pass else "FAIL",
        sum(1 for r in consumer_results if r.get("healthy")),
        len(consumer_results)))

    # 4. n8n instance health: GET /healthz
    logger.info("=== n8n Instance Health ===")
    n8n_result = validate_n8n_health(args.n8n_url)
    n8n_pass = n8n_result.get("healthy", False)
    checks["n8n_health"] = n8n_pass
    print("STATUS: %s n8n_health" % ("PASS" if n8n_pass else "FAIL"))

    # 5. pg_cron job count parity
    logger.info("=== pg_cron Parity ===")
    cron_result = validate_pg_cron_parity(source_inv, target_inv)
    cron_pass = cron_result.get("match", False)
    checks["pg_cron_parity"] = cron_pass
    print("STATUS: %s pg_cron_parity (source=%d, target=%d)" % (
        "PASS" if cron_pass else "FAIL",
        cron_result["source_count"], cron_result["target_count"]))

    # Generate readiness report
    all_pass = all(checks.values())
    readiness = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "cutover_ready": all_pass,
        "checks": checks,
        "blocking": [k for k, v in checks.items() if not v],
        "details": {
            "table_parity": table_results,
            "edge_functions": ef_results,
            "consumers": consumer_results,
            "n8n_health": n8n_result,
            "pg_cron_parity": cron_result,
        },
        "summary": {
            "total_checks": len(checks),
            "passed": sum(1 for v in checks.values() if v),
            "failed": sum(1 for v in checks.values() if not v),
        },
    }

    args.output.mkdir(parents=True, exist_ok=True)
    out_path = args.output / "readiness.json"
    with open(out_path, "w") as fh:
        json.dump(readiness, fh, indent=2, default=str)
    logger.info("Readiness report written to %s", out_path)

    print("CUTOVER_READY: %s" % ("YES" if all_pass else "NO"))

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
