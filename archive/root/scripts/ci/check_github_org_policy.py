#!/usr/bin/env python3
"""
GitHub Org Policy SSOT Drift Checker
=====================================
Compares declared SSOT (ssot/github/org-policy.yaml and ssot/github/branch-protection.yaml)
against the live GitHub API. Exits non-zero on any drift, making it suitable as a CI gate.

Usage:
    # Full drift check (requires GITHUB_TOKEN with admin:org scope)
    python3 scripts/ci/check_github_org_policy.py

    # Validate YAML structure only (no API calls)
    python3 scripts/ci/check_github_org_policy.py --validate-only

    # Check only org policy (skip branch protection)
    python3 scripts/ci/check_github_org_policy.py --scope org

    # Check only branch protection (skip org policy)
    python3 scripts/ci/check_github_org_policy.py --scope branch

Environment:
    GITHUB_TOKEN — PAT with admin:org scope (for org settings)
                   and repo scope (for branch protection)

SSOT files:
    ssot/github/org-policy.yaml         — Org-level security policy
    ssot/github/branch-protection.yaml  — Branch protection rules
"""

import json
import os
import sys
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
ORG_POLICY_FILE = REPO_ROOT / "ssot" / "github" / "org-policy.yaml"
BRANCH_PROTECTION_FILE = REPO_ROOT / "ssot" / "github" / "branch-protection.yaml"
ORG = "Insightpulseai"
REPO = "odoo"


def _load_yaml(path: Path) -> dict:
    """Load YAML file. Requires PyYAML."""
    try:
        import yaml
    except ImportError:
        print("ERROR: PyYAML required: pip install pyyaml", file=sys.stderr)
        sys.exit(1)
    with open(path) as f:
        return yaml.safe_load(f)


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
        if e.code == 404:
            # Branch protection not configured returns 404
            return {"_not_found": True}
        print(f"ERROR: GitHub API {path} -> {e.code}: {body}", file=sys.stderr)
        return {"_error": True, "_code": e.code, "_body": body}


# =============================================================================
# Org Policy Validation (structure only)
# =============================================================================

def validate_org_policy_structure() -> list:
    """Validate org-policy.yaml has all required fields."""
    if not ORG_POLICY_FILE.exists():
        return [f"SSOT file missing: {ORG_POLICY_FILE}"]

    ssot = _load_yaml(ORG_POLICY_FILE)
    errors = []

    # Top-level keys
    for key in ["schema_version", "updated", "org", "organization", "security"]:
        if key not in ssot:
            errors.append(f"org-policy.yaml: missing top-level key: {key}")

    org = ssot.get("organization", {})

    # Required org settings
    required_org_fields = [
        "two_factor_requirement",
        "default_repository_permission",
        "members_can_create_repositories",
        "members_can_create_public_repositories",
        "members_can_create_private_repositories",
        "members_can_fork_private_repositories",
    ]
    for field in required_org_fields:
        entry = org.get(field, {})
        if not isinstance(entry, dict) or "desired" not in entry:
            errors.append(f"org-policy.yaml: organization.{field}.desired is required")

    # Security features
    security = ssot.get("security", {})
    required_security_fields = [
        "secret_scanning",
        "push_protection",
        "dependabot_alerts",
        "dependabot_security_updates",
    ]
    for field in required_security_fields:
        entry = security.get(field, {})
        if not isinstance(entry, dict) or "desired" not in entry:
            errors.append(f"org-policy.yaml: security.{field}.desired is required")

    # Actions section
    actions = ssot.get("actions", {})
    required_actions_fields = [
        "allowed_actions",
        "default_workflow_permissions",
    ]
    for field in required_actions_fields:
        entry = actions.get(field, {})
        if not isinstance(entry, dict) or "desired" not in entry:
            errors.append(f"org-policy.yaml: actions.{field}.desired is required")

    return errors


def validate_branch_protection_structure() -> list:
    """Validate branch-protection.yaml has all required fields."""
    if not BRANCH_PROTECTION_FILE.exists():
        return [f"SSOT file missing: {BRANCH_PROTECTION_FILE}"]

    ssot = _load_yaml(BRANCH_PROTECTION_FILE)
    errors = []

    # Top-level keys
    for key in ["schema_version", "updated", "repo", "branches"]:
        if key not in ssot:
            errors.append(f"branch-protection.yaml: missing top-level key: {key}")

    branches = ssot.get("branches", {})
    main_branch = branches.get("main", {})

    if not main_branch:
        errors.append("branch-protection.yaml: branches.main is required")
        return errors

    # Required branch protection fields
    required_bp_fields = [
        "require_pull_request",
        "dismiss_stale_reviews",
        "require_status_checks",
        "restrict_force_push",
        "restrict_deletions",
    ]
    for field in required_bp_fields:
        entry = main_branch.get(field, {})
        if not isinstance(entry, dict) or "desired" not in entry:
            errors.append(f"branch-protection.yaml: branches.main.{field}.desired is required")

    # Required status checks must be specified
    status_checks = main_branch.get("require_status_checks", {})
    required_checks = status_checks.get("required_checks", [])
    if status_checks.get("desired") is True and not required_checks:
        errors.append("branch-protection.yaml: require_status_checks.required_checks list is empty")

    return errors


# =============================================================================
# Org Policy Drift Check (live API)
# =============================================================================

def check_org_policy_drift(token: str) -> list:
    """Compare org-policy.yaml against live GitHub API."""
    ssot = _load_yaml(ORG_POLICY_FILE)
    org_settings = ssot.get("organization", {})
    errors = []

    # Fetch live org settings
    live = _github_api(f"/orgs/{ORG}", token)
    if "_error" in live:
        return [f"Cannot fetch org settings: API returned {live.get('_code', '?')}"]

    # Map SSOT fields to GitHub API response fields
    field_mapping = {
        "two_factor_requirement": "two_factor_requirement_enabled",
        "default_repository_permission": "default_repository_permission",
        "members_can_create_repositories": "members_can_create_repositories",
        "members_can_create_public_repositories": "members_can_create_public_repositories",
        "members_can_create_private_repositories": "members_can_create_private_repositories",
        "members_can_create_internal_repositories": "members_can_create_internal_repositories",
        "members_can_fork_private_repositories": "members_can_fork_private_repositories",
    }

    for ssot_field, api_field in field_mapping.items():
        entry = org_settings.get(ssot_field, {})
        if not isinstance(entry, dict):
            continue

        desired = entry.get("desired")
        if desired is None:
            continue

        live_value = live.get(api_field)
        if live_value is None:
            # Field not in API response (may require higher privilege)
            continue

        if live_value != desired:
            errors.append(
                f"organization.{ssot_field}: "
                f"live={live_value}, desired={desired}"
            )

    # Check Actions permissions
    actions_ssot = ssot.get("actions", {})
    live_actions = _github_api(f"/orgs/{ORG}/actions/permissions", token)
    if "_error" not in live_actions and "_not_found" not in live_actions:
        # Check allowed_actions
        allowed_desired = actions_ssot.get("allowed_actions", {}).get("desired")
        if allowed_desired and live_actions.get("allowed_actions") != allowed_desired:
            errors.append(
                f"actions.allowed_actions: "
                f"live={live_actions.get('allowed_actions')}, desired={allowed_desired}"
            )

        # Check default_workflow_permissions
        wf_perms_desired = actions_ssot.get("default_workflow_permissions", {}).get("desired")
        if wf_perms_desired:
            live_wf_perms = _github_api(
                f"/orgs/{ORG}/actions/permissions/workflow", token
            )
            if "_error" not in live_wf_perms:
                live_perm = live_wf_perms.get("default_workflow_permissions")
                if live_perm and live_perm != wf_perms_desired:
                    errors.append(
                        f"actions.default_workflow_permissions: "
                        f"live={live_perm}, desired={wf_perms_desired}"
                    )

    # Report known drift entries from SSOT
    known_drift = ssot.get("known_drift", [])
    for drift in known_drift:
        severity = drift.get("severity", "medium")
        errors.append(
            f"KNOWN DRIFT [{severity.upper()}]: {drift['field']} "
            f"(current={drift.get('current_value', '?')}, "
            f"desired={drift.get('desired_value', '?')}) "
            f"-- {drift.get('action', 'no action specified')}"
        )

    return errors


# =============================================================================
# Branch Protection Drift Check (live API)
# =============================================================================

def check_branch_protection_drift(token: str) -> list:
    """Compare branch-protection.yaml against live GitHub API."""
    ssot = _load_yaml(BRANCH_PROTECTION_FILE)
    branches = ssot.get("branches", {})
    main_config = branches.get("main", {})
    errors = []

    # Fetch live branch protection
    live = _github_api(f"/repos/{ORG}/{REPO}/branches/main/protection", token)

    if live.get("_not_found"):
        errors.append(
            "branches.main: NO branch protection configured (404). "
            "Enable branch protection in repo Settings > Branches."
        )
        return errors

    if "_error" in live:
        return [f"Cannot fetch branch protection: API returned {live.get('_code', '?')}"]

    # Check pull request reviews
    pr_reviews = live.get("required_pull_request_reviews")
    if main_config.get("require_pull_request", {}).get("desired") is True:
        if pr_reviews is None:
            errors.append("branches.main.require_pull_request: desired=true but not configured")
        else:
            if main_config.get("dismiss_stale_reviews", {}).get("desired") is True:
                if not pr_reviews.get("dismiss_stale_reviews"):
                    errors.append(
                        "branches.main.dismiss_stale_reviews: desired=true, live=false"
                    )
            if main_config.get("require_code_owner_reviews", {}).get("desired") is True:
                if not pr_reviews.get("require_code_owner_reviews"):
                    errors.append(
                        "branches.main.require_code_owner_reviews: desired=true, live=false"
                    )
            review_count = main_config.get("require_pull_request", {}).get(
                "required_approving_review_count", 1
            )
            live_count = pr_reviews.get("required_approving_review_count", 0)
            if live_count < review_count:
                errors.append(
                    f"branches.main.required_approving_review_count: "
                    f"live={live_count}, desired>={review_count}"
                )

    # Check status checks
    status_checks = live.get("required_status_checks")
    if main_config.get("require_status_checks", {}).get("desired") is True:
        if status_checks is None:
            errors.append(
                "branches.main.require_status_checks: desired=true but not configured"
            )
        else:
            desired_strict = main_config.get("require_status_checks", {}).get("strict", True)
            if status_checks.get("strict") != desired_strict:
                errors.append(
                    f"branches.main.require_status_checks.strict: "
                    f"live={status_checks.get('strict')}, desired={desired_strict}"
                )

            desired_checks = set(
                main_config.get("require_status_checks", {}).get("required_checks", [])
            )
            live_contexts = set()
            for check in status_checks.get("checks", []):
                live_contexts.add(check.get("context", ""))
            # Also check legacy contexts field
            for ctx in status_checks.get("contexts", []):
                live_contexts.add(ctx)

            missing = desired_checks - live_contexts
            if missing:
                errors.append(
                    f"branches.main.required_checks: missing from live: {sorted(missing)}"
                )

    # Check force push restriction
    allow_force = live.get("allow_force_pushes", {})
    if main_config.get("restrict_force_push", {}).get("desired") is True:
        if allow_force.get("enabled", False):
            errors.append(
                "branches.main.restrict_force_push: desired=true but force push is ALLOWED"
            )

    # Check deletion restriction
    allow_delete = live.get("allow_deletions", {})
    if main_config.get("restrict_deletions", {}).get("desired") is True:
        if allow_delete.get("enabled", False):
            errors.append(
                "branches.main.restrict_deletions: desired=true but deletion is ALLOWED"
            )

    # Check linear history
    linear = live.get("required_linear_history", {})
    if main_config.get("require_linear_history", {}).get("desired") is True:
        if not linear.get("enabled", False):
            errors.append(
                "branches.main.require_linear_history: desired=true, live=false"
            )

    # Report known drift entries from SSOT
    known_drift = ssot.get("known_drift", [])
    for drift in known_drift:
        severity = drift.get("severity", "medium")
        errors.append(
            f"KNOWN DRIFT [{severity.upper()}]: {drift['field']} "
            f"(current={drift.get('current_value', '?')}, "
            f"desired={drift.get('desired_value', '?')}) "
            f"-- {drift.get('action', 'no action specified')}"
        )

    return errors


# =============================================================================
# Rulesets Drift Check
# =============================================================================

def check_rulesets_drift(token: str) -> list:
    """Check for org-level and repo-level rulesets."""
    errors = []

    # Check repo rulesets
    repo_rulesets = _github_api(f"/repos/{ORG}/{REPO}/rulesets", token)
    if isinstance(repo_rulesets, list):
        ruleset_names = [r.get("name", "") for r in repo_rulesets]
        print(f"  Repo rulesets found: {ruleset_names or '(none)'}")
    elif repo_rulesets.get("_not_found"):
        print("  Repo rulesets: none configured")

    # Check org rulesets
    org_rulesets = _github_api(f"/orgs/{ORG}/rulesets", token)
    if isinstance(org_rulesets, list):
        ruleset_names = [r.get("name", "") for r in org_rulesets]
        print(f"  Org rulesets found: {ruleset_names or '(none)'}")
    elif org_rulesets.get("_not_found"):
        print("  Org rulesets: none configured")

    return errors


# =============================================================================
# Main
# =============================================================================

def main():
    import argparse
    parser = argparse.ArgumentParser(description="GitHub Org Policy SSOT drift checker")
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Validate YAML structure only (no API calls)",
    )
    parser.add_argument(
        "--scope",
        choices=["org", "branch", "all"],
        default="all",
        help="Which scope to check (default: all)",
    )
    args = parser.parse_args()

    all_errors = []

    # --- Phase 1: Structure Validation (always runs) ---
    print("=== Validating SSOT structure ===")

    if args.scope in ("org", "all"):
        errors = validate_org_policy_structure()
        if errors:
            for e in errors:
                print(f"  ERROR: {e}")
            all_errors.extend(errors)
        else:
            print("  OK: org-policy.yaml structure valid")

    if args.scope in ("branch", "all"):
        errors = validate_branch_protection_structure()
        if errors:
            for e in errors:
                print(f"  ERROR: {e}")
            all_errors.extend(errors)
        else:
            print("  OK: branch-protection.yaml structure valid")

    if args.validate_only:
        print(f"\n{'=' * 50}")
        if all_errors:
            print(f"FAIL: {len(all_errors)} validation error(s)")
            sys.exit(1)
        else:
            print("PASS: All SSOT structure validation passed")
        return

    # --- Phase 2: Live API Drift Check ---
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        print(
            "\nSKIP: Live drift check (GITHUB_TOKEN not set). "
            "Set GITHUB_TOKEN with admin:org scope to enable.",
            file=sys.stderr,
        )
        if all_errors:
            sys.exit(1)
        return

    if args.scope in ("org", "all"):
        print("\n=== Checking org policy drift ===")
        errors = check_org_policy_drift(token)
        if errors:
            for e in errors:
                print(f"  DRIFT: {e}")
            all_errors.extend(errors)
        else:
            print("  OK: Org policy matches SSOT")

    if args.scope in ("branch", "all"):
        print("\n=== Checking branch protection drift ===")
        errors = check_branch_protection_drift(token)
        if errors:
            for e in errors:
                print(f"  DRIFT: {e}")
            all_errors.extend(errors)
        else:
            print("  OK: Branch protection matches SSOT")

        print("\n=== Checking rulesets ===")
        errors = check_rulesets_drift(token)
        all_errors.extend(errors)

    # --- Summary ---
    print(f"\n{'=' * 50}")
    if all_errors:
        # Separate known drift from actual failures for reporting
        known = [e for e in all_errors if "KNOWN DRIFT" in e]
        actual = [e for e in all_errors if "KNOWN DRIFT" not in e]

        if actual:
            print(f"FAIL: {len(actual)} drift(s) detected + {len(known)} known drift(s)")
        elif known:
            print(
                f"WARN: {len(known)} known drift(s) documented in SSOT. "
                "Resolve via GitHub Settings UI."
            )
        sys.exit(1)
    else:
        print("PASS: All GitHub org policy SSOT checks passed")


if __name__ == "__main__":
    main()
