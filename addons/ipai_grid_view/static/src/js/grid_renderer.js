/** @odoo-module **/
/**
 * IPAI Grid Renderer - UI Rendering Component
 *
 * Handles the visual rendering of the grid, including:
 * - Table structure (headers, rows, cells)
 * - Row selection checkboxes
 * - Sort indicators
 * - Column resizing
 * - Cell formatting and widgets
 */

import { Component, useState, useRef, onMounted, onWillUpdateProps } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";

/**
 * GridRenderer - Renders the grid/table UI
 */
export class GridRenderer extends Component {
    static template = "ipai_grid_view.GridRenderer";

    static props = {
        // Data
        records: { type: Array },
        columns: { type: Array },
        total: { type: Number },

        // State
        loading: { type: Boolean },
        selectedIds: { type: Object }, // Set
        allSelected: { type: Boolean },
        sortField: { type: String, optional: true },
        sortOrder: { type: String, optional: true },

        // Pagination
        offset: { type: Number },
        limit: { type: Number },

        // Callbacks
        onToggleSelection: { type: Function },
        onToggleSelectAll: { type: Function },
        onSort: { type: Function },
        onOpenRecord: { type: Function },
        onNextPage: { type: Function },
        onPrevPage: { type: Function },
        formatCellValue: { type: Function },
    };

    setup() {
        this.tableRef = useRef("table");
        this.resizingColumn = null;
        this.resizeStartX = 0;
        this.resizeStartWidth = 0;

        // Local state for hover effects
        this.state = useState({
            hoveredRow: null,
            hoveredColumn: null,
            resizing: false,
        });

        onMounted(() => {
            this._setupResizeHandlers();
        });
    }

    /**
     * Get pagination info
     */
    get pagination() {
        const currentPage = Math.floor(this.props.offset / this.props.limit) + 1;
        const totalPages = Math.ceil(this.props.total / this.props.limit);
        return {
            currentPage,
            totalPages,
            hasNext: this.props.offset + this.props.limit < this.props.total,
            hasPrev: this.props.offset > 0,
            start: this.props.offset + 1,
            end: Math.min(this.props.offset + this.props.limit, this.props.total),
        };
    }

    /**
     * Get visible columns only
     */
    get visibleColumns() {
        return this.props.columns.filter(col => col.visible !== false);
    }

    /**
     * Check if record is selected
     */
    isSelected(recordId) {
        return this.props.selectedIds.has(recordId);
    }

    /**
     * Handle row click
     */
    onRowClick(recordId, event) {
        // Don't open if clicking checkbox or action menu
        if (event.target.closest(".o_grid_checkbox, .o_grid_action_menu")) {
            return;
        }
        this.props.onOpenRecord(recordId);
    }

    /**
     * Handle checkbox click
     */
    onCheckboxClick(recordId, event) {
        event.stopPropagation();
        this.props.onToggleSelection(recordId);
    }

    /**
     * Handle header checkbox click
     */
    onHeaderCheckboxClick(event) {
        event.stopPropagation();
        this.props.onToggleSelectAll();
    }

    /**
     * Handle column header click for sorting
     */
    onColumnHeaderClick(column, event) {
        if (!column.sortable) return;
        this.props.onSort(column.field);
    }

    /**
     * Get sort icon class for column
     */
    getSortIcon(column) {
        if (this.props.sortField !== column.field) {
            return "fa-sort text-muted";
        }
        return this.props.sortOrder === "asc" ? "fa-sort-up" : "fa-sort-down";
    }

    /**
     * Get cell alignment class
     */
    getCellAlignment(column) {
        switch (column.alignment) {
            case "center":
                return "text-center";
            case "right":
                return "text-end";
            default:
                return "text-start";
        }
    }

    /**
     * Get row classes
     */
    getRowClasses(record, index) {
        const classes = ["o_grid_row"];
        if (this.isSelected(record.id)) {
            classes.push("o_grid_row_selected");
        }
        if (this.state.hoveredRow === index) {
            classes.push("o_grid_row_hover");
        }
        if (index % 2 === 1) {
            classes.push("o_grid_row_odd");
        }
        return classes.join(" ");
    }

    /**
     * Handle row hover
     */
    onRowMouseEnter(index) {
        this.state.hoveredRow = index;
    }

    onRowMouseLeave() {
        this.state.hoveredRow = null;
    }

    /**
     * Render cell value based on column type
     */
    getCellValue(record, column) {
        if (column.isSelection || column.isAction) {
            return null;
        }
        return this.props.formatCellValue(record, column);
    }

    /**
     * Get cell widget class
     */
    getCellWidgetClass(column) {
        const classes = ["o_grid_cell"];

        switch (column.columnType) {
            case "badge":
                classes.push("o_grid_cell_badge");
                break;
            case "avatar":
                classes.push("o_grid_cell_avatar");
                break;
            case "progress":
                classes.push("o_grid_cell_progress");
                break;
            case "link":
                classes.push("o_grid_cell_link");
                break;
            case "activity":
                classes.push("o_grid_cell_activity");
                break;
        }

        if (column.isPrimary) {
            classes.push("o_grid_cell_primary");
        }

        if (column.cssClass) {
            classes.push(column.cssClass);
        }

        return classes.join(" ");
    }

    /**
     * Setup column resize handlers
     */
    _setupResizeHandlers() {
        const table = this.tableRef.el;
        if (!table) return;

        // Mouse move handler for resizing
        const onMouseMove = (event) => {
            if (!this.resizingColumn) return;

            const diff = event.clientX - this.resizeStartX;
            const newWidth = Math.max(80, this.resizeStartWidth + diff);

            const header = table.querySelector(`th[data-column="${this.resizingColumn}"]`);
            if (header) {
                header.style.width = `${newWidth}px`;
            }
        };

        // Mouse up handler to end resize
        const onMouseUp = () => {
            if (this.resizingColumn) {
                this.resizingColumn = null;
                this.state.resizing = false;
                document.body.style.cursor = "";
            }
        };

        document.addEventListener("mousemove", onMouseMove);
        document.addEventListener("mouseup", onMouseUp);
    }

    /**
     * Start column resize
     */
    onResizeStart(column, event) {
        event.preventDefault();
        event.stopPropagation();

        this.resizingColumn = column.id;
        this.resizeStartX = event.clientX;
        this.state.resizing = true;

        const table = this.tableRef.el;
        const header = table.querySelector(`th[data-column="${column.id}"]`);
        if (header) {
            this.resizeStartWidth = header.offsetWidth;
        }

        document.body.style.cursor = "col-resize";
    }

    /**
     * Get column style with width
     */
    getColumnStyle(column) {
        return `width: ${column.width}px; min-width: ${column.minWidth || 80}px;`;
    }

    /**
     * Handle action menu click
     */
    onActionMenuClick(record, event) {
        event.stopPropagation();
        // Toggle action menu dropdown
        const menu = event.target.closest(".o_grid_action_menu");
        const dropdown = menu.querySelector(".o_grid_action_dropdown");
        if (dropdown) {
            dropdown.classList.toggle("show");
        }
    }

    /**
     * Execute row action
     */
    onRowAction(record, action, event) {
        event.stopPropagation();

        switch (action) {
            case "open":
                this.props.onOpenRecord(record.id);
                break;
            case "edit":
                this.props.onOpenRecord(record.id);
                break;
            case "delete":
                // Handled by controller
                break;
            case "duplicate":
                // Handled by controller
                break;
        }
    }

    /**
     * Get empty state message
     */
    get emptyStateMessage() {
        if (this.props.loading) {
            return _t("Loading...");
        }
        return _t("No records found");
    }
}

/**
 * GridCell - Individual cell component for special rendering
 */
export class GridCell extends Component {
    static template = "ipai_grid_view.GridCell";

    static props = {
        record: { type: Object },
        column: { type: Object },
        value: { type: [String, Number, Boolean, Object, Array], optional: true },
    };

    /**
     * Get avatar URL for avatar cells
     */
    get avatarUrl() {
        const record = this.props.record;
        // Use Odoo's image URL pattern
        return `/web/image?model=${record._model}&id=${record.id}&field=image_128`;
    }

    /**
     * Get badge color based on value
     */
    get badgeColor() {
        const value = this.props.value;
        // Map common status values to colors
        const colorMap = {
            draft: "secondary",
            new: "info",
            active: "success",
            done: "success",
            open: "primary",
            pending: "warning",
            cancelled: "danger",
            closed: "dark",
        };
        return colorMap[value?.toLowerCase()] || "secondary";
    }

    /**
     * Get progress bar percentage
     */
    get progressPercent() {
        const value = this.props.value;
        if (typeof value === "number") {
            return Math.min(100, Math.max(0, value));
        }
        return 0;
    }
}
