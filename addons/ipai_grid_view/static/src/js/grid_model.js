/** @odoo-module **/
/**
 * IPAI Grid Model - Data Management
 *
 * Handles data fetching, caching, and state management for the grid view.
 * Implements server-side pagination, sorting, and filtering.
 */

import { Model } from "@web/model/model";
import { KeepLast } from "@web/core/utils/concurrency";

/**
 * GridModel - ORM-based data model for grid views
 */
export class GridModel extends Model {
    /**
     * Initialize the grid model
     */
    setup(params, services) {
        this.orm = services.orm;
        this.keepLast = new KeepLast();
        this.resModel = params.resModel;
        this.fields = params.fields;
        this.activeFields = params.activeFields || {};

        // State
        this.data = {
            records: [],
            count: 0,
            offset: 0,
            limit: params.limit || 10,
            domain: params.domain || [],
            context: params.context || {},
            orderBy: params.orderBy || [],
            groupBy: params.groupBy || [],
        };

        // Column configuration
        this.columns = this._buildColumns(params.columns || []);

        // Cache for record data
        this._cache = new Map();
    }

    /**
     * Build column configuration from parameters
     */
    _buildColumns(columnDefs) {
        const defaultColumns = [
            {
                id: "_selection",
                field: "_selection",
                label: "",
                type: "checkbox",
                width: 40,
                sortable: false,
                filterable: false,
                isSelection: true,
            },
        ];

        const columns = columnDefs.map((col, index) => ({
            id: col.id || `col_${index}`,
            field: col.field || col.name,
            label: col.label || col.string || col.field,
            type: col.type || "char",
            width: col.width || 150,
            minWidth: col.minWidth || 80,
            maxWidth: col.maxWidth || 500,
            alignment: col.alignment || "left",
            sortable: col.sortable !== false,
            filterable: col.filterable !== false,
            searchable: col.searchable !== false,
            visible: col.visible !== false,
            columnType: col.columnType || "standard",
            cssClass: col.cssClass || "",
            isPrimary: col.isPrimary || false,
            isAvatar: col.isAvatar || false,
            isAction: col.isAction || false,
        }));

        // Add action column at the end
        columns.push({
            id: "_actions",
            field: "_actions",
            label: "",
            type: "menu",
            width: 50,
            sortable: false,
            filterable: false,
            isAction: true,
        });

        return [...defaultColumns, ...columns];
    }

    /**
     * Load grid data from server
     */
    async load(params = {}) {
        const {
            offset = this.data.offset,
            limit = this.data.limit,
            domain = this.data.domain,
            orderBy = this.data.orderBy,
            context = this.data.context,
        } = params;

        // Build field list from columns
        const fields = this.columns
            .filter(col => col.field && !col.field.startsWith("_"))
            .map(col => col.field);

        // Add common fields
        if (!fields.includes("id")) fields.push("id");
        if (!fields.includes("display_name")) fields.push("display_name");

        // Build order string
        let order = null;
        if (orderBy && orderBy.length > 0) {
            order = orderBy.map(o => `${o.name} ${o.asc ? "ASC" : "DESC"}`).join(", ");
        }

        try {
            // Execute search_read with keepLast to handle race conditions
            const result = await this.keepLast.add(
                this.orm.searchRead(
                    this.resModel,
                    domain,
                    fields,
                    {
                        offset,
                        limit,
                        order,
                        context,
                    }
                )
            );

            // Get total count
            const count = await this.orm.searchCount(this.resModel, domain, { context });

            // Update state
            this.data.records = result;
            this.data.count = count;
            this.data.offset = offset;
            this.data.limit = limit;
            this.data.domain = domain;
            this.data.orderBy = orderBy;
            this.data.context = context;

            // Update cache
            result.forEach(record => this._cache.set(record.id, record));

            return {
                records: result,
                count,
                offset,
                limit,
            };
        } catch (error) {
            console.error("GridModel load error:", error);
            throw error;
        }
    }

    /**
     * Reload current data
     */
    async reload() {
        return this.load();
    }

    /**
     * Load a specific record by ID
     */
    async loadRecord(recordId) {
        // Check cache first
        if (this._cache.has(recordId)) {
            return this._cache.get(recordId);
        }

        const fields = this.columns
            .filter(col => col.field && !col.field.startsWith("_"))
            .map(col => col.field);

        const result = await this.orm.read(this.resModel, [recordId], fields);

        if (result.length > 0) {
            this._cache.set(recordId, result[0]);
            return result[0];
        }

        return null;
    }

    /**
     * Update a record
     */
    async updateRecord(recordId, values) {
        await this.orm.write(this.resModel, [recordId], values);
        this._cache.delete(recordId);
        return this.loadRecord(recordId);
    }

    /**
     * Delete records
     */
    async deleteRecords(recordIds) {
        await this.orm.unlink(this.resModel, recordIds);
        recordIds.forEach(id => this._cache.delete(id));
        return this.reload();
    }

    /**
     * Create a new record
     */
    async createRecord(values) {
        const id = await this.orm.create(this.resModel, values);
        return this.loadRecord(id);
    }

    /**
     * Execute bulk action on records
     */
    async executeBulkAction(recordIds, action, params = {}) {
        switch (action) {
            case "delete":
                return this.deleteRecords(recordIds);
            case "archive":
                await this.orm.write(this.resModel, recordIds, { active: false });
                return this.reload();
            case "unarchive":
                await this.orm.write(this.resModel, recordIds, { active: true });
                return this.reload();
            case "duplicate":
                for (const id of recordIds) {
                    await this.orm.call(this.resModel, "copy", [[id]]);
                }
                return this.reload();
            default:
                // Custom action - call server method
                await this.orm.call(this.resModel, action, [recordIds], params);
                return this.reload();
        }
    }

    /**
     * Sort by column
     */
    sortBy(field, order = null) {
        const existingSort = this.data.orderBy.find(o => o.name === field);

        if (existingSort && order === null) {
            // Toggle direction
            existingSort.asc = !existingSort.asc;
        } else if (order !== null) {
            // Set specific order
            this.data.orderBy = [{ name: field, asc: order === "asc" }];
        } else {
            // New sort
            this.data.orderBy = [{ name: field, asc: true }];
        }

        return this.load();
    }

    /**
     * Apply filter domain
     */
    async applyFilter(domain) {
        this.data.domain = domain;
        this.data.offset = 0;
        return this.load();
    }

    /**
     * Navigate to page
     */
    async goToPage(page) {
        const offset = (page - 1) * this.data.limit;
        if (offset >= 0 && offset < this.data.count) {
            return this.load({ offset });
        }
    }

    /**
     * Set page size
     */
    async setLimit(limit) {
        this.data.limit = limit;
        this.data.offset = 0;
        return this.load();
    }

    /**
     * Get visible columns
     */
    getVisibleColumns() {
        return this.columns.filter(col => col.visible);
    }

    /**
     * Toggle column visibility
     */
    toggleColumnVisibility(columnId) {
        const column = this.columns.find(col => col.id === columnId);
        if (column) {
            column.visible = !column.visible;
        }
    }

    /**
     * Reorder columns
     */
    reorderColumns(fromIndex, toIndex) {
        const column = this.columns.splice(fromIndex, 1)[0];
        this.columns.splice(toIndex, 0, column);
    }

    /**
     * Resize column
     */
    resizeColumn(columnId, width) {
        const column = this.columns.find(col => col.id === columnId);
        if (column) {
            column.width = Math.max(column.minWidth, Math.min(column.maxWidth, width));
        }
    }

    /**
     * Get current pagination state
     */
    getPagination() {
        const currentPage = Math.floor(this.data.offset / this.data.limit) + 1;
        const totalPages = Math.ceil(this.data.count / this.data.limit);
        return {
            currentPage,
            totalPages,
            total: this.data.count,
            offset: this.data.offset,
            limit: this.data.limit,
            hasNext: this.data.offset + this.data.limit < this.data.count,
            hasPrev: this.data.offset > 0,
            start: this.data.offset + 1,
            end: Math.min(this.data.offset + this.data.limit, this.data.count),
        };
    }

    /**
     * Get records for export
     */
    async getExportData(columns, domain = null) {
        const fields = columns.map(col => col.field).filter(f => !f.startsWith("_"));
        const exportDomain = domain || this.data.domain;

        // Fetch all matching records (no limit)
        return this.orm.searchRead(
            this.resModel,
            exportDomain,
            fields,
            {
                order: this.data.orderBy.map(o => `${o.name} ${o.asc ? "ASC" : "DESC"}`).join(", "),
                context: this.data.context,
            }
        );
    }
}
