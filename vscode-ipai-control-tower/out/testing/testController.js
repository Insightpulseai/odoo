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
exports.OdooTestController = void 0;
const vscode = __importStar(require("vscode"));
const path = __importStar(require("path"));
const cp = __importStar(require("child_process"));
/**
 * Odoo 18 Test Controller — surfaces module tests in VS Code Test Explorer.
 *
 * For each ipai_* module with test files, creates test items that:
 * 1. Create a disposable test_<module> database
 * 2. Run odoo-bin --test-enable --stop-after-init
 * 3. Parse output for pass/fail
 * 4. Drop the test database
 */
class OdooTestController {
    workspaceRoot;
    controller;
    runProfiles = [];
    constructor(workspaceRoot) {
        this.workspaceRoot = workspaceRoot;
        this.controller = vscode.tests.createTestController('ipai.odooTests', 'Odoo 18 Module Tests');
        // Run profile
        this.runProfiles.push(this.controller.createRunProfile('Run Odoo Tests', vscode.TestRunProfileKind.Run, (request, token) => this.runTests(request, token)));
        this.controller.resolveHandler = async (item) => {
            if (!item) {
                // Root — discover all modules
                await this.discoverTests();
            }
        };
    }
    /**
     * Populate the test tree from discovered modules.
     */
    async loadModules(modules) {
        // Clear existing
        this.controller.items.forEach((item) => this.controller.items.delete(item.id));
        for (const mod of modules) {
            if (!mod.hasTests)
                continue;
            const moduleItem = this.controller.createTestItem(mod.name, mod.name, vscode.Uri.file(mod.path));
            moduleItem.canResolveChildren = true;
            for (const testFile of mod.testFiles) {
                const fileName = path.basename(testFile, '.py');
                const fileItem = this.controller.createTestItem(`${mod.name}/${fileName}`, fileName, vscode.Uri.file(testFile));
                moduleItem.children.add(fileItem);
            }
            this.controller.items.add(moduleItem);
        }
    }
    async discoverTests() {
        // Discovery is driven by loadModules() called from extension.ts
        // This handler is for lazy resolution
    }
    async runTests(request, token) {
        const run = this.controller.createTestRun(request);
        const items = this.collectTestItems(request);
        // Group by module
        const moduleGroups = new Map();
        for (const item of items) {
            const moduleName = item.id.split('/')[0];
            if (!moduleGroups.has(moduleName)) {
                moduleGroups.set(moduleName, []);
            }
            moduleGroups.get(moduleName).push(item);
        }
        for (const [moduleName, testItems] of moduleGroups) {
            if (token.isCancellationRequested)
                break;
            for (const item of testItems) {
                run.started(item);
            }
            try {
                const result = await this.runModuleTests(moduleName, token);
                for (const item of testItems) {
                    if (result.success) {
                        run.passed(item, result.duration);
                    }
                    else {
                        run.failed(item, new vscode.TestMessage(result.output), result.duration);
                    }
                }
            }
            catch (err) {
                for (const item of testItems) {
                    run.errored(item, new vscode.TestMessage(err instanceof Error ? err.message : String(err)));
                }
            }
        }
        run.end();
    }
    async runModuleTests(moduleName, token) {
        const config = vscode.workspace.getConfiguration('ipai');
        const pythonPath = config.get('odoo.pythonPath') || 'python3';
        const vendorPath = path.join(this.workspaceRoot, config.get('odoo.vendorPath', 'vendor/odoo'));
        const addonsPath = path.join(this.workspaceRoot, config.get('odoo.addonsPath', 'addons/ipai'));
        const dbPrefix = config.get('odoo.testDbPrefix', 'test_');
        const dbName = `${dbPrefix}${moduleName}`;
        const odooBin = path.join(vendorPath, 'odoo-bin');
        const start = Date.now();
        return new Promise((resolve) => {
            // Create test DB, run tests, drop DB
            const script = [
                `createdb ${dbName} 2>/dev/null || true`,
                `${pythonPath} ${odooBin} ` +
                    `--database=${dbName} ` +
                    `--db_host=localhost --db_port=5432 --db_user=tbwa --db_password=False ` +
                    `--addons-path=${vendorPath}/addons,${addonsPath} ` +
                    `-i ${moduleName} ` +
                    `--test-enable --stop-after-init ` +
                    `--no-http 2>&1`,
                `dropdb ${dbName} 2>/dev/null || true`,
            ].join(' && ');
            const proc = cp.exec(script, {
                cwd: this.workspaceRoot,
                timeout: 120000,
                env: { ...process.env, PGHOST: 'localhost', PGPORT: '5432', PGUSER: 'tbwa' },
            });
            let output = '';
            proc.stdout?.on('data', (data) => (output += data));
            proc.stderr?.on('data', (data) => (output += data));
            token.onCancellationRequested(() => proc.kill());
            proc.on('close', (code) => {
                const duration = Date.now() - start;
                const hasError = output.includes('ERROR') ||
                    output.includes('FAIL') ||
                    code !== 0;
                resolve({
                    success: !hasError,
                    output: output.slice(-2000), // last 2000 chars
                    duration,
                });
            });
            proc.on('error', (err) => {
                resolve({
                    success: false,
                    output: err.message,
                    duration: Date.now() - start,
                });
            });
        });
    }
    collectTestItems(request) {
        const items = [];
        if (request.include) {
            for (const item of request.include) {
                items.push(item);
            }
        }
        else {
            this.controller.items.forEach((item) => items.push(item));
        }
        return items;
    }
    dispose() {
        this.controller.dispose();
        for (const p of this.runProfiles) {
            p.dispose();
        }
    }
}
exports.OdooTestController = OdooTestController;
//# sourceMappingURL=testController.js.map