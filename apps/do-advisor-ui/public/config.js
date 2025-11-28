/**
 * DO Advisor UI Configuration
 *
 * Edit these values to connect to your infrastructure
 */
window.DO_ADVISOR_CONFIG = {
    // DigitalOcean Agent Platform
    agentEndpoint: 'https://wr2azp5dsl6mu6xvxtpglk5v.agents.do-ai.run',
    agentApiKey: '', // Set via environment or manually

    // Self-Hosted Stack Endpoints
    n8n: {
        endpoint: 'https://n8n.insightpulseai.net',
        apiKey: '',
    },
    mattermost: {
        endpoint: 'https://mattermost.insightpulseai.net',
        apiKey: '',
    },
    superset: {
        endpoint: 'https://superset.insightpulseai.net',
        apiKey: '',
    },
    odoo: {
        endpoint: 'https://odoo.insightpulseai.net',
        database: 'odooprod',
        username: '',
        password: '',
    },

    // DigitalOcean API
    digitalocean: {
        apiToken: '', // DIGITALOCEAN_ACCESS_TOKEN
    },

    // Refresh Intervals (milliseconds)
    intervals: {
        recommendations: 60000,  // 1 minute
        jobs: 30000,             // 30 seconds
        metrics: 60000,          // 1 minute
        infrastructure: 120000,  // 2 minutes
    },

    // Feature Flags
    features: {
        enableAIChat: true,
        enableExport: true,
        enableNotifications: true,
        enableDarkModeToggle: false, // Dark mode is default
    },

    // Chart Colors (Azure-inspired palette)
    chartColors: {
        primary: '#0078d4',
        success: '#107c10',
        warning: '#ffaa44',
        critical: '#d13438',
        muted: '#797775',
        series: [
            '#0078d4', // Azure Blue
            '#8764b8', // Purple
            '#107c10', // Green
            '#ffaa44', // Orange
            '#d13438', // Red
            '#00bcf2', // Cyan
        ],
    },
};

// Freeze config to prevent accidental modifications
Object.freeze(window.DO_ADVISOR_CONFIG);
