# Supabase Vault Secrets Integration
# Control plane for secrets across Odoo, Vercel, DigitalOcean, MCP stacks
#
# Supabase Vault provides encrypted secret storage accessible via:
# - Edge Functions (Deno.env)
# - Database functions (vault.get_secret())
# - Terraform (when provider supports it)
#
# TODO: Replace pseudo-resources with concrete supabase_* resources
#       when Supabase Terraform provider adds Vault support.

# -----------------------------------------------------------------------------
# Secret Variables (injected via CI or environment)
# -----------------------------------------------------------------------------

variable "odoo_db_url" {
  type        = string
  sensitive   = true
  default     = ""
  description = "Odoo PostgreSQL connection URL"
}

variable "digitalocean_token" {
  type        = string
  sensitive   = true
  default     = ""
  description = "DigitalOcean API token for infrastructure"
}

variable "vercel_token" {
  type        = string
  sensitive   = true
  default     = ""
  description = "Vercel API token for deployments"
}

variable "openai_api_key" {
  type        = string
  sensitive   = true
  default     = ""
  description = "OpenAI API key for AI features"
}

variable "anthropic_api_key" {
  type        = string
  sensitive   = true
  default     = ""
  description = "Anthropic API key for Claude integration"
}

variable "github_app_private_key" {
  type        = string
  sensitive   = true
  default     = ""
  description = "GitHub App private key for repo integrations"
}

# -----------------------------------------------------------------------------
# Supabase Vault Resources (Pseudo-structure)
# -----------------------------------------------------------------------------
# When Supabase Terraform provider adds vault support, uncomment and use:

# resource "supabase_vault_secret" "odoo_db_url" {
#   project_ref = var.production_project_ref
#   name        = "ODOO_DB_URL"
#   value       = var.odoo_db_url
#   description = "Odoo PostgreSQL connection URL"
# }

# resource "supabase_vault_secret" "digitalocean_token" {
#   project_ref = var.production_project_ref
#   name        = "DIGITALOCEAN_TOKEN"
#   value       = var.digitalocean_token
#   description = "DigitalOcean API token"
# }

# resource "supabase_vault_secret" "vercel_token" {
#   project_ref = var.production_project_ref
#   name        = "VERCEL_TOKEN"
#   value       = var.vercel_token
#   description = "Vercel API token"
# }

# resource "supabase_vault_secret" "openai_api_key" {
#   project_ref = var.production_project_ref
#   name        = "OPENAI_API_KEY"
#   value       = var.openai_api_key
#   description = "OpenAI API key"
# }

# resource "supabase_vault_secret" "anthropic_api_key" {
#   project_ref = var.production_project_ref
#   name        = "ANTHROPIC_API_KEY"
#   value       = var.anthropic_api_key
#   description = "Anthropic API key"
# }

# resource "supabase_vault_secret" "github_app_private_key" {
#   project_ref = var.production_project_ref
#   name        = "GITHUB_APP_PRIVATE_KEY"
#   value       = var.github_app_private_key
#   description = "GitHub App private key"
# }

# -----------------------------------------------------------------------------
# Alternative: SQL-based Vault setup via null_resource
# -----------------------------------------------------------------------------
# Use this pattern to manage Vault secrets via SQL when Terraform provider
# doesn't support native Vault resources.

# resource "null_resource" "vault_secrets" {
#   count = var.odoo_db_url != "" ? 1 : 0
#
#   provisioner "local-exec" {
#     command = <<-EOT
#       psql "$DATABASE_URL" -c "
#         SELECT vault.create_secret('${var.odoo_db_url}', 'ODOO_DB_URL');
#         SELECT vault.create_secret('${var.digitalocean_token}', 'DIGITALOCEAN_TOKEN');
#       "
#     EOT
#     environment = {
#       DATABASE_URL = "postgresql://postgres:${var.db_password}@db.${var.production_project_ref}.supabase.co:5432/postgres"
#     }
#   }
# }

# -----------------------------------------------------------------------------
# Outputs (safe - no sensitive values exposed)
# -----------------------------------------------------------------------------

output "vault_secrets_configured" {
  value       = var.odoo_db_url != "" || var.digitalocean_token != "" || var.vercel_token != ""
  description = "Whether any Vault secrets are configured"
}
