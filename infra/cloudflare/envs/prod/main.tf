data "cloudflare_zone" "zone" {
  name = var.zone_name
}

# =============================================================================
# SSOT-driven DNS locals
# =============================================================================
# Reads infra/dns/subdomain-registry.yaml and derives Terraform module inputs.
# Rules:
#   - Only records with lifecycle=active (or no lifecycle field) are provisioned.
#   - Records with status=planned or lifecycle=planned are skipped.
#   - Records with environment=staging are excluded from prod Terraform.
#   - Type A records → split by cloudflare_proxied for app_subdomains / extra_a_subdomains.
#   - Type CNAME records → passed as cname_records map.
# =============================================================================
locals {
  _ssot = yamldecode(file("${path.root}/../../../infra/dns/subdomain-registry.yaml"))

  # Filter: active + non-staging + non-planned
  _prod_active = [
    for r in local._ssot.subdomains :
    r
    if try(r.lifecycle, "active") == "active"
    && try(r.status, "active") != "planned"
    && !contains(keys(r), "environment")
  ]

  # Split by record type
  _prod_a     = [for r in local._prod_active : r if r.type == "A"]
  _prod_cname = [for r in local._prod_active : r if r.type == "CNAME"]

  # Proxied A records (passed as app_subdomains — get origin IP, proxied=true)
  _proxied_a = [for r in local._prod_a : r.name if try(r.cloudflare_proxied, true) == true]

  # Non-proxied A records (passed as extra_a_subdomains — get origin IP, proxied=false)
  _unproxied_a = [for r in local._prod_a : r.name if try(r.cloudflare_proxied, true) == false]

  # CNAME records as map: name → {target, proxied}
  _cname_map = {
    for r in local._prod_cname :
    r.name => {
      target  = r.target
      proxied = try(r.cloudflare_proxied, true)
    }
  }
}

module "dns_records" {
  source      = "../../modules/dns-records"
  zone_id     = data.cloudflare_zone.zone.id
  zone_name   = var.zone_name
  origin_ipv4 = var.origin_ipv4

  # Zoho Mail (active system)
  zoho_mx = [
    { priority = 10, host = "mx.zoho.com" },
    { priority = 20, host = "mx2.zoho.com" },
    { priority = 50, host = "mx3.zoho.com" },
  ]

  # SSOT-derived A records (proxied subdomains → same origin_ipv4)
  app_subdomains = local._proxied_a

  # SSOT-derived A records (non-proxied, e.g. stage-ocr in prod — none currently)
  extra_a_subdomains = local._unproxied_a

  # SSOT-derived CNAME records (App Platform, Vercel services)
  cname_records = local._cname_map

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
    enabled  = false
    selector = "zoho"
    value    = "TODO_FROM_ZOHO_ADMIN"
  }
}

# ─── Health check WAF bypass ─────────────────────────────────────────────────
# Allows CI and monitoring to probe /healthz, /health, /web/health, /api/health
# through Cloudflare WAF when both UA and token match.
module "healthcheck_waf_bypass" {
  source            = "../../modules/healthcheck-waf-bypass"
  zone_id           = data.cloudflare_zone.zone.id
  healthcheck_token = var.healthcheck_token
}
