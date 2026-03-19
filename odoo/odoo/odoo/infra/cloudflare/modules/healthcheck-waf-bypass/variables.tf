variable "zone_id" {
  type        = string
  description = "Cloudflare zone ID (from data.cloudflare_zone)"
}

variable "healthcheck_token" {
  type        = string
  sensitive   = true
  description = "Shared secret for X-Healthcheck-Token header. Must match HEALTHCHECK_TOKEN in CI."
}
