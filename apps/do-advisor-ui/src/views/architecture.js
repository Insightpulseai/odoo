/**
 * DO Advisor - Architecture Diagrams View
 *
 * Azure-style architecture diagram browser with draw.io integration
 */

class ArchitectureView {
    constructor() {
        this.diagrams = [];
        this.manifestUrl = '/docs/diagrams/architecture/manifest.json';
        this.githubConfig = {
            org: 'jgtolentino',
            repo: 'odoo-ce',
            branch: 'main',
            basePath: 'docs/diagrams/architecture'
        };
    }

    /**
     * Initialize the architecture view
     */
    async init() {
        await this.loadManifest();
        this.render();
        this.initCharts();
    }

    /**
     * Load diagram manifest
     */
    async loadManifest() {
        try {
            // In production, fetch from actual manifest
            // For now, use embedded sample data
            this.diagrams = this.getSampleDiagrams();
        } catch (error) {
            console.error('Error loading manifest:', error);
            this.diagrams = this.getSampleDiagrams();
        }
    }

    /**
     * Sample diagrams for demo
     */
    getSampleDiagrams() {
        return [
            {
                id: 'fin-workspace-overview',
                title: 'fin-workspace Platform Overview',
                description: 'High-level architecture including DO Advisor, n8n, Superset, Odoo',
                providers: ['digitalocean', 'generic'],
                source: 'manual',
                file_drawio: 'fin-workspace-overview.drawio',
                file_image: 'previews/fin-workspace-overview.png',
                last_updated: '2025-11-26T00:00:00Z',
                tags: ['overview', 'platform', 'do-advisor'],
                components: { count: 12, types: ['droplet', 'kubernetes', 'database', 'app'] }
            },
            {
                id: 'do-advisor-architecture',
                title: 'DO Advisor Agent Architecture',
                description: 'Internal architecture of the unified agent and UI',
                providers: ['digitalocean', 'generic'],
                source: 'manual',
                file_drawio: 'do-advisor-architecture.drawio',
                file_image: 'previews/do-advisor-architecture.png',
                last_updated: '2025-11-26T00:00:00Z',
                tags: ['do-advisor', 'agent', 'mcp'],
                components: { count: 8, types: ['agent', 'ui', 'mcp', 'api'] }
            },
            {
                id: 'azure-fin-workspace',
                title: 'Azure Integration Architecture',
                description: 'Azure services integration with fin-workspace',
                providers: ['azure'],
                source: 'azure-resource-graph',
                file_drawio: 'azure-fin-workspace.drawio',
                file_image: 'previews/azure-fin-workspace.png',
                last_updated: '2025-11-25T00:00:00Z',
                tags: ['azure', 'hybrid', 'integration'],
                components: { count: 15, types: ['vm', 'storage', 'network', 'function'] }
            },
            {
                id: 'k8s-doks-cluster',
                title: 'DOKS Kubernetes Cluster',
                description: 'DigitalOcean Kubernetes cluster topology',
                providers: ['kubernetes', 'digitalocean'],
                source: 'kubectl',
                file_drawio: 'k8s-doks-cluster.drawio',
                file_image: 'previews/k8s-doks-cluster.png',
                last_updated: '2025-11-24T00:00:00Z',
                tags: ['kubernetes', 'doks', 'containers'],
                components: { count: 20, types: ['pod', 'service', 'ingress', 'node'] }
            }
        ];
    }

    /**
     * Render the architecture view
     */
    render() {
        const container = document.getElementById('view-architecture');
        if (!container) return;

        container.innerHTML = `
            <div class="view-header">
                <h1>Architecture Diagrams</h1>
                <div class="view-actions">
                    <button class="btn btn-primary" id="generate-diagram-btn">
                        <span>&#43;</span> Generate Diagram
                    </button>
                    <button class="btn btn-secondary" id="refresh-diagrams-btn">
                        <span>&#8635;</span> Refresh
                    </button>
                </div>
            </div>

            <!-- Summary Cards -->
            <div class="arch-summary-cards">
                <div class="mini-card">
                    <span class="mini-value">${this.diagrams.length}</span>
                    <span class="mini-label">Total Diagrams</span>
                </div>
                <div class="mini-card">
                    <span class="mini-value">${this.getUniqueProviders().length}</span>
                    <span class="mini-label">Providers</span>
                </div>
                <div class="mini-card">
                    <span class="mini-value">${this.getTotalComponents()}</span>
                    <span class="mini-label">Components</span>
                </div>
                <div class="mini-card">
                    <span class="mini-value">${this.getRecentCount()}</span>
                    <span class="mini-label">Updated (7d)</span>
                </div>
            </div>

            <!-- Provider Filter -->
            <div class="arch-filters">
                <div class="filter-group">
                    <label>Provider:</label>
                    <select id="provider-filter" class="filter-select">
                        <option value="all">All Providers</option>
                        ${this.getUniqueProviders().map(p => `<option value="${p}">${this.formatProvider(p)}</option>`).join('')}
                    </select>
                </div>
                <div class="filter-group">
                    <label>Source:</label>
                    <select id="source-filter" class="filter-select">
                        <option value="all">All Sources</option>
                        <option value="manual">Manual</option>
                        <option value="azure-resource-graph">Azure Resource Graph</option>
                        <option value="kubectl">Kubernetes</option>
                        <option value="doctl">DigitalOcean CLI</option>
                    </select>
                </div>
            </div>

            <!-- Diagrams Grid -->
            <div class="arch-grid" id="diagrams-grid">
                ${this.renderDiagramCards()}
            </div>

            <!-- Provider Stats Chart -->
            <div class="arch-stats">
                <div class="card panel chart-panel">
                    <div class="panel-header">
                        <h2 class="panel-title">Components by Provider</h2>
                    </div>
                    <div class="panel-content">
                        <div class="chart-container" id="provider-chart"></div>
                    </div>
                </div>
                <div class="card panel chart-panel">
                    <div class="panel-header">
                        <h2 class="panel-title">Diagram Updates Timeline</h2>
                    </div>
                    <div class="panel-content">
                        <div class="chart-container" id="timeline-chart"></div>
                    </div>
                </div>
            </div>
        `;

        this.attachEventListeners();
    }

    /**
     * Render diagram cards
     */
    renderDiagramCards() {
        return this.diagrams.map(diagram => `
            <div class="arch-card" data-id="${diagram.id}">
                <div class="arch-card-preview">
                    <div class="arch-card-placeholder">
                        <span class="arch-icon">${this.getProviderIcon(diagram.providers[0])}</span>
                    </div>
                </div>
                <div class="arch-card-content">
                    <div class="arch-card-header">
                        <h3 class="arch-card-title">${diagram.title}</h3>
                        <div class="arch-card-providers">
                            ${diagram.providers.map(p => `<span class="provider-badge ${p}">${this.formatProvider(p)}</span>`).join('')}
                        </div>
                    </div>
                    <p class="arch-card-description">${diagram.description}</p>
                    <div class="arch-card-meta">
                        <span class="meta-item">
                            <span class="meta-icon">&#9679;</span>
                            ${diagram.components.count} components
                        </span>
                        <span class="meta-item">
                            <span class="meta-icon">&#128197;</span>
                            ${this.formatDate(diagram.last_updated)}
                        </span>
                    </div>
                    <div class="arch-card-tags">
                        ${diagram.tags.map(t => `<span class="tag">${t}</span>`).join('')}
                    </div>
                    <div class="arch-card-actions">
                        <button class="btn btn-primary btn-sm" onclick="archView.openInDrawio('${diagram.id}')">
                            Open in draw.io
                        </button>
                        <button class="btn btn-secondary btn-sm" onclick="archView.viewDetails('${diagram.id}')">
                            Details
                        </button>
                        <button class="btn btn-secondary btn-sm" onclick="archView.downloadDiagram('${diagram.id}')">
                            Download
                        </button>
                    </div>
                </div>
            </div>
        `).join('');
    }

    /**
     * Open diagram in draw.io using GitHub integration
     */
    openInDrawio(diagramId) {
        const diagram = this.diagrams.find(d => d.id === diagramId);
        if (!diagram) return;

        const { org, repo, branch, basePath } = this.githubConfig;
        const path = `${basePath}/${diagram.file_drawio}`;
        const url = `https://app.diagrams.net/?mode=github#H${org}/${repo}/${branch}/${path}`;

        window.open(url, '_blank');
    }

    /**
     * View diagram details
     */
    viewDetails(diagramId) {
        const diagram = this.diagrams.find(d => d.id === diagramId);
        if (!diagram) return;

        // Show modal or expand card with details
        console.log('View details:', diagram);
        alert(`Diagram: ${diagram.title}\n\nProviders: ${diagram.providers.join(', ')}\nComponents: ${diagram.components.count}\nTypes: ${diagram.components.types.join(', ')}\n\nSource: ${diagram.source}`);
    }

    /**
     * Download diagram file
     */
    downloadDiagram(diagramId) {
        const diagram = this.diagrams.find(d => d.id === diagramId);
        if (!diagram) return;

        const { org, repo, branch, basePath } = this.githubConfig;
        const url = `https://raw.githubusercontent.com/${org}/${repo}/${branch}/${basePath}/${diagram.file_drawio}`;

        window.open(url, '_blank');
    }

    /**
     * Initialize ECharts
     */
    initCharts() {
        this.initProviderChart();
        this.initTimelineChart();
    }

    /**
     * Provider distribution chart
     */
    initProviderChart() {
        const container = document.getElementById('provider-chart');
        if (!container || typeof echarts === 'undefined') return;

        const chart = echarts.init(container, 'azureDark');

        // Aggregate components by provider
        const providerData = {};
        this.diagrams.forEach(d => {
            d.providers.forEach(p => {
                providerData[p] = (providerData[p] || 0) + d.components.count;
            });
        });

        const option = {
            tooltip: { trigger: 'item' },
            series: [{
                type: 'pie',
                radius: ['40%', '70%'],
                avoidLabelOverlap: false,
                itemStyle: {
                    borderRadius: 4,
                    borderColor: '#1b1a19',
                    borderWidth: 2
                },
                label: { show: false },
                emphasis: {
                    label: { show: true, fontSize: 14, fontWeight: 'bold' }
                },
                data: Object.entries(providerData).map(([name, value], i) => ({
                    name: this.formatProvider(name),
                    value,
                    itemStyle: { color: this.getProviderColor(name) }
                }))
            }]
        };

        chart.setOption(option);
        window.addEventListener('resize', () => chart.resize());
    }

    /**
     * Timeline chart
     */
    initTimelineChart() {
        const container = document.getElementById('timeline-chart');
        if (!container || typeof echarts === 'undefined') return;

        const chart = echarts.init(container, 'azureDark');

        const option = {
            tooltip: { trigger: 'axis' },
            xAxis: {
                type: 'category',
                data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                axisLabel: { fontSize: 10 }
            },
            yAxis: {
                type: 'value',
                axisLabel: { fontSize: 10 }
            },
            series: [{
                type: 'bar',
                data: [1, 0, 2, 1, 0, 0, 1],
                itemStyle: {
                    color: '#0078d4',
                    borderRadius: [4, 4, 0, 0]
                }
            }]
        };

        chart.setOption(option);
        window.addEventListener('resize', () => chart.resize());
    }

    /**
     * Attach event listeners
     */
    attachEventListeners() {
        const providerFilter = document.getElementById('provider-filter');
        const sourceFilter = document.getElementById('source-filter');
        const generateBtn = document.getElementById('generate-diagram-btn');
        const refreshBtn = document.getElementById('refresh-diagrams-btn');

        providerFilter?.addEventListener('change', () => this.filterDiagrams());
        sourceFilter?.addEventListener('change', () => this.filterDiagrams());
        generateBtn?.addEventListener('click', () => this.showGenerateDialog());
        refreshBtn?.addEventListener('click', () => this.loadManifest().then(() => this.render()));
    }

    /**
     * Filter diagrams based on selected filters
     */
    filterDiagrams() {
        const provider = document.getElementById('provider-filter')?.value || 'all';
        const source = document.getElementById('source-filter')?.value || 'all';

        const grid = document.getElementById('diagrams-grid');
        if (!grid) return;

        const cards = grid.querySelectorAll('.arch-card');
        cards.forEach(card => {
            const diagram = this.diagrams.find(d => d.id === card.dataset.id);
            if (!diagram) return;

            const matchesProvider = provider === 'all' || diagram.providers.includes(provider);
            const matchesSource = source === 'all' || diagram.source === source;

            card.style.display = (matchesProvider && matchesSource) ? 'flex' : 'none';
        });
    }

    /**
     * Show generate diagram dialog
     */
    showGenerateDialog() {
        alert('Generate Diagram feature coming soon!\n\nThis will use the diagram-ai-generator MCP skill to:\n1. Scan your infrastructure (Azure, DO, K8s)\n2. Generate a .drawio diagram\n3. Save to docs/diagrams/architecture');
    }

    // Helper methods
    getUniqueProviders() {
        const providers = new Set();
        this.diagrams.forEach(d => d.providers.forEach(p => providers.add(p)));
        return Array.from(providers);
    }

    getTotalComponents() {
        return this.diagrams.reduce((sum, d) => sum + d.components.count, 0);
    }

    getRecentCount() {
        const weekAgo = Date.now() - 7 * 24 * 60 * 60 * 1000;
        return this.diagrams.filter(d => new Date(d.last_updated).getTime() > weekAgo).length;
    }

    formatProvider(provider) {
        const names = {
            azure: 'Azure',
            aws: 'AWS',
            gcp: 'GCP',
            kubernetes: 'Kubernetes',
            digitalocean: 'DigitalOcean',
            generic: 'Generic'
        };
        return names[provider] || provider;
    }

    getProviderIcon(provider) {
        const icons = {
            azure: '&#9729;',  // Cloud
            aws: '&#9729;',
            gcp: '&#9729;',
            kubernetes: '&#9096;',  // Wheel
            digitalocean: '&#128167;',  // Droplet
            generic: '&#9632;'
        };
        return icons[provider] || '&#9632;';
    }

    getProviderColor(provider) {
        const colors = {
            azure: '#0078d4',
            aws: '#ff9900',
            gcp: '#4285f4',
            kubernetes: '#326ce5',
            digitalocean: '#0080ff',
            generic: '#797775'
        };
        return colors[provider] || '#797775';
    }

    formatDate(dateStr) {
        const date = new Date(dateStr);
        const now = new Date();
        const diff = now - date;
        const days = Math.floor(diff / (24 * 60 * 60 * 1000));

        if (days === 0) return 'Today';
        if (days === 1) return 'Yesterday';
        if (days < 7) return `${days} days ago`;
        return date.toLocaleDateString();
    }
}

// Initialize and export
window.archView = new ArchitectureView();

// Add to navigation
document.addEventListener('DOMContentLoaded', () => {
    // Add Architecture nav item if not present
    const navMenu = document.querySelector('.nav-menu');
    if (navMenu && !document.querySelector('[data-view="architecture"]')) {
        const archNavItem = document.createElement('li');
        archNavItem.className = 'nav-item';
        archNavItem.dataset.view = 'architecture';
        archNavItem.innerHTML = `
            <span class="nav-icon">&#9633;</span>
            <span class="nav-text">Architecture</span>
        `;
        // Insert after Overview
        const overviewItem = navMenu.querySelector('[data-view="dashboard"]');
        if (overviewItem) {
            overviewItem.parentNode.insertBefore(archNavItem, overviewItem.nextSibling);
        }
    }
});
