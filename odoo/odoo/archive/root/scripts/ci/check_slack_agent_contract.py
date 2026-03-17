#!/usr/bin/env python3
"""
scripts/ci/check_slack_agent_contract.py

Static contract validator for apps/slack-agent.

Checks (no network, no runtime):
  1. Required route files exist (events, interactive, commands)
  2. Signature verification is present in every route
  3. ACK-fast pattern: ACK 200 must precede enqueue (no blocking work first)
  4. Idempotency: slackEventKey / slackInteractionKey / slackCommandKey present
  5. Install state SSOT exists and contains required fields
  6. Integration appears in _index.yaml

Exit 0 = all checks pass
Exit 1 = one or more checks failed (details printed to stderr)
"""

import sys
import os
import re
import yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ROUTES = ROOT / "apps/slack-agent/server/routes/api/slack"
SSOT_INDEX = ROOT / "ssot/integrations/_index.yaml"
INSTALL_YAML = ROOT / "ssot/integrations/slack_agent.install.yaml"

ERRORS: list[str] = []


def fail(msg: str) -> None:
    ERRORS.append(msg)
    print(f"  FAIL: {msg}", file=sys.stderr)


def ok(msg: str) -> None:
    print(f"  ok:   {msg}")


# ── 1. Required route files ──────────────────────────────────────────────────

def check_routes_exist() -> None:
    print("\n[1] Route files")
    required = ["events.post.ts", "interactive.post.ts", "commands.post.ts"]
    for fname in required:
        path = ROUTES / fname
        if path.exists():
            ok(f"{fname} exists")
        else:
            fail(f"Missing route file: apps/slack-agent/server/routes/api/slack/{fname}")


# ── 2. Signature verification present in every route ─────────────────────────

def check_signature_verification() -> None:
    print("\n[2] Signature verification")
    for ts_file in ROUTES.glob("*.post.ts"):
        src = ts_file.read_text()
        if "verifySlackSignature" in src:
            ok(f"{ts_file.name}: verifySlackSignature present")
        else:
            fail(
                f"{ts_file.name}: verifySlackSignature NOT found — "
                "all Slack endpoints MUST verify signatures before processing"
            )


# ── 3. ACK-fast pattern ───────────────────────────────────────────────────────
# Rule: setResponseStatus(event, 200) and send() must appear BEFORE
#       enqueueSlackRun() in each file.
# We verify relative line positions; if send() line > enqueue line → fail.

def check_ack_fast() -> None:
    print("\n[3] ACK-fast pattern (send() before enqueue)")
    for ts_file in ROUTES.glob("*.post.ts"):
        src = ts_file.read_text()
        lines = src.splitlines()

        ack_line = None
        enqueue_line = None
        for i, line in enumerate(lines, 1):
            if re.search(r"\bsend\s*\(", line) and ack_line is None:
                ack_line = i
            if re.search(r"\benqueueSlackRun\s*\(", line) and enqueue_line is None:
                enqueue_line = i

        if ack_line is None:
            fail(f"{ts_file.name}: send() call not found — endpoint must ACK immediately")
        elif enqueue_line is None:
            # No enqueue at all is fine for error-path-only routes
            ok(f"{ts_file.name}: no enqueue found (may be error-path-only) — skipping order check")
        elif ack_line < enqueue_line:
            ok(f"{ts_file.name}: ACK on line {ack_line} precedes enqueue on line {enqueue_line}")
        else:
            fail(
                f"{ts_file.name}: enqueue on line {enqueue_line} precedes ACK on line {ack_line} — "
                "ACK MUST be sent before any async work (Slack 3s timeout)"
            )


# ── 4. Idempotency key usage ──────────────────────────────────────────────────

def check_idempotency() -> None:
    print("\n[4] Idempotency keys")
    patterns = {
        "events.post.ts": "slackEventKey",
        "interactive.post.ts": "slackInteractionKey",
        "commands.post.ts": "slackCommandKey",
    }
    for fname, fn_name in patterns.items():
        path = ROUTES / fname
        if not path.exists():
            continue  # already flagged in check 1
        src = path.read_text()
        if fn_name in src:
            ok(f"{fname}: {fn_name} used")
        else:
            fail(
                f"{fname}: {fn_name} NOT found — "
                "every Slack endpoint MUST build a deterministic idempotency key for ops.runs dedup"
            )


# ── 5. Install state SSOT complete ───────────────────────────────────────────

def check_install_yaml() -> None:
    print("\n[5] Install state SSOT")
    if not INSTALL_YAML.exists():
        fail(f"Missing: {INSTALL_YAML.relative_to(ROOT)}")
        return
    ok(f"{INSTALL_YAML.relative_to(ROOT)} exists")

    try:
        data = yaml.safe_load(INSTALL_YAML.read_text())
    except yaml.YAMLError as exc:
        fail(f"YAML parse error in install YAML: {exc}")
        return

    required_fields = ["endpoints", "required_scopes", "ack_contract", "idempotency_contract", "secrets"]
    for field in required_fields:
        if field in data:
            ok(f"  field present: {field}")
        else:
            fail(f"Install YAML missing required field: {field}")

    # ACK ms must be <= 2500
    ack_ms = data.get("ack_contract", {}).get("ack_within_ms")
    if ack_ms is None:
        fail("Install YAML: ack_contract.ack_within_ms not set")
    elif ack_ms > 2500:
        fail(f"Install YAML: ack_within_ms={ack_ms} exceeds safe 2500ms threshold")
    else:
        ok(f"  ack_within_ms={ack_ms} (≤2500)")


# ── 6. Integration registered in _index.yaml ────────────────────────────────

def check_index_registration() -> None:
    print("\n[6] Integration index registration")
    if not SSOT_INDEX.exists():
        fail(f"Missing: {SSOT_INDEX.relative_to(ROOT)}")
        return
    ok(f"{SSOT_INDEX.relative_to(ROOT)} exists")

    try:
        data = yaml.safe_load(SSOT_INDEX.read_text())
    except yaml.YAMLError as exc:
        fail(f"YAML parse error in _index.yaml: {exc}")
        return

    ids = [entry.get("id") for entry in data.get("integrations", [])]
    if "slack_agent" in ids:
        ok("  slack_agent registered in _index.yaml")
    else:
        fail("slack_agent NOT found in ssot/integrations/_index.yaml — add it")

    # Install state referenced?
    for entry in data.get("integrations", []):
        if entry.get("id") == "slack_agent":
            if "install_state" in entry:
                ok(f"  install_state referenced: {entry['install_state']}")
            else:
                fail("_index.yaml: slack_agent entry missing install_state reference")


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=== Slack Agent Contract Validator ===")
    print(f"Root: {ROOT}")

    check_routes_exist()
    check_signature_verification()
    check_ack_fast()
    check_idempotency()
    check_install_yaml()
    check_index_registration()

    print()
    if ERRORS:
        print(f"RESULT: FAIL ({len(ERRORS)} error(s))", file=sys.stderr)
        sys.exit(1)
    else:
        print("RESULT: PASS — all Slack agent contract invariants satisfied")
        sys.exit(0)
