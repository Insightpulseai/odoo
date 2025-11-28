# ========================================================================================
# THE BLUEPRINT: Production-Grade Odoo 18 CE Image
# ========================================================================================
# Based on the "Modern Odoo Deployment Pipeline", this Dockerfile acts as the immutable
# recipe for your Marketing Agency ERP. It creates a self-contained artifact that includes
# all dependencies, OCA libraries, and custom logic required for "Activation".
# ========================================================================================

FROM odoo:18.0

# ----------------------------------------------------------------------------------------
# 0. METADATA & LABELS (The Artifact Signature)
# ----------------------------------------------------------------------------------------
LABEL org.opencontainers.image.title="IPAI Finance & PPM ERP" \
      org.opencontainers.image.description="All-in-one Agency ERP with Finance, Project, and Reporting capabilities" \
      org.opencontainers.image.vendor="Coding Partner" \
      org.opencontainers.image.version="18.0.1.0.0" \
      org.opencontainers.image.source="https://github.com/your-org/ipai-finance-ppm"

# ----------------------------------------------------------------------------------------
# 1. SYSTEM PREPARATION (Root Access)
# ----------------------------------------------------------------------------------------
USER root

# Set strict shell settings to fail the "Factory" build immediately if any command errors out
SHELL ["/bin/bash", "-xo", "pipefail", "-c"]

# Install system utilities required for fetching repos and Python packages.
# We also include 'postgresql-client' to allow the container to perform database
# checks during the "Activation" phase (e.g., waiting for DB to be ready).
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git \
        python3-pip \
        postgresql-client \
        curl \
        wget \
        vim \
    && rm -rf /var/lib/apt/lists/*

# ----------------------------------------------------------------------------------------
# 2. PYTHON DEPENDENCIES
# ----------------------------------------------------------------------------------------
# Install Python libraries required by specific OCA modules.
# - wheel: Ensures smooth compilation of binary packages.
# - openpyxl: Required by 'report_xlsx' for Excel exports.
# - pandas: Used for advanced financial analysis and data manipulation.
# - num2words: Essential for check printing (textual amounts) in Accounting.
# - xlwt: Legacy Excel support (often needed for older bank exports).
# - xlrd: Read Excel files
# - python-dateutil: Date utilities
RUN pip3 install --no-cache-dir --break-system-packages \
    wheel \
    openpyxl \
    pandas \
    num2words \
    xlwt \
    xlrd \
    python-dateutil

# ----------------------------------------------------------------------------------------
# 3. OCA "MUST-HAVE" MODULES (The Holy Grail Suite)
# ----------------------------------------------------------------------------------------
# We create a structured, dedicated directory for third-party addons.
# This separates community code from the core and your custom logic.
RUN mkdir -p /mnt/extra-addons/oca

# A. REPORTING ENGINE (The 'mis_builder' & 'report_xlsx' home)
# Critical for the "Financial Reporting" phase. Allows defining P&L/Balance Sheets
# directly in the UI without code deployment.
RUN git clone --depth 1 -b 18.0 https://github.com/OCA/reporting-engine.git /mnt/extra-addons/oca/reporting-engine

# B. FINANCIAL REPORTING (The 'account_financial_reporting' home)
# Fills the gap in Odoo Community Edition by providing standard audit reports:
# Trial Balance, General Ledger, and Aged Partner Balance.
RUN git clone --depth 1 -b 18.0 https://github.com/OCA/account-financial-reporting.git /mnt/extra-addons/oca/account-financial-reporting

# C. PROJECT MANAGEMENT (The 'project' home)
# Adds "Enterprise-grade" features like Task Dependencies (WBS enforcement)
# and Timelines, essential for the "Marketing Agency" workflow.
RUN git clone --depth 1 -b 18.0 https://github.com/OCA/project.git /mnt/extra-addons/oca/project

# D. WEB ENHANCEMENTS (The 'web' home)
# 'web_responsive' is crucial for mobile approval workflows, allowing Directors
# (CKVC) to sign off on tasks from mobile devices.
RUN git clone --depth 1 -b 18.0 https://github.com/OCA/web.git /mnt/extra-addons/oca/web

# E. SERVER TOOLS (Utilities and base extensions)
RUN git clone --depth 1 -b 18.0 https://github.com/OCA/server-tools.git /mnt/extra-addons/oca/server-tools

# ----------------------------------------------------------------------------------------
# 4. CUSTOM MODULE INSTALLATION (Your IP)
# ----------------------------------------------------------------------------------------
# We copy your custom 'ipai_finance_ppm' module into the container.
# This "bakes" your code into the image, making the artifact immutable.
COPY ./ipai_finance_ppm /mnt/extra-addons/custom/ipai_finance_ppm

# ----------------------------------------------------------------------------------------
# 5. CREATE LOG DIRECTORY
# ----------------------------------------------------------------------------------------
RUN mkdir -p /var/log/odoo && chown -R odoo:odoo /var/log/odoo

# ----------------------------------------------------------------------------------------
# 6. FINAL CONFIGURATION & ACTIVATION READINESS
# ----------------------------------------------------------------------------------------
# Ensure Odoo user owns all new files to prevent permission errors at runtime.
RUN chown -R odoo:odoo /mnt/extra-addons

# Configure the ODOO_ADDONS_PATH environment variable.
# This tells Odoo where to look for modules during the boot process.
# Order matters: Custom > OCA > Core.
ENV ODOO_ADDONS_PATH=/mnt/extra-addons/custom,/mnt/extra-addons/oca/reporting-engine,/mnt/extra-addons/oca/account-financial-reporting,/mnt/extra-addons/oca/project,/mnt/extra-addons/oca/web,/mnt/extra-addons/oca/server-tools,/usr/lib/python3/dist-packages/odoo/addons

# HEALTHCHECK: The Heartbeat of Activation
# This instruction tells Docker/Kubernetes how to check if Odoo is actually responsive.
# If the server is stuck or dead, the orchestrator will automatically restart it.
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD curl -f http://localhost:8069/web/health || exit 1

# Switch back to the Odoo user for security.
# Running as root in production is a security risk.
USER odoo

# The Entrypoint is inherited from the base image (./entrypoint.sh),
# which handles the DB connection and server startup.
