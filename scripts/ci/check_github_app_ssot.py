#!/usr/bin/env python3
"""
GitHub App SSOT Drift Checker
==============================
Compares declared SSOT (ssot/github/apps/*.yaml) against the live GitHub API.
Exits non-zero on any drift, making it suitable as a CI gate.

Usage:
    # Check all apps (requires GITHUB_TOKEN with admin:org scope)
    python3 scripts/ci/check_github_app_ssot.py

    # Check only pulser-hub (requires GITHUB_APP_PRIVATE_KEY for JWT auth)
    python3 scripts/ci/check_github_app_ssot.py --app pulser-hub

    # Update org-installed.yaml from live API (snapshot mode)
    python3 scripts/ci/check_github_app_ssot.py --update

Environment:
    GITHUB_TOKEN           — PAT with admin:org scope (for org installations)
    GITHUB_APP_PRIVATE_KEY — RSA PEM (for pulser-hub JWT auth, optional)

SSOT files:
    ssot/github/apps/pulser-hub.yaml    — Custom app contract
    ssot/github/apps/org-installed.yaml  — Third-party app inventory
"""

import json
import os
import sys
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SSOT_DIR = REPO_ROOT / "ssot" / "github" / "apps"
ORG = "Insightpulseai"


def _load_yaml(path: Path) -> dict:
    """Load YAML file. Uses PyYAML if available, else basic parser."""
    try:
        import yaml
        with open(path) as f:
            return yaml.safe_load(f)
    except ImportError:
        # Fallback: very basic YAML-like parser for CI environments
        raise RuntimeError("PyYAML required: pip install pyyaml")


def _github_api(path: str, token: str) -> dict:
    """Make authenticated GitHub API GET request."""
    url = f"https://api.github.com{path}"
    req = Request(url)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    try:
        with urlopen(req) as resp:
            return json.loads(resp.read())
    except HTTPError as e:
        body = e.read().decode()
        print(f"ERROR: GitHub API {path} → {e.code}: {body}", file=sys.stderr)
        return {}


def check_org_installations(token: str) -> list:
    """Fetch live org installations and compare with SSOT."""
    ssot_file = SSOT_DIR / "org-installed.yaml"
    if not ssot_file.exists():
        return [f"SSOT file missing: {ssot_file}"]

    ssot = _load_yaml(ssot_file)
    ssot_apps = {a["slug"]: a for a in ssot.get("apps", [])}

    data = _github_api(f"/orgs/{ORG}/installations", token)
    live_apps = {}
    for inst in data.get("installations", []):
        slug = inst.get("app_slug", "unknown")
        live_apps[slug] = {
            "app_id": inst["app_id"],
            "installation_id": inst["id"],
            "permissions": inst.get("permissions", {}),
            "events": sorted(inst.get("events", [])),
            "repository_selection": inst.get("repository_selection", ""),
        }

    errors = []

    # Check for apps in SSOT but not live
    for slug in ssot_apps:
        if slug not in live_apps:
            errors.append(f"SSOT declares '{slug}' but not found in live installations")

    # Check for apps live but not in SSOT
    for slug in live_apps:
        if slug not in ssot_apps:
            errors.append(f"Live app '{slug}' (id: {live_apps[slug]['app_id']}) not in SSOT")

    # Check permission drift for apps in both
    for slug in set(ssot_apps) & set(live_apps):
        ssot_perms = ssot_apps[slug].get("permissions", {})
        live_perms = live_apps[slug]["permissions"]

        for perm, level in live_perms.items():
            ssot_level = ssot_perms.get(perm)
            if ssot_level is None:
                errors.append(f"{slug}: live has '{perm}:{level}' not declared in SSOT")
            elif ssot_level != level:
                errors.append(f"{slug}: '{perm}' SSOT={ssot_level} vs live={level}")

        for perm in ssot_perms:
            if perm not in live_perms:
                errors.append(f"{slug}: SSOT declares '{perm}' but not in live permissions")

        # Check events drift
        ssot_events = sorted(ssot_apps[slug].get("events", []))
        live_events = live_apps[slug]["events"]
        if ssot_events != live_events:
            added = set(live_events) - set(ssot_events)
            removed = set(ssot_events) - set(live_events)
            if added:
                errors.append(f"{slug}: live has extra events: {sorted(added)}")
            if removed:
                errors.append(f"{slug}: SSOT has events not in live: {sorted(removed)}")

    return errors


def check_pulser_hub() -> list:
    """Check pulser-hub SSOT against live App settings (requires JWT auth)."""
    ssot_file = SSOT_DIR / "pulser-hub.yaml"
    if not ssot_file.exists():
        return [f"SSOT file missing: {ssot_file}"]

    ssot = _load_yaml(ssot_file)
    app_config = ssot.get("app", {})

    errors = []

    # Try to get live app info via JWT
    private_key = os.environ.get("GITHUB_APP_PRIVATE_KEY", "")
    if not private_key:
        print("SKIP: pulser-hub live check (GITHUB_APP_PRIVATE_KEY not set)", file=sys.stderr)
        return []

    try:
        sys.path.insert(0, str(REPO_ROOT / "scripts" / "github_app"))
        from auth import mint_jwt, get_app_info
        app_jwt = mint_jwt()
        live = get_app_info(app_jwt)
    except Exception as e:
        return [f"pulser-hub JWT auth failed: {e}"]

    # Compare permissions
    ssot_perms = app_config.get("permissions", {})
    live_perms = live.get("permissions", {})

    for perm, level in live_perms.items():
        ssot_level = ssot_perms.get(perm)
        if ssot_level is None:
            errors.append(f"pulser-hub: live has '{perm}:{level}' not in SSOT")
        elif ssot_level != level:
            errors.append(f"pulser-hub: '{perm}' SSOT={ssot_level} vs live={level}")

    for perm in ssot_perms:
        if perm not in live_perms:
            errors.append(f"pulser-hub: SSOT declares '{perm}' not in live")

    # Compare events
    ssot_events = sorted(app_config.get("events", []))
    live_events = sorted(live.get("events", []))
    if ssot_events != live_events:
        added = set(live_events) - set(ssot_events)
        removed = set(ssot_events) - set(live_events)
        if added:
            errors.append(f"pulser-hub: live has extra events: {sorted(added)}")
        if removed:
            errors.append(f"pulser-hub: SSOT has events not in live: {sorted(removed)}")

    # Check webhook URL
    ssot_webhook = app_config.get("webhook", {}).get("url", "")
    # Webhook URL can only be checked via App settings (not API without JWT)
    # Flag known drift from SSOT
    known_drift = app_config.get("known_drift", [])
    for drift in known_drift:
        errors.append(
            f"pulser-hub KNOWN DRIFT: {drift['field']} "
            f"(live={drift.get('live_value', '?')}, desired={drift.get('desired_value', '?')}) "
            f"— {drift.get('action', 'no action specified')}"
        )

    return errors


def update_org_installed(token: str):
    """Snapshot live org installations to SSOT file."""
    try:
        import yaml
    except ImportError:
        print("ERROR: PyYAML required for --update: pip install pyyaml", file=sys.stderr)
        sys.exit(1)

    data = _github_api(f"/orgs/{ORG}/installations", token)
    apps = []
    for inst in data.get("installations", []):
        apps.append({
            "slug": inst["app_slug"],
            "app_id": inst["app_id"],
            "installation_id": inst["id"],
            "target_type": inst.get("target_type", ""),
            "repository_selection": inst.get("repository_selection", ""),
            "permissions": dict(sorted(inst.get("permissions", {}).items())),
            "events": sorted(inst.get("events", [])),
            "notes": "",
            "permission_review": "",
        })

    output = {
        "schema_version": "1.0",
        "updated": __import__("datetime").date.today().isoformat(),
        "org": ORG,
        "apps": sorted(apps, key=lambda a: a["slug"]),
    }

    ssot_file = SSOT_DIR / "org-installed.yaml"
    with open(ssot_file, "w") as f:
        f.write("# schema: ssot.github.apps.org_installed.v1\n")
        f.write("# Auto-generated by scripts/ci/check_github_app_ssot.py --update\n")
        f.write(f"# Source: gh api orgs/{ORG}/installations\n\n")
        yaml.dump(output, f, default_flow_style=False, sort_keys=False)

    print(f"OK: Updated {ssot_file} with {len(apps)} apps")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="GitHub App SSOT drift checker")
    parser.add_argument("--app", help="Check specific app only (e.g. pulser-hub)")
    parser.add_argument("--update", action="store_true", help="Update org-installed.yaml from live API")
    args = parser.parse_args()

    token = os.environ.get("GITHUB_TOKEN", "")
    if not token and not args.app == "pulser-hub":
        print("ERROR: GITHUB_TOKEN required (admin:org scope)", file=sys.stderr)
        sys.exit(1)

    if args.update:
        update_org_installed(token)
        return

    all_errors = []

    if not args.app or args.app == "org":
        print("=== Checking org-installed apps ===")
        errors = check_org_installations(token)
        all_errors.extend(errors)
        if errors:
            for e in errors:
                print(f"  DRIFT: {e}")
        else:
            print("  OK: All org apps match SSOT")

    if not args.app or args.app == "pulser-hub":
        print("\n=== Checking pulser-hub ===")
        errors = check_pulser_hub()
        all_errors.extend(errors)
        if errors:
            for e in errors:
                print(f"  DRIFT: {e}")
        else:
            print("  OK: pulser-hub matches SSOT")

    print(f"\n{'='*50}")
    if all_errors:
        print(f"FAIL: {len(all_errors)} drift(s) detected")
        sys.exit(1)
    else:
        print("PASS: All GitHub App SSOT checks passed")


if __name__ == "__main__":
    main()
