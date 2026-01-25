# Output Values for Supabase Terraform

output "project_ref" {
  value       = var.production_project_ref
  description = "Supabase project reference ID"
}

output "project_url" {
  value       = "https://${var.production_project_ref}.supabase.co"
  description = "Supabase project URL"
}

output "api_url" {
  value       = "https://${var.production_project_ref}.supabase.co/rest/v1"
  description = "PostgREST API endpoint"
}

output "graphql_url" {
  value       = "https://${var.production_project_ref}.supabase.co/graphql/v1"
  description = "GraphQL endpoint"
}

output "realtime_url" {
  value       = "wss://${var.production_project_ref}.supabase.co/realtime/v1"
  description = "Realtime WebSocket endpoint"
}

output "storage_url" {
  value       = "https://${var.production_project_ref}.supabase.co/storage/v1"
  description = "Storage API endpoint"
}

output "functions_url" {
  value       = "https://${var.production_project_ref}.supabase.co/functions/v1"
  description = "Edge Functions base URL"
}

output "studio_url" {
  value       = "https://supabase.com/dashboard/project/${var.production_project_ref}"
  description = "Supabase Studio dashboard URL"
}
