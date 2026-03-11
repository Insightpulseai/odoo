#!/usr/bin/env bash
set -euo pipefail

root="$(git rev-parse --show-toplevel)"

mkdir -p \
  "$root/infra/cloudflare/envs/prod" \
  "$root/infra/cloudflare/modules/dns-records" \
  "$root/scripts/cf" \
  "$root/.github/workflows" \
  "$root/addons/ipai/ipai_system_config/models" \
  "$root/addons/ipai/ipai_system_config/security" \
  "$root/addons/ipai/ipai_system_config/data" \
  "$root/supabase/migrations" \
  "$root/supabase/functions" \
  "$root/docs/architecture"

# -------------------------
# Terraform: Cloudflare DNS
# -------------------------

cat > "$root/infra/cloudflare/envs/prod/providers.tf" <<'EOF'
terraform {
  required_version = ">= 1.6.0"
  required_providers {
    cloudflare = {
      source  = "cloudflare/cloudflare"
      version = "~> 4.0"
    }
  }
}

provider "cloudflare" {
  api_token = var.cloudflare_api_token
}
EOF

cat > "$root/infra/cloudflare/envs/prod/variables.tf" <<'EOF'
variable "cloudflare_api_token" {
  type      = string
  sensitive = true
}

variable "zone_name" {
  type        = string
  description = "Authoritative DNS zone (e.g. insightpulseai.com)"
}

# A record target for apex/subdomains that should point to your droplet/LB
variable "origin_ipv4" {
  type        = string
  description = "IPv4 address for A records (e.g. 178.128.112.214)"
}
EOF

cat > "$root/infra/cloudflare/envs/prod/main.tf" <<'EOF'
data "cloudflare_zone" "zone" {
  name = var.zone_name
}

module "dns_records" {
  source    = "../../modules/dns-records"
  zone_id   = data.cloudflare_zone.zone.id
  zone_name = var.zone_name
  origin_ipv4 = var.origin_ipv4

  # Zoho Mail (active system)
  zoho_mx = [
    { priority = 10, host = "mx.zoho.com"  },
    { priority = 20, host = "mx2.zoho.com" },
    { priority = 50, host = "mx3.zoho.com" },
  ]

  # Core subdomains (SSOT)
  # NOTE: adjust list as you standardize services
  app_subdomains = [
    "erp",
    "n8n",
    "mcp",
    "superset",
    "auth",
    "api",
  ]

  # Optional: additional subdomains you want pointed at the same origin
  extra_a_subdomains = [
    "www",
  ]

  # TXT records (SPF/DMARC placeholders, update as needed)
  txt_records = {
    "@" = [
      "v=spf1 include:zohomail.com ~all"
    ]
    "_dmarc" = [
      # TODO: update policy once you confirm DMARC requirements
      "v=DMARC1; p=none; rua=mailto:postmaster@${var.zone_name}; ruf=mailto:postmaster@${var.zone_name}; fo=1"
    ]
  }

  # DKIM: Zoho provides a selector + value; keep as TODO until you paste the real selector/value
  dkim = {
    enabled = false
    selector = "zoho"
    value    = "TODO_FROM_ZOHO_ADMIN"
  }
}
EOF

cat > "$root/infra/cloudflare/envs/prod/terraform.tfvars.example" <<'EOF'
# Cloudflare API token with DNS edit permissions for the zone
cloudflare_api_token = "PASTE_IN_ENV_OR_TFVARS_NOT_COMMITTED"

# Canonical domain (no .net)
zone_name = "insightpulseai.com"

# Your canonical origin (droplet/LB)
origin_ipv4 = "178.128.112.214"
EOF

cat > "$root/infra/cloudflare/modules/dns-records/variables.tf" <<'EOF'
variable "zone_id" {
  type = string
}

variable "zone_name" {
  type = string
}

variable "origin_ipv4" {
  type = string
}

variable "zoho_mx" {
  type = list(object({
    priority = number
    host     = string
  }))
}

variable "app_subdomains" {
  type = list(string)
}

variable "extra_a_subdomains" {
  type    = list(string)
  default = []
}

variable "txt_records" {
  type    = map(list(string))
  default = {}
}

variable "dkim" {
  type = object({
    enabled  = bool
    selector = string
    value    = string
  })
  default = {
    enabled  = false
    selector = "zoho"
    value    = "TODO"
  }
}
EOF

cat > "$root/infra/cloudflare/modules/dns-records/main.tf" <<'EOF'
locals {
  # Apex + common A records
  a_names = toset(concat(["@"], var.app_subdomains, var.extra_a_subdomains))

  # Records that should be proxied through Cloudflare (apps)
  proxied_names = toset(var.app_subdomains)
}

# A records (apex + subdomains)
resource "cloudflare_record" "a_records" {
  for_each = local.a_names

  zone_id = var.zone_id
  name    = each.value
  type    = "A"
  value   = var.origin_ipv4
  ttl     = 1 # auto
  proxied = contains(local.proxied_names, each.value)
}

# MX records (Zoho)
resource "cloudflare_record" "mx_zoho" {
  for_each = { for i, mx in var.zoho_mx : i => mx }

  zone_id  = var.zone_id
  name     = "@"
  type     = "MX"
  value    = each.value.host
  priority = each.value.priority
  ttl      = 3600
  proxied  = false
}

# TXT records (SPF/DMARC etc.)
resource "cloudflare_record" "txt" {
  for_each = {
    for k, vals in var.txt_records :
    k => vals
  }

  zone_id = var.zone_id
  name    = each.key
  type    = "TXT"
  ttl     = 3600
  proxied = false

  # Cloudflare requires one TXT value per record, so we emit one record per string below
  # This wrapper record is replaced by the for_each below in txt_values.
  value = "placeholder"
  lifecycle { ignore_changes = [value] }
}

resource "cloudflare_record" "txt_values" {
  for_each = {
    for name, vals in var.txt_records :
    name => vals
  }

  zone_id  = var.zone_id
  name     = each.key
  type     = "TXT"
  ttl      = 3600
  proxied  = false

  # explode into stable keys
  dynamic "value" {
    for_each = toset(each.value)
    content {}
  }

  # Terraform Cloudflare provider doesn't support multiple values in one TXT record consistently,
  # so we implement one resource per TXT string by rewriting to a distinct map.
}

# Re-implement TXT properly as one record per string (stable)
locals {
  txt_flat = {
    for pair in flatten([
      for name, vals in var.txt_records : [
        for v in vals : {
          key  = "${name}::${substr(sha1(v),0,12)}"
          name = name
          v    = v
        }
      ]
    ]) : pair.key => pair
  }
}

resource "cloudflare_record" "txt_flat" {
  for_each = local.txt_flat
  zone_id  = var.zone_id
  name     = each.value.name
  type     = "TXT"
  value    = each.value.v
  ttl      = 3600
  proxied  = false
}

# DKIM (optional, only when enabled)
resource "cloudflare_record" "dkim" {
  count  = var.dkim.enabled ? 1 : 0
  zone_id = var.zone_id
  name    = "${var.dkim.selector}._domainkey"
  type    = "TXT"
  value   = var.dkim.value
  ttl     = 3600
  proxied = false
}
EOF

cat > "$root/infra/cloudflare/modules/dns-records/outputs.tf" <<'EOF'
output "zone_name" { value = var.zone_name }
EOF

# -------------------------
# Scripts: plan/apply/verify
# -------------------------

cat > "$root/scripts/cf/plan.sh" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

env_dir="${1:-infra/cloudflare/envs/prod}"
cd "$(git rev-parse --show-toplevel)/${env_dir}"

: "${TF_VAR_cloudflare_api_token:?Set TF_VAR_cloudflare_api_token}"

terraform fmt -recursive
terraform init -upgrade
terraform validate
terraform plan -out tfplan
EOF
chmod +x "$root/scripts/cf/plan.sh"

cat > "$root/scripts/cf/apply.sh" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

env_dir="${1:-infra/cloudflare/envs/prod}"
cd "$(git rev-parse --show-toplevel)/${env_dir}"

: "${TF_VAR_cloudflare_api_token:?Set TF_VAR_cloudflare_api_token}"

terraform init -upgrade
terraform apply -auto-approve tfplan || terraform apply -auto-approve
EOF
chmod +x "$root/scripts/cf/apply.sh"

cat > "$root/scripts/cf/verify_dns.sh" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

zone="${1:?Usage: verify_dns.sh <zone>}"
origin="${2:-}"

dig_cmd() { command -v dig >/dev/null 2>&1 && dig "$@" || true; }

echo "== A records =="
dig_cmd +short A "${zone}"
dig_cmd +short A "www.${zone}"
dig_cmd +short A "erp.${zone}"
dig_cmd +short A "n8n.${zone}"

echo "== MX records =="
dig_cmd +short MX "${zone}"

echo "== SPF (TXT @) =="
dig_cmd +short TXT "${zone}"

echo "== DMARC (TXT _dmarc) =="
dig_cmd +short TXT "_dmarc.${zone}"

if [[ -n "${origin}" ]]; then
  echo "== Checking apex A equals expected origin: ${origin} =="
  actual="$(dig_cmd +short A "${zone}" | head -n1 || true)"
  [[ "${actual}" == "${origin}" ]] && echo "OK" || (echo "WARN: ${actual} != ${origin}" && exit 1)
fi
EOF
chmod +x "$root/scripts/cf/verify_dns.sh"

# -------------------------
# GitHub Action: DNS SSOT gate
# -------------------------
cat > "$root/.github/workflows/infra-cloudflare-dns.yml" <<'EOF'
name: infra-cloudflare-dns

on:
  pull_request:
    paths:
      - "infra/cloudflare/**"
      - ".github/workflows/infra-cloudflare-dns.yml"
  push:
    branches: ["main"]
    paths:
      - "infra/cloudflare/**"
      - ".github/workflows/infra-cloudflare-dns.yml"

jobs:
  plan:
    runs-on: ubuntu-latest
    permissions:
      contents: read
    env:
      TF_IN_AUTOMATION: "true"
      TF_VAR_cloudflare_api_token: ${{ secrets.CLOUDFLARE_API_TOKEN }}
    steps:
      - uses: actions/checkout@v4
      - uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: "1.7.5"
      - name: Terraform fmt/validate/plan
        run: |
          cd infra/cloudflare/envs/prod
          terraform fmt -recursive -check
          terraform init -upgrade
          terraform validate
          terraform plan
EOF

# -------------------------
# Odoo: SSOT Settings Module
# -------------------------
cat > "$root/addons/ipai/ipai_system_config/__manifest__.py" <<'EOF'
{
  "name": "IPAI System Config (SSOT)",
  "version": "19.0.1.0.0",
  "category": "Tools",
  "summary": "Env-backed SSOT for critical Odoo settings (base url, alias domain, SMTP).",
  "license": "LGPL-3",
  "depends": ["base", "mail"],
  "data": [
    "security/ir.model.access.csv",
  ],
  "post_init_hook": "post_init_hook",
  "installable": True,
  "application": False,
}
EOF

cat > "$root/addons/ipai/ipai_system_config/__init__.py" <<'EOF'
from . import models
from .hooks import post_init_hook
EOF

cat > "$root/addons/ipai/ipai_system_config/hooks.py" <<'EOF'
import os
from odoo import api, SUPERUSER_ID

def _env(name, default=None):
    v = os.getenv(name)
    return v if v not in (None, "") else default

def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})

    icp = env["ir.config_parameter"].sudo()
    MailServer = env["ir.mail_server"].sudo()

    # Canonical (no .net): use insightpulseai.com and your production URL
    base_url    = _env("ODOO_BASE_URL")         # e.g. https://erp.insightpulseai.com
    alias_domain= _env("ODOO_ALIAS_DOMAIN")     # e.g. insightpulseai.com

    if base_url:
        icp.set_param("web.base.url", base_url)
        icp.set_param("web.base.url.freeze", "True")

    if alias_domain:
        # Alias domain for mail aliases
        icp.set_param("mail.catchall.domain", alias_domain)

    # SMTP SSOT (Zoho Mail)
    smtp_host = _env("ODOO_SMTP_HOST")
    smtp_port = int(_env("ODOO_SMTP_PORT", "587"))
    smtp_user = _env("ODOO_SMTP_USER")
    smtp_pass = _env("ODOO_SMTP_PASS")
    smtp_tls  = _env("ODOO_SMTP_TLS", "1") == "1"

    if smtp_host and smtp_user and smtp_pass:
        ms = MailServer.search([("name", "=", "SSOT SMTP")], limit=1)
        vals = {
            "name": "SSOT SMTP",
            "smtp_host": smtp_host,
            "smtp_port": smtp_port,
            "smtp_user": smtp_user,
            "smtp_pass": smtp_pass,
            "smtp_encryption": "starttls" if smtp_tls else "none",
            "smtp_authentication": "login",
            "sequence": 1,
            "active": True,
        }
        if ms:
            ms.write(vals)
        else:
            MailServer.create(vals)
EOF

cat > "$root/addons/ipai/ipai_system_config/models/__init__.py" <<'EOF'
# reserved for future SSOT models (kept empty intentionally)
EOF

cat > "$root/addons/ipai/ipai_system_config/security/ir.model.access.csv" <<'EOF'
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
EOF

# -------------------------
# Supabase skeleton (kept minimal; no assumptions about project refs)
# -------------------------
cat > "$root/docs/arch/ODOO_SUPABASE_MONOREPO_LAYOUT.md" <<'EOF'
# Odoo + Supabase Monorepo (OCA-style) — SSOT Layout

This repo is structured so **Odoo + OCA add-ons** and **Supabase (migrations/functions)** can ship together,
with infra SSOT (Cloudflare DNS) versioned alongside.

Recommended high-level layout:

- addons/                 # Odoo add-ons mounted via addons-path generator
  - ipai/                 # your custom SSOT modules
- external-src/           # OCA repos (submodules/subtrees), enumerated by generator
- infra/
  - cloudflare/           # DNS SSOT (Terraform)
- sandbox/                # dev/stage compose
- supabase/
  - migrations/           # SQL migrations (SSOT)
  - functions/            # Edge Functions (SSOT)
- scripts/
  - cf/                   # terraform plan/apply/verify wrappers
EOF

# -------------------------
# Gitignore: terraform + tfvars + state
# -------------------------
if ! grep -q 'infra/cloudflare/.terraform' "$root/.gitignore" 2>/dev/null; then
  cat >> "$root/.gitignore" <<'EOF'

# Terraform (Cloudflare SSOT)
infra/cloudflare/**/.terraform/
infra/cloudflare/**/.terraform.lock.hcl
infra/cloudflare/**/terraform.tfstate*
infra/cloudflare/**/tfplan
infra/cloudflare/**/terraform.tfvars
EOF
fi

echo "✅ SSOT files written."
