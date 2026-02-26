---
description: Containerize application with Docker multi-stage builds and docker-compose
---

# Dockerize Application

## Goal

Containerize the application in a production-ready way with health checks, security, and compose orchestration.

## Steps

### 1. Detect Runtime & Build Steps

Analyze the application to determine:

- Runtime (Node.js, Python, Go, Odoo, etc.)
- Build steps (compile, bundle, install dependencies)
- Dependencies (database, Redis, message queue)
- Port(s) exposed
- Health check endpoint

### 2. Create Dockerfile

**Multi-stage build** (when applicable):

- Stage 1: Build dependencies and compile
- Stage 2: Production runtime with minimal image

**Security best practices**:

- Non-root user
- Minimal base image (alpine, slim, distroless)
- No secrets in layers
- Explicit COPY (avoid `COPY .`)

**Example (Node.js)**:

```dockerfile
# Stage 1: Build
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

# Stage 2: Production
FROM node:18-alpine
WORKDIR /app

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001

# Copy built assets
COPY --from=builder --chown=nodejs:nodejs /app/dist ./dist
COPY --from=builder --chown=nodejs:nodejs /app/node_modules ./node_modules
COPY --chown=nodejs:nodejs package.json ./

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD node healthcheck.js || exit 1

USER nodejs
EXPOSE 3000

CMD ["node", "dist/main.js"]
```

### 3. Create .dockerignore

Exclude unnecessary files from build context:

```
node_modules
npm-debug.log
.git
.env
.env.local
dist
build
coverage
*.log
.DS_Store
```

### 4. Create docker-compose.yml

Orchestrate application and dependencies:

```yaml
version: "3.8"

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - DATABASE_URL=postgresql://postgres:password@db:5432/myapp
      - REDIS_URL=redis://redis:6379
    env_file:
      - .env
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    healthcheck:
      test: ["CMD", "node", "healthcheck.js"]
      interval: 30s
      timeout: 3s
      retries: 3
      start_period: 5s

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=myapp
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

### 5. Create .env.example

Document environment variables:

```bash
# Application
NODE_ENV=production
PORT=3000

# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/myapp

# Redis
REDIS_URL=redis://localhost:6379

# API Keys (replace with actual values)
API_KEY=your-api-key-here
SECRET_KEY=your-secret-key-here
```

### 6. Verify

#### Build

```bash
docker build -t myapp:latest .
```

#### Run with Compose

```bash
docker-compose up -d
```

#### Health Check

```bash
# Wait for services to be healthy
docker-compose ps

# Test health endpoint
curl http://localhost:3000/health
```

#### Smoke Test

```bash
# Test main functionality
curl http://localhost:3000/api/status

# Check logs
docker-compose logs app

# Verify database connection
docker-compose exec app node -e "require('./dist/db').testConnection()"
```

## Output Format

### Files Created

- `Dockerfile` - Multi-stage production build
- `.dockerignore` - Build context exclusions
- `docker-compose.yml` - Orchestration config
- `.env.example` - Environment variable template
- `healthcheck.js` - Health check script (if needed)

### Verification Report

````markdown
## Docker Build Verification

### Build

✅ `docker build` completed successfully

- Image size: 234MB (alpine-based)
- Build time: 45s
- Layers: 12

### Compose Up

✅ All services started successfully

```bash
$ docker-compose ps
NAME                COMMAND                  SERVICE   STATUS
myapp-app-1         "node dist/main.js"      app       Up (healthy)
myapp-db-1          "docker-entrypoint.s…"   db        Up (healthy)
myapp-redis-1       "redis-server --appe…"   redis     Up
```
````

### Health Check

✅ Application health endpoint responding

```bash
$ curl http://localhost:3000/health
{"status":"ok","uptime":42,"database":"connected"}
```

### Smoke Test

✅ API endpoints functional
✅ Database connection verified
✅ Redis connection verified

### Security

✅ Non-root user (nodejs:1001)
✅ Minimal base image (alpine)
✅ No secrets in Dockerfile
✅ Health checks configured

```

## Verification
- [ ] Dockerfile uses multi-stage build
- [ ] Non-root user configured
- [ ] Health check implemented
- [ ] docker-compose.yml includes all dependencies
- [ ] .env.example documents all variables
- [ ] Build succeeds
- [ ] Compose up succeeds
- [ ] Health check passes
- [ ] Smoke tests pass
```
