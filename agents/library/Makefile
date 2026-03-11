SHELL := /usr/bin/env bash
.ONESHELL:
.SHELLFLAGS := -euo pipefail -c

PY := python3
PIP := python3 -m pip

RAW := agent-library/raw
DIST := agent-library/dist
EVID := agent-library/evidence

bootstrap:
	$(PIP) install --upgrade pip
	$(PIP) install -r agent-library/ci/requirements.txt

# Crawl targets (add more roots by editing agent-library/templates/sources.yaml)

crawl_all:
	$(PY) agent-library/scripts/run_crawl.py --sources agent-library/templates/sources.yaml --out $(RAW)

catalog_all:
	$(PY) agent-library/scripts/run_catalog.py --root $(RAW) --out $(DIST)

distill_all:
	$(PY) agent-library/scripts/distill.py --catalog $(DIST) --out $(DIST) --evidence $(EVID)

validate:
	$(PY) agent-library/scripts/validate_outputs.py --dist $(DIST) --schemas agent-library/schemas

clean:
	rm -rf $(RAW) $(DIST) $(EVID)
