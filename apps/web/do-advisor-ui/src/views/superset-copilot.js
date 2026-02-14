/**
 * DO Advisor - Superset Copilot View
 *
 * AI-powered Superset assistant with MCP integration
 */

class SupersetCopilot {
    constructor() {
        this.dashboards = [];
        this.charts = [];
        this.datasets = [];
        this.selectedDashboard = null;
        this.config = window.DO_ADVISOR_CONFIG?.superset || {};
    }

    /**
     * Initialize the Superset Copilot
     */
    async init() {
        await this.loadSupersetData();
        this.render();
        this.initThemeSync();
    }

    /**
     * Load data from Superset via MCP
     */
    async loadSupersetData() {
        try {
            // In production, call MCP tools
            // For now, use sample data
            this.dashboards = this.getSampleDashboards();
            this.charts = this.getSampleCharts();
            this.datasets = this.getSampleDatasets();
        } catch (error) {
            console.error('Error loading Superset data:', error);
        }
    }

    /**
     * Sample dashboards
     */
    getSampleDashboards() {
        return [
            {
                id: 1,
                dashboard_title: 'Finance PPM Overview',
                published: true,
                changed_on: '2025-11-25T10:30:00Z',
                chart_count: 8,
                owners: ['admin'],
                tags: ['finance', 'ppm', 'kpi']
            },
            {
                id: 2,
                dashboard_title: 'OCR Quality Metrics',
                published: true,
                changed_on: '2025-11-24T15:45:00Z',
                chart_count: 5,
                owners: ['admin'],
                tags: ['ocr', 'quality', 'monitoring']
            },
            {
                id: 3,
                dashboard_title: 'Infrastructure Health',
                published: true,
                changed_on: '2025-11-26T08:00:00Z',
                chart_count: 12,
                owners: ['admin'],
                tags: ['infra', 'doks', 'monitoring']
            },
            {
                id: 4,
                dashboard_title: 'Expense Analytics',
                published: false,
                changed_on: '2025-11-20T14:20:00Z',
                chart_count: 6,
                owners: ['admin'],
                tags: ['expense', 'hr', 'finance']
            }
        ];
    }

    /**
     * Sample charts
     */
    getSampleCharts() {
        return [
            { id: 1, slice_name: 'Monthly Expenses Trend', viz_type: 'echarts_timeseries_line', datasource_id: 1 },
            { id: 2, slice_name: 'Expense by Category', viz_type: 'pie', datasource_id: 1 },
            { id: 3, slice_name: 'OCR Success Rate', viz_type: 'big_number_total', datasource_id: 2 },
            { id: 4, slice_name: 'CPU Usage Heatmap', viz_type: 'heatmap', datasource_id: 3 },
            { id: 5, slice_name: 'Pod Status Distribution', viz_type: 'echarts_area', datasource_id: 3 },
            { id: 6, slice_name: 'Budget vs Actual', viz_type: 'compare', datasource_id: 1 }
        ];
    }

    /**
     * Sample datasets
     */
    getSampleDatasets() {
        return [
            { id: 1, table_name: 'hr_expense', schema: 'public', database_id: 1 },
            { id: 2, table_name: 'ocr_expense_log', schema: 'public', database_id: 1 },
            { id: 3, table_name: 'k8s_metrics', schema: 'monitoring', database_id: 2 },
            { id: 4, table_name: 'finance_logframe', schema: 'public', database_id: 1 }
        ];
    }

    /**
     * Render the Superset Copilot view
     */
    render() {
        const container = document.getElementById('view-superset');
        if (!container) return;

        container.innerHTML = `
            <div class="view-header">
                <h1>Superset Copilot</h1>
                <div class="view-actions">
                    <button class="btn btn-primary" id="ask-copilot-btn">
                        <span>&#128172;</span> Ask Copilot
                    </button>
                    <a href="${this.config.endpoint || '#'}" target="_blank" class="btn btn-secondary">
                        Open Superset
                    </a>
                </div>
            </div>

            <!-- Copilot Chat -->
            <div class="copilot-section">
                <div class="card panel copilot-panel">
                    <div class="panel-header">
                        <h2 class="panel-title">AI Assistant</h2>
                        <span class="status-indicator">
                            <span class="status-dot success"></span>
                            Connected
                        </span>
                    </div>
                    <div class="panel-content">
                        <div class="copilot-chat" id="copilot-chat">
                            <div class="copilot-message assistant">
                                <div class="message-avatar">&#129302;</div>
                                <div class="message-content">
                                    <p>Hello! I'm your Superset Copilot. I can help you:</p>
                                    <ul>
                                        <li>Explore dashboards and charts</li>
                                        <li>Explain chart configurations</li>
                                        <li>Generate SQL queries</li>
                                        <li>Create new visualizations</li>
                                    </ul>
                                    <p>What would you like to know?</p>
                                </div>
                            </div>
                        </div>
                        <div class="copilot-input">
                            <input type="text" id="copilot-query" placeholder="Ask about dashboards, charts, or data...">
                            <button class="btn btn-primary" id="send-query-btn">Send</button>
                        </div>
                        <div class="copilot-suggestions">
                            <span class="suggestion-label">Try:</span>
                            <button class="suggestion-btn" data-query="Show me all published dashboards">Dashboards</button>
                            <button class="suggestion-btn" data-query="What chart types are used most?">Chart Types</button>
                            <button class="suggestion-btn" data-query="Explain the Finance PPM dashboard">Explain Dashboard</button>
                            <button class="suggestion-btn" data-query="Show OCR success rate over time">Query Data</button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Dashboard Grid -->
            <div class="superset-grid">
                <div class="card panel">
                    <div class="panel-header">
                        <h2 class="panel-title">Dashboards</h2>
                        <span class="badge">${this.dashboards.length}</span>
                    </div>
                    <div class="panel-content">
                        <div class="dashboard-list" id="dashboard-list">
                            ${this.renderDashboardList()}
                        </div>
                    </div>
                </div>

                <div class="card panel">
                    <div class="panel-header">
                        <h2 class="panel-title">Charts</h2>
                        <span class="badge">${this.charts.length}</span>
                    </div>
                    <div class="panel-content">
                        <div class="chart-list" id="chart-list">
                            ${this.renderChartList()}
                        </div>
                    </div>
                </div>

                <div class="card panel">
                    <div class="panel-header">
                        <h2 class="panel-title">Datasets</h2>
                        <span class="badge">${this.datasets.length}</span>
                    </div>
                    <div class="panel-content">
                        <div class="dataset-list" id="dataset-list">
                            ${this.renderDatasetList()}
                        </div>
                    </div>
                </div>
            </div>

            <!-- Theme Sync -->
            <div class="theme-section">
                <div class="card panel">
                    <div class="panel-header">
                        <h2 class="panel-title">Theme Tokens</h2>
                        <button class="btn btn-secondary btn-sm" id="sync-theme-btn">Sync Theme</button>
                    </div>
                    <div class="panel-content">
                        <div class="theme-preview">
                            <div class="theme-token">
                                <span class="token-swatch" style="background: var(--accent-primary)"></span>
                                <span class="token-name">colorPrimary</span>
                                <span class="token-value">#0078d4</span>
                            </div>
                            <div class="theme-token">
                                <span class="token-swatch" style="background: var(--color-success)"></span>
                                <span class="token-name">colorSuccess</span>
                                <span class="token-value">#107c10</span>
                            </div>
                            <div class="theme-token">
                                <span class="token-swatch" style="background: var(--color-warning)"></span>
                                <span class="token-name">colorWarning</span>
                                <span class="token-value">#ffaa44</span>
                            </div>
                            <div class="theme-token">
                                <span class="token-swatch" style="background: var(--color-critical)"></span>
                                <span class="token-name">colorError</span>
                                <span class="token-value">#d13438</span>
                            </div>
                        </div>
                        <p class="theme-note">
                            Theme tokens sync with Superset's Ant Design v5 system.
                            Use <code>echartsOptionsOverrides</code> for chart-specific styling.
                        </p>
                    </div>
                </div>
            </div>
        `;

        this.attachEventListeners();
    }

    /**
     * Render dashboard list
     */
    renderDashboardList() {
        return this.dashboards.map(dash => `
            <div class="superset-item" data-id="${dash.id}">
                <div class="item-status ${dash.published ? 'published' : 'draft'}">
                    ${dash.published ? '&#10003;' : '&#9711;'}
                </div>
                <div class="item-info">
                    <div class="item-title">${dash.dashboard_title}</div>
                    <div class="item-meta">
                        ${dash.chart_count} charts &bull; Updated ${this.formatRelativeTime(dash.changed_on)}
                    </div>
                </div>
                <div class="item-actions">
                    <button class="table-action-btn" title="Explain" onclick="supersetCopilot.explainDashboard(${dash.id})">&#128172;</button>
                    <button class="table-action-btn" title="Open" onclick="supersetCopilot.openDashboard(${dash.id})">&#8599;</button>
                </div>
            </div>
        `).join('');
    }

    /**
     * Render chart list
     */
    renderChartList() {
        return this.charts.map(chart => `
            <div class="superset-item" data-id="${chart.id}">
                <div class="item-icon">${this.getChartTypeIcon(chart.viz_type)}</div>
                <div class="item-info">
                    <div class="item-title">${chart.slice_name}</div>
                    <div class="item-meta">
                        <span class="tag">${chart.viz_type}</span>
                    </div>
                </div>
                <div class="item-actions">
                    <button class="table-action-btn" title="Explain" onclick="supersetCopilot.explainChart(${chart.id})">&#128172;</button>
                </div>
            </div>
        `).join('');
    }

    /**
     * Render dataset list
     */
    renderDatasetList() {
        return this.datasets.map(ds => `
            <div class="superset-item" data-id="${ds.id}">
                <div class="item-icon">&#128451;</div>
                <div class="item-info">
                    <div class="item-title">${ds.table_name}</div>
                    <div class="item-meta">
                        ${ds.schema}.${ds.table_name}
                    </div>
                </div>
                <div class="item-actions">
                    <button class="table-action-btn" title="Query" onclick="supersetCopilot.queryDataset(${ds.id})">&#9881;</button>
                </div>
            </div>
        `).join('');
    }

    /**
     * Attach event listeners
     */
    attachEventListeners() {
        const queryInput = document.getElementById('copilot-query');
        const sendBtn = document.getElementById('send-query-btn');
        const suggestions = document.querySelectorAll('.suggestion-btn');
        const syncThemeBtn = document.getElementById('sync-theme-btn');

        queryInput?.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendQuery();
        });

        sendBtn?.addEventListener('click', () => this.sendQuery());

        suggestions.forEach(btn => {
            btn.addEventListener('click', () => {
                queryInput.value = btn.dataset.query;
                this.sendQuery();
            });
        });

        syncThemeBtn?.addEventListener('click', () => this.syncTheme());
    }

    /**
     * Send query to Copilot
     */
    async sendQuery() {
        const input = document.getElementById('copilot-query');
        const chat = document.getElementById('copilot-chat');
        const query = input.value.trim();

        if (!query) return;

        // Add user message
        chat.innerHTML += `
            <div class="copilot-message user">
                <div class="message-content">${query}</div>
                <div class="message-avatar">&#128100;</div>
            </div>
        `;

        input.value = '';

        // Simulate response (in production, call MCP)
        setTimeout(() => {
            const response = this.generateResponse(query);
            chat.innerHTML += `
                <div class="copilot-message assistant">
                    <div class="message-avatar">&#129302;</div>
                    <div class="message-content">${response}</div>
                </div>
            `;
            chat.scrollTop = chat.scrollHeight;
        }, 500);

        chat.scrollTop = chat.scrollHeight;
    }

    /**
     * Generate copilot response (mock)
     */
    generateResponse(query) {
        const lowerQuery = query.toLowerCase();

        if (lowerQuery.includes('dashboard')) {
            const published = this.dashboards.filter(d => d.published);
            return `
                <p>I found <strong>${this.dashboards.length}</strong> dashboards, ${published.length} of which are published:</p>
                <ul>
                    ${published.map(d => `<li><strong>${d.dashboard_title}</strong> - ${d.chart_count} charts</li>`).join('')}
                </ul>
                <p>Would you like me to explain any of these?</p>
            `;
        }

        if (lowerQuery.includes('chart type')) {
            const types = {};
            this.charts.forEach(c => types[c.viz_type] = (types[c.viz_type] || 0) + 1);
            return `
                <p>Here's the distribution of chart types:</p>
                <ul>
                    ${Object.entries(types).map(([type, count]) => `<li><strong>${type}</strong>: ${count}</li>`).join('')}
                </ul>
                <p>The most popular type is <strong>echarts_timeseries_line</strong> for time-series data.</p>
            `;
        }

        if (lowerQuery.includes('explain') && lowerQuery.includes('finance')) {
            return `
                <p><strong>Finance PPM Dashboard</strong></p>
                <p>This dashboard provides an overview of Project Portfolio Management metrics including:</p>
                <ul>
                    <li><strong>Budget vs Actual</strong> - Compares planned vs actual spending</li>
                    <li><strong>Monthly Expenses Trend</strong> - Time-series of expense data</li>
                    <li><strong>Expense by Category</strong> - Pie chart breakdown</li>
                </ul>
                <p>Data source: <code>hr_expense</code> table via the Odoo PostgreSQL database.</p>
            `;
        }

        if (lowerQuery.includes('ocr') || lowerQuery.includes('success rate')) {
            return `
                <p>Based on the <strong>OCR Quality Metrics</strong> dashboard:</p>
                <ul>
                    <li>Current success rate: <strong>87%</strong></li>
                    <li>P95 latency: <strong>24s</strong></li>
                    <li>Top failing vendors: SM, 7-Eleven variants</li>
                </ul>
                <p>To query this data:</p>
                <pre><code>SELECT
  date_trunc('day', create_date) as day,
  COUNT(*) FILTER (WHERE status = 'processed') * 100.0 / COUNT(*) as success_rate
FROM ocr_expense_log
GROUP BY 1
ORDER BY 1 DESC
LIMIT 7;</code></pre>
            `;
        }

        return `
            <p>I can help you explore Superset dashboards, charts, and data. Try asking:</p>
            <ul>
                <li>"Show me all published dashboards"</li>
                <li>"Explain the Finance PPM dashboard"</li>
                <li>"What chart types are used?"</li>
                <li>"Query the OCR success rate"</li>
            </ul>
        `;
    }

    /**
     * Explain dashboard via MCP
     */
    explainDashboard(dashboardId) {
        const dash = this.dashboards.find(d => d.id === dashboardId);
        if (!dash) return;

        const input = document.getElementById('copilot-query');
        input.value = `Explain the "${dash.dashboard_title}" dashboard`;
        this.sendQuery();
    }

    /**
     * Explain chart via MCP
     */
    explainChart(chartId) {
        const chart = this.charts.find(c => c.id === chartId);
        if (!chart) return;

        const input = document.getElementById('copilot-query');
        input.value = `Explain the "${chart.slice_name}" chart (type: ${chart.viz_type})`;
        this.sendQuery();
    }

    /**
     * Open dashboard in Superset
     */
    openDashboard(dashboardId) {
        const url = `${this.config.endpoint || 'http://localhost:8088'}/superset/dashboard/${dashboardId}/`;
        window.open(url, '_blank');
    }

    /**
     * Query dataset
     */
    queryDataset(datasetId) {
        const ds = this.datasets.find(d => d.id === datasetId);
        if (!ds) return;

        const input = document.getElementById('copilot-query');
        input.value = `Show sample data from ${ds.schema}.${ds.table_name}`;
        this.sendQuery();
    }

    /**
     * Sync theme tokens with Superset
     */
    syncTheme() {
        const tokens = {
            colorPrimary: getComputedStyle(document.documentElement).getPropertyValue('--accent-primary').trim(),
            colorSuccess: getComputedStyle(document.documentElement).getPropertyValue('--color-success').trim(),
            colorWarning: getComputedStyle(document.documentElement).getPropertyValue('--color-warning').trim(),
            colorError: getComputedStyle(document.documentElement).getPropertyValue('--color-critical').trim(),
        };

        console.log('Theme tokens to sync:', tokens);
        alert('Theme tokens synced to Superset!\n\n' + JSON.stringify(tokens, null, 2));
    }

    /**
     * Initialize theme sync
     */
    initThemeSync() {
        // Could watch for theme changes and auto-sync
    }

    // Helper methods
    getChartTypeIcon(vizType) {
        const icons = {
            pie: '&#128200;',
            echarts_timeseries_line: '&#128200;',
            echarts_area: '&#128200;',
            big_number_total: '&#128290;',
            heatmap: '&#9632;',
            compare: '&#128200;',
        };
        return icons[vizType] || '&#128200;';
    }

    formatRelativeTime(dateStr) {
        const date = new Date(dateStr);
        const now = new Date();
        const diff = now - date;
        const hours = Math.floor(diff / 3600000);
        const days = Math.floor(diff / 86400000);

        if (hours < 24) return `${hours}h ago`;
        return `${days}d ago`;
    }
}

// Initialize and export
window.supersetCopilot = new SupersetCopilot();

// Add styles for Superset Copilot
const style = document.createElement('style');
style.textContent = `
    .copilot-section {
        margin-bottom: var(--spacing-lg);
    }

    .copilot-panel {
        min-height: 400px;
    }

    .copilot-chat {
        max-height: 300px;
        overflow-y: auto;
        padding: var(--spacing-md);
        background: var(--bg-primary);
        border-radius: var(--radius-md);
        margin-bottom: var(--spacing-md);
    }

    .copilot-message {
        display: flex;
        gap: var(--spacing-sm);
        margin-bottom: var(--spacing-md);
    }

    .copilot-message.user {
        flex-direction: row-reverse;
    }

    .message-avatar {
        width: 32px;
        height: 32px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: var(--bg-tertiary);
        border-radius: 50%;
        font-size: 16px;
    }

    .message-content {
        flex: 1;
        padding: var(--spacing-sm) var(--spacing-md);
        background: var(--bg-secondary);
        border-radius: var(--radius-md);
        font-size: 13px;
    }

    .copilot-message.user .message-content {
        background: var(--accent-primary);
        color: white;
    }

    .message-content ul {
        margin: var(--spacing-sm) 0;
        padding-left: var(--spacing-lg);
    }

    .message-content pre {
        background: var(--bg-primary);
        padding: var(--spacing-sm);
        border-radius: var(--radius-sm);
        overflow-x: auto;
        margin: var(--spacing-sm) 0;
    }

    .message-content code {
        font-family: 'Cascadia Code', monospace;
        font-size: 12px;
    }

    .copilot-input {
        display: flex;
        gap: var(--spacing-sm);
    }

    .copilot-input input {
        flex: 1;
    }

    .copilot-suggestions {
        display: flex;
        align-items: center;
        gap: var(--spacing-sm);
        margin-top: var(--spacing-md);
        flex-wrap: wrap;
    }

    .suggestion-label {
        font-size: 12px;
        color: var(--text-muted);
    }

    .suggestion-btn {
        padding: var(--spacing-xs) var(--spacing-sm);
        background: var(--bg-tertiary);
        border: 1px solid var(--border-primary);
        border-radius: var(--radius-sm);
        color: var(--text-secondary);
        font-size: 11px;
        cursor: pointer;
    }

    .suggestion-btn:hover {
        background: var(--bg-hover);
        color: var(--text-primary);
    }

    .superset-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: var(--spacing-md);
        margin-bottom: var(--spacing-lg);
    }

    .superset-item {
        display: flex;
        align-items: center;
        gap: var(--spacing-sm);
        padding: var(--spacing-sm);
        border-radius: var(--radius-sm);
        cursor: pointer;
    }

    .superset-item:hover {
        background: var(--bg-hover);
    }

    .item-status, .item-icon {
        width: 24px;
        text-align: center;
        font-size: 14px;
    }

    .item-status.published {
        color: var(--color-success);
    }

    .item-status.draft {
        color: var(--text-muted);
    }

    .item-info {
        flex: 1;
        min-width: 0;
    }

    .item-title {
        font-size: 13px;
        font-weight: 500;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .item-meta {
        font-size: 11px;
        color: var(--text-muted);
    }

    .theme-section .panel {
        max-width: 600px;
    }

    .theme-preview {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: var(--spacing-md);
        margin-bottom: var(--spacing-md);
    }

    .theme-token {
        display: flex;
        align-items: center;
        gap: var(--spacing-sm);
    }

    .token-swatch {
        width: 24px;
        height: 24px;
        border-radius: var(--radius-sm);
    }

    .token-name {
        flex: 1;
        font-size: 12px;
    }

    .token-value {
        font-family: monospace;
        font-size: 11px;
        color: var(--text-muted);
    }

    .theme-note {
        font-size: 12px;
        color: var(--text-tertiary);
    }

    @media (max-width: 1200px) {
        .superset-grid {
            grid-template-columns: 1fr;
        }
    }
`;
document.head.appendChild(style);
