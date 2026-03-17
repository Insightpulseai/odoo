FROM mcr.microsoft.com/devcontainers/base:jammy

# Install fundamental ERP dependencies
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
        libldap2-dev \
        libsasl2-dev \
        libxml2-dev \
        libxslt1-dev \
        zlib1g-dev \
        jq \
        curl \
        git \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

# The devcontainer features (Python 3.12, Node.js) will be layered on top automatically via devcontainer.json
