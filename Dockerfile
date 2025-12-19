# syntax=docker/dockerfile:1.7
# =============================================================================
# Odoo 18 CE + OCA Monorepo - Production Image
# =============================================================================
# OCA Structure:
#   addons/ipai/     - 22 production IPAI modules
#   external-src/    - 14 OCA repositories (source of truth)
#   archive/addons/  - 10 deprecated modules (excluded from build)
#
# Build Examples:
#   docker build -t erp-saas:2.0 .
#   docker build --build-arg BASE_REF=odoo:18.0-20251208 -t erp-saas:2.0 .
#
# DHI Alternative: See docker/hardened/Dockerfile.dhi for Docker Hardened baseline
# =============================================================================

# Pin exact base image (supports digest pinning for reproducibility)
ARG BASE_REF=odoo:18.0

FROM ${BASE_REF} AS base

USER root

# =============================================================================
# System Dependencies
# =============================================================================
# Minimal dependencies for OCA modules (reporting, xmlsec, pandas)
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    python3-pandas \
    python3-xlrd \
    python3-xlsxwriter \
    python3-xmlsec \
    && rm -rf /var/lib/apt/lists/*

# =============================================================================
# Directory Structure (OCA Monorepo)
# =============================================================================
RUN mkdir -p /mnt/addons/ipai \
    && mkdir -p /mnt/addons/oca \
    && mkdir -p /mnt/addons/ce

# =============================================================================
# Copy OCA Modules (external-src → /mnt/addons/oca)
# =============================================================================
# Source of truth: external-src/ (14 OCA git submodules)
# Assumes: git submodule update --init --recursive run locally or in CI
COPY ./external-src/reporting-engine /mnt/addons/oca/reporting-engine
COPY ./external-src/account-closing /mnt/addons/oca/account-closing
COPY ./external-src/account-financial-reporting /mnt/addons/oca/account-financial-reporting
COPY ./external-src/account-financial-tools /mnt/addons/oca/account-financial-tools
COPY ./external-src/account-invoicing /mnt/addons/oca/account-invoicing
COPY ./external-src/project /mnt/addons/oca/project
COPY ./external-src/hr-expense /mnt/addons/oca/hr-expense
COPY ./external-src/purchase-workflow /mnt/addons/oca/purchase-workflow
COPY ./external-src/maintenance /mnt/addons/oca/maintenance
COPY ./external-src/dms /mnt/addons/oca/dms
COPY ./external-src/calendar /mnt/addons/oca/calendar
COPY ./external-src/web /mnt/addons/oca/web
COPY ./external-src/contract /mnt/addons/oca/contract
COPY ./external-src/server-tools /mnt/addons/oca/server-tools

# =============================================================================
# Copy IPAI Production Modules (22 modules)
# =============================================================================
# New structure: addons/ipai/ contains all production modules
# Archive modules (archive/addons/) are NOT copied (excluded from build)
COPY ./addons/ipai /mnt/addons/ipai

# =============================================================================
# Copy Configuration
# =============================================================================
COPY ./deploy/odoo.conf /etc/odoo/odoo.conf

# =============================================================================
# Install Python Dependencies
# =============================================================================
# OCA module dependencies
RUN find /mnt/addons/oca -name "requirements.txt" -exec pip3 install --no-cache-dir --break-system-packages -r {} \; 2>/dev/null || true

# IPAI module dependencies
RUN find /mnt/addons/ipai -name "requirements.txt" -exec pip3 install --no-cache-dir --break-system-packages -r {} \; 2>/dev/null || true

# =============================================================================
# Permissions
# =============================================================================
RUN chown -R odoo:odoo /mnt/addons /etc/odoo/odoo.conf

USER odoo

# =============================================================================
# Environment Variables
# =============================================================================
# Database connection (overrideable via docker-compose)
ENV HOST=db \
    PORT=5432 \
    USER=odoo \
    PASSWORD=odoo \
    DB=odoo

ENV ODOO_RC=/etc/odoo/odoo.conf

# OCA Monorepo Addon Path
# Format: Odoo core → IPAI modules → OCA repos (each repo root contains modules)
ENV ODOO_ADDONS_PATH=/usr/lib/python3/dist-packages/odoo/addons,/mnt/addons/ipai,/mnt/addons/oca/reporting-engine,/mnt/addons/oca/account-closing,/mnt/addons/oca/account-financial-reporting,/mnt/addons/oca/account-financial-tools,/mnt/addons/oca/account-invoicing,/mnt/addons/oca/project,/mnt/addons/oca/hr-expense,/mnt/addons/oca/purchase-workflow,/mnt/addons/oca/maintenance,/mnt/addons/oca/dms,/mnt/addons/oca/calendar,/mnt/addons/oca/web,/mnt/addons/oca/contract,/mnt/addons/oca/server-tools

# =============================================================================
# Health Check
# =============================================================================
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8069/web/health || exit 1

# =============================================================================
# OCI Labels (Self-Describing Image)
# =============================================================================
LABEL org.opencontainers.image.title="ERP SaaS - Odoo 18 CE + OCA Monorepo" \
      org.opencontainers.image.description="Odoo 18 CE + 14 OCA repos + 22 IPAI production modules" \
      org.opencontainers.image.vendor="InsightPulse AI" \
      org.opencontainers.image.version="2.0.0-alpha" \
      org.opencontainers.image.base.name="${BASE_REF}" \
      com.insightpulseai.odoo.version="18.0" \
      com.insightpulseai.oca.repos="14" \
      com.insightpulseai.ipai.modules="22"

# =============================================================================
# Production Ready
# =============================================================================
# Image contains:
# - Odoo 18 CE base (official image or digest-pinned)
# - 14 OCA repositories (account, project, HR, reporting, server tools)
# - 22 IPAI production modules (Finance PPM, BIR compliance, core system)
# - Health check for orchestration
# - OCI labels for SBOM/provenance tracking
# - Environment variables for database connection
# =============================================================================
