"""Smoke tests: OCA external Python dependencies must be importable.

Run:  pytest tests/smoke/test_python_deps.py -v
CI:   Called by the smoke-test job in .github/workflows/oca-deps-smoke.yml

If this test fails in CI it means requirements-oca.txt is not wired into
the Dockerfile (or the constraints version was yanked from PyPI).
"""

import importlib

import pytest

# (import_name, pip_package_name, requiring_odoo_module)
OCA_DEPS = [
    ("odoorpc", "odoorpc", "upgrade_analysis"),
    ("openupgradelib", "openupgradelib", "upgrade_analysis"),
]


@pytest.mark.parametrize("import_name,package_name,required_by", OCA_DEPS)
def test_oca_dep_importable(import_name: str, package_name: str, required_by: str) -> None:
    """Verify each OCA external dep can be imported."""
    try:
        mod = importlib.import_module(import_name)
    except ImportError as exc:
        pytest.fail(
            f"{package_name} is not importable (required by Odoo module '{required_by}'). "
            f"Install it via: pip install -c requirements-constraints.txt -r requirements-oca.txt\n"
            f"Original error: {exc}"
        )
    assert mod is not None
