/**
 * DO Advisor - ECharts Metrics Visualization
 *
 * Azure-style charts for resource usage, cost trends, and job success rates
 */

let resourceChart = null;
let costChart = null;
let jobsChart = null;
let chartColors = {};

/**
 * Initialize all charts with Azure dark theme
 */
function initializeCharts(colors) {
    chartColors = colors || {
        primary: '#0078d4',
        success: '#107c10',
        warning: '#ffaa44',
        critical: '#d13438',
        muted: '#797775',
        series: ['#0078d4', '#8764b8', '#107c10', '#ffaa44', '#d13438', '#00bcf2'],
    };

    // Register Azure dark theme
    echarts.registerTheme('azureDark', getAzureDarkTheme());

    // Initialize charts
    initResourceChart();
    initCostChart();
    initJobsChart();

    // Handle resize
    window.addEventListener('resize', () => {
        resourceChart?.resize();
        costChart?.resize();
        jobsChart?.resize();
    });
}

/**
 * Azure Dark Theme Configuration
 */
function getAzureDarkTheme() {
    return {
        backgroundColor: 'transparent',
        textStyle: {
            color: '#d2d0ce',
            fontFamily: 'Segoe UI, -apple-system, sans-serif',
        },
        title: {
            textStyle: {
                color: '#ffffff',
            },
        },
        legend: {
            textStyle: {
                color: '#d2d0ce',
            },
        },
        tooltip: {
            backgroundColor: '#3b3a39',
            borderColor: '#484644',
            textStyle: {
                color: '#ffffff',
            },
        },
        xAxis: {
            axisLine: {
                lineStyle: {
                    color: '#484644',
                },
            },
            axisTick: {
                lineStyle: {
                    color: '#484644',
                },
            },
            axisLabel: {
                color: '#a19f9d',
            },
            splitLine: {
                lineStyle: {
                    color: '#323130',
                },
            },
        },
        yAxis: {
            axisLine: {
                lineStyle: {
                    color: '#484644',
                },
            },
            axisTick: {
                lineStyle: {
                    color: '#484644',
                },
            },
            axisLabel: {
                color: '#a19f9d',
            },
            splitLine: {
                lineStyle: {
                    color: '#323130',
                },
            },
        },
        grid: {
            borderColor: '#484644',
        },
    };
}

/**
 * Resource Usage Chart (Line)
 */
function initResourceChart() {
    const container = document.getElementById('resource-chart');
    if (!container) return;

    resourceChart = echarts.init(container, 'azureDark');

    const option = {
        tooltip: {
            trigger: 'axis',
            axisPointer: {
                type: 'cross',
                label: {
                    backgroundColor: '#3b3a39',
                },
            },
        },
        legend: {
            data: ['CPU', 'Memory', 'Network'],
            top: 0,
            right: 0,
            textStyle: {
                fontSize: 11,
            },
        },
        grid: {
            left: 40,
            right: 20,
            top: 30,
            bottom: 30,
        },
        xAxis: {
            type: 'category',
            boundaryGap: false,
            data: [],
            axisLabel: {
                fontSize: 10,
            },
        },
        yAxis: {
            type: 'value',
            max: 100,
            axisLabel: {
                formatter: '{value}%',
                fontSize: 10,
            },
        },
        series: [
            {
                name: 'CPU',
                type: 'line',
                smooth: true,
                symbol: 'none',
                lineStyle: {
                    width: 2,
                    color: chartColors.primary,
                },
                areaStyle: {
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                        { offset: 0, color: 'rgba(0, 120, 212, 0.3)' },
                        { offset: 1, color: 'rgba(0, 120, 212, 0)' },
                    ]),
                },
                data: [],
            },
            {
                name: 'Memory',
                type: 'line',
                smooth: true,
                symbol: 'none',
                lineStyle: {
                    width: 2,
                    color: chartColors.series[1],
                },
                areaStyle: {
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                        { offset: 0, color: 'rgba(135, 100, 184, 0.3)' },
                        { offset: 1, color: 'rgba(135, 100, 184, 0)' },
                    ]),
                },
                data: [],
            },
            {
                name: 'Network',
                type: 'line',
                smooth: true,
                symbol: 'none',
                lineStyle: {
                    width: 2,
                    color: chartColors.success,
                },
                data: [],
            },
        ],
    };

    resourceChart.setOption(option);
}

/**
 * Cost Trend Chart (Bar + Line)
 */
function initCostChart() {
    const container = document.getElementById('cost-chart');
    if (!container) return;

    costChart = echarts.init(container, 'azureDark');

    const option = {
        tooltip: {
            trigger: 'axis',
            axisPointer: {
                type: 'shadow',
            },
            formatter: (params) => {
                const cost = params[0];
                return `${cost.name}<br/>Cost: $${cost.value.toFixed(2)}`;
            },
        },
        grid: {
            left: 50,
            right: 20,
            top: 20,
            bottom: 30,
        },
        xAxis: {
            type: 'category',
            data: [],
            axisLabel: {
                fontSize: 10,
            },
        },
        yAxis: {
            type: 'value',
            axisLabel: {
                formatter: '${value}',
                fontSize: 10,
            },
        },
        series: [
            {
                type: 'bar',
                barWidth: '60%',
                itemStyle: {
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                        { offset: 0, color: chartColors.primary },
                        { offset: 1, color: 'rgba(0, 120, 212, 0.3)' },
                    ]),
                    borderRadius: [4, 4, 0, 0],
                },
                data: [],
            },
        ],
    };

    costChart.setOption(option);
}

/**
 * Job Success Rate Chart (Stacked Bar)
 */
function initJobsChart() {
    const container = document.getElementById('jobs-chart');
    if (!container) return;

    jobsChart = echarts.init(container, 'azureDark');

    const option = {
        tooltip: {
            trigger: 'axis',
            axisPointer: {
                type: 'shadow',
            },
        },
        legend: {
            show: false, // Using custom legend in HTML
        },
        grid: {
            left: 40,
            right: 20,
            top: 10,
            bottom: 30,
        },
        xAxis: {
            type: 'category',
            data: [],
            axisLabel: {
                fontSize: 10,
            },
        },
        yAxis: {
            type: 'value',
            max: 100,
            axisLabel: {
                formatter: '{value}',
                fontSize: 10,
            },
        },
        series: [
            {
                name: 'Success',
                type: 'bar',
                stack: 'total',
                barWidth: '50%',
                itemStyle: {
                    color: chartColors.success,
                    borderRadius: [0, 0, 0, 0],
                },
                data: [],
            },
            {
                name: 'Failed',
                type: 'bar',
                stack: 'total',
                itemStyle: {
                    color: chartColors.critical,
                },
                data: [],
            },
            {
                name: 'Skipped',
                type: 'bar',
                stack: 'total',
                itemStyle: {
                    color: chartColors.muted,
                    borderRadius: [4, 4, 0, 0],
                },
                data: [],
            },
        ],
    };

    jobsChart.setOption(option);
}

/**
 * Update all charts with new data
 */
function updateAllCharts(metrics) {
    if (metrics.resourceUsage) {
        updateResourceChart(metrics.resourceUsage);
    }
    if (metrics.costTrend) {
        updateCostChart(metrics.costTrend);
    }
    if (metrics.jobSuccess) {
        updateJobsChart(metrics.jobSuccess);
    }
}

/**
 * Update Resource Usage Chart
 */
function updateResourceChart(data, range = '24h') {
    if (!resourceChart || !data) return;

    // Filter data based on range
    let filteredData = data;
    const now = Date.now();
    const ranges = {
        '1h': 3600000,
        '24h': 86400000,
        '7d': 7 * 86400000,
        '30d': 30 * 86400000,
    };

    if (ranges[range]) {
        filteredData = data.filter(d => (now - d.time.getTime()) <= ranges[range]);
    }

    const times = filteredData.map(d =>
        d.time.toLocaleTimeString('en', { hour: '2-digit', minute: '2-digit' })
    );

    resourceChart.setOption({
        xAxis: {
            data: times,
        },
        series: [
            { data: filteredData.map(d => d.cpu.toFixed(1)) },
            { data: filteredData.map(d => d.memory.toFixed(1)) },
            { data: filteredData.map(d => d.network.toFixed(1)) },
        ],
    });
}

/**
 * Update Cost Trend Chart
 */
function updateCostChart(data) {
    if (!costChart || !data) return;

    costChart.setOption({
        xAxis: {
            data: data.map(d => d.month),
        },
        series: [
            { data: data.map(d => d.cost) },
        ],
    });

    // Update cost summary in header
    const currentCost = data[data.length - 1]?.cost || 0;
    const previousCost = data[data.length - 2]?.cost || currentCost;
    const change = ((currentCost - previousCost) / previousCost * 100).toFixed(0);

    const costEl = document.getElementById('current-month-cost');
    const changeEl = document.getElementById('cost-change');

    if (costEl) costEl.textContent = currentCost.toFixed(2);
    if (changeEl) {
        changeEl.textContent = `${change >= 0 ? '+' : ''}${change}%`;
        changeEl.className = `cost-change ${change <= 0 ? 'positive' : 'negative'}`;
    }
}

/**
 * Update Jobs Success Rate Chart
 */
function updateJobsChart(data) {
    if (!jobsChart || !data) return;

    jobsChart.setOption({
        xAxis: {
            data: data.map(d => d.day),
        },
        series: [
            { data: data.map(d => d.success) },
            { data: data.map(d => d.failed) },
            { data: data.map(d => d.skipped) },
        ],
    });
}

/**
 * Create a mini gauge chart for score display
 */
function createScoreGauge(containerId, score) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const chart = echarts.init(container, 'azureDark');

    const option = {
        series: [
            {
                type: 'gauge',
                startAngle: 180,
                endAngle: 0,
                min: 0,
                max: 100,
                splitNumber: 4,
                pointer: {
                    show: false,
                },
                progress: {
                    show: true,
                    width: 12,
                    itemStyle: {
                        color: score >= 80 ? chartColors.success :
                               score >= 60 ? chartColors.warning : chartColors.critical,
                    },
                },
                axisLine: {
                    lineStyle: {
                        width: 12,
                        color: [[1, '#323130']],
                    },
                },
                axisTick: { show: false },
                splitLine: { show: false },
                axisLabel: { show: false },
                detail: {
                    valueAnimation: true,
                    fontSize: 24,
                    fontWeight: 'bold',
                    color: '#ffffff',
                    offsetCenter: [0, '20%'],
                },
                data: [{ value: score }],
            },
        ],
    };

    chart.setOption(option);
    return chart;
}

/**
 * Create a donut chart for category breakdown
 */
function createCategoryDonut(containerId, data) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const chart = echarts.init(container, 'azureDark');

    const option = {
        tooltip: {
            trigger: 'item',
            formatter: '{b}: {c} ({d}%)',
        },
        series: [
            {
                type: 'pie',
                radius: ['50%', '70%'],
                avoidLabelOverlap: false,
                label: { show: false },
                emphasis: {
                    label: {
                        show: true,
                        fontSize: 14,
                        fontWeight: 'bold',
                    },
                },
                labelLine: { show: false },
                data: data.map((item, i) => ({
                    value: item.value,
                    name: item.name,
                    itemStyle: { color: chartColors.series[i % chartColors.series.length] },
                })),
            },
        ],
    };

    chart.setOption(option);
    return chart;
}

// Export functions for use in app.js
window.initializeCharts = initializeCharts;
window.updateAllCharts = updateAllCharts;
window.updateResourceChart = updateResourceChart;
window.createScoreGauge = createScoreGauge;
window.createCategoryDonut = createCategoryDonut;
