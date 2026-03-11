"""
Process Mining API for Odoo Copilot

Local-first query service for process mining insights.
Connects to the pm.* schema in Odoo's PostgreSQL database.

Usage:
    export PM_DB_DSN="postgres://odoo:odoo@localhost:5432/odoo_dev"
    uvicorn app.main:app --host 0.0.0.0 --port 8787
"""

import os
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any

import asyncpg
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

DB_DSN = os.getenv("PM_DB_DSN")  # e.g. postgres://user:pass@host:5432/dbname

_pool: asyncpg.Pool | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage database connection pool lifecycle."""
    global _pool
    if not DB_DSN:
        raise RuntimeError("PM_DB_DSN environment variable is required")
    _pool = await asyncpg.create_pool(dsn=DB_DSN, min_size=1, max_size=5)
    yield
    if _pool:
        await _pool.close()


app = FastAPI(
    title="Odoo Process Mining API",
    description="Local-first query service for process mining insights",
    version="0.1.0",
    lifespan=lifespan,
)


# --------------------------------------------------------------------------
# Models
# --------------------------------------------------------------------------


class ProcessSummary(BaseModel):
    """Summary statistics for a process."""

    process: str
    cases: int
    median_duration_s: int | None
    p95_duration_s: int | None
    open_cases: int


class Edge(BaseModel):
    """DFG edge with latency stats."""

    activity_from: str
    activity_to: str
    edge_count: int
    p50_s: int | None
    p95_s: int | None


class Variant(BaseModel):
    """Process variant (unique activity sequence)."""

    variant_id: str
    case_count: int
    sequence: list[str]


class Event(BaseModel):
    """Single event in a case timeline."""

    activity: str
    ts: datetime
    source_model: str | None
    source_id: int | None
    attrs_json: dict[str, Any]


class Deviation(BaseModel):
    """Conformance deviation detected by rule engine."""

    rule_id: str
    severity: str
    details_json: dict[str, Any]
    created_at: datetime


class CaseDetail(BaseModel):
    """Full case detail with timeline and deviations."""

    case_id: str
    process: str
    source_model: str
    source_id: int
    company_id: int | None
    start_ts: datetime | None
    end_ts: datetime | None
    duration_s: int | None
    variant_id: str | None
    attrs_json: dict[str, Any]
    events: list[Event]
    deviations: list[Deviation]


class DeviationSummary(BaseModel):
    """Deviation with case context."""

    deviation_id: int
    case_id: str
    rule_id: str
    severity: str
    details_json: dict[str, Any]
    created_at: datetime


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    database: str
    pm_schema: bool


# --------------------------------------------------------------------------
# Endpoints
# --------------------------------------------------------------------------


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Check API and database connectivity."""
    assert _pool is not None
    try:
        async with _pool.acquire() as conn:
            # Check pm schema exists
            result = await conn.fetchval(
                "SELECT EXISTS(SELECT 1 FROM information_schema.schemata WHERE schema_name='pm')"
            )
            return HealthResponse(status="ok", database="connected", pm_schema=result)
    except Exception as e:
        return HealthResponse(status="error", database=str(e), pm_schema=False)


@app.get("/pm/{process}/summary", response_model=ProcessSummary)
async def get_process_summary(process: str, company_id: int | None = None):
    """
    Get summary statistics for a process.

    Args:
        process: Process name (e.g., 'p2p', 'o2c')
        company_id: Optional filter by company
    """
    assert _pool is not None
    q = """
        WITH base AS (
            SELECT duration_s, end_ts
            FROM pm.case
            WHERE process = $1
              AND ($2::bigint IS NULL OR company_id = $2)
        )
        SELECT
            COUNT(*)::int AS cases,
            percentile_cont(0.5) WITHIN GROUP (ORDER BY duration_s) AS p50,
            percentile_cont(0.95) WITHIN GROUP (ORDER BY duration_s) AS p95,
            COUNT(*) FILTER (WHERE end_ts IS NULL)::int AS open_cases
        FROM base
        WHERE duration_s IS NOT NULL;
    """
    async with _pool.acquire() as conn:
        row = await conn.fetchrow(q, process, company_id)

    return ProcessSummary(
        process=process,
        cases=row["cases"] or 0,
        median_duration_s=int(row["p50"]) if row["p50"] is not None else None,
        p95_duration_s=int(row["p95"]) if row["p95"] is not None else None,
        open_cases=row["open_cases"] or 0,
    )


@app.get("/pm/{process}/bottlenecks", response_model=list[Edge])
async def get_bottlenecks(process: str, limit: int = Query(10, ge=1, le=100)):
    """
    Get top edges sorted by latency (bottlenecks).

    Args:
        process: Process name
        limit: Maximum number of edges to return
    """
    assert _pool is not None
    q = """
        SELECT activity_from, activity_to, edge_count, p50_s, p95_s
        FROM pm.edge
        WHERE process = $1
        ORDER BY p95_s DESC NULLS LAST, edge_count DESC
        LIMIT $2;
    """
    async with _pool.acquire() as conn:
        rows = await conn.fetch(q, process, limit)

    return [
        Edge(
            activity_from=r["activity_from"],
            activity_to=r["activity_to"],
            edge_count=r["edge_count"],
            p50_s=r["p50_s"],
            p95_s=r["p95_s"],
        )
        for r in rows
    ]


@app.get("/pm/{process}/variants", response_model=list[Variant])
async def get_variants(process: str, limit: int = Query(10, ge=1, le=100)):
    """
    Get top variants sorted by case count.

    Args:
        process: Process name
        limit: Maximum number of variants to return
    """
    assert _pool is not None
    q = """
        SELECT variant_id, case_count, sequence
        FROM pm.variant
        WHERE process = $1
        ORDER BY case_count DESC
        LIMIT $2;
    """
    async with _pool.acquire() as conn:
        rows = await conn.fetch(q, process, limit)

    return [
        Variant(
            variant_id=r["variant_id"],
            case_count=r["case_count"],
            sequence=list(r["sequence"]),
        )
        for r in rows
    ]


@app.get("/pm/{process}/cases/{case_id}", response_model=CaseDetail)
async def get_case(process: str, case_id: str):
    """
    Get full case detail including timeline and deviations.

    Args:
        process: Process name
        case_id: Case identifier
    """
    assert _pool is not None
    async with _pool.acquire() as conn:
        # Get case
        c = await conn.fetchrow(
            "SELECT * FROM pm.case WHERE case_id = $1 AND process = $2;",
            case_id,
            process,
        )
        if not c:
            raise HTTPException(status_code=404, detail="Case not found")

        # Get events
        events = await conn.fetch(
            """
            SELECT activity, ts, source_model, source_id, attrs_json
            FROM pm.event
            WHERE case_id = $1
            ORDER BY ts, event_id;
            """,
            case_id,
        )

        # Get deviations
        deviations = await conn.fetch(
            """
            SELECT rule_id, severity, details_json, created_at
            FROM pm.deviation
            WHERE case_id = $1
            ORDER BY created_at DESC;
            """,
            case_id,
        )

    return CaseDetail(
        case_id=c["case_id"],
        process=c["process"],
        source_model=c["source_model"],
        source_id=c["source_id"],
        company_id=c["company_id"],
        start_ts=c["start_ts"],
        end_ts=c["end_ts"],
        duration_s=c["duration_s"],
        variant_id=c["variant_id"],
        attrs_json=dict(c["attrs_json"]) if c["attrs_json"] else {},
        events=[
            Event(
                activity=e["activity"],
                ts=e["ts"],
                source_model=e["source_model"],
                source_id=e["source_id"],
                attrs_json=dict(e["attrs_json"]) if e["attrs_json"] else {},
            )
            for e in events
        ],
        deviations=[
            Deviation(
                rule_id=d["rule_id"],
                severity=d["severity"],
                details_json=dict(d["details_json"]) if d["details_json"] else {},
                created_at=d["created_at"],
            )
            for d in deviations
        ],
    )


@app.get("/pm/{process}/deviations", response_model=list[DeviationSummary])
async def get_deviations(
    process: str,
    rule_id: str | None = None,
    severity: str | None = None,
    limit: int = Query(50, ge=1, le=500),
):
    """
    List deviations with optional filters.

    Args:
        process: Process name
        rule_id: Optional filter by rule ID
        severity: Optional filter by severity (low, medium, high)
        limit: Maximum number of deviations to return
    """
    assert _pool is not None
    q = """
        SELECT deviation_id, case_id, rule_id, severity, details_json, created_at
        FROM pm.deviation
        WHERE process = $1
          AND ($2::text IS NULL OR rule_id = $2)
          AND ($3::text IS NULL OR severity = $3)
        ORDER BY created_at DESC
        LIMIT $4;
    """
    async with _pool.acquire() as conn:
        rows = await conn.fetch(q, process, rule_id, severity, limit)

    return [
        DeviationSummary(
            deviation_id=r["deviation_id"],
            case_id=r["case_id"],
            rule_id=r["rule_id"],
            severity=r["severity"],
            details_json=dict(r["details_json"]) if r["details_json"] else {},
            created_at=r["created_at"],
        )
        for r in rows
    ]


@app.post("/pm/{process}/etl/run")
async def trigger_etl(process: str):
    """
    Trigger incremental ETL for a process.

    Args:
        process: Process name (currently only 'p2p' supported)
    """
    assert _pool is not None
    if process != "p2p":
        raise HTTPException(status_code=400, detail=f"ETL not implemented for {process}")

    async with _pool.acquire() as conn:
        result = await conn.fetchrow("SELECT * FROM pm.run_p2p_etl();")

    return {
        "status": "completed",
        "process": process,
        "cases_processed": result["cases_processed"],
        "events_created": result["events_created"],
        "deviations_found": result["deviations_found"],
    }
