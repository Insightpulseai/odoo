# Supabase Terraform Infrastructure

Terraform configuration for managing Supabase as the control plane.

## Quick Start

```bash
# Set access token and org ID
export TF_VAR_supabase_access_token="sbp_xxxxxxxxxxxxx"
export TF_VAR_supabase_org_id="your-org-id"

# Using Makefile (recommended)
make plan              # Plan for dev (default)
make ENV=prod plan     # Plan for production
make ENV=staging apply # Apply to staging

# Or using Terraform directly
terraform init
terraform plan -var-file="envs/dev/terraform.tfvars"
terraform apply -var-file="envs/dev/terraform.tfvars"
```

## Directory Structure

```
infra/supabase/
├── main.tf                    # Provider configuration
├── variables.tf               # Input variables
├── production.tf              # Project resources
├── outputs.tf                 # Output values
├── vault_secrets.tf           # Vault secrets (placeholder)
├── Makefile                   # Idempotent operations
├── terraform.tfvars.example   # Example values
├── README.md
└── envs/
    ├── dev/
    │   └── terraform.tfvars.example   # Development config template
    ├── staging/
    │   └── terraform.tfvars.example   # Staging config template
    └── prod/
        └── terraform.tfvars.example   # Production config template
```

## Multi-Environment Usage

| Environment | Command | Purpose |
|-------------|---------|---------|
| Development | `make ENV=dev plan` | Local/sandbox testing |
| Staging | `make ENV=staging plan` | Pre-production validation |
| Production | `make ENV=prod plan` | Live deployment |

## Makefile Targets

| Target | Description |
|--------|-------------|
| `make help` | Show all available targets |
| `make init` | Initialize Terraform |
| `make plan` | Plan changes for environment |
| `make apply` | Apply changes for environment |
| `make destroy` | Destroy resources (DANGEROUS) |
| `make fmt` | Format Terraform files |
| `make validate` | Validate configuration |
| `make db-push` | Push Supabase migrations |

## What This Manages

**Terraform (infra-as-code):**
- API settings (schemas, max rows)
- Auth configuration
- Project metadata
- Vault secrets (when provider supports)

**Supabase CLI (via Makefile):**
- Database migrations
- Edge Functions deployment

## What This Does NOT Manage

- Preview branches (automatic via GitHub Integration)
- Real-time subscriptions
- Storage buckets (managed via migrations)

## Environment Variables

```bash
# Required
export TF_VAR_supabase_access_token="sbp_..."
export TF_VAR_supabase_org_id="..."

# Optional (for Vault integration)
export TF_VAR_odoo_db_url="postgresql://..."
export TF_VAR_digitalocean_token="dop_..."
export TF_VAR_vercel_token="..."
```

## CI/CD Integration

This stack is deployed via `.github/workflows/terraform-supabase.yml`:
- **PR**: `terraform plan` with comment
- **Main merge**: `terraform apply` + evidence capture

## Documentation

- [Terraform Integration Guide](../../docs/infra/SUPABASE_TERRAFORM_INTEGRATION.md)
- [Supabase Environments](../../docs/infra/SUPABASE_ENVIRONMENTS.md)
- [Supabase Branching](../../docs/infra/SUPABASE_BRANCHING_INTEGRATION.md)
