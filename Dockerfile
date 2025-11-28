# -----------------------------------------------------------------------------
# TARGET: Odoo 18 CE + OCA Production Image
# Build: docker build -t odoo-ce-prod .
# Save:  docker save -o odoo_ce_prod.tar odoo-ce-prod
# -----------------------------------------------------------------------------
FROM odoo:18.0

USER root

# 1. Install System Dependencies for OCA Modules
# (Some OCA reporting tools need xmlsec1, pandas, etc.)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    git \
    libssl-dev \
    python3-pandas \
    python3-xlrd \
    python3-xlsxwriter \
    python3-xmlsec \
    gcc \
    libxml2-dev \
    libxslt1-dev \
    libsasl2-dev \
    libldap2-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 2. Prepare Directories
RUN mkdir -p /mnt/extra-addons \
    && mkdir -p /mnt/oca-addons

# 3. Copy OCA Submodules (The "Muscle" - 14 Repositories)
# Assumes `git submodule update --init --recursive` was run locally
COPY ./external-src/reporting-engine /mnt/oca-addons/reporting-engine
COPY ./external-src/account-closing /mnt/oca-addons/account-closing
COPY ./external-src/account-financial-reporting /mnt/oca-addons/account-financial-reporting
COPY ./external-src/account-financial-tools /mnt/oca-addons/account-financial-tools
COPY ./external-src/account-invoicing /mnt/oca-addons/account-invoicing
COPY ./external-src/project /mnt/oca-addons/project
COPY ./external-src/hr-expense /mnt/oca-addons/hr-expense
COPY ./external-src/purchase-workflow /mnt/oca-addons/purchase-workflow
COPY ./external-src/maintenance /mnt/oca-addons/maintenance
COPY ./external-src/dms /mnt/oca-addons/dms
COPY ./external-src/calendar /mnt/oca-addons/calendar
COPY ./external-src/web /mnt/oca-addons/web
COPY ./external-src/contract /mnt/oca-addons/contract
COPY ./external-src/server-tools /mnt/oca-addons/server-tools

# 4. Copy Custom Delta Modules
# - ipai_bir_compliance (Tax Shield)
# - ipai_ce_cleaner (Enterprise upsell hiding)
# - tbwa_spectra_integration (Company-specific export)
COPY ./addons /mnt/extra-addons

# 5. Copy Configuration
COPY ./deploy/odoo.conf /etc/odoo/odoo.conf

# 6. Install Python Dependencies from OCA modules and custom addons
# Note: --break-system-packages required for Python 3.12+ in containers (PEP 668)
RUN find /mnt/oca-addons -name "requirements.txt" -exec pip3 install --no-cache-dir --break-system-packages -r {} \; 2>/dev/null || true
RUN if [ -f /mnt/extra-addons/requirements.txt ]; then \
      pip install --no-cache-dir --break-system-packages -r /mnt/extra-addons/requirements.txt; \
    fi

# 7. Fix Permissions
RUN chown -R odoo:odoo /mnt/extra-addons /mnt/oca-addons /etc/odoo/odoo.conf

USER odoo

# 8. Environment Variables for Database Connection
ENV HOST=db \
    PORT=5432 \
    USER=odoo \
    PASSWORD=odoo \
    DB=odoo

ENV ODOO_RC=/etc/odoo/odoo.conf

# 9. Define the Addons Path via Environment Variable
# This tells Odoo where to look for modules inside the container
ENV ODOO_ADDONS_PATH=/usr/lib/python3/dist-packages/odoo/addons,/mnt/extra-addons,/mnt/oca-addons/reporting-engine,/mnt/oca-addons/account-closing,/mnt/oca-addons/account-financial-reporting,/mnt/oca-addons/account-financial-tools,/mnt/oca-addons/account-invoicing,/mnt/oca-addons/project,/mnt/oca-addons/hr-expense,/mnt/oca-addons/purchase-workflow,/mnt/oca-addons/maintenance,/mnt/oca-addons/dms,/mnt/oca-addons/calendar,/mnt/oca-addons/web,/mnt/oca-addons/contract,/mnt/oca-addons/server-tools

# 10. Health Check for Container Orchestration
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8069/web/health || exit 1

# The image is now production-ready with:
# - Odoo 18 CE base
# - 14 OCA repositories
# - 3 custom delta modules (Tax Shield, CE Cleaner, Spectra)
# - Health check for orchestration
# - Database environment variables
