/** @odoo-module **/

import { ListController } from "@web/views/list/list_controller";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";

/**
 * Patch ListController to track selection and add AI bulk action
 */
patch(ListController.prototype, {
    setup() {
        super.setup(...arguments);

        // Get services
        this.askAiContext = useService("ask_ai_context");

        // Update context
        this._updateAiContext();
    },

    /**
     * Update AI context with current list data
     */
    _updateAiContext() {
        this.askAiContext.setContext({
            model: this.props.resModel,
            viewType: "list",
            resIds: [],
        });
    },

    /**
     * Override to track selected records
     */
    onSelectionChanged(resIds) {
        super.onSelectionChanged?.(...arguments);

        // Update AI context with selected IDs
        this.askAiContext.setSelectedIds(resIds);
    },

    /**
     * Add "Ask AI" to action menu
     */
    getStaticActionMenuItems() {
        const menuItems = super.getStaticActionMenuItems();

        // Add Ask AI option for selection
        menuItems.askAi = {
            sequence: 5,
            icon: "fa fa-magic",
            description: this.env._t("Ask AI about selected"),
            callback: () => this._onAskAi(),
        };

        return menuItems;
    },

    /**
     * Open AI panel with selected records context
     */
    _onAskAi() {
        const askAi = this.env.services.ask_ai;
        const selectedIds = this.model.root.selection.map(r => r.resId);

        if (askAi) {
            askAi.open({
                model: this.props.resModel,
                res_ids: selectedIds,
                view_type: "list",
            });
        }
    },
});
