/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, onWillStart, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

/**
 * IPAI Project Gantt - CE-safe Gantt-like planning view
 *
 * Displays tasks with ipai_planned_start/end as horizontal bars
 * on a timeline. Click to open task form.
 */
class IpaiProjectGantt extends Component {
    setup() {
        this.orm = useService("orm");
        this.action = useService("action");

        this.state = useState({
            loading: true,
            tasks: [],
            projects: [],
            error: null,
            selectedProjectId: null,
            from: null,
            to: null,
            viewMode: "week", // week, month, quarter
        });

        onWillStart(async () => {
            try {
                // Default window: last 14 days to next 60 days
                const now = new Date();
                const from = new Date(now.getTime() - 14 * 86400000);
                const to = new Date(now.getTime() + 60 * 86400000);
                this.state.from = from.toISOString().slice(0, 10);
                this.state.to = to.toISOString().slice(0, 10);

                await this.loadProjects();
                await this.loadTasks();
            } catch (e) {
                this.state.error = String(e?.message || e);
            } finally {
                this.state.loading = false;
            }
        });
    }

    async loadProjects() {
        const projects = await this.orm.searchRead(
            "project.project",
            [["active", "=", true]],
            ["id", "name"],
            { order: "name asc", limit: 100 }
        );
        this.state.projects = projects;
    }

    async loadTasks() {
        const domain = [
            ["active", "=", true],
            ["ipai_planned_start", "!=", false],
            ["ipai_planned_end", "!=", false],
        ];

        if (this.state.selectedProjectId) {
            domain.push(["project_id", "=", this.state.selectedProjectId]);
        }

        const fields = [
            "name",
            "project_id",
            "user_ids",
            "stage_id",
            "ipai_planned_start",
            "ipai_planned_end",
            "ipai_planned_duration",
            "date_deadline",
            "priority",
            "color",
        ];

        const tasks = await this.orm.searchRead("project.task", domain, fields, {
            limit: 500,
            order: "ipai_planned_start asc",
        });

        this.state.tasks = tasks.map((t) => ({
            id: t.id,
            name: t.name,
            project: t.project_id?.[1] || "",
            projectId: t.project_id?.[0] || null,
            stage: t.stage_id?.[1] || "",
            start: t.ipai_planned_start,
            end: t.ipai_planned_end,
            duration: t.ipai_planned_duration || 0,
            deadline: t.date_deadline || null,
            priority: t.priority || "0",
            color: t.color || 0,
        }));
    }

    getRange() {
        if (!this.state.tasks.length) {
            const now = Date.now();
            return { min: now - 7 * 86400000, max: now + 30 * 86400000 };
        }
        const starts = this.state.tasks.map((t) => new Date(t.start).getTime());
        const ends = this.state.tasks.map((t) => new Date(t.end).getTime());
        const min = Math.min(...starts);
        const max = Math.max(...ends);
        // Add padding
        const padding = (max - min) * 0.05 || 86400000;
        return { min: min - padding, max: Math.max(max + padding, min + 86400000) };
    }

    getBarStyle(task) {
        const range = this.getRange();
        const s = new Date(task.start).getTime();
        const e = new Date(task.end).getTime();
        const left = Math.round(((s - range.min) / (range.max - range.min)) * 100);
        const width = Math.max(1, Math.round(((e - s) / (range.max - range.min)) * 100));
        return `left: ${left}%; width: ${width}%;`;
    }

    getBarColor(task) {
        const colors = [
            "#3b82f6", // blue
            "#22c55e", // green
            "#f59e0b", // amber
            "#ef4444", // red
            "#8b5cf6", // violet
            "#ec4899", // pink
            "#14b8a6", // teal
            "#f97316", // orange
            "#6366f1", // indigo
            "#84cc16", // lime
        ];
        return colors[task.color % colors.length];
    }

    formatDate(dateStr) {
        if (!dateStr) return "";
        return dateStr.slice(0, 10);
    }

    async onProjectChange(ev) {
        const value = ev.target.value;
        this.state.selectedProjectId = value ? parseInt(value, 10) : null;
        this.state.loading = true;
        try {
            await this.loadTasks();
        } finally {
            this.state.loading = false;
        }
    }

    async refresh() {
        this.state.loading = true;
        try {
            await this.loadTasks();
        } finally {
            this.state.loading = false;
        }
    }

    openTask(taskId) {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "project.task",
            res_id: taskId,
            views: [[false, "form"]],
            target: "current",
        });
    }

    openTaskList() {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "project.task",
            views: [[false, "list"], [false, "form"]],
            domain: [["ipai_planned_start", "!=", false], ["ipai_planned_end", "!=", false]],
            context: { search_default_has_planned_dates: 1 },
            target: "current",
        });
    }
}

IpaiProjectGantt.template = "ipai_project_gantt.IpaiProjectGantt";
registry.category("actions").add("ipai_project_gantt.gantt", IpaiProjectGantt);
