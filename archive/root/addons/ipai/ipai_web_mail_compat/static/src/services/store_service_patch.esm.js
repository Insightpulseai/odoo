// Copyright 2026 InsightPulse AI
// License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
//
// Replaces: mail_tracking/static/src/services/store_service_patch.esm.js
// Reason  : Record.one() was removed from Odoo 19; onStarted() plain-object
//           initialisation is the correct pattern.
//
// Guard   : symbol marker prevents double-application if bundle order is
//           somehow wrong and both files end up loaded.

import {Store} from "@mail/core/common/store_service";
import {_t} from "@web/core/l10n/translation";
import {patch} from "@web/core/utils/patch";

const PATCH_MARKER = "__ipai_web_mail_compat_store_patched__";

if (!Store.prototype[PATCH_MARKER]) {
    Object.defineProperty(Store.prototype, PATCH_MARKER, {
        value: true,
        writable: false,
        configurable: false,
        enumerable: false,
    });

    patch(Store.prototype, {
        onStarted() {
            super.onStarted(...arguments);
            // Initialise the "Failed" virtual mailbox as a plain object.
            // Record.one("Thread") was removed in Odoo 19; the mailbox object
            // is sufficient for OWL reactivity when assigned here.
            this.failed = {
                id: "failed",
                model: "mail.box",
                name: _t("Failed"),
            };
        },
    });
}
