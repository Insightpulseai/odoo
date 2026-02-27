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

# CNAME records (DO App Platform, Vercel, external services)
# Populated from infra/dns/subdomain-registry.yaml via envs/prod/main.tf locals.
# Only lifecycle=active CNAME records are passed here.
resource "cloudflare_record" "cname_records" {
  for_each = var.cname_records

  zone_id = var.zone_id
  name    = each.key
  type    = "CNAME"
  value   = each.value.target
  ttl     = 1 # auto
  proxied = each.value.proxied
}
