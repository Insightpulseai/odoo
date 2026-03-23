import * as fs from 'fs';
import * as path from 'path';
import { AgentPassport } from './passport.js';

export class AgentRegistry {
  private passportsDir: string;
  
  constructor(passportsDir: string = 'agents/passports') {
    this.passportsDir = passportsDir;
  }

  register(passport: AgentPassport): void {
    const filePath = path.join(this.passportsDir, `${passport.data.id}.yaml`);
    if (fs.existsSync(filePath)) {
      throw new Error(`Agent ${passport.data.id} is already registered.`);
    }
    fs.writeFileSync(filePath, passport.toYAML());
  }

  get(agentId: string): AgentPassport {
    const filePath = path.join(this.passportsDir, `${agentId}.yaml`);
    if (!fs.existsSync(filePath)) {
      throw new Error(`Agent ${agentId} not found in ${this.passportsDir}`);
    }
    return AgentPassport.fromYAML(fs.readFileSync(filePath, 'utf-8'));
  }

  update(agentId: string, updatedPassport: AgentPassport): void {
    const filePath = path.join(this.passportsDir, `${agentId}.yaml`);
    if (!fs.existsSync(filePath)) {
      throw new Error(`Agent ${agentId} not found.`);
    }
    fs.writeFileSync(filePath, updatedPassport.toYAML());
  }

  list(): AgentPassport[] {
    if (!fs.existsSync(this.passportsDir)) return [];
    const files = fs.readdirSync(this.passportsDir).filter(f => f.endsWith('.yaml'));
    return files.map(f => this.get(f.replace('.yaml', '')));
  }

  remove(agentId: string): void {
    const passport = this.get(agentId);
    // Soft remove: set stage to S16 and kill switch to active
    const updatedData = JSON.parse(JSON.stringify(passport.data));
    updatedData.stage = 'S16';
    updatedData.kill_switch = { ...updatedData.kill_switch, active: true, reason: 'Retired' };
    
    const updated = new AgentPassport(updatedData);
    this.update(agentId, updated);
  }
}
