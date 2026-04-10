"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.InfraRepoAdapter = void 0;
const cp = __importStar(require("child_process"));
/**
 * Adapter for Azure runtime health checks.
 * Calls `az` CLI and existing smoke scripts — does NOT own business logic.
 */
class InfraRepoAdapter {
    workspaceRoot;
    resourceGroup;
    containerAppName;
    constructor(workspaceRoot, resourceGroup, containerAppName) {
        this.workspaceRoot = workspaceRoot;
        this.resourceGroup = resourceGroup;
        this.containerAppName = containerAppName;
    }
    // -----------------------------------------------------------------------
    // Container App checks
    // -----------------------------------------------------------------------
    async checkContainerApp() {
        try {
            const result = await this.runAz([
                'containerapp',
                'show',
                '--name',
                this.containerAppName,
                '--resource-group',
                this.resourceGroup,
                '--query',
                '{status:properties.runningStatus, fqdn:properties.configuration.ingress.fqdn}',
                '-o',
                'json',
            ]);
            const data = JSON.parse(result);
            const isRunning = data.status === 'Running' || data.fqdn;
            return {
                name: `Container App: ${this.containerAppName}`,
                category: 'container-app',
                status: isRunning ? 'pass' : 'fail',
                detail: isRunning
                    ? `Running at ${data.fqdn}`
                    : `Status: ${data.status ?? 'unknown'}`,
                timestamp: new Date(),
            };
        }
        catch (err) {
            return this.failedCheck(`Container App: ${this.containerAppName}`, 'container-app', err);
        }
    }
    async checkContainerAppRevisions() {
        try {
            const result = await this.runAz([
                'containerapp',
                'revision',
                'list',
                '--name',
                this.containerAppName,
                '--resource-group',
                this.resourceGroup,
                '--query',
                '[].{name:name, active:properties.active, replicas:properties.replicas}',
                '-o',
                'json',
            ]);
            const revisions = JSON.parse(result);
            const activeCount = revisions.filter((r) => r.active).length;
            return {
                name: 'ACA Revisions',
                category: 'container-app',
                status: activeCount > 0 ? 'pass' : 'fail',
                detail: `${activeCount} active revision(s) of ${revisions.length} total`,
                timestamp: new Date(),
            };
        }
        catch (err) {
            return this.failedCheck('ACA Revisions', 'container-app', err);
        }
    }
    // -----------------------------------------------------------------------
    // Database checks
    // -----------------------------------------------------------------------
    async checkPostgres() {
        try {
            const result = await this.runAz([
                'postgres',
                'flexible-server',
                'list',
                '--resource-group',
                this.resourceGroup,
                '--query',
                '[0].{name:name, state:state, version:version, ha:highAvailability.mode}',
                '-o',
                'json',
            ]);
            const data = JSON.parse(result);
            const isReady = data.state === 'Ready';
            return {
                name: `PostgreSQL: ${data.name}`,
                category: 'database',
                status: isReady ? 'pass' : 'fail',
                detail: `State: ${data.state}, v${data.version}, HA: ${data.ha ?? 'Disabled'}`,
                timestamp: new Date(),
            };
        }
        catch (err) {
            return this.failedCheck('PostgreSQL', 'database', err);
        }
    }
    // -----------------------------------------------------------------------
    // Identity checks
    // -----------------------------------------------------------------------
    async checkManagedIdentity() {
        try {
            const result = await this.runAz([
                'containerapp',
                'identity',
                'show',
                '--name',
                this.containerAppName,
                '--resource-group',
                this.resourceGroup,
                '-o',
                'json',
            ]);
            const data = JSON.parse(result);
            const hasSystemAssigned = data.type?.includes('SystemAssigned');
            return {
                name: 'Managed Identity',
                category: 'identity',
                status: hasSystemAssigned ? 'pass' : 'warning',
                detail: hasSystemAssigned
                    ? `System-assigned MI active (${data.principalId?.slice(0, 8)}...)`
                    : 'No system-assigned managed identity',
                timestamp: new Date(),
            };
        }
        catch (err) {
            return this.failedCheck('Managed Identity', 'identity', err);
        }
    }
    // -----------------------------------------------------------------------
    // AI service checks
    // -----------------------------------------------------------------------
    async checkFoundryEndpoint(endpoint) {
        try {
            const result = await this.runShell(`curl -s -o /dev/null -w '%{http_code}' '${endpoint}/health' --max-time 5`);
            const status = result.trim();
            return {
                name: 'Foundry Endpoint',
                category: 'ai-service',
                status: status === '200' ? 'pass' : 'fail',
                detail: `HTTP ${status}`,
                timestamp: new Date(),
            };
        }
        catch (err) {
            return this.failedCheck('Foundry Endpoint', 'ai-service', err);
        }
    }
    // -----------------------------------------------------------------------
    // Run all checks
    // -----------------------------------------------------------------------
    async runAllChecks() {
        const checks = await Promise.allSettled([
            this.checkContainerApp(),
            this.checkContainerAppRevisions(),
            this.checkPostgres(),
            this.checkManagedIdentity(),
        ]);
        return checks.map((c) => c.status === 'fulfilled'
            ? c.value
            : this.failedCheck('Unknown', 'container-app', c.reason));
    }
    // -----------------------------------------------------------------------
    // Helpers
    // -----------------------------------------------------------------------
    failedCheck(name, category, err) {
        return {
            name,
            category,
            status: 'fail',
            detail: err instanceof Error ? err.message : String(err),
            timestamp: new Date(),
        };
    }
    runAz(args) {
        return this.runShell(`az ${args.map((a) => `'${a}'`).join(' ')}`);
    }
    runShell(command) {
        return new Promise((resolve, reject) => {
            cp.exec(command, { cwd: this.workspaceRoot, timeout: 15000 }, (err, stdout, stderr) => {
                if (err) {
                    reject(new Error(stderr || err.message));
                }
                else {
                    resolve(stdout.trim());
                }
            });
        });
    }
}
exports.InfraRepoAdapter = InfraRepoAdapter;
//# sourceMappingURL=infraRepoAdapter.js.map