#!/usr/bin/env python3
"""
scripts/odoo/extract_settings_catalog.py
=========================================
Extract Odoo 19 CE res.config.settings field catalog from a running instance.

Produces a deterministic, stably-sorted YAML artifact at
ssot/odoo/settings_catalog.yaml.

Two extraction modes:
  1. XML-RPC (default): connects to a live Odoo via ODOO_URL/ODOO_DB/creds
  2. Source scan (--source-scan): parses addons/**/models/res_config_settings.py
     for a best-effort offline catalog (no runtime needed, less accurate)

Env vars (XML-RPC mode):
    ODOO_URL              e.g. https://erp.insightpulseai.com
    ODOO_DB               e.g. odoo
    ODOO_ADMIN_LOGIN      default: admin
    ODOO_ADMIN_PASSWORD

Usage:
    # Live extraction (recommended):
    python scripts/odoo/extract_settings_catalog.py

    # Source-scan mode (offline, best-effort):
    python scripts/odoo/extract_settings_catalog.py --source-scan

    # Custom output path:
    python scripts/odoo/extract_settings_catalog.py --output /tmp/catalog.yaml

    # Dry-run (print to stdout, don't write):
    python scripts/odoo/extract_settings_catalog.py --dry-run

Exit codes:
    0 = catalog written successfully
    1 = error (auth, connection, parse failure)
"""
from __future__ import annotations

import argparse
import ast
import datetime
import os
import re
import sys
import xmlrpc.client
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(1)


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_OUTPUT = REPO_ROOT / "ssot" / "odoo" / "settings_catalog.yaml"

# ── YAML formatting helpers ──────────────────────────────────────────────

# Custom YAML representer for clean output
class CleanDumper(yaml.SafeDumper):
    """Dumper that produces clean, readable YAML."""
    pass


def _str_representer(dumper, data):
    if "\n" in data:
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)


def _none_representer(dumper, _data):
    return dumper.represent_scalar("tag:yaml.org,2002:null", "null")


CleanDumper.add_representer(str, _str_representer)
CleanDumper.add_representer(type(None), _none_representer)


# ── Mechanism classification ─────────────────────────────────────────────

MECHANISM_MODULE = "module_install"
MECHANISM_GROUP = "group_toggle"
MECHANISM_CONFIG = "config_parameter"
MECHANISM_RELATED = "related"
MECHANISM_COMPUTED = "computed"
MECHANISM_DEFAULT = "default"


def classify_field_name(name: str) -> str | None:
    """Classify mechanism from field name prefix convention."""
    if name.startswith("module_"):
        return MECHANISM_MODULE
    if name.startswith("group_"):
        return MECHANISM_GROUP
    return None


# ── XML-RPC extraction ───────────────────────────────────────────────────

def connect_xmlrpc(url: str, db: str, login: str, password: str):
    """Connect to Odoo via XML-RPC and return (uid, models proxy, version)."""
    common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
    try:
        version_info = common.version()
    except Exception as e:
        print(f"ERROR: Cannot reach {url}: {e}", file=sys.stderr)
        sys.exit(1)

    uid = common.authenticate(db, login, password, {})
    if not uid:
        print("ERROR: Odoo authentication failed", file=sys.stderr)
        sys.exit(1)

    models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")
    server_version = version_info.get("server_version", "unknown")
    return uid, models, server_version


def extract_via_xmlrpc(url: str, db: str, login: str, password: str) -> dict:
    """Extract settings catalog from live Odoo via XML-RPC."""
    uid, models, server_version = connect_xmlrpc(url, db, login, password)

    # Fetch all fields on res.config.settings from ir.model.fields
    fields_data = models.execute_kw(
        db, uid, password,
        "ir.model.fields", "search_read",
        [[["model", "=", "res.config.settings"]]],
        {
            "fields": [
                "name", "field_description", "ttype", "help",
                "related", "modules",
            ],
            "order": "name asc",
        },
    )

    # Fetch config parameters that reference res.config.settings fields
    # ir.config_parameter doesn't store the field link directly,
    # so we'll detect config_parameter from field attributes
    # In Odoo, config_parameter is a Python attribute, not in ir.model.fields.
    # We read it from the model's fields_get() which returns Python-level metadata.
    fields_get = models.execute_kw(
        db, uid, password,
        "res.config.settings", "fields_get",
        [],
        {"attributes": ["string", "type", "help", "related", "config_parameter"]},
    )

    # Group by declaring module
    modules_map: dict[str, list[dict]] = {}

    for fname, fmeta in sorted(fields_get.items()):
        # Skip internal / ORM fields
        if fname.startswith("__") or fname in (
            "id", "create_uid", "create_date", "write_uid", "write_date",
            "display_name",
        ):
            continue

        ttype = fmeta.get("type", "")
        string = fmeta.get("string", "")
        help_text = fmeta.get("help", "") or ""
        related_field = fmeta.get("related", "")
        config_param = fmeta.get("config_parameter", "")

        # Determine mechanism
        mechanism = classify_field_name(fname)
        if not mechanism:
            if config_param:
                mechanism = MECHANISM_CONFIG
            elif related_field:
                mechanism = MECHANISM_RELATED
            else:
                mechanism = MECHANISM_COMPUTED

        # Find declaring module from ir.model.fields data
        ir_field = next((f for f in fields_data if f["name"] == fname), None)
        declaring_module = "base"
        if ir_field and ir_field.get("modules"):
            # modules is a comma-separated string of module names
            mod_str = ir_field["modules"]
            mods = [m.strip() for m in mod_str.split(",") if m.strip()]
            if mods:
                declaring_module = mods[0]

        # Build field entry
        entry: dict = {
            "name": fname,
            "ttype": ttype,
            "string": string,
            "mechanism": mechanism,
        }

        if mechanism == MECHANISM_CONFIG and config_param:
            entry["config_parameter"] = config_param
        elif mechanism == MECHANISM_MODULE:
            entry["depends_module"] = fname.removeprefix("module_")
        elif mechanism == MECHANISM_GROUP:
            # implied_group is not exposed via fields_get; leave as name-derived
            pass
        elif mechanism == MECHANISM_RELATED and related_field:
            entry["related"] = related_field

        if help_text.strip():
            entry["help"] = help_text.strip()

        modules_map.setdefault(declaring_module, []).append(entry)

    # Build sorted module list
    modules_list = []
    for mod_name in sorted(modules_map.keys()):
        fields_sorted = sorted(modules_map[mod_name], key=lambda f: f["name"])
        modules_list.append({
            "module": mod_name,
            "fields": fields_sorted,
        })

    return {
        "method": "xmlrpc",
        "runtime_identity": f"odoo-{server_version}",
        "odoo_git_ref": server_version,
        "modules": modules_list,
        "field_count": sum(len(m["fields"]) for m in modules_list),
        "module_count": len(modules_list),
    }


# ── Source-scan extraction (offline, best-effort) ────────────────────────

# Regex patterns for field declarations in res_config_settings.py
FIELD_PATTERN = re.compile(
    r"^\s+(\w+)\s*=\s*fields\.(Boolean|Char|Text|Html|Integer|Float|"
    r"Monetary|Date|Datetime|Selection|Many2one|Many2many|One2many|Binary|Image)"
    r"\s*\(",
    re.MULTILINE,
)
CONFIG_PARAM_PATTERN = re.compile(r"""config_parameter\s*=\s*['"]([^'"]+)['"]""")
IMPLIED_GROUP_PATTERN = re.compile(r"""implied_group\s*=\s*['"]([^'"]+)['"]""")
RELATED_PATTERN = re.compile(r"""related\s*=\s*['"]([^'"]+)['"]""")
STRING_PATTERN = re.compile(r"""string\s*=\s*['"]([^'"]+)['"]""")


def extract_via_source_scan(addons_paths: list[Path] | None = None) -> dict:
    """Scan addons source for res_config_settings.py files."""
    if addons_paths is None:
        addons_paths = [
            REPO_ROOT / "addons" / "odoo",
            REPO_ROOT / "addons" / "oca",
            REPO_ROOT / "addons" / "ipai",
        ]

    modules_map: dict[str, list[dict]] = {}
    scanned_files = 0

    for addons_dir in addons_paths:
        if not addons_dir.exists():
            continue
        for settings_file in sorted(addons_dir.rglob("models/res_config_settings.py")):
            scanned_files += 1
            module_dir = settings_file.parent.parent
            module_name = module_dir.name

            try:
                source = settings_file.read_text(encoding="utf-8")
            except Exception:
                continue

            fields_list = _parse_settings_source(source, module_name)
            if fields_list:
                modules_map[module_name] = fields_list

    modules_list = []
    for mod_name in sorted(modules_map.keys()):
        fields_sorted = sorted(modules_map[mod_name], key=lambda f: f["name"])
        modules_list.append({
            "module": mod_name,
            "fields": fields_sorted,
        })

    return {
        "method": "source_scan",
        "runtime_identity": None,
        "odoo_git_ref": None,
        "modules": modules_list,
        "field_count": sum(len(m["fields"]) for m in modules_list),
        "module_count": len(modules_list),
        "scanned_files": scanned_files,
    }


def _parse_settings_source(source: str, module_name: str) -> list[dict]:
    """Parse a res_config_settings.py source file for field declarations."""
    fields = []

    for match in FIELD_PATTERN.finditer(source):
        fname = match.group(1)
        ftype = match.group(2).lower()

        # Map Odoo field class names to ttype strings
        ttype_map = {
            "boolean": "boolean", "char": "char", "text": "text",
            "html": "html", "integer": "integer", "float": "float",
            "monetary": "monetary", "date": "date", "datetime": "datetime",
            "selection": "selection", "many2one": "many2one",
            "many2many": "many2many", "one2many": "one2many",
            "binary": "binary", "image": "binary",
        }
        ttype = ttype_map.get(ftype, ftype)

        # Extract the full field definition (find matching paren)
        start = match.start()
        paren_start = source.index("(", start)
        depth = 1
        pos = paren_start + 1
        while pos < len(source) and depth > 0:
            if source[pos] == "(":
                depth += 1
            elif source[pos] == ")":
                depth -= 1
            pos += 1
        field_def = source[paren_start:pos]

        # Classify mechanism
        mechanism = classify_field_name(fname)
        config_param = ""
        implied_group = ""
        related = ""
        string_label = ""

        cp_match = CONFIG_PARAM_PATTERN.search(field_def)
        if cp_match:
            config_param = cp_match.group(1)

        ig_match = IMPLIED_GROUP_PATTERN.search(field_def)
        if ig_match:
            implied_group = ig_match.group(1)

        rel_match = RELATED_PATTERN.search(field_def)
        if rel_match:
            related = rel_match.group(1)

        str_match = STRING_PATTERN.search(field_def)
        if str_match:
            string_label = str_match.group(1)

        if not mechanism:
            if config_param:
                mechanism = MECHANISM_CONFIG
            elif related:
                mechanism = MECHANISM_RELATED
            elif ig_match:
                mechanism = MECHANISM_GROUP
            else:
                mechanism = MECHANISM_COMPUTED

        entry: dict = {
            "name": fname,
            "ttype": ttype,
            "string": string_label or fname,
            "mechanism": mechanism,
        }

        if mechanism == MECHANISM_CONFIG and config_param:
            entry["config_parameter"] = config_param
        elif mechanism == MECHANISM_MODULE:
            entry["depends_module"] = fname.removeprefix("module_")
        elif mechanism == MECHANISM_GROUP and implied_group:
            entry["implied_group"] = implied_group
        elif mechanism == MECHANISM_RELATED and related:
            entry["related"] = related

        fields.append(entry)

    return fields


# ── Output assembly ──────────────────────────────────────────────────────

HEADER = """\
# ssot/odoo/settings_catalog.yaml
#
# Odoo 19 CE res.config.settings field catalog — runtime-derived SSOT.
#
# Schema: ssot.odoo.settings_catalog.v1
# Validator: scripts/ci/check_settings_catalog.py
# Generator: scripts/odoo/extract_settings_catalog.py
#
# DO NOT EDIT DIRECTLY — regenerate from a running Odoo 19 CE instance.
#
"""


def build_catalog(extraction: dict) -> dict:
    """Assemble the full catalog document."""
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    return {
        "schema": "ssot.odoo.settings_catalog.v1",
        "version": "1.0",
        "odoo_version": "19.0",
        "edition": "CE",
        "extraction": {
            "method": extraction["method"],
            "extracted_at": now,
            "runtime_identity": extraction.get("runtime_identity"),
            "odoo_git_ref": extraction.get("odoo_git_ref"),
            "field_count": extraction["field_count"],
            "module_count": extraction["module_count"],
        },
        "modules": extraction["modules"],
    }


def write_catalog(catalog: dict, output: Path) -> None:
    """Write catalog to YAML file with header comment."""
    body = yaml.dump(
        catalog,
        Dumper=CleanDumper,
        default_flow_style=False,
        sort_keys=False,
        allow_unicode=True,
        width=120,
    )
    output.write_text(HEADER + body, encoding="utf-8")


# ── Main ─────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract Odoo 19 CE settings catalog"
    )
    parser.add_argument(
        "--output", "-o",
        default=str(DEFAULT_OUTPUT),
        help=f"Output file path (default: {DEFAULT_OUTPUT.relative_to(REPO_ROOT)})",
    )
    parser.add_argument(
        "--source-scan",
        action="store_true",
        help="Use offline source-scan mode instead of XML-RPC",
    )
    parser.add_argument(
        "--addons-path",
        action="append",
        help="Additional addons path to scan (source-scan mode only)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print catalog to stdout without writing",
    )
    args = parser.parse_args()

    if args.source_scan:
        print("Mode: source-scan (offline, best-effort)")
        addons_paths = None
        if args.addons_path:
            addons_paths = [Path(p).resolve() for p in args.addons_path]
        extraction = extract_via_source_scan(addons_paths)
        print(
            f"Scanned {extraction.get('scanned_files', 0)} settings files, "
            f"found {extraction['field_count']} fields in "
            f"{extraction['module_count']} modules"
        )
    else:
        url = os.environ.get("ODOO_URL", "").rstrip("/")
        db = os.environ.get("ODOO_DB", "")
        login = os.environ.get("ODOO_ADMIN_LOGIN", "admin")
        password = os.environ.get("ODOO_ADMIN_PASSWORD", "")

        for name, val in [
            ("ODOO_URL", url), ("ODOO_DB", db), ("ODOO_ADMIN_PASSWORD", password),
        ]:
            if not val:
                print(f"ERROR: {name} is required for XML-RPC mode", file=sys.stderr)
                print("Hint: use --source-scan for offline extraction", file=sys.stderr)
                sys.exit(1)

        print(f"Mode: XML-RPC ({url}, db={db})")
        extraction = extract_via_xmlrpc(url, db, login, password)
        print(
            f"Extracted {extraction['field_count']} fields in "
            f"{extraction['module_count']} modules from "
            f"{extraction['runtime_identity']}"
        )

    catalog = build_catalog(extraction)

    if args.dry_run:
        body = yaml.dump(
            catalog, Dumper=CleanDumper, default_flow_style=False,
            sort_keys=False, allow_unicode=True, width=120,
        )
        print(HEADER + body)
    else:
        output = Path(args.output)
        write_catalog(catalog, output)
        print(f"Catalog written to: {output}")


if __name__ == "__main__":
    main()
