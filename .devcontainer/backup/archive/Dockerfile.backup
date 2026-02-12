ARG PYTHON_VERSION=3.12
FROM mcr.microsoft.com/devcontainers/python:${PYTHON_VERSION}

# Install system dependencies for Odoo 19 and DocFlow (OCR)
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    libffi-dev \
    libfreetype6-dev \
    libharfbuzz-dev \
    libfribidi-dev \
    libjpeg-dev \
    liblcms2-dev \
    libldap2-dev \
    libpq-dev \
    libsasl2-dev \
    libssl-dev \
    libwebp-dev \
    libxcb1-dev \
    libxml2-dev \
    libxmlsec1-dev \
    libxslt1-dev \
    libyaml-dev \
    zlib1g-dev \
    # OCR dependencies
    tesseract-ocr \
    poppler-utils \
    # Node.js for Odoo web assets (rtlcss, etc.)
    nodejs \
    npm \
    # PostgreSQL client
    postgresql-client \
    && apt-get clean -y && rm -rf /var/lib/apt/lists/*

# Install wkhtmltopdf for PDF report generation
# Odoo 19 requires wkhtmltopdf with patched Qt
RUN apt-get update && apt-get install -y --no-install-recommends wkhtmltopdf \
    && apt-get clean -y && rm -rf /var/lib/apt/lists/* \
    || echo "wkhtmltopdf not available in repo; install manually if needed"

# Install rtlcss for RTL language support
RUN npm install -g rtlcss

# Create odoo user and directories
RUN useradd -m -d /home/odoo -s /bin/bash odoo \
    && mkdir -p /var/lib/odoo \
    && chown -R odoo:odoo /var/lib/odoo

USER odoo
