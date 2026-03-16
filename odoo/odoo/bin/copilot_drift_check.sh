#!/bin/bash
set -e

echo "Running Copilot Drift Check..."

# Regenerate manifest
python3 scripts/copilot_ingest.py

# Check for git changes in out/copilot_index/
if [ -n "$(git status --porcelain out/copilot_index)" ]; then
    echo "FAIL: Drift detected in Copilot index!"
    echo "The generated manifest does not match the source docs in kb/."
    echo "Run 'python3 scripts/copilot_ingest.py' locally and commit the changes."
    git diff out/copilot_index
    exit 1
else
    echo "SUCCESS: No drift detected in Copilot index."
fi
