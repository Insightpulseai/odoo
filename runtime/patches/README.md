# runtime/patches — Deterministic Vendor Patches

This directory contains patches that must be re-applied to vendored OCA or
third-party code after each submodule update. Each patch is idempotent and
applies cleanly with `git apply` or `patch -p1`.

## Patch Inventory

| Patch | Applies to | Rationale | Last verified |
|-------|-----------|-----------|---------------|
| `oca_mail_tracking_odoo19_prepare_outgoing_list.patch` | `addons/oca/mail/mail_tracking/models/mail_mail.py` | OCA rigid Odoo18 signature breaks Odoo19 MRO when `mass_mailing` passes `doc_to_followers=` | Odoo 19.0 / OCA mail 17.0 — 2026-02-27 |
| `oca_account_usability_odoo19_anglo_saxon.patch` | `addons/oca/account-financial-tools/account_usability/` | Odoo19 removed `anglo_saxon_accounting`; OCA re-add causes Owl `UncaughtPromiseError` | Odoo 19.0 / OCA account-financial-tools 17.0 — 2026-02-27 |
| `odoo-test-helper/0001-odoo19-metamodel-module_to_models.patch` | `odoo-test-helper` package | MetaModel refactor in Odoo19: `module_to_models` → `_module_to_models__` | Odoo 19.0 / odoo-test-helper 2.0.x — 2026-02-27 |

**Re-verify this table whenever:**
- `git-aggregator` updates `addons/oca/*` pins (`oca.yml` or equivalent)
- `requirements-constraints.txt` changes `odoo-test-helper` version
- Odoo minor version bump (19.0.x → 19.0.y)

**CI gate:** `scripts/apply_runtime_patches.sh --check` runs in
`.github/workflows/vendor-patch-verify.yml` on every PR touching `runtime/patches/`.

---

## Patches

### `oca_mail_tracking_odoo19_prepare_outgoing_list.patch`

**Applies to:** `addons/oca/mail/mail_tracking/models/mail_mail.py`

**Why:** OCA `mail_tracking._prepare_outgoing_list` (Odoo 18.x signature) uses
positional args and a rigid signature that breaks with Odoo 19's MRO when
`mass_mailing` passes `doc_to_followers=` as a keyword argument.

**What it does:**

1. Adds `**kwargs` to the signature so unknown kwargs don't raise TypeError
2. Changes the `super()` call to use keyword syntax (`mail_server=mail_server`)
   so the call chain works regardless of MRO depth

**Apply:**

```bash
cd addons/oca/mail
git apply ../../../runtime/patches/oca_mail_tracking_odoo19_prepare_outgoing_list.patch
```

**Companion module:** `addons/ipai/ipai_zoho_mail_api` — contains a shim in
`models/mail_mail.py` that strips any kwargs unknown to the base
`mail._prepare_outgoing_list(mail_server, doc_to_followers)` method.
The shim logs a WARNING when it strips anything, so MRO regressions are visible.

---

### `oca_account_usability_odoo19_anglo_saxon.patch`

**Applies to:** `addons/oca/account-financial-tools/`

**Why:** Odoo 19 removed the `anglo_saxon_accounting` field from `res.config.settings` and changed its inventory valuation strategy. The `account_usability` module attempts to add this field to the Accounting settings view, which causes an Owl `UncaughtPromiseError` and prevents the settings page from loading.

**What it does:**

1. Removes the `anglo_saxon_accounting` computing field from `account_usability/models/res_config_settings.py`.
2. Removes the corresponding configuration block from `account_usability/views/res_config_settings_views.xml`.

**Apply:**

```bash
cd addons/oca/account-financial-tools
git apply ../../../runtime/patches/oca_account_usability_odoo19_anglo_saxon.patch
```

---

### `odoo-test-helper/0001-odoo19-metamodel-module_to_models.patch`

**Applies to:** `odoo-test-helper` package

**Why:** Renames `module_to_models` → `_module_to_models__` to match Odoo 19
MetaModel refactoring.

---

## Re-applying after OCA update

```bash
# Idempotent — skips already-applied patches and patches whose targets are absent:
bash scripts/apply_runtime_patches.sh

# Dry-run check only (used by CI):
bash scripts/apply_runtime_patches.sh --check
```
