PYTHON ?= python3

.PHONY: resolve-conflicts fix-manifest

resolve-conflicts:
$(PYTHON) scripts/resolve_conflicts.py

fix-manifest:
$(PYTHON) scripts/resolve_conflicts.py --auto-manifest
