#!/usr/bin/env python3
import argparse
from pathlib import Path
import yaml
import jsonschema
import json


def load_yaml(p: Path):
    return yaml.safe_load(p.read_text())


def load_schema(p: Path):
    return json.loads(p.read_text())


def validate(doc, schema, name):
    jsonschema.validate(instance=doc, schema=schema)
    print(f"[ok] {name}")


def maybe_validate_yaml(dist: Path, schemas: Path, filename: str, schema_file: str):
    p = dist / filename
    if not p.exists():
        print(f"[skip] {filename} not present")
        return
    validate(load_yaml(p), load_schema(schemas / schema_file), filename)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dist", required=True)
    ap.add_argument("--schemas", required=True)
    args = ap.parse_args()

    dist = Path(args.dist)
    schemas = Path(args.schemas)

    maybe_validate_yaml(dist, schemas, "capability_atoms.yaml", "capability_atoms.schema.json")
    maybe_validate_yaml(dist, schemas, "ux_patterns.yaml", "ux_patterns.schema.json")
    maybe_validate_yaml(
        dist, schemas, "locale_overlays/philippines_tax.yaml", "locale_overlay.schema.json"
    )
    maybe_validate_yaml(
        dist,
        schemas,
        "product_mappings/concur_to_odoo19_ce_oca_ipai.yaml",
        "product_mapping.schema.json",
    )


if __name__ == "__main__":
    main()
