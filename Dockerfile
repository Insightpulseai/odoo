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
# Copy OCA Modules (external-src → /mnt/addons/oca - FLATTENED)
# =============================================================================
# Source of truth: external-src/ (OCA git submodules)
# Strategy: Flatten all OCA modules into single /mnt/addons/oca root
# Benefit: Single addon path instead of 14+ enumerated paths

# Copy vendor source to temporary location
COPY ./external-src /tmp/external-src

# Flatten OCA modules with collision detection
RUN set -eux; \
  mkdir -p /mnt/addons/oca; \
  echo "Flattening OCA modules from external-src..."; \
  module_count=0; \
  for repo in /tmp/external-src/*; do \
    [ -d "$repo" ] || continue; \
    repo_name=$(basename "$repo"); \
    echo "Processing repo: $repo_name"; \
    for mod in "$repo"/*; do \
      [ -d "$mod" ] || continue; \
      [ -f "$mod/__manifest__.py" ] || continue; \
      mod_name=$(basename "$mod"); \
      if [ -d "/mnt/addons/oca/$mod_name" ]; then \
        echo "ERROR: OCA module name collision: $mod_name"; \
        echo "  Already exists in: /mnt/addons/oca/$mod_name"; \
        echo "  Trying to copy from: $mod"; \
        exit 1; \
      fi; \
      cp -a "$mod" "/mnt/addons/oca/$mod_name"; \
      module_count=$((module_count + 1)); \
    done; \
  done; \
  echo ""; \
  echo "========================================"; \
  echo "OCA Module Flatten Summary"; \
  echo "========================================"; \
  echo "Total modules flattened: $module_count"; \
  find /mnt/addons/oca -maxdepth 1 -type d -name "*" ! -name "oca" | sort; \
  echo "========================================"; \
  rm -rf /tmp/external-src

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

# OCA Monorepo Addon Path (Aggregated)
# Format: Odoo core → IPAI modules → OCA modules (flattened)
# All OCA modules flattened into /mnt/addons/oca during build
ENV ODOO_ADDONS_PATH=/usr/lib/python3/dist-packages/odoo/addons,/mnt/addons/ipai,/mnt/addons/oca

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
