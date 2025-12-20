/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, onMounted, useRef } from "@odoo/owl";

const actionRegistry = registry.category("actions");

class FinancePpmDashboard extends Component {
    setup() {
        this.ganttRef = useRef("gantt");
        this.calendarRef = useRef("calendar");

        onMounted(() => {
            this._initCharts();
        });
    }

    _initCharts() {
        if (!window.echarts) {
            console.error("ECharts not loaded");
            return;
        }

        const ganttDom = this.ganttRef.el;
        const calDom = this.calendarRef.el;

        const ganttChart = echarts.init(ganttDom);
        const calendarChart = echarts.init(calDom);

        ganttChart.setOption(getClosingGanttOption());
        calendarChart.setOption(getTaxCalendarOption());
    }
}

FinancePpmDashboard.template = "ipai_finance_ppm_dashboard.PpmDashboard";

actionRegistry.add("ipai_finance_ppm_dashboard.action", FinancePpmDashboard);

/**
 * Static demo options – wire to real Odoo data later.
 * These mirror the examples we discussed.
 */

function getClosingGanttOption() {
    const categories = [
        "Foundation & Corp",
        "Revenue / WIP",
        "VAT & Tax Reporting",
        "Working Capital"
    ];

    const data = [
        [0, "2025-11-24", "2025-11-27", "Accrue monthly expense for employee cellphone allowance", "CKVC"],
        [0, "2025-11-24", "2025-11-28", "Record monthly recognition of computer-related costs", "CKVC"],
        [1, "2025-11-25", "2025-11-29", "Prepare WIP schedule summary per job", "JPAL"],
        [2, "2025-11-26", "2025-11-29", "Compile & record VAT reports", "JAP"],
        [3, "2025-11-24", "2025-11-30", "Prepare AP aging report", "RIM"],
    ];

    return {
        title: { text: "November 2025 Month-End Close (PPM)", left: "center" },
        tooltip: {
            formatter: params => {
                const d = params.data;
                return [
                    `<b>${d[3]}</b>`,
                    `Lane: ${categories[d[0]]}`,
                    `Owner: ${d[4]}`,
                    `Start: ${d[1]}`,
                    `End: ${d[2]}`
                ].join("<br/>");
            },
        },
        grid: { top: 60, left: 140, right: 40, bottom: 40 },
        xAxis: {
            type: "time",
            min: "2025-11-23",
            max: "2025-12-01",
        },
        yAxis: {
            type: "category",
            data: categories,
        },
        series: [{
            type: "custom",
            encode: { x: [1, 2], y: 0 },
            renderItem: (params, api) => {
                const categoryIndex = api.value(0);
                const start = api.coord([api.value(1), categoryIndex]);
                const end = api.coord([api.value(2), categoryIndex]);
                const height = api.size([0, 1])[1] * 0.6;
                return {
                    type: "rect",
                    shape: {
                        x: start[0],
                        y: start[1] - height / 2,
                        width: end[0] - start[0],
                        height: height,
                    },
                    style: api.style(),
                };
            },
            data,
        }],
    };
}

function getTaxCalendarOption() {
    const birEvents = [
        ["2026-01-10", 4], // sample – 1601C deadline + approvals
        ["2026-01-12", 2],
        ["2026-01-13", 3],
        ["2026-04-15", 4],
        ["2026-07-27", 4],
        ["2026-10-26", 4],
    ];

    return {
        title: { text: "BIR Filing Calendar 2026", left: "center" },
        tooltip: {
            formatter: params => {
                const [date, value] = params.data;
                return `${date}<br/>Load: ${value} step(s) / form(s)`;
            },
        },
        visualMap: {
            min: 0,
            max: 4,
            orient: "horizontal",
            left: "center",
            top: 35,
            calculable: true,
        },
        calendar: {
            range: "2026",
            cellSize: ["auto", 18],
            top: 80,
            left: 40,
            right: 20,
            bottom: 20,
        },
        series: [{
            type: "heatmap",
            coordinateSystem: "calendar",
            data: birEvents,
        }],
    };
}
