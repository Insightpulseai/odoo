#!/usr/bin/env python3
"""
Odoo Schema Extractor

Introspects Odoo metadata tables (ir_model, ir_model_fields, ir_model_data)
and exports schema as JSON/YAML + Mermaid ERD + extension points report.

Usage:
    export PGHOST=db PGDATABASE=odoo PGUSER=postgres PGPASSWORD=xxx
    python3 tools/odoo_schema/export_schema.py

Output:
    docs/data_model/schema.json
    docs/data_model/schema.yaml
    docs/data_model/erd.mmd
    docs/data_model/EXTENSION_POINTS.md
"""
import os
import json
import sys
from collections import defaultdict

try:
    import psycopg2
except ImportError as e:
    raise SystemExit(
        "psycopg2 missing. Run inside Odoo container or: pip install psycopg2-binary"
    ) from e


def env(name, default=None):
    """Get env var with optional default."""
    v = os.environ.get(name, default)
    if v is None or v == "":
        raise SystemExit(f"Missing env var: {name}")
    return v


def pg_conn():
    """Create PostgreSQL connection using libpq-style env vars."""
    host = (
        os.environ.get("PGHOST")
        or os.environ.get("DB_HOST")
        or env("ODOO_DB_HOST", "db")
    )
    port = int(
        os.environ.get("PGPORT")
        or os.environ.get("DB_PORT")
        or env("ODOO_DB_PORT", "5432")
    )
    db = (
        os.environ.get("PGDATABASE")
        or os.environ.get("DB_NAME")
        or env("ODOO_DB", "odoo")
    )
    user = (
        os.environ.get("PGUSER")
        or os.environ.get("DB_USER")
        or env("ODOO_DB_USER", "postgres")
    )
    pwd = (
        os.environ.get("PGPASSWORD")
        or os.environ.get("DB_PASSWORD")
        or os.environ.get("ODOO_DB_PASSWORD", "")
    )
    return psycopg2.connect(host=host, port=port, dbname=db, user=user, password=pwd)


def fetchall(cur, q, args=None):
    """Execute query and return list of dicts."""
    cur.execute(q, args or ())
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, row)) for row in cur.fetchall()]


def export_schema():
    """Main export function."""
    out_dir = env("OUT_DIR", "docs/data_model")
    os.makedirs(out_dir, exist_ok=True)

    with pg_conn() as conn, conn.cursor() as cur:
        # Installed modules
        modules = fetchall(
            cur,
            """
            SELECT name, state, latest_version
            FROM ir_module_module
            ORDER BY name
        """,
        )
        installed = {
            m["name"] for m in modules if m["state"] in ("installed", "to upgrade")
        }

        # Models
        models = fetchall(
            cur,
            """
            SELECT id, model, name
            FROM ir_model
            ORDER BY model
        """,
        )
        model_by_id = {m["id"]: m for m in models}

        # Fields
        fields = fetchall(
            cur,
            """
            SELECT
              f.id,
              f.model_id,
              m.model AS model,
              f.name AS field,
              f.ttype AS type,
              f.relation,
              f.required,
              f.readonly,
              f.index,
              f.store,
              f.translate
            FROM ir_model_fields f
            JOIN ir_model m ON m.id = f.model_id
            ORDER BY m.model, f.name
        """,
        )

        # Map models/fields to module via ir_model_data (best-effort)
        imd = fetchall(
            cur,
            """
            SELECT module, model, res_id, name
            FROM ir_model_data
            WHERE model IN ('ir.model', 'ir.model.fields')
        """,
        )
        model_origin = {}
        field_origin = {}
        for r in imd:
            if r["module"] and r["module"] != "base":
                if r["model"] == "ir.model":
                    model_origin[r["res_id"]] = r["module"]
                elif r["model"] == "ir.model.fields":
                    field_origin[r["res_id"]] = r["module"]

        schema = {
            "meta": {
                "db": os.environ.get("PGDATABASE")
                or os.environ.get("ODOO_DB")
                or os.environ.get("DB_NAME"),
                "installed_modules_count": sum(
                    1 for m in modules if m["state"] in ("installed", "to upgrade")
                ),
                "generated_by": "tools/odoo_schema/export_schema.py",
            },
            "modules": modules,
            "models": [],
            "edges": [],
        }

        edges = set()
        model_fields = defaultdict(list)

        for f in fields:
            fmod = field_origin.get(f["id"]) or "UNKNOWN"
            model_fields[f["model"]].append(
                {
                    "field": f["field"],
                    "type": f["type"],
                    "relation": f["relation"],
                    "required": f["required"],
                    "readonly": f["readonly"],
                    "index": f["index"],
                    "store": f["store"],
                    "translate": f["translate"],
                    "origin_module": fmod,
                }
            )

            # Create ER edges for relational fields
            if f["type"] in ("many2one", "one2many", "many2many") and f["relation"]:
                edges.add((f["model"], f["relation"], f["type"], f["field"]))

        for m in models:
            origin = model_origin.get(m["id"]) or "UNKNOWN"
            schema["models"].append(
                {
                    "model": m["model"],
                    "name": m["name"],
                    "origin_module": origin,
                    "fields": model_fields.get(m["model"], []),
                }
            )

        schema["edges"] = [
            {"from": a, "to": b, "rel": rel, "field": fld}
            for (a, b, rel, fld) in sorted(edges)
        ]

        # Write JSON
        json_path = os.path.join(out_dir, "schema.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(schema, f, indent=2, ensure_ascii=False)

        # Write YAML (minimal, no external deps)
        yaml_path = os.path.join(out_dir, "schema.yaml")
        with open(yaml_path, "w", encoding="utf-8") as f:
            f.write("meta:\n")
            for k, v in schema["meta"].items():
                f.write(f"  {k}: {json.dumps(v)}\n")
            f.write("models:\n")
            for m in schema["models"]:
                f.write(f"  - model: {m['model']}\n")
                f.write(f"    name: {json.dumps(m['name'])}\n")
                f.write(f"    origin_module: {m['origin_module']}\n")
                f.write("    fields:\n")
                for fld in m["fields"]:
                    f.write(f"      - field: {fld['field']}\n")
                    f.write(f"        type: {fld['type']}\n")
                    if fld["relation"]:
                        f.write(f"        relation: {fld['relation']}\n")
                    f.write(f"        required: {str(bool(fld['required'])).lower()}\n")
                    f.write(f"        readonly: {str(bool(fld['readonly'])).lower()}\n")
                    f.write(f"        index: {str(bool(fld['index'])).lower()}\n")
                    f.write(f"        store: {str(bool(fld['store'])).lower()}\n")
                    f.write(
                        f"        translate: {str(bool(fld['translate'])).lower()}\n"
                    )
                    f.write(f"        origin_module: {fld['origin_module']}\n")

        # Mermaid ERD (subset: only key anchors + relations)
        anchors = set(
            os.environ.get(
                "ANCHORS",
                "res.partner,res.users,res.company,crm.lead,sale.order,"
                "purchase.order,stock.picking,account.move,project.task,"
                "account.analytic.account,account.analytic.line",
            ).split(",")
        )
        mm_path = os.path.join(out_dir, "erd.mmd")
        with open(mm_path, "w", encoding="utf-8") as f:
            f.write("erDiagram\n")
            # Entities
            for m in schema["models"]:
                if m["model"] in anchors:
                    f.write(f"  {m['model'].replace('.', '_')} {{\n")
                    for fld in m["fields"][:25]:
                        t = fld["type"]
                        n = fld["field"]
                        f.write(f"    {t} {n}\n")
                    f.write("  }\n")
            # Edges
            for e in schema["edges"]:
                if e["from"] in anchors and e["to"] in anchors:
                    a = e["from"].replace(".", "_")
                    b = e["to"].replace(".", "_")
                    # Approximate cardinality by rel type
                    if e["rel"] == "many2one":
                        f.write(f"  {a} }}o--|| {b} : {e['field']}\n")
                    elif e["rel"] == "one2many":
                        f.write(f"  {a} ||--o{{ {b} : {e['field']}\n")
                    else:
                        f.write(f"  {a} }}o--o{{ {b} : {e['field']}\n")

        # Extension points report (models owned by ipai_* or with ipai_* fields)
        ext_path = os.path.join(out_dir, "EXTENSION_POINTS.md")
        with open(ext_path, "w", encoding="utf-8") as f:
            f.write("# Extension Points\n\n")
            f.write("## Custom-owned models (origin_module starts with ipai_)\n\n")
            for m in schema["models"]:
                if (m["origin_module"] or "").startswith("ipai_"):
                    f.write(f"- `{m['model']}` (module: `{m['origin_module']}`)\n")
            f.write(
                "\n## Fields likely from custom modules "
                "(field origin_module starts with ipai_)\n\n"
            )
            for m in schema["models"]:
                hits = [
                    fld
                    for fld in m["fields"]
                    if (fld["origin_module"] or "").startswith("ipai_")
                ]
                if hits:
                    f.write(f"- `{m['model']}`:\n")
                    for fld in hits[:50]:
                        f.write(
                            f"  - `{fld['field']}` ({fld['type']}) "
                            f"from `{fld['origin_module']}`\n"
                        )

    print(f"Wrote:\n- {json_path}\n- {yaml_path}\n- {mm_path}\n- {ext_path}")
    return 0


if __name__ == "__main__":
    sys.exit(export_schema())
