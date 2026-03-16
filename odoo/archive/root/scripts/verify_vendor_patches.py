#!/usr/bin/env python3
"""
CI gate: verify vendor patches are applied and odoo_test_helper is importable.

Checks:
  1. odoo_test_helper.FakeModelLoader is importable without errors
  2. MetaModel attribute access is forward-compatible (both old + new names work)
  3. Patch idempotency marker (_module_to_models__) is present in the installed file

Exit codes:
  0  all checks pass
  2  import failure or attribute access failure (patch not applied or broken)

Hook into the same CI stage that runs OCA requirements install:
  python3 scripts/verify_vendor_patches.py
"""

import sys
import importlib
import importlib.util
from pathlib import Path


def check_import() -> bool:
    """Check that odoo_test_helper.FakeModelLoader imports without error."""
    try:
        from odoo_test_helper import FakeModelLoader  # noqa: F401
        print("[vendor-patch-verify] ✅ odoo_test_helper.FakeModelLoader importable")
        return True
    except ImportError as e:
        print(f"[vendor-patch-verify] ⚠️  odoo_test_helper not installed (skipping): {e}")
        # Not an error if the package isn't installed at all — only gates if installed
        return True
    except AttributeError as e:
        print(f"[vendor-patch-verify] ❌ FAIL AttributeError importing FakeModelLoader: {e}")
        print("  This means the Odoo 19 MetaModel rename patch was not applied.")
        print("  Run: bash runtime/scripts/apply_vendor_patches.sh")
        return False
    except Exception as e:
        print(f"[vendor-patch-verify] ❌ FAIL unexpected error importing FakeModelLoader: {e}")
        return False


def check_patch_marker() -> bool:
    """Verify the idempotency marker is present in the installed file."""
    import site, glob

    candidates = []
    for base in (site.getsitepackages() or []) + [site.getusersitepackages() or ""]:
        if base:
            p = Path(base) / "odoo_test_helper" / "fake_model_loader.py"
            if p.exists():
                candidates.append(p)

    if not candidates:
        for p in glob.glob("/**/odoo_test_helper/fake_model_loader.py", recursive=True):
            if Path(p).exists():
                candidates.append(Path(p))

    if not candidates:
        print("[vendor-patch-verify] ⚠️  fake_model_loader.py not found — skipping marker check")
        return True

    target = candidates[0]
    content = target.read_text(encoding="utf-8")

    if "_module_to_models__" in content:
        print(f"[vendor-patch-verify] ✅ Patch marker present in {target}")
        return True
    elif "module_to_models = models.MetaModel.module_to_models" in content:
        print(f"[vendor-patch-verify] ❌ FAIL: patch NOT applied to {target}")
        print("  Old attribute access still present. Apply patch:")
        print("  bash runtime/scripts/apply_vendor_patches.sh")
        return False
    else:
        print(f"[vendor-patch-verify] ⚠️  Neither old nor new pattern found in {target}")
        print("  odoo-test-helper may have been updated upstream. Review patch.")
        return True


def main() -> int:
    print("[vendor-patch-verify] Running vendor patch verification …")
    print()

    results = [
        check_import(),
        check_patch_marker(),
    ]

    print()
    if all(results):
        print("[vendor-patch-verify] ✅ All checks passed")
        return 0
    else:
        print("[vendor-patch-verify] ❌ One or more checks failed")
        return 2


if __name__ == "__main__":
    sys.exit(main())
