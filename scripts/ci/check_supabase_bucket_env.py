#!/usr/bin/env python3
"""
check_supabase_bucket_env.py — Supabase bucket prefix guard

Prevents staging code from writing to production buckets and vice versa.

Rules:
  staging    → bucket names MUST start with "staging-"
  production → bucket names MUST start with "prod-"
  preview    → any prefix allowed (ephemeral, non-critical)

Reads from environment variables:
  DEPLOY_ENV              — "staging" | "production" | "preview"
  SUPABASE_STORAGE_BUCKET — the bucket name used by this deployment
                            (may be a comma-separated list for multi-bucket apps)

Exit codes:
  0 — bucket prefix is correct for the environment (or env is "preview")
  1 — bucket prefix mismatch (cross-env write blocked)
  2 — required env var missing or unparseable
"""

import os
import sys

ENV_BUCKET_PREFIXES = {
    "staging":    "staging-",
    "production": "prod-",
}

PREVIEW_ENVS = {"preview", "development", "dev"}


def main() -> int:
    deploy_env = os.environ.get("DEPLOY_ENV", "").strip().lower()
    bucket_raw  = os.environ.get("SUPABASE_STORAGE_BUCKET", "").strip()

    if not deploy_env:
        print("ERROR: DEPLOY_ENV is not set", file=sys.stderr)
        return 2

    # Preview / dev environments: no constraint
    if deploy_env in PREVIEW_ENVS:
        print(f"  SKIP  env={deploy_env!r} — bucket prefix constraint not enforced for preview/dev")
        return 0

    if deploy_env not in ENV_BUCKET_PREFIXES:
        print(f"ERROR: Unknown DEPLOY_ENV={deploy_env!r}  (expected: staging | production | preview)",
              file=sys.stderr)
        return 2

    if not bucket_raw:
        print("ERROR: SUPABASE_STORAGE_BUCKET is not set", file=sys.stderr)
        return 2

    required_prefix = ENV_BUCKET_PREFIXES[deploy_env]
    buckets = [b.strip() for b in bucket_raw.split(",") if b.strip()]
    violations = [b for b in buckets if not b.startswith(required_prefix)]

    if violations:
        print("BUCKET PREFIX VIOLATION — cross-environment write blocked", file=sys.stderr)
        print(f"  env={deploy_env!r}  required prefix={required_prefix!r}", file=sys.stderr)
        for b in violations:
            print(f"  BLOCKED  {b!r}  (does not start with {required_prefix!r})", file=sys.stderr)
        print(file=sys.stderr)
        print(f"  fix  Rename bucket to start with {required_prefix!r}  OR", file=sys.stderr)
        print(f"       Set SUPABASE_STORAGE_BUCKET to a {required_prefix}* bucket name", file=sys.stderr)
        return 1

    for b in buckets:
        print(f"  OK  {deploy_env}  {b!r}  (prefix={required_prefix!r})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
