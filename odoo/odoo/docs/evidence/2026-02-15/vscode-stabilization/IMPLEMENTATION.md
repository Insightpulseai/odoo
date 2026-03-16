# VS Code Stabilization Implementation Evidence

## Summary

Since `product.json` is not present in the repository, we implemented a build-time stabilization strategy. We created scripts to patch `product.json` dynamically and validate it against the host's `vscode.d.ts`. We also added a missing asset to prevent load errors.

## Changes

### Scripts

- `scripts/vscode/stabilize_product_json.py`: Removes invalid API proposals, deduplicates draw.io extensions, and blocks broken extensions.
- `scripts/vscode/validate_product_api_proposals.py`: Validates that enabled API proposals exist in the host `vscode.d.ts`.

### Assets

- `docs/kb/odoo19/assets/odoo_core_erd.drawio`: Added minimal valid XML to prevent "file not found" errors.

### CI

- `.github/workflows/vscode_stabilization.yml`: CI workflow to test the stabilization and validation scripts.

## Verification

We verified the scripts by running them against a mock `product.json` and `vscode.d.ts`.

### Mock Data

**Input `product.json`:**

```json
{
  "extensionEnabledApiProposals": {
    "valid.ext": ["validProposal"],
    "invalid.ext": ["attributableCoverage", "chatSessionsProvider@3"]
  },
  "builtInExtensions": [
    { "id": "hediet.vscode-drawio" },
    { "id": "hediet.vscode-drawio-insiders-build" },
    "copilot-swe-agent",
    "valid-extension"
  ]
}
```

**Input `vscode.d.ts`:**

```typescript
export interface validProposal {}
```

### Execution Output

```
Removing proposal 'attributableCoverage' from extension 'invalid.ext'
Removing proposal 'chatSessionsProvider@3' from extension 'invalid.ext'
Removing extension 'hediet.vscode-drawio-insiders-build'
Removing extension 'copilot-swe-agent'
Successfully stabilized product.json. Wrote to stabilized_product.json
Validation SUCCESS: All enabled proposals appear to be valid.
```

### Resulting `product.json`

```json
{
  "extensionEnabledApiProposals": {
    "valid.ext": ["validProposal"],
    "invalid.ext": []
  },
  "builtInExtensions": [
    {
      "id": "hediet.vscode-drawio"
    },
    "valid-extension"
  ]
}
```

## Next Steps

Integrate `scripts/vscode/stabilize_product_json.py` into your actual VS Code build pipeline, running it on the `product.json` before packaging.
