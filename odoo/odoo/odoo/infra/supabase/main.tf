# Supabase Terraform Configuration
# Manages project settings and API configuration
# Database migrations handled via GitHub Integration (supabase-branching.yml)

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    supabase = {
      source  = "supabase/supabase"
      version = "~> 1.0"
    }
  }

  # Remote state backend (optional - configure as needed)
  # backend "s3" {
  #   bucket = "odoo-ce-terraform-state"
  #   key    = "supabase/terraform.tfstate"
  #   region = "ap-southeast-1"
  # }
}

provider "supabase" {
  access_token = var.supabase_access_token
}
