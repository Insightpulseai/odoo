# Supabase Terraform Infrastructure

Terraform configuration for managing Supabase project settings.

## Quick Start

```bash
# Set access token
export SUPABASE_ACCESS_TOKEN="sbp_xxxxxxxxxxxxx"
export TF_VAR_supabase_org_id="your-org-id"

# Initialize
terraform init

# Plan changes
terraform plan

# Apply (requires manual approval)
terraform apply
```

## Files

| File | Purpose |
|------|---------|
| `main.tf` | Provider configuration |
| `variables.tf` | Input variables |
| `production.tf` | Production project resources |
| `outputs.tf` | Output values |
| `terraform.tfvars.example` | Example variable values |

## What This Manages

- API settings (schemas, max rows)
- Project metadata

## What This Does NOT Manage

- Database migrations (use `supabase-branching.yml`)
- Edge Functions (use Supabase CLI)
- Preview branches (automatic via GitHub Integration)

## Documentation

See [SUPABASE_TERRAFORM_INTEGRATION.md](../../docs/infra/SUPABASE_TERRAFORM_INTEGRATION.md) for complete guide.
