#!/bin/bash

# check_spec_architecture_terms.sh
# Verifies that spec/ documentation uses canonical terminology and reflects settled decisions.

EXIT_CODE=0

# Deprecated Terms
DEPRECATED_TERMS=(
    "Tableau"
    "ops-platform"
    "design-system"
    "lakehouse repo"
    "lakehouse repository"
)

echo "--- Checking for deprecated terms in spec/ ---"
for term in "${DEPRECATED_TERMS[@]}"; do
    results=$(grep -r "$term" spec/)
    if [ ! -z "$results" ]; then
        echo "FAIL: Found deprecated term '$term':"
        echo "$results"
        EXIT_CODE=1
    fi
done

# Settled Decision Drift
echo "--- Checking for settled architecture drift in spec/ ---"

# Databricks vs Fabric drift
results=$(grep -r "Databricks or Fabric" spec/)
if [ ! -z "$results" ]; then
    echo "FAIL: Found unresolved 'Databricks or Fabric' choice (settled as both mandatory):"
    echo "$results"
    EXIT_CODE=1
fi

# n8n as CDC drift
results=$(grep -r "n8n for CDC" spec/)
if [ ! -z "$results" ]; then
    echo "FAIL: Found n8n described as CDC backbone (settled as orchestration only):"
    echo "$results"
    EXIT_CODE=1
fi

# M365 SDK vs Runtime block
results=$(grep -r "SDK as core runtime" spec/ docs/architecture/)
if [ ! -z "$results" ]; then
    echo "FAIL: Found M365 SDK described as core runtime (settled as channel layer):"
    echo "$results"
    EXIT_CODE=1
fi

if [ $EXIT_CODE -eq 0 ]; then
    echo "PASS: All spec terms are canonical."
else
    echo "FAIL: Please normalize terminology and architecture language."
fi

exit $EXIT_CODE
