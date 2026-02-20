#!/usr/bin/env bash
# =============================================================================
# Repository Root Detection Helper
# =============================================================================
# Provides repo_root() function that returns the git repository root path.
# Handles git submodules by walking up to find the true monorepo root.
# Fails with a clear error if not inside a git repository.
#
# Usage:
#   source "${SCRIPT_DIR}/../lib/repo_root.sh"
#   ROOT="$(repo_root)"
# =============================================================================

set -euo pipefail

# Echo the git repo root for the current working dir, or fail with a clear message.
# Handles submodules by looking for sentinel file (config/oca/module_allowlist.yml).
# If not found, walks up the directory tree until it finds the monorepo root.
repo_root() {
  local current_root
  current_root=$(git rev-parse --show-toplevel 2>/dev/null) || {
    echo "ERROR: not inside a git repo. cd to the monorepo root and retry." >&2
    exit 2
  }

  # Check if we're already at monorepo root (has the sentinel file)
  if [[ -f "${current_root}/config/oca/module_allowlist.yml" ]]; then
    echo "${current_root}"
    return 0
  fi

  # Walk up to find monorepo root
  local check_dir="${current_root}/.."
  while [[ -d "${check_dir}" ]]; do
    local potential_root
    potential_root=$(cd "${check_dir}" && git rev-parse --show-toplevel 2>/dev/null) || break

    # Check for sentinel file
    if [[ -f "${potential_root}/config/oca/module_allowlist.yml" ]]; then
      echo "${potential_root}"
      return 0
    fi

    # Move up one level
    check_dir="${potential_root}/.."

    # Prevent infinite loop if we reach root
    if [[ "${potential_root}" == "/" ]] || [[ "${potential_root}" == "${check_dir}" ]]; then
      break
    fi
  done

  # Fallback: return the original git root
  echo "${current_root}"
}
