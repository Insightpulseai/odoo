data "cloudflare_zone" "zone" {
  name = var.zone_name
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
    enabled  = false
    selector = "zoho"
    value    = "TODO_FROM_ZOHO_ADMIN"
  }
}
