/**
 * DO Advisor - Jobs & Automations Monitor
 *
 * Monitors n8n workflows, Odoo cron jobs, and other scheduled tasks
 */

class JobsMonitor {
    constructor() {
        this.jobs = [];
        this.sources = ['n8n', 'odoo', 'superset', 'system'];
        this.statusFilter = 'all';
    }

    /**
     * Fetch all jobs from connected sources
     */
    async fetchAllJobs() {
        const results = await Promise.allSettled([
            this.fetchN8nWorkflows(),
            this.fetchOdooCrons(),
            this.fetchSupersetJobs(),
        ]);

        this.jobs = results
            .filter(r => r.status === 'fulfilled')
            .flatMap(r => r.value);

        return this.jobs;
    }

    /**
     * Fetch n8n workflow executions
     */
    async fetchN8nWorkflows() {
        const config = window.DO_ADVISOR_CONFIG?.n8n;
        if (!config?.endpoint) return this.getMockN8nJobs();

        try {
            // Fetch workflows
            const workflowsRes = await fetch(`${config.endpoint}/api/v1/workflows`, {
                headers: { 'X-N8N-API-KEY': config.apiKey },
            });
            const workflows = await workflowsRes.json();

            // Fetch recent executions
            const executionsRes = await fetch(`${config.endpoint}/api/v1/executions?limit=50`, {
                headers: { 'X-N8N-API-KEY': config.apiKey },
            });
            const executions = await executionsRes.json();

            return this.mapN8nToJobs(workflows.data, executions.data);
        } catch (error) {
            console.error('Error fetching n8n jobs:', error);
            return this.getMockN8nJobs();
        }
    }

    /**
     * Map n8n data to unified job format
     */
    mapN8nToJobs(workflows, executions) {
        const executionMap = new Map();
        executions.forEach(exec => {
            if (!executionMap.has(exec.workflowId)) {
                executionMap.set(exec.workflowId, exec);
            }
        });

        return workflows.map(wf => {
            const lastExec = executionMap.get(wf.id);
            const status = this.determineN8nStatus(wf, lastExec);

            return {
                id: `n8n-${wf.id}`,
                name: wf.name,
                source: 'n8n',
                status: status,
                schedule: wf.settings?.scheduleType === 'cron' ? wf.settings.cronExpression : 'Manual',
                lastRun: lastExec ? new Date(lastExec.startedAt) : null,
                duration: lastExec ? this.formatDuration(lastExec.stoppedAt - lastExec.startedAt) : '-',
                error: lastExec?.status === 'error' ? lastExec.data?.resultData?.error?.message : null,
                active: wf.active,
            };
        });
    }

    /**
     * Determine n8n workflow status
     */
    determineN8nStatus(workflow, lastExecution) {
        if (!workflow.active) return 'disabled';
        if (lastExecution?.status === 'running') return 'running';
        if (lastExecution?.status === 'error') return 'failed';

        // Check if stale (cron job that hasn't run in expected window)
        if (workflow.settings?.scheduleType === 'cron' && lastExecution) {
            const cronInterval = this.parseCronInterval(workflow.settings.cronExpression);
            const timeSinceLastRun = Date.now() - new Date(lastExecution.startedAt).getTime();
            if (timeSinceLastRun > cronInterval * 2) return 'stale';
        }

        if (lastExecution?.status === 'success') return 'success';
        return 'scheduled';
    }

    /**
     * Fetch Odoo scheduled actions (ir.cron)
     */
    async fetchOdooCrons() {
        const config = window.DO_ADVISOR_CONFIG?.odoo;
        if (!config?.endpoint) return this.getMockOdooJobs();

        try {
            // Authenticate
            const authRes = await fetch(`${config.endpoint}/jsonrpc`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    jsonrpc: '2.0',
                    method: 'call',
                    params: {
                        service: 'common',
                        method: 'authenticate',
                        args: [config.database, config.username, config.password, {}],
                    },
                    id: 1,
                }),
            });
            const { result: uid } = await authRes.json();

            // Fetch crons
            const cronsRes = await fetch(`${config.endpoint}/jsonrpc`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    jsonrpc: '2.0',
                    method: 'call',
                    params: {
                        service: 'object',
                        method: 'execute_kw',
                        args: [
                            config.database, uid, config.password,
                            'ir.cron', 'search_read',
                            [[]],
                            { fields: ['name', 'active', 'interval_number', 'interval_type', 'lastcall', 'nextcall'] },
                        ],
                    },
                    id: 2,
                }),
            });
            const { result: crons } = await cronsRes.json();

            return this.mapOdooToJobs(crons);
        } catch (error) {
            console.error('Error fetching Odoo crons:', error);
            return this.getMockOdooJobs();
        }
    }

    /**
     * Map Odoo cron data to unified job format
     */
    mapOdooToJobs(crons) {
        return crons.map(cron => {
            const lastRun = cron.lastcall ? new Date(cron.lastcall) : null;
            const nextRun = cron.nextcall ? new Date(cron.nextcall) : null;

            let status = 'scheduled';
            if (!cron.active) status = 'disabled';
            else if (nextRun && nextRun < new Date()) status = 'stale';

            return {
                id: `odoo-${cron.id}`,
                name: cron.name,
                source: 'odoo',
                status: status,
                schedule: `Every ${cron.interval_number} ${cron.interval_type}`,
                lastRun: lastRun,
                nextRun: nextRun,
                duration: '-',
                active: cron.active,
            };
        });
    }

    /**
     * Fetch Superset scheduled reports/refreshes
     */
    async fetchSupersetJobs() {
        const config = window.DO_ADVISOR_CONFIG?.superset;
        if (!config?.endpoint) return [];

        // TODO: Implement Superset API integration
        return [];
    }

    /**
     * Get mock n8n jobs for development
     */
    getMockN8nJobs() {
        return [
            {
                id: 'n8n-W001',
                name: 'W001_MONTHLY_CLOSE',
                source: 'n8n',
                status: 'running',
                schedule: '0 0 1 * *',
                lastRun: new Date(Date.now() - 5 * 60000),
                duration: '5m 23s',
                progress: 60,
            },
            {
                id: 'n8n-W002',
                name: 'W002_DAILY_BACKUP',
                source: 'n8n',
                status: 'scheduled',
                schedule: '0 2 * * *',
                lastRun: new Date(Date.now() - 22 * 3600000),
                duration: '12m 45s',
            },
            {
                id: 'n8n-W003',
                name: 'W003_OCR_SYNC',
                source: 'n8n',
                status: 'stale',
                schedule: '*/30 * * * *',
                lastRun: new Date(Date.now() - 3 * 86400000),
                duration: '2m 10s',
            },
            {
                id: 'n8n-W004',
                name: 'W004_EMAIL_DIGEST',
                source: 'n8n',
                status: 'failed',
                schedule: '0 8 * * *',
                lastRun: new Date(Date.now() - 2 * 3600000),
                duration: '1m 02s',
                error: 'SMTP connection timeout',
            },
        ];
    }

    /**
     * Get mock Odoo jobs for development
     */
    getMockOdooJobs() {
        return [
            {
                id: 'odoo-C001',
                name: 'Cleanup: Autovacuum',
                source: 'odoo',
                status: 'scheduled',
                schedule: 'Every 1 days',
                lastRun: new Date(Date.now() - 21 * 3600000),
                duration: '45s',
            },
            {
                id: 'odoo-C002',
                name: 'Mail: Fetchmail Service',
                source: 'odoo',
                status: 'success',
                schedule: 'Every 5 minutes',
                lastRun: new Date(Date.now() - 3 * 60000),
                duration: '12s',
            },
        ];
    }

    /**
     * Filter jobs by status
     */
    getFilteredJobs(status = 'all') {
        if (status === 'all') return this.jobs;
        return this.jobs.filter(job => job.status === status);
    }

    /**
     * Get job counts by status
     */
    getStatusCounts() {
        const counts = {
            running: 0,
            scheduled: 0,
            stale: 0,
            failed: 0,
            success: 0,
            disabled: 0,
        };

        this.jobs.forEach(job => {
            if (counts.hasOwnProperty(job.status)) {
                counts[job.status]++;
            }
        });

        return counts;
    }

    /**
     * Trigger a job to run immediately
     */
    async runJob(jobId) {
        const job = this.jobs.find(j => j.id === jobId);
        if (!job) return { success: false, message: 'Job not found' };

        if (job.source === 'n8n') {
            return this.triggerN8nWorkflow(job);
        } else if (job.source === 'odoo') {
            return this.triggerOdooCron(job);
        }

        return { success: false, message: 'Unsupported job source' };
    }

    /**
     * Trigger n8n workflow execution
     */
    async triggerN8nWorkflow(job) {
        const config = window.DO_ADVISOR_CONFIG?.n8n;
        if (!config?.endpoint) return { success: false, message: 'n8n not configured' };

        try {
            const workflowId = job.id.replace('n8n-', '');
            const response = await fetch(`${config.endpoint}/api/v1/workflows/${workflowId}/execute`, {
                method: 'POST',
                headers: { 'X-N8N-API-KEY': config.apiKey },
            });

            if (!response.ok) throw new Error('Failed to trigger workflow');

            return { success: true, message: `Workflow ${job.name} triggered` };
        } catch (error) {
            return { success: false, message: error.message };
        }
    }

    /**
     * Trigger Odoo cron job
     */
    async triggerOdooCron(job) {
        // TODO: Implement Odoo cron trigger via JSON-RPC
        return { success: false, message: 'Odoo cron trigger not implemented' };
    }

    /**
     * Parse cron expression to get interval in milliseconds
     */
    parseCronInterval(cron) {
        // Simplified parsing - returns expected interval in ms
        if (!cron) return Infinity;

        const parts = cron.split(' ');
        if (parts[0].startsWith('*/')) {
            const minutes = parseInt(parts[0].slice(2));
            return minutes * 60 * 1000;
        }
        if (parts[1].startsWith('*/')) {
            const hours = parseInt(parts[1].slice(2));
            return hours * 60 * 60 * 1000;
        }
        // Default to daily
        return 24 * 60 * 60 * 1000;
    }

    /**
     * Format duration in human-readable form
     */
    formatDuration(ms) {
        if (!ms || ms < 0) return '-';
        const seconds = Math.floor(ms / 1000);
        const minutes = Math.floor(seconds / 60);
        const hours = Math.floor(minutes / 60);

        if (hours > 0) return `${hours}h ${minutes % 60}m`;
        if (minutes > 0) return `${minutes}m ${seconds % 60}s`;
        return `${seconds}s`;
    }
}

// Export for use in app.js
window.JobsMonitor = JobsMonitor;
