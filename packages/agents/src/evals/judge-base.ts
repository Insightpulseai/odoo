import { EvalResult } from './eval-result.js';
import { AgentPassport } from '../registry/passport.js';

export interface EvalTestCase {
  id: string;
  input: any;
  expected_output: any;
  system_instructions?: string;
}

export interface EvalSuite {
  id: string;
  name: string;
  description: string;
  target_agent_id?: string; // Optional if generic suite
  pass_threshold: number;
  test_cases: EvalTestCase[];
}

export abstract class BaseJudge {
  public abstract readonly judgeId: string;

  /**
   * Executes a single test case against the agent and returns a score [0.0, 1.0].
   */
  abstract evaluateCase(
    passport: AgentPassport,
    testCase: EvalTestCase
  ): Promise<{ score: number; feedback?: string; metadata?: any }>;

  /**
   * Evaluates the entire suite by running individual test cases
   * and aggregating the final score to determine pass/fail.
   */
  async evaluateSuite(passport: AgentPassport, suite: EvalSuite): Promise<EvalResult> {
    if (suite.test_cases.length === 0) {
      throw new Error(`Empty eval suite: ${suite.id}`);
    }

    let totalScore = 0;
    const feedbacks: string[] = [];

    for (const testCase of suite.test_cases) {
      const result = await this.evaluateCase(passport, testCase);
      totalScore += result.score;
      if (result.feedback) feedbacks.push(`[${testCase.id}]: ${result.feedback}`);
    }

    const averageScore = totalScore / suite.test_cases.length;
    const passed = averageScore >= suite.pass_threshold;

    return EvalResult.create({
      agent_id: passport.data.id,
      suite_id: suite.id,
      judge_id: this.judgeId,
      score: averageScore,
      passed,
      feedback: feedbacks.join('\n')
    });
  }
}
