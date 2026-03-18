/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

/**
 * Row Editor Component
 * Provides inline editing for database rows
 */
export class RowEditor extends Component {
    static template = "ipai_workos_db.RowEditor";
    static props = {
        rowId: { type: Number },
        databaseId: { type: Number },
        readonly: { type: Boolean, optional: true },
    };

    setup() {
        this.orm = useService("orm");
        this.state = useState({
            row: null,
            properties: [],
            editingProperty: null,
            loading: true,
        });
    }

    async loadData() {
        this.state.loading = true;
        try {
            const [row] = await this.orm.read("ipai.workos.row", [this.props.rowId], ["values_json"]);
            const properties = await this.orm.searchRead(
                "ipai.workos.property",
                [["database_id", "=", this.props.databaseId]],
                ["id", "name", "property_type", "options_json", "is_visible"],
                { order: "sequence" }
            );
            this.state.row = row;
            this.state.properties = properties;
        } finally {
            this.state.loading = false;
        }
    }

    startEdit(propertyId) {
        if (!this.props.readonly) {
            this.state.editingProperty = propertyId;
        }
    }

    async saveValue(propertyId, value) {
        const values = JSON.parse(this.state.row.values_json || "{}");
        values[propertyId] = value;
        await this.orm.write("ipai.workos.row", [this.props.rowId], {
            values_json: JSON.stringify(values),
        });
        this.state.row.values_json = JSON.stringify(values);
        this.state.editingProperty = null;
    }

    cancelEdit() {
        this.state.editingProperty = null;
    }

    getValue(propertyId) {
        const values = JSON.parse(this.state.row?.values_json || "{}");
        return values[propertyId] ?? null;
    }
}
