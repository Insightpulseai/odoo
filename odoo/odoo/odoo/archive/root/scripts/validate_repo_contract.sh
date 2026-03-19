#!/usr/bin/env bash
set -euo pipefail
fail(){ echo "ERROR: $*" >&2; exit 1; }

test -d runtime || fail "missing runtime/"
test -d addons || fail "missing addons/"
test -d vendor || fail "missing vendor/"
test -f docs/SLUG_POLICY.md || fail "missing docs/SLUG_POLICY.md"
test -f docs/SCHEMA_NAMESPACE_POLICY.md || fail "missing docs/SCHEMA_NAMESPACE_POLICY.md"

bad_addons="$(find addons -mindepth 1 -maxdepth 1 -type d ! -name 'ipai_*' -printf '%f\n' | head -n 50 || true)"
[[ -z "$bad_addons" ]] || { echo "$bad_addons"; fail "addons/ must contain only ipai_*"; }

bad_vendor="$(find vendor -type d -name 'ipai_*' -printf '%p\n' | head -n 50 || true)"
[[ -z "$bad_vendor" ]] || { echo "$bad_vendor"; fail "vendor/ must not contain ipai_*"; }

echo "OK: repo contract valid"
