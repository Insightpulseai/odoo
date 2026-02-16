"""
Local MCP Server - FastAPI Application
Provides SQLite-backed MCP tools for local development
"""
import json
import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel

from .config import settings
from .database import init_all_databases, get_skills_db, get_rag_db, get_memory_db


# ============================================================================
# Models
# ============================================================================

class Skill(BaseModel):
    id: str
    name: str
    version: Optional[str] = None
    status: str = "dev"
    metadata: Optional[dict] = None
    file_path: Optional[str] = None


class ConversationMessage(BaseModel):
    role: str
    content: str
    timestamp: Optional[str] = None


class Conversation(BaseModel):
    id: str
    session_id: str
    user_id: Optional[str] = None
    messages: List[ConversationMessage]
    context: Optional[dict] = None
    summary: Optional[str] = None


class CommitInfo(BaseModel):
    id: str
    commit_hash: str
    author: str
    commit_message: str
    files_changed: List[str]
    commit_date: str


# ============================================================================
# App Initialization
# ============================================================================

app = FastAPI(
    title="Local MCP Server",
    description="SQLite-backed MCP server for local Odoo development",
    version="0.1.0"
)


@app.on_event("startup")
async def startup_event():
    """Initialize databases on startup"""
    await init_all_databases()
    print(f"✅ Local MCP Server initialized")
    print(f"   Skills DB: {settings.skills_db_path}")
    print(f"   RAG DB: {settings.rag_db_path}")
    print(f"   Memory DB: {settings.memory_db_path}")


# ============================================================================
# Auth
# ============================================================================

async def verify_api_key(x_api_key: str = Header(..., alias="X-API-Key")):
    """Verify API key for protected endpoints"""
    if x_api_key != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return True


# ============================================================================
# Health & Status
# ============================================================================

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "ok",
        "version": "0.1.0",
        "databases": {
            "skills": str(settings.skills_db_path.exists()),
            "rag": str(settings.rag_db_path.exists()),
            "memory": str(settings.memory_db_path.exists())
        }
    }


@app.get("/status")
async def status():
    """Detailed status endpoint"""
    async with get_skills_db() as db:
        cursor = await db.execute("SELECT COUNT(*) as count FROM skills")
        skills_count = (await cursor.fetchone())[0]

    async with get_memory_db() as db:
        cursor = await db.execute("SELECT COUNT(*) as count FROM conversations WHERE archived = 0")
        conversations_count = (await cursor.fetchone())[0]

        cursor = await db.execute("SELECT COUNT(*) as count FROM commit_embeddings")
        commits_count = (await cursor.fetchone())[0]

    return {
        "status": "ok",
        "stats": {
            "skills": skills_count,
            "active_conversations": conversations_count,
            "indexed_commits": commits_count
        },
        "config": {
            "odoo_lab_url": settings.odoo_lab_url,
            "embedding_model": settings.embedding_model,
            "repo_path": str(settings.repo_path)
        }
    }


# ============================================================================
# Skills Management
# ============================================================================

@app.get("/skills", response_model=List[Skill])
async def list_skills(
    status: Optional[str] = None,
    _: bool = Depends(verify_api_key)
):
    """List skills from local registry"""
    async with get_skills_db() as db:
        if status:
            cursor = await db.execute(
                "SELECT * FROM skills WHERE status = ? ORDER BY name",
                (status,)
            )
        else:
            cursor = await db.execute(
                "SELECT * FROM skills ORDER BY name"
            )

        rows = await cursor.fetchall()

        return [
            Skill(
                id=row[0],
                name=row[1],
                version=row[2],
                status=row[3],
                metadata=json.loads(row[4]) if row[4] else None,
                file_path=row[5]
            )
            for row in rows
        ]


@app.post("/skills", response_model=Skill)
async def create_skill(
    skill: Skill,
    _: bool = Depends(verify_api_key)
):
    """Create a new skill in local registry"""
    skill_id = skill.id or str(uuid.uuid4())
    now = datetime.utcnow().isoformat()

    async with get_skills_db() as db:
        await db.execute(
            """
            INSERT INTO skills (id, name, version, status, metadata, file_path, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                skill_id,
                skill.name,
                skill.version,
                skill.status,
                json.dumps(skill.metadata) if skill.metadata else None,
                skill.file_path,
                now,
                now
            )
        )
        await db.commit()

    return Skill(id=skill_id, **skill.dict(exclude={"id"}))


# ============================================================================
# Conversation Memory (Claude Memory)
# ============================================================================

@app.get("/conversations", response_model=List[Conversation])
async def list_conversations(
    session_id: Optional[str] = None,
    limit: int = 50,
    _: bool = Depends(verify_api_key)
):
    """List recent conversations"""
    async with get_memory_db() as db:
        if session_id:
            cursor = await db.execute(
                """
                SELECT id, session_id, user_id, messages, context, summary
                FROM conversations
                WHERE session_id = ? AND archived = 0
                ORDER BY updated_at DESC
                LIMIT ?
                """,
                (session_id, limit)
            )
        else:
            cursor = await db.execute(
                """
                SELECT id, session_id, user_id, messages, context, summary
                FROM conversations
                WHERE archived = 0
                ORDER BY updated_at DESC
                LIMIT ?
                """,
                (limit,)
            )

        rows = await cursor.fetchall()

        return [
            Conversation(
                id=row[0],
                session_id=row[1],
                user_id=row[2],
                messages=json.loads(row[3]) if row[3] else [],
                context=json.loads(row[4]) if row[4] else None,
                summary=row[5]
            )
            for row in rows
        ]


@app.post("/conversations", response_model=Conversation)
async def create_conversation(
    conversation: Conversation,
    _: bool = Depends(verify_api_key)
):
    """Create or update a conversation in memory"""
    conv_id = conversation.id or str(uuid.uuid4())
    now = datetime.utcnow().isoformat()

    async with get_memory_db() as db:
        await db.execute(
            """
            INSERT OR REPLACE INTO conversations
            (id, session_id, user_id, messages, context, summary, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                conv_id,
                conversation.session_id,
                conversation.user_id,
                json.dumps([m.dict() for m in conversation.messages]),
                json.dumps(conversation.context) if conversation.context else None,
                conversation.summary,
                now
            )
        )
        await db.commit()

    return Conversation(id=conv_id, **conversation.dict(exclude={"id"}))


# ============================================================================
# Commit Embeddings
# ============================================================================

@app.get("/commits", response_model=List[CommitInfo])
async def list_commits(
    author: Optional[str] = None,
    limit: int = 100,
    _: bool = Depends(verify_api_key)
):
    """List indexed commits"""
    async with get_memory_db() as db:
        if author:
            cursor = await db.execute(
                """
                SELECT id, commit_hash, author, commit_message, files_changed, commit_date
                FROM commit_embeddings
                WHERE author = ?
                ORDER BY commit_date DESC
                LIMIT ?
                """,
                (author, limit)
            )
        else:
            cursor = await db.execute(
                """
                SELECT id, commit_hash, author, commit_message, files_changed, commit_date
                FROM commit_embeddings
                ORDER BY commit_date DESC
                LIMIT ?
                """,
                (limit,)
            )

        rows = await cursor.fetchall()

        return [
            CommitInfo(
                id=row[0],
                commit_hash=row[1],
                author=row[2],
                commit_message=row[3],
                files_changed=json.loads(row[4]) if row[4] else [],
                commit_date=row[5]
            )
            for row in rows
        ]


# ============================================================================
# MCP Tools (Odoo Integration)
# ============================================================================

@app.get("/odoo/models")
async def list_odoo_models(_: bool = Depends(verify_api_key)):
    """List Odoo models from lab instance (stub - implement XML-RPC)"""
    # TODO: Implement Odoo XML-RPC client
    return {
        "status": "not_implemented",
        "message": "Odoo XML-RPC client to be implemented",
        "odoo_url": settings.odoo_lab_url
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8765)
