import { AgentPassport, AgentPassportData } from '../registry/passport.js';

export class PassportBuilder {
  static createNewAgent(id: string, name: string, domain: string, owners: string[]): AgentPassport {
    const data: AgentPassportData = {
      schema: 'ipai.passport.v1',
      id,
      version: '0.1.0',
      name,
      domain,
      stage: 'S01',
      maturity: 'L0',
      contract_ref: `agents/contracts/${id}.manifest.yaml`,
      skills: [],
      kill_switch: { enabled: false },
      owners,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };
    return new AgentPassport(data);
  }
}
