/** @odoo-module **/

import { Chatter } from "@mail/core/web/chatter";
import { patch } from "@web/core/utils/patch";
import { AskAIButton } from "./ask_ai_button/ask_ai_button";

/**
 * Patch Chatter component to add "Ask AI" button
 */
patch(Chatter.prototype, {
    setup() {
        super.setup(...arguments);
    },
});

// Add AskAIButton to Chatter's static components
patch(Chatter, {
    components: {
        ...Chatter.components,
        AskAIButton,
    },
});
