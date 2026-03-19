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

variable "healthcheck_token" {
  type        = string
  sensitive   = true
  description = "Shared secret for health check WAF bypass (X-Healthcheck-Token header)"
}
