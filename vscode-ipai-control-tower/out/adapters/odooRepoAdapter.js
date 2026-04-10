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
exports.OdooRepoAdapter = void 0;
const vscode = __importStar(require("vscode"));
const path = __importStar(require("path"));
const fs = __importStar(require("fs/promises"));
const cp = __importStar(require("child_process"));
/**
 * Reads and parses Odoo 18 module manifests from the workspace.
 * Uses a Python subprocess for safe AST-based manifest evaluation.
 */
class OdooRepoAdapter {
    workspaceRoot;
    constructor(workspaceRoot) {
        this.workspaceRoot = workspaceRoot;
    }
    // -----------------------------------------------------------------------
    // Configuration helpers
    // -----------------------------------------------------------------------
    get config() {
        return vscode.workspace.getConfiguration('ipai');
    }
    get addonsPath() {
        return path.join(this.workspaceRoot, this.config.get('odoo.addonsPath', 'addons/ipai'));
    }
    get ocaPath() {
        return path.join(this.workspaceRoot, this.config.get('odoo.ocaPath', 'addons/oca'));
    }
    get vendorPath() {
        return path.join(this.workspaceRoot, this.config.get('odoo.vendorPath', 'vendor/odoo'));
    }
    // -----------------------------------------------------------------------
    // Manifest parsing
    // -----------------------------------------------------------------------
    /**
     * Parse a single __manifest__.py using Python AST (safe, no eval).
     */
    async parseManifest(manifestPath) {
        try {
            const raw = await this.runPython(`import ast, json, sys; print(json.dumps(ast.literal_eval(open(sys.argv[1]).read())))`, [manifestPath]);
            const data = JSON.parse(raw);
            return {
                name: data.name ?? path.basename(path.dirname(manifestPath)),
                version: data.version ?? '18.0.1.0.0',
                category: data.category,
                summary: data.summary,
                description: data.description,
                author: data.author,
                website: data.website,
                license: data.license,
                depends: data.depends ?? [],
                data: data.data,
                demo: data.demo,
                installable: data.installable !== false,
                application: data.application,
                auto_install: data.auto_install,
                external_dependencies: data.external_dependencies,
            };
        }
        catch {
            return null;
        }
    }
    // -----------------------------------------------------------------------
    // Module discovery
    // -----------------------------------------------------------------------
    /**
     * Discover all ipai_* modules under the addons path.
     */
    async discoverModules() {
        const entries = await this.listDirs(this.addonsPath);
        const modules = [];
        for (const entry of entries) {
            const modulePath = path.join(this.addonsPath, entry);
            const manifestPath = path.join(modulePath, '__manifest__.py');
            const manifest = await this.parseManifest(manifestPath);
            const hasInit = await this.fileExists(path.join(modulePath, '__init__.py'));
            const testFiles = await this.findFiles(modulePath, 'tests/test_*.py');
            const modelFiles = await this.findFiles(modulePath, 'models/*.py');
            const viewFiles = await this.findFiles(modulePath, 'views/*.xml');
            const securityFiles = await this.findFiles(modulePath, 'security/*.csv');
            const dataFiles = await this.findFiles(modulePath, 'data/*.xml');
            const classification = this.classifyModule(entry, manifest, hasInit, modelFiles, viewFiles);
            const ipaiDeps = (manifest?.depends ?? []).filter((d) => d.startsWith('ipai_'));
            modules.push({
                name: entry,
                path: modulePath,
                manifest,
                classification,
                hasTests: testFiles.length > 0,
                testFiles,
                modelFiles,
                viewFiles,
                securityFiles,
                dataFiles,
                ipaiDeps,
                reverseDeps: [], // populated after all modules are loaded
            });
        }
        // Build reverse dependency map
        for (const mod of modules) {
            for (const dep of mod.ipaiDeps) {
                const target = modules.find((m) => m.name === dep);
                if (target) {
                    target.reverseDeps.push(mod.name);
                }
            }
        }
        return modules;
    }
    /**
     * Heuristic classification for a module.
     */
    classifyModule(name, manifest, hasInit, modelFiles, viewFiles) {
        if (!manifest) {
            return 'not-a-module';
        }
        if (!manifest.installable) {
            return 'deprecated';
        }
        // Check for bridge indicators: models that import requests/aiohttp
        // This is a heuristic — full check is in the diagnostics provider
        const hasModels = modelFiles.filter((f) => !f.endsWith('__init__.py')).length > 0;
        const hasViews = viewFiles.length > 0;
        if (!hasModels && !hasViews && hasInit) {
            return 'stub';
        }
        // Modules with no __init__.py beyond manifest are stubs
        if (!hasInit && manifest) {
            return 'stub';
        }
        return 'active';
    }
    // -----------------------------------------------------------------------
    // Consolidation plan
    // -----------------------------------------------------------------------
    async loadConsolidationPlan() {
        const planPath = path.join(this.workspaceRoot, this.config.get('consolidation.planPath', 'spec/consolidation/plan.json'));
        try {
            const raw = await fs.readFile(planPath, 'utf-8');
            return JSON.parse(raw);
        }
        catch {
            return null;
        }
    }
    // -----------------------------------------------------------------------
    // File utilities
    // -----------------------------------------------------------------------
    async listDirs(dirPath) {
        try {
            const entries = await fs.readdir(dirPath, { withFileTypes: true });
            return entries
                .filter((e) => e.isDirectory() && !e.name.startsWith('.'))
                .map((e) => e.name)
                .sort();
        }
        catch {
            return [];
        }
    }
    async fileExists(filePath) {
        try {
            await fs.access(filePath);
            return true;
        }
        catch {
            return false;
        }
    }
    async findFiles(basePath, pattern) {
        const relUri = vscode.Uri.file(basePath);
        const globPattern = new vscode.RelativePattern(relUri, pattern);
        const uris = await vscode.workspace.findFiles(globPattern);
        return uris.map((u) => u.fsPath).sort();
    }
    runPython(script, args) {
        return new Promise((resolve, reject) => {
            const pythonPath = this.config.get('odoo.pythonPath') || 'python3';
            const proc = cp.spawn(pythonPath, ['-c', script, ...args], {
                cwd: this.workspaceRoot,
                timeout: 5000,
            });
            let stdout = '';
            let stderr = '';
            proc.stdout.on('data', (data) => (stdout += data));
            proc.stderr.on('data', (data) => (stderr += data));
            proc.on('close', (code) => {
                if (code === 0) {
                    resolve(stdout.trim());
                }
                else {
                    reject(new Error(`Python exited ${code}: ${stderr}`));
                }
            });
            proc.on('error', reject);
        });
    }
}
exports.OdooRepoAdapter = OdooRepoAdapter;
//# sourceMappingURL=odooRepoAdapter.js.map