import * as fs from 'fs';
import { StageGateResult } from './gate-engine.js';

export class TransitionLog {
  private logPath: string;

  constructor(logPath: string = 'agents/foundry/gates/transitions.jsonl') {
    this.logPath = logPath;
  }

  log(agentId: string, gateResult: StageGateResult) {
    const entry = {
      agent_id: agentId,
      trigger_time: new Date().toISOString(),
      gate_result: gateResult
    };

    try {
      fs.appendFileSync(this.logPath, JSON.stringify(entry) + '\n');
    } catch (e) {
      console.error('Failed to write to transition log', e);
    }
  }

  getHistory(agentId: string): any[] {
    if (!fs.existsSync(this.logPath)) return [];
    const lines = fs.readFileSync(this.logPath, 'utf8').split('\n').filter(Boolean);
    return lines.map(l => JSON.parse(l)).filter(e => e.agent_id === agentId);
  }
}
