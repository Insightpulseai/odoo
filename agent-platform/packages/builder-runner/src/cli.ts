#!/usr/bin/env node

/**
 * CLI runner for the agent platform.
 *
 * Commands:
 *   chat <prompt>    — Execute a single precursor request
 *   health           — Check Foundry client health
 *   eval             — Run eval dataset against runtime
 *   status           — Show deployment readiness status
 */

import { randomUUID } from 'node:crypto';
import { resolve } from 'node:path';
import { defaultContextEnvelope } from '@ipai/builder-contract';
import type { PrecursorRequest } from '@ipai/builder-contract';
import { MockFoundryClient, AzureFoundryClient } from '@ipai/builder-foundry-client';
import { Orchestrator } from '@ipai/builder-orchestrator';
import { runEvals, generateEvidencePack } from '@ipai/builder-evals';

async function main(): Promise<void> {
  const args = process.argv.slice(2);
  const command = args[0];

  if (!command) {
    console.log('Usage: builder-runner <command> [args]');
    console.log('Commands: chat, health, eval, status');
    process.exit(1);
  }

  // Resolve agents/ root (sibling directory to agent-platform/)
  const agentsRoot = resolve(process.env['AGENTS_ROOT'] ?? resolve(__dirname, '../../../../agents'));

  // Select Foundry client based on environment
  const useAzure = process.env['AZURE_AI_FOUNDRY_ENDPOINT'];
  const foundryClient = useAzure ? new AzureFoundryClient() : new MockFoundryClient();

  const orchestrator = new Orchestrator({
    agentsRoot,
    agentProfile: 'ipai-odoo-copilot-azure',
    foundryClient,
  });

  await orchestrator.initialize();

  switch (command) {
    case 'chat': {
      const prompt = args.slice(1).join(' ') || 'What is InsightPulseAI Odoo Copilot?';
      const request: PrecursorRequest = {
        request_id: randomUUID(),
        timestamp: new Date().toISOString(),
        prompt,
        context: defaultContextEnvelope(),
        channel: 'api',
      };

      const response = await orchestrator.execute(request);
      console.log('\n--- Response ---');
      console.log(response.content);
      console.log('\n--- Metadata ---');
      console.log(`Request ID: ${response.request_id}`);
      console.log(`Blocked: ${response.blocked}`);
      console.log(`Latency: ${response.latency_ms}ms`);
      console.log(`Tool calls: ${response.tool_calls.length}`);
      break;
    }

    case 'health': {
      const healthy = await foundryClient.healthCheck();
      console.log(`Foundry client: ${foundryClient.name}`);
      console.log(`Configured: ${foundryClient.isConfigured()}`);
      console.log(`Healthy: ${healthy}`);
      process.exit(healthy ? 0 : 1);
      break;
    }

    case 'eval': {
      console.log('Running eval suite...');
      const result = await runEvals({
        agentsRoot,
        orchestrator,
        outputDir: resolve(__dirname, '../../../../agent-platform/eval-results'),
      });
      console.log(generateEvidencePack(result));
      process.exit(result.summary.failed > 0 ? 1 : 0);
      break;
    }

    case 'status': {
      console.log('=== Deployment Readiness Status ===');
      console.log(`Foundry client: ${foundryClient.name} (configured: ${foundryClient.isConfigured()})`);
      console.log(`Agent profile: ipai-odoo-copilot-azure`);
      console.log(`Agents root: ${agentsRoot}`);

      const specialists = orchestrator.getPolicyEngine().createSpecialistRouter().listSpecialists();
      console.log(`Registered specialists: ${specialists.length}`);

      // Register known blockers
      const taxRouter = orchestrator.getPolicyEngine().createSpecialistRouter();
      taxRouter.register({
        domain: 'tax-compliance',
        agent_id: 'taxpulse-v0',
        version: '0.0.0',
        capabilities: ['bir-filing', 'withholding-tax'],
        production_ready: false,
        blockers: ['ATC namespace divergence unresolved', 'No eval corpus for tax specialist'],
      });

      const taxRoute = taxRouter.route('compute withholding tax for this vendor bill', {});
      console.log(`\nTax specialist routing test:`);
      console.log(`  Should route: ${taxRoute.should_route}`);
      console.log(`  Block reason: ${taxRoute.block_reason ?? 'none'}`);
      console.log(`  Fail-closed: ${!taxRoute.should_route ? 'YES (correct)' : 'NO (needs investigation)'}`);

      console.log('\n=== Cloud Blockers ===');
      console.log('- [ ] AZURE_AI_FOUNDRY_ENDPOINT not set (using MockFoundryClient)');
      console.log('- [ ] Managed identity not configured');
      console.log('- [ ] AI Search index not populated');
      console.log('- [ ] App Insights not connected');
      console.log('- [ ] ATC namespace divergence blocks autonomous tax operations');
      break;
    }

    default:
      console.error(`Unknown command: ${command}`);
      process.exit(1);
  }
}

export { main };

main().catch((err) => {
  console.error('Fatal error:', err);
  process.exit(1);
});
