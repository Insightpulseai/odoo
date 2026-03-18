FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
COPY ../../packages/odoo-docs-kb /app/packages/odoo-docs-kb
COPY ../../agents/knowledge/odoo19_docs /app/agents/knowledge/odoo19_docs

ENV PYTHONPATH=/app:/app/packages

EXPOSE 8080
CMD ["uvicorn", "service:app", "--host", "0.0.0.0", "--port", "8080"]
