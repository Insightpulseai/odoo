/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

/**
 * Expense OCR Status Widget
 */
export class ExpenseOcrStatus extends Component {
    static template = "ipai_expense_ocr.ExpenseOcrStatus";

    setup() {
        this.rpc = useService("rpc");
        this.notification = useService("notification");

        this.state = useState({
            loading: false,
            status: null,
        });
    }

    async checkStatus() {
        if (!this.props.expenseId) return;

        this.state.loading = true;

        try {
            const result = await this.rpc(`/ipai/expense_ocr/status/${this.props.expenseId}`);

            if (result.success) {
                this.state.status = result;
            }
        } catch (error) {
            console.error("Failed to check OCR status:", error);
        } finally {
            this.state.loading = false;
        }
    }

    getConfidenceLevel(confidence) {
        if (confidence >= 0.9) return "high";
        if (confidence >= 0.7) return "medium";
        return "low";
    }

    getConfidenceColor(confidence) {
        if (confidence >= 0.9) return "#28a745";
        if (confidence >= 0.7) return "#ffc107";
        return "#dc3545";
    }
}

ExpenseOcrStatus.props = {
    expenseId: { type: Number, optional: true },
};

// Register component
registry.category("view_widgets").add("expense_ocr_status", ExpenseOcrStatus);
