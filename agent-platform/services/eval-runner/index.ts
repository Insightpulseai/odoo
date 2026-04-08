// Eval Runner — executes evaluation suites against agent outputs
// TODO: Implement eval suite loading and assertion execution

export interface EvalSuite {
  name: string;
  agentId: string;
  assertions: EvalAssertion[];
}

export interface EvalAssertion {
  id: string;
  input: unknown;
  expectedOutput: unknown;
  comparator: "exact" | "contains" | "schema" | "judge";
}

export interface EvalResult {
  suiteName: string;
  passed: number;
  failed: number;
  results: { assertionId: string; pass: boolean; detail?: string }[];
  timestamp: string;
}

export class EvalRunner {
  async run(suite: EvalSuite): Promise<EvalResult> {
    // TODO: Iterate assertions, invoke agent, compare results
    // TODO: Support judge-based evaluation via Foundry models
    throw new Error("NotImplemented: eval runner");
  }
}
