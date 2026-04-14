"""
agents/tests/test_payment_reconcile_workflow.py

Unit tests for Pulser Account Reconciliation Workflow.
D365 benchmark: Account Reconciliation Agent
Epic: #524 Finance Agents Parity

Tests run without real Azure credentials via unittest.mock stubs.
"""
import os
import sys
import types
import unittest
from unittest.mock import MagicMock, patch
import pytest


# ---------------------------------------------------------------------------
# Stub out heavy dependencies before import
# ---------------------------------------------------------------------------

def _make_agent_framework_stub():
    """Return a minimal agent_framework stub module tree."""
    af = types.ModuleType("agent_framework")
    af_foundry = types.ModuleType("agent_framework.foundry")
    af_workflows = types.ModuleType("agent_framework.workflows")

    class _Tool:
        """Minimal @tool decorator stub."""
        def __init__(self, func=None, *, approval_mode=None):
            self._approval_mode = approval_mode
            if func is not None:
                self._func = func
                self.__call__ = func
            else:
                self._func = None

        def __call__(self, func=None, **kwargs):
            if callable(func):
                # Called as @tool (no args)
                wrapped = _Tool.__new__(_Tool)
                wrapped._func = func
                wrapped._approval_mode = None
                wrapped.__call__ = func
                wrapped.__name__ = func.__name__
                wrapped.__doc__ = func.__doc__
                return wrapped
            # Called as @tool(approval_mode=...) — return decorator
            approval = kwargs.get("approval_mode", self._approval_mode)
            def decorator(f):
                wrapped = _Tool.__new__(_Tool)
                wrapped._func = f
                wrapped._approval_mode = approval
                wrapped.__call__ = f
                wrapped.__name__ = f.__name__
                wrapped.__doc__ = f.__doc__
                return wrapped
            return decorator

    tool_instance = _Tool()

    class _Agent:
        def __init__(self, **kwargs):
            self.name = kwargs.get("name", "")
            self.tools = kwargs.get("tools", [])

    class _FileCheckpointStorage:
        def __init__(self, storage_path=None):
            self.storage_path = storage_path

    class _HandoffBuilder:
        def __init__(self, **kwargs):
            self._kwargs = kwargs

        def with_start_agent(self, agent):
            self._start = agent
            return self

        def build(self):
            workflow = MagicMock()
            workflow.name = self._kwargs.get("name", "")
            return workflow

    af.tool = tool_instance
    af.Agent = _Agent
    af.FileCheckpointStorage = _FileCheckpointStorage

    af_foundry.FoundryChatClient = MagicMock(return_value=MagicMock())
    af_workflows.HandoffBuilder = _HandoffBuilder

    af.foundry = af_foundry
    af.workflows = af_workflows

    return af, af_foundry, af_workflows


def _make_azure_identity_stub():
    azure = types.ModuleType("azure")
    azure_identity = types.ModuleType("azure.identity")
    azure_identity.ManagedIdentityCredential = MagicMock(return_value=MagicMock())
    azure_identity.ChainedTokenCredential = MagicMock(return_value=MagicMock())
    azure.identity = azure_identity
    return azure, azure_identity


def _make_pydantic_stub():
    pydantic = types.ModuleType("pydantic")
    pydantic.Field = MagicMock(return_value=None)
    return pydantic


# Register stubs before the workflow module is imported
_af, _af_foundry, _af_workflows = _make_agent_framework_stub()
_azure, _azure_identity = _make_azure_identity_stub()
_pydantic = _make_pydantic_stub()

sys.modules.setdefault("agent_framework", _af)
sys.modules.setdefault("agent_framework.foundry", _af_foundry)
sys.modules.setdefault("agent_framework.workflows", _af_workflows)
sys.modules.setdefault("azure", _azure)
sys.modules.setdefault("azure.identity", _azure_identity)
sys.modules.setdefault("pydantic", _pydantic)


@pytest.fixture(scope="module", autouse=True)
def env_vars():
    """Inject required env vars so module-level code doesn't raise KeyError."""
    with patch.dict(os.environ, {
        "AZURE_CLIENT_ID": "test-client-id",
        "IPAI_FOUNDRY_ENDPOINT": "https://test.services.ai.azure.com/api/projects/test",
        "PULSER_CHECKPOINT_PATH": "/tmp/test-pulser-checkpoints",
    }):
        yield


# Import the module under test AFTER stubs and env vars are in place
@pytest.fixture(scope="module")
def workflow_module(env_vars):
    import importlib
    import agents.workflows.payment_reconcile_workflow as mod
    return mod


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestBuildReconWorkflow:
    """Smoke tests for build_reconcile_workflow factory."""

    def test_returns_workflow_object(self, workflow_module):
        wf = workflow_module.build_reconcile_workflow("dataverse_pasig", "2026-04")
        assert wf is not None

    def test_accepts_company_id_and_period(self, workflow_module):
        wf = workflow_module.build_reconcile_workflow("company_abc", "2026-03")
        assert wf is not None

    def test_workflow_name_includes_company_and_period(self, workflow_module):
        wf = workflow_module.build_reconcile_workflow("dataverse_pasig", "2026-05")
        assert hasattr(wf, "name")
        assert "dataverse_pasig" in wf.name
        assert "2026-05" in wf.name


@pytest.mark.unit
class TestReadOnlyToolSignatures:
    """Verify all read-only tools are callable with expected signatures."""

    def test_get_bank_statement_lines_callable(self, workflow_module):
        fn = workflow_module.get_bank_statement_lines
        assert callable(fn) or callable(getattr(fn, "__call__", None))

    def test_get_open_ar_lines_callable(self, workflow_module):
        fn = workflow_module.get_open_ar_lines
        assert callable(fn) or callable(getattr(fn, "__call__", None))

    def test_get_open_ap_lines_callable(self, workflow_module):
        fn = workflow_module.get_open_ap_lines
        assert callable(fn) or callable(getattr(fn, "__call__", None))

    def test_get_intercompany_transactions_callable(self, workflow_module):
        fn = workflow_module.get_intercompany_transactions
        assert callable(fn) or callable(getattr(fn, "__call__", None))

    def test_match_bank_line_to_move_callable(self, workflow_module):
        fn = workflow_module.match_bank_line_to_move
        assert callable(fn) or callable(getattr(fn, "__call__", None))

    def test_get_bank_statement_lines_accepts_company_and_period(self, workflow_module):
        import inspect
        fn = workflow_module.get_bank_statement_lines
        func = getattr(fn, "_func", fn)
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())
        assert "company_id" in params
        assert "period" in params

    def test_get_open_ar_lines_accepts_company_id(self, workflow_module):
        import inspect
        fn = workflow_module.get_open_ar_lines
        func = getattr(fn, "_func", fn)
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())
        assert "company_id" in params

    def test_get_intercompany_accepts_source_target_period(self, workflow_module):
        import inspect
        fn = workflow_module.get_intercompany_transactions
        func = getattr(fn, "_func", fn)
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())
        assert "source_company" in params
        assert "target_company" in params
        assert "period" in params


@pytest.mark.unit
class TestMutatingToolApprovalGuardrails:
    """Verify mutating tools carry approval_mode='always_require'."""

    def test_reconcile_bank_line_has_always_require(self, workflow_module):
        tool = workflow_module.reconcile_bank_line
        assert getattr(tool, "_approval_mode", None) == "always_require", (
            "reconcile_bank_line must declare approval_mode='always_require'"
        )

    def test_clear_intercompany_transaction_has_always_require(self, workflow_module):
        tool = workflow_module.clear_intercompany_transaction
        assert getattr(tool, "_approval_mode", None) == "always_require", (
            "clear_intercompany_transaction must declare approval_mode='always_require'"
        )

    def test_reconcile_bank_line_callable(self, workflow_module):
        fn = workflow_module.reconcile_bank_line
        assert callable(fn) or callable(getattr(fn, "__call__", None))

    def test_clear_intercompany_callable(self, workflow_module):
        fn = workflow_module.clear_intercompany_transaction
        assert callable(fn) or callable(getattr(fn, "__call__", None))

    def test_reconcile_bank_line_signature(self, workflow_module):
        import inspect
        fn = workflow_module.reconcile_bank_line
        func = getattr(fn, "_func", fn)
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())
        assert "bank_line_id" in params
        assert "move_line_id" in params

    def test_clear_intercompany_signature(self, workflow_module):
        import inspect
        fn = workflow_module.clear_intercompany_transaction
        func = getattr(fn, "_func", fn)
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())
        assert "source_company" in params
        assert "target_company" in params
        assert "invoice_id" in params
        assert "wht_amount" in params


@pytest.mark.unit
class TestReadOnlyToolsLackApprovalGuard:
    """Read-only tools must NOT have approval_mode set (safety net)."""

    def test_get_bank_statement_lines_no_approval(self, workflow_module):
        tool = workflow_module.get_bank_statement_lines
        mode = getattr(tool, "_approval_mode", None)
        assert mode != "always_require"

    def test_match_bank_line_to_move_no_approval(self, workflow_module):
        tool = workflow_module.match_bank_line_to_move
        mode = getattr(tool, "_approval_mode", None)
        assert mode != "always_require"
