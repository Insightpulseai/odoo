"""Pydantic models for Notion Sync service."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class SyncWatermark(BaseModel):
    """Tracks the last sync time for a database."""

    database_id: str
    database_name: str
    last_synced_at: datetime
    last_edited_time: datetime
    record_count: int = 0


class NotionPage(BaseModel):
    """Represents a Notion page from API response."""

    id: str
    created_time: datetime
    last_edited_time: datetime
    archived: bool = False
    properties: dict[str, Any]
    url: str | None = None


class BronzeRecord(BaseModel):
    """Record stored in bronze layer."""

    page_id: str
    database_id: str
    database_name: str
    payload: str  # JSON string
    last_edited_time: datetime
    synced_at: datetime = Field(default_factory=datetime.utcnow)
    is_archived: bool = False


class SilverProgram(BaseModel):
    """Normalized program record for silver layer."""

    id: str
    page_id: str
    name: str
    owner: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    status: str | None = None
    description: str | None = None
    last_edited_time: datetime
    synced_at: datetime = Field(default_factory=datetime.utcnow)
    is_archived: bool = False


class SilverProject(BaseModel):
    """Normalized project record for silver layer."""

    id: str
    page_id: str
    program_id: str | None = None
    name: str
    budget_total: float | None = None
    currency: str = "USD"
    start_date: datetime | None = None
    end_date: datetime | None = None
    status: str | None = None
    priority: str | None = None
    owner: str | None = None
    last_edited_time: datetime
    synced_at: datetime = Field(default_factory=datetime.utcnow)
    is_archived: bool = False


class SilverBudgetLine(BaseModel):
    """Normalized budget line record for silver layer."""

    id: str
    page_id: str
    project_id: str | None = None
    category: str | None = None
    vendor: str | None = None
    description: str | None = None
    amount: float | None = None
    committed_date: datetime | None = None
    invoice_date: datetime | None = None
    paid_date: datetime | None = None
    actual_amount: float | None = None
    notes: str | None = None
    currency: str = "USD"
    last_edited_time: datetime
    synced_at: datetime = Field(default_factory=datetime.utcnow)
    is_archived: bool = False


class SilverRisk(BaseModel):
    """Normalized risk record for silver layer."""

    id: str
    page_id: str
    project_id: str | None = None
    title: str
    severity: str | None = None
    probability: str | None = None
    status: str | None = None
    mitigation: str | None = None
    owner: str | None = None
    last_edited_time: datetime
    synced_at: datetime = Field(default_factory=datetime.utcnow)
    is_archived: bool = False


class SyncResult(BaseModel):
    """Result of a sync operation."""

    database_name: str
    database_id: str
    pages_synced: int
    pages_archived: int
    errors: list[str] = Field(default_factory=list)
    duration_seconds: float
    success: bool = True


class SyncSummary(BaseModel):
    """Summary of all sync operations."""

    started_at: datetime
    completed_at: datetime | None = None
    results: list[SyncResult] = Field(default_factory=list)
    total_pages_synced: int = 0
    total_errors: int = 0
    success: bool = True

    def add_result(self, result: SyncResult) -> None:
        """Add a sync result to the summary."""
        self.results.append(result)
        self.total_pages_synced += result.pages_synced
        self.total_errors += len(result.errors)
        if not result.success:
            self.success = False

    def complete(self) -> None:
        """Mark the sync as complete."""
        self.completed_at = datetime.utcnow()
