#!/usr/bin/env python3
from __future__ import annotations

import ast
import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

ROOT = Path(__file__).resolve().parents[1]

SCAN_DIRS = ["addons", "oca", "vendor", "external-src"]
MANIFEST_FILES = {"__manifest__.py", "__openerp__.py"}

FIELD_TYPE_MAP = {
    "Char": "varchar",
    "Text": "text",
    "Boolean": "boolean",
    "Integer": "int",
    "Float": "float",
    "Monetary": "decimal",
    "Binary": "binary",
    "Date": "date",
    "Datetime": "datetime",
    "Selection": "varchar",
    "Many2one": "int",
    "Many2many": "int",
}


@dataclass
class FieldDef:
    name: str
    field_type: str
    store: bool = True
    required: bool = False
    index: bool = False
    relation: Optional[str] = None
    inverse: Optional[str] = None
    relation_table: Optional[str] = None
    column1: Optional[str] = None
    column2: Optional[str] = None
    ondelete: Optional[str] = None
    related: Optional[str] = None
    compute: Optional[str] = None


@dataclass
class ModelDef:
    name: str
    module: str
    table: Optional[str]
    model_type: str
    inherits: List[str] = field(default_factory=list)
    inherits_delegated: Dict[str, str] = field(default_factory=dict)
    fields: Dict[str, FieldDef] = field(default_factory=dict)
    sql_constraints: List[Tuple[str, str, str]] = field(default_factory=list)
    python_constraints: List[str] = field(default_factory=list)
    file_paths: Set[str] = field(default_factory=set)


@dataclass
class TableDef:
    name: str
    fields: Dict[str, str] = field(default_factory=dict)
    notes: List[str] = field(default_factory=list)


def iter_module_roots() -> Dict[Path, str]:
    module_roots: Dict[Path, str] = {}
    for dir_name in SCAN_DIRS:
        root_dir = ROOT / dir_name
        if not root_dir.exists():
            continue
        for manifest in root_dir.rglob("__manifest__.py"):
            module_roots[manifest.parent] = manifest.parent.name
        for manifest in root_dir.rglob("__openerp__.py"):
            module_roots[manifest.parent] = manifest.parent.name
    return module_roots


def find_module_root(path: Path, module_roots: Dict[Path, str]) -> Optional[Path]:
    for parent in [path] + list(path.parents):
        if parent in module_roots:
            return parent
    return None


def literal_eval(node: ast.AST) -> Any:
    try:
        return ast.literal_eval(node)
    except Exception:
        return None


def get_base_name(node: ast.AST) -> Optional[str]:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = get_base_name(node.value)
        if base:
            return f"{base}.{node.attr}"
        return node.attr
    return None


def is_odoo_model_base(node: ast.AST) -> Optional[str]:
    name = get_base_name(node)
    if not name:
        return None
    if name.endswith("models.Model"):
        return "Model"
    if name.endswith("models.TransientModel"):
        return "TransientModel"
    if name.endswith("models.AbstractModel"):
        return "AbstractModel"
    return None


def parse_field_call(node: ast.Call) -> Optional[FieldDef]:
    if not isinstance(node.func, ast.Attribute):
        return None
    if not isinstance(node.func.value, ast.Name):
        return None
    if node.func.value.id != "fields":
        return None
    field_type = node.func.attr
    field = FieldDef(name="", field_type=field_type)
    if node.args:
        first_arg = literal_eval(node.args[0])
        if isinstance(first_arg, str):
            field.relation = first_arg
    if field_type == "One2many" and len(node.args) >= 2:
        field.inverse = literal_eval(node.args[1])
    if field_type == "Many2many":
        if len(node.args) >= 2:
            field.relation_table = literal_eval(node.args[1])
        if len(node.args) >= 3:
            field.column1 = literal_eval(node.args[2])
        if len(node.args) >= 4:
            field.column2 = literal_eval(node.args[3])
    for keyword in node.keywords:
        if keyword.arg == "store":
            store_val = literal_eval(keyword.value)
            if isinstance(store_val, bool):
                field.store = store_val
        if keyword.arg == "required":
            required_val = literal_eval(keyword.value)
            if isinstance(required_val, bool):
                field.required = required_val
        if keyword.arg == "index":
            index_val = literal_eval(keyword.value)
            if isinstance(index_val, bool):
                field.index = index_val
        if keyword.arg == "ondelete":
            ondelete_val = literal_eval(keyword.value)
            if isinstance(ondelete_val, str):
                field.ondelete = ondelete_val
        if keyword.arg == "related":
            related_val = literal_eval(keyword.value)
            if isinstance(related_val, str):
                field.related = related_val
        if keyword.arg == "compute":
            compute_val = literal_eval(keyword.value)
            if isinstance(compute_val, str):
                field.compute = compute_val
    return field


def parse_model(file_path: Path, module: str) -> List[ModelDef]:
    source = file_path.read_text(encoding="utf-8", errors="ignore")
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []
    models: List[ModelDef] = []
    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue
        model_type = None
        for base in node.bases:
            model_type = is_odoo_model_base(base)
            if model_type:
                break
        if not model_type:
            continue
        attrs: Dict[str, Any] = {}
        fields: Dict[str, FieldDef] = {}
        sql_constraints: List[Tuple[str, str, str]] = []
        python_constraints: List[str] = []
        for item in node.body:
            if isinstance(item, ast.Assign):
                if len(item.targets) != 1:
                    continue
                target = item.targets[0]
                if isinstance(target, ast.Name):
                    name = target.id
                    if name in {"_name", "_inherit", "_table", "_auto", "_inherits"}:
                        attrs[name] = literal_eval(item.value)
                        continue
                    if isinstance(item.value, ast.Call):
                        field_def = parse_field_call(item.value)
                        if field_def:
                            field_def.name = name
                            fields[name] = field_def
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name) and target.id == "_sql_constraints":
                        constraints_val = literal_eval(item.value)
                        if isinstance(constraints_val, list):
                            for entry in constraints_val:
                                if (
                                    isinstance(entry, (list, tuple))
                                    and len(entry) >= 3
                                    and all(isinstance(v, str) for v in entry[:3])
                                ):
                                    sql_constraints.append((entry[0], entry[1], entry[2]))
            if isinstance(item, ast.FunctionDef):
                for decorator in item.decorator_list:
                    if isinstance(decorator, ast.Call):
                        deco_name = get_base_name(decorator.func)
                        if deco_name == "api.constrains":
                            python_constraints.append(item.name)
        model_name = attrs.get("_name")
        inherit_val = attrs.get("_inherit")
        inherit_list: List[str] = []
        if isinstance(inherit_val, str):
            inherit_list = [inherit_val]
        elif isinstance(inherit_val, (list, tuple)):
            inherit_list = [v for v in inherit_val if isinstance(v, str)]
        if not model_name and isinstance(inherit_val, str):
            model_name = inherit_val
        if not model_name:
            continue
        auto_val = attrs.get("_auto")
        if auto_val is False:
            table_name = None
        else:
            table_name = attrs.get("_table")
            if not table_name:
                table_name = model_name.replace(".", "_")
        inherits_delegated = {}
        inherits_val = attrs.get("_inherits")
        if isinstance(inherits_val, dict):
            inherits_delegated = {
                k: v for k, v in inherits_val.items() if isinstance(k, str) and isinstance(v, str)
            }
        model_def = ModelDef(
            name=model_name,
            module=module,
            table=table_name,
            model_type=model_type,
            inherits=inherit_list,
            inherits_delegated=inherits_delegated,
            fields=fields,
            sql_constraints=sql_constraints,
            python_constraints=python_constraints,
        )
        model_def.file_paths.add(str(file_path.relative_to(ROOT)))
        models.append(model_def)
    return models


def collect_models() -> Dict[str, ModelDef]:
    module_roots = iter_module_roots()
    models: Dict[str, ModelDef] = {}
    for module_root, module_name in sorted(module_roots.items(), key=lambda x: x[1]):
        for file_path in module_root.rglob("*.py"):
            if any(part.startswith(".") for part in file_path.parts):
                continue
            if file_path.name in MANIFEST_FILES:
                continue
            file_models = parse_model(file_path, module_name)
            for model_def in file_models:
                existing = models.get(model_def.name)
                if existing:
                    existing.fields.update(model_def.fields)
                    existing.sql_constraints.extend(model_def.sql_constraints)
                    existing.python_constraints.extend(model_def.python_constraints)
                    existing.file_paths.update(model_def.file_paths)
                    if model_def.table and not existing.table:
                        existing.table = model_def.table
                    if model_def.inherits:
                        existing.inherits = sorted(set(existing.inherits + model_def.inherits))
                    existing.inherits_delegated.update(model_def.inherits_delegated)
                else:
                    models[model_def.name] = model_def
    return models


def ensure_meta_fields(model: ModelDef, table: TableDef) -> None:
    for meta, field_type in [
        ("id", "int"),
        ("create_uid", "int"),
        ("create_date", "datetime"),
        ("write_uid", "int"),
        ("write_date", "datetime"),
    ]:
        if meta not in table.fields:
            table.fields[meta] = field_type
    if "active" in model.fields and "active" not in table.fields:
        table.fields["active"] = FIELD_TYPE_MAP.get("Boolean", "boolean")
    if "company_id" in model.fields and "company_id" not in table.fields:
        table.fields["company_id"] = FIELD_TYPE_MAP.get("Many2one", "int")


def derive_many2many_table(model: ModelDef, field: FieldDef, model_table: str, models: Dict[str, ModelDef]) -> Tuple[str, str, str]:
    relation_table = field.relation_table
    comodel_table = None
    if field.relation:
        comodel = models.get(field.relation)
        comodel_table = comodel.table if comodel else field.relation.replace(".", "_")
    if not relation_table:
        relation_table = f"{model_table}_{field.name}_rel"
    col1 = field.column1 or f"{model_table}_id"
    col2 = field.column2 or f"{comodel_table or 'id'}_id"
    return relation_table, col1, col2


def build_tables(models: Dict[str, ModelDef]) -> Tuple[Dict[str, TableDef], List[Tuple[str, str]]]:
    tables: Dict[str, TableDef] = {}
    refs: List[Tuple[str, str]] = []
    for model in models.values():
        if not model.table:
            continue
        if model.model_type == "AbstractModel":
            continue
        table = tables.setdefault(model.table, TableDef(name=model.table))
        for field in model.fields.values():
            if field.field_type == "One2many":
                continue
            if field.field_type in {"Many2one", "Many2many"}:
                if not field.store:
                    continue
            if field.compute and not field.store:
                continue
            if field.related and not field.store:
                continue
            if field.field_type == "Many2many":
                continue
            field_type = FIELD_TYPE_MAP.get(field.field_type, "varchar")
            table.fields.setdefault(field.name, field_type)
            if field.field_type == "Many2one" and field.relation:
                refs.append((f"{model.table}.{field.name}", field.relation))
        ensure_meta_fields(model, table)
        if model.sql_constraints:
            for name, sql, msg in model.sql_constraints:
                table.notes.append(f"{name}: {sql} ({msg})")
    # many2many tables
    for model in models.values():
        if not model.table:
            continue
        if model.model_type == "AbstractModel":
            continue
        for field in model.fields.values():
            if field.field_type != "Many2many":
                continue
            if field.compute and not field.store:
                continue
            if field.related and not field.store:
                continue
            model_table = model.table
            relation_table, col1, col2 = derive_many2many_table(model, field, model_table, models)
            if relation_table not in tables:
                tables[relation_table] = TableDef(name=relation_table)
            tables[relation_table].fields.setdefault(col1, "int")
            tables[relation_table].fields.setdefault(col2, "int")
            if field.relation:
                refs.append((f"{relation_table}.{col2}", field.relation))
            refs.append((f"{relation_table}.{col1}", model.name))
    return tables, refs


def collect_stub_tables(tables: Dict[str, TableDef], refs: List[Tuple[str, str]], models: Dict[str, ModelDef]) -> None:
    model_by_name = models
    for _, target_model in refs:
        if target_model in model_by_name and model_by_name[target_model].table:
            continue
        table_name = target_model.replace(".", "_")
        if table_name not in tables:
            tables[table_name] = TableDef(name=table_name, fields={"id": "int"}, notes=["stub for core model"]) 


def generate_dbml(tables: Dict[str, TableDef], refs: List[Tuple[str, str]], models: Dict[str, ModelDef]) -> str:
    lines: List[str] = []
    for table_name in sorted(tables.keys()):
        table = tables[table_name]
        lines.append(f"Table {table.name} {{")
        for field_name in sorted(table.fields.keys()):
            field_type = table.fields[field_name]
            pk = " [pk]" if field_name == "id" else ""
            lines.append(f"  {field_name} {field_type}{pk}")
        if table.notes:
            note = "\\n".join(sorted(set(table.notes)))
            lines.append(f"  Note: '{note}'")
        lines.append("}")
        lines.append("")
    # refs
    for source, target_model in sorted(refs):
        target_table = target_model.replace(".", "_")
        if target_model in models and models[target_model].table:
            target_table = models[target_model].table
        lines.append(f"Ref: {source} > {target_table}.id")
    return "\n".join(lines).rstrip() + "\n"


def generate_mermaid(tables: Dict[str, TableDef], refs: List[Tuple[str, str]], models: Dict[str, ModelDef]) -> str:
    lines = ["erDiagram"]
    for table_name in sorted(tables.keys()):
        table = tables[table_name]
        lines.append(f"  {table.name} {{")
        for field_name in sorted(table.fields.keys()):
            field_type = table.fields[field_name]
            lines.append(f"    {field_type} {field_name}")
        lines.append("  }")
    for source, target_model in sorted(refs):
        source_table, source_field = source.split(".")
        target_table = target_model.replace(".", "_")
        if target_model in models and models[target_model].table:
            target_table = models[target_model].table
        lines.append(f"  {source_table} ||--o{{ {target_table} : \"{source_field}\"")
    return "\n".join(lines).rstrip() + "\n"


def generate_plantuml(tables: Dict[str, TableDef], refs: List[Tuple[str, str]], models: Dict[str, ModelDef]) -> str:
    lines = ["@startuml", "hide circle", "skinparam linetype ortho"]
    for table_name in sorted(tables.keys()):
        table = tables[table_name]
        lines.append(f"entity {table.name} {{")
        for field_name in sorted(table.fields.keys()):
            field_type = table.fields[field_name]
            lines.append(f"  {field_type} {field_name}")
        lines.append("}")
    for source, target_model in sorted(refs):
        source_table, source_field = source.split(".")
        target_table = target_model.replace(".", "_")
        if target_model in models and models[target_model].table:
            target_table = models[target_model].table
        lines.append(f"{source_table} }}o--|| {target_table} : {source_field}")
    lines.append("@enduml")
    return "\n".join(lines).rstrip() + "\n"


def generate_orm_map(models: Dict[str, ModelDef]) -> str:
    lines: List[str] = ["# Odoo ORM Map", ""]
    for model_name in sorted(models.keys()):
        model = models[model_name]
        lines.append(f"## {model.name}")
        lines.append("")
        lines.append(f"- Module: `{model.module}`")
        lines.append(f"- Model type: `{model.model_type}`")
        lines.append(f"- Table: `{model.table or 'N/A'}`")
        if model.inherits:
            lines.append(f"- _inherit: `{', '.join(model.inherits)}`")
        if model.inherits_delegated:
            inherits_fmt = ", ".join(f"{k} via {v}" for k, v in model.inherits_delegated.items())
            lines.append(f"- _inherits: `{inherits_fmt}`")
        if model.sql_constraints:
            lines.append("- SQL constraints:")
            for name, sql, msg in sorted(model.sql_constraints):
                lines.append(f"  - `{name}`: `{sql}` ({msg})")
        if model.python_constraints:
            lines.append("- Python constraints:")
            for name in sorted(set(model.python_constraints)):
                lines.append(f"  - `{name}`")
        lines.append("")
        persisted = []
        non_persisted = []
        for field in sorted(model.fields.values(), key=lambda f: f.name):
            is_persisted = True
            if field.field_type == "One2many":
                is_persisted = False
            if field.compute and not field.store:
                is_persisted = False
            if field.related and not field.store:
                is_persisted = False
            if field.field_type == "Many2many":
                is_persisted = True
            if is_persisted:
                persisted.append(field)
            else:
                non_persisted.append(field)
        lines.append("### Persisted fields")
        for field in persisted:
            details = []
            if field.relation:
                details.append(f"relation={field.relation}")
            if field.related:
                details.append(f"related={field.related}")
            if field.compute:
                details.append(f"compute={field.compute}")
            if field.required:
                details.append("required")
            if field.index:
                details.append("index")
            if field.ondelete:
                details.append(f"ondelete={field.ondelete}")
            detail_str = f" ({', '.join(details)})" if details else ""
            lines.append(f"- `{field.name}`: `{field.field_type}`{detail_str}")
        lines.append("")
        lines.append("### Non-persisted fields")
        if non_persisted:
            for field in non_persisted:
                details = []
                if field.relation:
                    details.append(f"relation={field.relation}")
                if field.related:
                    details.append(f"related={field.related}")
                if field.compute:
                    details.append(f"compute={field.compute}")
                detail_str = f" ({', '.join(details)})" if details else ""
                lines.append(f"- `{field.name}`: `{field.field_type}`{detail_str}")
        else:
            lines.append("- _none_")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def generate_module_deltas(models: Dict[str, ModelDef]) -> str:
    lines = ["# Odoo Module Deltas", ""]
    ipai_modules = sorted({m.module for m in models.values() if m.module.startswith("ipai")})
    for module in ipai_modules:
        lines.append(f"## {module}")
        lines.append("")
        new_tables = []
        extended_tables: Dict[str, List[str]] = {}
        relation_tables: Set[str] = set()
        for model in models.values():
            if model.module != module:
                continue
            if model.model_type == "AbstractModel":
                continue
            if model.table and model.name.replace(".", "_") == model.table:
                if model.name not in model.inherits or model.name in model.inherits and model.name != model.table:
                    new_tables.append(model.table)
            if model.inherits and model.name in model.inherits and model.table:
                fields_added = sorted(model.fields.keys())
                if fields_added:
                    extended_tables.setdefault(model.table, []).extend(fields_added)
            for field in model.fields.values():
                if field.field_type == "Many2many" and model.table:
                    relation_table, _, _ = derive_many2many_table(model, field, model.table, models)
                    relation_tables.add(relation_table)
        if new_tables:
            lines.append("- New tables:")
            for table in sorted(set(new_tables)):
                lines.append(f"  - `{table}`")
        if extended_tables:
            lines.append("- Extended tables:")
            for table in sorted(extended_tables.keys()):
                fields_list = ", ".join(sorted(set(extended_tables[table])))
                lines.append(f"  - `{table}`: {fields_list}")
        if relation_tables:
            lines.append("- Relation tables:")
            for table in sorted(relation_tables):
                lines.append(f"  - `{table}`")
        if not any([new_tables, extended_tables, relation_tables]):
            lines.append("- _No model changes detected._")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def generate_model_index(models: Dict[str, ModelDef]) -> Dict[str, Any]:
    model_entries = []
    for model_name in sorted(models.keys()):
        model = models[model_name]
        field_entries = []
        for field in sorted(model.fields.values(), key=lambda f: f.name):
            field_entries.append(
                {
                    "name": field.name,
                    "type": field.field_type,
                    "store": field.store,
                    "relation": field.relation,
                    "required": field.required,
                    "index": field.index,
                    "ondelete": field.ondelete,
                    "related": field.related,
                    "compute": field.compute,
                }
            )
        model_entries.append(
            {
                "name": model.name,
                "table": model.table,
                "module": model.module,
                "inherits": model.inherits,
                "inherits_delegated": model.inherits_delegated,
                "fields": field_entries,
                "sql_constraints": [
                    {"name": name, "sql": sql, "message": msg}
                    for name, sql, msg in sorted(model.sql_constraints)
                ],
                "python_constraints": sorted(set(model.python_constraints)),
                "relations": sorted({f.relation for f in model.fields.values() if f.relation}),
            }
        )
    return {"models": model_entries}


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main() -> None:
    models = collect_models()
    tables, refs = build_tables(models)
    collect_stub_tables(tables, refs, models)

    dbml = generate_dbml(tables, refs, models)
    mermaid = generate_mermaid(tables, refs, models)
    plantuml = generate_plantuml(tables, refs, models)
    orm_map = generate_orm_map(models)
    module_deltas = generate_module_deltas(models)
    model_index = generate_model_index(models)

    output_dir = ROOT / "docs" / "data-model"
    write_file(output_dir / "ODOO_CANONICAL_SCHEMA.dbml", dbml)
    write_file(output_dir / "ODOO_ERD.mmd", mermaid)
    write_file(output_dir / "ODOO_ERD.puml", plantuml)
    write_file(output_dir / "ODOO_ORM_MAP.md", orm_map)
    write_file(output_dir / "ODOO_MODULE_DELTAS.md", module_deltas)
    write_file(output_dir / "ODOO_MODEL_INDEX.json", json.dumps(model_index, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
