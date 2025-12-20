/** @odoo-module */

import { Component, useState, onMounted } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import {
    searchMonthlyRevenueInsights,
    formatRevenue,
    formatMonth,
    calculateRelevance,
} from "./api";

/**
 * MonthlyRevenueSearch Component
 *
 * OWL component providing natural language search over monthly revenue insights.
 * Uses semantic vector search via Supabase Edge Functions.
 *
 * @extends Component
 */
export class MonthlyRevenueSearch extends Component {
    static template = "ipai_finance_ppm.MonthlyRevenueSearch";
    static props = {
        companyId: { type: Number, optional: true },
    };

    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.user = useService("user");

        this.state = useState({
            query: "",
            results: [],
            loading: false,
            error: null,
            hasSearched: false,
        });

        onMounted(async () => {
            // Get company ID from props or current user context
            if (!this.props.companyId) {
                try {
                    const userCompanyId = await this.user.hasGroup("base.group_multi_company")
                        ? this.user.companyId
                        : 1;
                    this.companyId = userCompanyId;
                } catch {
                    this.companyId = 1;
                }
            } else {
                this.companyId = this.props.companyId;
            }
        });
    }

    /**
     * Handle search form submission
     */
    async onSearch(ev) {
        ev.preventDefault();

        const query = this.state.query.trim();
        if (!query) {
            this.notification.add("Please enter a search query", {
                type: "warning",
            });
            return;
        }

        this.state.loading = true;
        this.state.error = null;

        try {
            const results = await searchMonthlyRevenueInsights({
                companyId: this.companyId,
                query: query,
                matchCount: 10,
            });

            this.state.results = results.map((r) => ({
                ...r,
                formattedMonth: formatMonth(r.month),
                formattedRevenue: formatRevenue(r.revenue),
                relevance: calculateRelevance(r.distance),
            }));
            this.state.hasSearched = true;
        } catch (error) {
            console.error("Search error:", error);
            this.state.error = error.message || "Search failed";
            this.notification.add(this.state.error, { type: "danger" });
        } finally {
            this.state.loading = false;
        }
    }

    /**
     * Clear search results and query
     */
    onClear() {
        this.state.query = "";
        this.state.results = [];
        this.state.hasSearched = false;
        this.state.error = null;
    }

    /**
     * Handle input change
     */
    onQueryChange(ev) {
        this.state.query = ev.target.value;
    }

    /**
     * Handle keyboard shortcuts
     */
    onKeyDown(ev) {
        if (ev.key === "Enter" && !ev.shiftKey) {
            this.onSearch(ev);
        } else if (ev.key === "Escape") {
            this.onClear();
        }
    }

    /**
     * Get relevance badge class based on score
     */
    getRelevanceClass(relevance) {
        if (relevance >= 80) return "bg-success";
        if (relevance >= 50) return "bg-warning";
        return "bg-secondary";
    }
}

// Register component as an action
registry.category("actions").add("ipai_finance_ppm.monthly_revenue_search", MonthlyRevenueSearch);
