# Custom Odoo 18 Image for InsightPulse ERP
FROM odoo:18.0

# Switch to root to install dependencies
USER root

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy all custom modules to Odoo addons path
COPY ./addons /mnt/extra-addons

# Copy Odoo configuration
COPY ./deploy/odoo.conf /etc/odoo/odoo.conf

# Install Python dependencies if requirements.txt exists
# Note: --break-system-packages required for Python 3.12+ in containers (PEP 668)
RUN if [ -f /mnt/extra-addons/requirements.txt ]; then \
      pip install --no-cache-dir --break-system-packages -r /mnt/extra-addons/requirements.txt; \
    fi

# Set proper ownership for Odoo user
RUN chown -R odoo:odoo /mnt/extra-addons /etc/odoo/odoo.conf

# Environment variable defaults
ENV HOST=db \
    PORT=5432 \
    USER=odoo \
    PASSWORD=odoo \
    DB=odoo

ENV ODOO_RC=/etc/odoo/odoo.conf

# Switch back to Odoo user for security
USER odoo

# Health check for container orchestration
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8069/web/health || exit 1
