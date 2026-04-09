/** @odoo-module **/
/**
 * Composer AI Action — registers "Ask AI" button in the Odoo 18 mail composer toolbar.
 *
 * Uses the native `registerComposerAction()` API from @mail/core/common/composer_actions.
 * This places the AI button alongside emoji picker, file upload, and send button.
 *
 * Architecture:
 *   registerComposerAction("ipai-ask-ai", ...)
 *     → setup: attaches reactive state (ipaiAiPanel) to the Composer component
 *     → onSelected: toggles ipaiAiPanel.show
 *     → Template patch (composer_ai_patch.xml) renders AiInlinePanel conditionally
 *
 * The setup() function runs during Composer.setup() → useComposerActions() lifecycle,
 * so useState() calls are valid OWL hooks at this point.
 */

import { useState } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { registerComposerAction } from "@mail/core/common/composer_actions";

registerComposerAction("ipai-ask-ai", {
    icon: "fa fa-magic",
    name: _t("Ask AI"),
    sequenceQuick: 25, // Between emoji (20) and send (30)
    condition: () => true, // Always available
    setup({ owner }) {
        // Attach reactive state to the Composer component instance.
        // This runs during Composer.setup() → useComposerActions(), so
        // OWL hooks like useState() are valid here.
        owner.ipaiAiPanel = useState({ show: false });
        console.debug("[IPAI] Ask AI action registered on composer", owner.constructor.name);
    },
    onSelected({ owner }) {
        // Toggle inline AI panel visibility.
        // The template patch (composer_ai_patch.xml) reads owner.ipaiAiPanel.show
        // to conditionally render the AiInlinePanel component.
        owner.ipaiAiPanel.show = !owner.ipaiAiPanel.show;
        console.debug("[IPAI] AI panel toggled:", owner.ipaiAiPanel.show);
    },
});
