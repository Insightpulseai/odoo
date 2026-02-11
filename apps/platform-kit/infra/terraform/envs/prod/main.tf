# ============================================================================
# Platform Kit - Production Environment
# ============================================================================

terraform {
  required_version = ">= 1.6.0"

  # TODO: Configure backend for state storage
  # backend "s3" {
  #   bucket = "platform-kit-tfstate"
  #   key    = "prod/terraform.tfstate"
  #   region = "us-east-1"
  # }
}

# ============================================================================
# Provider Configuration
# ============================================================================

# TODO: Add providers when selected
# provider "digitalocean" {
#   token = var.do_token
# }
#
# provider "cloudflare" {
#   api_token = var.cloudflare_api_token
# }

# ============================================================================
# Variables
# ============================================================================

variable "environment" {
  type        = string
  description = "Environment name"
  default     = "prod"
}

# ============================================================================
# Module Instantiation
# ============================================================================

module "platform_kit" {
  source = "../../modules/platform_kit"

  environment  = var.environment
  project_name = "platform-kit"

  tags = {
    owner       = "platform-team"
    criticality = "high"
  }
}

# ============================================================================
# Outputs
# ============================================================================

output "name_prefix" {
  value = module.platform_kit.name_prefix
}
