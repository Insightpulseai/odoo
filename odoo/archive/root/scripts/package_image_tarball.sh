#!/usr/bin/env bash
set -euo pipefail

IMAGE_NAME=${IMAGE_NAME:-ghcr.io/jgtolentino/odoo-ce:latest}
OUTPUT_TARBALL=${OUTPUT_TARBALL:-odoo-ce-latest.tar.gz}

main() {
  echo "[1/3] Building image ${IMAGE_NAME}..."
  docker build -t "${IMAGE_NAME}" .

  echo "[2/3] Saving image to tarball ${OUTPUT_TARBALL}..."
  tmp_tar=$(mktemp odoo-image.XXXXXX.tar)
  trap 'rm -f "$tmp_tar"' EXIT

  docker save "${IMAGE_NAME}" > "$tmp_tar"
  gzip -c "$tmp_tar" > "${OUTPUT_TARBALL}"

  echo "[3/3] Tarball ready: ${OUTPUT_TARBALL}"
  echo "To load on a target host:"
  echo "  scp ${OUTPUT_TARBALL} <user>@<host>:/path/to/odoo-ce/"
  echo "  docker load < ${OUTPUT_TARBALL}"
  echo "  docker compose -f docker-compose.prod.yml up -d odoo"
}

main "$@"
