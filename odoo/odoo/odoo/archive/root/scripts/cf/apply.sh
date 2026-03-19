#!/usr/bin/env bash
set -euo pipefail

env_dir="${1:-infra/cloudflare/envs/prod}"
cd "$(git rev-parse --show-toplevel)/${env_dir}"

: "${TF_VAR_cloudflare_api_token:?Set TF_VAR_cloudflare_api_token}"

terraform init -upgrade
terraform apply -auto-approve tfplan || terraform apply -auto-approve
