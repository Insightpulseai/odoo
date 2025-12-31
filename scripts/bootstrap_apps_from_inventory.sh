#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "${ROOT}"

LATEST="inventory/latest/apps.list.json"
[[ -f "${LATEST}" ]] || { echo "missing ${LATEST} (run export_state.sh first)"; exit 1; }

mkdir -p apps

slugify() {
  echo "$1" \
    | tr '[:upper:]' '[:lower:]' \
    | sed -E 's/[^a-z0-9]+/-/g' \
    | sed -E 's/^-+|-+$//g' \
    | cut -c1-64
}

jq -c '.[]' "${LATEST}" | while read -r row; do
  id="$(echo "${row}" | jq -r '.id')"

  # best-effort name extraction
  name="$(echo "${row}" | jq -r '.spec.name // .name // empty')"
  [[ -n "${name}" && "${name}" != "null" ]] || name="do-app-${id}"

  slug="$(slugify "${name}")"
  dir="apps/${slug}"

  mkdir -p "${dir}/do"

  # raw + resolved
  cp "inventory/latest/apps.${id}.json" "${dir}/do/app.json"

  cat > "${dir}/APP.md" <<MD
# ${name}

- do_app_id: ${id}
- slug: ${slug}

## Links
- public ingress (if any): $(jq -r '.default_ingress // empty' "${dir}/do/app.json" | sed 's/^$/n\/a/')

## Notes
- Source of truth: apps/<slug>/do/app.json
MD

  cat > "${dir}/spec.yaml" <<YAML
# fin-workspace app spec (normalized)
name: ${name}
slug: ${slug}
do:
  app_id: ${id}
  region: $(jq -r '.spec.region.slug // empty' "${dir}/do/app.json" | sed 's/^$/unknown/')
  ingress: $(jq -r '.default_ingress // empty' "${dir}/do/app.json" | sed 's/^$/n\/a/')
owners:
  - platform: fin-workspace
env: prod
YAML

  echo "✓ ${dir}"
done

echo "✅ bootstrapped apps/* from inventory/latest"
