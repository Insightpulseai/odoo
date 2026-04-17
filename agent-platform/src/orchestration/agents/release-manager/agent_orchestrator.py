"""
agent-platform/agents/release-manager/agent_orchestrator.py

IPAI Release Manager Orchestrator
Forked from: microsoft-foundry/Release-Manager-Assistant (substrate only)
Changes from RMA:
  - Removed: ThreadSafeCache → Redis (stateless ACA invariant)
  - Removed: JiraAgent, VisualizationAgent, synthetic MCP server
  - Added: go/no-go engine against release_contract.yaml
  - Added: OdooHealthAgent integration
  - Added: BIR freeze window check
  - Added: Stamp promotion sequencing
  - Retargeted: ADO org → insightpulseai / project → ipai-platform
  - Region: southeastasia (RMA hardcodes 5 regions, all excluding SEA)

Uses: agent_framework (MAF) + MCPStreamableHTTPTool + Redis + OTLP telemetry
"""
import os
import json
import asyncio
from datetime import datetime, timezone
from typing import Optional

import redis.asyncio as aioredis

# Agent framework imports are lazy — the /health endpoint must respond even
# when the Foundry MAF client is not yet wired. Actual workflow runs only
# when /release-manager/evaluate is hit, which does a deferred import.
try:
    from agent_framework import Agent, MCPStreamableHTTPTool
    from agent_framework.azure_ai import AzureAIAgentClient as FoundryChatClient
    try:
        from agent_framework.workflows import SequentialBuilder, FileCheckpointStorage
    except ImportError:
        from agent_framework.workflow import SequentialBuilder, FileCheckpointStorage
    _MAF_AVAILABLE = True
except ImportError as _e:
    _MAF_IMPORT_ERROR = str(_e)
    _MAF_AVAILABLE = False
    Agent = None  # type: ignore
    MCPStreamableHTTPTool = None  # type: ignore
    FoundryChatClient = None  # type: ignore
    SequentialBuilder = None  # type: ignore
    FileCheckpointStorage = None  # type: ignore

from azure.identity import DefaultAzureCredential, ManagedIdentityCredential, ChainedTokenCredential
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

# ---------------------------------------------------------------------------
# Telemetry — from RMA's AppTracerProvider pattern, wired to App Insights
# ---------------------------------------------------------------------------
def setup_telemetry() -> trace.Tracer:
    provider = TracerProvider()
    otlp_endpoint = os.environ.get(
        "OTEL_EXPORTER_OTLP_ENDPOINT",
        "http://localhost:4317"  # App Insights OpenTelemetry collector
    )
    exporter = OTLPSpanExporter(endpoint=otlp_endpoint)
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)
    return trace.get_tracer("ipai.release-manager")

tracer = setup_telemetry()

# ---------------------------------------------------------------------------
# Auth — keyless, same as all IPAI ACA services
# ---------------------------------------------------------------------------
credential = ChainedTokenCredential(
    ManagedIdentityCredential(client_id=os.environ.get("AZURE_CLIENT_ID", "")),
)

# ---------------------------------------------------------------------------
# Redis — replaces RMA's ThreadSafeCache (ACA stateless invariant)
# ---------------------------------------------------------------------------
REDIS_URL = os.environ.get("REDIS_URL", "redis://cache-ipai-dev.redis.cache.windows.net:6380")
redis_client: Optional[aioredis.Redis] = None

async def get_redis() -> aioredis.Redis:
    global redis_client
    if redis_client is None:
        redis_client = await aioredis.from_url(
            REDIS_URL,
            password=os.environ.get("REDIS_KEY", ""),
            ssl=True,
            decode_responses=True,
        )
    return redis_client

async def cache_get(key: str) -> Optional[dict]:
    r = await get_redis()
    val = await r.get(f"rm:{key}")
    return json.loads(val) if val else None

async def cache_set(key: str, value: dict, ttl_seconds: int = 3600) -> None:
    r = await get_redis()
    await r.setex(f"rm:{key}", ttl_seconds, json.dumps(value))

# ---------------------------------------------------------------------------
# MAF client — ipai-copilot-resource / ipai-copilot project
# Lazy instantiation so uvicorn can start even if MAF is not available.
# ---------------------------------------------------------------------------
client = None

def _get_client():
    global client
    if client is None:
        if not _MAF_AVAILABLE:
            raise RuntimeError(f"agent_framework not available: {_MAF_IMPORT_ERROR}")
        client = FoundryChatClient(
            project_endpoint=os.environ.get(
                "IPAI_FOUNDRY_ENDPOINT",
                "https://ipai-copilot-resource.services.ai.azure.com/api/projects/ipai-copilot"
            ),
            model="claude-sonnet-4-6",
            credential=credential,
        )
    return client

# ---------------------------------------------------------------------------
# MCP tools — deferred until first use (depend on MAF being available)
# ---------------------------------------------------------------------------
ado_mcp = None
odoo_mcp = None

def _get_mcp_tools():
    """Instantiate MCP tools lazily. Requires MAF."""
    global ado_mcp, odoo_mcp
    if ado_mcp is None or odoo_mcp is None:
        if not _MAF_AVAILABLE:
            raise RuntimeError(f"agent_framework not available: {_MAF_IMPORT_ERROR}")
        c = _get_client()
        ado_mcp = MCPStreamableHTTPTool(
            name="azure-devops",
            url="https://dev.azure.com/insightpulseai/_mcp/sse",
            client=c,
            description="Azure DevOps ipai-platform — pipelines, PRs, work items, builds",
            headers={"Authorization": f"Bearer {os.environ.get('ADO_ENTRA_TOKEN', '')}"},
        )
        odoo_mcp = MCPStreamableHTTPTool(
            name="odoo",
            url=os.environ.get("ODOO_MCP_URL", "https://erp.insightpulseai.com/mcp"),
            client=c,
            description="Odoo 18 CE — module health, BIR calendar, accounting state",
        )
    return ado_mcp, odoo_mcp

# ---------------------------------------------------------------------------
# Specialist agents — retargeted from RMA
# ---------------------------------------------------------------------------
SYSTEM_BASE = """
You are part of IPAI's Release Manager agent system.
IPAI stack: Odoo 18 CE on Azure Container Apps (SEA).
ADO org: insightpulseai / project: ipai-platform.
Always cite: ADO pipeline ID, Odoo module name+version, gate score.
Output must be structured JSON for the go/no-go engine.
"""

# Specialist agents are instantiated lazily inside evaluate_release() after
# MAF availability is confirmed and MCP tools are initialized. See _build_agents().

def _build_agents():
    """Create the three specialist agents. Requires MAF + MCP tools."""
    if not _MAF_AVAILABLE:
        raise RuntimeError(f"agent_framework not available: {_MAF_IMPORT_ERROR}")
    c = _get_client()
    ado, odoo = _get_mcp_tools()

    evidence = Agent(
        client=c,
        name="EvidenceGatherer",
        instructions=SYSTEM_BASE + """
        Gather release evidence. Use ADO MCP for pipeline/SAST/PR/coverage.
        Use Odoo MCP for module health, BIR calendar, accounting period lock.
        Return structured JSON matching the evidence contract.
        """,
        tools=[ado, odoo],
    )
    gate = Agent(
        client=c,
        name="GateEvaluator",
        instructions=SYSTEM_BASE + """
        Evaluate evidence against ssot/release/release_contract.yaml gates.
        Output JSON: {decision, gate_score, failures, hold_reason, requires_approval}.
        APPROVED / BLOCKED / CONDITIONAL per constitution thresholds.
        """,
        tools=[odoo],
    )
    promotion = Agent(
        client=c,
        name="StampPromoter",
        instructions=SYSTEM_BASE + """
        If APPROVED, trigger stamp promotion (dev→staging→prod) via ADO MCP.
        PHT working-hours check for prod; dual-approval required for prod/BIR override.
        """,
        tools=[ado],
    )
    return evidence, gate, promotion

# ---------------------------------------------------------------------------
# Go/No-go engine — the part RMA doesn't have
# ---------------------------------------------------------------------------
async def evaluate_release(module: str, version: str) -> dict:
    """
    Core decision engine. Run the full gate sequence and return a decision.

    This is the capability gap vs Microsoft's RMA:
    RMA reads pipeline status. IPAI's engine evaluates it against policy.
    """
    with tracer.start_as_current_span("release_manager.evaluate") as span:
        span.set_attribute("module", module)
        span.set_attribute("version", version)

        # Check Redis cache first (idempotency — same trigger = same result)
        cache_key = f"{module}:{version}"
        cached = await cache_get(cache_key)
        if cached:
            span.set_attribute("cache_hit", True)
            return cached

        # Build the evaluation workflow
        if not _MAF_AVAILABLE:
            return {
                "decision": "ERROR",
                "error": f"agent_framework not available: {_MAF_IMPORT_ERROR}",
                "module": module,
                "version": version,
            }
        evidence_agent, gate_agent, promotion_agent = _build_agents()
        checkpoint_storage = FileCheckpointStorage(
            storage_path=os.environ.get("CHECKPOINT_PATH", "/var/lib/pulser/checkpoints")
        )

        workflow = (
            SequentialBuilder(
                participants=[evidence_agent, gate_agent, promotion_agent],
                checkpoint_storage=checkpoint_storage,
            )
            .with_request_info(agents=["StampPromoter"])
            .build()
        )

        # Run the workflow
        result_text = ""
        async for event in workflow.run_stream(
            f"Evaluate release for module={module} version={version}. "
            f"ADO org=insightpulseai project=ipai-platform. "
            f"Current UTC time: {datetime.now(timezone.utc).isoformat()}"
        ):
            if event.type == "output":
                result_text += str(event.data)

        # Parse and persist
        try:
            result = json.loads(result_text)
        except json.JSONDecodeError:
            result = {"raw": result_text, "decision": "ERROR", "parse_failed": True}

        # Persist evidence bundle to Blob Storage
        await persist_evidence_bundle(module, version, result)

        # Cache result for idempotency (1 hour TTL)
        await cache_set(cache_key, result, ttl_seconds=3600)

        span.set_attribute("decision", result.get("decision", "UNKNOWN"))
        return result


async def persist_evidence_bundle(module: str, version: str, result: dict) -> None:
    """Write evidence bundle to stipaidev/releases/ for audit trail."""
    from azure.storage.blob import BlobServiceClient

    try:
        blob_client = BlobServiceClient(
            account_url=f"https://stipaidev.blob.core.windows.net",
            credential=credential,
        )
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        blob_path = f"releases/{module}/{version}/{timestamp}/decision.json"

        container = blob_client.get_container_client("releases")
        container.upload_blob(
            name=blob_path,
            data=json.dumps(result, indent=2),
            overwrite=True,
        )
    except Exception as e:
        print(f"Warning: Could not persist evidence bundle: {e}")


# ---------------------------------------------------------------------------
# FastAPI endpoint — exposed via /release-manager/evaluate
# ---------------------------------------------------------------------------
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="IPAI Release Manager", version="1.0.0")

class ReleaseEvalRequest(BaseModel):
    module: str      # e.g. "ipai_bir_tax_compliance"
    version: str     # e.g. "18.0.1.2.0"
    stamp: str = "dev"  # "dev" | "staging" | "prod"

@app.post("/release-manager/evaluate")
async def evaluate(req: ReleaseEvalRequest) -> dict:
    """
    Evaluate a module release against IPAI's go/no-go gate.
    Called by ADO pipeline at the end of CI.
    """
    try:
        result = await evaluate_release(req.module, req.version)
        if result.get("decision") == "BLOCKED":
            raise HTTPException(status_code=422, detail=result)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "agent": "release-manager", "stamp": os.environ.get("STAMP", "dev")}
