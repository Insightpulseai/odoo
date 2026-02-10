ARG PYTHON_VERSION=3.11
FROM mcr.microsoft.com/devcontainers/python:${PYTHON_VERSION}

# Install system dependencies for Odoo and DocFlow (OCR)
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libxml2-dev \
    libxslt1-dev \
    libjpeg-dev \
    zlib1g-dev \
    libldap2-dev \
    libsasl2-dev \
    libffi-dev \
    libssl-dev \
    tesseract-ocr \
    poppler-utils \
    && apt-get clean -y && rm -rf /var/lib/apt/lists/*
# Note: wkhtmltopdf removed (not available in Debian Trixie)
# Install separately if needed: https://wkhtmltopdf.org/downloads.html
