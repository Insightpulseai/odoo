# Custom Odoo 18 Image for InsightPulse ERP
FROM odoo:18.0

# Switch to root to install dependencies
USER root

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    git \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy all custom modules to Odoo addons path
COPY ./addons /mnt/extra-addons

# Copy Odoo configuration
COPY ./deploy/odoo.conf /etc/odoo/odoo.conf

# Set proper ownership for Odoo user
RUN chown -R odoo:odoo /mnt/extra-addons /etc/odoo/odoo.conf

# Switch back to Odoo user for security
USER odoo

# The image is now ready for production deployment
