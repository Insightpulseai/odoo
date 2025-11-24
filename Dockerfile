# Use the official Odoo 18 base image
FROM odoo:18.0

# Switch to root to perform necessary file operations
USER root

# Install system dependencies (DigitalOcean recommendation)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    git \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy your custom modules into the standard Odoo addons path
# This path is already configured in the default Odoo entrypoint script.
COPY ./addons /mnt/extra-addons

# Copy your custom configuration file
COPY ./deploy/odoo.conf /etc/odoo/odoo.conf

# Install Python dependencies from custom modules (if requirements.txt exists)
# RUN pip install --no-cache-dir -r /mnt/extra-addons/requirements.txt

# Set ownership back to the 'odoo' user for security
RUN chown -R odoo:odoo /mnt/extra-addons /etc/odoo/odoo.conf

# Switch back to the non-root user
USER odoo

# The image is now production-ready.
