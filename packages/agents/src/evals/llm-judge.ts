import { BaseJudge, EvalTestCase, EvalSuite } from './judge-base.js';
import { AgentPassport } from '../registry/passport.js';
import { EvalResult, EvalResultData } from './eval-result.js';

export class LLMJudge extends BaseJudge {
  public readonly judgeId = 'llm-judge-v1';

  async evaluateSuite(passport: AgentPassport, suite: EvalSuite): Promise<EvalResult> {
    const mockLLMResponse = `
    {
      "agent_id": "${passport.data.id}",
      "target_stage": "S04",
      "judge_id": "${this.judgeId}",
      "decision": "pass",
      "confidence": 0.95,
      "reasoning": "Agent clearly followed instructions.",
      "evidence_refs": ["unit_tests_exist", "linting_pass"]
    }
    `;

    try {
      const parsed = JSON.parse(mockLLMResponse.trim());
      // Structural parsing explicitly enforced by throwing if missing fields 
      return EvalResult.create(parsed as EvalResultData);
    } catch (e) {
      // Malformed output strictly throws to Runner for fail-close
      throw new Error(`LLM output malformed: ${(e as Error).message}`);
    }
  }

  async evaluateCase(passport: AgentPassport, testCase: EvalTestCase) {
    return { score: 0, feedback: '' }; // legacy stub
  }
}
