# Input Variables for Supabase Terraform
# Supabase Control Plane Configuration

variable "environment" {
  type        = string
  description = "Environment name (dev/staging/prod)"
  default     = "dev"

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, prod."
  }
}

variable "supabase_access_token" {
  type        = string
  sensitive   = true
  description = "Supabase personal access token (sbp_*). Set via SUPABASE_ACCESS_TOKEN env var."
}

variable "supabase_org_id" {
  type        = string
  description = "Supabase organization ID"
}

variable "production_project_ref" {
  type        = string
  default     = "spdtwktxdalcfigzeqrz"
  description = "Production project reference ID"
}

variable "db_password" {
  type        = string
  sensitive   = true
  description = "Database password (managed externally, lifecycle ignored)"
  default     = "placeholder-ignored"
}

variable "region" {
  type        = string
  default     = "ap-southeast-1"
  description = "Supabase project region"
}

variable "api_schemas" {
  type        = list(string)
  default     = ["public", "storage", "graphql_public", "mcp_jobs"]
  description = "Schemas exposed via PostgREST API"
}

variable "api_max_rows" {
  type        = number
  default     = 1000
  description = "Maximum rows returned per API request"
}

variable "site_url" {
  type        = string
  default     = "https://erp.insightpulseai.net"
  description = "Primary site URL for auth redirects"
}

variable "additional_redirect_urls" {
  type = list(string)
  default = [
    "https://control.insightpulseai.net/**",
    "http://localhost:3000/**",
    "http://localhost:5173/**"
  ]
  description = "Additional allowed redirect URLs for auth"
}
