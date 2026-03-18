variable "cloudflare_api_token" {
  type        = string
  sensitive   = true
  description = "Cloudflare API token with DNS edit permissions"
}

variable "zone_id" {
  type        = string
  sensitive   = true
  description = "Cloudflare Zone ID for insightpulseai.com"
}

variable "origin_ipv4" {
  type        = string
  default     = "178.128.112.214"
  description = "Origin server IPv4 address (DigitalOcean droplet)"
}

variable "proxied" {
  type        = bool
  default     = true
  description = "Whether to proxy traffic through Cloudflare"
}

variable "zoho_dkim_value" {
  type        = string
  sensitive   = true
  description = "DKIM public key value for Zoho Mail"
}
