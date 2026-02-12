# ============================================================================
# Platform Kit - Dev Environment
# ============================================================================

terraform {
  required_version = ">= 1.6.0"

  # TODO: Configure backend for state storage
  # backend "s3" {
  #   bucket = "platform-kit-tfstate"
  #   key    = "dev/terraform.tfstate"
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
  default     = "dev"
}

# ============================================================================
# Module Instantiation
# ============================================================================

module "platform_kit" {
  source = "../../modules/platform_kit"

  environment  = var.environment
  project_name = "platform-kit"

  tags = {
    owner = "platform-team"
  }
}

# ============================================================================
# Outputs
# ============================================================================

output "name_prefix" {
  value = module.platform_kit.name_prefix
}
