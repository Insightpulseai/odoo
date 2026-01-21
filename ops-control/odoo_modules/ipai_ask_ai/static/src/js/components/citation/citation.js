/** @odoo-module **/

import { Component } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

/**
 * Citation - Clickable reference to an Odoo record
 *
 * Schema:
 * {
 *   model: "res.partner",
 *   res_id: 123,
 *   label: "Partner Name",
 *   field: "name" // optional - specific field referenced
 * }
 */
export class Citation extends Component {
    static template = "ipai_ask_ai.Citation";
    static props = {
        citation: Object,
    };

    setup() {
        this.action = useService("action");
    }

    get label() {
        return this.props.citation.label || `${this.props.citation.model}/${this.props.citation.res_id}`;
    }

    get model() {
        return this.props.citation.model;
    }

    get resId() {
        return this.props.citation.res_id;
    }

    get field() {
        return this.props.citation.field;
    }

    get icon() {
        // Model-specific icons
        const modelIcons = {
            "res.partner": "fa-user",
            "res.users": "fa-user-circle",
            "res.company": "fa-building",
            "sale.order": "fa-shopping-cart",
            "purchase.order": "fa-truck",
            "account.move": "fa-file-text-o",
            "stock.picking": "fa-cube",
            "project.project": "fa-folder",
            "project.task": "fa-tasks",
            "crm.lead": "fa-bullseye",
            "hr.employee": "fa-id-card",
            "product.product": "fa-cube",
            "product.template": "fa-cubes",
        };
        return modelIcons[this.model] || "fa-file-o";
    }

    /**
     * Navigate to the cited record
     */
    onClick() {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: this.model,
            res_id: this.resId,
            views: [[false, "form"]],
            target: "current",
        });
    }
}
