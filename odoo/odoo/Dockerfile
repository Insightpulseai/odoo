# syntax=docker/dockerfile:1.7
# =============================================================================
# Root Dockerfile — Delegates to docker/Dockerfile.unified
# =============================================================================
# The canonical production image definition lives at docker/Dockerfile.unified.
# This root Dockerfile exists for convenience (docker build .) and backwards
# compatibility. It produces the same image as:
#
#   docker build -f docker/Dockerfile.unified .
#
# =============================================================================

ARG ODOO_BASE=odoo:19
FROM ${ODOO_BASE}

ARG PROFILE=standard
ARG BUILD_DATE
ARG GIT_SHA

USER root

# System Dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    libpq-dev \
    libxml2-dev \
    libxslt1-dev \
    libsasl2-dev \
    libldap2-dev \
    libssl-dev \
    libffi-dev \
    libjpeg-dev \
    liblcms2-dev \
    zlib1g-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Directory Structure
RUN mkdir -p /opt/odoo/addons/oca \
    && mkdir -p /opt/odoo/addons/ipai

# OCA Python Dependencies
COPY docker/requirements/oca_rest_framework.txt /tmp/oca_rest_framework.txt
RUN pip3 install --no-cache-dir --break-system-packages \
    -r /tmp/oca_rest_framework.txt \
    && rm /tmp/oca_rest_framework.txt

# OCA Modules — Flatten from addons/oca
COPY ./addons/oca /tmp/oca-src

RUN set -eux; \
  module_count=0; \
  for repo in /tmp/oca-src/*; do \
    [ -d "$repo" ] || continue; \
    for mod in "$repo"/*; do \
      [ -d "$mod" ] || continue; \
      [ -f "$mod/__manifest__.py" ] || continue; \
      mod_name=$(basename "$mod"); \
      if [ -d "/opt/odoo/addons/oca/$mod_name" ]; then \
        echo "ERROR: OCA module collision: $mod_name"; \
        exit 1; \
      fi; \
      cp -a "$mod" "/opt/odoo/addons/oca/$mod_name"; \
      module_count=$((module_count + 1)); \
    done; \
  done; \
  echo "OCA modules flattened: $module_count"; \
  rm -rf /tmp/oca-src

RUN find /opt/odoo/addons/oca -name "requirements.txt" \
    -exec pip3 install --no-cache-dir --break-system-packages -r {} \; 2>/dev/null || true

# IPAI Custom Modules
COPY ./addons/ipai /opt/odoo/addons/ipai

RUN find /opt/odoo/addons/ipai -name "requirements.txt" \
    -exec pip3 install --no-cache-dir --break-system-packages -r {} \; 2>/dev/null || true

# Configuration
COPY ./config/prod/odoo.conf /etc/odoo/odoo.conf

# Permissions
RUN chown -R odoo:odoo /opt/odoo/addons /etc/odoo/odoo.conf

USER odoo

# Runtime Environment
ENV ODOO_RC=/etc/odoo/odoo.conf \
    IPAI_PROFILE=${PROFILE}

ENV ODOO_ADDONS_PATH=/usr/lib/python3/dist-packages/odoo/addons,/opt/odoo/addons/oca,/opt/odoo/addons/ipai

# Health Check
HEALTHCHECK --interval=30s --timeout=10s --start-period=90s --retries=3 \
    CMD curl -sf http://localhost:8069/web/health || exit 1

# OCI Labels
LABEL org.opencontainers.image.source="https://github.com/Insightpulseai/odoo" \
      org.opencontainers.image.title="IPAI Odoo Runtime" \
      org.opencontainers.image.description="Odoo 19 CE + OCA + InsightPulse AI modules" \
      org.opencontainers.image.vendor="InsightPulse AI" \
      com.insightpulseai.odoo.version="19.0" \
      com.insightpulseai.profile="${PROFILE}"

EXPOSE 8069 8072
