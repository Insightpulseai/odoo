variable "cloudflare_account_id" {
  type        = string
  description = "Cloudflare account ID"
}

variable "zone_name" {
  type        = string
  description = "DNS zone name"
}

resource "cloudflare_zone" "this" {
  account_id = var.cloudflare_account_id
  zone       = var.zone_name
}

output "zone_id" {
  value       = cloudflare_zone.this.id
  description = "Cloudflare zone ID"
}

output "zone_name" {
  value       = cloudflare_zone.this.zone
  description = "DNS zone name"
}
