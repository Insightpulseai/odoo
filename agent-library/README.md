# Agent Library (v1)

This pack turns product/docs pages into:

- `capability_atoms.yaml` (normalized feature atoms)
- `ux_patterns.yaml` (reusable UI/UX patterns)
- `docs_ux_kit.yaml` (documentation IA/UX kit)
- `locale_overlays/*.yaml` (e.g., Philippines tax overlay)
- `product_mappings/*.yaml` (e.g., Concur → Odoo 19 CE + OCA + minimal IPAI glue)
- `evidence/*.jsonl` (traceable excerpts with URLs and heading paths)

## Contract

- Every extracted claim must map to at least 1 evidence row.
- YAML outputs must validate against JSON schemas.
- No UI/manual steps; CLI-only.

## Quickstart

```bash
make -f agent-library/Makefile bootstrap
make -f agent-library/Makefile crawl_all
make -f agent-library/Makefile catalog_all
make -f agent-library/Makefile distill_all
make -f agent-library/Makefile validate
```
