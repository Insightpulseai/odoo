import { Command } from 'commander';
import { TaskEnvelope } from './task-envelope.js';
import { InMemoryTaskQueue } from './queue.js';
import { RoutingRulesEngine } from './routing-rules.js';
import { taskBusHealth } from './health.js';
import * as fs from 'fs';

const program = new Command();
program.name('taskbus').description('InsightPulse AI Task Bus CLI').version('0.1.0');

// Mock state for CLI purposes
const queue = new InMemoryTaskQueue();
const rules = new RoutingRulesEngine();

program.command('submit')
  .description('Submit a new task to the bus')
  .argument('<type>', 'The task type (e.g. task.odoo.lint)')
  .argument('<payload-json>', 'JSON string of the task payload')
  .action((type, payloadJson) => {
    try {
      const payload = JSON.parse(payloadJson);
      const envelope = TaskEnvelope.create({ type, payload, correlation_id: 'sys-cli-root' });
      queue.enqueue(envelope, 2);
      console.log(`Successfully submitted task: ${envelope.id}`);
    } catch (e) {
      console.error('Failed to submit task:', e);
    }
  });

program.command('health')
  .description('Check task bus health')
  .action(() => {
    const health = taskBusHealth(queue, rules);
    console.table(health);
  });

program.command('queue')
  .description('View current queue size')
  .action(() => {
    console.log(`Current queue depth: ${queue.size()}`);
  });

program.command('status')
  .description('Get task status')
  .argument('<task-id>', 'ID of the task')
  .action((taskId) => {
    console.log(`Status for ${taskId}: checking... (Not fully implemented in MVP CLI)`);
  });

program.command('dead-letter')
  .description('View dead letter logs')
  .action(() => {
    try {
      const logs = fs.readFileSync('agents/foundry/dead-letter.jsonl', 'utf-8');
      console.log(logs);
    } catch(e) {
      console.log('No dead-letter tasks found (file missing/empty).');
    }
  });

program.parse();
