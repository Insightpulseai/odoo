"""Pytest fixtures for Notion Sync tests."""

from datetime import datetime

import pytest

from notion_sync.models import NotionPage


@pytest.fixture
def sample_notion_page() -> NotionPage:
    """Create a sample Notion page for testing."""
    return NotionPage(
        id="12345678-1234-1234-1234-123456789abc",
        created_time=datetime(2024, 1, 1, 12, 0, 0),
        last_edited_time=datetime(2024, 1, 15, 14, 30, 0),
        archived=False,
        properties={
            "Name": {
                "title": [{"plain_text": "Test Project"}]
            },
            "Status": {
                "select": {"name": "In Progress"}
            },
            "Budget Total": {
                "number": 100000
            },
            "Start Date": {
                "date": {"start": "2024-01-01"}
            },
            "Owner": {
                "people": [{"name": "John Doe", "id": "user-123"}]
            },
            "Program": {
                "relation": [{"id": "program-abc-123"}]
            },
        },
        url="https://notion.so/Test-Project-12345678",
    )


@pytest.fixture
def sample_column_mappings() -> list[dict[str, str]]:
    """Create sample column mappings for testing."""
    return [
        {"source": "Name", "target": "name", "type": "title"},
        {"source": "Status", "target": "status", "type": "select"},
        {"source": "Budget Total", "target": "budget_total", "type": "number"},
        {"source": "Start Date", "target": "start_date", "type": "date"},
        {"source": "Owner", "target": "owner", "type": "person"},
        {"source": "Program", "target": "program_id", "type": "relation"},
    ]
