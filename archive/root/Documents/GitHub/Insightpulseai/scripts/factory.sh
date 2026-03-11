#!/usr/bin/env bash
set -euo pipefail

cmd="${1:-}"
shift || true

CATALOG="templates/catalog.yaml"

need() { command -v "$1" >/dev/null 2>&1 || { echo "ERROR: missing dependency: $1" >&2; exit 1; }; }

usage() {
  cat <<'TXT'
Usage:
  ./scripts/factory.sh list
  ./scripts/factory.sh new <template-id> <app-name>
  ./scripts/factory.sh build <app-name>
  ./scripts/factory.sh verify

Notes:
- Installs/builds are always scoped to apps/<app-name> (no root workspace bleed).
TXT
}

list_templates() {
  need python3
  python3 - <<'PY'
import sys, yaml, pathlib
p = pathlib.Path("templates/catalog.yaml")
doc = yaml.safe_load(p.read_text())
for t in doc.get("templates", []):
  tid = t.get("id","")
  name = t.get("name","")
  print(f"{tid:<32} {name}")
PY
}

new_app() {
  local tid="${1:-}"
  local app="${2:-}"
  [[ -n "$tid" && -n "$app" ]] || { usage; exit 1; }

  case "$tid" in
    supabase-platform-kit-nextjs)
      ./scripts/new_platform_app.sh "$app"
      ;;
    visactor-nextjs-template|stack-auth-multi-tenant-nextjs)
      ./scripts/new_from_template.sh "$tid" "$app"
      ;;
    *)
      echo "ERROR: unknown template id: $tid" >&2
      echo "Available:"
      list_templates
      exit 1
      ;;
  esac
}

build_app() {
  local app="${1:-}"
  [[ -n "$app" ]] || { usage; exit 1; }
  local dir="apps/$app"
  [[ -d "$dir" ]] || { echo "ERROR: missing $dir" >&2; exit 1; }

  pnpm --dir "$dir" install
  pnpm --dir "$dir" run build
  echo "✅ build ok: $dir"
}

verify_repo() {
  [[ -f pnpm-workspace.yaml ]] || { echo "ERROR: pnpm-workspace.yaml missing" >&2; exit 1; }
  pnpm -w list --depth 0 >/dev/null 2>&1 || true
  ./scripts/ci_guard_platform_kit.sh apps
  ./scripts/ci_guard_template_pins.sh templates/vendor
  echo "✅ factory verify complete"
}

case "$cmd" in
  list)   list_templates ;;
  new)    new_app "${1:-}" "${2:-}" ;;
  build)  build_app "${1:-}" ;;
  verify) verify_repo ;;
  ""|-h|--help) usage ;;
  *) echo "ERROR: unknown command: $cmd" >&2; usage; exit 1 ;;
esac
