#!/usr/bin/env python3
import json
import re
import sys
import os
import argparse


def get_proposals_from_dts(dts_path):
    """
    Parses vscode.d.ts to extract available API proposals.
    """
    if not os.path.exists(dts_path):
        print(f"Error: vscode.d.ts not found at {dts_path}")
        sys.exit(1)

    with open(dts_path, "r") as f:
        content = f.read()

    # Simple heuristic: scan for proposed API names (camelCase)
    # This is a loose check but effective for catching "DOES NOT EXIST" errors
    # which imply the string is missing entirely from the host definition.
    return set(re.findall(r"\b[a-zA-Z][a-zA-Z0-9]+\b", content))


def validate_proposals(product_path, dts_path):
    """
    Validates that all enabled API proposals in product.json exist in vscode.d.ts.
    """
    if not os.path.exists(product_path):
        print(f"Error: product.json not found at {product_path}")
        sys.exit(1)

    try:
        with open(product_path, "r") as f:
            product_data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse product.json: {e}")
        sys.exit(1)

    dts_content_words = get_proposals_from_dts(dts_path)

    failed = False

    if "extensionEnabledApiProposals" in product_data:
        for ext_id, proposals in product_data["extensionEnabledApiProposals"].items():
            for proposal in proposals:
                # Handle @ version suffix logic (e.g. chatSessionsProvider@3 -> chatSessionsProvider)
                clean_proposal = proposal.split("@")[0]

                if clean_proposal not in dts_content_words:
                    print(
                        f"ERROR: Proposal '{proposal}' (extension: {ext_id}) not found in vscode.d.ts"
                    )
                    failed = True
                else:
                    # Optional: print success for debugging
                    # print(f"OK: Proposal '{proposal}' found.")
                    pass

    if failed:
        print("Validation FAILED: Some enabled proposals are missing from the host definition.")
        sys.exit(1)
    else:
        print("Validation SUCCESS: All enabled proposals appear to be valid.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate product.json API proposals.")
    parser.add_argument("--product", required=True, help="Path to product.json")
    parser.add_argument("--dts", required=True, help="Path to vscode.d.ts or vscode.proposed.d.ts")

    args = parser.parse_args()
    validate_proposals(args.product, args.dts)
