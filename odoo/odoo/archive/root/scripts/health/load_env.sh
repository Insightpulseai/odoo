#!/usr/bin/env bash
set -euo pipefail

ENV_FILE="${1:-.env.platform.local}"
if [[ ! -f "$ENV_FILE" ]]; then
  echo "Missing env file: $ENV_FILE" >&2
  exit 1
fi

# Export KEY=VALUE lines; ignore comments/blank; strip optional leading "export "
set -a
# shellcheck disable=SC1090
source <(grep -vE '^\s*#|^\s*$' "$ENV_FILE" | sed -E 's/^\s*export\s+//')
set +a
