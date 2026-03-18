output "ruleset_id" {
  value       = cloudflare_ruleset.healthcheck_bypass.id
  description = "ID of the healthcheck WAF bypass ruleset"
}
