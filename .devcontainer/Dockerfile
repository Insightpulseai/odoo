# =============================================================================
# .devcontainer/Dockerfile — InsightPulseAI Odoo 18 CE Dev Container
# Thin image: Python 3.12 + Odoo CE 18.0 (pinned) + system deps
# Runtime config mounted via Compose (config/dev/odoo.conf → /etc/odoo/odoo.conf)
# =============================================================================
FROM python:3.12-slim

ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID
ARG ODOO_BRANCH=18.0
ARG ODOO_COMMIT=3a6e478d483ac9b3ce323958d2b08ba0a37dbee7

ENV LANG=C.UTF-8 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ODOO_HOME=/opt/odoo \
    DEBIAN_FRONTEND=noninteractive

# ---------------------------------------------------------------------------
# System deps — Odoo + dev tools
# ---------------------------------------------------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl wget sudo zsh \
    build-essential \
    libpq-dev libxml2-dev libxslt1-dev \
    libldap2-dev libsasl2-dev libjpeg-dev \
    libffi-dev libssl-dev \
    postgresql-client \
    nodejs npm \
    && rm -rf /var/lib/apt/lists/*

# ---------------------------------------------------------------------------
# Create vscode user (matches official Anthropic devcontainer pattern)
# ---------------------------------------------------------------------------
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME -s /bin/zsh \
    && echo "$USERNAME ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# ---------------------------------------------------------------------------
# Clone Odoo 19.0 from GitHub — pinned to immutable commit
# Override ODOO_COMMIT at build time: --build-arg ODOO_COMMIT=<sha>
# ---------------------------------------------------------------------------
RUN git clone --branch ${ODOO_BRANCH} --single-branch --depth 1 \
    https://github.com/odoo/odoo.git ${ODOO_HOME} \
    && cd ${ODOO_HOME} && git fetch --depth 1 origin ${ODOO_COMMIT} \
    && git checkout ${ODOO_COMMIT} \
    && git log --oneline -1 > /etc/odoo_version.txt

# ---------------------------------------------------------------------------
# Python deps
# ---------------------------------------------------------------------------
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r ${ODOO_HOME}/requirements.txt \
    && pip install --no-cache-dir psycopg2-binary debugpy

# ---------------------------------------------------------------------------
# Dirs
# ---------------------------------------------------------------------------
RUN mkdir -p /var/lib/odoo /etc/odoo \
    && chown -R $USERNAME:$USERNAME /var/lib/odoo

WORKDIR /workspaces/odoo
USER $USERNAME
