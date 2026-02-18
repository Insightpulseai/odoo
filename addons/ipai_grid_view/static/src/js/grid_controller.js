/** @odoo-module **/
/**
 * IPAI Grid Controller - Action Handler
 *
 * Handles user interactions and coordinates between the model and renderer.
 * Implements bulk actions, navigation, and record operations.
 */

import { Component, useState, onWillStart, onMounted, useRef } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { useBus } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";
import { GridViewState } from "./grid_view";

/**
 * GridController - Main controller component for grid views
 */
export class GridController extends Component {
    static template = "ipai_grid_view.GridController";
    static components = {};

    static props = {
        resModel: { type: String },
        domain: { type: Array, optional: true },
        context: { type: Object, optional: true },
        fields: { type: Object, optional: true },
        archInfo: { type: Object, optional: true },
        Model: { type: Function },
        Renderer: { type: Function },
    };

    setup() {
        // Services
        this.orm = useService("orm");
        this.action = useService("action");
        this.notification = useService("notification");
        this.dialog = useService("dialog");
        this.user = useService("user");

        // Refs
        this.rootRef = useRef("root");
        this.searchInputRef = useRef("searchInput");

        // State
        this.state = useState(new GridViewState());

        // Model instance
        this.model = null;

        // Search debounce timer
        this._searchTimer = null;

        // Lifecycle hooks
        onWillStart(async () => {
            await this.loadData();
        });

        onMounted(() => {
            this._setupKeyboardShortcuts();
        });
    }

    /**
     * Initialize and load grid data
     */
    async loadData() {
        this.state.loading = true;
        this.state.error = null;

        try {
            // Initialize model
            const ModelClass = this.props.Model;
            this.model = new ModelClass();
            this.model.setup(
                {
                    resModel: this.props.resModel,
                    fields: this.props.fields,
                    domain: this.props.domain || [],
                    context: this.props.context || {},
                    columns: this._getColumnsFromArch(),
                },
                { orm: this.orm }
            );

            // Load data
            const result = await this.model.load();

            // Update state
            this.state.records = result.records;
            this.state.total = result.count;
            this.state.offset = result.offset;
            this.state.limit = result.limit;
            this.state.columns = this.model.getVisibleColumns();
        } catch (error) {
            this.state.error = error.message || _t("Failed to load data");
            console.error("Grid load error:", error);
        } finally {
            this.state.loading = false;
        }
    }

    /**
     * Extract column configuration from view arch
     */
    _getColumnsFromArch() {
        const archInfo = this.props.archInfo;
        if (!archInfo || !archInfo.children) {
            return this._getDefaultColumns();
        }

        const columns = [];
        archInfo.children.forEach(node => {
            if (node.tag === "field") {
                const fieldName = node.attrs.name;
                const fieldInfo = this.props.fields[fieldName] || {};

                columns.push({
                    field: fieldName,
                    label: node.attrs.string || fieldInfo.string || fieldName,
                    type: fieldInfo.type || "char",
                    widget: node.attrs.widget,
                    width: parseInt(node.attrs.width) || 150,
                    sortable: node.attrs.sortable !== "false",
                    invisible: node.attrs.invisible === "1",
                    isPrimary: fieldName === "name" || fieldName === "display_name",
                });
            }
        });

        return columns;
    }

    /**
     * Get default columns when no arch is available
     */
    _getDefaultColumns() {
        const fields = this.props.fields || {};
        const columns = [];

        // Priority fields
        const priorityFields = ["name", "display_name", "email", "phone", "partner_id", "user_id", "state", "active"];

        priorityFields.forEach(fieldName => {
            if (fields[fieldName]) {
                columns.push({
                    field: fieldName,
                    label: fields[fieldName].string || fieldName,
                    type: fields[fieldName].type,
                    isPrimary: fieldName === "name",
                });
            }
        });

        // Add some additional fields
        Object.entries(fields).forEach(([name, field]) => {
            if (columns.length >= 8) return;
            if (priorityFields.includes(name)) return;
            if (name.startsWith("_") || name === "id") return;
            if (["char", "selection", "many2one", "date", "datetime"].includes(field.type)) {
                columns.push({
                    field: name,
                    label: field.string || name,
                    type: field.type,
                });
            }
        });

        return columns;
    }

    /**
     * Reload data with current state
     */
    async reload() {
        this.state.loading = true;
        try {
            const domain = this.state.getDomain(this.props.domain);
            const result = await this.model.load({
                domain,
                offset: this.state.offset,
                limit: this.state.limit,
                orderBy: this.state.sortField
                    ? [{ name: this.state.sortField, asc: this.state.sortOrder === "asc" }]
                    : [],
            });
            this.state.records = result.records;
            this.state.total = result.count;
            this.state.clearSelection();
        } catch (error) {
            this.notification.add(_t("Failed to reload data"), { type: "danger" });
        } finally {
            this.state.loading = false;
        }
    }

    // ==========================================
    // Selection Handlers
    // ==========================================

    /**
     * Toggle selection for a single record
     */
    onToggleSelection(recordId) {
        this.state.toggleSelection(recordId);
    }

    /**
     * Toggle select all
     */
    onToggleSelectAll() {
        this.state.selectAll();
    }

    /**
     * Clear all selections
     */
    onClearSelection() {
        this.state.clearSelection();
    }

    // ==========================================
    // Sort Handlers
    // ==========================================

    /**
     * Sort by column
     */
    async onSort(field) {
        this.state.setSort(field);
        await this.reload();
    }

    /**
     * Get sort indicator for column
     */
    getSortIndicator(field) {
        if (this.state.sortField !== field) return null;
        return this.state.sortOrder === "asc" ? "fa-sort-up" : "fa-sort-down";
    }

    // ==========================================
    // Pagination Handlers
    // ==========================================

    /**
     * Go to next page
     */
    async onNextPage() {
        this.state.nextPage();
        await this.reload();
    }

    /**
     * Go to previous page
     */
    async onPrevPage() {
        this.state.prevPage();
        await this.reload();
    }

    /**
     * Go to specific page
     */
    async onGoToPage(page) {
        this.state.goToPage(page);
        await this.reload();
    }

    /**
     * Change page size
     */
    async onPageSizeChange(size) {
        this.state.setPageSize(size);
        await this.reload();
    }

    // ==========================================
    // Search & Filter Handlers
    // ==========================================

    /**
     * Handle search input
     */
    onSearchInput(event) {
        const value = event.target.value;

        // Debounce search
        if (this._searchTimer) {
            clearTimeout(this._searchTimer);
        }

        this._searchTimer = setTimeout(() => {
            this.state.setSearchTerm(value);
            this.reload();
        }, 300);
    }

    /**
     * Clear search
     */
    onClearSearch() {
        this.state.setSearchTerm("");
        if (this.searchInputRef.el) {
            this.searchInputRef.el.value = "";
        }
        this.reload();
    }

    /**
     * Add filter
     */
    onAddFilter(filter) {
        this.state.addFilter(filter);
        this.reload();
    }

    /**
     * Remove filter
     */
    onRemoveFilter(index) {
        this.state.removeFilter(index);
        this.reload();
    }

    /**
     * Clear all filters
     */
    onClearFilters() {
        this.state.clearFilters();
        this.onClearSearch();
    }

    // ==========================================
    // View Mode Handlers
    // ==========================================

    /**
     * Switch to list view
     */
    onSwitchToList() {
        this.state.setViewMode("list");
    }

    /**
     * Switch to kanban view
     */
    onSwitchToKanban() {
        this.state.setViewMode("kanban");
    }

    // ==========================================
    // Record Actions
    // ==========================================

    /**
     * Open record form view
     */
    async onOpenRecord(recordId) {
        await this.action.doAction({
            type: "ir.actions.act_window",
            res_model: this.props.resModel,
            res_id: recordId,
            views: [[false, "form"]],
            target: "current",
        });
    }

    /**
     * Create new record
     */
    async onCreateRecord() {
        await this.action.doAction({
            type: "ir.actions.act_window",
            res_model: this.props.resModel,
            views: [[false, "form"]],
            target: "current",
        });
    }

    /**
     * Delete selected records
     */
    async onDeleteSelected() {
        if (this.state.selectedCount === 0) {
            return;
        }

        // Confirm deletion
        const confirmed = await this._confirmAction(
            _t("Delete Records"),
            _t("Are you sure you want to delete %s record(s)?", this.state.selectedCount)
        );

        if (confirmed) {
            try {
                await this.model.executeBulkAction(
                    Array.from(this.state.selectedIds),
                    "delete"
                );
                this.notification.add(
                    _t("Successfully deleted %s record(s)", this.state.selectedCount),
                    { type: "success" }
                );
                await this.reload();
            } catch (error) {
                this.notification.add(_t("Failed to delete records"), { type: "danger" });
            }
        }
    }

    /**
     * Archive selected records
     */
    async onArchiveSelected() {
        if (this.state.selectedCount === 0) return;

        try {
            await this.model.executeBulkAction(
                Array.from(this.state.selectedIds),
                "archive"
            );
            this.notification.add(
                _t("Successfully archived %s record(s)", this.state.selectedCount),
                { type: "success" }
            );
            await this.reload();
        } catch (error) {
            this.notification.add(_t("Failed to archive records"), { type: "danger" });
        }
    }

    /**
     * Duplicate selected records
     */
    async onDuplicateSelected() {
        if (this.state.selectedCount === 0) return;

        try {
            await this.model.executeBulkAction(
                Array.from(this.state.selectedIds),
                "duplicate"
            );
            this.notification.add(
                _t("Successfully duplicated %s record(s)", this.state.selectedCount),
                { type: "success" }
            );
            await this.reload();
        } catch (error) {
            this.notification.add(_t("Failed to duplicate records"), { type: "danger" });
        }
    }

    /**
     * Export data
     */
    async onExport() {
        // Get export data
        const columns = this.state.columns.filter(c => !c.isSelection && !c.isAction);
        const data = await this.model.getExportData(columns);

        // Create CSV content
        const headers = columns.map(c => c.label);
        const rows = data.map(record =>
            columns.map(col => {
                const value = record[col.field];
                if (Array.isArray(value)) return value[1] || value[0];
                return value ?? "";
            })
        );

        const csvContent = [
            headers.join(","),
            ...rows.map(row => row.map(cell => `"${String(cell).replace(/"/g, '""')}"`).join(","))
        ].join("\n");

        // Download file
        const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = `${this.props.resModel}_export.csv`;
        link.click();
        URL.revokeObjectURL(url);

        this.notification.add(_t("Export completed"), { type: "success" });
    }

    // ==========================================
    // Column Actions
    // ==========================================

    /**
     * Toggle column visibility
     */
    onToggleColumn(columnId) {
        this.model.toggleColumnVisibility(columnId);
        this.state.columns = this.model.getVisibleColumns();
    }

    /**
     * Resize column
     */
    onResizeColumn(columnId, width) {
        this.model.resizeColumn(columnId, width);
    }

    // ==========================================
    // Helper Methods
    // ==========================================

    /**
     * Confirm action dialog
     */
    async _confirmAction(title, message) {
        return new Promise(resolve => {
            this.dialog.add(
                "web.ConfirmationDialog",
                {
                    title,
                    body: message,
                    confirm: () => resolve(true),
                    cancel: () => resolve(false),
                }
            );
        });
    }

    /**
     * Setup keyboard shortcuts
     */
    _setupKeyboardShortcuts() {
        const root = this.rootRef.el;
        if (!root) return;

        root.addEventListener("keydown", event => {
            // Ctrl+A: Select all
            if (event.ctrlKey && event.key === "a") {
                event.preventDefault();
                this.onToggleSelectAll();
            }
            // Delete: Delete selected
            if (event.key === "Delete" && this.state.selectedCount > 0) {
                event.preventDefault();
                this.onDeleteSelected();
            }
            // Escape: Clear selection
            if (event.key === "Escape") {
                this.onClearSelection();
            }
            // Ctrl+F: Focus search
            if (event.ctrlKey && event.key === "f") {
                event.preventDefault();
                this.searchInputRef.el?.focus();
            }
        });
    }

    /**
     * Get formatted cell value for display
     */
    formatCellValue(record, column) {
        const value = record[column.field];

        if (value === null || value === undefined || value === false) {
            return "";
        }

        switch (column.type) {
            case "many2one":
                return Array.isArray(value) ? value[1] : value;
            case "many2many":
            case "one2many":
                return Array.isArray(value) ? `${value.length} records` : "";
            case "date":
                return value ? new Date(value).toLocaleDateString() : "";
            case "datetime":
                return value ? new Date(value).toLocaleString() : "";
            case "boolean":
                return value ? "Yes" : "No";
            case "monetary":
            case "float":
                return typeof value === "number" ? value.toLocaleString() : value;
            case "selection":
                // Would need field definition to get label
                return value;
            default:
                return String(value);
        }
    }
}
