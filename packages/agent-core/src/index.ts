/**
 * Agent Core — Plan/Apply/Verify Loop
 *
 * Provides the core agent loop abstraction for remediation workflows.
 * Pluggable into Claude, Codex, Gemini, or local models.
 */

// ============================================================================
// Types
// ============================================================================

export interface PlanInput {
  title: string;
  context: {
    pr_url?: string;
    failing_checks?: string[];
    diff?: string;
    logs?: string;
    [key: string]: unknown;
  };
}

export interface PatchStep {
  kind: "edit" | "command" | "comment";
  file?: string;
  old_content?: string;
  new_content?: string;
  command?: string;
  message?: string;
}

export interface PatchPlan {
  summary: string;
  confidence: number; // 0-1
  steps: PatchStep[];
  reasoning?: string;
}

export interface ApplyResult {
  success: boolean;
  steps_applied: number;
  steps_failed: number;
  errors: string[];
  commit_sha?: string;
}

export interface VerifyResult {
  success: boolean;
  checks_passed: string[];
  checks_failed: string[];
  logs?: string;
}

export interface AgentLoop {
  plan(input: PlanInput): Promise<PatchPlan>;
  apply(plan: PatchPlan, context: PlanInput): Promise<ApplyResult>;
  verify(context: PlanInput): Promise<VerifyResult>;
}

// ============================================================================
// Stub Implementation (v0.1)
// ============================================================================

/**
 * Naive planner - returns stub plan for testing.
 * Real implementation connects to Claude/Codex/Gemini.
 */
export function naivePlan(input: PlanInput): PatchPlan {
  return {
    summary: `Stub plan for: ${input.title}`,
    confidence: 0.1,
    steps: [
      {
        kind: "command",
        command: "echo 'TODO: implement real remediation logic'",
      },
    ],
    reasoning: "This is a stub implementation. Replace with actual LLM integration.",
  };
}

/**
 * Create a basic agent loop with stub implementations.
 * Override individual methods for real functionality.
 */
export function createAgentLoop(overrides?: Partial<AgentLoop>): AgentLoop {
  return {
    async plan(input: PlanInput): Promise<PatchPlan> {
      if (overrides?.plan) {
        return overrides.plan(input);
      }
      return naivePlan(input);
    },

    async apply(plan: PatchPlan, _context: PlanInput): Promise<ApplyResult> {
      if (overrides?.apply) {
        return overrides.apply(plan, _context);
      }

      // Stub: pretend all steps succeeded
      return {
        success: true,
        steps_applied: plan.steps.length,
        steps_failed: 0,
        errors: [],
      };
    },

    async verify(_context: PlanInput): Promise<VerifyResult> {
      if (overrides?.verify) {
        return overrides.verify(_context);
      }

      // Stub: pretend verification passed
      return {
        success: true,
        checks_passed: ["stub-check"],
        checks_failed: [],
      };
    },
  };
}

// ============================================================================
// Prompt Templates
// ============================================================================

export const PROMPTS = {
  /**
   * System prompt for CI remediation agent
   */
  CI_REMEDIATION: `You are a CI remediation agent. Your job is to analyze failing CI checks and propose minimal fixes.

Rules:
1. Only fix what's broken - don't refactor or improve unrelated code
2. Prefer the smallest possible change
3. Explain your reasoning
4. If unsure, ask for clarification rather than guessing

Output format:
{
  "summary": "Brief description of the fix",
  "confidence": 0.0-1.0,
  "steps": [
    {"kind": "edit", "file": "path/to/file", "old_content": "...", "new_content": "..."},
    {"kind": "command", "command": "npm run lint -- --fix"}
  ],
  "reasoning": "Why this fix is correct"
}`,

  /**
   * User prompt template for lint failures
   */
  LINT_FAILURE: (files: string[], logs: string) => `
The following lint checks are failing:

Files with issues:
${files.join("\n")}

Lint output:
\`\`\`
${logs}
\`\`\`

Please analyze the errors and propose fixes.
`,

  /**
   * User prompt template for test failures
   */
  TEST_FAILURE: (testName: string, logs: string) => `
The following test is failing: ${testName}

Test output:
\`\`\`
${logs}
\`\`\`

Please analyze the failure and propose a fix.
`,
};

// ============================================================================
// Utilities
// ============================================================================

/**
 * Parse CI logs to extract failing checks
 */
export function parseFailingChecks(logs: string): string[] {
  const checks: string[] = [];

  // Common patterns for failing checks
  const patterns = [
    /^FAIL\s+(.+)$/gm, // Jest
    /^ERROR:\s+(.+)$/gm, // Generic
    /^E\s+(.+)$/gm, // pytest
    /^✖\s+(.+)$/gm, // eslint
  ];

  for (const pattern of patterns) {
    let match;
    while ((match = pattern.exec(logs)) !== null) {
      checks.push(match[1].trim());
    }
  }

  return [...new Set(checks)];
}

/**
 * Extract file paths from diff or error logs
 */
export function extractFilePaths(content: string): string[] {
  const paths: string[] = [];

  // Common patterns
  const patterns = [
    /^diff --git a\/(.+) b\//gm, // Git diff
    /^--- a\/(.+)$/gm, // Diff headers
    /^\+\+\+ b\/(.+)$/gm,
    /File: (.+\.(?:ts|js|py|go|rs))(?::|$)/gm, // Error locations
    /at (.+\.(?:ts|js|py)):(\d+)/gm, // Stack traces
  ];

  for (const pattern of patterns) {
    let match;
    while ((match = pattern.exec(content)) !== null) {
      const path = match[1].trim();
      if (path && !path.startsWith("/dev/null")) {
        paths.push(path);
      }
    }
  }

  return [...new Set(paths)];
}
