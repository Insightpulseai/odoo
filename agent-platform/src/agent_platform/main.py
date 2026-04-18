"""FastAPI gateway — entry point for agent-platform."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from agent_platform import __version__
from agent_platform.logging import configure_logging, get_logger
from agent_platform.settings import get_settings

_logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    settings = get_settings()
    configure_logging(settings.log_level)
    _logger.info("agent_platform.startup", version=__version__, env=settings.env)
    yield
    _logger.info("agent_platform.shutdown")


app = FastAPI(title="IPAI Agent Platform", version=__version__, lifespan=lifespan)


@app.get("/health")
async def health() -> JSONResponse:
    return JSONResponse({"status": "ok", "version": __version__})
