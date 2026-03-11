#!/usr/bin/env python3
"""
Build an ORM ↔ SQL crosswalk JSON from DBML + schema.json.

Inputs (env vars):
  ERD_DBML_OUT       Path to odoo.dbml   (default: docs/erd/odoo.dbml)
  ERD_SCHEMA_JSON    Path to schema.json (default: docs/data_model/schema.json)
  ERD_CROSSWALK_OUT  Output path         (default: docs/erd/odoo_crosswalk.json)

Output JSON structure:
  {
    "meta": { "generated_by": ..., "dbml_source": ..., "schema_source": ... },
    "models": [
      {
        "model":   "res.partner",
        "table":   "res_partner",
        "matched": true,
        "fields":  [
          { "field": "name", "type": "char", "column": "name", "matched": true }
        ]
      }
    ],
    "unmatched_models": [ "some.model.without.table" ],
    "unmatched_tables": [ "some_table_not_in_orm" ]
  }

Exit codes:
  0  success
  1  error (missing inputs or parse failure)
"""

import json
import os
import re
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# DBML minimal parser — extract table names and column lists only
# ---------------------------------------------------------------------------

def parse_dbml_tables(dbml_text: str) -> dict[str, list[str]]:
    """
    Returns {table_name: [col_name, ...]} from DBML text.
    Handles both  Table foo { ... }  and  Table schema.foo { ... }.
    """
    result: dict[str, list[str]] = {}
    # Match Table <name> { <body> }
    table_re = re.compile(r'Table\s+([\w.]+)\s*\{([^}]*)\}', re.DOTALL)
    col_re = re.compile(r'^\s*([\w]+)\s+', re.MULTILINE)

    for m in table_re.finditer(dbml_text):
        name = m.group(1)
        # strip schema prefix for lookup key (keep full name as value too)
        short = name.split(".")[-1]
        body = m.group(2)
        cols = []
        for line in body.splitlines():
            line = line.strip()
            # skip Note: lines and empty lines
            if not line or line.startswith("Note:") or line.startswith("//"):
                continue
            cm = col_re.match(line)
            if cm:
                cols.append(cm.group(1))
        result[short] = cols
        if "." in name:
            result[name] = cols  # also index by full qualified name

    return result


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    dbml_path = Path(os.environ.get("ERD_DBML_OUT", "docs/erd/odoo.dbml"))
    schema_path = Path(os.environ.get("ERD_SCHEMA_JSON", "docs/data_model/schema.json"))
    out_path = Path(os.environ.get("ERD_CROSSWALK_OUT", "docs/erd/odoo_crosswalk.json"))

    # --- load inputs --------------------------------------------------------
    if not dbml_path.exists():
        print(f"ERROR: DBML not found: {dbml_path}")
        print("Run export_dbml.py first, or set ERD_DBML_OUT.")
        return 1

    dbml_tables = parse_dbml_tables(dbml_path.read_text(encoding="utf-8"))
    print(f"Parsed {len(dbml_tables)} tables from {dbml_path}")

    orm_models: list[dict] = []
    if schema_path.exists():
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        orm_models = schema.get("models", [])
        print(f"Loaded {len(orm_models)} ORM models from {schema_path}")
    else:
        print(f"WARNING: schema.json not found ({schema_path}); ORM side will be empty.")
        print("Generate it with: python3 tools/odoo_schema/export_schema.py")

    # --- build model→table map from ir_model data ---------------------------
    # schema.json encodes the _table as the model name with dots → underscores
    # (Odoo convention). Fields with store=True map 1:1 to columns.

    def model_to_table(model_name: str) -> str:
        """Default Odoo convention: res.partner → res_partner."""
        return model_name.replace(".", "_")

    # --- crosswalk ----------------------------------------------------------
    crosswalk_models = []
    all_table_names = set(dbml_tables.keys())
    matched_tables: set[str] = set()

    for m in sorted(orm_models, key=lambda x: x["model"]):
        model_name = m["model"]
        table_name = model_to_table(model_name)
        in_dbml = table_name in dbml_tables
        if in_dbml:
            matched_tables.add(table_name)

        # field crosswalk (stored fields only)
        field_entries = []
        for f in m.get("fields", []):
            if not f.get("store"):
                continue
            fname = f["field"]
            ftype = f["type"]
            # many2one fields: try fname_id first, then fname
            if ftype == "many2one":
                col_candidate = fname + "_id"
                if in_dbml and col_candidate in dbml_tables.get(table_name, []):
                    col = col_candidate
                    col_matched = True
                elif in_dbml and fname in dbml_tables.get(table_name, []):
                    col = fname
                    col_matched = True
                else:
                    col = col_candidate  # best guess
                    col_matched = False
            else:
                col = fname
                col_matched = in_dbml and (col in dbml_tables.get(table_name, []))

            field_entries.append({
                "field":   fname,
                "type":    ftype,
                "column":  col,
                "matched": col_matched,
            })

        crosswalk_models.append({
            "model":   model_name,
            "table":   table_name,
            "matched": in_dbml,
            "fields":  field_entries,
        })

    unmatched_models = [e["model"] for e in crosswalk_models if not e["matched"]]
    unmatched_tables = sorted(all_table_names - matched_tables - {
        t for t in all_table_names if "." in t  # skip fq duplicates
    })

    # --- output -------------------------------------------------------------
    out_path.parent.mkdir(parents=True, exist_ok=True)
    output = {
        "meta": {
            "generated_by":  "scripts/erd/export_crosswalk.py",
            "dbml_source":   str(dbml_path),
            "schema_source": str(schema_path),
        },
        "models":            crosswalk_models,
        "unmatched_models":  unmatched_models,
        "unmatched_tables":  unmatched_tables,
    }

    out_path.write_text(
        json.dumps(output, indent=2, sort_keys=False, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    total = len(crosswalk_models)
    matched = sum(1 for e in crosswalk_models if e["matched"])
    print(f"Wrote: {out_path}")
    print(f"  {matched}/{total} models matched to DBML tables")
    print(f"  {len(unmatched_models)} unmatched models, {len(unmatched_tables)} unmatched tables")
    return 0


if __name__ == "__main__":
    sys.exit(main())
