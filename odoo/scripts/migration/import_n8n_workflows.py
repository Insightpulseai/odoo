#!/usr/bin/env python3
"""Import n8n workflows to self-hosted instance.

All workflows are imported disabled. Enablement follows wave schedule
defined in ssot/migration/workflow_migration_map.yaml.

Usage:
    python import_n8n_workflows.py \
        --mode dry-run \
        --output docs/evidence/migration/workflows \
        --manifest ssot/migration/workflow_migration_map.yaml
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
logger = logging.getLogger("import_n8n_workflows")


def load_workflow_map(manifest_path: Path) -> dict:
    """Load workflow migration map from YAML."""
    with open(manifest_path, "r") as fh:
        data = yaml.safe_load(fh) or {}
    workflows = data.get("workflows", [])
    logger.info("Loaded workflow map with %d workflows", len(workflows))
    return data


def load_workflow_json(workflow_path: Path) -> dict | None:
    """Read a single n8n workflow JSON file."""
    if not workflow_path.exists():
        logger.warning("Workflow file not found: %s", workflow_path)
        return None
    with open(workflow_path, "r") as fh:
        return json.load(fh)


def apply_url_rewrites(
    workflow: dict, rewrites: list[dict]
) -> dict:
    """Apply URL rewrites to transform cloud URLs to self-hosted.

    Walks all string values in the workflow JSON and replaces
    source patterns with target patterns.
    """
    raw = json.dumps(workflow)
    for rewrite in rewrites:
        source = rewrite.get("from", "")
        target = rewrite.get("to", "")
        if source and target and source in raw:
            count = raw.count(source)
            raw = raw.replace(source, target)
            logger.info("URL rewrite: '%s' -> '%s' (%d occurrences)", source, target, count)
    return json.loads(raw)


def import_workflow_to_n8n(
    n8n_url: str,
    api_key: str,
    workflow: dict,
) -> dict:
    """POST workflow to n8n API with active=false."""
    # Force workflow to disabled state
    workflow["active"] = False

    # Remove id to allow n8n to assign a new one
    workflow.pop("id", None)

    headers = {
        "Content-Type": "application/json",
        "X-N8N-API-KEY": api_key,
    }

    try:
        resp = requests.post(
            f"{n8n_url}/api/v1/workflows",
            headers=headers,
            json=workflow,
            timeout=30,
        )
        if resp.status_code in (200, 201):
            result = resp.json()
            return {
                "status": "imported",
                "id": result.get("id"),
                "name": result.get("name", workflow.get("name", "unknown")),
                "active": result.get("active", False),
            }
        else:
            return {
                "status": "failed",
                "name": workflow.get("name", "unknown"),
                "http_status": resp.status_code,
                "error": resp.text[:300],
            }
    except requests.RequestException as exc:
        return {
            "status": "failed",
            "name": workflow.get("name", "unknown"),
            "error": str(exc),
        }


def identify_credential_updates(workflow: dict) -> list[dict]:
    """Identify credentials referenced in the workflow that need manual update.

    Returns a list of credential references with type and name.
    """
    credentials_needed: list[dict] = []
    nodes = workflow.get("nodes", [])

    for node in nodes:
        creds = node.get("credentials", {})
        for cred_type, cred_ref in creds.items():
            cred_name = cred_ref.get("name", "unknown") if isinstance(cred_ref, dict) else str(cred_ref)
            credentials_needed.append({
                "node": node.get("name", "unknown"),
                "credential_type": cred_type,
                "credential_name": cred_name,
                "action": "manual_update_required",
            })

    return credentials_needed


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Import n8n workflows to self-hosted instance."
    )
    parser.add_argument("--mode", choices=["dry-run", "execute"], default="dry-run")
    parser.add_argument("--output", type=Path, default=Path("docs/evidence/migration/workflows"))
    parser.add_argument("--manifest", type=Path, default=Path("ssot/migration/workflow_migration_map.yaml"))
    parser.add_argument("--workflows-dir", type=Path, default=None,
                        help="Root directory containing workflow JSON files (auto-detected if omitted)")
    parser.add_argument("--n8n-url", default=os.environ.get("TARGET_N8N_URL", ""),
                        help="Target n8n instance base URL")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    logger.info("Mode: %s | Output: %s | Manifest: %s", args.mode, args.output, args.manifest)

    if not args.manifest.exists():
        logger.error("Workflow manifest not found: %s", args.manifest)
        return 1

    # Auto-detect workflows directory
    if args.workflows_dir is None:
        for candidate in [
            Path("automations/n8n/workflows"),
            Path("n8n/workflows"),
            Path("n8n"),
        ]:
            if candidate.is_dir():
                args.workflows_dir = candidate
                break
        if args.workflows_dir is None:
            args.workflows_dir = Path("n8n/workflows")
    logger.info("Workflows directory: %s", args.workflows_dir)

    wf_map = load_workflow_map(args.manifest)
    workflows = wf_map.get("workflows", [])
    url_rewrites = wf_map.get("url_rewrites", [])
    waves = wf_map.get("waves", [])

    # Default URL rewrite: managed Supabase to self-hosted
    default_rewrites = [
        {"from": "spdtwktxdalcfigzeqrz.supabase.co", "to": "supabase.insightpulseai.com"},
    ]
    if not url_rewrites:
        url_rewrites = default_rewrites
    else:
        # Ensure default rewrite is included
        existing_froms = {r.get("from") for r in url_rewrites}
        for dr in default_rewrites:
            if dr["from"] not in existing_froms:
                url_rewrites.append(dr)

    if args.mode == "dry-run":
        logger.info("[DRY-RUN] %d workflows to import", len(workflows))
        all_credentials: list[dict] = []

        for wf_entry in workflows:
            name = wf_entry.get("name", "unknown")
            json_path = args.workflows_dir / wf_entry.get("file", f"{name}.json")
            wave = wf_entry.get("wave", "unassigned")
            exists = json_path.exists()

            logger.info("[DRY-RUN]   %s (wave: %s, file: %s) [%s]",
                        name, wave, json_path, "exists" if exists else "MISSING")

            if exists:
                wf_data = load_workflow_json(json_path)
                if wf_data:
                    creds = identify_credential_updates(wf_data)
                    all_credentials.extend(creds)

        if url_rewrites:
            logger.info("[DRY-RUN] URL rewrites to apply:")
            for rw in url_rewrites:
                logger.info("[DRY-RUN]   '%s' -> '%s'", rw.get("from", ""), rw.get("to", ""))

        if all_credentials:
            logger.info("[DRY-RUN] Credentials requiring manual update:")
            seen = set()
            for cred in all_credentials:
                key = f"{cred['credential_type']}:{cred['credential_name']}"
                if key not in seen:
                    seen.add(key)
                    logger.info("[DRY-RUN]   %s (%s)", cred["credential_name"], cred["credential_type"])

        if waves:
            logger.info("[DRY-RUN] Wave schedule:")
            for wave in waves:
                logger.info("[DRY-RUN]   Wave %s: %s", wave.get("id", "?"), wave.get("description", ""))

        args.output.mkdir(parents=True, exist_ok=True)
        report = {
            "mode": "dry-run",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "workflow_count": len(workflows),
            "url_rewrites": url_rewrites,
            "credentials_to_update": all_credentials,
            "waves": waves,
        }
        with open(args.output / "workflow_import_report.json", "w") as fh:
            json.dump(report, fh, indent=2)
        return 0

    # Execute mode
    n8n_url = args.n8n_url
    api_key = os.environ.get("N8N_API_KEY", "")
    if not n8n_url:
        logger.error("TARGET_N8N_URL must be set (--n8n-url or env var)")
        return 1
    if not api_key:
        logger.error("N8N_API_KEY environment variable must be set")
        return 1

    import_results: list[dict] = []
    all_credentials: list[dict] = []
    any_failed = False

    for wf_entry in workflows:
        name = wf_entry.get("name", "unknown")
        json_path = args.workflows_dir / wf_entry.get("file", f"{name}.json")

        wf_data = load_workflow_json(json_path)
        if wf_data is None:
            import_results.append({"name": name, "status": "failed", "error": "file not found"})
            any_failed = True
            continue

        # Collect credential references
        creds = identify_credential_updates(wf_data)
        all_credentials.extend(creds)

        # Apply URL rewrites
        if url_rewrites:
            wf_data = apply_url_rewrites(wf_data, url_rewrites)

        # Import to n8n
        logger.info("Importing workflow: %s", name)
        result = import_workflow_to_n8n(n8n_url, api_key, wf_data)
        result["wave"] = wf_entry.get("wave", "unassigned")
        import_results.append(result)

        if result["status"] == "failed":
            any_failed = True
            logger.error("Failed to import workflow %s: %s", name, result.get("error", ""))
        else:
            logger.info("Imported workflow %s (id=%s, active=%s)", name, result.get("id"), result.get("active"))

    # Write report
    args.output.mkdir(parents=True, exist_ok=True)
    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "import_results": import_results,
        "credentials_to_update": all_credentials,
        "summary": {
            "total": len(workflows),
            "imported": sum(1 for r in import_results if r["status"] == "imported"),
            "failed": sum(1 for r in import_results if r["status"] == "failed"),
            "unique_credentials": len({
                f"{c['credential_type']}:{c['credential_name']}" for c in all_credentials
            }),
        },
    }
    with open(args.output / "workflow_import_report.json", "w") as fh:
        json.dump(report, fh, indent=2)

    if all_credentials:
        logger.warning("=== MANUAL ACTION REQUIRED ===")
        logger.warning("The following credentials must be updated on the target n8n instance:")
        seen = set()
        for cred in all_credentials:
            key = f"{cred['credential_type']}:{cred['credential_name']}"
            if key not in seen:
                seen.add(key)
                logger.warning("  - %s (%s)", cred["credential_name"], cred["credential_type"])

    imported_count = sum(1 for r in import_results if r["status"] == "imported")
    failed_count = sum(1 for r in import_results if r["status"] == "failed")
    print("STATUS: %s n8n_workflow_import (%d imported, %d failed)" % (
        "FAIL" if any_failed else "PASS", imported_count, failed_count))

    if any_failed:
        logger.error("Workflow import completed with failures")
        return 1

    logger.info("Workflow import complete: %d imported (all disabled)", len(import_results))
    return 0


if __name__ == "__main__":
    sys.exit(main())
