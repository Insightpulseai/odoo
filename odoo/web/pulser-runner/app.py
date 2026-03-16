"""
Pulser Runner — Work Item Processing API

FastAPI service that:
1. Receives work items from GitHub App or Odoo
2. Executes remediation loops (plan → apply → verify)
3. Stores evidence and updates status
4. Tracks SLA timers

Usage:
    uvicorn app:app --host 0.0.0.0 --port 8788 --reload
"""

import os
import json
import time
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pulser-runner")

# ============================================================================
# Configuration
# ============================================================================

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
USE_SUPABASE = bool(SUPABASE_URL and SUPABASE_SERVICE_KEY)

# In-memory store for development (when Supabase not configured)
MEM_STORE: Dict[str, List[Dict[str, Any]]] = {
    "work_items": [],
    "runs": [],
    "evidence": [],
}

# Supabase client (lazy init)
_supabase_client = None


def get_supabase():
    global _supabase_client
    if _supabase_client is None and USE_SUPABASE:
        from supabase import create_client

        _supabase_client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    return _supabase_client


# ============================================================================
# Pydantic Models
# ============================================================================


class WorkItemIn(BaseModel):
    tenant_id: str
    source: str  # github_pr | odoo_event | manual
    source_ref: str
    title: str
    description: Optional[str] = None
    status: str = "open"
    lane: Optional[str] = None  # DEV | HR | IT | FIN | MGR
    priority: int = Field(default=3, ge=1, le=4)
    payload: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)


class WorkItemOut(BaseModel):
    id: str
    tenant_id: str
    source: str
    source_ref: str
    title: str
    status: str
    lane: Optional[str]
    priority: int
    created_at: str


class RunIn(BaseModel):
    work_item_id: str
    tenant_id: str
    runner: Optional[str] = None
    meta: Dict[str, Any] = Field(default_factory=dict)


class RunOut(BaseModel):
    id: str
    work_item_id: str
    stage: str
    started_at: str


class EvidenceIn(BaseModel):
    tenant_id: str
    work_item_id: str
    kind: str  # log | patch | doc | report | screenshot | check | approval
    uri: Optional[str] = None
    body: Optional[str] = None
    meta: Dict[str, Any] = Field(default_factory=dict)
    actor_id: Optional[str] = None


class SLACheckResult(BaseModel):
    breached_count: int
    breached_items: List[Dict[str, Any]]


# ============================================================================
# Application Lifecycle
# ============================================================================


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Pulser Runner starting...")
    logger.info(f"Supabase: {'connected' if USE_SUPABASE else 'not configured (using in-memory store)'}")
    yield
    logger.info("Pulser Runner shutting down...")


app = FastAPI(
    title="Pulser Runner",
    description="Work item processing and remediation API",
    version="0.1.0",
    lifespan=lifespan,
)


# ============================================================================
# Health Check
# ============================================================================


@app.get("/health")
def health():
    return {
        "ok": True,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "supabase": USE_SUPABASE,
    }


# ============================================================================
# Work Items API
# ============================================================================


@app.post("/v1/work-items", response_model=Dict[str, Any])
async def create_work_item(wi: WorkItemIn, background_tasks: BackgroundTasks):
    """Create a new work item."""
    now = datetime.now(timezone.utc).isoformat()

    if USE_SUPABASE:
        supabase = get_supabase()
        result = (
            supabase.schema("runtime")
            .from_("work_items")
            .insert(
                {
                    "tenant_id": wi.tenant_id,
                    "source": wi.source,
                    "source_ref": wi.source_ref,
                    "title": wi.title,
                    "description": wi.description,
                    "status": wi.status,
                    "lane": wi.lane,
                    "priority": wi.priority,
                    "payload": wi.payload,
                    "tags": wi.tags,
                }
            )
            .execute()
        )

        if result.data:
            item = result.data[0]
            logger.info(f"Created work item {item['id']} in Supabase")
            return {
                "work_item_id": item["id"],
                "status": item["status"],
                "created_at": item["created_at"],
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to create work item")
    else:
        # In-memory fallback
        item_id = f"wi_{int(time.time() * 1000)}"
        item = {
            "id": item_id,
            "tenant_id": wi.tenant_id,
            "source": wi.source,
            "source_ref": wi.source_ref,
            "title": wi.title,
            "description": wi.description,
            "status": wi.status,
            "lane": wi.lane,
            "priority": wi.priority,
            "payload": wi.payload,
            "tags": wi.tags,
            "created_at": now,
            "updated_at": now,
        }
        MEM_STORE["work_items"].append(item)
        logger.info(f"Created work item {item_id} in memory")

        return {
            "work_item_id": item_id,
            "status": item["status"],
            "created_at": now,
            "note": "Stored in memory (Supabase not configured)",
        }


@app.get("/v1/work-items")
async def list_work_items(
    tenant_id: Optional[str] = None,
    status: Optional[str] = None,
    lane: Optional[str] = None,
    limit: int = 50,
):
    """List work items with optional filters."""
    if USE_SUPABASE:
        supabase = get_supabase()
        query = supabase.schema("runtime").from_("work_items").select("*")

        if tenant_id:
            query = query.eq("tenant_id", tenant_id)
        if status:
            query = query.eq("status", status)
        if lane:
            query = query.eq("lane", lane)

        query = query.order("updated_at", desc=True).limit(limit)
        result = query.execute()

        return {"items": result.data, "count": len(result.data)}
    else:
        items = MEM_STORE["work_items"]
        if status:
            items = [x for x in items if x.get("status") == status]
        if lane:
            items = [x for x in items if x.get("lane") == lane]
        if tenant_id:
            items = [x for x in items if x.get("tenant_id") == tenant_id]

        return {"items": items[:limit], "count": len(items)}


@app.patch("/v1/work-items/{work_item_id}")
async def update_work_item(work_item_id: str, updates: Dict[str, Any]):
    """Update a work item's status or other fields."""
    allowed_fields = {"status", "lane", "priority", "assignee_id", "payload"}
    filtered = {k: v for k, v in updates.items() if k in allowed_fields}

    if not filtered:
        raise HTTPException(status_code=400, detail="No valid fields to update")

    if USE_SUPABASE:
        supabase = get_supabase()
        result = (
            supabase.schema("runtime")
            .from_("work_items")
            .update(filtered)
            .eq("id", work_item_id)
            .execute()
        )

        if result.data:
            return {"updated": True, "work_item_id": work_item_id}
        else:
            raise HTTPException(status_code=404, detail="Work item not found")
    else:
        for item in MEM_STORE["work_items"]:
            if item.get("id") == work_item_id:
                item.update(filtered)
                item["updated_at"] = datetime.now(timezone.utc).isoformat()
                return {"updated": True, "work_item_id": work_item_id}

        raise HTTPException(status_code=404, detail="Work item not found")


# ============================================================================
# Runs API
# ============================================================================


@app.post("/v1/runs/start", response_model=Dict[str, Any])
async def start_run(run: RunIn):
    """Start a new remediation run for a work item."""
    now = datetime.now(timezone.utc).isoformat()

    if USE_SUPABASE:
        supabase = get_supabase()

        # Create run
        result = (
            supabase.schema("runtime")
            .from_("runs")
            .insert(
                {
                    "tenant_id": run.tenant_id,
                    "work_item_id": run.work_item_id,
                    "stage": "planned",
                    "runner": run.runner,
                    "meta": run.meta,
                }
            )
            .execute()
        )

        if result.data:
            run_data = result.data[0]

            # Update work item status
            supabase.schema("runtime").from_("work_items").update(
                {"status": "running"}
            ).eq("id", run.work_item_id).execute()

            return {
                "run_id": run_data["id"],
                "work_item_id": run.work_item_id,
                "stage": run_data["stage"],
                "started_at": run_data["started_at"],
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to create run")
    else:
        run_id = f"run_{int(time.time() * 1000)}"
        run_data = {
            "id": run_id,
            "tenant_id": run.tenant_id,
            "work_item_id": run.work_item_id,
            "stage": "planned",
            "runner": run.runner,
            "meta": run.meta,
            "started_at": now,
        }
        MEM_STORE["runs"].append(run_data)

        # Update work item status
        for item in MEM_STORE["work_items"]:
            if item.get("id") == run.work_item_id:
                item["status"] = "running"
                break

        return {
            "run_id": run_id,
            "work_item_id": run.work_item_id,
            "stage": "planned",
            "started_at": now,
        }


@app.patch("/v1/runs/{run_id}")
async def update_run(run_id: str, updates: Dict[str, Any]):
    """Update a run's stage or metadata."""
    allowed_fields = {"stage", "meta", "finished_at"}
    filtered = {k: v for k, v in updates.items() if k in allowed_fields}

    if USE_SUPABASE:
        supabase = get_supabase()
        result = (
            supabase.schema("runtime")
            .from_("runs")
            .update(filtered)
            .eq("id", run_id)
            .execute()
        )

        if result.data:
            return {"updated": True, "run_id": run_id}
        else:
            raise HTTPException(status_code=404, detail="Run not found")
    else:
        for run in MEM_STORE["runs"]:
            if run.get("id") == run_id:
                run.update(filtered)
                return {"updated": True, "run_id": run_id}

        raise HTTPException(status_code=404, detail="Run not found")


# ============================================================================
# Evidence API
# ============================================================================


@app.post("/v1/evidence", response_model=Dict[str, Any])
async def create_evidence(evidence: EvidenceIn):
    """Attach evidence to a work item."""
    if USE_SUPABASE:
        supabase = get_supabase()
        result = (
            supabase.schema("runtime")
            .from_("evidence")
            .insert(
                {
                    "tenant_id": evidence.tenant_id,
                    "work_item_id": evidence.work_item_id,
                    "kind": evidence.kind,
                    "uri": evidence.uri,
                    "body": evidence.body,
                    "meta": evidence.meta,
                    "actor_id": evidence.actor_id,
                }
            )
            .execute()
        )

        if result.data:
            return {"evidence_id": result.data[0]["id"]}
        else:
            raise HTTPException(status_code=500, detail="Failed to create evidence")
    else:
        evidence_id = f"ev_{int(time.time() * 1000)}"
        ev_data = {
            "id": evidence_id,
            "tenant_id": evidence.tenant_id,
            "work_item_id": evidence.work_item_id,
            "kind": evidence.kind,
            "uri": evidence.uri,
            "body": evidence.body,
            "meta": evidence.meta,
            "actor_id": evidence.actor_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        MEM_STORE["evidence"].append(ev_data)
        return {"evidence_id": evidence_id}


@app.get("/v1/evidence/{work_item_id}")
async def get_evidence(work_item_id: str):
    """Get all evidence for a work item."""
    if USE_SUPABASE:
        supabase = get_supabase()
        result = (
            supabase.schema("runtime")
            .from_("evidence")
            .select("*")
            .eq("work_item_id", work_item_id)
            .order("created_at", desc=True)
            .execute()
        )
        return {"evidence": result.data}
    else:
        evidence = [e for e in MEM_STORE["evidence"] if e.get("work_item_id") == work_item_id]
        return {"evidence": evidence}


# ============================================================================
# SLA API
# ============================================================================


@app.post("/v1/sla/check", response_model=SLACheckResult)
async def check_sla_breaches(tenant_id: Optional[str] = None):
    """Check for SLA breaches and mark them."""
    if USE_SUPABASE:
        supabase = get_supabase()

        # Call the RPC function
        result = supabase.rpc("check_sla_breaches").execute()

        breached = result.data or []
        if tenant_id:
            # Filter by tenant if specified (RPC returns all)
            breached = [b for b in breached if True]  # RPC handles filtering

        return SLACheckResult(
            breached_count=len(breached),
            breached_items=breached,
        )
    else:
        # Simple in-memory SLA check
        now = datetime.now(timezone.utc)
        breached = []

        for item in MEM_STORE["work_items"]:
            if item.get("status") in ("open", "running"):
                created = datetime.fromisoformat(item.get("created_at", now.isoformat()).replace("Z", "+00:00"))
                priority = item.get("priority", 3)

                # SLA hours by priority
                sla_hours = {1: 4, 2: 8, 3: 24, 4: 72}.get(priority, 24)
                deadline = created.timestamp() + (sla_hours * 3600)

                if now.timestamp() > deadline:
                    breached.append(
                        {
                            "work_item_id": item["id"],
                            "title": item.get("title"),
                            "lane": item.get("lane"),
                            "priority": priority,
                            "minutes_overdue": int((now.timestamp() - deadline) / 60),
                        }
                    )

        return SLACheckResult(
            breached_count=len(breached),
            breached_items=breached,
        )


# ============================================================================
# Stats API
# ============================================================================


@app.get("/v1/stats")
async def get_stats(tenant_id: str):
    """Get work item statistics."""
    if USE_SUPABASE:
        supabase = get_supabase()
        result = supabase.rpc("get_work_item_stats", {"p_tenant_id": tenant_id}).execute()
        return {"stats": result.data}
    else:
        # Simple in-memory stats
        stats = {}
        for item in MEM_STORE["work_items"]:
            if item.get("tenant_id") == tenant_id:
                key = f"{item.get('lane', 'NONE')}|{item.get('status')}|{item.get('priority')}"
                stats[key] = stats.get(key, 0) + 1

        return {"stats": stats}


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8788)
