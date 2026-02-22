FROM odoo:19.0

USER root

# Install dependencies for common OCA modules
RUN apt-get update && apt-get install -y \
    python3-dev \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    libsasl2-dev \
    libldap2-dev \
    build-essential \
    libssl-dev \
    libffi-dev \
    libmysqlclient-dev \
    libjpeg-dev \
    libpq-dev \
    liblcms2-dev \
    libblas-dev \
    libatlas-base-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements if any
COPY ./requirements.txt /etc/odoo/requirements.txt
RUN pip3 install --no-cache-dir -r /etc/odoo/requirements.txt

# Create volume directories
RUN mkdir -p /var/lib/odoo/addons/selected \
    && chown -R odoo:odoo /var/lib/odoo

# Switch back to odoo user
USER odoo

# Set entrypoint and default command
ENTRYPOINT ["/usr/bin/entrypoint.sh"]
CMD ["odoo"]
