#!/bin/bash
# =============================================================================
# Shared Environment Loader
# =============================================================================
# Source this file at the start of any script to auto-load credentials.
#
# Usage in scripts:
#   source "$(dirname "$0")/lib/load_env.sh"
#
# Searches for .env files in order:
#   1. .env.local (highest priority, gitignored)
#   2. .env (standard)
#   3. ~/.ipai/.env (user-global config)
# =============================================================================

_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
_REPO_ROOT="$(cd "$_SCRIPT_DIR/../.." && pwd)"

load_env_file() {
    local env_file="$1"
    if [ -f "$env_file" ]; then
        # Export all variables, skip comments and empty lines
        set -a
        # shellcheck disable=SC1090
        source "$env_file"
        set +a
        return 0
    fi
    return 1
}

# Load in priority order (later files override earlier)
_ENV_LOADED=false

# 1. User global config (lowest priority)
if [ -f "$HOME/.ipai/.env" ]; then
    load_env_file "$HOME/.ipai/.env"
    _ENV_LOADED=true
fi

# 2. Repo .env
if [ -f "$_REPO_ROOT/.env" ]; then
    load_env_file "$_REPO_ROOT/.env"
    _ENV_LOADED=true
fi

# 3. Repo .env.local (highest priority, gitignored)
if [ -f "$_REPO_ROOT/.env.local" ]; then
    load_env_file "$_REPO_ROOT/.env.local"
    _ENV_LOADED=true
fi

# Warn if no env file found
if [ "$_ENV_LOADED" = false ]; then
    echo "[WARN] No .env file found. Create one from .env.example:" >&2
    echo "       cp .env.example .env && \$EDITOR .env" >&2
fi

# Verify critical Supabase vars are set
_verify_supabase_env() {
    local missing=()
    [ -z "${SUPABASE_URL:-}" ] && missing+=("SUPABASE_URL")
    [ -z "${SUPABASE_SERVICE_ROLE_KEY:-}" ] && missing+=("SUPABASE_SERVICE_ROLE_KEY")
    [ -z "${POSTGRES_URL:-}" ] && [ -z "${POSTGRES_URL_NON_POOLING:-}" ] && missing+=("POSTGRES_URL")

    if [ ${#missing[@]} -gt 0 ]; then
        echo "[WARN] Missing Supabase credentials: ${missing[*]}" >&2
        echo "       Add them to .env or .env.local" >&2
        return 1
    fi
    return 0
}

# Export helper for scripts that need Supabase
require_supabase_env() {
    if ! _verify_supabase_env; then
        exit 1
    fi
}

# Export DB URL helper (prefer non-pooling for migrations)
get_db_url() {
    if [ -n "${POSTGRES_URL_NON_POOLING:-}" ]; then
        echo "$POSTGRES_URL_NON_POOLING"
    else
        echo "${POSTGRES_URL:-}"
    fi
}

export -f get_db_url
