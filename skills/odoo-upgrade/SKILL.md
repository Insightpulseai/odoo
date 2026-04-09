# Odoo upgrade and migration skill

Use this skill when:
- Upgrading addons between Odoo versions
- Changing API/version assumptions
- Adapting manifests, XML, tests, or data files for a new version
- Handling deprecations and migration-safe refactors
- Porting OCA modules (17.0 → 18.0 → 19.0)

## Checklist

1. Identify version-sensitive surfaces (renamed APIs, removed methods, changed behavior).
2. Isolate migration changes from feature changes — separate PRs.
3. Keep transport/platform logic outside addons.
4. Record any data migration or compatibility assumptions.
5. Add targeted regression coverage.
6. Run `odoo-bin upgrade_code --addons-path <path>` for automated code upgrades.

## Odoo 18 Breaking Changes (vs 17.0)

- `tree` views renamed to `list` globally
- Use `Command` tuples for x2many operations
- Portal and Internal User are mutually exclusive groups

## OCA Porting Workflow

```
1. oca-port origin/17.0 origin/18.0 <module> --verbose --dry-run
2. odoo-bin upgrade_code --addons-path <path>
3. odoo-bin -d test_<module> -i <module> --stop-after-init --test-enable
4. Classify result per testing.md failure matrix
```

Never port without running `upgrade_code`.

## Transport (SDK)

- Odoo 18: XML-RPC (`xmlrpc/2/common`, `xmlrpc/2/object`) + JSON-RPC

Reference: `spec/odoo-external-sdk/transport-design.md`

## Refuse or Escalate If

- The upgrade mixes migration changes with new features in the same PR
- A data migration would be destructive without a rollback plan
- The change assumes a version-specific API without version detection
