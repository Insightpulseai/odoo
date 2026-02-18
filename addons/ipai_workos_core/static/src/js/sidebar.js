/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

/**
 * Work OS Sidebar Component
 * Renders hierarchical page tree for navigation
 */
export class WorkOSSidebar extends Component {
    static template = "ipai_workos_core.Sidebar";
    static props = {
        spaceId: { type: Number, optional: true },
        onPageSelect: { type: Function, optional: true },
    };

    setup() {
        this.orm = useService("orm");
        this.state = useState({
            pages: [],
            expandedPages: new Set(),
            selectedPageId: null,
            loading: true,
        });

        onWillStart(async () => {
            await this.loadPages();
        });
    }

    async loadPages() {
        this.state.loading = true;
        try {
            if (this.props.spaceId) {
                this.state.pages = await this.orm.call(
                    "ipai.workos.page",
                    "get_page_tree",
                    [this.props.spaceId]
                );
            }
        } finally {
            this.state.loading = false;
        }
    }

    togglePage(pageId) {
        if (this.state.expandedPages.has(pageId)) {
            this.state.expandedPages.delete(pageId);
        } else {
            this.state.expandedPages.add(pageId);
        }
    }

    selectPage(pageId) {
        this.state.selectedPageId = pageId;
        if (this.props.onPageSelect) {
            this.props.onPageSelect(pageId);
        }
    }

    isExpanded(pageId) {
        return this.state.expandedPages.has(pageId);
    }

    isSelected(pageId) {
        return this.state.selectedPageId === pageId;
    }
}

// Register component for use in templates
// Will be extended in future phases for full sidebar functionality
