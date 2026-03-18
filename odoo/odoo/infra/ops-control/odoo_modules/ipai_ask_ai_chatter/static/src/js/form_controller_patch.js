/** @odoo-module **/

import { FormController } from "@web/views/form/form_controller";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";

/**
 * Patch FormController to track context and add AI action
 */
patch(FormController.prototype, {
    setup() {
        super.setup(...arguments);

        // Get services
        this.askAiContext = useService("ask_ai_context");

        // Update context on mount and record change
        this._updateAiContext();
    },

    /**
     * Update AI context with current form data
     */
    _updateAiContext() {
        const model = this.props.resModel;
        const resId = this.props.resId;
        const displayName = this.model?.root?.data?.display_name;

        this.askAiContext.setContext({
            model,
            resId,
            viewType: "form",
            displayName,
        });
    },

    /**
     * Override to update context when record changes
     */
    async load() {
        await super.load(...arguments);
        this._updateAiContext();
    },

    /**
     * Add "Ask AI" to form action items
     */
    getStaticActionMenuItems() {
        const menuItems = super.getStaticActionMenuItems();

        // Add Ask AI option
        menuItems.askAi = {
            sequence: 5,
            icon: "fa fa-magic",
            description: this.env._t("Ask AI"),
            callback: () => this._onAskAi(),
        };

        return menuItems;
    },

    /**
     * Open AI panel with current form context
     */
    _onAskAi() {
        const askAi = this.env.services.ask_ai;
        if (askAi) {
            askAi.open({
                model: this.props.resModel,
                res_id: this.props.resId,
                display_name: this.model?.root?.data?.display_name,
                view_type: "form",
            });
        }
    },
});
