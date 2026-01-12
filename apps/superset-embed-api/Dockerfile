# =============================================================================
# Superset Embed API - Production Docker Image
# =============================================================================
# Self-signed JWT guest token service for Superset dashboard embedding
#
# Build:
#   docker build -t ghcr.io/jgtolentino/superset-embed-api:latest .
#
# Run:
#   docker run -p 3001:3001 \
#     -e SUPERSET_GUEST_TOKEN_SECRET=... \
#     -e SUPERSET_DOMAIN=https://superset.insightpulseai.net \
#     ghcr.io/jgtolentino/superset-embed-api:latest
# =============================================================================

FROM node:20-slim

WORKDIR /app

# Copy package files
COPY package.json package-lock.json* ./

# Install production dependencies only
RUN npm ci --only=production

# Copy source
COPY src/ ./src/

# Create non-root user
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 apiuser && \
    chown -R apiuser:nodejs /app

USER apiuser

# Expose port
EXPOSE 3001

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD node -e "fetch('http://localhost:3001/health').then(r => process.exit(r.ok ? 0 : 1)).catch(() => process.exit(1))"

# Start server
CMD ["node", "src/index.js"]
