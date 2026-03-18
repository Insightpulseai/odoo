#!/usr/bin/env python3
"""
Odoo-aware CI Gate
Enforces module policies: manifest, license, security, SSOT inclusion.
"""
import json
import os
import re
import sys
from pathlib import Path
from typing import Optional


def load_yaml(path: Path) -> dict:
    """Load YAML file."""
    try:
        import yaml
        return yaml.safe_load(path.read_text("utf-8")) or {}
    except Exception:
        return {}


def read_text(p: Path) -> str:
    """Read file as text with error handling."""
    return p.read_text("utf-8", errors="replace")


def has_models(py_text: str) -> bool:
    """Check if Python file defines Odoo models."""
    return bool(re.search(r"class\s+\w+\(models\.Model\)", py_text))


def find_security_files(module_path: Path) -> list[Path]:
    """Find security-related files in module."""
    hits = []
    for rel in [
        "security/ir.model.access.csv",
        "security/security.xml",
        "security/ir.rules.xml",
    ]:
        path = module_path / rel
        if path.exists():
            hits.append(path)

    # Also check security directory
    sec_dir = module_path / "security"
    if sec_dir.is_dir():
        hits.extend(sec_dir.glob("*.csv"))
        hits.extend(sec_dir.glob("*.xml"))

    return hits


def find_controllers(module_path: Path) -> list[Path]:
    """Find controller files in module."""
    results = []
    for pattern in ["controllers/*.py", "controller/*.py"]:
        results.extend(module_path.glob(pattern))
    return [p for p in results if p.name != "__init__.py"]


def parse_manifest(manifest_path: Path) -> dict:
    """
    Parse Odoo manifest file.
    Returns dict with manifest data.
    """
    src = read_text(manifest_path)

    # Try direct eval (manifest is typically a dict literal)
    try:
        # Find the dict literal
        match = re.search(r"^(\{[\s\S]*\})\s*$", src, re.MULTILINE)
        if match:
            return eval(match.group(1), {"__builtins__": {}}, {})
    except Exception:
        pass

    # Fallback: try to extract using ast
    try:
        import ast
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.Dict):
                result = {}
                for key, value in zip(node.keys, node.values):
                    if isinstance(key, ast.Constant):
                        try:
                            result[key.value] = ast.literal_eval(
                                ast.unparse(value)
                            )
                        except Exception:
                            result[key.value] = None
                if "name" in result:
                    return result
    except Exception:
        pass

    raise ValueError("Unable to parse manifest")


def match_pattern(name: str, patterns: list[str]) -> bool:
    """Check if name matches any wildcard pattern."""
    for pattern in patterns:
        regex = "^" + pattern.replace("*", ".*") + "$"
        if re.match(regex, name):
            return True
    return False


def get_tier_checks(name: str, policy: dict) -> Optional[dict]:
    """Get tier-specific checks for a module."""
    tiers = policy.get("tiers", {})
    for tier_name, tier_config in tiers.items():
        patterns = tier_config.get("patterns", [])
        if match_pattern(name, patterns):
            return tier_config.get("checks", {})
    return None


def main():
    root = Path(os.environ.get("GITHUB_WORKSPACE", Path.cwd()))
    policy = load_yaml(root / "config/odoo/ci_policy.yml")
    desired_path = root / "config/odoo/desired_modules.yml"
    desired = load_yaml(desired_path) if desired_path.exists() else {}
    desired_mods = set(desired.get("modules") or [])

    # Get changed modules from environment
    changed_json = os.environ.get("ODOO_CHANGED_MODULES_JSON", "")
    if not changed_json:
        print("No changed modules detected; gate passes.")
        return

    try:
        changed = json.loads(changed_json)
    except json.JSONDecodeError:
        print("Invalid ODOO_CHANGED_MODULES_JSON; gate passes.")
        return

    if not changed:
        print("No changed modules detected; gate passes.")
        return

    # Get policy checks
    checks = policy.get("checks", {})
    forbid_controllers = bool(checks.get("forbid_http_controllers_default", False))
    require_security_if_models = bool(checks.get("require_security_if_models", True))
    require_manifest = bool(checks.get("require_manifest", True))
    require_license = bool(checks.get("require_license_agpl3_or_lgpl3", True))

    # Get exempt patterns
    exempt = policy.get("desired_modules_exempt", [])

    errors = []
    warnings = []

    for m in changed:
        name = m["name"]
        path = root / m["path"]

        # Get tier-specific checks (override defaults)
        tier_checks = get_tier_checks(name, policy)
        if tier_checks:
            local_checks = {**checks, **tier_checks}
        else:
            local_checks = checks

        # Find manifest
        manifest = path / "__manifest__.py"
        legacy = path / "__openerp__.py"
        manifest_path = manifest if manifest.exists() else (
            legacy if legacy.exists() else None
        )

        if require_manifest and not manifest_path:
            errors.append(f"{name}: missing __manifest__.py")
            continue

        # Parse manifest
        manifest_dict = {}
        if manifest_path:
            try:
                manifest_dict = parse_manifest(manifest_path)
            except Exception as e:
                errors.append(f"{name}: cannot parse manifest: {e}")
                continue

        # License check
        if local_checks.get("require_license_agpl3_or_lgpl3", require_license):
            lic = (manifest_dict.get("license") or "").strip()
            allowed = ["AGPL-3", "LGPL-3", "OEEL-1", "GPL-3"]
            if lic not in allowed:
                errors.append(
                    f"{name}: license '{lic}' not allowed "
                    f"(expected one of: {', '.join(allowed)})"
                )

        # SSOT check: module must be in desired_modules.yml
        if not match_pattern(name, exempt):
            if name not in desired_mods:
                errors.append(
                    f"{name}: changed but not in config/odoo/desired_modules.yml. "
                    "Add it to the SSOT list or add an exemption."
                )

        # Controllers check
        if local_checks.get("forbid_http_controllers_default", forbid_controllers):
            ctrls = find_controllers(path)
            if ctrls:
                ctrl_names = [str(c.relative_to(root)) for c in ctrls[:3]]
                warnings.append(
                    f"{name}: HTTP controllers detected: {', '.join(ctrl_names)}"
                )

        # Security check: if models exist, require security files
        if local_checks.get("require_security_if_models", require_security_if_models):
            py_files = list(path.rglob("*.py"))
            has_any_model = any(has_models(read_text(p)) for p in py_files)
            if has_any_model:
                sec_files = find_security_files(path)
                if not sec_files:
                    errors.append(
                        f"{name}: models detected but no security files "
                        "(expected security/ir.model.access.csv)"
                    )

    # Report results
    if warnings:
        print("Warnings:")
        for w in warnings:
            print(f"  ⚠ {w}")
        print()

    if errors:
        print("Errors (blocking):")
        for e in errors:
            print(f"  ✗ {e}")
        print()
        print("Odoo-aware CI gate FAILED")
        sys.exit(2)

    print(f"✓ Checked {len(changed)} module(s)")
    print("Odoo-aware CI gate PASSED")


if __name__ == "__main__":
    main()
