# =============================================================================
# Unified Odoo 18 CE + OCA Production Image
# =============================================================================
# Multi-stage build with profile support for flexibility and maintainability
#
# Build Profiles:
#   PROFILE=standard (default) - Minimal production set (14 OCA repos, 5 modules)
#   PROFILE=parity            - Enterprise parity set (32 OCA repos, all 27 modules)
#
# Build Examples:
#   docker build --build-arg PROFILE=standard -t odoo-ce:prod .
#   docker build --build-arg PROFILE=parity -t odoo-ce:enterprise-parity .
#
# Aligns with:
#   - spec/ipai-control-center/constitution.md (5-module architecture)
#   - docs/adr/ADR-0001-NO-NOTION-INTEGRATION.md (no SaaS integrations)
#   - docs/adr/ADR-0002-UNIFIED-DOCKERFILE.md (unified build approach)
# =============================================================================

# -----------------------------------------------------------------------------
# Stage 0: Base - System dependencies and directory structure
# -----------------------------------------------------------------------------
FROM odoo:18.0 AS base

USER root

# Install system dependencies for OCA modules
# (reporting tools need xmlsec1, pandas, financial tools need various libs)
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

# Prepare directories for addons
RUN mkdir -p /mnt/extra-addons /mnt/oca-addons

# -----------------------------------------------------------------------------
# Stage 1: OCA Standard - Minimal production set (14 repositories)
# -----------------------------------------------------------------------------
FROM base AS oca-standard

# Copy OCA submodules (assumes `git submodule update --init --recursive`)
# Standard set: Accounting, Project, HR Expense, Purchase, Maintenance, DMS, Web, Server Tools
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

# Build addons path for standard profile (14 OCA repos)
ENV ODOO_ADDONS_PATH_OCA=/mnt/oca-addons/reporting-engine,/mnt/oca-addons/account-closing,/mnt/oca-addons/account-financial-reporting,/mnt/oca-addons/account-financial-tools,/mnt/oca-addons/account-invoicing,/mnt/oca-addons/project,/mnt/oca-addons/hr-expense,/mnt/oca-addons/purchase-workflow,/mnt/oca-addons/maintenance,/mnt/oca-addons/dms,/mnt/oca-addons/calendar,/mnt/oca-addons/web,/mnt/oca-addons/contract,/mnt/oca-addons/server-tools

# -----------------------------------------------------------------------------
# Stage 2: OCA Parity - Enterprise parity set (32 repositories)
# -----------------------------------------------------------------------------
FROM base AS oca-parity

# Copy all OCA submodules for enterprise parity
# Standard set (14 repos)
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

# Additional parity repos (18 repos)
COPY ./external-src/account-reconcile /mnt/oca-addons/account-reconcile 2>/dev/null || true
COPY ./external-src/bank-payment /mnt/oca-addons/bank-payment 2>/dev/null || true
COPY ./external-src/commission /mnt/oca-addons/commission 2>/dev/null || true
COPY ./external-src/crm /mnt/oca-addons/crm 2>/dev/null || true
COPY ./external-src/field-service /mnt/oca-addons/field-service 2>/dev/null || true
COPY ./external-src/helpdesk /mnt/oca-addons/helpdesk 2>/dev/null || true
COPY ./external-src/hr /mnt/oca-addons/hr 2>/dev/null || true
COPY ./external-src/knowledge /mnt/oca-addons/knowledge 2>/dev/null || true
COPY ./external-src/manufacture /mnt/oca-addons/manufacture 2>/dev/null || true
COPY ./external-src/mis-builder /mnt/oca-addons/mis-builder 2>/dev/null || true
COPY ./external-src/partner-contact /mnt/oca-addons/partner-contact 2>/dev/null || true
COPY ./external-src/payroll /mnt/oca-addons/payroll 2>/dev/null || true
COPY ./external-src/sale-workflow /mnt/oca-addons/sale-workflow 2>/dev/null || true
COPY ./external-src/server-ux /mnt/oca-addons/server-ux 2>/dev/null || true
COPY ./external-src/social /mnt/oca-addons/social 2>/dev/null || true
COPY ./external-src/stock-logistics-warehouse /mnt/oca-addons/stock-logistics-warehouse 2>/dev/null || true
COPY ./external-src/stock-logistics-workflow /mnt/oca-addons/stock-logistics-workflow 2>/dev/null || true
COPY ./external-src/timesheet /mnt/oca-addons/timesheet 2>/dev/null || true

# Build addons path for parity profile (all available OCA repos)
ENV ODOO_ADDONS_PATH_OCA=/mnt/oca-addons/reporting-engine,/mnt/oca-addons/account-closing,/mnt/oca-addons/account-financial-reporting,/mnt/oca-addons/account-financial-tools,/mnt/oca-addons/account-invoicing,/mnt/oca-addons/account-reconcile,/mnt/oca-addons/bank-payment,/mnt/oca-addons/project,/mnt/oca-addons/timesheet,/mnt/oca-addons/contract,/mnt/oca-addons/field-service,/mnt/oca-addons/hr-expense,/mnt/oca-addons/hr,/mnt/oca-addons/payroll,/mnt/oca-addons/purchase-workflow,/mnt/oca-addons/sale-workflow,/mnt/oca-addons/crm,/mnt/oca-addons/commission,/mnt/oca-addons/stock-logistics-warehouse,/mnt/oca-addons/stock-logistics-workflow,/mnt/oca-addons/helpdesk,/mnt/oca-addons/manufacture,/mnt/oca-addons/maintenance,/mnt/oca-addons/reporting-engine,/mnt/oca-addons/mis-builder,/mnt/oca-addons/server-tools,/mnt/oca-addons/server-ux,/mnt/oca-addons/web,/mnt/oca-addons/dms,/mnt/oca-addons/knowledge,/mnt/oca-addons/partner-contact,/mnt/oca-addons/social,/mnt/oca-addons/calendar

# -----------------------------------------------------------------------------
# Stage 3: Runtime - Final image with selected profile
# -----------------------------------------------------------------------------
ARG PROFILE=standard
FROM oca-${PROFILE} AS runtime

# Copy custom IPAI modules
# For standard profile: 5-module architecture (ipai_workspace_core, ipai_ppm, ipai_advisor, ipai_workbooks, ipai_connectors)
# For parity profile: All 27 existing ipai_* modules (backward compatibility)
ARG PROFILE=standard

# Always copy 5-module architecture (new standard)
COPY ./addons/ipai_workspace_core /mnt/extra-addons/ipai_workspace_core 2>/dev/null || true
COPY ./addons/ipai_ppm /mnt/extra-addons/ipai_ppm 2>/dev/null || true
COPY ./addons/ipai_advisor /mnt/extra-addons/ipai_advisor 2>/dev/null || true
COPY ./addons/ipai_workbooks /mnt/extra-addons/ipai_workbooks 2>/dev/null || true
COPY ./addons/ipai_connectors /mnt/extra-addons/ipai_connectors 2>/dev/null || true

# For parity profile: copy all 27 legacy modules for backward compatibility
RUN if [ "$PROFILE" = "parity" ]; then \
    echo "Parity profile: Copying all ipai_* modules for backward compatibility"; \
fi

# Copy all addons (handles both 5-module and 27-module scenarios)
COPY ./addons /mnt/extra-addons

# Copy Odoo configuration
COPY ./deploy/odoo.conf /etc/odoo/odoo.conf

# Install Python dependencies from OCA modules and custom addons
# Note: --break-system-packages required for Python 3.12+ in containers (PEP 668)
RUN find /mnt/oca-addons -name "requirements.txt" -exec pip3 install --no-cache-dir --break-system-packages -r {} \; 2>/dev/null || true
RUN if [ -f /mnt/extra-addons/requirements.txt ]; then \
      pip install --no-cache-dir --break-system-packages -r /mnt/extra-addons/requirements.txt; \
    fi

# Fix permissions
RUN chown -R odoo:odoo /mnt/extra-addons /mnt/oca-addons /etc/odoo/odoo.conf

USER odoo

# Environment variables for database connection
ENV HOST=db \
    PORT=5432 \
    USER=odoo \
    PASSWORD=odoo \
    DB=odoo

ENV ODOO_RC=/etc/odoo/odoo.conf

# IPAI Stack Integration Environment Variables (Supabase, n8n, Mattermost, Superset)
# Values injected from docker-compose.yml or deployment platform
ENV SUPABASE_URL="" \
    SUPABASE_SERVICE_ROLE_KEY="" \
    N8N_BASE_URL="" \
    N8N_WEBHOOK_SECRET="" \
    MATTERMOST_BASE_URL="" \
    MATTERMOST_BOT_TOKEN="" \
    SUPERSET_BASE_URL="" \
    SUPERSET_EMBED_SECRET=""

# Build final addons path (CE base + custom + OCA from selected profile)
ENV ODOO_ADDONS_PATH=/usr/lib/python3/dist-packages/odoo/addons,/mnt/extra-addons,${ODOO_ADDONS_PATH_OCA}

# Health check for container orchestration
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8069/web/health || exit 1

# Image Metadata
LABEL maintainer="InsightPulse AI <platform@insightpulseai.net>" \
      org.opencontainers.image.title="Odoo CE 18 + OCA + IPAI" \
      org.opencontainers.image.description="Production-ready Odoo CE 18 with OCA modules and IPAI custom addons" \
      org.opencontainers.image.vendor="InsightPulse AI" \
      org.opencontainers.image.version="18.0" \
      com.insightpulseai.profile="${PROFILE}" \
      com.insightpulseai.architecture="5-module (standard) or 27-module (parity)" \
      com.insightpulseai.stack="Supabase+n8n+Mattermost+Superset" \
      com.insightpulseai.adr="ADR-0001 (No Notion), ADR-0002 (Unified Dockerfile)"

# =============================================================================
# The image is now production-ready with:
# - Odoo 18 CE base
# - Profile-based OCA repositories (14 standard, 32 parity)
# - IPAI custom modules (5-module architecture or 27-module legacy)
# - IPAI stack integration (Supabase, n8n, Mattermost, Superset)
# - No enterprise SaaS integrations (Notion/Concur/Cheqroom/SAP removed)
# - Health check for orchestration
# =============================================================================
