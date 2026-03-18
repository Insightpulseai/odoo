# OCA Stack Management Makefile
# Usage: make fetch | make update | make lock | make verify

SHELL := /bin/bash
.ONESHELL:
.PHONY: fetch update lock verify clean help

OCA_DIR := addons/oca
REQ_FILE := oca-requirements.txt
LOCK_FILE := oca.lock

# Colors
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m

help:
	@echo "OCA Stack Management"
	@echo ""
	@echo "Commands:"
	@echo "  make fetch    - Clone/update OCA repos from requirements"
	@echo "  make update   - Pull latest from 18.0 branch for each repo"
	@echo "  make lock     - Generate lock file with current SHAs"
	@echo "  make verify   - Verify all repos match lock file"
	@echo "  make clean    - Remove all OCA repos (dangerous)"
	@echo ""

fetch:
	@echo -e "$(GREEN)>>> Fetching OCA repositories...$(NC)"
	@set -euo pipefail
	@mkdir -p $(OCA_DIR)
	@while IFS=' ' read -r name url ref || [[ -n "$$name" ]]; do
		[[ "$$name" =~ ^#.*$$ || -z "$$name" ]] && continue
		echo -e "$(YELLOW)→ $$name$(NC)"
		if [[ -d "$(OCA_DIR)/$$name" ]]; then
			echo "  exists, skipping (use 'make update' to pull)"
		else
			git clone --depth 1 --branch "$$ref" "$$url" "$(OCA_DIR)/$$name"
			echo "  cloned @ $$ref"
		fi
	done < $(REQ_FILE)
	@echo -e "$(GREEN)>>> Fetch complete$(NC)"

update:
	@echo -e "$(GREEN)>>> Updating OCA repositories...$(NC)"
	@set -euo pipefail
	@while IFS=' ' read -r name url ref || [[ -n "$$name" ]]; do
		[[ "$$name" =~ ^#.*$$ || -z "$$name" ]] && continue
		echo -e "$(YELLOW)→ $$name$(NC)"
		if [[ -d "$(OCA_DIR)/$$name" ]]; then
			cd "$(OCA_DIR)/$$name"
			git fetch origin "$$ref"
			git checkout "$$ref"
			git pull origin "$$ref" --ff-only
			cd - > /dev/null
			echo "  updated to latest $$ref"
		else
			echo -e "  $(RED)not found, run 'make fetch' first$(NC)"
		fi
	done < $(REQ_FILE)
	@echo -e "$(GREEN)>>> Update complete$(NC)"

lock:
	@echo -e "$(GREEN)>>> Generating lock file...$(NC)"
	@set -euo pipefail
	@echo "# OCA Lock File - DO NOT EDIT MANUALLY" > $(LOCK_FILE)
	@echo "# Generated: $$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> $(LOCK_FILE)
	@echo "" >> $(LOCK_FILE)
	@while IFS=' ' read -r name url ref || [[ -n "$$name" ]]; do
		[[ "$$name" =~ ^#.*$$ || -z "$$name" ]] && continue
		if [[ -d "$(OCA_DIR)/$$name" ]]; then
			sha=$$(cd "$(OCA_DIR)/$$name" && git rev-parse HEAD)
			echo "$$name $$url $$sha" >> $(LOCK_FILE)
			echo -e "$(YELLOW)→ $$name$(NC) @ $$sha"
		fi
	done < $(REQ_FILE)
	@echo -e "$(GREEN)>>> Lock file generated: $(LOCK_FILE)$(NC)"

verify:
	@echo -e "$(GREEN)>>> Verifying OCA repositories...$(NC)"
	@set -euo pipefail
	@errors=0
	@while IFS=' ' read -r name url sha || [[ -n "$$name" ]]; do
		[[ "$$name" =~ ^#.*$$ || -z "$$name" ]] && continue
		if [[ -d "$(OCA_DIR)/$$name" ]]; then
			current=$$(cd "$(OCA_DIR)/$$name" && git rev-parse HEAD)
			if [[ "$$current" == "$$sha" ]]; then
				echo -e "$(GREEN)✓$(NC) $$name @ $$sha"
			else
				echo -e "$(RED)✗$(NC) $$name mismatch: expected $$sha, got $$current"
				errors=$$((errors + 1))
			fi
		else
			echo -e "$(RED)✗$(NC) $$name: directory not found"
			errors=$$((errors + 1))
		fi
	done < $(LOCK_FILE)
	@if [[ $$errors -gt 0 ]]; then
		echo -e "$(RED)>>> Verification FAILED: $$errors errors$(NC)"
		exit 1
	fi
	@echo -e "$(GREEN)>>> Verification PASSED$(NC)"

clean:
	@echo -e "$(RED)>>> WARNING: This will remove all OCA repos!$(NC)"
	@read -p "Are you sure? [y/N] " confirm
	@if [[ "$$confirm" == "y" || "$$confirm" == "Y" ]]; then
		rm -rf $(OCA_DIR)/*
		echo -e "$(GREEN)>>> Cleaned$(NC)"
	else
		echo "Aborted"
	fi
