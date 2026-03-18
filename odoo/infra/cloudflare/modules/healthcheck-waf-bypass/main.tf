# =============================================================================
# Cloudflare WAF Bypass for Health Checks
# =============================================================================
# Allows automated health probes through the WAF when ALL conditions match:
#   1. User-Agent contains "healthcheck/"
#   2. X-Healthcheck-Token header equals the shared secret
#   3. URI path is a known health endpoint
#
# No blanket IP bypass. No wildcard paths. Least-privilege only.
# =============================================================================

resource "cloudflare_ruleset" "healthcheck_bypass" {
  zone_id     = var.zone_id
  name        = "healthcheck-waf-bypass"
  description = "Allow automated health probes on health endpoints with valid token"
  kind        = "zone"
  phase       = "http_request_firewall_custom"

  rules {
    action      = "skip"
    expression  = <<-EXPR
      (
        http.request.headers["user-agent"][0] contains "healthcheck/"
        and http.request.headers["x-healthcheck-token"][0] eq "${var.healthcheck_token}"
        and (
          http.request.uri.path eq "/healthz"
          or http.request.uri.path eq "/health"
          or http.request.uri.path eq "/web/health"
          or http.request.uri.path eq "/api/health"
          or http.request.uri.path eq "/.well-known/openid-configuration"
        )
      )
    EXPR
    description = "Bypass WAF for health probes with valid UA + token on health paths only"
    enabled     = true

    action_parameters {
      ruleset = "current"
    }
  }
}
