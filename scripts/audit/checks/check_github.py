#!/usr/bin/env python3
"""
GitHub Integration Audit Check

Validates:
- Token authentication
- Rate limit status
- Workflow access
- Recent runs
- Repository permissions
"""
import json
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib import HTTPClient, CheckResult, IntegrationResult, check_env_vars, redact_dict


def main():
    output_file = sys.argv[1] if len(sys.argv) > 1 else "github_audit.json"

    # Check environment variables (GITHUB_TOKEN is usually set by GitHub Actions)
    env_check = check_env_vars(
        required=["GITHUB_TOKEN"],
        optional=["GH_TOKEN", "GITHUB_REPOSITORY"]
    )

    # Also check GH_TOKEN as fallback
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")

    result = IntegrationResult(
        name="GitHub",
        status="SKIP",
        risk_tier="critical",
        checks=[],
        recommendations=[]
    )

    if not token:
        result.status = "SKIP"
        result.recommendations.append("Set GITHUB_TOKEN or GH_TOKEN for GitHub audit")
        result.evidence = {"missing_required": ["GITHUB_TOKEN"]}
        save_result(result, output_file)
        return

    client = HTTPClient(timeout=30)
    repo = os.environ.get("GITHUB_REPOSITORY", "jgtolentino/odoo-ce")

    checks = []
    latencies = []
    user_info = {}

    # Check 1: Auth test
    check, user_info = run_auth_check(client, token)
    checks.append(check)
    if check.latency_ms:
        latencies.append(check.latency_ms)

    # Check 2: Rate limit
    check = run_rate_limit_check(client, token)
    checks.append(check)
    if check.latency_ms:
        latencies.append(check.latency_ms)

    # Check 3: List workflows
    check = run_workflows_check(client, token, repo)
    checks.append(check)
    if check.latency_ms:
        latencies.append(check.latency_ms)

    # Check 4: Recent runs
    check = run_recent_runs_check(client, token, repo)
    checks.append(check)
    if check.latency_ms:
        latencies.append(check.latency_ms)

    # Check 5: Repo permissions
    check = run_repo_permissions_check(client, token, repo)
    checks.append(check)
    if check.latency_ms:
        latencies.append(check.latency_ms)

    # Calculate result
    result.checks = checks
    result.pass_count = sum(1 for c in checks if c.status == "PASS")
    result.error_count = sum(1 for c in checks if c.status == "FAIL")
    result.latency_avg_ms = round(sum(latencies) / len(latencies), 2) if latencies else None

    if result.error_count == 0:
        result.status = "PASS"
        result.access_level = "ok"
    elif result.pass_count > 0:
        result.status = "PARTIAL"
        result.access_level = "insufficient"
    else:
        result.status = "FAIL"
        result.access_level = "insufficient"

    result.evidence = {
        "repository": repo,
        "user": user_info.get("login"),
        "token_type": "fine_grained" if user_info.get("login") else "classic"
    }

    save_result(result, output_file)


def run_auth_check(client, token):
    """Validate token authentication."""
    check = CheckResult(
        name="auth_test",
        integration="github",
        description="Validate token authentication",
        status="FAIL"
    )
    user_info = {}

    try:
        headers = {"Authorization": f"Bearer {token}"}
        resp = client.request("GET", "https://api.github.com/user", headers=headers)
        check.http_status = resp["status_code"]
        check.latency_ms = resp["latency_ms"]
        check.rate_limit = resp.get("rate_limit")

        if resp["status_code"] == 200:
            check.status = "PASS"
            body = resp.get("body", {})
            user_info = {"login": body.get("login"), "id": body.get("id")}
            check.evidence = {
                "user_login": body.get("login"),
                "user_type": body.get("type")
            }

            # Check scopes from headers
            scopes = resp.get("headers", {}).get("X-OAuth-Scopes", "")
            if scopes:
                check.evidence["scopes"] = scopes.split(", ")
        elif resp["status_code"] == 401:
            check.error = "Token authentication failed"
        else:
            check.error = f"Unexpected status: {resp['status_code']}"

    except Exception as e:
        check.error = str(e)

    return check, user_info


def run_rate_limit_check(client, token):
    """Check rate limit status."""
    check = CheckResult(
        name="rate_limit",
        integration="github",
        description="Check rate limit status",
        status="FAIL"
    )

    try:
        headers = {"Authorization": f"Bearer {token}"}
        resp = client.request("GET", "https://api.github.com/rate_limit", headers=headers)
        check.http_status = resp["status_code"]
        check.latency_ms = resp["latency_ms"]

        if resp["status_code"] == 200:
            check.status = "PASS"
            body = resp.get("body", {})
            core = body.get("resources", {}).get("core", {})
            check.evidence = {
                "limit": core.get("limit"),
                "remaining": core.get("remaining"),
                "reset": core.get("reset"),
                "used": core.get("used")
            }
            check.rate_limit = {
                "remaining": core.get("remaining"),
                "limit": core.get("limit")
            }
        else:
            check.error = f"Rate limit check failed: {resp['status_code']}"

    except Exception as e:
        check.error = str(e)

    return check


def run_workflows_check(client, token, repo):
    """List repository workflows."""
    check = CheckResult(
        name="list_workflows",
        integration="github",
        description="List repository workflows",
        status="FAIL"
    )

    try:
        headers = {"Authorization": f"Bearer {token}"}
        resp = client.request(
            "GET",
            f"https://api.github.com/repos/{repo}/actions/workflows",
            headers=headers
        )
        check.http_status = resp["status_code"]
        check.latency_ms = resp["latency_ms"]

        if resp["status_code"] == 200:
            check.status = "PASS"
            body = resp.get("body", {})
            workflows = body.get("workflows", [])
            check.evidence = {
                "workflow_count": body.get("total_count", len(workflows)),
                "workflow_names": [w.get("name") for w in workflows[:10]]
            }
        elif resp["status_code"] == 404:
            check.error = f"Repository {repo} not found or not accessible"
        else:
            check.error = f"Workflows check failed: {resp['status_code']}"

    except Exception as e:
        check.error = str(e)

    return check


def run_recent_runs_check(client, token, repo):
    """List recent workflow runs."""
    check = CheckResult(
        name="recent_runs",
        integration="github",
        description="List recent workflow runs",
        status="FAIL"
    )

    try:
        headers = {"Authorization": f"Bearer {token}"}
        resp = client.request(
            "GET",
            f"https://api.github.com/repos/{repo}/actions/runs?per_page=5",
            headers=headers
        )
        check.http_status = resp["status_code"]
        check.latency_ms = resp["latency_ms"]

        if resp["status_code"] == 200:
            check.status = "PASS"
            body = resp.get("body", {})
            runs = body.get("workflow_runs", [])
            check.evidence = {
                "total_runs": body.get("total_count"),
                "recent_runs": [
                    {
                        "name": r.get("name"),
                        "status": r.get("status"),
                        "conclusion": r.get("conclusion")
                    }
                    for r in runs[:5]
                ]
            }
        else:
            check.error = f"Runs check failed: {resp['status_code']}"

    except Exception as e:
        check.error = str(e)

    return check


def run_repo_permissions_check(client, token, repo):
    """Check repository permissions."""
    check = CheckResult(
        name="repo_permissions",
        integration="github",
        description="Check repository access permissions",
        status="FAIL"
    )

    try:
        headers = {"Authorization": f"Bearer {token}"}
        resp = client.request(
            "GET",
            f"https://api.github.com/repos/{repo}",
            headers=headers
        )
        check.http_status = resp["status_code"]
        check.latency_ms = resp["latency_ms"]

        if resp["status_code"] == 200:
            check.status = "PASS"
            body = resp.get("body", {})
            permissions = body.get("permissions", {})
            check.evidence = {
                "repo_name": body.get("full_name"),
                "private": body.get("private"),
                "permissions": permissions,
                "default_branch": body.get("default_branch")
            }
        elif resp["status_code"] == 404:
            check.error = f"Repository {repo} not accessible"
        else:
            check.error = f"Repo check failed: {resp['status_code']}"

    except Exception as e:
        check.error = str(e)

    return check


def save_result(result, output_file):
    """Save result to file."""
    data = result.to_dict()
    data = redact_dict(data)

    os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else ".", exist_ok=True)
    with open(output_file, "w") as f:
        json.dump(data, f, indent=2, default=str)

    print(f"GitHub audit: {result.status} ({result.pass_count} passed, {result.error_count} failed)")


if __name__ == "__main__":
    main()
