// Copyright 2026 InsightPulse AI
// License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
//
// Runtime proof that the ipai_web_mail_compat overlay is present in the
// compiled asset bundle (not silently ignored or missing).
//
// Validation (browser DevTools console on any backend page):
//   window.__IPAI_COMPAT__.mail_tracking
//   // → { loaded: true, ts: <epoch ms>, patch: "store+template" }
//
// If this object is absent, the ("remove"/"add") asset stanza didn't fire —
// check: module installed, bundle rebuilt, browser cache cleared.

(function () {
    window.__IPAI_COMPAT__ = window.__IPAI_COMPAT__ || {};
    window.__IPAI_COMPAT__.mail_tracking = {
        loaded: true,
        ts: Date.now(),
        patch: "store+template",
        module: "ipai_web_mail_compat",
        fixes: [
            "Record.one() removed from Store.setup() → onStarted() plain object",
            "mail.Discuss.mobileTopbar → mail.DiscussContent.mobileTopbar",
        ],
    };
})();
