# =============================================================================
# Cloudflare DNS Records for insightpulseai.com
# =============================================================================
# This module manages DNS records for insightpulseai.com via Cloudflare.
# Records were imported from existing Cloudflare configuration.
#
# Import commands: see scripts/import_existing.sh
# =============================================================================

# -----------------------------------------------------------------------------
# A Records - Web Servers
# -----------------------------------------------------------------------------

resource "cloudflare_record" "root_a" {
  zone_id = var.zone_id
  name    = "@"
  type    = "A"
  content = var.origin_ipv4
  proxied = var.proxied
  ttl     = 1 # Auto when proxied
}

resource "cloudflare_record" "www_a" {
  zone_id = var.zone_id
  name    = "www"
  type    = "A"
  content = var.origin_ipv4
  proxied = var.proxied
  ttl     = 1
}

resource "cloudflare_record" "erp_a" {
  zone_id = var.zone_id
  name    = "erp"
  type    = "A"
  content = var.origin_ipv4
  proxied = var.proxied
  ttl     = 1
}

# -----------------------------------------------------------------------------
# MX Records - Zoho Mail
# -----------------------------------------------------------------------------

resource "cloudflare_record" "mx1" {
  zone_id  = var.zone_id
  name     = "@"
  type     = "MX"
  content  = "mx.zoho.com"
  priority = 10
  ttl      = 3600
}

resource "cloudflare_record" "mx2" {
  zone_id  = var.zone_id
  name     = "@"
  type     = "MX"
  content  = "mx2.zoho.com"
  priority = 20
  ttl      = 3600
}

resource "cloudflare_record" "mx3" {
  zone_id  = var.zone_id
  name     = "@"
  type     = "MX"
  content  = "mx3.zoho.com"
  priority = 50
  ttl      = 3600
}

# -----------------------------------------------------------------------------
# TXT Records - Email Authentication
# -----------------------------------------------------------------------------

resource "cloudflare_record" "spf" {
  zone_id = var.zone_id
  name    = "@"
  type    = "TXT"
  content = "v=spf1 include:zohomail.com ~all"
  ttl     = 3600
}

resource "cloudflare_record" "dmarc" {
  zone_id = var.zone_id
  name    = "_dmarc"
  type    = "TXT"
  content = "v=DMARC1; p=quarantine; rua=mailto:dmarc-reports@insightpulseai.com"
  ttl     = 3600
}

resource "cloudflare_record" "dkim_zoho" {
  zone_id = var.zone_id
  name    = "zoho._domainkey"
  type    = "TXT"
  content = var.zoho_dkim_value
  ttl     = 3600
}
