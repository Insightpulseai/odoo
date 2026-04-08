#!/usr/bin/env bash
# Validate infrastructure SSOT files
set -euo pipefail
echo "Validating infra SSOT..."
python3 -c "import yaml; yaml.safe_load(open('infra/ssot/topology/resource-topology.yaml'))" && echo "PASS: resource-topology.yaml" || echo "FAIL: resource-topology.yaml"
python3 -c "import yaml; yaml.safe_load(open('infra/ssot/policies/infra-policy.yaml'))" && echo "PASS: infra-policy.yaml" || echo "FAIL: infra-policy.yaml"
echo "Done."
