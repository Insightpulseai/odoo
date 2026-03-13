/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

/**
 * View Switcher Component
 * Provides view tabs and switching for databases
 */
export class ViewSwitcher extends Component {
    static template = "ipai_workos_views.ViewSwitcher";
    static props = {
        databaseId: { type: Number },
        onViewChange: { type: Function, optional: true },
    };

    setup() {
        this.orm = useService("orm");
        this.state = useState({
            views: [],
            activeViewId: null,
            loading: true,
        });

        onWillStart(async () => {
            await this.loadViews();
        });
    }

    async loadViews() {
        this.state.loading = true;
        try {
            const views = await this.orm.call(
                "ipai.workos.view",
                "get_views_for_database",
                [this.props.databaseId]
            );
            this.state.views = views;

            // Set default view as active
            const defaultView = views.find(v => v.is_default) || views[0];
            if (defaultView) {
                this.state.activeViewId = defaultView.id;
            }
        } finally {
            this.state.loading = false;
        }
    }

    selectView(viewId) {
        this.state.activeViewId = viewId;
        if (this.props.onViewChange) {
            const view = this.state.views.find(v => v.id === viewId);
            this.props.onViewChange(view);
        }
    }

    async createView(viewType) {
        const viewId = await this.orm.create("ipai.workos.view", [{
            name: `New ${viewType} view`,
            database_id: this.props.databaseId,
            view_type: viewType,
        }]);
        await this.loadViews();
        this.selectView(viewId[0]);
    }

    isActive(viewId) {
        return this.state.activeViewId === viewId;
    }

    getViewIcon(viewType) {
        const icons = {
            table: "fa-table",
            kanban: "fa-columns",
            calendar: "fa-calendar",
            gallery: "fa-th",
            list: "fa-list",
        };
        return icons[viewType] || "fa-eye";
    }
}
