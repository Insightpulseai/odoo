# Odoo EE → OCA → Adapter Parity Decision Table

| Source (EE) | Target (OCA) | Adapter Action | Notes |
|-------------|--------------|---------------|-------|
| v18 view    | OCA view     | normalize_views(v18) | Handles deprecated fields, layout differences |
| v19 view    | OCA view     | normalize_views(v19) | Handles new features, layout changes |
| v18 manifest| OCA manifest | normalize_manifest(v18) | Normalizes keys, removes EE-only fields |
| v19 manifest| OCA manifest | normalize_manifest(v19) | Normalizes keys, removes EE-only fields |
| Deprecated  | Supported    | scan_deprecations()   | Flags deprecated features for migration |
| Custom code | OCA contract | classify_parity()     | Ensures only OCA-conformant code is accepted |

> All normalization logic must be implemented in adapters. CI guards block version-specific code outside adapters.
