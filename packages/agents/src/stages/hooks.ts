import { AgentPassport } from '../registry/passport.js';

export type StageHook = (passport: AgentPassport) => Promise<void>;

export class StageHookRegistry {
  private enterHooks = new Map<string, StageHook[]>();
  private exitHooks = new Map<string, StageHook[]>();

  registerEnter(stageId: string, hook: StageHook) {
    if (!this.enterHooks.has(stageId)) this.enterHooks.set(stageId, []);
    this.enterHooks.get(stageId)!.push(hook);
  }

  registerExit(stageId: string, hook: StageHook) {
    if (!this.exitHooks.has(stageId)) this.exitHooks.set(stageId, []);
    this.exitHooks.get(stageId)!.push(hook);
  }

  async triggerEnter(stageId: string, passport: AgentPassport) {
    const hooks = this.enterHooks.get(stageId) || [];
    for (const hook of hooks) {
      await hook(passport);
    }
  }

  async triggerExit(stageId: string, passport: AgentPassport) {
    const hooks = this.exitHooks.get(stageId) || [];
    for (const hook of hooks) {
      await hook(passport);
    }
  }
}
