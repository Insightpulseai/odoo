# apps/bot-proxy/Dockerfile
# Lightweight Python image running the 6-agent Bot Framework proxy.
# Built and pushed by .github/workflows/build-bot-proxy.yml or manually:
#   docker build -t ipaiodoodevacr.azurecr.io/ipai-bot-proxy:latest .
#   az acr login --name ipaiodoodevacr
#   docker push ipaiodoodevacr.azurecr.io/ipai-bot-proxy:latest

FROM python:3.12-slim AS base

# Non-root user for ACA runtime
RUN groupadd --gid 1000 app && useradd --uid 1000 --gid app --shell /bin/bash --create-home app

WORKDIR /app

# Install deps first (leverage docker layer cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY src/ ./src/

USER app

EXPOSE 8088
ENV PORT=8088 \
    PYTHONUNBUFFERED=1 \
    LOG_LEVEL=INFO

# Healthcheck — ACA liveness/readiness probes in the Bicep module
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8088/healthz', timeout=3)" || exit 1

CMD ["python", "-m", "src.main"]
