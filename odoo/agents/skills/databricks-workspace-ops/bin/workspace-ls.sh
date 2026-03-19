#!/usr/bin/env bash
# databricks-workspace-ops: List workspace objects at a given path
# Usage: workspace-ls.sh <path> [--profile <profile>]
set -euo pipefail

PATH_ARG="${1:?Usage: workspace-ls.sh <path> [--profile <profile>]}"
shift

databricks workspace ls "${PATH_ARG}" --output json "$@"
