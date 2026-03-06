"""Connector contract certification tests.

Parametrized across all registered connectors using fixture data.
"""

from __future__ import annotations

import pytest

from workbench.connectors.certification import ConnectorCertifier
from workbench.connectors.types import ConnectorState
from tests.fixtures.connector_fixtures import (
    CONNECTOR_FIXTURES,
    FixturedConnector,
    create_fixtured_connector,
)


CONNECTOR_IDS = list(CONNECTOR_FIXTURES.keys())


@pytest.fixture(params=CONNECTOR_IDS)
def fixtured_connector(request: pytest.FixtureRequest) -> FixturedConnector:
    """Parametrized fixture: creates a FixturedConnector for each connector_id."""
    return create_fixtured_connector(request.param)


class TestConnectorContract:
    """All registered connectors must pass the 7-check certification."""

    def test_full_certification(self, fixtured_connector: FixturedConnector) -> None:
        """Run full certification -- all 7 checks must pass."""
        certifier = ConnectorCertifier()
        report = certifier.certify(fixtured_connector)
        for check in report.checks:
            assert check.passed, (
                f"[{fixtured_connector.connector_id}] {check.name}: {check.message}"
            )
        assert report.passed

    def test_test_connection_succeeds(
        self, fixtured_connector: FixturedConnector
    ) -> None:
        certifier = ConnectorCertifier()
        check = certifier._check_test_connection(fixtured_connector)
        assert check.passed, check.message

    def test_schema_is_stable(
        self, fixtured_connector: FixturedConnector
    ) -> None:
        certifier = ConnectorCertifier()
        check = certifier._check_schema_stable(fixtured_connector)
        assert check.passed, check.message

    def test_update_yields_checkpoint(
        self, fixtured_connector: FixturedConnector
    ) -> None:
        state = ConnectorState(connector_id=fixtured_connector.connector_id)
        certifier = ConnectorCertifier()
        check = certifier._check_update_yields_checkpoint(
            fixtured_connector, state
        )
        assert check.passed, check.message

    def test_data_matches_schema(
        self, fixtured_connector: FixturedConnector
    ) -> None:
        state = ConnectorState(connector_id=fixtured_connector.connector_id)
        ops = list(fixtured_connector.update(state))
        certifier = ConnectorCertifier()
        check = certifier._check_data_matches_schema(fixtured_connector, ops)
        assert check.passed, check.message

    def test_close_releases_resources(
        self, fixtured_connector: FixturedConnector
    ) -> None:
        certifier = ConnectorCertifier()
        check = certifier._check_close_releases(fixtured_connector)
        assert check.passed, check.message
