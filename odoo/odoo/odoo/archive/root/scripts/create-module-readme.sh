#!/usr/bin/env bash
# =============================================================================
# Create OCA-style readme/ folder structure for a module
#
# Usage:
#   ./scripts/create-module-readme.sh <module_path>
#   ./scripts/create-module-readme.sh addons/ipai/my_module
#
# This creates the readme/ folder with OCA template files:
#   - DESCRIPTION.rst
#   - USAGE.rst
#   - CONFIGURE.rst
#   - CONTRIBUTORS.rst
#
# After creation, run pre-commit to generate README.rst:
#   pre-commit run oca-gen-addon-readme --all-files
# =============================================================================
set -euo pipefail

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check argument
if [ $# -lt 1 ]; then
  echo "Usage: $0 <module_path>"
  echo "Example: $0 addons/ipai/my_module"
  exit 1
fi

MODULE_PATH="$1"
README_DIR="${MODULE_PATH}/readme"
TEMPLATE_DIR="templates/module_readme"

# Check module exists
if [ ! -d "$MODULE_PATH" ]; then
  echo "Error: Module path does not exist: $MODULE_PATH"
  exit 1
fi

# Check __manifest__.py exists
if [ ! -f "${MODULE_PATH}/__manifest__.py" ]; then
  echo "Error: Not an Odoo module (missing __manifest__.py): $MODULE_PATH"
  exit 1
fi

# Create readme directory
if [ -d "$README_DIR" ]; then
  echo -e "${YELLOW}Warning: readme/ already exists, skipping existing files${NC}"
else
  mkdir -p "$README_DIR"
  echo -e "${GREEN}Created: $README_DIR${NC}"
fi

# Copy template files (only if they don't exist)
for template_file in DESCRIPTION.rst USAGE.rst CONFIGURE.rst CONTRIBUTORS.rst; do
  target_file="${README_DIR}/${template_file}"

  if [ -f "$target_file" ]; then
    echo "  Skipping (exists): $template_file"
  else
    if [ -f "${TEMPLATE_DIR}/${template_file}" ]; then
      cp "${TEMPLATE_DIR}/${template_file}" "$target_file"
      echo -e "${GREEN}  Created: $template_file${NC}"
    else
      # Create minimal template inline
      case $template_file in
        DESCRIPTION.rst)
          echo "This module provides..." > "$target_file"
          ;;
        USAGE.rst)
          echo "To use this module, go to..." > "$target_file"
          ;;
        CONFIGURE.rst)
          echo "No special configuration is needed." > "$target_file"
          ;;
        CONTRIBUTORS.rst)
          echo "* InsightPulseAI <https://github.com/jgtolentino>" > "$target_file"
          ;;
      esac
      echo -e "${GREEN}  Created: $template_file (minimal)${NC}"
    fi
  fi
done

echo ""
echo "Done! Next steps:"
echo "  1. Edit the files in ${README_DIR}/"
echo "  2. Run: pre-commit run oca-gen-addon-readme --all-files"
echo "  3. Verify generated README.rst in ${MODULE_PATH}/"
