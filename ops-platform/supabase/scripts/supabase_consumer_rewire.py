#!/usr/bin/env python3
"""
supabase_consumer_rewire.py — Rewire consumers from cloud to self-hosted Supabase.

Reads consumer manifest and updates SUPABASE_URL, SUPABASE_ANON_KEY,
SUPABASE_SERVICE_ROLE_KEY for each consumer based on its type.

Usage:
    python3 supabase_consumer_rewire.py [--dry-run] [--consumer <name>]
    python3 supabase_consumer_rewire.py --help
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


KV_NAME = os.environ.get("KV_NAME", "kv-ipai-dev")
VM_HOST = os.environ.get("VM_HOST", "4.193.100.31")
VM_USER = os.environ.get("VM_USER", "azureuser")
DEFAULT_EVIDENCE_DIR = f"docs/evidence/{datetime.now().strftime('%Y%m%d-%H%M')}/supabase-migration"
REPO_ROOT = subprocess.run(
    ["git", "rev-parse", "--show-toplevel"],
    capture_output=True, text=True
).stdout.strip() or "."
MANIFEST_PATH = os.path.join(
    REPO_ROOT, "ops-platform/supabase/cutover/consumers.yaml"
)


def get_kv_secret(name: str) -> str:
    try:
        result = subprocess.run(
            ["az", "keyvault", "secret", "show",
             "--vault-name", KV_NAME, "--name", name,
             "--query", "value", "-o", "tsv"],
            capture_output=True, text=True, check=True, timeout=30,
        )
        return result.stdout.strip()
    except Exception:
        return ""


def run_cmd(cmd: list[str], timeout: int = 60) -> tuple[int, str, str]:
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except Exception as exc:
        return 1, "", str(exc)


def load_manifest(path: str) -> list[dict]:
    """Load consumers.yaml. Supports simple YAML without pyyaml dependency."""
    if not os.path.exists(path):
        print(f"[WARN] Manifest not found at {path}. Using built-in defaults.", file=sys.stderr)
        return get_default_consumers()

    try:
        import yaml
        with open(path) as f:
            data = yaml.safe_load(f)
        return data.get("consumers", []) if isinstance(data, dict) else data
    except ImportError:
        # Parse simple YAML without pyyaml
        return parse_simple_yaml(path)


def parse_simple_yaml(path: str) -> list[dict]:
    """Minimal YAML parser for the consumer manifest."""
    consumers = []
    current = None

    with open(path) as f:
        for line in f:
            stripped = line.rstrip()
            if not stripped or stripped.startswith("#"):
                continue

            indent = len(line) - len(line.lstrip())

            if stripped.startswith("- name:"):
                if current:
                    consumers.append(current)
                current = {"name": stripped.split(":", 1)[1].strip().strip('"').strip("'")}
            elif current and ":" in stripped:
                key, _, val = stripped.partition(":")
                key = key.strip().strip("-").strip()
                val = val.strip().strip('"').strip("'")
                if key == "env_vars" or key == "smoke_test":
                    # Handle as sub-dict or string
                    current[key] = val if val else {}
                else:
                    current[key] = val

    if current:
        consumers.append(current)
    return consumers


def get_default_consumers() -> list[dict]:
    """Built-in consumer list when no manifest exists."""
    return [
        {
            "name": "ipai-odoo-dev-web",
            "type": "container_app",
            "resource_group": "rg-ipai-dev",
            "env_vars": "SUPABASE_URL,SUPABASE_ANON_KEY,SUPABASE_SERVICE_ROLE_KEY",
            "smoke_test": "curl -sf https://erp.insightpulseai.com/web/health",
        },
        {
            "name": "ipai-mcp-dev",
            "type": "container_app",
            "resource_group": "rg-ipai-dev",
            "env_vars": "SUPABASE_URL,SUPABASE_ANON_KEY,SUPABASE_SERVICE_ROLE_KEY",
            "smoke_test": "curl -sf https://mcp.insightpulseai.com/health",
        },
        {
            "name": "n8n",
            "type": "env_file",
            "env_file_path": "/opt/n8n/.env",
            "env_vars": "SUPABASE_URL,SUPABASE_ANON_KEY,SUPABASE_SERVICE_ROLE_KEY",
            "smoke_test": "curl -sf https://n8n.insightpulseai.com/healthz",
        },
        {
            "name": "github-actions",
            "type": "github_actions",
            "repo": "Insightpulseai/odoo",
            "env_vars": "SUPABASE_URL,SUPABASE_ANON_KEY,SUPABASE_SERVICE_ROLE_KEY",
            "smoke_test": "",
        },
    ]


def rewire_container_app(consumer: dict, new_vars: dict, dry_run: bool) -> dict:
    """Update Azure Container App environment variables."""
    name = consumer["name"]
    rg = consumer.get("resource_group", "rg-ipai-dev")

    set_args = " ".join(
        f"{k}={v}" for k, v in new_vars.items()
    )
    cmd = [
        "az", "containerapp", "update",
        "--name", name,
        "--resource-group", rg,
        "--set-env-vars", *[f"{k}={v}" for k, v in new_vars.items()],
    ]

    if dry_run:
        return {"status": "dry_run", "command": " ".join(cmd)}

    rc, stdout, stderr = run_cmd(cmd, timeout=120)
    if rc == 0:
        return {"status": "success", "output": stdout[:200]}
    return {"status": "failed", "error": stderr[:200]}


def rewire_github_actions(consumer: dict, new_vars: dict, dry_run: bool) -> dict:
    """Update GitHub Actions secrets."""
    repo = consumer.get("repo", "Insightpulseai/odoo")
    results = {}

    for key, value in new_vars.items():
        cmd_str = f"echo '{value}' | gh secret set {key} --repo {repo}"
        if dry_run:
            results[key] = "dry_run"
            continue

        rc, stdout, stderr = run_cmd(
            ["bash", "-c", f"echo '{value}' | gh secret set {key} --repo {repo}"],
            timeout=30,
        )
        results[key] = "success" if rc == 0 else f"failed: {stderr[:100]}"

    return {"status": "dry_run" if dry_run else "attempted", "secrets": results}


def rewire_env_file(consumer: dict, new_vars: dict, dry_run: bool) -> dict:
    """Update .env file on VM via SSH."""
    env_path = consumer.get("env_file_path", "/opt/n8n/.env")

    # Build sed commands to replace existing vars or append new ones
    sed_cmds = []
    for key, value in new_vars.items():
        # Escape special characters in value
        escaped_value = value.replace("/", "\\/").replace("&", "\\&")
        sed_cmds.append(
            f"grep -q '^{key}=' {env_path} && "
            f"sed -i 's|^{key}=.*|{key}={value}|' {env_path} || "
            f"echo '{key}={value}' >> {env_path}"
        )

    ssh_cmd = " && ".join(sed_cmds)
    full_cmd = [
        "ssh", "-o", "StrictHostKeyChecking=accept-new",
        "-o", "ConnectTimeout=10",
        f"{VM_USER}@{VM_HOST}",
        ssh_cmd,
    ]

    if dry_run:
        return {"status": "dry_run", "file": env_path, "vars": list(new_vars.keys())}

    rc, stdout, stderr = run_cmd(full_cmd, timeout=30)
    if rc == 0:
        return {"status": "success", "file": env_path}
    return {"status": "failed", "error": stderr[:200]}


def run_smoke_test(consumer: dict) -> dict:
    """Run the consumer's smoke test."""
    test_cmd = consumer.get("smoke_test", "")
    if not test_cmd:
        return {"status": "skipped", "reason": "no smoke test defined"}

    rc, stdout, stderr = run_cmd(["bash", "-c", test_cmd], timeout=15)
    return {
        "status": "pass" if rc == 0 else "fail",
        "command": test_cmd,
        "output": stdout[:200] if stdout else stderr[:200],
    }


REWIRE_HANDLERS = {
    "container_app": rewire_container_app,
    "github_actions": rewire_github_actions,
    "env_file": rewire_env_file,
}


def main():
    parser = argparse.ArgumentParser(
        description="Rewire consumers from cloud to self-hosted Supabase.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would change without changing")
    parser.add_argument("--consumer", default="",
                        help="Rewire single consumer by name")
    parser.add_argument("--output-dir",
                        default=os.environ.get("EVIDENCE_DIR", DEFAULT_EVIDENCE_DIR),
                        help="Evidence output directory")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    print(f"[INFO] Loading consumer manifest from {MANIFEST_PATH}", file=sys.stderr)
    consumers = load_manifest(MANIFEST_PATH)

    if args.consumer:
        consumers = [c for c in consumers if c.get("name") == args.consumer]
        if not consumers:
            print(f"[ERROR] Consumer '{args.consumer}' not found in manifest.", file=sys.stderr)
            sys.exit(1)

    print(f"[INFO] Consumers to rewire: {len(consumers)}", file=sys.stderr)

    # Get new self-hosted credentials
    print("[INFO] Fetching self-hosted Supabase credentials from Key Vault...", file=sys.stderr)
    new_vars = {
        "SUPABASE_URL": os.environ.get(
            "SUPABASE_SELF_HOSTED_URL",
            get_kv_secret("supabase-self-hosted-url") or "https://supabase.insightpulseai.com"
        ),
        "SUPABASE_ANON_KEY": os.environ.get(
            "SUPABASE_SELF_HOSTED_ANON_KEY",
            get_kv_secret("supabase-self-hosted-anon-key")
        ),
        "SUPABASE_SERVICE_ROLE_KEY": os.environ.get(
            "SUPABASE_SELF_HOSTED_SERVICE_ROLE_KEY",
            get_kv_secret("supabase-self-hosted-service-role-key")
        ),
    }

    missing = [k for k, v in new_vars.items() if not v]
    if missing and not args.dry_run:
        print(f"[ERROR] Missing self-hosted credentials: {', '.join(missing)}", file=sys.stderr)
        print("[ERROR] Add them to KV or set via environment variables.", file=sys.stderr)
        sys.exit(1)

    if args.dry_run:
        print("[DRY RUN] New values:", file=sys.stderr)
        for k, v in new_vars.items():
            print(f"  {k}: {v[:20]}..." if v else f"  {k}: <not set>", file=sys.stderr)

    # Process each consumer
    results = []
    for consumer in consumers:
        name = consumer.get("name", "unknown")
        ctype = consumer.get("type", "unknown")
        print(f"\n[INFO] Rewiring: {name} (type: {ctype})", file=sys.stderr)

        handler = REWIRE_HANDLERS.get(ctype)
        if not handler:
            print(f"  [WARN] Unknown consumer type: {ctype}", file=sys.stderr)
            result = {"name": name, "type": ctype, "rewire": {"status": "skipped", "reason": f"unknown type: {ctype}"}, "smoke_test": {"status": "skipped"}}
            results.append(result)
            continue

        # Rewire
        rewire_result = handler(consumer, new_vars, args.dry_run)
        print(f"  Rewire: {rewire_result.get('status', 'unknown')}", file=sys.stderr)

        # Smoke test (skip in dry run)
        if args.dry_run:
            smoke_result = {"status": "skipped", "reason": "dry run"}
        else:
            print(f"  Running smoke test...", file=sys.stderr)
            smoke_result = run_smoke_test(consumer)
            print(f"  Smoke test: {smoke_result.get('status', 'unknown')}", file=sys.stderr)

        results.append({
            "name": name,
            "type": ctype,
            "rewire": rewire_result,
            "smoke_test": smoke_result,
        })

    # Write evidence
    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "dry_run": args.dry_run,
        "target_url": new_vars.get("SUPABASE_URL", ""),
        "consumer_count": len(results),
        "results": results,
        "summary": {
            "rewired": sum(1 for r in results if r["rewire"].get("status") in ("success", "dry_run")),
            "failed": sum(1 for r in results if r["rewire"].get("status") == "failed"),
            "smoke_pass": sum(1 for r in results if r["smoke_test"].get("status") == "pass"),
            "smoke_fail": sum(1 for r in results if r["smoke_test"].get("status") == "fail"),
        },
    }

    evidence_path = os.path.join(args.output_dir, "consumer_rewire_results.json")
    with open(evidence_path, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n[INFO] Evidence saved to {evidence_path}", file=sys.stderr)

    # Print report
    output = json.dumps(report, indent=2)
    print(output)

    # Exit code based on results
    if report["summary"]["failed"] > 0 and not args.dry_run:
        sys.exit(1)


if __name__ == "__main__":
    main()
