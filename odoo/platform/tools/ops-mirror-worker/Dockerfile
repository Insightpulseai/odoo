FROM python:3.11-slim

LABEL maintainer="InsightPulse AI <ops@insightpulseai.com>"
LABEL description="OPS Mirror Worker - Odoo outbox drainer to Supabase"

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy worker script
COPY worker.py .

# Environment variables (set at runtime)
ENV POLL_SECONDS=5 \
    BATCH_SIZE=25 \
    MAX_ATTEMPTS=10 \
    PYTHONUNBUFFERED=1

CMD ["python", "worker.py"]
