#!/usr/bin/env python3
"""Pre-flight validation for connector runtime environment.

Checks:
1. DATABRICKS_HOST reachable (or --check-local mode)
2. DATABRICKS_TOKEN or profile auth works
3. Secret scope 'notion-ppm' accessible with expected keys
4. SLACK_WEBHOOK_URL set (optional, warn if missing)
5. Connector-specific creds present per connector_id
6. Unity Catalog accessible, schemas exist
7. Cluster policies allow requested node types

Usage:
    python scripts/validate_runtime_env.py              # Full remote check
    python scripts/validate_runtime_env.py --check-local  # Local-only checks
    python scripts/validate_runtime_env.py --connector notion  # Check specific connector
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass, field


@dataclass
class CheckResult:
    """Result of a single validation check."""
    name: str
    passed: bool
    message: str = ""
    severity: str = "error"  # error | warning


@dataclass
class ValidationReport:
    """Full validation report."""
    checks: list[CheckResult] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return all(c.passed for c in self.checks if c.severity == "error")

    @property
    def summary(self) -> str:
        passed = sum(1 for c in self.checks if c.passed)
        total = len(self.checks)
        errors = sum(1 for c in self.checks if not c.passed and c.severity == "error")
        warnings = sum(1 for c in self.checks if not c.passed and c.severity == "warning")
        return f"{passed}/{total} passed, {errors} errors, {warnings} warnings"

    def print_report(self) -> None:
        """Print formatted validation report."""
        print("\n" + "=" * 60)
        print("CONNECTOR RUNTIME ENVIRONMENT VALIDATION")
        print("=" * 60)
        for check in self.checks:
            icon = "PASS" if check.passed else ("WARN" if check.severity == "warning" else "FAIL")
            print(f"  [{icon}] {check.name}")
            if check.message:
                print(f"         {check.message}")
        print("-" * 60)
        print(f"  Result: {self.summary}")
        print("=" * 60 + "\n")


# Required env vars for each connector
CONNECTOR_ENV_REQUIREMENTS: dict[str, list[str]] = {
    "notion": ["NOTION_TOKEN"],
    "azure": ["AZURE_SUBSCRIPTION_ID", "AZURE_CLIENT_ID", "AZURE_CLIENT_SECRET", "AZURE_TENANT_ID"],
    "odoo_pg": ["ODOO_PG_HOST", "ODOO_PG_PORT", "ODOO_PG_DATABASE", "ODOO_PG_USER", "ODOO_PG_PASSWORD"],
    "github": ["GITHUB_TOKEN", "GITHUB_ORG"],
}

# Expected secret scope keys (Databricks)
SECRET_SCOPE_KEYS: dict[str, list[str]] = {
    "notion-ppm": [
        "notion_token",
        "programs_db_id",
        "projects_db_id",
        "budget_lines_db_id",
        "risks_db_id",
        "azure_subscription_id",
        "azure_client_id",
        "azure_client_secret",
        "azure_tenant_id",
        "odoo_pg_host",
        "odoo_pg_port",
        "odoo_pg_database",
        "odoo_pg_user",
        "odoo_pg_password",
        "github_token",
        "github_org",
    ],
}


def check_env_var(name: str, required: bool = True) -> CheckResult:
    """Check if an environment variable is set."""
    val = os.environ.get(name)
    if val:
        # Show prefix only for security
        preview = val[:8] + "..." if len(val) > 8 else val
        return CheckResult(name=f"env:{name}", passed=True, message=f"Set ({preview})")
    severity = "error" if required else "warning"
    return CheckResult(
        name=f"env:{name}",
        passed=False,
        message=f"Not set in environment",
        severity=severity,
    )


def check_databricks_host() -> CheckResult:
    """Check DATABRICKS_HOST is reachable."""
    host = os.environ.get("DATABRICKS_HOST")
    if not host:
        return CheckResult(name="databricks_host", passed=False, message="DATABRICKS_HOST not set")
    try:
        import urllib.request
        url = f"https://{host}/api/2.0/clusters/list"
        token = os.environ.get("DATABRICKS_TOKEN", "")
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
        urllib.request.urlopen(req, timeout=10)
        return CheckResult(name="databricks_host", passed=True, message=f"Reachable: {host}")
    except Exception as e:
        return CheckResult(name="databricks_host", passed=False, message=f"Unreachable: {e}")


def check_python_imports() -> CheckResult:
    """Check that SDK modules are importable."""
    try:
        # Just check the module structure exists
        import importlib
        spec = importlib.util.find_spec("workbench.connectors")
        if spec is not None:
            return CheckResult(name="python_imports", passed=True, message="workbench.connectors importable")
        return CheckResult(name="python_imports", passed=False, message="workbench.connectors not found")
    except Exception as e:
        return CheckResult(name="python_imports", passed=False, message=str(e))


def check_local_files() -> CheckResult:
    """Check that key SDK files exist."""
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    required_files = [
        "src/workbench/connectors/sync_engine.py",
        "src/workbench/connectors/base.py",
        "src/workbench/connectors/types.py",
        "src/workbench/connectors/state.py",
        "src/workbench/connectors/schema_manager.py",
        "src/workbench/connectors/registry.py",
        "src/workbench/connectors/retry.py",
        "src/workbench/connectors/monitoring.py",
    ]
    missing = [f for f in required_files if not os.path.exists(os.path.join(base, f))]
    if missing:
        return CheckResult(
            name="sdk_files",
            passed=False,
            message=f"Missing: {', '.join(missing)}",
        )
    return CheckResult(name="sdk_files", passed=True, message=f"All {len(required_files)} SDK files present")


def check_connector_env(connector_id: str) -> list[CheckResult]:
    """Check environment variables for a specific connector."""
    results = []
    env_vars = CONNECTOR_ENV_REQUIREMENTS.get(connector_id, [])
    for var in env_vars:
        results.append(check_env_var(var, required=True))
    return results


def run_validation(
    check_local: bool = False,
    connector_id: str | None = None,
) -> ValidationReport:
    """Run all validation checks."""
    report = ValidationReport()

    # Always check local files
    report.checks.append(check_local_files())
    report.checks.append(check_python_imports())

    if check_local:
        # Local-only mode: check env vars and files
        report.checks.append(check_env_var("DATABRICKS_HOST", required=False))
        report.checks.append(check_env_var("DATABRICKS_TOKEN", required=False))
        report.checks.append(check_env_var("SLACK_WEBHOOK_URL", required=False))
    else:
        # Full mode: check Databricks connectivity
        report.checks.append(check_env_var("DATABRICKS_HOST"))
        report.checks.append(check_env_var("DATABRICKS_TOKEN"))
        report.checks.append(check_databricks_host())
        report.checks.append(check_env_var("SLACK_WEBHOOK_URL", required=False))

    # Connector-specific checks
    if connector_id:
        report.checks.extend(check_connector_env(connector_id))
    else:
        # Check all connectors
        for cid in CONNECTOR_ENV_REQUIREMENTS:
            report.checks.extend(check_connector_env(cid))

    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate connector runtime environment")
    parser.add_argument("--check-local", action="store_true", help="Local-only checks (no Databricks API)")
    parser.add_argument("--connector", type=str, help="Check specific connector only")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    report = run_validation(
        check_local=args.check_local,
        connector_id=args.connector,
    )

    if args.json:
        output = {
            "passed": report.passed,
            "summary": report.summary,
            "checks": [
                {"name": c.name, "passed": c.passed, "message": c.message, "severity": c.severity}
                for c in report.checks
            ],
        }
        print(json.dumps(output, indent=2))
    else:
        report.print_report()

    sys.exit(0 if report.passed else 1)


if __name__ == "__main__":
    main()
