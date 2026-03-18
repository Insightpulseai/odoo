/** @odoo-module **/
import { registry } from "@web/core/registry";
import { Component, onMounted, useRef, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

class OmcClarityDashboard extends Component {
    setup() {
        this.orm = useService("orm");
        this.chartRef = "echarts_main";
        this.logframeChartRef = "echarts_logframe";
        this.phases = [];
        this.logframe = [];
        this.complianceMetrics = {};

        onWillStart(async () => {
            await this.loadData();
        });

        onMounted(() => {
            this.renderChart();
            this.renderLogframeChart();
        });
    }

    async loadData() {
        const domain = [['x_is_phase', '=', true]];
        const fields = ['name', 'x_todo_ids'];

        this.phases = await this.orm.searchRead("project.task", domain, fields);

        for (let phase of this.phases) {
            const todos = await this.orm.searchRead("x_finance.todo", [['x_task_id', '=', phase.id]], ['x_is_done']);
            phase.total_todos = todos.length;
            phase.done_todos = todos.filter(t => t.x_is_done).length;
            phase.completion = phase.total_todos > 0 ? Math.round((phase.done_todos / phase.total_todos) * 100) : 0;
        }

        // Load logframe data
        this.logframe = await this.orm.searchRead("omc.logframe", [],
            ['x_name', 'x_level', 'x_indicator', 'x_target', 'x_task_ids']);

        // Calculate compliance metrics
        await this.calculateComplianceMetrics();

        if (this.chartInstance) {
            this.renderChart();
        }
        if (this.logframeChartInstance) {
            this.renderLogframeChart();
        }
    }

    async calculateComplianceMetrics() {
        // Get all tasks with deadlines
        const allTasks = await this.orm.searchRead("project.task",
            [['date_deadline', '!=', false], ['project_id.name', '=', 'TBWA SMP – Month-End Closing & Tax Filing 2025–2026']],
            ['name', 'date_deadline', 'stage_id']
        );

        const today = new Date();
        let onTimeCount = 0;
        let totalCompleted = 0;
        let lateCount = 0;

        for (let task of allTasks) {
            const deadline = new Date(task.date_deadline);

            // Check if task is done (stage contains "done" or "closed")
            if (task.stage_id && task.stage_id[1]) {
                const stageName = task.stage_id[1].toLowerCase();
                if (stageName.includes('done') || stageName.includes('closed') || stageName.includes('complete')) {
                    totalCompleted++;

                    // For now, assume completed tasks were on time if deadline is in the future or within 7 days past
                    const daysDiff = Math.floor((today - deadline) / (1000 * 60 * 60 * 24));
                    if (daysDiff <= 7) {
                        onTimeCount++;
                    } else {
                        lateCount++;
                    }
                }
            }
        }

        // Calculate IM1 and IM2 completion rates from linked tasks
        const im1 = this.logframe.find(lf => lf.x_level === 'im1');
        const im2 = this.logframe.find(lf => lf.x_level === 'im2');

        this.complianceMetrics = {
            totalTasks: allTasks.length,
            completedTasks: totalCompleted,
            onTimeSubmissions: totalCompleted > 0 ? Math.round((onTimeCount / totalCompleted) * 100) : 0,
            lateSubmissions: lateCount,
            im1Completion: im1 && im1.x_task_ids ? Math.round((im1.x_task_ids.length / 13) * 100) : 0, // 13 total IM1 tasks
            im2Completion: im2 && im2.x_task_ids ? Math.round((im2.x_task_ids.length / 4) * 100) : 0, // 4 total IM2 tasks
            goalTarget: 100,
            goalActual: totalCompleted > 0 ? Math.round((onTimeCount / totalCompleted) * 100) : 0
        };
    }

    renderChart() {
        const chartDom = document.getElementById(this.chartRef);
        if (!chartDom) return;

        this.chartInstance = echarts.init(chartDom);

        const option = {
            tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
            legend: { data: ['Total To-Dos', 'Completed', '% Completion'] },
            grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
            xAxis: {
                type: 'value',
                boundaryGap: [0, 0.01]
            },
            yAxis: {
                type: 'category',
                data: this.phases.map(p => p.name)
            },
            series: [
                {
                    name: 'Total To-Dos',
                    type: 'bar',
                    data: this.phases.map(p => p.total_todos),
                    itemStyle: { color: '#e0e0e0' }
                },
                {
                    name: 'Completed',
                    type: 'bar',
                    data: this.phases.map(p => p.done_todos),
                    itemStyle: { color: '#28a745' }
                },
                {
                    name: '% Completion',
                    type: 'line',
                    xAxisIndex: 0,
                    data: this.phases.map(p => p.completion),
                    symbol: 'circle',
                    itemStyle: { color: '#007bff' }
                }
            ]
        };

        this.chartInstance.setOption(option);
    }

    renderLogframeChart() {
        const chartDom = document.getElementById(this.logframeChartRef);
        if (!chartDom) return;

        this.logframeChartInstance = echarts.init(chartDom);

        const option = {
            title: {
                text: 'Logical Framework Compliance Dashboard',
                left: 'center',
                textStyle: { fontSize: 18, fontWeight: 'bold' }
            },
            tooltip: { trigger: 'item' },
            legend: {
                orient: 'horizontal',
                bottom: '0%',
                data: ['Goal', 'IM1: Month-End', 'IM2: Tax Filing']
            },
            grid: [
                { left: '5%', top: '15%', width: '40%', height: '65%' },
                { left: '55%', top: '15%', width: '40%', height: '65%' }
            ],
            xAxis: [
                { type: 'category', gridIndex: 0, data: ['Goal', 'IM1', 'IM2'] },
                { type: 'value', gridIndex: 1, max: 100, axisLabel: { formatter: '{value}%' } }
            ],
            yAxis: [
                { type: 'value', gridIndex: 0, max: 100, axisLabel: { formatter: '{value}%' } },
                { type: 'category', gridIndex: 1, data: ['On-Time %', 'IM1 Progress', 'IM2 Progress'] }
            ],
            series: [
                {
                    name: 'Compliance Metrics',
                    type: 'bar',
                    xAxisIndex: 0,
                    yAxisIndex: 0,
                    data: [
                        {
                            value: this.complianceMetrics.goalActual,
                            itemStyle: {
                                color: this.complianceMetrics.goalActual >= 95 ? '#28a745' :
                                    this.complianceMetrics.goalActual >= 80 ? '#ffc107' : '#dc3545'
                            }
                        },
                        {
                            value: this.complianceMetrics.im1Completion,
                            itemStyle: {
                                color: this.complianceMetrics.im1Completion >= 95 ? '#28a745' :
                                    this.complianceMetrics.im1Completion >= 80 ? '#ffc107' : '#dc3545'
                            }
                        },
                        {
                            value: this.complianceMetrics.im2Completion,
                            itemStyle: {
                                color: this.complianceMetrics.im2Completion >= 95 ? '#28a745' :
                                    this.complianceMetrics.im2Completion >= 80 ? '#ffc107' : '#dc3545'
                            }
                        }
                    ],
                    label: {
                        show: true,
                        position: 'top',
                        formatter: '{c}%'
                    }
                },
                {
                    name: 'Performance Indicators',
                    type: 'bar',
                    xAxisIndex: 1,
                    yAxisIndex: 1,
                    data: [
                        this.complianceMetrics.onTimeSubmissions,
                        this.complianceMetrics.im1Completion,
                        this.complianceMetrics.im2Completion
                    ],
                    itemStyle: { color: '#007bff' },
                    label: {
                        show: true,
                        position: 'right',
                        formatter: '{c}%'
                    }
                }
            ]
        };

        this.logframeChartInstance.setOption(option);
    }
}

OmcClarityDashboard.template = "omc_finance_ppm.Dashboard";

registry.category("actions").add("omc_finance_ppm.dashboard_client_action", OmcClarityDashboard);
