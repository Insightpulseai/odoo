#!/bin/bash
set -e

# Setup venv if not exists
VENV_DIR="/tmp/docflow_venv_312"
if [ ! -d "$VENV_DIR" ]; then
    python3.12 -m venv "$VENV_DIR" --without-pip
    source "$VENV_DIR/bin/activate"
    curl -sS https://bootstrap.pypa.io/get-pip.py | python
    pip install -U pip
    pip install -e docflow-agentic-finance
    pip install python-dotenv
else
    source "$VENV_DIR/bin/activate"
fi

# 1. Smoke Test: Expect Failure (Missing LLM_MODEL)
echo "Running Smoke Test 1: Expect Failure..."
# Unset vars to be sure
unset LLM_MODEL
unset DOCFLOW_INBOX_DIR
unset DOCFLOW_ARCHIVE_DIR

if (cd docflow-agentic-finance && python3 -m src.docflow.runner); then
    echo "❌ Failed: Runner should have failed without env vars"
    exit 1
else
    echo "✅ Passed: Runner failed as expected"
fi

# 2. Smoke Test: Expect Success (Minimal Env)
echo "Running Smoke Test 2: Expect Success..."
export DOCFLOW_INBOX_DIR=./inbox
export DOCFLOW_ARCHIVE_DIR=./archive
export DOCFLOW_ARTIFACTS_DIR=./artifacts
export LLM_MODEL=dummy-smoke
export OPENAI_API_KEY=dummy

# Create dirs inside the module folder
mkdir -p "docflow-agentic-finance/inbox" "docflow-agentic-finance/archive" "docflow-agentic-finance/artifacts"

if (cd docflow-agentic-finance && python3 -m src.docflow.runner); then
    echo "✅ Passed: Runner started with minimal env"
else
    echo "❌ Failed: Runner failed with minimal env"
    exit 1
fi
