output "root_a_record_id" {
  value       = cloudflare_record.root_a.id
  description = "ID of the root A record"
}

output "www_a_record_id" {
  value       = cloudflare_record.www_a.id
  description = "ID of the www A record"
}

output "erp_a_record_id" {
  value       = cloudflare_record.erp_a.id
  description = "ID of the erp A record"
}

output "mx_record_ids" {
  value = {
    mx1 = cloudflare_record.mx1.id
    mx2 = cloudflare_record.mx2.id
    mx3 = cloudflare_record.mx3.id
  }
  description = "IDs of MX records"
}

output "spf_record_id" {
  value       = cloudflare_record.spf.id
  description = "ID of the SPF record"
}

output "dmarc_record_id" {
  value       = cloudflare_record.dmarc.id
  description = "ID of the DMARC record"
}

output "dkim_record_id" {
  value       = cloudflare_record.dkim_zoho.id
  description = "ID of the DKIM record"
}
