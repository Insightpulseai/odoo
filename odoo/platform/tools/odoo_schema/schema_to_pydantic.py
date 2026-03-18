#!/usr/bin/env python3
"""
Schema to Pydantic ORM Stubs Generator

Generates Pydantic BaseModel classes from schema.json for type-safe
ORM access patterns.

Usage:
    export SCHEMA_JSON=docs/data_model/schema.json
    export OUT_PY=docs/data_model/orm_models.py
    python3 tools/odoo_schema/schema_to_pydantic.py

Output:
    docs/data_model/orm_models.py
"""
import json
import os
import re
import sys

# Odoo field type to Python type mapping
TYPE_MAP = {
    "char": "str",
    "text": "str",
    "html": "str",
    "integer": "int",
    "float": "float",
    "monetary": "float",
    "boolean": "bool",
    "date": "str",
    "datetime": "str",
    "many2one": "int | None",
    "one2many": "list[int]",
    "many2many": "list[int]",
    "selection": "str",
    "binary": "str | None",
    "json": "dict",
    "reference": "str | None",
    "image": "str | None",
}


def safe_name(name: str) -> str:
    """Convert model/field name to valid Python identifier."""
    s = re.sub(r"[^0-9a-zA-Z_]", "_", name.replace(".", "_"))
    if s[0].isdigit():
        s = "_" + s
    return s


def model_to_class(model_name: str) -> str:
    """Convert Odoo model name to PascalCase class name."""
    parts = model_name.replace(".", "_").split("_")
    return "".join(p.capitalize() for p in parts)


def generate_pydantic():
    """Main generator function."""
    schema_path = os.environ.get("SCHEMA_JSON", "docs/data_model/schema.json")
    out_path = os.environ.get("OUT_PY", "docs/data_model/orm_models.py")

    if not os.path.exists(schema_path):
        print(f"Schema file not found: {schema_path}")
        print("Run export_schema.py first.")
        return 1

    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)

    lines = []
    lines.append('"""')
    lines.append("Odoo ORM Models - Pydantic Stubs")
    lines.append("")
    lines.append("Auto-generated from schema.json. Do not hand-edit.")
    lines.append(f"Database: {schema.get('meta', {}).get('db', 'unknown')}")
    lines.append(f"Models: {len(schema.get('models', []))}")
    lines.append('"""')
    lines.append("from typing import Optional")
    lines.append("from pydantic import BaseModel, Field")
    lines.append("")
    lines.append("")

    # Track generated class names to avoid duplicates
    generated = set()

    for m in schema.get("models", []):
        cls = model_to_class(m["model"])

        # Handle duplicate class names
        if cls in generated:
            cls = cls + "_" + safe_name(m["origin_module"])
        generated.add(cls)

        lines.append(f"class {cls}(BaseModel):")
        lines.append(f'    """')
        lines.append(f'    Odoo model: {m["model"]}')
        lines.append(f'    Origin module: {m["origin_module"]}')
        lines.append(f'    """')

        fields = m.get("fields", [])
        if not fields:
            lines.append("    pass")
            lines.append("")
            lines.append("")
            continue

        for fld in fields:
            ftype = fld.get("type", "")
            fname = safe_name(fld["field"])
            pytype = TYPE_MAP.get(ftype, "object")
            req = bool(fld.get("required"))

            # Handle reserved Python keywords
            if fname in ("class", "def", "return", "import", "from", "global", "type"):
                fname = fname + "_"

            if req:
                default = ""
            else:
                if "None" in pytype:
                    default = " = None"
                elif pytype.startswith("list"):
                    default = " = Field(default_factory=list)"
                elif pytype == "dict":
                    default = " = Field(default_factory=dict)"
                else:
                    default = f" = None"
                    pytype = f"Optional[{pytype}]"

            # Add relation info as comment
            comment = ""
            if fld.get("relation"):
                comment = f"  # → {fld['relation']}"

            lines.append(f"    {fname}: {pytype}{default}{comment}")

        lines.append("")
        lines.append("")

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"Wrote: {out_path}")
    print(f"Generated {len(generated)} model classes")
    return 0


if __name__ == "__main__":
    sys.exit(generate_pydantic())
