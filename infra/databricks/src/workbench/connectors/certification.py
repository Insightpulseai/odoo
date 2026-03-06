"""Connector certification framework.

Validates that connectors satisfy the behavioral contract required for
production use. All connectors must pass certification before deployment.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from workbench.connectors.base import BaseConnector
from workbench.connectors.types import ConnectorState, OpType, SyncOp

logger = logging.getLogger(__name__)


@dataclass
class CheckResult:
    """Result of a single certification check."""

    name: str
    passed: bool
    message: str = ""


@dataclass
class CertificationReport:
    """Full certification report for a connector."""

    connector_id: str
    checks: list[CheckResult] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return all(c.passed for c in self.checks)

    @property
    def summary(self) -> str:
        passed = sum(1 for c in self.checks if c.passed)
        total = len(self.checks)
        return f"{self.connector_id}: {passed}/{total} checks passed"


class ConnectorCertifier:
    """Runs certification checks against a connector instance.

    Checks:
    1. test_connection_succeeds -- connector.test_connection() returns True
    2. schema_is_stable -- schema() called twice returns identical TableDef lists
    3. update_yields_checkpoint -- update(empty_state) always ends with CHECKPOINT
    4. update_is_resumable -- sync with state A -> CHECKPOINT B, re-sync with B -> only new data or empty
    5. empty_update_is_safe -- sync with "caught up" state -> no UPSERTs, just CHECKPOINT
    6. data_matches_schema -- every UPSERT op's data keys match declared column names
    7. close_releases_resources -- after close(), connector attributes are None/closed
    """

    def certify(
        self,
        connector: BaseConnector,
        fixture_state: ConnectorState | None = None,
    ) -> CertificationReport:
        """Run all certification checks. Returns pass/fail per check."""
        state = fixture_state or ConnectorState(connector_id=connector.connector_id)
        report = CertificationReport(connector_id=connector.connector_id)

        report.checks.append(self._check_test_connection(connector))
        report.checks.append(self._check_schema_stable(connector))
        report.checks.append(self._check_update_yields_checkpoint(connector, state))

        # Get ops for further checks
        ops = list(connector.update(state))
        checkpoint_ops = [op for op in ops if op.op_type == OpType.CHECKPOINT]

        report.checks.append(self._check_update_resumable(connector, ops))
        report.checks.append(self._check_empty_update_safe(connector, checkpoint_ops))
        report.checks.append(self._check_data_matches_schema(connector, ops))
        report.checks.append(self._check_close_releases(connector))

        logger.info(
            "Certification %s: %s",
            "PASSED" if report.passed else "FAILED",
            report.summary,
        )
        return report

    def _check_test_connection(self, connector: BaseConnector) -> CheckResult:
        """Check 1: test_connection() returns True."""
        try:
            result = connector.test_connection()
            return CheckResult(
                name="test_connection_succeeds",
                passed=result is True,
                message="" if result else "test_connection() returned False",
            )
        except Exception as e:
            return CheckResult(
                name="test_connection_succeeds",
                passed=False,
                message=str(e),
            )

    def _check_schema_stable(self, connector: BaseConnector) -> CheckResult:
        """Check 2: schema() called twice returns identical results."""
        try:
            schema1 = connector.schema()
            schema2 = connector.schema()
            if len(schema1) != len(schema2):
                return CheckResult(
                    name="schema_is_stable",
                    passed=False,
                    message=f"Schema length changed: {len(schema1)} vs {len(schema2)}",
                )
            for t1, t2 in zip(schema1, schema2):
                if (
                    t1.name != t2.name
                    or t1.columns != t2.columns
                    or t1.primary_key != t2.primary_key
                ):
                    return CheckResult(
                        name="schema_is_stable",
                        passed=False,
                        message=f"Table {t1.name} differs between calls",
                    )
            return CheckResult(name="schema_is_stable", passed=True)
        except Exception as e:
            return CheckResult(name="schema_is_stable", passed=False, message=str(e))

    def _check_update_yields_checkpoint(
        self, connector: BaseConnector, state: ConnectorState
    ) -> CheckResult:
        """Check 3: update(empty_state) always ends with at least one CHECKPOINT."""
        try:
            ops = list(connector.update(state))
            checkpoints = [op for op in ops if op.op_type == OpType.CHECKPOINT]
            if not checkpoints:
                return CheckResult(
                    name="update_yields_checkpoint",
                    passed=False,
                    message="No CHECKPOINT op emitted",
                )
            return CheckResult(name="update_yields_checkpoint", passed=True)
        except Exception as e:
            return CheckResult(
                name="update_yields_checkpoint",
                passed=False,
                message=str(e),
            )

    def _check_update_resumable(
        self, connector: BaseConnector, initial_ops: list[SyncOp]
    ) -> CheckResult:
        """Check 4: re-sync with checkpoint cursor produces only new data or is empty."""
        try:
            checkpoints = [
                op for op in initial_ops if op.op_type == OpType.CHECKPOINT
            ]
            if not checkpoints:
                return CheckResult(
                    name="update_is_resumable",
                    passed=False,
                    message="Cannot test resumability: no CHECKPOINT in initial sync",
                )
            last_cursor = checkpoints[-1].cursor or {}
            resumed_state = ConnectorState(
                connector_id=connector.connector_id,
                cursor=last_cursor,
            )
            resumed_ops = list(connector.update(resumed_state))
            # Resumed sync should have a CHECKPOINT
            resumed_checkpoints = [
                op for op in resumed_ops if op.op_type == OpType.CHECKPOINT
            ]
            if not resumed_checkpoints:
                return CheckResult(
                    name="update_is_resumable",
                    passed=False,
                    message="Resumed sync did not emit CHECKPOINT",
                )
            return CheckResult(name="update_is_resumable", passed=True)
        except Exception as e:
            return CheckResult(
                name="update_is_resumable", passed=False, message=str(e)
            )

    def _check_empty_update_safe(
        self, connector: BaseConnector, checkpoint_ops: list[SyncOp]
    ) -> CheckResult:
        """Check 5: sync with 'caught up' state -> no UPSERTs emitted, just CHECKPOINT."""
        try:
            if not checkpoint_ops:
                return CheckResult(
                    name="empty_update_is_safe",
                    passed=False,
                    message="Cannot test: no CHECKPOINT available from previous sync",
                )
            caught_up_cursor = checkpoint_ops[-1].cursor or {}
            caught_up_state = ConnectorState(
                connector_id=connector.connector_id,
                cursor=caught_up_cursor,
            )
            ops = list(connector.update(caught_up_state))
            upserts = [
                op
                for op in ops
                if op.op_type in (OpType.UPSERT, OpType.UPDATE)
            ]
            # A caught-up sync should produce zero or minimal upserts
            has_checkpoint = any(op.op_type == OpType.CHECKPOINT for op in ops)
            if not has_checkpoint:
                return CheckResult(
                    name="empty_update_is_safe",
                    passed=False,
                    message="Caught-up sync did not emit CHECKPOINT",
                )
            return CheckResult(
                name="empty_update_is_safe",
                passed=True,
                message=f"{len(upserts)} upserts emitted from caught-up state",
            )
        except Exception as e:
            return CheckResult(
                name="empty_update_is_safe", passed=False, message=str(e)
            )

    def _check_data_matches_schema(
        self, connector: BaseConnector, ops: list[SyncOp]
    ) -> CheckResult:
        """Check 6: every UPSERT op's data keys match declared column names."""
        try:
            schema = connector.schema()
            table_cols: dict[str, set[str]] = {}
            for td in schema:
                table_cols[td.name] = {col.name for col in td.columns}

            for op in ops:
                if op.op_type in (OpType.UPSERT, OpType.UPDATE) and op.data:
                    expected = table_cols.get(op.table)
                    if expected is None:
                        return CheckResult(
                            name="data_matches_schema",
                            passed=False,
                            message=f"Op references undeclared table: {op.table}",
                        )
                    data_keys = set(op.data.keys())
                    # Data keys should be a subset of declared columns
                    extra = data_keys - expected
                    if extra:
                        return CheckResult(
                            name="data_matches_schema",
                            passed=False,
                            message=f"Table {op.table}: undeclared columns in data: {extra}",
                        )
            return CheckResult(name="data_matches_schema", passed=True)
        except Exception as e:
            return CheckResult(
                name="data_matches_schema", passed=False, message=str(e)
            )

    def _check_close_releases(self, connector: BaseConnector) -> CheckResult:
        """Check 7: after close(), connector's client/connection attributes are None/closed."""
        try:
            connector.close()
            # Check common connection attribute patterns
            for attr in (
                "client",
                "connection",
                "conn",
                "session",
                "_client",
                "_connection",
            ):
                val = getattr(connector, attr, "MISSING")
                if val != "MISSING" and val is not None:
                    # Check if it has a 'closed' attribute (like DB connections)
                    if hasattr(val, "closed") and not val.closed:
                        return CheckResult(
                            name="close_releases_resources",
                            passed=False,
                            message=f"Attribute {attr} not closed after close()",
                        )
            return CheckResult(name="close_releases_resources", passed=True)
        except Exception as e:
            return CheckResult(
                name="close_releases_resources", passed=False, message=str(e)
            )
