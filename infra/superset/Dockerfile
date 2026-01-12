# =============================================================================
# SUPERSET - Production Docker Image
# =============================================================================
# Custom Superset image with:
# - Embedded dashboard support
# - Guest token JWT authentication
# - Additional database drivers
# - Playwright for thumbnails
#
# Build:
#   docker build -t ghcr.io/jgtolentino/ipai-superset:latest .
#
# Push:
#   docker push ghcr.io/jgtolentino/ipai-superset:latest
# =============================================================================

FROM apache/superset:latest

USER root

# Install system dependencies for Playwright
ENV PLAYWRIGHT_BROWSERS_PATH=/usr/local/share/playwright-browsers

# Install Python packages:
# - psycopg2-binary: PostgreSQL driver
# - pymssql: SQL Server driver
# - Authlib: OAuth2/JWT support
# - openpyxl: Excel export
# - Pillow: Image processing
# - playwright: Dashboard thumbnails
RUN . /app/.venv/bin/activate && \
    pip install --no-cache-dir \
      psycopg2-binary \
      pymssql \
      Authlib \
      openpyxl \
      Pillow \
      playwright && \
    playwright install-deps && \
    PLAYWRIGHT_BROWSERS_PATH=/usr/local/share/playwright-browsers playwright install chromium

# Copy custom Superset configuration
COPY superset_config.py /app/pythonpath/superset_config.py

# Set ownership for Superset user
RUN chown -R superset:superset /app/pythonpath

USER superset

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8088/health || exit 1

# Default command
CMD ["/app/docker/entrypoints/run-server.sh"]
