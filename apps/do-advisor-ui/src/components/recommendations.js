/**
 * DO Advisor - Recommendations Component
 *
 * Handles rendering and interaction with recommendation cards
 */

class RecommendationsManager {
    constructor() {
        this.recommendations = [];
        this.filters = {
            category: 'all',
            impact: 'all',
            search: '',
        };
    }

    /**
     * Fetch recommendations from DO Advisor Agent
     */
    async fetchRecommendations() {
        const config = window.DO_ADVISOR_CONFIG;

        try {
            const response = await fetch(`${config.agentEndpoint}/api/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${config.agentApiKey}`,
                },
                body: JSON.stringify({
                    messages: [{
                        role: 'user',
                        content: 'List all current recommendations in JSON format with fields: id, category, severity, title, resource, impact, description, actions'
                    }],
                }),
            });

            if (!response.ok) throw new Error('Failed to fetch recommendations');

            const data = await response.json();
            // Parse recommendations from agent response
            this.recommendations = this.parseAgentResponse(data);
            return this.recommendations;
        } catch (error) {
            console.error('Error fetching recommendations:', error);
            return this.getMockRecommendations();
        }
    }

    /**
     * Parse agent response into recommendations array
     */
    parseAgentResponse(response) {
        try {
            // Try to extract JSON from response
            const content = response.choices?.[0]?.message?.content || response.content || '';
            const jsonMatch = content.match(/\[[\s\S]*\]/);
            if (jsonMatch) {
                return JSON.parse(jsonMatch[0]);
            }
        } catch (e) {
            console.warn('Could not parse agent response as JSON');
        }
        return this.getMockRecommendations();
    }

    /**
     * Get mock recommendations for development/demo
     */
    getMockRecommendations() {
        return [
            {
                id: 'rec-001',
                category: 'cost',
                severity: 'medium',
                title: 'Right-size underutilized Droplet',
                resource: 'droplet-staging-02',
                impact: 'Save $20/month',
                description: 'This Droplet has averaged less than 5% CPU usage over the past 7 days. Consider downsizing to a smaller instance.',
                actions: ['Resize Droplet', 'View Metrics', 'Dismiss'],
            },
            {
                id: 'rec-002',
                category: 'security',
                severity: 'critical',
                title: 'SSL certificate expiring soon',
                resource: 'api.insightpulseai.net',
                impact: 'Expires in 14 days',
                description: 'The SSL certificate for this domain will expire soon. Renew immediately to avoid service disruption.',
                actions: ['Renew Certificate', 'View Details'],
            },
            {
                id: 'rec-003',
                category: 'reliability',
                severity: 'high',
                title: 'Enable HA for DOKS cluster',
                resource: 'k8s-fin-workspace',
                impact: 'Improve uptime',
                description: 'Your cluster has a single control plane node. Enable HA control plane for production workloads.',
                actions: ['Enable HA', 'Learn More'],
            },
            {
                id: 'rec-004',
                category: 'performance',
                severity: 'medium',
                title: 'High latency on API endpoint',
                resource: '/api/v1/reports',
                impact: 'P95 > 2 seconds',
                description: 'This endpoint consistently exceeds the 500ms latency SLO. Consider caching or query optimization.',
                actions: ['View Traces', 'Add Caching'],
            },
            {
                id: 'rec-005',
                category: 'operational',
                severity: 'low',
                title: 'Clean up unused snapshots',
                resource: '5 snapshots > 90 days old',
                impact: 'Save $15/month',
                description: 'You have snapshots that havent been used in over 90 days. Consider deleting them.',
                actions: ['Review Snapshots', 'Dismiss'],
            },
        ];
    }

    /**
     * Filter recommendations based on current filters
     */
    getFilteredRecommendations() {
        return this.recommendations.filter(rec => {
            if (this.filters.category !== 'all' && rec.category !== this.filters.category) {
                return false;
            }
            if (this.filters.impact !== 'all' && rec.severity !== this.filters.impact) {
                return false;
            }
            if (this.filters.search) {
                const searchLower = this.filters.search.toLowerCase();
                return rec.title.toLowerCase().includes(searchLower) ||
                       rec.resource.toLowerCase().includes(searchLower) ||
                       rec.description.toLowerCase().includes(searchLower);
            }
            return true;
        });
    }

    /**
     * Group recommendations by severity for summary
     */
    getSummary() {
        const summary = {
            critical: 0,
            high: 0,
            medium: 0,
            low: 0,
            total: this.recommendations.length,
        };

        this.recommendations.forEach(rec => {
            if (summary.hasOwnProperty(rec.severity)) {
                summary[rec.severity]++;
            }
        });

        return summary;
    }

    /**
     * Calculate advisor score based on recommendations
     */
    calculateScore() {
        const penalties = {
            critical: 15,
            high: 8,
            medium: 3,
            low: 1,
        };

        let totalPenalty = 0;
        this.recommendations.forEach(rec => {
            totalPenalty += penalties[rec.severity] || 0;
        });

        return Math.max(0, Math.min(100, 100 - totalPenalty));
    }

    /**
     * Get category icon
     */
    getCategoryIcon(category) {
        const icons = {
            cost: '💰',
            security: '🔒',
            reliability: '🛡️',
            performance: '⚡',
            operational: '⚙️',
        };
        return icons[category] || '📋';
    }

    /**
     * Get severity badge class
     */
    getSeverityClass(severity) {
        return {
            critical: 'badge-critical',
            high: 'badge-high',
            medium: 'badge-medium',
            low: 'badge-low',
        }[severity] || 'badge-info';
    }

    /**
     * Apply fix for a recommendation (calls agent)
     */
    async applyFix(recommendationId) {
        const rec = this.recommendations.find(r => r.id === recommendationId);
        if (!rec) return { success: false, message: 'Recommendation not found' };

        const config = window.DO_ADVISOR_CONFIG;

        try {
            const response = await fetch(`${config.agentEndpoint}/api/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${config.agentApiKey}`,
                },
                body: JSON.stringify({
                    messages: [{
                        role: 'user',
                        content: `Apply the recommended fix for: ${rec.title} on resource ${rec.resource}. Provide step-by-step commands.`
                    }],
                }),
            });

            if (!response.ok) throw new Error('Failed to apply fix');

            const data = await response.json();
            return {
                success: true,
                message: 'Fix applied successfully',
                details: data.choices?.[0]?.message?.content,
            };
        } catch (error) {
            console.error('Error applying fix:', error);
            return {
                success: false,
                message: error.message,
            };
        }
    }

    /**
     * Dismiss a recommendation
     */
    dismiss(recommendationId) {
        this.recommendations = this.recommendations.filter(r => r.id !== recommendationId);
        // TODO: Persist dismissal to backend
    }
}

// Export for use in app.js
window.RecommendationsManager = RecommendationsManager;
