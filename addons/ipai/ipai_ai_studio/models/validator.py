# -*- coding: utf-8 -*-
"""
Static validator for generated Odoo addons.

Performs strict validation to prevent UI breakage:
- Required files exist
- Python compiles without errors
- XML parses correctly
"""
import compileall
import glob
import os
from xml.etree import ElementTree as ET


def validate_generated_addon(addon_path: str):
    """
    Strict static validation:
    - required files exist
    - python compileall ok
    - xml parses
    Returns (ok: bool, report: str)
    """
    rep = []
    ok = True

    def fail(msg):
        nonlocal ok
        ok = False
        rep.append("FAIL: " + msg)

    def info(msg):
        rep.append("OK: " + msg)

    # Required files
    req = ["__manifest__.py", "__init__.py", "models/__init__.py", "models/models.py"]
    for r in req:
        p = os.path.join(addon_path, r)
        if not os.path.isfile(p):
            fail(f"Missing required file: {r}")
        else:
            info(f"Found {r}")

    # Compile python
    try:
        c_ok = compileall.compile_dir(addon_path, quiet=1)
        if not c_ok:
            fail("compileall reported failures")
        else:
            info("compileall passed")
    except Exception as e:
        fail("compileall exception: " + str(e))

    # Parse XML
    xmls = glob.glob(os.path.join(addon_path, "**/*.xml"), recursive=True)
    bad = []
    for x in xmls:
        try:
            ET.parse(x)
        except Exception as e:
            bad.append((x, str(e)))
    if bad:
        for x, e in bad[:50]:
            fail(f"XML parse error: {x}: {e}")
    else:
        info(f"XML parse OK ({len(xmls)} files)")

    # Check manifest can be evaluated
    manifest_path = os.path.join(addon_path, "__manifest__.py")
    if os.path.isfile(manifest_path):
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                content = f.read()
            manifest_dict = eval(content)
            if not isinstance(manifest_dict, dict):
                fail("__manifest__.py does not evaluate to a dict")
            elif "name" not in manifest_dict:
                fail("__manifest__.py missing 'name' key")
            else:
                info("__manifest__.py is valid")
        except Exception as e:
            fail(f"__manifest__.py eval error: {e}")

    # Check CSV files for proper format
    csvs = glob.glob(os.path.join(addon_path, "**/*.csv"), recursive=True)
    for csv_path in csvs:
        try:
            with open(csv_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            if lines:
                header = lines[0].strip().split(",")
                if "id" not in header:
                    fail(
                        f"CSV {os.path.basename(csv_path)}: missing 'id' column in header"
                    )
                else:
                    info(f"CSV {os.path.basename(csv_path)} format OK")
        except Exception as e:
            fail(f"CSV {os.path.basename(csv_path)} error: {e}")

    return ok, "\n".join(rep)
