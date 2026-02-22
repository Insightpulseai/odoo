// Copyright 2026 InsightPulse AI
// License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
//
// Replaces the OCA mail_tracking store patch for Odoo 19 compatibility.
// Record.one() was removed; the failed mailbox is a plain object set in
// onStarted(), which is the correct Odoo 19 pattern.

import {Store} from "@mail/core/common/store_service";
import {_t} from "@web/core/l10n/translation";
import {patch} from "@web/core/utils/patch";

patch(Store.prototype, {
    onStarted() {
        super.onStarted(...arguments);
        this.failed = {
            id: "failed",
            model: "mail.box",
            name: _t("Failed"),
        };
    },
});
