#!/bin/bash
# Categorize spec bundles as active or archived based on modification date
# Usage: ./categorize-specs.sh <specs_directory>

set -euo pipefail

SPECS_DIR="${1:?Specs directory required}"
CUTOFF_DAYS=90  # 3 months

# Get cutoff date (90 days ago)
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    CUTOFF_DATE=$(date -v-${CUTOFF_DAYS}d +%s)
else
    # Linux
    CUTOFF_DATE=$(date -d "${CUTOFF_DAYS} days ago" +%s)
fi

# Output CSV header
echo "spec,category,last_modified,reason"

# Iterate through spec bundles
for spec_dir in "$SPECS_DIR"/*/ ; do
    if [[ ! -d "$spec_dir" ]]; then
        continue
    fi

    spec_name=$(basename "$spec_dir")

    # Find most recently modified file in spec bundle
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        last_modified=$(find "$spec_dir" -type f -print0 | xargs -0 stat -f "%m %N" | sort -rn | head -1 | cut -d' ' -f1)
    else
        # Linux
        last_modified=$(find "$spec_dir" -type f -printf "%T@ %p\n" | sort -rn | head -1 | cut -d' ' -f1 | cut -d'.' -f1)
    fi

    # Categorize based on modification date
    if [[ $last_modified -ge $CUTOFF_DATE ]]; then
        category="active"
        reason="modified_within_90_days"
    else
        category="archived"
        reason="no_modifications_90_days"
    fi

    # Format last modified date
    if [[ "$OSTYPE" == "darwin"* ]]; then
        last_modified_str=$(date -r "$last_modified" "+%Y-%m-%d")
    else
        last_modified_str=$(date -d "@$last_modified" "+%Y-%m-%d")
    fi

    echo "$spec_name,$category,$last_modified_str,$reason"
done
