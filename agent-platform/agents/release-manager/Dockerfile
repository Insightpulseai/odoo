FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    STAMP=dev \
    PORT=8000

WORKDIR /app

RUN apt-get update \
 && apt-get install -y --no-install-recommends ca-certificates \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY agent_orchestrator.py odoo_health_agent.py ./
COPY static/ ./static/

RUN useradd --create-home --uid 10001 rm \
 && mkdir -p /var/lib/pulser/checkpoints \
 && chown -R rm:rm /app /var/lib/pulser
USER rm

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health').read()" || exit 1

CMD ["uvicorn", "agent_orchestrator:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "info"]
