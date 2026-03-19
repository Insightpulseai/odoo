#!/usr/bin/env python3
"""
check_github_enterprise_ssot.py
================================
CI validator for ssot/github/enterprise-cloud.yaml.

Schema: ssot.github.enterprise.v1
Contract: docs/architecture/GITHUB_ENTERPRISE_CONTRACT.md

Validates structural invariants for GitHub Enterprise Cloud governance (Track A).
Exit 0 = all checks pass.
Exit 1 = one or more checks failed (errors written to stderr).

Usage:
    python scripts/ci/check_github_enterprise_ssot.py
    python scripts/ci/check_github_enterprise_ssot.py --repo-root /path/to/repo

Python: 3.12+ (stdlib + pyyaml only)
"""

import argparse
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print(
        "ERROR: pyyaml is required. Install with: pip install pyyaml",
        file=sys.stderr,
    )
    sys.exit(1)

SSOT_REL_PATH = "ssot/github/enterprise-cloud.yaml"


def _get(data: dict, *keys, default=None):
    """Safe nested key access."""
    node = data
    for key in keys:
        if not isinstance(node, dict) or key not in node:
            return default
        node = node[key]
    return node


def validate(repo_root: Path) -> list[str]:
    """
    Run all invariant checks against the SSOT file.

    Returns a list of error strings. Empty list means all checks passed.
    """
    errors: list[str] = []
    ssot_path = repo_root / SSOT_REL_PATH

    # Check 1: File exists
    if not ssot_path.exists():
        errors.append(
            f"SSOT file not found: {SSOT_REL_PATH}\n"
            "  Expected: ssot/github/enterprise-cloud.yaml\n"
            "  Fix: create the file using the schema ssot.github.enterprise.v1"
        )
        # Cannot continue without the file
        return errors

    # Load YAML
    try:
        raw = ssot_path.read_text(encoding="utf-8")
        data = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        errors.append(f"YAML parse error in {SSOT_REL_PATH}:\n  {exc}")
        return errors

    if not isinstance(data, dict):
        errors.append(
            f"SSOT file {SSOT_REL_PATH} must be a YAML mapping at top level, got {type(data).__name__}"
        )
        return errors

    # Check 2: enterprise.type == "personal_accounts"
    enterprise_type = _get(data, "enterprise", "type")
    if enterprise_type != "personal_accounts":
        errors.append(
            f"enterprise.type must be 'personal_accounts', got: {enterprise_type!r}\n"
            "  File: ssot/github/enterprise-cloud.yaml\n"
            "  Contract: docs/architecture/GITHUB_ENTERPRISE_CONTRACT.md §Track A"
        )

    # Check 3a: policy.sso.enabled == True
    sso_enabled = _get(data, "policy", "sso", "enabled")
    if sso_enabled is not True:
        errors.append(
            f"policy.sso.enabled must be true, got: {sso_enabled!r}\n"
            "  File: ssot/github/enterprise-cloud.yaml\n"
            "  Contract: docs/architecture/GITHUB_ENTERPRISE_CONTRACT.md §SAML SSO"
        )

    # Check 3b: policy.sso.mode == "saml"
    sso_mode = _get(data, "policy", "sso", "mode")
    if sso_mode != "saml":
        errors.append(
            f"policy.sso.mode must be 'saml', got: {sso_mode!r}\n"
            "  File: ssot/github/enterprise-cloud.yaml\n"
            "  Contract: docs/architecture/GITHUB_ENTERPRISE_CONTRACT.md §SAML SSO"
        )

    # Check 4: policy.repo_rulesets.default_branch_protection.require_status_checks == True
    require_status_checks = _get(
        data,
        "policy",
        "repo_rulesets",
        "default_branch_protection",
        "require_status_checks",
    )
    if require_status_checks is not True:
        errors.append(
            f"policy.repo_rulesets.default_branch_protection.require_status_checks must be true, "
            f"got: {require_status_checks!r}\n"
            "  File: ssot/github/enterprise-cloud.yaml\n"
            "  Contract: docs/architecture/GITHUB_ENTERPRISE_CONTRACT.md §Repository Rulesets"
        )

    # Check 5: policy.repo_rulesets.default_branch_protection.require_pull_request == True
    require_pr = _get(
        data,
        "policy",
        "repo_rulesets",
        "default_branch_protection",
        "require_pull_request",
    )
    if require_pr is not True:
        errors.append(
            f"policy.repo_rulesets.default_branch_protection.require_pull_request must be true, "
            f"got: {require_pr!r}\n"
            "  File: ssot/github/enterprise-cloud.yaml\n"
            "  Contract: docs/architecture/GITHUB_ENTERPRISE_CONTRACT.md §Repository Rulesets"
        )

    # Check 6: policy.auth.require_2fa == True
    require_2fa = _get(data, "policy", "auth", "require_2fa")
    if require_2fa is not True:
        errors.append(
            f"policy.auth.require_2fa must be true, got: {require_2fa!r}\n"
            "  File: ssot/github/enterprise-cloud.yaml\n"
            "  Contract: docs/architecture/GITHUB_ENTERPRISE_CONTRACT.md §Two-Factor Authentication"
        )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate GitHub Enterprise Cloud SSOT invariants",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Path to repository root (default: current directory)",
    )
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()

    print(f"Checking {SSOT_REL_PATH} ... ", end="", flush=True)
    errors = validate(repo_root)

    if errors:
        print("FAIL")
        print(
            f"\n{len(errors)} invariant(s) failed for {SSOT_REL_PATH}:\n",
            file=sys.stderr,
        )
        for i, err in enumerate(errors, 1):
            print(f"  [{i}] {err}\n", file=sys.stderr)
        print(
            "Reference: docs/architecture/GITHUB_ENTERPRISE_CONTRACT.md",
            file=sys.stderr,
        )
        return 1

    print("PASS")
    print(f"  All {6} invariants satisfied.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
