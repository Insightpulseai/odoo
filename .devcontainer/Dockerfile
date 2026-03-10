# =============================================================================
# .devcontainer/Dockerfile — InsightPulseAI Odoo 19 CE Dev Container
# For Claude Code --dangerously-skip-permissions safe usage
# Based on official Anthropic devcontainer pattern
# =============================================================================
FROM python:3.12-slim

ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

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
    iproute2 iptables \
    dnsutils \
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
ARG ODOO_BRANCH=19.0
ARG ODOO_COMMIT=3a6e478d483ac9b3ce323958d2b08ba0a37dbee7
RUN git clone --branch ${ODOO_BRANCH} --single-branch \
    https://github.com/odoo/odoo.git ${ODOO_HOME} \
    && cd ${ODOO_HOME} && git checkout ${ODOO_COMMIT} \
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
RUN mkdir -p /mnt/extra-addons /mnt/oca-addons /var/lib/odoo /etc/odoo \
    && chown -R $USERNAME:$USERNAME /mnt/extra-addons /mnt/oca-addons /var/lib/odoo

# ---------------------------------------------------------------------------
# Odoo test config pre-baked
# ---------------------------------------------------------------------------
COPY .devcontainer/odoo.devcontainer.conf /etc/odoo/odoo.conf
RUN chown $USERNAME /etc/odoo/odoo.conf

WORKDIR /workspaces/odoo
USER $USERNAME
