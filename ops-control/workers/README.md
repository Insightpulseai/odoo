# OCR Parallel Workers

This directory contains the worker processes that claim and execute queued runs in parallel, mimicking the Claude Code Web / Codex experience.

## Architecture

```
┌─────────────┐      ┌──────────────────┐      ┌─────────────┐
│  Figma Make │ ────▶│  Supabase Edge   │◀──── │   Worker 1  │
│     UI      │      │  Function (API)  │      │ (concur=4)  │
└─────────────┘      └──────────────────┘      └─────────────┘
                              ▲                        
                              │                        
                              ▼                        
                     ┌──────────────────┐      ┌─────────────┐
                     │   ops.runs       │      │   Worker 2  │
                     │   (SKIP LOCKED)  │◀──── │ (concur=4)  │
                     └──────────────────┘      └─────────────┘
```

**Key features:**
- **SKIP LOCKED claiming** prevents race conditions (N workers can poll concurrently)
- **Heartbeat mechanism** keeps runs "alive" and allows recovery of stuck jobs
- **Cancelable** via UI (sets `canceled_at` timestamp)
- **Lane-based** UI organization (A/B/C/D lanes per session)

## Quick Start

### 1. Build the worker

```bash
cd workers
npm install
```

### 2. Set environment variables

```bash
export SUPABASE_FN_URL="https://<project-ref>.supabase.co/functions/v1/ops-executor"
export SUPABASE_ANON="<your-anon-key>"
export WORKER_ID="ocr-worker-1"
export CONCURRENCY=4
export BATCH=1
```

### 3. Run locally (dev mode)

```bash
npm run dev
```

### 4. Run in production

Deploy to:
- **DigitalOcean App Platform** (Dockerfile below)
- **Kubernetes** (Deployment with replicas=N)
- **GitHub Actions** (long-running workflow)
- **Cloud Run / Lambda** (not ideal for polling; use DO/K8s instead)

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SUPABASE_FN_URL` | ✅ | - | Edge function base URL |
| `SUPABASE_ANON` | ✅ | - | Supabase anon key |
| `WORKER_ID` | ❌ | `worker-<random>` | Unique worker identifier |
| `CONCURRENCY` | ❌ | `4` | Number of parallel execution slots |
| `BATCH` | ❌ | `1` | Runs to claim per request |
| `POLL_INTERVAL_MS` | ❌ | `800` | Milliseconds between polls when queue is empty |

## Example Deployment (DigitalOcean)

**Dockerfile:**

\`\`\`dockerfile
FROM node:18-alpine
WORKDIR /app
COPY workers/package*.json ./
RUN npm ci --only=production
COPY workers/ocr-worker.js ./
CMD ["node", "ocr-worker.js"]
\`\`\`

**Deploy:**

\`\`\`bash
# Build and push to registry
docker build -t <registry>/ocr-worker:latest .
docker push <registry>/ocr-worker:latest

# Deploy to DO App Platform via doctl or UI
# Set env vars in the app settings
\`\`\`

## Example Deployment (Kubernetes)

\`\`\`yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ocr-worker
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ocr-worker
  template:
    metadata:
      labels:
        app: ocr-worker
    spec:
      containers:
      - name: worker
        image: <registry>/ocr-worker:latest
        env:
        - name: SUPABASE_FN_URL
          value: "https://<ref>.supabase.co/functions/v1/ops-executor"
        - name: SUPABASE_ANON
          valueFrom:
            secretKeyRef:
              name: supabase-secrets
              key: anon-key
        - name: WORKER_ID
          valueFrom:
            fieldRef:
              fieldPath: metadata.name
        - name: CONCURRENCY
          value: "4"
        resources:
          requests:
            cpu: 100m
            memory: 256Mi
          limits:
            cpu: 500m
            memory: 512Mi
\`\`\`

## Verifying Parallel Execution

### 1. Check active workers in database

\`\`\`sql
select distinct claimed_by, count(*) 
from ops.runs 
where status = 'running'
group by claimed_by;
\`\`\`

### 2. Watch runs being claimed (realtime)

\`\`\`sql
select id, status, claimed_by, claimed_at, heartbeat_at, lane
from ops.runs
order by created_at desc
limit 20;
\`\`\`

### 3. Check for stuck runs (heartbeat > 10s old)

\`\`\`sql
select id, claimed_by, heartbeat_at, 
       extract(epoch from (now() - heartbeat_at)) as seconds_since_heartbeat
from ops.runs
where status = 'running'
  and heartbeat_at < now() - interval '10 seconds';
\`\`\`

## Scaling

- **Horizontal:** Deploy more worker instances (each claims independently via SKIP LOCKED)
- **Vertical:** Increase `CONCURRENCY` per worker (more parallel slots)
- **Priority:** Set `priority` field on runs (lower = higher priority)

Example: 3 workers × 4 concurrency = 12 parallel runs

## Next Steps

1. **Wire real MCP tools** instead of simulation (replace tool stubs in executor)
2. **Add workspace isolation** (repo checkout + branch per lane)
3. **Stream artifacts to UI** (diffs, logs, manifests)
4. **Push notifications** (webhook to Poke/Slack when run needs input)
