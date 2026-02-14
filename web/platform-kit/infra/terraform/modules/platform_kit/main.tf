# ============================================================================
# Platform Kit - Terraform Module
# ============================================================================
# Purpose: Infrastructure for Platform Kit ecosystem
# Providers: TBD (DigitalOcean, Cloudflare, AWS, etc.)
#
# Note: Supabase resources are typically managed via CLI, not Terraform.
# This module is for surrounding infrastructure (DNS, compute, storage).
# ============================================================================

terraform {
  required_version = ">= 1.6.0"
}

# ============================================================================
# Variables
# ============================================================================

variable "environment" {
  type        = string
  description = "Environment name (dev, staging, prod)"
  default     = "dev"
}

variable "project_name" {
  type        = string
  description = "Project name for resource naming"
  default     = "platform-kit"
}

variable "tags" {
  type        = map(string)
  description = "Tags to apply to all resources"
  default     = {}
}

# ============================================================================
# Locals
# ============================================================================

locals {
  common_tags = merge(
    {
      project     = var.project_name
      environment = var.environment
      managed_by  = "terraform"
    },
    var.tags
  )

  name_prefix = "${var.project_name}-${var.environment}"
}

# ============================================================================
# Outputs
# ============================================================================

output "name_prefix" {
  value       = local.name_prefix
  description = "Resource name prefix"
}

output "common_tags" {
  value       = local.common_tags
  description = "Common tags for all resources"
}

# ============================================================================
# TODO: Add provider-specific resources
# ============================================================================
# Example resources to add:
#
# 1. DigitalOcean Droplet (for n8n, Plane, etc.)
#    resource "digitalocean_droplet" "app" { ... }
#
# 2. DigitalOcean Managed PostgreSQL (if not using Supabase)
#    resource "digitalocean_database_cluster" "postgres" { ... }
#
# 3. Cloudflare DNS records
#    resource "cloudflare_record" "app" { ... }
#
# 4. DigitalOcean Spaces (object storage)
#    resource "digitalocean_spaces_bucket" "artifacts" { ... }
#
# 5. DigitalOcean Load Balancer
#    resource "digitalocean_loadbalancer" "app" { ... }
# ============================================================================
