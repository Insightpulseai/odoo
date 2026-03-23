import { AgentPassport } from './passport.js';
import * as fs from 'fs';
import * as path from 'path';

export class PassportVersioner {
  private historyDir: string;

  constructor(historyDir: string = 'agents/passports/history') {
    this.historyDir = historyDir;
    if (!fs.existsSync(this.historyDir)) {
      fs.mkdirSync(this.historyDir, { recursive: true });
    }
  }

  bumpVersion(passport: AgentPassport, changeType: 'major' | 'minor' | 'patch'): AgentPassport {
    const oldVersion = passport.data.version || '0.1.0';
    const parts = oldVersion.replace('v', '').split('.').map(Number);
    let [major, minor, patch] = parts.length === 3 ? parts : [0, 1, 0];

    if (changeType === 'major') { major++; minor = 0; patch = 0; }
    else if (changeType === 'minor') { minor++; patch = 0; }
    else { patch++; }

    const newVersion = `${major}.${minor}.${patch}`;

    // Archive old version
    const agentDir = path.join(this.historyDir, passport.data.id);
    if (!fs.existsSync(agentDir)) {
      fs.mkdirSync(agentDir, { recursive: true });
    }
    fs.writeFileSync(path.join(agentDir, `v${oldVersion}.yaml`), passport.toYAML());

    // Create new passport instance
    const newData = JSON.parse(JSON.stringify(passport.data));
    newData.version = newVersion;
    newData.updated_at = new Date().toISOString();

    return new AgentPassport(newData);
  }
}
