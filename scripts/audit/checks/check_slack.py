#!/usr/bin/env python3
"""
Slack Integration Audit Check

Validates:
- Bot token authentication
- Channel access
- Bot info
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib import HTTPClient, CheckResult, IntegrationResult, check_env_vars, redact_dict


def main():
    output_file = sys.argv[1] if len(sys.argv) > 1 else "slack_audit.json"

    env_check = check_env_vars(
        required=["SLACK_BOT_TOKEN"],
        optional=["SLACK_TEST_CHANNEL", "SLACK_SIGNING_SECRET"]
    )

    result = IntegrationResult(
        name="Slack",
        status="SKIP",
        risk_tier="medium",
        checks=[],
        recommendations=[]
    )

    if env_check["missing_required"]:
        result.status = "SKIP"
        result.recommendations.append(f"Set required env vars: {', '.join(env_check['missing_required'])}")
        result.evidence = {"missing_required": env_check["missing_required"]}
        save_result(result, output_file)
        return

    client = HTTPClient(timeout=30)
    token = os.environ["SLACK_BOT_TOKEN"]

    checks = []
    latencies = []
    team_info = {}

    # Check 1: Auth test
    check, team_info = run_auth_check(client, token)
    checks.append(check)
    if check.latency_ms:
        latencies.append(check.latency_ms)

    # Check 2: List conversations
    check = run_conversations_check(client, token)
    checks.append(check)
    if check.latency_ms:
        latencies.append(check.latency_ms)

    # Check 3: Bot info
    check = run_bot_info_check(client, token)
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
        "team_id": team_info.get("team_id"),
        "team_name": team_info.get("team")
    }

    save_result(result, output_file)


def run_auth_check(client, token):
    """Validate bot token."""
    check = CheckResult(
        name="auth_test",
        integration="slack",
        description="Validate bot token",
        status="FAIL"
    )
    team_info = {}

    try:
        headers = {"Authorization": f"Bearer {token}"}
        resp = client.request("POST", "https://slack.com/api/auth.test", headers=headers)
        check.http_status = resp["status_code"]
        check.latency_ms = resp["latency_ms"]

        if resp["status_code"] == 200:
            body = resp.get("body", {})
            if body.get("ok"):
                check.status = "PASS"
                team_info = {
                    "team_id": body.get("team_id"),
                    "team": body.get("team"),
                    "user_id": body.get("user_id")
                }
                check.evidence = {
                    "team_id": body.get("team_id"),
                    "team": body.get("team"),
                    "user": body.get("user"),
                    "bot_id": body.get("bot_id")
                }
            else:
                check.error = f"Auth failed: {body.get('error', 'unknown')}"
        else:
            check.error = f"Auth request failed: {resp['status_code']}"

    except Exception as e:
        check.error = str(e)

    return check, team_info


def run_conversations_check(client, token):
    """List accessible channels."""
    check = CheckResult(
        name="list_conversations",
        integration="slack",
        description="List accessible channels",
        status="FAIL"
    )

    try:
        headers = {"Authorization": f"Bearer {token}"}
        resp = client.request(
            "GET",
            "https://slack.com/api/conversations.list?types=public_channel&limit=10",
            headers=headers
        )
        check.http_status = resp["status_code"]
        check.latency_ms = resp["latency_ms"]

        if resp["status_code"] == 200:
            body = resp.get("body", {})
            if body.get("ok"):
                check.status = "PASS"
                channels = body.get("channels", [])
                check.evidence = {
                    "channel_count": len(channels),
                    "channel_names": [c.get("name") for c in channels[:10]]
                }
            else:
                error = body.get("error", "unknown")
                if error == "missing_scope":
                    check.status = "PARTIAL"
                    check.error = "Missing scope: channels:read"
                    check.recommendations = ["Add channels:read scope to bot"]
                else:
                    check.error = f"Conversations list failed: {error}"
        else:
            check.error = f"Request failed: {resp['status_code']}"

    except Exception as e:
        check.error = str(e)

    return check


def run_bot_info_check(client, token):
    """Get bot information."""
    check = CheckResult(
        name="bot_info",
        integration="slack",
        description="Get bot information",
        status="FAIL"
    )

    try:
        headers = {"Authorization": f"Bearer {token}"}
        # First get the bot user ID from auth.test
        auth_resp = client.request("POST", "https://slack.com/api/auth.test", headers=headers)

        if auth_resp["status_code"] == 200 and auth_resp.get("body", {}).get("ok"):
            bot_id = auth_resp["body"].get("bot_id")
            if bot_id:
                resp = client.request(
                    "GET",
                    f"https://slack.com/api/bots.info?bot={bot_id}",
                    headers=headers
                )
                check.http_status = resp["status_code"]
                check.latency_ms = resp["latency_ms"]

                if resp["status_code"] == 200:
                    body = resp.get("body", {})
                    if body.get("ok"):
                        check.status = "PASS"
                        bot = body.get("bot", {})
                        check.evidence = {
                            "bot_id": bot.get("id"),
                            "bot_name": bot.get("name"),
                            "app_id": bot.get("app_id")
                        }
                    else:
                        check.error = f"Bot info failed: {body.get('error', 'unknown')}"
                else:
                    check.error = f"Request failed: {resp['status_code']}"
            else:
                check.status = "PASS"
                check.evidence = {"note": "User token (not bot token)"}
        else:
            check.error = "Could not get bot ID from auth.test"

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

    print(f"Slack audit: {result.status} ({result.pass_count} passed, {result.error_count} failed)")


if __name__ == "__main__":
    main()
