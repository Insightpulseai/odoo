# =============================================================================
# Odoo 19 Development Image — OCA REST Framework Support
# =============================================================================
# Extends official odoo:19 with OCA Python dependencies baked in
# Prevents "uninstallable" state for base_rest and related modules
# =============================================================================

ARG ODOO_BASE_IMAGE=odoo:19
FROM ${ODOO_BASE_IMAGE}

USER root

# =============================================================================
# Install OCA REST Framework Python Dependencies
# =============================================================================
# Source: addons/oca/rest-framework/base_rest/__manifest__.py
# Baked at build time for deterministic deployments

COPY docker/requirements/oca_rest_framework.txt /tmp/oca_rest_framework.txt
RUN python3 -m pip install --no-cache-dir --break-system-packages -r /tmp/oca_rest_framework.txt \
    && rm /tmp/oca_rest_framework.txt

USER odoo

# =============================================================================
# Image Ready
# =============================================================================
# Contains: Odoo 19 CE + OCA REST framework Python dependencies
# Modules: base_rest, base_rest_datamodel installable without manual pip
# =============================================================================
