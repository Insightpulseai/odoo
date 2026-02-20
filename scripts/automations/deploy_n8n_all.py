#!/usr/bin/env python3
"""
deploy_n8n_all.py — Idempotent, diff-based n8n workflow deployer.

Deploys all canonical workflow JSONs from automations/n8n/ to a target n8n instance.
Safe by default (dry-run). Requires --apply for live deployment.

Usage:
    python scripts/automations/deploy_n8n_all.py \
        [--env {dev,stage,prod}] \
        [--dry-run] \
        [--apply] \
        [--out out/automation_sweep] \
        [--verbose]

Required env vars (for --apply):
    N8N_BASE_URL    https://n8n.insightpulseai.com
    N8N_API_KEY     <jwt>

Exit codes:
    0  = all deploys succeeded (or dry-run complete)
    1  = missing env vars / validation errors
    2  = one or more deploys failed
"""
import argparse
import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CANONICAL_DIR = REPO_ROOT / "automations" / "n8n"
WORKFLOW_DIRS = [
    CANONICAL_DIR / "workflows",
    CANONICAL_DIR,
]


# ---------------------------------------------------------------------------
# n8n API helpers
# ---------------------------------------------------------------------------


def n8n_request(method: str, path: str, base_url: str, api_key: str, body: dict = None):
    url = f"{base_url.rstrip('/')}{path}"
    headers = {
        "X-N8N-API-KEY": api_key,
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "n8n-deploy/1.0 curl/8.7.1",
    }
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode()), resp.status
    except urllib.error.HTTPError as e:
        body_text = e.read().decode(errors="replace")
        return {"error": body_text, "status": e.code}, e.code
    except Exception as e:
        return {"error": str(e)}, 0


def list_workflows(base_url: str, api_key: str) -> list[dict]:
    data, status = n8n_request("GET", "/api/v1/workflows", base_url, api_key)
    if status != 200:
        return []
    return data.get("data", [])


def get_workflow_by_name(name: str, workflows: list[dict]) -> dict | None:
    for wf in workflows:
        if wf.get("name") == name:
            return wf
    return None


_API_ALLOWED_KEYS = {"name", "nodes", "connections", "settings", "staticData"}


def _strip_for_api(wf_json: dict) -> dict:
    """Strip read-only / additional fields rejected by n8n v2 Public API."""
    return {k: v for k, v in wf_json.items() if k in _API_ALLOWED_KEYS}


def create_workflow(wf_json: dict, base_url: str, api_key: str) -> tuple[dict, int]:
    return n8n_request("POST", "/api/v1/workflows", base_url, api_key, body=_strip_for_api(wf_json))


def update_workflow(wf_id: str, wf_json: dict, base_url: str, api_key: str) -> tuple[dict, int]:
    return n8n_request("PUT", f"/api/v1/workflows/{wf_id}", base_url, api_key, body=_strip_for_api(wf_json))


def workflows_differ(local: dict, remote: dict) -> bool:
    """Compare workflow content (nodes + connections), ignoring metadata."""
    def normalize(wf: dict) -> dict:
        return {
            "name": wf.get("name"),
            "nodes": wf.get("nodes", []),
            "connections": wf.get("connections", {}),
            "settings": wf.get("settings", {}),
        }
    return json.dumps(normalize(local), sort_keys=True) != json.dumps(normalize(remote), sort_keys=True)


# ---------------------------------------------------------------------------
# Load local workflows
# ---------------------------------------------------------------------------


def load_local_workflows(verbose: bool) -> list[dict]:
    results = []
    seen_names = set()

    for wf_dir in WORKFLOW_DIRS:
        if not wf_dir.exists():
            continue
        for fpath in sorted(wf_dir.glob("*.json")):
            try:
                data = json.loads(fpath.read_text(encoding="utf-8", errors="replace"))
            except Exception as e:
                print(f"  WARN: Cannot parse {fpath}: {e}", file=sys.stderr)
                continue
            # Basic shape validation
            if not {"name", "nodes", "connections"}.issubset(data.keys()):
                if verbose:
                    print(f"  SKIP: {fpath.name} — not a valid n8n workflow shape", file=sys.stderr)
                continue
            name = data.get("name", "")
            if name in seen_names:
                if verbose:
                    print(f"  SKIP: {fpath.name} — duplicate name '{name}'", file=sys.stderr)
                continue
            seen_names.add(name)
            data["_source_path"] = str(fpath.relative_to(REPO_ROOT))
            results.append(data)

    if verbose:
        print(f"  Loaded {len(results)} canonical workflows", file=sys.stderr)
    return results


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description="Idempotent n8n workflow deployer")
    parser.add_argument("--env", choices=["dev", "stage", "prod"], default="stage")
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--out", default="out/automation_sweep")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    is_apply = args.apply
    v = args.verbose
    out_dir = REPO_ROOT / args.out
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"=== n8n Deploy ({'APPLY' if is_apply else 'DRY-RUN'}) | env={args.env}", file=sys.stderr)

    # Env var check
    base_url = os.environ.get("N8N_BASE_URL", "").rstrip("/")
    api_key = os.environ.get("N8N_API_KEY", "")

    if not base_url or not api_key:
        if is_apply:
            print("✗ ERROR: N8N_BASE_URL and N8N_API_KEY must be set for --apply", file=sys.stderr)
            return 1
        else:
            print("  WARN: N8N_BASE_URL/N8N_API_KEY not set — dry-run only, no API calls", file=sys.stderr)
            base_url = "https://n8n.insightpulseai.com"

    # Load local workflows
    local_wfs = load_local_workflows(v)
    if not local_wfs:
        print("✗ No valid workflow JSONs found in automations/n8n/", file=sys.stderr)
        return 1

    # Fetch remote workflows (if API key available)
    remote_wfs = []
    if api_key:
        print(f"  Fetching remote workflows from {base_url}...", file=sys.stderr)
        remote_wfs = list_workflows(base_url, api_key)
        print(f"  Remote: {len(remote_wfs)} workflows", file=sys.stderr)

    # Plan
    results = []
    for local in local_wfs:
        name = local["name"]
        remote = get_workflow_by_name(name, remote_wfs)

        if remote is None:
            action = "CREATE"
        elif workflows_differ(local, remote):
            action = "UPDATE"
        else:
            action = "SKIP (identical)"

        result = {
            "name": name,
            "source": local.get("_source_path"),
            "action": action,
            "remote_id": remote.get("id") if remote else None,
            "status": "planned",
        }

        print(f"  {action:20s} {name}", file=sys.stderr)

        if is_apply and action in ("CREATE", "UPDATE"):
            # Remove internal key before posting
            payload = {k: v for k, v in local.items() if not k.startswith("_")}
            if action == "CREATE":
                resp, status = create_workflow(payload, base_url, api_key)
                result["status"] = "created" if status in (200, 201) else "failed"
            else:
                resp, status = update_workflow(str(remote["id"]), payload, base_url, api_key)
                result["status"] = "updated" if status == 200 else "failed"
            result["response_status"] = status
            if result["status"] == "failed":
                result["error"] = resp.get("error", str(resp))
                print(f"  ✗ FAILED: {name} — {result['error'][:100]}", file=sys.stderr)
        elif not is_apply and action in ("CREATE", "UPDATE"):
            result["status"] = "dry-run"

        results.append(result)

    # Write results
    deploy_report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "env": args.env,
        "apply": is_apply,
        "base_url": base_url,
        "total": len(results),
        "created": sum(1 for r in results if r["status"] == "created"),
        "updated": sum(1 for r in results if r["status"] == "updated"),
        "skipped": sum(1 for r in results if "SKIP" in r["action"]),
        "failed": sum(1 for r in results if r["status"] == "failed"),
        "dry_run": sum(1 for r in results if r["status"] == "dry-run"),
        "results": results,
    }

    out_path = out_dir / "deploy_results.json"
    out_path.write_text(json.dumps(deploy_report, indent=2), encoding="utf-8")
    print(f"\n  Results written: {out_path}", file=sys.stderr)
    print(
        f"  Created={deploy_report['created']}  Updated={deploy_report['updated']}  "
        f"Skipped={deploy_report['skipped']}  Failed={deploy_report['failed']}  "
        f"DryRun={deploy_report['dry_run']}",
        file=sys.stderr,
    )

    if deploy_report["failed"] > 0:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
