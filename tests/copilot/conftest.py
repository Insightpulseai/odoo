# -*- coding: utf-8 -*-
"""Shared fixtures for copilot contract tests.

All fixtures are designed to work without Odoo runtime or Azure credentials.
They mock the minimal Odoo env surface needed by the code under test.
"""

import sys
import types
from unittest.mock import MagicMock

import pytest


# ---------------------------------------------------------------------------
# Odoo stub — allows importing copilot modules without real Odoo
# ---------------------------------------------------------------------------

def _install_odoo_stub():
    """Install a minimal Odoo stub into sys.modules so that
    `from odoo import ...` works for static analysis tests.

    This is idempotent — safe to call multiple times.
    """
    if "odoo" in sys.modules and not isinstance(sys.modules["odoo"], types.ModuleType):
        return  # real Odoo is loaded, do not overwrite

    # Only install if odoo is NOT available
    try:
        import odoo  # noqa: F401
        return  # real Odoo exists
    except ImportError:
        pass

    # Build minimal stub tree
    odoo_mod = types.ModuleType("odoo")
    odoo_mod._ = lambda *a, **kw: a[0] if a else ""
    odoo_mod.api = types.ModuleType("odoo.api")
    odoo_mod.api.depends = lambda *a: lambda fn: fn
    odoo_mod.api.model = lambda fn: fn
    odoo_mod.api.model_create_multi = lambda fn: fn

    odoo_mod.fields = types.ModuleType("odoo.fields")
    for ftype in ("Char", "Text", "Boolean", "Integer", "Float",
                   "Selection", "Many2one", "One2many", "Many2many",
                   "Datetime", "Date", "Html", "Binary"):
        setattr(odoo_mod.fields, ftype, lambda *a, **kw: None)
    odoo_mod.fields.Command = MagicMock()

    odoo_mod.models = types.ModuleType("odoo.models")

    class _StubModel:
        _name = None
        _description = ""
        _auto = True
        _order = "id"
        _rec_name = "name"
        _inherit = []
        _inherits = {}

        def __init_subclass__(cls, **kw):
            super().__init_subclass__(**kw)

    odoo_mod.models.Model = _StubModel
    odoo_mod.models.TransientModel = _StubModel
    odoo_mod.models.AbstractModel = _StubModel

    odoo_exceptions = types.ModuleType("odoo.exceptions")
    class _UserError(Exception):
        pass
    class _ValidationError(Exception):
        pass
    odoo_exceptions.UserError = _UserError
    odoo_exceptions.ValidationError = _ValidationError
    odoo_mod.exceptions = odoo_exceptions

    odoo_http = types.ModuleType("odoo.http")
    odoo_http.Controller = type("Controller", (), {})
    odoo_http.route = lambda *a, **kw: lambda fn: fn
    odoo_http.request = MagicMock()
    odoo_mod.http = odoo_http

    odoo_tools = types.ModuleType("odoo.tools")
    odoo_mod.tools = odoo_tools

    # Register stubs
    sys.modules["odoo"] = odoo_mod
    sys.modules["odoo.api"] = odoo_mod.api
    sys.modules["odoo.fields"] = odoo_mod.fields
    sys.modules["odoo.models"] = odoo_mod.models
    sys.modules["odoo.exceptions"] = odoo_exceptions
    sys.modules["odoo.http"] = odoo_http
    sys.modules["odoo.tools"] = odoo_tools

    # Addons stubs so that `from odoo.addons...` resolves
    odoo_addons = types.ModuleType("odoo.addons")
    sys.modules["odoo.addons"] = odoo_addons


# Install stub on import so all test modules can rely on it
_install_odoo_stub()


# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------

import os

REPO_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)
COPILOT_ADDON_PATH = os.path.join(
    REPO_ROOT, "addons", "ipai", "ipai_odoo_copilot"
)
BRIDGE_ADDON_PATH = os.path.join(
    REPO_ROOT, "addons", "ipai", "ipai_enterprise_bridge"
)


@pytest.fixture
def repo_root():
    return REPO_ROOT


@pytest.fixture
def copilot_addon_path():
    return COPILOT_ADDON_PATH


# ---------------------------------------------------------------------------
# Module import helpers
# ---------------------------------------------------------------------------

def _load_module_source(module_name, file_path):
    """Load a Python module from a file path.

    Uses an 'odoo.addons.' prefixed module name so that Odoo's
    Model metaclass accepts the class definition.
    """
    import importlib.util
    # Odoo's Model.__new__ asserts cls.__module__.startswith('odoo.addons.')
    # so we must fake the module name accordingly.
    qualified_name = "odoo.addons._test_." + module_name
    spec = importlib.util.spec_from_file_location(qualified_name, file_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# Module-level caches to avoid re-importing (Odoo metaclass does not like
# multiple registrations of the same _name in different modules).
_MODULE_CACHE = {}


def load_foundry_service():
    """Load foundry_service.py as a raw Python module (cached)."""
    key = "foundry_service"
    if key not in _MODULE_CACHE:
        path = os.path.join(COPILOT_ADDON_PATH, "models", "foundry_service.py")
        _MODULE_CACHE[key] = _load_module_source(key, path)
    return _MODULE_CACHE[key]


def load_tool_executor():
    """Load tool_executor.py as a raw Python module (cached)."""
    key = "tool_executor"
    if key not in _MODULE_CACHE:
        path = os.path.join(COPILOT_ADDON_PATH, "models", "tool_executor.py")
        _MODULE_CACHE[key] = _load_module_source(key, path)
    return _MODULE_CACHE[key]


def load_foundry_provider_config():
    """Load foundry_provider_config.py as a raw Python module (cached)."""
    key = "foundry_provider_config"
    if key not in _MODULE_CACHE:
        path = os.path.join(
            BRIDGE_ADDON_PATH, "models", "foundry_provider_config.py"
        )
        _MODULE_CACHE[key] = _load_module_source(key, path)
    return _MODULE_CACHE[key]


@pytest.fixture
def foundry_service_module():
    return load_foundry_service()


@pytest.fixture
def tool_executor_module():
    return load_tool_executor()


@pytest.fixture
def foundry_provider_config_module():
    return load_foundry_provider_config()


# ---------------------------------------------------------------------------
# Mock env and context fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_env():
    """Minimal mock Odoo env that supports self.env[model] lookups."""
    env = MagicMock()
    # Make env[model] return a mock recordset
    env.__getitem__ = MagicMock(side_effect=lambda model: MagicMock())
    env.__contains__ = MagicMock(return_value=True)
    env.uid = 1
    env.cr = MagicMock()
    return env


@pytest.fixture
def context_envelope():
    """Standard context envelope with all 11 tools permitted."""
    return {
        "permitted_tools": [
            "read_record",
            "search_records",
            "search_docs",
            "get_report",
            "read_finance_close",
            "view_campaign_perf",
            "view_dashboard",
            "search_strategy_docs",
            "search_odoo_docs",
            "search_azure_docs",
            "search_databricks_docs",
        ],
        "company_id": 1,
        "entity_ids": [1],
        "user_id": 1,
        "surface": "copilot",
        "source": "api",
        "mode": "read_only",
    }


@pytest.fixture
def mock_settings():
    """Default settings dict as returned by FoundryService._get_settings."""
    return {
        "enabled": True,
        "endpoint": "https://portal.azure.com/test",
        "api_endpoint": "https://test.services.ai.azure.com",
        "project": "test-project",
        "agent_name": "odoo-copilot",
        "model": "gpt-4o",
        "search_service": "test-search",
        "search_connection": "",
        "search_index": "odoo18-docs",
        "memory_enabled": False,
        "read_only_mode": True,
        "agent_api_mode": "agents",
    }


@pytest.fixture
def sample_search_results():
    """Sample search results matching the KB result schema."""
    return {
        "results": [
            {
                "title": "Sale Order Workflow",
                "content": "The sale order workflow in Odoo 18...",
                "score": 0.92,
                "path": "/developer/reference/backend/orm.html",
                "heading_chain": "ORM > CRUD > create",
            },
            {
                "title": "Invoice Creation",
                "content": "Invoices are created from confirmed sale orders...",
                "score": 0.87,
                "path": "/developer/reference/backend/actions.html",
                "heading_chain": "Actions > Server Actions",
            },
        ],
        "source": "odoo18-docs",
        "count": 2,
    }
