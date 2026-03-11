#!/usr/bin/env bash
set -euo pipefail

# Supabase Local Development Workflow
# Requires: supabase CLI installed, docker available
# Usage: ./scripts/supabase_local.sh [command]
#
# Commands:
#   start   - Start local Supabase stack
#   reset   - Reset database and apply migrations
#   status  - Show status of local services
#   stop    - Stop local Supabase stack
#   migrate - Apply pending migrations only
#   seed    - Run seed files
#   all     - Full reset + seed (default)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$REPO_ROOT"

command="${1:-all}"

echo "[supabase-local] Running command: $command"

case "$command" in
  start)
    supabase start
    supabase status
    ;;

  reset)
    supabase db reset
    ;;

  status)
    supabase status
    ;;

  stop)
    supabase stop
    ;;

  migrate)
    supabase db push
    ;;

  seed)
    if [ -f supabase/seed.sql ]; then
      supabase db execute -f supabase/seed.sql
    else
      echo "[supabase-local] No seed.sql found, skipping"
    fi
    ;;

  all)
    supabase start || true
    supabase db reset
    supabase status
    ;;

  *)
    echo "Unknown command: $command"
    echo "Usage: $0 [start|reset|status|stop|migrate|seed|all]"
    exit 1
    ;;
esac

echo "[supabase-local] Done"
