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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dist", required=True)
    ap.add_argument("--schemas", required=True)
    args = ap.parse_args()

    dist = Path(args.dist)
    schemas = Path(args.schemas)

    cap = load_yaml(dist / "capability_atoms.yaml")
    ux = load_yaml(dist / "ux_patterns.yaml")

    validate(cap, load_schema(schemas / "capability_atoms.schema.json"), "capability_atoms.yaml")
    validate(ux, load_schema(schemas / "ux_patterns.schema.json"), "ux_patterns.yaml")


if __name__ == "__main__":
    main()
