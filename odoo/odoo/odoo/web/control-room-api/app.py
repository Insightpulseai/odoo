"""
Control Room API — Job Orchestration and Lineage Tracking

FastAPI service that provides Databricks-style control room functionality:
1. Job submission and validation
2. Run execution and monitoring
3. Artifact management
4. Data lineage tracking
5. Continue CLI integration via webhooks

Usage:
    uvicorn app:app --host 0.0.0.0 --port 8789 --reload
"""

import os
import time
import logging
import hashlib
import httpx
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from contextlib import asynccontextmanager
from enum import Enum

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("control-room-api")

# ============================================================================
# Configuration
# ============================================================================

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
USE_SUPABASE = bool(SUPABASE_URL and SUPABASE_SERVICE_KEY)
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "dev-secret")

# In-memory store for development (when Supabase not configured)
MEM_STORE: Dict[str, List[Dict[str, Any]]] = {
    "jobs": [],
    "runs": [],
    "artifacts": [],
    "lineage_edges": [],
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
# Enums
# ============================================================================


class JobType(str, Enum):
    SPARK_ETL = "spark_etl"
    DIAGRAM_EXPORT = "diagram_export"
    SCHEMA_MIGRATION = "schema_migration"
    KB_CATALOG = "kb_catalog"
    CODE_VALIDATION = "code_validation"


class RunStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class EdgeType(str, Enum):
    DATA_FLOW = "data_flow"
    TRANSFORMATION = "transformation"
    DEPENDENCY = "dependency"


# ============================================================================
# Pydantic Models
# ============================================================================


class JobSpec(BaseModel):
    text: str = Field(..., description="Natural language description of the job")
    inputs: Dict[str, Any] = Field(default_factory=dict, description="Input parameters")


class CodeFile(BaseModel):
    path: str
    content: str


class RepoContext(BaseModel):
    url: Optional[str] = None
    ref: Optional[str] = "main"


class CallbackConfig(BaseModel):
    on_complete: Optional[str] = None
    on_fail: Optional[str] = None
    on_progress: Optional[str] = None


class JobIn(BaseModel):
    job_type: JobType
    spec: JobSpec
    code: Optional[Dict[str, List[CodeFile]]] = None
    created_by: str = "unknown"
    repo: Optional[RepoContext] = None
    callbacks: Optional[CallbackConfig] = None
    tenant_id: str = "default"


class JobOut(BaseModel):
    id: str
    job_type: JobType
    status: str
    created_at: str
    created_by: str


class RunOut(BaseModel):
    run_id: str
    job_id: str
    job_type: JobType
    status: RunStatus
    started_at: Optional[str]
    completed_at: Optional[str]
    artifacts: List[Dict[str, Any]] = Field(default_factory=list)
    logs_url: Optional[str] = None
    result: Optional[Dict[str, Any]] = None


class ArtifactIn(BaseModel):
    run_id: str
    path: str
    content_type: str = "application/octet-stream"
    storage_url: str
    size_bytes: int = 0
    tenant_id: str = "default"


class ArtifactOut(BaseModel):
    id: str
    run_id: str
    path: str
    content_type: str
    storage_url: str
    created_at: str


class LineageEdgeIn(BaseModel):
    source_entity: str
    target_entity: str
    job_id: Optional[str] = None
    run_id: Optional[str] = None
    edge_type: EdgeType = EdgeType.DATA_FLOW
    metadata: Dict[str, Any] = Field(default_factory=dict)
    tenant_id: str = "default"


class LineageGraphOut(BaseModel):
    entity: str
    upstream: List[Dict[str, Any]]
    downstream: List[Dict[str, Any]]


class ValidationResult(BaseModel):
    valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class WebhookPayload(BaseModel):
    run_id: str
    status: RunStatus
    summary: Optional[str] = None
    artifacts: List[Dict[str, Any]] = Field(default_factory=list)
    error: Optional[str] = None


# ============================================================================
# Application Lifecycle
# ============================================================================


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Control Room API starting...")
    logger.info(f"Supabase: {'connected' if USE_SUPABASE else 'not configured (using in-memory store)'}")
    yield
    logger.info("Control Room API shutting down...")


app = FastAPI(
    title="Control Room API",
    description="Databricks-style job orchestration and lineage tracking",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Authentication
# ============================================================================


async def verify_token(authorization: Optional[str] = Header(None)):
    """Simple token verification - extend for JWT validation."""
    if not authorization:
        return {"tenant_id": "default", "user_id": "anonymous", "role": "viewer"}

    # In production, decode JWT and extract claims
    # For now, accept any Bearer token
    if authorization.startswith("Bearer "):
        return {"tenant_id": "default", "user_id": "authenticated", "role": "operator"}

    return {"tenant_id": "default", "user_id": "anonymous", "role": "viewer"}


# ============================================================================
# Health Check
# ============================================================================


@app.get("/health")
def health():
    return {
        "ok": True,
        "service": "control-room-api",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "supabase": USE_SUPABASE,
    }


# ============================================================================
# Jobs API
# ============================================================================


@app.post("/api/v1/jobs/run", response_model=Dict[str, Any])
async def submit_job(
    job: JobIn,
    background_tasks: BackgroundTasks,
    auth: dict = Depends(verify_token),
):
    """Submit a job for execution."""
    now = datetime.now(timezone.utc).isoformat()

    if USE_SUPABASE:
        supabase = get_supabase()
        # Create job record
        job_result = (
            supabase.schema("runtime")
            .from_("cr_jobs")
            .insert(
                {
                    "tenant_id": job.tenant_id,
                    "job_type": job.job_type.value,
                    "spec": job.spec.model_dump(),
                    "code": job.code.model_dump() if job.code else None,
                    "repo": job.repo.model_dump() if job.repo else None,
                    "callbacks": job.callbacks.model_dump() if job.callbacks else None,
                    "created_by": job.created_by,
                }
            )
            .execute()
        )

        if not job_result.data:
            raise HTTPException(status_code=500, detail="Failed to create job")

        job_data = job_result.data[0]
        job_id = job_data["id"]

        # Create initial run
        run_result = (
            supabase.schema("runtime")
            .from_("cr_runs")
            .insert(
                {
                    "job_id": job_id,
                    "tenant_id": job.tenant_id,
                    "status": RunStatus.QUEUED.value,
                }
            )
            .execute()
        )

        if run_result.data:
            run_id = run_result.data[0]["id"]
            # Queue execution in background
            background_tasks.add_task(execute_job, job_id, run_id, job)
            logger.info(f"Created job {job_id} with run {run_id}")
            return {
                "job_id": job_id,
                "run_id": run_id,
                "status": RunStatus.QUEUED.value,
                "created_at": job_data["created_at"],
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to create run")
    else:
        # In-memory fallback
        job_id = f"job_{int(time.time() * 1000)}"
        run_id = f"run_{int(time.time() * 1000)}"

        job_data = {
            "id": job_id,
            "tenant_id": job.tenant_id,
            "job_type": job.job_type.value,
            "spec": job.spec.model_dump(),
            "code": job.code if job.code else None,
            "repo": job.repo.model_dump() if job.repo else None,
            "callbacks": job.callbacks.model_dump() if job.callbacks else None,
            "created_by": job.created_by,
            "created_at": now,
        }
        MEM_STORE["jobs"].append(job_data)

        run_data = {
            "id": run_id,
            "job_id": job_id,
            "tenant_id": job.tenant_id,
            "status": RunStatus.QUEUED.value,
            "started_at": None,
            "completed_at": None,
            "created_at": now,
        }
        MEM_STORE["runs"].append(run_data)

        # Queue execution
        background_tasks.add_task(execute_job, job_id, run_id, job)
        logger.info(f"Created job {job_id} with run {run_id} (in-memory)")

        return {
            "job_id": job_id,
            "run_id": run_id,
            "status": RunStatus.QUEUED.value,
            "created_at": now,
            "note": "Stored in memory (Supabase not configured)",
        }


@app.post("/api/v1/jobs/validate", response_model=ValidationResult)
async def validate_job(job: JobIn, auth: dict = Depends(verify_token)):
    """Validate a job without executing it."""
    errors = []
    warnings = []

    # Basic validation
    if not job.spec.text.strip():
        errors.append("Job spec text cannot be empty")

    if job.job_type == JobType.SPARK_ETL:
        if "source" not in job.spec.inputs:
            errors.append("spark_etl requires 'source' in spec.inputs")
        if "target" not in job.spec.inputs:
            warnings.append("spark_etl should specify 'target' in spec.inputs")

    if job.job_type == JobType.DIAGRAM_EXPORT:
        if "source_glob" not in job.spec.inputs and "source" not in job.spec.inputs:
            errors.append("diagram_export requires 'source' or 'source_glob' in spec.inputs")

    if job.code and job.code.get("files"):
        for f in job.code["files"]:
            if not f.path:
                errors.append("Code files must have a path")

    return ValidationResult(valid=len(errors) == 0, errors=errors, warnings=warnings)


@app.get("/api/v1/jobs")
async def list_jobs(
    tenant_id: Optional[str] = None,
    job_type: Optional[JobType] = None,
    limit: int = 50,
    auth: dict = Depends(verify_token),
):
    """List jobs with optional filters."""
    if USE_SUPABASE:
        supabase = get_supabase()
        query = supabase.schema("runtime").from_("cr_jobs").select("*")

        if tenant_id:
            query = query.eq("tenant_id", tenant_id)
        if job_type:
            query = query.eq("job_type", job_type.value)

        query = query.order("created_at", desc=True).limit(limit)
        result = query.execute()

        return {"jobs": result.data, "count": len(result.data)}
    else:
        jobs = MEM_STORE["jobs"]
        if tenant_id:
            jobs = [j for j in jobs if j.get("tenant_id") == tenant_id]
        if job_type:
            jobs = [j for j in jobs if j.get("job_type") == job_type.value]

        return {"jobs": jobs[:limit], "count": len(jobs)}


# ============================================================================
# Runs API
# ============================================================================


@app.get("/api/v1/runs/{run_id}", response_model=RunOut)
async def get_run(run_id: str, auth: dict = Depends(verify_token)):
    """Get run status and details."""
    if USE_SUPABASE:
        supabase = get_supabase()
        run_result = (
            supabase.schema("runtime")
            .from_("cr_runs")
            .select("*, cr_jobs(*)")
            .eq("id", run_id)
            .single()
            .execute()
        )

        if not run_result.data:
            raise HTTPException(status_code=404, detail="Run not found")

        run = run_result.data

        # Get artifacts
        artifacts_result = (
            supabase.schema("runtime")
            .from_("cr_artifacts")
            .select("*")
            .eq("run_id", run_id)
            .execute()
        )

        return RunOut(
            run_id=run["id"],
            job_id=run["job_id"],
            job_type=run["cr_jobs"]["job_type"],
            status=run["status"],
            started_at=run.get("started_at"),
            completed_at=run.get("completed_at"),
            artifacts=artifacts_result.data or [],
            logs_url=run.get("logs_url"),
            result=run.get("result"),
        )
    else:
        for run in MEM_STORE["runs"]:
            if run.get("id") == run_id:
                job = next((j for j in MEM_STORE["jobs"] if j["id"] == run["job_id"]), None)
                artifacts = [a for a in MEM_STORE["artifacts"] if a.get("run_id") == run_id]

                return RunOut(
                    run_id=run["id"],
                    job_id=run["job_id"],
                    job_type=job["job_type"] if job else "unknown",
                    status=run["status"],
                    started_at=run.get("started_at"),
                    completed_at=run.get("completed_at"),
                    artifacts=artifacts,
                    logs_url=run.get("logs_url"),
                    result=run.get("result"),
                )

        raise HTTPException(status_code=404, detail="Run not found")


@app.get("/api/v1/runs")
async def list_runs(
    job_id: Optional[str] = None,
    status: Optional[RunStatus] = None,
    limit: int = 50,
    auth: dict = Depends(verify_token),
):
    """List runs with optional filters."""
    if USE_SUPABASE:
        supabase = get_supabase()
        query = supabase.schema("runtime").from_("cr_runs").select("*")

        if job_id:
            query = query.eq("job_id", job_id)
        if status:
            query = query.eq("status", status.value)

        query = query.order("created_at", desc=True).limit(limit)
        result = query.execute()

        return {"runs": result.data, "count": len(result.data)}
    else:
        runs = MEM_STORE["runs"]
        if job_id:
            runs = [r for r in runs if r.get("job_id") == job_id]
        if status:
            runs = [r for r in runs if r.get("status") == status.value]

        return {"runs": runs[:limit], "count": len(runs)}


@app.post("/api/v1/runs/{run_id}/cancel")
async def cancel_run(run_id: str, auth: dict = Depends(verify_token)):
    """Cancel a running job."""
    if USE_SUPABASE:
        supabase = get_supabase()
        result = (
            supabase.schema("runtime")
            .from_("cr_runs")
            .update(
                {
                    "status": RunStatus.CANCELLED.value,
                    "completed_at": datetime.now(timezone.utc).isoformat(),
                }
            )
            .eq("id", run_id)
            .in_("status", [RunStatus.QUEUED.value, RunStatus.RUNNING.value])
            .execute()
        )

        if result.data:
            logger.info(f"Cancelled run {run_id}")
            return {"cancelled": True, "run_id": run_id}
        else:
            raise HTTPException(status_code=400, detail="Run cannot be cancelled")
    else:
        for run in MEM_STORE["runs"]:
            if run.get("id") == run_id:
                if run["status"] in [RunStatus.QUEUED.value, RunStatus.RUNNING.value]:
                    run["status"] = RunStatus.CANCELLED.value
                    run["completed_at"] = datetime.now(timezone.utc).isoformat()
                    return {"cancelled": True, "run_id": run_id}
                else:
                    raise HTTPException(status_code=400, detail="Run cannot be cancelled")

        raise HTTPException(status_code=404, detail="Run not found")


@app.post("/api/v1/runs/{run_id}/events")
async def push_event(run_id: str, event: Dict[str, Any], auth: dict = Depends(verify_token)):
    """Push an event for a run (used by executors)."""
    event_type = event.get("event_type", "log")
    data = event.get("data", {})

    logger.info(f"Run {run_id} event: {event_type} - {data}")

    # Store event or update run status based on event type
    if event_type == "status":
        new_status = data.get("status")
        if new_status and USE_SUPABASE:
            supabase = get_supabase()
            update_data = {"status": new_status}
            if new_status in [RunStatus.COMPLETED.value, RunStatus.FAILED.value]:
                update_data["completed_at"] = datetime.now(timezone.utc).isoformat()
            if new_status == RunStatus.RUNNING.value:
                update_data["started_at"] = datetime.now(timezone.utc).isoformat()

            supabase.schema("runtime").from_("cr_runs").update(update_data).eq("id", run_id).execute()

    return {"received": True, "event_type": event_type}


# ============================================================================
# Artifacts API
# ============================================================================


@app.post("/api/v1/artifacts", response_model=ArtifactOut)
async def create_artifact(artifact: ArtifactIn, auth: dict = Depends(verify_token)):
    """Create an artifact record."""
    now = datetime.now(timezone.utc).isoformat()
    checksum = hashlib.sha256(artifact.storage_url.encode()).hexdigest()[:16]

    if USE_SUPABASE:
        supabase = get_supabase()
        result = (
            supabase.schema("runtime")
            .from_("cr_artifacts")
            .insert(
                {
                    "run_id": artifact.run_id,
                    "tenant_id": artifact.tenant_id,
                    "path": artifact.path,
                    "content_type": artifact.content_type,
                    "size_bytes": artifact.size_bytes,
                    "storage_url": artifact.storage_url,
                    "checksum": checksum,
                }
            )
            .execute()
        )

        if result.data:
            return ArtifactOut(
                id=result.data[0]["id"],
                run_id=artifact.run_id,
                path=artifact.path,
                content_type=artifact.content_type,
                storage_url=artifact.storage_url,
                created_at=result.data[0]["created_at"],
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to create artifact")
    else:
        artifact_id = f"art_{int(time.time() * 1000)}"
        artifact_data = {
            "id": artifact_id,
            "run_id": artifact.run_id,
            "tenant_id": artifact.tenant_id,
            "path": artifact.path,
            "content_type": artifact.content_type,
            "size_bytes": artifact.size_bytes,
            "storage_url": artifact.storage_url,
            "checksum": checksum,
            "created_at": now,
        }
        MEM_STORE["artifacts"].append(artifact_data)

        return ArtifactOut(
            id=artifact_id,
            run_id=artifact.run_id,
            path=artifact.path,
            content_type=artifact.content_type,
            storage_url=artifact.storage_url,
            created_at=now,
        )


@app.get("/api/v1/artifacts/{artifact_id}")
async def get_artifact(artifact_id: str, auth: dict = Depends(verify_token)):
    """Get artifact details."""
    if USE_SUPABASE:
        supabase = get_supabase()
        result = (
            supabase.schema("runtime")
            .from_("cr_artifacts")
            .select("*")
            .eq("id", artifact_id)
            .single()
            .execute()
        )

        if result.data:
            return result.data
        else:
            raise HTTPException(status_code=404, detail="Artifact not found")
    else:
        for artifact in MEM_STORE["artifacts"]:
            if artifact.get("id") == artifact_id:
                return artifact

        raise HTTPException(status_code=404, detail="Artifact not found")


# ============================================================================
# Lineage API
# ============================================================================


@app.get("/api/v1/lineage/graph", response_model=LineageGraphOut)
async def get_lineage_graph(
    entity: str,
    depth: int = 2,
    auth: dict = Depends(verify_token),
):
    """Get upstream and downstream lineage for an entity."""
    if USE_SUPABASE:
        supabase = get_supabase()

        # Get upstream (entities that flow into this one)
        upstream_result = (
            supabase.schema("runtime")
            .from_("cr_lineage_edges")
            .select("*")
            .eq("target_entity", entity)
            .is_("deleted_at", "null")
            .execute()
        )

        # Get downstream (entities this flows into)
        downstream_result = (
            supabase.schema("runtime")
            .from_("cr_lineage_edges")
            .select("*")
            .eq("source_entity", entity)
            .is_("deleted_at", "null")
            .execute()
        )

        return LineageGraphOut(
            entity=entity,
            upstream=upstream_result.data or [],
            downstream=downstream_result.data or [],
        )
    else:
        upstream = [e for e in MEM_STORE["lineage_edges"] if e.get("target_entity") == entity and not e.get("deleted_at")]
        downstream = [e for e in MEM_STORE["lineage_edges"] if e.get("source_entity") == entity and not e.get("deleted_at")]

        return LineageGraphOut(entity=entity, upstream=upstream, downstream=downstream)


@app.post("/api/v1/lineage/edges")
async def create_lineage_edge(edge: LineageEdgeIn, auth: dict = Depends(verify_token)):
    """Create a lineage edge."""
    now = datetime.now(timezone.utc).isoformat()

    if USE_SUPABASE:
        supabase = get_supabase()
        result = (
            supabase.schema("runtime")
            .from_("cr_lineage_edges")
            .insert(
                {
                    "tenant_id": edge.tenant_id,
                    "source_entity": edge.source_entity,
                    "target_entity": edge.target_entity,
                    "job_id": edge.job_id,
                    "run_id": edge.run_id,
                    "edge_type": edge.edge_type.value,
                    "metadata": edge.metadata,
                }
            )
            .execute()
        )

        if result.data:
            return {"edge_id": result.data[0]["id"], "created": True}
        else:
            raise HTTPException(status_code=500, detail="Failed to create lineage edge")
    else:
        edge_id = f"edge_{int(time.time() * 1000)}"
        edge_data = {
            "id": edge_id,
            "tenant_id": edge.tenant_id,
            "source_entity": edge.source_entity,
            "target_entity": edge.target_entity,
            "job_id": edge.job_id,
            "run_id": edge.run_id,
            "edge_type": edge.edge_type.value,
            "metadata": edge.metadata,
            "created_at": now,
            "deleted_at": None,
        }
        MEM_STORE["lineage_edges"].append(edge_data)

        return {"edge_id": edge_id, "created": True}


# ============================================================================
# Webhooks API
# ============================================================================


@app.post("/api/v1/webhooks/continue")
async def continue_webhook(payload: WebhookPayload, auth: dict = Depends(verify_token)):
    """Webhook endpoint for Continue CLI callbacks."""
    logger.info(f"Continue webhook received: run={payload.run_id}, status={payload.status}")

    # Update run with callback result
    if USE_SUPABASE:
        supabase = get_supabase()
        update_data = {
            "status": payload.status.value,
            "result": {
                "summary": payload.summary,
                "error": payload.error,
            },
        }
        if payload.status in [RunStatus.COMPLETED, RunStatus.FAILED]:
            update_data["completed_at"] = datetime.now(timezone.utc).isoformat()

        supabase.schema("runtime").from_("cr_runs").update(update_data).eq("id", payload.run_id).execute()
    else:
        for run in MEM_STORE["runs"]:
            if run.get("id") == payload.run_id:
                run["status"] = payload.status.value
                run["result"] = {"summary": payload.summary, "error": payload.error}
                if payload.status in [RunStatus.COMPLETED, RunStatus.FAILED]:
                    run["completed_at"] = datetime.now(timezone.utc).isoformat()
                break

    return {"received": True, "run_id": payload.run_id}


# ============================================================================
# Job Execution (Background)
# ============================================================================


async def execute_job(job_id: str, run_id: str, job: JobIn):
    """Execute a job in the background."""
    logger.info(f"Executing job {job_id} (run {run_id})")

    now = datetime.now(timezone.utc).isoformat()

    # Update status to running
    if USE_SUPABASE:
        supabase = get_supabase()
        supabase.schema("runtime").from_("cr_runs").update(
            {"status": RunStatus.RUNNING.value, "started_at": now}
        ).eq("id", run_id).execute()
    else:
        for run in MEM_STORE["runs"]:
            if run.get("id") == run_id:
                run["status"] = RunStatus.RUNNING.value
                run["started_at"] = now
                break

    try:
        # Simulate execution based on job type
        # In production, dispatch to K8s Job or DO runner
        result = {"success": True, "message": f"Executed {job.job_type.value}"}

        if job.job_type == JobType.DIAGRAM_EXPORT:
            result["output"] = {
                "exported_files": ["diagram.png", "diagram.svg"],
                "format": "drawio",
            }

        # Update status to completed
        completed_at = datetime.now(timezone.utc).isoformat()
        if USE_SUPABASE:
            supabase = get_supabase()
            supabase.schema("runtime").from_("cr_runs").update(
                {
                    "status": RunStatus.COMPLETED.value,
                    "completed_at": completed_at,
                    "result": result,
                }
            ).eq("id", run_id).execute()
        else:
            for run in MEM_STORE["runs"]:
                if run.get("id") == run_id:
                    run["status"] = RunStatus.COMPLETED.value
                    run["completed_at"] = completed_at
                    run["result"] = result
                    break

        # Send callback if configured
        if job.callbacks and job.callbacks.on_complete:
            await send_callback(
                job.callbacks.on_complete,
                {
                    "run_id": run_id,
                    "job_id": job_id,
                    "status": "completed",
                    "result": result,
                },
            )

        logger.info(f"Job {job_id} completed successfully")

    except Exception as e:
        logger.error(f"Job {job_id} failed: {e}")

        # Update status to failed
        failed_at = datetime.now(timezone.utc).isoformat()
        error_result = {"success": False, "error": str(e)}

        if USE_SUPABASE:
            supabase = get_supabase()
            supabase.schema("runtime").from_("cr_runs").update(
                {
                    "status": RunStatus.FAILED.value,
                    "completed_at": failed_at,
                    "result": error_result,
                }
            ).eq("id", run_id).execute()
        else:
            for run in MEM_STORE["runs"]:
                if run.get("id") == run_id:
                    run["status"] = RunStatus.FAILED.value
                    run["completed_at"] = failed_at
                    run["result"] = error_result
                    break

        # Send failure callback
        if job.callbacks and job.callbacks.on_fail:
            await send_callback(
                job.callbacks.on_fail,
                {
                    "run_id": run_id,
                    "job_id": job_id,
                    "status": "failed",
                    "error": str(e),
                },
            )


async def send_callback(url: str, payload: Dict[str, Any]):
    """Send a webhook callback."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=10.0)
            logger.info(f"Callback sent to {url}: {response.status_code}")
    except Exception as e:
        logger.error(f"Callback failed for {url}: {e}")


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8789)
