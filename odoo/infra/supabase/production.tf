# Production Supabase Project Resource
# Import existing project: terraform import supabase_project.production spdtwktxdalcfigzeqrz

# Import block for existing project
import {
  to = supabase_project.production
  id = var.production_project_ref
}

resource "supabase_project" "production" {
  organization_id   = var.supabase_org_id
  name              = "odoo-ce-production"
  database_password = var.db_password
  region            = var.region

  lifecycle {
    # Password managed externally via Supabase dashboard
    ignore_changes = [database_password]
  }
}

# API Settings
resource "supabase_settings" "api" {
  project_ref = var.production_project_ref

  api = jsonencode({
    db_schema            = join(",", var.api_schemas)
    db_extra_search_path = "public,extensions"
    max_rows             = var.api_max_rows
  })
}

# Auth Settings (if supported by provider version)
# Note: Check provider docs for auth settings support
# resource "supabase_settings" "auth" {
#   project_ref = var.production_project_ref
#
#   auth = jsonencode({
#     site_url                 = var.site_url
#     additional_redirect_urls = var.additional_redirect_urls
#     jwt_expiry               = 3600
#     enable_signup            = true
#     double_confirm_changes   = true
#   })
# }
