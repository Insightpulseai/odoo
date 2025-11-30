/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, onMounted, useRef } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class PpmDashboard extends Component {
    setup() {
        this.orm = useService("orm");
        this.chartRefs = {
            planning: useRef("planning"),
            portfolio: useRef("portfolio"),
            scenario: useRef("scenario"),
            intake: useRef("intake"),
        };

        onMounted(() => {
            this.loadData();
        });
    }

    async loadData() {
        const [kpiData, strategyData, periodsData, intakeData, insightsData] = await Promise.all([
            this.orm.searchRead("ppm.dashboard.kpi", [], ["projects_ongoing", "total_cost", "cost_variance", "project_health_score", "budget_health_score"], { limit: 1 }),
            this.orm.searchRead("ppm.strategy.spend", [], ["strategy", "spend"]),
            this.orm.searchRead("ppm.financial.period", [], ["period_code", "cost_type", "planned_value", "actual_cost", "earned_value"]),
            this.orm.searchRead("ppm.intake.request", [], ["name", "business_value_score", "ease_of_implementation", "strategic_alignment_score", "status"]),
            this.orm.searchRead("ppm.ai.insight", [], ["name", "insight_summary", "severity"]),
        ]);

        this.dashboardData = {
            kpi: kpiData.length ? kpiData[0] : {},
            strategySpend: strategyData,
            financialPeriods: periodsData,
            intakeRequests: intakeData,
            aiInsights: insightsData,
        };

        this.renderCharts();
    }

    renderCharts() {
        this.renderPlanningGauges();
        this.renderPortfolioTreemap();
        this.renderScenarioArea();
        this.renderIntakeHeatmap();
    }

    renderPlanningGauges() {
        const el = this.chartRefs.planning.el;
        if (!el || !window.echarts) return;
        const chart = echarts.init(el);

        const kpi = this.dashboardData.kpi || {};
        const projectHealth = kpi.project_health_score || 0;
        const budgetHealth = kpi.budget_health_score || 0;

        const option = {
            title: { text: "Project & Budget Health", left: "center" },
            tooltip: { formatter: "{a} <br/>{b}: {c}%" },
            series: [
                {
                    name: "Project Health",
                    type: "gauge",
                    radius: "45%",
                    center: ["30%", "60%"],
                    min: 0,
                    max: 100,
                    detail: { formatter: "{value}%" },
                    data: [{ value: projectHealth, name: "Project Health" }],
                },
                {
                    name: "Budget Health",
                    type: "gauge",
                    radius: "45%",
                    center: ["70%", "60%"],
                    min: 0,
                    max: 100,
                    detail: { formatter: "{value}%" },
                    data: [{ value: budgetHealth, name: "Budget Health" }],
                },
            ],
        };
        chart.setOption(option);
        this.attachResize(chart);
    }

    renderPortfolioTreemap() {
        const el = this.chartRefs.portfolio.el;
        if (!el || !window.echarts) return;
        const chart = echarts.init(el);

        const data = (this.dashboardData.strategySpend || []).map((row) => ({
            name: row.strategy,
            value: row.spend,
        }));

        const option = {
            title: { text: "Total Spend by Strategy", left: "center" },
            tooltip: {
                formatter: (info) => `${info.name}: ${info.value.toLocaleString()}`,
            },
            series: [
                {
                    type: "treemap",
                    roam: false,
                    nodeClick: false,
                    data: data,
                },
            ],
        };
        chart.setOption(option);
        this.attachResize(chart);
    }

    renderScenarioArea() {
        const el = this.chartRefs.scenario.el;
        if (!el || !window.echarts) return;
        const chart = echarts.init(el);

        const rows = this.dashboardData.financialPeriods || [];
        const periods = [...new Set(rows.map((r) => r.period_code))].sort();
        const planned = [];
        const actual = [];
        const earned = [];

        periods.forEach((period) => {
            const group = rows.filter((r) => r.period_code === period);
            const sumPlanned = group.reduce((acc, r) => acc + (r.planned_value || 0), 0);
            const sumActual = group.reduce((acc, r) => acc + (r.actual_cost || 0), 0);
            const sumEarned = group.reduce((acc, r) => acc + (r.earned_value || 0), 0);
            planned.push(sumPlanned);
            actual.push(sumActual);
            earned.push(sumEarned);
        });

        const option = {
            title: { text: "Scenario Analysis – Budget vs Actual vs Earned", left: "center" },
            tooltip: { trigger: "axis" },
            legend: { top: 30 },
            xAxis: { type: "category", data: periods },
            yAxis: { type: "value" },
            series: [
                { name: "Planned Value", type: "line", stack: "total", areaStyle: {}, data: planned },
                { name: "Actual Cost", type: "line", stack: "total", areaStyle: {}, data: actual },
                { name: "Earned Value", type: "line", stack: "total", areaStyle: {}, data: earned },
            ],
        };
        chart.setOption(option);
        this.attachResize(chart);
    }

    renderIntakeHeatmap() {
        const el = this.chartRefs.intake.el;
        if (!el || !window.echarts) return;
        const chart = echarts.init(el);

        const rows = this.dashboardData.intakeRequests || [];
        const projects = rows.map((r) => r.name);
        const metrics = ["Business Value", "Ease of Implementation", "Strategic Alignment"];

        const data = [];
        rows.forEach((r, rowIdx) => {
            data.push([0, rowIdx, r.business_value_score || 0]);
            data.push([1, rowIdx, r.ease_of_implementation || 0]);
            data.push([2, rowIdx, r.strategic_alignment_score || 0]);
        });

        const option = {
            title: { text: "Project Intake – Score Heatmap", left: "center" },
            tooltip: {
                position: "top",
                formatter: (params) => {
                    const metric = metrics[params.data[0]];
                    const proj = projects[params.data[1]];
                    return `${proj}<br/>${metric}: ${params.data[2]}`;
                },
            },
            grid: { height: "70%", top: 60, left: 110 },
            xAxis: {
                type: "category",
                data: metrics,
                axisLabel: { rotate: 0 },
            },
            yAxis: {
                type: "category",
                data: projects,
            },
            visualMap: {
                min: 0,
                max: 10,
                calculable: true,
                orient: "horizontal",
                left: "center",
                bottom: 10,
            },
            series: [
                {
                    name: "Score",
                    type: "heatmap",
                    data: data,
                    label: { show: true },
                },
            ],
        };
        chart.setOption(option);
        this.attachResize(chart);
    }

    attachResize(chart) {
        window.addEventListener("resize", () => {
            chart.resize();
        });
    }
}

PpmDashboard.template = "ipai_ppm_demo.PpmDashboardMain";

registry.category("actions").add("ppm_dashboard_client_action", PpmDashboard);
