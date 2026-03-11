/** @odoo-module **/
/**
 * Backward-compatibility shim: Record.one / .many / .attr
 *
 * In Odoo 17 the mail Record class exposed static field-definition helpers:
 *     Record.one(targetModel, opts)   →  one-to-one relation
 *     Record.many(targetModel, opts)  →  one-to-many relation
 *     Record.attr(default, opts)      →  primitive attribute
 *
 * In Odoo 19 these were moved to a standalone `fields` namespace:
 *     fields.One()   fields.Many()   fields.Attr()
 *   (exported from @mail/model/misc via @mail/core/common/record)
 *
 * OCA modules ported from 17.0 (e.g. mail_tracking, web_responsive)
 * may still reference Record.one() etc., producing:
 *     TypeError: Record.one is not a function
 *
 * This shim re-attaches the old names so legacy call-sites work unchanged.
 * It is idempotent — safe to load even if no legacy code is present.
 */

import { Record, fields } from "@mail/core/common/record";

// Only patch if the methods are genuinely missing (avoid double-patching).
if (typeof Record.one !== "function") {
    Record.one = fields.One;
}
if (typeof Record.many !== "function") {
    Record.many = fields.Many;
}
if (typeof Record.attr !== "function") {
    Record.attr = fields.Attr;
}
