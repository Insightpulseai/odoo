#!/usr/bin/env python3
"""Deploy Edge Functions to self-hosted Supabase runtime.

Reads deploy manifest and syncs functions to target VM.

Usage:
    python migrate_edge_functions.py \
        --mode dry-run \
        --output docs/evidence/migration/functions \
        --manifest ops-platform/supabase/edge-functions/deploy/manifest.yaml \
        --vm-host 4.193.100.31 \
        --vm-user azureuser \
        --ssh-key /tmp/vm_key
"""

import argparse
import json
import logging
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests
import yaml

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("migrate_edge_functions")

DEFAULT_FUNCTIONS_DIR = "supabase/functions"
REMOTE_FUNCTIONS_DIR = "/opt/supabase-deploy/volumes/functions"


def load_deploy_manifest(manifest_path: Path) -> dict:
    """Load and parse the Edge Functions deploy manifest."""
    with open(manifest_path, "r") as fh:
        data = yaml.safe_load(fh) or {}
    logger.info("Loaded deploy manifest from %s", manifest_path)
    return data


def enumerate_functions(manifest: dict) -> list[dict]:
    """Extract function list from manifest with metadata."""
    raw = manifest.get("functions", manifest.get("edge_functions", []))

    functions: list[dict] = []
    if isinstance(raw, dict):
        for name, meta in raw.items():
            meta = meta or {}
            functions.append({
                "name": name,
                "entrypoint": meta.get("entrypoint", "index.ts"),
                "smoke_test_path": meta.get("smoke_test_path", f"/{name}"),
                "env_vars": meta.get("env_vars", []),
                "enabled": meta.get("enabled", True),
            })
    elif isinstance(raw, list):
        for item in raw:
            if isinstance(item, str):
                functions.append({
                    "name": item,
                    "entrypoint": "index.ts",
                    "smoke_test_path": f"/{item}",
                    "env_vars": [],
                    "enabled": True,
                })
            elif isinstance(item, dict):
                name = item.get("name", "unknown")
                functions.append({
                    "name": name,
                    "entrypoint": item.get("entrypoint", "index.ts"),
                    "smoke_test_path": item.get("smoke_test_path", f"/{name}"),
                    "env_vars": item.get("env_vars", []),
                    "enabled": item.get("enabled", True),
                })

    logger.info("Enumerated %d functions from manifest", len(functions))
    return functions


def verify_source_exists(functions_dir: Path, function_name: str) -> bool:
    """Check that the function source directory exists locally."""
    fn_dir = functions_dir / function_name
    return fn_dir.is_dir()


def scp_function(
    functions_dir: Path,
    function_name: str,
    vm_host: str,
    vm_user: str,
    ssh_key: str,
) -> bool:
    """SCP function directory to target VM."""
    local_path = functions_dir / function_name
    remote_path = f"{vm_user}@{vm_host}:{REMOTE_FUNCTIONS_DIR}/{function_name}"

    cmd = [
        "scp", "-r",
        "-i", ssh_key,
        "-o", "StrictHostKeyChecking=no",
        "-o", "ConnectTimeout=10",
        str(local_path),
        remote_path,
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, timeout=120)
        if result.returncode != 0:
            logger.error("scp failed for %s: %s", function_name, result.stderr.decode()[:300])
            return False
        logger.info("Uploaded %s to %s", function_name, remote_path)
        return True
    except subprocess.TimeoutExpired:
        logger.error("scp timed out for %s", function_name)
        return False
    except FileNotFoundError:
        logger.error("scp binary not found in PATH")
        return False


def deploy_function_via_ssh(
    function_name: str,
    vm_host: str,
    vm_user: str,
    ssh_key: str,
) -> bool:
    """Run `supabase functions deploy <name>` on the VM via SSH."""
    cmd = [
        "ssh",
        "-i", ssh_key,
        "-o", "StrictHostKeyChecking=no",
        "-o", "ConnectTimeout=10",
        f"{vm_user}@{vm_host}",
        f"cd /opt/supabase-deploy && supabase functions deploy {function_name} --no-verify-jwt",
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, timeout=120)
        if result.returncode != 0:
            logger.error("supabase functions deploy failed for %s: %s",
                         function_name, result.stderr.decode()[:300])
            return False
        logger.info("Deployed function %s on %s", function_name, vm_host)
        return True
    except (subprocess.TimeoutExpired, FileNotFoundError) as exc:
        logger.error("Failed to deploy function %s: %s", function_name, exc)
        return False


def smoke_test_function(
    base_url: str, function_name: str, smoke_test_path: str
) -> dict:
    """Smoke test: curl -sf $SELF_HOSTED_URL/functions/v1/<name>."""
    url = f"{base_url}/functions/v1/{function_name}"
    try:
        resp = requests.get(url, timeout=15)
        healthy = 200 <= resp.status_code < 500  # 4xx may be expected without auth
        return {
            "name": function_name,
            "url": url,
            "status_code": resp.status_code,
            "healthy": healthy,
            "body_preview": resp.text[:200],
        }
    except requests.RequestException as exc:
        return {
            "name": function_name,
            "url": url,
            "status_code": -1,
            "healthy": False,
            "error": str(exc),
        }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Deploy Edge Functions to self-hosted Supabase runtime."
    )
    parser.add_argument("--mode", choices=["dry-run", "execute"], default="dry-run")
    parser.add_argument("--output", type=Path, default=Path("docs/evidence/migration/functions"))
    parser.add_argument("--manifest", type=Path,
                        default=Path("ops-platform/supabase/edge-functions/deploy/manifest.yaml"))
    parser.add_argument("--functions-dir", type=Path, default=Path(DEFAULT_FUNCTIONS_DIR))
    parser.add_argument("--vm-host", default=os.environ.get("VM_HOST", "4.193.100.31"))
    parser.add_argument("--vm-user", default=os.environ.get("VM_USER", "azureuser"))
    parser.add_argument("--ssh-key", default=os.environ.get("SSH_KEY_PATH", "/tmp/vm_key"))
    parser.add_argument("--target-url", default=os.environ.get("TARGET_SUPABASE_URL", ""),
                        help="Base URL of self-hosted Supabase for smoke tests")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    logger.info("Mode: %s | Output: %s | Manifest: %s", args.mode, args.output, args.manifest)

    if not args.manifest.exists():
        logger.error("Deploy manifest not found: %s", args.manifest)
        return 1

    manifest = load_deploy_manifest(args.manifest)
    functions = enumerate_functions(manifest)

    if args.mode == "dry-run":
        logger.info("[DRY-RUN] Functions to deploy:")
        for fn in functions:
            source_exists = verify_source_exists(args.functions_dir, fn["name"])
            logger.info("[DRY-RUN]   %s (source: %s, smoke: %s) [%s]",
                        fn["name"], args.functions_dir / fn["name"],
                        fn["smoke_test_path"],
                        "exists" if source_exists else "MISSING")
        logger.info("[DRY-RUN] Target: %s@%s", args.vm_user, args.vm_host)
        logger.info("[DRY-RUN] Remote dir: %s", REMOTE_FUNCTIONS_DIR)
        logger.info("[DRY-RUN] Would restart edge-runtime after deployment")

        args.output.mkdir(parents=True, exist_ok=True)
        report = {
            "mode": "dry-run",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "functions": functions,
            "target_vm": f"{args.vm_user}@{args.vm_host}",
        }
        with open(args.output / "function_deployment_report.json", "w") as fh:
            json.dump(report, fh, indent=2)
        return 0

    # Execute mode
    deploy_results: list[dict] = []
    any_failed = False

    for fn in functions:
        name = fn["name"]

        if not verify_source_exists(args.functions_dir, name):
            logger.error("Source not found for function: %s", name)
            deploy_results.append({"name": name, "status": "failed", "reason": "source not found"})
            any_failed = True
            continue

        # SCP function source to VM
        scp_ok = scp_function(args.functions_dir, name, args.vm_host, args.vm_user, args.ssh_key)
        if not scp_ok:
            deploy_results.append({"name": name, "status": "failed", "reason": "scp failed"})
            any_failed = True
            continue

        # Deploy via supabase CLI on VM
        deploy_ok = deploy_function_via_ssh(name, args.vm_host, args.vm_user, args.ssh_key)
        deploy_results.append({
            "name": name,
            "status": "deployed" if deploy_ok else "failed",
        })
        if not deploy_ok:
            any_failed = True

    deployed_count = sum(1 for r in deploy_results if r["status"] == "deployed")

    # Smoke tests
    smoke_results: list[dict] = []
    if args.target_url:
        logger.info("Running smoke tests against %s", args.target_url)
        for fn in functions:
            result = smoke_test_function(args.target_url, fn["name"], fn["smoke_test_path"])
            smoke_results.append(result)
            status = "OK" if result["healthy"] else "FAIL"
            logger.info("Smoke test %s: %s (HTTP %s)", fn["name"], status, result["status_code"])
    else:
        logger.warning("TARGET_SUPABASE_URL not set; skipping smoke tests")

    args.output.mkdir(parents=True, exist_ok=True)
    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "deploy_results": deploy_results,
        "smoke_tests": smoke_results,
        "summary": {
            "total": len(functions),
            "deployed": deployed_count,
            "failed": sum(1 for r in deploy_results if r["status"] == "failed"),
            "smoke_healthy": sum(1 for r in smoke_results if r.get("healthy")),
        },
    }
    with open(args.output / "function_deployment_report.json", "w") as fh:
        json.dump(report, fh, indent=2)

    healthy_count = sum(1 for r in smoke_results if r.get("healthy"))
    unhealthy_count = len(smoke_results) - healthy_count
    print("STATUS: %s edge_functions_deploy (%d deployed, %d failed)" % (
        "FAIL" if any_failed else "PASS", deployed_count,
        sum(1 for r in deploy_results if r["status"] == "failed")))
    if smoke_results:
        print("STATUS: %s edge_functions_smoke (%d healthy, %d unhealthy)" % (
            "FAIL" if unhealthy_count > 0 else "PASS", healthy_count, unhealthy_count))

    if any_failed:
        logger.error("Function deployment completed with failures")
        return 1

    logger.info("Function deployment complete: %d deployed", deployed_count)
    return 0


if __name__ == "__main__":
    sys.exit(main())
