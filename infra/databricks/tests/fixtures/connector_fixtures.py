"""Fixture data and mock connectors for certification and integration tests."""

from __future__ import annotations

from typing import Any, Iterator

from workbench.connectors.base import BaseConnector
from workbench.connectors.types import (
    ColumnDef,
    ConnectorState,
    OpType,
    SyncMode,
    SyncOp,
    TableDef,
)


# --- Fixture data per connector ---

NOTION_FIXTURE: dict[str, Any] = {
    "tables": [
        TableDef(
            name="programs",
            columns=(
                ColumnDef("id", "STRING", nullable=False),
                ColumnDef("name", "STRING"),
                ColumnDef("status", "STRING"),
                ColumnDef("last_edited", "TIMESTAMP"),
            ),
            primary_key=("id",),
        ),
    ],
    "rows": {
        "programs": [
            {
                "id": "pg-001",
                "name": "Alpha Program",
                "status": "active",
                "last_edited": "2026-01-01T00:00:00Z",
            },
            {
                "id": "pg-002",
                "name": "Beta Program",
                "status": "planning",
                "last_edited": "2026-01-02T00:00:00Z",
            },
        ],
    },
    "cursor": {"last_edited": {"programs": "2026-01-02T00:00:00Z"}},
}

AZURE_FIXTURE: dict[str, Any] = {
    "tables": [
        TableDef(
            name="advisor_recommendations",
            columns=(
                ColumnDef("id", "STRING", nullable=False),
                ColumnDef("category", "STRING"),
                ColumnDef("impact", "STRING"),
                ColumnDef("description", "STRING"),
            ),
            primary_key=("id",),
        ),
    ],
    "rows": {
        "advisor_recommendations": [
            {
                "id": "rec-001",
                "category": "Cost",
                "impact": "High",
                "description": "Resize VM",
            },
        ],
    },
    "cursor": {"azure": {"advisor": "2026-01-01T00:00:00Z"}},
}

GITHUB_FIXTURE: dict[str, Any] = {
    "tables": [
        TableDef(
            name="repositories",
            columns=(
                ColumnDef("id", "LONG", nullable=False),
                ColumnDef("full_name", "STRING"),
                ColumnDef("description", "STRING"),
                ColumnDef("updated_at", "TIMESTAMP"),
            ),
            primary_key=("id",),
        ),
    ],
    "rows": {
        "repositories": [
            {
                "id": 1,
                "full_name": "org/repo1",
                "description": "Test repo",
                "updated_at": "2026-01-01T00:00:00Z",
            },
        ],
    },
    "cursor": {"github": {"org/repo1": {"repos": "2026-01-01T00:00:00Z"}}},
}

ODOO_PG_FIXTURE: dict[str, Any] = {
    "tables": [
        TableDef(
            name="res_partner",
            columns=(
                ColumnDef("id", "LONG", nullable=False),
                ColumnDef("name", "STRING"),
                ColumnDef("email", "STRING"),
                ColumnDef("write_date", "TIMESTAMP"),
            ),
            primary_key=("id",),
        ),
    ],
    "rows": {
        "res_partner": [
            {
                "id": 1,
                "name": "Partner A",
                "email": "a@test.com",
                "write_date": "2026-01-01T00:00:00Z",
            },
        ],
    },
    "cursor": {"write_dates": {"res_partner": "2026-01-01T00:00:00Z"}},
}

CONNECTOR_FIXTURES: dict[str, dict[str, Any]] = {
    "notion": NOTION_FIXTURE,
    "azure": AZURE_FIXTURE,
    "github": GITHUB_FIXTURE,
    "odoo_pg": ODOO_PG_FIXTURE,
}


class FixturedConnector(BaseConnector):
    """A connector backed by static fixture data for testing.

    Simulates real connector behavior:
    - test_connection() always True
    - schema() returns fixture tables
    - update() yields UPSERTs from fixture rows + CHECKPOINT
    - Respects cursor: if cursor matches fixture cursor, yields no UPSERTs
    """

    def __init__(self, connector_id: str, fixture: dict[str, Any]) -> None:
        self.connector_id = connector_id
        self.connector_name = f"Fixtured {connector_id}"
        self._fixture = fixture
        self._closed = False
        super().__init__(config={})

    def test_connection(self) -> bool:
        return True

    def schema(self) -> list[TableDef]:
        return list(self._fixture["tables"])

    def update(self, state: ConnectorState) -> Iterator[SyncOp]:
        cursor = state.cursor
        fixture_cursor = self._fixture.get("cursor", {})

        for table_def in self._fixture["tables"]:
            table_name = table_def.name
            rows = self._fixture.get("rows", {}).get(table_name, [])

            # If cursor matches fixture cursor, no new data
            if cursor == fixture_cursor:
                pass  # No upserts for caught-up state
            else:
                for row in rows:
                    yield SyncOp(
                        op_type=OpType.UPSERT,
                        table=table_name,
                        data=dict(row),
                    )

        yield SyncOp(
            op_type=OpType.CHECKPOINT,
            table="",
            cursor=dict(fixture_cursor),
        )

    def close(self) -> None:
        self._closed = True


def create_fixtured_connector(connector_id: str) -> FixturedConnector:
    """Create a FixturedConnector for a given connector_id."""
    fixture = CONNECTOR_FIXTURES.get(connector_id)
    if fixture is None:
        raise KeyError(f"No fixture data for connector: {connector_id}")
    return FixturedConnector(connector_id, fixture)
