import { AgentRegistry } from '../registry/registry.js';
import { StageGateEngine } from '../stages/gate-engine.js';
import * as process from 'process';

export async function runCIValidation(agentId: string, targetStage: string) {
  const registry = new AgentRegistry('agents/passports');
  const engine = new StageGateEngine();

  try {
    let passport;
    try {
      passport = registry.get(agentId);
    } catch (e) {
      console.error(`[CI RUNNER] ❌ UNKNOWN AGENT: ${agentId}`);
      process.exit(1);
    }

    console.log(`[CI RUNNER] Validating Agent: ${agentId} targeting Stage: ${targetStage}...`);
    
    const result = await engine.evaluate(passport, targetStage);
    
    if (result.overall_result === 'pass') {
      console.log(`[CI RUNNER] ✅ Agent passed gate validation perfectly.`);
      process.exit(0);
    } else {
      console.log(`[CI RUNNER] ❌ Agent failed gate validation.`);
      console.table(result.criteria);
      process.exit(1);
    }
  } catch (e: any) {
    console.error(`[CI RUNNER] 🚨 Fatal validation exception:`, e.message);
    process.exit(1);
  }
}
