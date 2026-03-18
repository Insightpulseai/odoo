/** @odoo-module **/
/**
 * IPAI Grid View - Main View Component
 *
 * This module implements a comprehensive grid/list view for Odoo 18 using OWL.
 * It provides data display, sorting, filtering, selection, and bulk actions.
 *
 * Architecture:
 * - GridView: Main view registration
 * - GridController: Action handling and user interaction
 * - GridRenderer: UI rendering and DOM updates
 * - GridModel: Data fetching and state management
 */

import { registry } from "@web/core/registry";
import { GridController } from "./grid_controller";
import { GridRenderer } from "./grid_renderer";
import { GridModel } from "./grid_model";

/**
 * Grid View definition for Odoo's view registry
 */
export const gridView = {
    type: "ipai_grid",
    display_name: "Grid",
    icon: "fa fa-th-list",
    multiRecord: true,
    searchMenuTypes: ["filter", "groupBy", "comparison", "favorite"],

    Controller: GridController,
    Renderer: GridRenderer,
    Model: GridModel,

    props: (genericProps, view) => {
        const { arch, relatedModels, resModel, fields } = genericProps;
        return {
            ...genericProps,
            archInfo: view.arch,
            Model: GridModel,
            Renderer: GridRenderer,
            buttonTemplate: "ipai_grid_view.GridButtons",
        };
    },
};

// Register the grid view
registry.category("views").add("ipai_grid", gridView);

/**
 * GridViewState - Reactive state management for grid views
 *
 * Tracks:
 * - Current page and pagination
 * - Sort configuration
 * - Selected records
 * - Filter state
 * - View mode (list/kanban)
 */
export class GridViewState {
    constructor() {
        this.records = [];
        this.total = 0;
        this.offset = 0;
        this.limit = 10;
        this.sortField = null;
        this.sortOrder = "asc";
        this.selectedIds = new Set();
        this.allSelected = false;
        this.viewMode = "list";
        this.searchTerm = "";
        this.activeFilters = [];
        this.columns = [];
        this.loading = true;
        this.error = null;
    }

    /**
     * Get current pagination info
     */
    get pagination() {
        const currentPage = Math.floor(this.offset / this.limit) + 1;
        const totalPages = Math.ceil(this.total / this.limit);
        return {
            currentPage,
            totalPages,
            hasNext: this.offset + this.limit < this.total,
            hasPrev: this.offset > 0,
            start: this.offset + 1,
            end: Math.min(this.offset + this.limit, this.total),
        };
    }

    /**
     * Get selected record count
     */
    get selectedCount() {
        return this.selectedIds.size;
    }

    /**
     * Check if a specific record is selected
     */
    isSelected(recordId) {
        return this.selectedIds.has(recordId);
    }

    /**
     * Toggle selection for a record
     */
    toggleSelection(recordId) {
        if (this.selectedIds.has(recordId)) {
            this.selectedIds.delete(recordId);
        } else {
            this.selectedIds.add(recordId);
        }
        this.allSelected = this.selectedIds.size === this.records.length;
    }

    /**
     * Select all visible records
     */
    selectAll() {
        if (this.allSelected) {
            this.selectedIds.clear();
            this.allSelected = false;
        } else {
            this.records.forEach(record => this.selectedIds.add(record.id));
            this.allSelected = true;
        }
    }

    /**
     * Clear all selections
     */
    clearSelection() {
        this.selectedIds.clear();
        this.allSelected = false;
    }

    /**
     * Set sort configuration
     */
    setSort(field, order = null) {
        if (this.sortField === field) {
            this.sortOrder = this.sortOrder === "asc" ? "desc" : "asc";
        } else {
            this.sortField = field;
            this.sortOrder = order || "asc";
        }
    }

    /**
     * Reset to first page
     */
    resetPagination() {
        this.offset = 0;
    }

    /**
     * Go to next page
     */
    nextPage() {
        if (this.pagination.hasNext) {
            this.offset += this.limit;
        }
    }

    /**
     * Go to previous page
     */
    prevPage() {
        if (this.pagination.hasPrev) {
            this.offset = Math.max(0, this.offset - this.limit);
        }
    }

    /**
     * Go to specific page
     */
    goToPage(page) {
        const newOffset = (page - 1) * this.limit;
        if (newOffset >= 0 && newOffset < this.total) {
            this.offset = newOffset;
        }
    }

    /**
     * Update page size
     */
    setPageSize(size) {
        this.limit = size;
        this.offset = 0;
    }

    /**
     * Add a filter
     */
    addFilter(filter) {
        this.activeFilters.push(filter);
        this.resetPagination();
    }

    /**
     * Remove a filter by index
     */
    removeFilter(index) {
        this.activeFilters.splice(index, 1);
        this.resetPagination();
    }

    /**
     * Clear all filters
     */
    clearFilters() {
        this.activeFilters = [];
        this.resetPagination();
    }

    /**
     * Set search term
     */
    setSearchTerm(term) {
        this.searchTerm = term;
        this.resetPagination();
    }

    /**
     * Switch view mode
     */
    setViewMode(mode) {
        this.viewMode = mode;
    }

    /**
     * Get current domain based on filters and search
     */
    getDomain(baseDomain = []) {
        const domain = [...baseDomain];

        // Add search term domain
        if (this.searchTerm && this.columns.length > 0) {
            const searchableColumns = this.columns.filter(c => c.searchable);
            if (searchableColumns.length > 0) {
                const searchDomain = [];
                searchableColumns.forEach((col, i) => {
                    if (i > 0) searchDomain.push("|");
                    searchDomain.push([col.field, "ilike", this.searchTerm]);
                });
                domain.push(...searchDomain);
            }
        }

        // Add filter domains
        this.activeFilters.forEach(filter => {
            if (filter.domain) {
                domain.push(...filter.domain);
            }
        });

        return domain;
    }

    /**
     * Get current sort order string
     */
    getOrderString() {
        if (!this.sortField) return null;
        return `${this.sortField} ${this.sortOrder}`;
    }
}
