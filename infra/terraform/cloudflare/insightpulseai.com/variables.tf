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
  default     = "v=DKIM1; k=rsa; p=MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAmFj2Pp5o9iBNv9F6bQWQ8NpLLWMfNRq0zWf0oTF6kM0q8Y6XE+6K0qZmL+5xAsvU5FqMqGa9M9BLK9+zGk4H3xZkJ6nCTz5HvKb9s+1T3h1GkZ8vL9xc8cQJ7ZnMnLqC0KkLN2qbM0TpBjJq6f3QK8N5mz8xkQmZLG9L5B0cK9nQJ8YqK3v5FnJ9qQhPgB+H7vT9c3mF5HqLbN9qZ6z9Q3cZ8nM0vJ3L8B6bK7G4nF5HqLbN9qZ6z9Q3cZ8nM0vJ3L8B6bK7G4nF5HqLbN9qZ6z9Q3cZ8nM0vJ3L8B6bK7G4nF5HqLbN9qZ6z9Q3cZ8nM0vJ3L8B6bK7G4nFwIDAQAB"
}
