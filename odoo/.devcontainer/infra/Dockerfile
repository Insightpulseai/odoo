FROM mcr.microsoft.com/devcontainers/base:jammy

# Install fundamental infrastructure dependencies
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
        make \
        postgresql-client \
        shellcheck \
        jq \
        curl \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

# The devcontainer features (Azure CLI, Terraform, AZD, TFLint) will be layered on top automatically via devcontainer.json
