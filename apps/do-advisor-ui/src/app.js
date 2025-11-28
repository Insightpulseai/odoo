/**
 * DO Advisor - Main Application
 *
 * Azure Advisor-style dashboard for DigitalOcean + Self-Hosted Stack
 */

class DOAdvisorApp {
    constructor() {
        this.config = window.DO_ADVISOR_CONFIG;
        this.currentView = 'dashboard';
        this.data = {
            recommendations: [],
            jobs: [],
            metrics: {},
            infrastructure: [],
        };

        this.init();
    }

    async init() {
        this.setupNavigation();
        this.setupEventListeners();
        this.initCharts();

        // Load initial data
        await this.loadAllData();

        // Start refresh intervals
        this.startRefreshCycles();

        // Update timestamp
        this.updateLastUpdated();
    }

    setupNavigation() {
        const navItems = document.querySelectorAll('.nav-item');
        const panelLinks = document.querySelectorAll('.panel-link');

        navItems.forEach(item => {
            item.addEventListener('click', () => {
                const view = item.dataset.view;
                this.switchView(view);

                // Update active state
                navItems.forEach(i => i.classList.remove('active'));
                item.classList.add('active');
            });
        });

        panelLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const view = link.dataset.view;
                this.switchView(view);

                // Update nav active state
                navItems.forEach(i => {
                    i.classList.toggle('active', i.dataset.view === view);
                });
            });
        });
    }

    switchView(viewName) {
        const views = document.querySelectorAll('.view');
        views.forEach(view => {
            view.classList.toggle('active', view.id === `view-${viewName}`);
        });
        this.currentView = viewName;

        // Update breadcrumb
        const current = document.querySelector('.breadcrumb .current');
        current.textContent = viewName.charAt(0).toUpperCase() + viewName.slice(1);
    }

    setupEventListeners() {
        // Menu toggle (mobile)
        const menuToggle = document.getElementById('menu-toggle');
        const sidebar = document.getElementById('sidebar');
        menuToggle?.addEventListener('click', () => {
            sidebar.classList.toggle('open');
        });

        // Refresh button
        const refreshBtn = document.getElementById('refresh-btn');
        refreshBtn?.addEventListener('click', () => this.loadAllData());

        // Job tabs
        const tabBtns = document.querySelectorAll('.tab-btn');
        tabBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                tabBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                this.filterJobs(btn.dataset.tab);
            });
        });

        // Filters
        const recCategoryFilter = document.getElementById('rec-category-filter');
        const recImpactFilter = document.getElementById('rec-impact-filter');
        recCategoryFilter?.addEventListener('change', () => this.filterRecommendations());
        recImpactFilter?.addEventListener('change', () => this.filterRecommendations());

        // Time range for charts
        const resourceTimeRange = document.getElementById('resource-time-range');
        resourceTimeRange?.addEventListener('change', () => this.updateResourceChart());
    }

    async loadAllData() {
        try {
            await Promise.all([
                this.loadRecommendations(),
                this.loadJobs(),
                this.loadMetrics(),
                this.loadInfrastructure(),
            ]);
            this.updateLastUpdated();
        } catch (error) {
            console.error('Error loading data:', error);
        }
    }

    async loadRecommendations() {
        // Sample data - replace with actual API call
        this.data.recommendations = [
            {
                id: 1,
                category: 'cost',
                severity: 'medium',
                title: 'Idle Droplet detected',
                resource: 'droplet-staging-02',
                impact: 'Save $20/month',
                description: 'This droplet has averaged less than 5% CPU usage over the past 7 days.',
            },
            {
                id: 2,
                category: 'security',
                severity: 'critical',
                title: 'SSL certificate expiring',
                resource: 'api.insightpulseai.net',
                impact: 'Expires in 14 days',
                description: 'SSL certificate will expire soon. Renew to avoid service disruption.',
            },
            {
                id: 3,
                category: 'reliability',
                severity: 'high',
                title: 'Single node DOKS cluster',
                resource: 'k8s-fin-workspace',
                impact: 'No HA protection',
                description: 'Cluster has only one worker node. Add nodes for high availability.',
            },
            {
                id: 4,
                category: 'performance',
                severity: 'medium',
                title: 'High latency endpoint',
                resource: '/api/v1/reports',
                impact: 'P95 > 2s',
                description: 'This endpoint consistently exceeds latency SLO.',
            },
            {
                id: 5,
                category: 'operational',
                severity: 'low',
                title: 'Unused Volume',
                resource: 'vol-backup-old',
                impact: 'Save $10/month',
                description: 'This volume has not been attached to any Droplet in 30 days.',
            },
        ];

        this.renderRecommendations();
        this.updateSummaryCounts();
    }

    async loadJobs() {
        // Sample data - replace with n8n API, Odoo cron, etc.
        this.data.jobs = [
            {
                id: 'W001',
                name: 'W001_MONTHLY_CLOSE',
                source: 'n8n',
                status: 'running',
                schedule: '0 0 1 * *',
                lastRun: new Date(Date.now() - 5 * 60000),
                duration: '5m 23s',
                progress: 60,
            },
            {
                id: 'W002',
                name: 'W002_DAILY_BACKUP',
                source: 'n8n',
                status: 'scheduled',
                schedule: '0 2 * * *',
                lastRun: new Date(Date.now() - 22 * 3600000),
                duration: '12m 45s',
            },
            {
                id: 'W003',
                name: 'W003_OCR_SYNC',
                source: 'n8n',
                status: 'stale',
                schedule: '*/30 * * * *',
                lastRun: new Date(Date.now() - 3 * 86400000),
                duration: '2m 10s',
            },
            {
                id: 'C001',
                name: 'ir_cron_cleanup',
                source: 'odoo',
                status: 'scheduled',
                schedule: '0 3 * * *',
                lastRun: new Date(Date.now() - 21 * 3600000),
                duration: '45s',
            },
            {
                id: 'W004',
                name: 'W004_EMAIL_DIGEST',
                source: 'n8n',
                status: 'failed',
                schedule: '0 8 * * *',
                lastRun: new Date(Date.now() - 2 * 3600000),
                duration: '1m 02s',
                error: 'SMTP connection timeout',
            },
            {
                id: 'S001',
                name: 'superset_refresh_dashboard',
                source: 'superset',
                status: 'success',
                schedule: '0 */6 * * *',
                lastRun: new Date(Date.now() - 30 * 60000),
                duration: '3m 15s',
            },
        ];

        this.renderJobs();
        this.updateJobCounts();
    }

    async loadMetrics() {
        // Generate sample metrics data
        const now = Date.now();
        const points = 24;
        const interval = 3600000; // 1 hour

        this.data.metrics = {
            resourceUsage: Array.from({ length: points }, (_, i) => ({
                time: new Date(now - (points - i) * interval),
                cpu: 30 + Math.random() * 40,
                memory: 50 + Math.random() * 30,
                network: 10 + Math.random() * 20,
            })),
            costTrend: Array.from({ length: 12 }, (_, i) => ({
                month: new Date(now - (11 - i) * 30 * 86400000).toLocaleDateString('en', { month: 'short' }),
                cost: 100 + Math.random() * 50,
            })),
            jobSuccess: Array.from({ length: 7 }, (_, i) => ({
                day: new Date(now - (6 - i) * 86400000).toLocaleDateString('en', { weekday: 'short' }),
                success: Math.floor(80 + Math.random() * 20),
                failed: Math.floor(Math.random() * 10),
                skipped: Math.floor(Math.random() * 5),
            })),
        };

        this.updateCharts();
    }

    async loadInfrastructure() {
        // Sample infrastructure data
        this.data.infrastructure = [
            { name: 'DOKS Cluster', type: 'kubernetes', status: 'Running', health: 'healthy' },
            { name: 'Odoo Droplet', type: 'droplet', status: '3 vCPU / 4GB', health: 'healthy' },
            { name: 'PostgreSQL', type: 'database', status: 'Primary', health: 'healthy' },
            { name: 'n8n', type: 'app', status: 'Active', health: 'healthy' },
            { name: 'Mattermost', type: 'app', status: 'Active', health: 'healthy' },
            { name: 'Superset', type: 'app', status: 'Active', health: 'warning' },
        ];

        this.renderInfrastructure();
    }

    renderRecommendations() {
        const list = document.getElementById('recommendations-list');
        const fullList = document.getElementById('recommendations-full-list');

        // Dashboard list (top 5)
        if (list) {
            list.innerHTML = this.data.recommendations.slice(0, 5).map(rec => `
                <div class="recommendation-item" data-id="${rec.id}">
                    <div class="recommendation-severity ${rec.severity}"></div>
                    <div class="recommendation-content">
                        <span class="recommendation-category">${rec.category}</span>
                        <div class="recommendation-title">${rec.title}</div>
                        <div class="recommendation-resource">${rec.resource}</div>
                    </div>
                    <div class="recommendation-impact">${rec.impact}</div>
                </div>
            `).join('');
        }

        // Full list
        if (fullList) {
            fullList.innerHTML = this.data.recommendations.map(rec => `
                <div class="recommendation-card" data-id="${rec.id}">
                    <div class="recommendation-card-header">
                        <div class="recommendation-card-icon ${rec.category}">
                            ${this.getCategoryIcon(rec.category)}
                        </div>
                        <div class="recommendation-card-info">
                            <div class="recommendation-card-title">${rec.title}</div>
                            <div class="recommendation-card-meta">
                                <span class="tag">${rec.category}</span>
                                <span>${rec.resource}</span>
                            </div>
                        </div>
                        <div class="recommendation-severity-badge ${rec.severity}">
                            ${rec.severity.toUpperCase()}
                        </div>
                    </div>
                    <div class="recommendation-card-body">
                        <div class="recommendation-description">${rec.description}</div>
                        <div class="recommendation-details">
                            <div class="detail-item">
                                <span class="detail-label">Impact</span>
                                <span class="detail-value">${rec.impact}</span>
                            </div>
                            <div class="detail-item">
                                <span class="detail-label">Effort</span>
                                <span class="detail-value">Quick Win</span>
                            </div>
                            <div class="detail-item">
                                <span class="detail-label">Category</span>
                                <span class="detail-value">${rec.category}</span>
                            </div>
                        </div>
                        <div class="recommendation-actions">
                            <button class="btn btn-primary">Apply Fix</button>
                            <button class="btn btn-secondary">View Details</button>
                            <button class="btn btn-secondary">Dismiss</button>
                        </div>
                    </div>
                </div>
            `).join('');
        }
    }

    renderJobs(filter = 'running') {
        const list = document.getElementById('jobs-list');
        const tbody = document.getElementById('jobs-table-body');

        const filteredJobs = filter === 'all'
            ? this.data.jobs
            : this.data.jobs.filter(job => job.status === filter);

        // Dashboard list
        if (list) {
            list.innerHTML = filteredJobs.slice(0, 8).map(job => `
                <div class="job-item" data-id="${job.id}">
                    <div class="job-status ${job.status}"></div>
                    <div class="job-info">
                        <div class="job-name">${job.name}</div>
                        <div class="job-source">
                            <span class="tag ${job.source}">${job.source}</span>
                        </div>
                    </div>
                    <div class="job-time">
                        ${this.formatRelativeTime(job.lastRun)}
                        <div class="job-duration">${job.duration}</div>
                    </div>
                </div>
            `).join('') || '<div class="empty-state"><span>No jobs in this status</span></div>';
        }

        // Full table
        if (tbody) {
            tbody.innerHTML = this.data.jobs.map(job => `
                <tr data-id="${job.id}">
                    <td>
                        <span class="status-indicator">
                            <span class="status-dot ${job.status}"></span>
                            ${job.status}
                        </span>
                    </td>
                    <td><strong>${job.name}</strong></td>
                    <td><span class="tag ${job.source}">${job.source}</span></td>
                    <td><code>${job.schedule}</code></td>
                    <td>${this.formatRelativeTime(job.lastRun)}</td>
                    <td>${job.duration}</td>
                    <td>
                        <div class="table-actions">
                            <button class="table-action-btn" title="Run Now">▶</button>
                            <button class="table-action-btn" title="View Logs">📋</button>
                            <button class="table-action-btn danger" title="Disable">⏸</button>
                        </div>
                    </td>
                </tr>
            `).join('');
        }
    }

    renderInfrastructure() {
        const grid = document.getElementById('infra-status');
        if (!grid) return;

        grid.innerHTML = this.data.infrastructure.map(item => `
            <div class="infra-item">
                <div class="infra-icon">${this.getInfraIcon(item.type)}</div>
                <div class="infra-details">
                    <div class="infra-name">${item.name}</div>
                    <div class="infra-status">${item.status}</div>
                </div>
                <div class="infra-health ${item.health}"></div>
            </div>
        `).join('');
    }

    filterJobs(status) {
        this.renderJobs(status);
    }

    filterRecommendations() {
        const category = document.getElementById('rec-category-filter')?.value || 'all';
        const impact = document.getElementById('rec-impact-filter')?.value || 'all';

        let filtered = [...this.data.recommendations];

        if (category !== 'all') {
            filtered = filtered.filter(r => r.category === category);
        }

        if (impact !== 'all') {
            filtered = filtered.filter(r => r.severity === impact);
        }

        // Re-render with filtered data
        const fullList = document.getElementById('recommendations-full-list');
        if (fullList) {
            // Update rendering logic here
        }
    }

    updateSummaryCounts() {
        const recs = this.data.recommendations;
        document.getElementById('critical-count').textContent =
            recs.filter(r => r.severity === 'critical').length;
        document.getElementById('warning-count').textContent =
            recs.filter(r => r.severity === 'high' || r.severity === 'medium').length;
        document.getElementById('healthy-count').textContent =
            this.data.infrastructure.filter(i => i.health === 'healthy').length;

        // Calculate score (0-100)
        const criticalPenalty = recs.filter(r => r.severity === 'critical').length * 15;
        const highPenalty = recs.filter(r => r.severity === 'high').length * 8;
        const mediumPenalty = recs.filter(r => r.severity === 'medium').length * 3;
        const score = Math.max(0, 100 - criticalPenalty - highPenalty - mediumPenalty);

        document.getElementById('score-value').textContent = score;
        document.getElementById('advisor-score').textContent = score;
    }

    updateJobCounts() {
        const jobs = this.data.jobs;
        document.getElementById('jobs-running').textContent =
            jobs.filter(j => j.status === 'running').length;
        document.getElementById('jobs-scheduled').textContent =
            jobs.filter(j => j.status === 'scheduled').length;
        document.getElementById('jobs-stale').textContent =
            jobs.filter(j => j.status === 'stale').length;
        document.getElementById('jobs-failed').textContent =
            jobs.filter(j => j.status === 'failed').length;
    }

    updateLastUpdated() {
        const el = document.getElementById('last-updated-time');
        if (el) {
            el.textContent = new Date().toLocaleTimeString();
        }
    }

    // Chart initialization and updates handled by metrics-charts.js

    initCharts() {
        if (typeof initializeCharts === 'function') {
            initializeCharts(this.config.chartColors);
        }
    }

    updateCharts() {
        if (typeof updateAllCharts === 'function') {
            updateAllCharts(this.data.metrics);
        }
    }

    updateResourceChart() {
        const range = document.getElementById('resource-time-range')?.value || '24h';
        // Filter data based on range and update chart
        if (typeof updateResourceChart === 'function') {
            updateResourceChart(this.data.metrics.resourceUsage, range);
        }
    }

    startRefreshCycles() {
        const { intervals } = this.config;

        setInterval(() => this.loadRecommendations(), intervals.recommendations);
        setInterval(() => this.loadJobs(), intervals.jobs);
        setInterval(() => this.loadMetrics(), intervals.metrics);
        setInterval(() => this.loadInfrastructure(), intervals.infrastructure);
    }

    // Utility methods
    getCategoryIcon(category) {
        const icons = {
            cost: '$',
            security: '🔒',
            reliability: '🛡',
            performance: '⚡',
            operational: '⚙',
        };
        return icons[category] || '•';
    }

    getInfraIcon(type) {
        const icons = {
            kubernetes: '☸',
            droplet: '💧',
            database: '🗄',
            app: '📦',
        };
        return icons[type] || '•';
    }

    formatRelativeTime(date) {
        const now = Date.now();
        const diff = now - date.getTime();
        const minutes = Math.floor(diff / 60000);
        const hours = Math.floor(diff / 3600000);
        const days = Math.floor(diff / 86400000);

        if (minutes < 60) return `${minutes}m ago`;
        if (hours < 24) return `${hours}h ago`;
        return `${days}d ago`;
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.doAdvisor = new DOAdvisorApp();
});
