SHELL := /usr/bin/env bash
.ONESHELL:
.SHELLFLAGS := -euo pipefail -c

PY := python3
PIP := python3 -m pip

RAW := raw
DIST := dist
EVID := evidence

bootstrap:
	$(PIP) install --upgrade pip
	$(PIP) install -r ci/requirements.txt

# Crawl targets (add more roots by editing templates/sources.yaml)

crawl_all:
	$(PY) scripts/run_crawl.py --sources templates/sources.yaml --out $(RAW)

catalog_all:
	$(PY) scripts/run_catalog.py --root $(RAW) --out $(DIST)

distill_all:
	$(PY) scripts/distill.py --catalog $(DIST) --out $(DIST) --evidence $(EVID)

validate:
	$(PY) scripts/validate_outputs.py --dist $(DIST) --schemas schemas

clean:
	rm -rf $(RAW) $(DIST) $(EVID)
