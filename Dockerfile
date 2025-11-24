# Custom Odoo CE image for InsightPulse
# Base image
FROM odoo:18.0

# Install required system dependencies for custom modules
USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        git \
        libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy custom addons baked into the image; owner set to odoo for runtime safety
COPY --chown=odoo:odoo ./addons /mnt/extra-addons/

# Install Python dependencies if a requirements file exists
RUN if [ -f /mnt/extra-addons/requirements.txt ]; then \
      pip install --no-cache-dir -r /mnt/extra-addons/requirements.txt; \
    fi

# Provide default configuration inside the image (override with bind mount in compose)
COPY --chown=odoo:odoo ./deploy/odoo.conf /etc/odoo/odoo.conf

# Default environment placeholders (override at runtime via compose/ENV)
ENV HOST=db \
    PORT=5432 \
    USER=odoo \
    PASSWORD=odoo \
    DB=odoo

# Run as non-root for security
USER odoo
