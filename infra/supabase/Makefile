# Supabase Terraform Makefile
# Idempotent operations for multi-environment management
#
# Usage:
#   make plan              # Plan for dev (default)
#   make ENV=prod plan     # Plan for production
#   make ENV=staging apply # Apply to staging
#
# Required environment variables:
#   TF_VAR_supabase_access_token
#   TF_VAR_supabase_org_id

.PHONY: init plan apply destroy fmt validate clean help

# Default environment
ENV ?= dev

# Terraform binary
TF := terraform

# Environment-specific tfvars (copy .example to remove .example suffix)
TFVARS := envs/$(ENV)/terraform.tfvars
TFVARS_EXAMPLE := envs/$(ENV)/terraform.tfvars.example

# Colors for output
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Show this help
	@echo "Supabase Terraform Management"
	@echo ""
	@echo "Usage: make [ENV=dev|staging|prod] <target>"
	@echo ""
	@echo "Targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "Examples:"
	@echo "  make plan              # Plan for dev environment"
	@echo "  make ENV=prod plan     # Plan for production"
	@echo "  make ENV=staging apply # Apply to staging"

init: ## Initialize Terraform
	@echo "$(GREEN)Initializing Terraform...$(NC)"
	$(TF) init -upgrade

fmt: ## Format Terraform files
	@echo "$(GREEN)Formatting Terraform files...$(NC)"
	$(TF) fmt -recursive

validate: init ## Validate Terraform configuration
	@echo "$(GREEN)Validating configuration...$(NC)"
	$(TF) validate

plan: init validate ## Plan changes for environment
	@echo "$(YELLOW)Planning for environment: $(ENV)$(NC)"
	@if [ ! -f $(TFVARS) ] && [ -f $(TFVARS_EXAMPLE) ]; then \
		echo "$(YELLOW)Using example tfvars: $(TFVARS_EXAMPLE)$(NC)"; \
		$(TF) plan -var-file="$(TFVARS_EXAMPLE)" -out=tfplan.$(ENV); \
	elif [ -f $(TFVARS) ]; then \
		$(TF) plan -var-file="$(TFVARS)" -out=tfplan.$(ENV); \
	else \
		echo "$(RED)Error: No tfvars found for $(ENV)$(NC)" && exit 1; \
	fi

apply: init ## Apply changes for environment
	@echo "$(YELLOW)Applying for environment: $(ENV)$(NC)"
	@if [ -f tfplan.$(ENV) ]; then \
		$(TF) apply tfplan.$(ENV); \
	elif [ -f $(TFVARS) ]; then \
		$(TF) apply -var-file="$(TFVARS)"; \
	elif [ -f $(TFVARS_EXAMPLE) ]; then \
		$(TF) apply -var-file="$(TFVARS_EXAMPLE)"; \
	else \
		echo "$(RED)Error: No tfvars found for $(ENV)$(NC)" && exit 1; \
	fi

destroy: init ## Destroy resources for environment (DANGEROUS)
	@echo "$(RED)WARNING: Destroying resources for environment: $(ENV)$(NC)"
	@read -p "Are you sure? [y/N] " confirm && [ "$$confirm" = "y" ]
	$(TF) destroy -var-file="$(TFVARS)"

output: ## Show outputs for environment
	@echo "$(GREEN)Outputs for environment: $(ENV)$(NC)"
	$(TF) output

state-list: ## List resources in state
	$(TF) state list

clean: ## Clean up local Terraform files
	@echo "$(GREEN)Cleaning up...$(NC)"
	rm -rf .terraform
	rm -f .terraform.lock.hcl
	rm -f tfplan.*
	rm -f terraform.tfstate*

# CI/CD targets
ci-plan: init validate ## CI: Plan without interaction
	$(TF) plan -var-file="$(TFVARS)" -out=tfplan.$(ENV) -no-color

ci-apply: init ## CI: Apply without interaction
	$(TF) apply -auto-approve -var-file="$(TFVARS)" -no-color

# Database operations (via Supabase CLI)
db-push: ## Push database migrations
	@echo "$(GREEN)Pushing database migrations...$(NC)"
	cd ../.. && supabase db push

db-diff: ## Show pending migration diff
	@echo "$(GREEN)Showing migration diff...$(NC)"
	cd ../.. && supabase db diff

db-reset: ## Reset local database (DEV ONLY)
	@if [ "$(ENV)" = "prod" ]; then \
		echo "$(RED)Cannot reset production database$(NC)"; \
		exit 1; \
	fi
	cd ../.. && supabase db reset
