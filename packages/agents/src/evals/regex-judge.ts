import { BaseJudge, EvalTestCase } from './judge-base.js';
import { AgentPassport } from '../registry/passport.js';

export class RegexJudge extends BaseJudge {
  public readonly judgeId = 'regex-judge-v1';

  async evaluateCase(passport: AgentPassport, testCase: EvalTestCase) {
    // For scaffolding MVP, `testCase.input` represents the mocked agent output
    const input = String(testCase.input);
    const pattern = new RegExp(String(testCase.expected_output), 'i');
    
    const passed = pattern.test(input);

    return {
      score: passed ? 1.0 : 0.0,
      feedback: passed ? 'Match found deterministically' : `Failed to match regex source: ${pattern.source}`
    };
  }
}
