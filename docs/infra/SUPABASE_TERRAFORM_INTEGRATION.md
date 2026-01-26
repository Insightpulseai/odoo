# Supabase Terraform Integration

> **Project ID:** `spdtwktxdalcfigzeqrz`
> **Terraform Provider:** `supabase/supabase` v1.x
> **Purpose:** Infrastructure-as-code management for Supabase project settings and CI/CD pipelines

---

## Overview

The Supabase Terraform Provider enables version control of project settings and automated provisioning. This integration complements the existing GitHub-based branching workflow (see [SUPABASE_BRANCHING_INTEGRATION.md](./SUPABASE_BRANCHING_INTEGRATION.md)).

**Use Terraform when:**
- Version controlling API settings, auth config, or project metadata
- Provisioning new Supabase projects programmatically
- Setting up CI/CD pipelines for infrastructure changes
- Managing multiple environments (dev/staging/prod) consistently

**Use GitHub Integration when:**
- Database migrations (handled by `supabase-branching.yml`)
- Edge Functions deployment
- Preview branches for PRs

---

## Provider Configuration

### Basic Setup

```hcl
# infra/supabase/main.tf

terraform {
  required_providers {
    supabase = {
      source  = "supabase/supabase"
      version = "~> 1.0"
    }
  }
}

provider "supabase" {
  # Access token from environment or file
  access_token = var.supabase_access_token
}

variable "supabase_access_token" {
  type        = string
  sensitive   = true
  description = "Supabase personal access token"
}
```

### Authentication Methods

```bash
# Option 1: Environment variable (recommended for CI)
export SUPABASE_ACCESS_TOKEN="sbp_xxxxxxxxxxxxx"

# Option 2: File-based (local development)
echo "sbp_xxxxxxxxxxxxx" > .supabase-token
chmod 600 .supabase-token
```

```hcl
# File-based provider configuration
provider "supabase" {
  access_token = file("${path.module}/.supabase-token")
}
```

---

## Project Import

Import the existing production project for management:

```hcl
# infra/supabase/production.tf

variable "production_project_ref" {
  type        = string
  default     = "spdtwktxdalcfigzeqrz"
  description = "Production Supabase project reference"
}

# Import existing project
import {
  to = supabase_project.production
  id = var.production_project_ref
}

resource "supabase_project" "production" {
  organization_id   = var.supabase_org_id
  name              = "odoo-ce-production"
  database_password = var.db_password
  region            = "ap-southeast-1"

  lifecycle {
    # Password managed externally
    ignore_changes = [database_password]
  }
}
```

```bash
# Import command
terraform import supabase_project.production spdtwktxdalcfigzeqrz
```

---

## Settings Management

### API Settings

```hcl
# infra/supabase/settings.tf

resource "supabase_settings" "production" {
  project_ref = var.production_project_ref

  api = jsonencode({
    db_schema            = "public,storage,graphql_public,mcp_jobs"
    db_extra_search_path = "public,extensions"
    max_rows             = 1000
  })
}
```

### Auth Settings

```hcl
resource "supabase_settings" "auth" {
  project_ref = var.production_project_ref

  auth = jsonencode({
    site_url                  = "https://erp.insightpulseai.net"
    additional_redirect_urls  = [
      "https://control.insightpulseai.net/**",
      "http://localhost:3000/**"
    ]
    jwt_expiry               = 3600
    enable_signup            = true
    double_confirm_changes   = true
  })
}
```

### Database Settings

```hcl
resource "supabase_settings" "database" {
  project_ref = var.production_project_ref

  database = jsonencode({
    statement_timeout = "120s"
    pool_mode         = "transaction"
  })
}
```

---

## Multi-Environment Setup

```hcl
# infra/supabase/environments.tf

locals {
  environments = {
    development = {
      name   = "odoo-ce-dev"
      region = "ap-southeast-1"
    }
    staging = {
      name   = "odoo-ce-staging"
      region = "ap-southeast-1"
    }
    production = {
      name   = "odoo-ce-production"
      region = "ap-southeast-1"
    }
  }
}

resource "supabase_project" "env" {
  for_each = local.environments

  organization_id   = var.supabase_org_id
  name              = each.value.name
  database_password = var.db_passwords[each.key]
  region            = each.value.region

  lifecycle {
    ignore_changes = [database_password]
  }
}

# Apply consistent settings across environments
resource "supabase_settings" "env" {
  for_each = supabase_project.env

  project_ref = each.value.id

  api = jsonencode({
    db_schema            = "public,storage,graphql_public,mcp_jobs"
    db_extra_search_path = "public,extensions"
    max_rows             = 1000
  })
}
```

---

## CI/CD Pipeline

### GitHub Actions Workflow

```yaml
# .github/workflows/terraform-supabase.yml

name: Terraform Supabase

on:
  push:
    branches: [main]
    paths:
      - 'infra/supabase/**'
  pull_request:
    branches: [main]
    paths:
      - 'infra/supabase/**'

env:
  TF_VAR_supabase_access_token: ${{ secrets.SUPABASE_ACCESS_TOKEN }}
  TF_VAR_supabase_org_id: ${{ secrets.SUPABASE_ORG_ID }}

jobs:
  plan:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: infra/supabase

    steps:
      - uses: actions/checkout@v4

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: "1.6.x"

      - name: Terraform Init
        run: terraform init

      - name: Terraform Format Check
        run: terraform fmt -check

      - name: Terraform Validate
        run: terraform validate

      - name: Terraform Plan
        id: plan
        run: terraform plan -no-color -out=tfplan
        continue-on-error: true

      - name: Post Plan to PR
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v7
        with:
          script: |
            const plan = `${{ steps.plan.outputs.stdout }}`;
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: `## Terraform Plan\n\`\`\`hcl\n${plan}\n\`\`\``
            });

  apply:
    needs: plan
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: infra/supabase
    environment: production

    steps:
      - uses: actions/checkout@v4

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: "1.6.x"

      - name: Terraform Init
        run: terraform init

      - name: Terraform Apply
        run: terraform apply -auto-approve

      - name: Capture Evidence
        run: |
          mkdir -p ../../docs/evidence/$(date +%Y%m%d-%H%M)/terraform
          terraform show -json > ../../docs/evidence/$(date +%Y%m%d-%H%M)/terraform/state.json
          terraform output -json > ../../docs/evidence/$(date +%Y%m%d-%H%M)/terraform/outputs.json
```

---

## Directory Structure

```
infra/supabase/
├── main.tf                    # Provider configuration
├── variables.tf               # Input variables
├── outputs.tf                 # Output values
├── production.tf              # Production project resource
├── vault_secrets.tf           # Vault secrets integration
├── Makefile                   # Idempotent operations
├── terraform.tfvars.example   # Example values
├── README.md
└── envs/
    ├── dev/
    │   └── terraform.tfvars   # Development config
    ├── staging/
    │   └── terraform.tfvars   # Staging config
    └── prod/
        └── terraform.tfvars   # Production config
```

---

## Variables Reference

```hcl
# infra/supabase/variables.tf

variable "supabase_access_token" {
  type        = string
  sensitive   = true
  description = "Supabase personal access token (sbp_*)"
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
  description = "Database password (managed externally)"
  default     = ""
}
```

```hcl
# infra/supabase/terraform.tfvars.example

supabase_org_id        = "nknnyrtlhxudbsbuazsu"
production_project_ref = "spdtwktxdalcfigzeqrz"
# supabase_access_token set via environment variable
```

---

## Outputs

```hcl
# infra/supabase/outputs.tf

output "project_url" {
  value       = "https://${var.production_project_ref}.supabase.co"
  description = "Supabase project URL"
}

output "api_url" {
  value       = "https://${var.production_project_ref}.supabase.co/rest/v1"
  description = "REST API endpoint"
}

output "graphql_url" {
  value       = "https://${var.production_project_ref}.supabase.co/graphql/v1"
  description = "GraphQL endpoint"
}

output "studio_url" {
  value       = "https://supabase.com/dashboard/project/${var.production_project_ref}"
  description = "Supabase Studio dashboard URL"
}
```

---

## Verification

```bash
# Initialize Terraform
cd infra/supabase
terraform init

# Validate configuration
terraform validate

# Plan changes
terraform plan

# Apply changes (requires approval in CI)
terraform apply

# Verify outputs
terraform output
```

---

## Integration with Existing Workflows

Terraform manages **project settings**, while GitHub Integration manages **database schema and functions**:

| Concern | Tool | Workflow |
|---------|------|----------|
| API settings | Terraform | `terraform-supabase.yml` |
| Auth configuration | Terraform | `terraform-supabase.yml` |
| Database migrations | Supabase CLI | `supabase-branching.yml` |
| Edge Functions | Supabase CLI | `supabase-branching.yml` |
| Preview branches | GitHub Integration | Automatic on PR |
| Production deploy | Both | Terraform + migrations |

---

## Supabase as Control Plane

Supabase serves as the unified control plane for secrets, configuration, and state across the InsightPulse AI stack:

```
┌─────────────────────────────────────────────────────────────┐
│                   Supabase Control Plane                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   Vault (Secrets)    Database (State)    Edge Functions     │
│         │                   │                   │           │
│         ▼                   ▼                   ▼           │
│   ┌─────────┐         ┌─────────┐         ┌─────────┐       │
│   │ Odoo    │         │ MCP     │         │ Webhooks│       │
│   │ Vercel  │         │ Jobs    │         │ Crons   │       │
│   │ DO      │         │ State   │         │ Sync    │       │
│   └─────────┘         └─────────┘         └─────────┘       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Vault Secrets Integration

Secrets are stored in Supabase Vault and injected into runtimes:

```hcl
# infra/supabase/vault_secrets.tf (placeholder)

variable "odoo_db_url" {
  type      = string
  sensitive = true
}

variable "digitalocean_token" {
  type      = string
  sensitive = true
}

# When Terraform provider supports Vault:
# resource "supabase_vault_secret" "odoo_db_url" {
#   project_ref = var.production_project_ref
#   name        = "ODOO_DB_URL"
#   value       = var.odoo_db_url
# }
```

### Runtime Secret Injection

Edge Functions access Vault secrets via:

```typescript
// supabase/functions/example/index.ts
const odooDbUrl = Deno.env.get('ODOO_DB_URL');
```

Database functions access via:

```sql
SELECT vault.get_secret('ODOO_DB_URL');
```

---

## Makefile Operations

Use the Makefile for idempotent, environment-aware operations:

```bash
# Plan for environment
make ENV=dev plan
make ENV=staging plan
make ENV=prod plan

# Apply to environment
make ENV=dev apply
make ENV=prod apply

# Validate configuration
make validate

# Format files
make fmt

# Database operations
make db-push      # Push migrations
make db-diff      # Show pending changes
make db-reset     # Reset local DB (dev only)
```

### CI Targets

```bash
# Non-interactive CI operations
make ci-plan ENV=prod
make ci-apply ENV=prod
```

---

## Troubleshooting

### Import Errors

```bash
# If project already exists in state
terraform state rm supabase_project.production
terraform import supabase_project.production spdtwktxdalcfigzeqrz
```

### Token Issues

```bash
# Verify token is valid
curl -sf "https://api.supabase.com/v1/projects" \
  -H "Authorization: Bearer $SUPABASE_ACCESS_TOKEN" | jq .

# Check token scopes
# Token must have project management permissions
```

### State Drift

```bash
# Refresh state from remote
terraform refresh

# Check for drift
terraform plan -detailed-exitcode
```

---

## Related Documentation

**In this repo:**
- [Supabase Environment Management](./SUPABASE_ENVIRONMENTS.md)
- [Supabase Branching Integration](./SUPABASE_BRANCHING_INTEGRATION.md)
- [DigitalOcean PR Sandbox Terraform](../../infra/digitalocean/pr-sandbox/)

**Official Supabase Docs:**
- [Terraform Provider](https://supabase.com/docs/guides/deployment/terraform)
- [Terraform Tutorial](https://supabase.com/docs/guides/deployment/terraform/tutorial)
- [Terraform Reference](https://supabase.com/docs/guides/deployment/terraform/reference)
- [Provider Registry](https://registry.terraform.io/providers/supabase/supabase/latest)

---

*Last updated: 2026-01-25*
