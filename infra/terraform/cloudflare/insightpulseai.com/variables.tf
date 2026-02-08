variable "cloudflare_api_token" {
  type        = string
  sensitive   = true
  description = "Cloudflare API token with DNS edit permissions"
}

variable "zone_id" {
  type        = string
  default     = "73f587aee652fc24fd643aec00dcca81"
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
  # Actual value from Cloudflare - concatenated TXT record
  default = "v=DKIM1; k=rsa; p=MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAmFj2PpxreN9r4Dv8DGdNpqc7VPsbAlDQh64jyTl78NCuXU4bAPHC2JCgeQkSnoxBH19Keewr62iRcsBNnHrz8HwgkbTg8ZwooC+Bd18Z9M4ZSwBD1IK53/lUKPMHmBAPoamo2COYKG+hmRvtxeJa3ZuX1Z9Hc2hYULEXg3pus9Su34FfD/GYb43ZaqSFqth4Qt14jOfBbX4lqAZJop2iwKRQCX00CBKugVHs/heVGnsBNKIqYMVgM9gtI0P2H81gxDlvisygCQVuuEHLHVmsx0UGBL+z3b4bMvaReWY66Otv2tUKP2rOssZCx9ZbtMrPJgx2xYv/tvtoQDi9A2pGBQIDAQAB"
}
