import json
import argparse
import sys
import os

def stabilize_product_json(product_json_path, output_path=None):
    """
    Stabilizes product.json by removing invalid API proposals and duplicate/broken extensions.
    """
    if not os.path.exists(product_json_path):
        print(f"Error: product.json not found at {product_json_path}")
        sys.exit(1)

    try:
        with open(product_json_path, 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse product.json: {e}")
        sys.exit(1)

    changes_made = False

    # 1. Remove non-existent/finalized proposed APIs
    proposals_to_remove = {
        "attributableCoverage",
        "notebookCellExecutionState",
        "contribIssueReporter",
        "fileComments",
        "chatVariableResolver",
        "lmTools",
        "documentPaste",
    }
    # Also handle chatSessionsProvider@3 and variants dynamically

    if "extensionEnabledApiProposals" in data:
        for extension_id, proposals in data["extensionEnabledApiProposals"].items():
            new_proposals = []
            for proposal in proposals:
                should_remove = False
                if proposal in proposals_to_remove:
                    should_remove = True
                elif proposal.startswith("chatSessionsProvider@"):
                    should_remove = True

                if should_remove:
                    print(f"Removing proposal '{proposal}' from extension '{extension_id}'")
                    changes_made = True
                else:
                    new_proposals.append(proposal)

            data["extensionEnabledApiProposals"][extension_id] = new_proposals

    # 2. Deduplicate draw.io extensions and remove broken ones
    blocked_extensions = {
        "hediet.vscode-drawio-insiders-build",
        "ms-python.vscode-python-envs",
        "copilot-swe-agent"
    }

    if "builtInExtensions" in data:
        built_in_extensions = data["builtInExtensions"]
        new_extensions = []

        # builtInExtensions can be a list of strings or objects { "id": "..." }
        for ext in built_in_extensions:
            ext_id = ext
            if isinstance(ext, dict):
                ext_id = ext.get("id", "")

            if ext_id in blocked_extensions:
                print(f"Removing extension '{ext_id}'")
                changes_made = True
            else:
                new_extensions.append(ext)

        data["builtInExtensions"] = new_extensions

    if changes_made:
        out = output_path if output_path else product_json_path
        with open(out, 'w') as f:
            json.dump(data, f, indent=4) # Use 4 spaces or tab depending on file convention
        print(f"Successfully stabilized product.json. Wrote to {out}")
    else:
        print("No changes needed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Stabilize product.json")
    parser.add_argument("product_json", help="Path to product.json file")
    parser.add_argument("--output", help="Output path (optional, defaults to overwrite)")
    args = parser.parse_args()

    stabilize_product_json(args.product_json, args.output)
