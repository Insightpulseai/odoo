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
exports.registerChatParticipant = registerChatParticipant;
const vscode = __importStar(require("vscode"));
/**
 * @ipai chat participant — domain-specific assistant that understands
 * the Odoo-on-Azure workspace, module health, and release state.
 *
 * Commands:
 *   @ipai /doctor   — run workspace doctor and explain findings
 *   @ipai /blockers — summarize current release blockers
 *   @ipai /classify — classify the current addon
 *   @ipai /azure    — check Azure runtime health
 */
function registerChatParticipant(context, getFindings, getModules, getAzureChecks, getReadinessReport) {
    const participant = vscode.chat.createChatParticipant('ipai.chatParticipant', async (request, context, stream, token) => {
        const command = request.command;
        if (command === 'doctor') {
            await handleDoctor(stream, getFindings());
        }
        else if (command === 'blockers') {
            await handleBlockers(stream, getReadinessReport(), getFindings());
        }
        else if (command === 'classify') {
            await handleClassify(stream, request.prompt, getModules());
        }
        else if (command === 'azure') {
            await handleAzure(stream, getAzureChecks());
        }
        else {
            await handleFreeform(stream, request.prompt, getModules(), getFindings());
        }
    });
    participant.iconPath = vscode.Uri.joinPath(context.extensionUri, 'media', 'control-tower.svg');
    return participant;
}
// ---------------------------------------------------------------------------
// Command handlers
// ---------------------------------------------------------------------------
async function handleDoctor(stream, findings) {
    if (findings.length === 0) {
        stream.markdown('**Workspace Doctor:** All checks passed. No findings.\n');
        return;
    }
    const errors = findings.filter((f) => f.severity === 'error');
    const warnings = findings.filter((f) => f.severity === 'warning');
    stream.markdown(`**Workspace Doctor:** ${errors.length} errors, ${warnings.length} warnings\n\n`);
    if (errors.length > 0) {
        stream.markdown('### Errors\n');
        for (const f of errors) {
            stream.markdown(`- **${f.module}** (${f.check}): ${f.message}\n`);
        }
        stream.markdown('\n');
    }
    if (warnings.length > 0) {
        stream.markdown('### Warnings\n');
        for (const f of warnings) {
            stream.markdown(`- **${f.module}** (${f.check}): ${f.message}\n`);
        }
    }
}
async function handleBlockers(stream, report, findings) {
    if (!report) {
        stream.markdown('Release readiness has not been evaluated yet. Run `IPAI: Run Release Readiness Audit` first.\n');
        return;
    }
    const failing = report.gates.filter((g) => g.status === 'fail');
    if (failing.length === 0 && findings.filter((f) => f.severity === 'error').length === 0) {
        stream.markdown(`**No blockers.** Branch \`${report.branch}\` is ship-ready.\n`);
        return;
    }
    stream.markdown(`**Release blockers for \`${report.branch}\`:**\n\n`);
    if (failing.length > 0) {
        stream.markdown('### Failing gates\n');
        for (const gate of failing) {
            stream.markdown(`- **[${gate.category.toUpperCase()}]** ${gate.name}: ${gate.detail}\n`);
        }
        stream.markdown('\n');
    }
    const errors = findings.filter((f) => f.severity === 'error');
    if (errors.length > 0) {
        stream.markdown('### Doctor errors\n');
        for (const f of errors) {
            stream.markdown(`- **${f.module}**: ${f.message}\n`);
        }
    }
}
async function handleClassify(stream, prompt, modules) {
    const moduleName = prompt.trim() || 'current file';
    const mod = modules.find((m) => prompt.includes(m.name));
    if (!mod) {
        stream.markdown(`Could not find module matching "${moduleName}" in the workspace.\n\n` +
            `Available modules: ${modules.map((m) => m.name).join(', ')}\n`);
        return;
    }
    stream.markdown(`**Module: ${mod.name}**\n\n`);
    stream.markdown(`- Classification: **${mod.classification}**\n`);
    stream.markdown(`- Installable: ${mod.manifest?.installable ?? 'N/A'}\n`);
    stream.markdown(`- Tests: ${mod.hasTests ? `${mod.testFiles.length} files` : 'none'}\n`);
    stream.markdown(`- Models: ${mod.modelFiles.filter((f) => !f.endsWith('__init__.py')).length}\n`);
    stream.markdown(`- Views: ${mod.viewFiles.length}\n`);
    stream.markdown(`- IPAI deps: ${mod.ipaiDeps.join(', ') || 'none'}\n`);
    stream.markdown(`- Used by: ${mod.reverseDeps.join(', ') || 'none'}\n`);
    if (mod.classification === 'bridge') {
        stream.markdown('\n> **Doctrine note:** Bridge modules should contain only config/state in Odoo. ' +
            'HTTP calls to external services should be externalized to Azure Functions.\n');
    }
    if (mod.classification === 'stub') {
        stream.markdown('\n> **Doctrine note:** Stub modules with no models/views are candidates for ' +
            'deletion or absorption into a parent module.\n');
    }
}
async function handleAzure(stream, checks) {
    if (checks.length === 0) {
        stream.markdown('Azure runtime has not been checked yet. Run `IPAI: Run Azure Runtime Smoke` first.\n');
        return;
    }
    const passing = checks.filter((c) => c.status === 'pass');
    const failing = checks.filter((c) => c.status === 'fail');
    stream.markdown(`**Azure Runtime:** ${passing.length} pass, ${failing.length} fail\n\n`);
    for (const check of checks) {
        const icon = check.status === 'pass' ? '✅' : check.status === 'fail' ? '❌' : '⚪';
        stream.markdown(`${icon} **${check.name}** — ${check.detail}\n`);
    }
}
async function handleFreeform(stream, prompt, modules, findings) {
    // Provide context about the workspace state
    const active = modules.filter((m) => m.classification === 'active').length;
    const deprecated = modules.filter((m) => m.classification === 'deprecated').length;
    const withTests = modules.filter((m) => m.hasTests).length;
    const errors = findings.filter((f) => f.severity === 'error').length;
    stream.markdown(`**Workspace context:**\n` +
        `- ${modules.length} total modules (${active} active, ${deprecated} deprecated)\n` +
        `- ${withTests}/${modules.length} have tests\n` +
        `- ${errors} doctor errors\n\n` +
        `For specific commands, try:\n` +
        `- \`@ipai /doctor\` — workspace health\n` +
        `- \`@ipai /blockers\` — release blockers\n` +
        `- \`@ipai /classify <module>\` — classify a module\n` +
        `- \`@ipai /azure\` — runtime health\n`);
}
//# sourceMappingURL=ipaiParticipant.js.map