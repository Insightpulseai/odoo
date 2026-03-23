import { Command } from 'commander';
import { AgentRegistry } from '../registry/registry.js';
import { RegistryIndex } from '../registry/registry-index.js';
import { searchAgents } from '../registry/search.js';
import { AgentPassport } from '../registry/passport.js';
import { validatePassportDetails } from '../registry/passport-validator.js';
import { StageGateEngine } from '../stages/gate-engine.js';
import { TransitionLog } from '../stages/transition-log.js';
import { EvalRunner } from '../evals/runner.js';
import { EvalMetricsAggregator } from '../evals/metrics.js';
import { FoundrySupervisor } from '../foundry/supervisor.js';
import { TransitionWorker } from '../foundry/transition-worker.js';
import { PassportVersioner } from '../registry/passport-version.js';
import { FoundryExporter } from '../foundry/exporter.js';
import { runCIValidation } from '../foundry/ci-runner.js';
import * as fs from 'fs';

const program = new Command();
program.name('agents').description('InsightPulse AI Agent Registry CLI').version('0.1.0');

const registry = new AgentRegistry('agents/passports');
const index = new RegistryIndex(registry);
try {
  index.build();
} catch (e) {
  // Gracefully handle missing directory on first run
}

program.command('list')
  .description('List all registered agents')
  .action(() => {
    const agents = index.getAll();
    console.table(agents.map(a => ({
      ID: a.data.id,
      Domain: a.data.domain,
      Stage: a.currentStage(),
      Maturity: a.maturityLevel()
    })));
  });

program.command('get')
  .description('Get agent passport by ID')
  .argument('<id>', 'Agent ID')
  .action((id) => {
    try {
      const agent = registry.get(id);
      console.log(agent.toYAML());
    } catch (e) {
      console.error(e.message);
    }
  });

program.command('validate')
  .description('Validate a passport file deeply')
  .argument('<filepath>', 'Path to passport YAML')
  .action((filepath) => {
    try {
      const raw = fs.readFileSync(filepath, 'utf8');
      const passport = AgentPassport.fromYAML(raw);
      const result = validatePassportDetails(passport);
      if (result.valid) {
         console.log('✅ Passport is valid');
      } else {
         console.log('❌ Passport validation failed:');
         result.errors.forEach(e => console.log(`  - ${e}`));
      }
    } catch (e) {
      console.error('Schema parsing or validation failed:', e.message);
    }
  });

program.command('search')
  .description('Search agents by criteria')
  .option('-d, --domain <domain>', 'Filter by domain')
  .option('-s, --stage <stage>', 'Filter by stage')
  .action((options) => {
    const results = searchAgents(index, options);
    console.table(results.map(a => ({
      ID: a.data.id,
      Stage: a.currentStage()
    })));
  });

const stagesCmd = program.command('stages').description('Manage and inspect agent lifecycle stages');

stagesCmd.command('list')
  .description('List all agents grouped by stage')
  .action(() => {
     const agents = index.getAll();
     const grouped = agents.reduce((acc, a) => {
       const stage = a.currentStage();
       acc[stage] = acc[stage] || [];
       acc[stage].push(a.data.id);
       return acc;
     }, {} as Record<string, string[]>);
     console.log(JSON.stringify(grouped, null, 2));
  });

stagesCmd.command('check')
  .description('Check gate status for next stage')
  .argument('<id>', 'Agent ID')
  .argument('<target-stage>', 'Target stage (e.g. S04)')
  .action(async (id, target) => {
     try {
       const agent = registry.get(id);
       const engine = new StageGateEngine();
       const result = await engine.evaluate(agent, target);
       console.log(`Gate ${result.gate_id} Result: ${result.overall_result}`);
       console.table(result.criteria);
     } catch (e) {
       console.error('Gate check failed:', e.message);
     }
  });

stagesCmd.command('history')
  .description('View stage transition history')
  .argument('<id>', 'Agent ID')
  .action((id) => {
     const log = new TransitionLog();
     const history = log.getHistory(id);
     console.table(history.map(h => ({
       Time: h.trigger_time,
       Gate: h.gate_result.gate_id,
       Result: h.gate_result.overall_result
     })));
  });

const evalCmd = program.command('eval').description('Run and inspect agent evaluations');

evalCmd.command('run')
  .description('Run an eval suite against an agent')
  .argument('<agent-id>', 'ID of the agent to test')
  .argument('<suite-path>', 'Path to the YAML suite file')
  .action(async (agentId, suitePath) => {
    try {
      const agent = registry.get(agentId);
      const runner = new EvalRunner();
      
      console.log(`Running suite ${suitePath} on agent ${agentId}...`);
      const result = await runner.run(agent, suitePath);
      
      console.log(`\nEval execution complete!`);
      console.log(`Passed: ${result.data.passed ? '✅ YES' : '❌ NO'}`);
      console.log(`Score:  ${(result.data.score * 100).toFixed(1)}%`);
      console.log(`Feedback:\n${result.data.feedback}`);

    } catch(e: any) {
      console.error('Eval run failed:', e.message);
    }
  });

evalCmd.command('report')
  .description('View historical metric aggregates for an agent')
  .argument('<agent-id>', 'ID of the agent')
  .action((id) => {
    const aggregator = new EvalMetricsAggregator();
    const metrics = aggregator.getMetrics(id);
    console.table([metrics]);
  });

program.parse();
