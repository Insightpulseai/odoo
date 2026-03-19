output "zone_id" {
  value       = module.zone.zone_id
  description = "Cloudflare zone ID"
}

output "zone_name" {
  value       = var.zone_name
  description = "DNS zone name"
}

output "app_ipv4" {
  value       = var.app_ipv4
  description = "Application IPv4 address"
}
