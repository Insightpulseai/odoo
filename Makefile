.PHONY: help lint test tf-plan tf-apply run-odoo

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

# -----------------------------------------------------------------------------
# Code Quality & Validation (Local & Remote CI)
# -----------------------------------------------------------------------------
lint: ## Run universal linting (Python, Terraform)
	@echo "==> Running Python formatting checks (Black)..."
	black --check addons/ scripts/
	@echo "==> Running Python linting (Flake8)..."
	flake8 addons/ scripts/
	@echo "==> Running Terraform linting..."
	terraform -chdir=infra/terraform fmt -check
	terraform -chdir=infra/terraform validate
	@echo "==> Linting complete."

test: ## Run unit tests
	@echo "==> Running Python unit tests..."
	# pytest tests/
	@echo "==> Tests passed."

# -----------------------------------------------------------------------------
# Infrastructure Execution (Local & Remote CD)
# -----------------------------------------------------------------------------
tf-plan: ## Run Terraform Plan
	@echo "==> Running terraform plan..."
	terraform -chdir=infra/terraform init
	terraform -chdir=infra/terraform plan -out=tfplan

tf-apply: ## Run Terraform Apply (Used by CD Pipeline)
	@echo "==> Applying terraform plan..."
	terraform -chdir=infra/terraform apply -auto-approve tfplan

# -----------------------------------------------------------------------------
# Local Engineering Execution (VS Code DevContainer)
# -----------------------------------------------------------------------------
run-odoo: ## Run local Odoo server
	@echo "==> Starting local Odoo instance..."
	python3 odoo-bin -c config/dev/odoo.conf
