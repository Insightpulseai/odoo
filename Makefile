.PHONY: ipai-guard
ipai-guard:
	python scripts/ci/validate_ipai_custom_modules.py

.PHONY: help
help:
	@echo "Available targets:"
	@echo "  ipai-guard    - Validate ipai_* custom modules against allowlist"
