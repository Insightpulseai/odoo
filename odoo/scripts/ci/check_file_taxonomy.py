#!/usr/bin/env python3
import pathlib
import sys

# Define strict placement bounds mapping extension -> allowed root folders
ALLOWED_EXTENSIONS_BY_ROOT = {
    "docs": [".md", ".drawio", ".png", ".svg", ".mmd", ".puml", ".json"],
    "ssot": [".yaml", ".yml", ".json", ".schema.json"],
    "spec": [".md"],
    "infra": [".tf", ".bicep", ".parameters.json", ".yaml", ".yml", ".sh", ".json", ".md"],
    "addons": [".py", ".xml", ".csv", ".js", ".md", ".png", ".svg"]
}

FORBIDDEN_EXTENSIONS_BY_ROOT = {
    "docs": [".py", ".ts", ".tsx", ".yaml", ".yml"],
    "ssot": [".md", ".txt", ".py", ".sh", ".ts", ".tsx"],
}

def check_file_taxonomy():
    repo_root = pathlib.Path(__file__).parent.parent.parent
    violations = []

    for path in repo_root.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue

        rel_path = path.relative_to(repo_root)
        root_dir = rel_path.parts[0] if len(rel_path.parts) > 0 else ""
        ext = "".join(path.suffixes)

        if root_dir in FORBIDDEN_EXTENSIONS_BY_ROOT:
            if any(ext.endswith(f_ext) for f_ext in FORBIDDEN_EXTENSIONS_BY_ROOT[root_dir]):
                violations.append(f"Violation: Forbidden extension {ext} in {root_dir}/ -> {rel_path}")

    if violations:
        print("File Taxonomy Violations Found:")
        for v in violations:
            print(v)
        sys.exit(1)
    else:
        print("File Taxonomy Check Passed.")
        sys.exit(0)

if __name__ == "__main__":
    check_file_taxonomy()
