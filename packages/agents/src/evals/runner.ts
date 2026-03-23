import * as yaml from 'js-yaml';
import * as fs from 'fs';
import * as path from 'path';
import { BaseJudge, EvalSuite } from './judge-base.js';
import { LLMJudge } from './llm-judge.js';
import { AgentPassport } from '../registry/passport.js';
import { EvalResult, EvalResultData } from './eval-result.js';
import { EvalMetricsAggregator } from './metrics.js';

export class EvalRunner {
  private judges = new Map<string, BaseJudge>();
  private defaultJudge = new LLMJudge();
  public metrics = new EvalMetricsAggregator();
  private ssotConfig: any;

  constructor() {
    this.judges.set(this.defaultJudge.judgeId, this.defaultJudge);
    const ssotPath = path.resolve(process.cwd(), 'ssot/agents/eval_engine.yaml');
    try {
      this.ssotConfig = yaml.load(fs.readFileSync(ssotPath, 'utf8'));
    } catch {
      this.ssotConfig = { thresholds: { confidence_min: 0.8, required_evidence_refs: true } };
    }
  }

  loadSuite(filePath: string): EvalSuite {
    const raw = fs.readFileSync(filePath, 'utf8');
    return yaml.load(raw) as EvalSuite;
  }

  async run(passport: AgentPassport, suiteDesc: string | EvalSuite, judgeId?: string): Promise<EvalResult> {
    this.metrics.record('eval_requests_total');
    const suite = typeof suiteDesc === 'string' ? this.loadSuite(suiteDesc) : suiteDesc;
    const judge = (judgeId ? this.judges.get(judgeId) : this.defaultJudge) || this.defaultJudge;

    let result: EvalResult;
    try {
      result = await Promise.race([
        judge.evaluateSuite(passport, suite),
        new Promise<EvalResult>((_, reject) => setTimeout(() => reject(new Error('timeout')), 5000))
      ]);
    } catch (e: any) {
      if (e.message === 'timeout') {
         this.metrics.record('eval_fail_timeout_total');
      } else {
         this.metrics.record('eval_fail_malformed_total');
      }
      return this.failClosed(passport.data.id, 'ambiguous', 'timeout or malformed boundary failure');
    }

    if (result.data.decision === 'ambiguous') {
      this.metrics.record('eval_fail_ambiguity_total');
      return this.failClosed(passport.data.id, 'ambiguous', 'LLM output ambiguous');
    }

    if (result.data.confidence < this.ssotConfig.thresholds.confidence_min) {
      this.metrics.record('eval_fail_explicit_total');
      return this.failClosed(passport.data.id, 'fail', 'Confidence below explicit SSOT threshold');
    }

    if (this.ssotConfig.thresholds.required_evidence_refs && (!result.data.evidence_refs || result.data.evidence_refs.length === 0)) {
      this.metrics.record('eval_fail_explicit_total');
      return this.failClosed(passport.data.id, 'fail', 'No explicit evidence refs provided');
    }

    if (result.data.decision === 'pass') {
      this.metrics.record('eval_success_total');
    } else {
      this.metrics.record('eval_fail_explicit_total');
    }

    return result;
  }

  private failClosed(agent_id: string, decision: 'fail' | 'ambiguous', reason: string): EvalResult {
    return EvalResult.create({
      agent_id,
      target_stage: 'quarantine',
      judge_id: 'runner-fail-closed',
      decision,
      confidence: 1.0,
      reasoning: reason,
      evidence_refs: []
    });
  }
}
