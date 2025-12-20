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

  /**
   * System prompt for merge conflict resolution
   */
  MERGE_CONFLICT: `You are a merge conflict resolution agent. Your job is to analyze git merge conflicts and propose resolutions.

Rules:
1. Understand the intent of both sides (ours vs theirs)
2. Preserve functionality from both branches when possible
3. If in doubt, prefer the base branch version and flag for human review
4. Never silently drop changes - explain every decision
5. Maintain code style consistency

Output format:
{
  "summary": "Brief description of the resolution",
  "confidence": 0.0-1.0,
  "steps": [
    {"kind": "edit", "file": "path/to/file", "old_content": "<<<<<<< HEAD\\n...\\n=======\\n...\\n>>>>>>>", "new_content": "resolved code"}
  ],
  "reasoning": "Why this resolution is correct",
  "human_review_needed": true/false,
  "review_notes": "What the human should verify"
}`,

  /**
   * User prompt template for merge conflicts
   */
  CONFLICT_RESOLUTION: (file: string, conflictContent: string, baseBranch: string, headBranch: string) => `
Merge conflict detected in: ${file}

Base branch: ${baseBranch}
Head branch: ${headBranch}

Conflict markers:
\`\`\`
${conflictContent}
\`\`\`

Please analyze the conflict and propose a resolution that:
1. Preserves functionality from both branches
2. Maintains code consistency
3. Explains the reasoning
`,

  /**
   * System prompt for code review feedback resolution
   */
  REVIEW_FEEDBACK: `You are a code review feedback agent. Your job is to analyze review comments and implement the requested changes.

Rules:
1. Address each review comment specifically
2. Prefer the smallest change that satisfies the reviewer
3. If a comment is unclear, note it but don't guess
4. Maintain existing code style
5. Add tests if the reviewer requested them

Output format:
{
  "summary": "Brief description of changes made",
  "confidence": 0.0-1.0,
  "steps": [
    {"kind": "edit", "file": "path/to/file", "old_content": "...", "new_content": "..."}
  ],
  "reasoning": "How each comment was addressed",
  "unresolved_comments": ["Comments that need clarification"]
}`,

  /**
   * User prompt template for review comments
   */
  ADDRESS_REVIEW: (comments: Array<{ file: string; line: number; body: string }>) => `
The following review comments need to be addressed:

${comments.map((c, i) => `${i + 1}. ${c.file}:${c.line}
   "${c.body}"
`).join("\n")}

Please analyze each comment and propose changes to address them.
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

/**
 * Parse git merge conflict markers from file content
 */
export interface ConflictBlock {
  file: string;
  startLine: number;
  endLine: number;
  ours: string;
  theirs: string;
  raw: string;
}

export function parseConflictMarkers(content: string, fileName: string = "unknown"): ConflictBlock[] {
  const conflicts: ConflictBlock[] = [];
  const lines = content.split("\n");

  let inConflict = false;
  let startLine = 0;
  let oursLines: string[] = [];
  let theirsLines: string[] = [];
  let inTheirs = false;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    if (line.startsWith("<<<<<<< ")) {
      inConflict = true;
      inTheirs = false;
      startLine = i + 1;
      oursLines = [];
      theirsLines = [];
    } else if (line.startsWith("=======") && inConflict) {
      inTheirs = true;
    } else if (line.startsWith(">>>>>>> ") && inConflict) {
      conflicts.push({
        file: fileName,
        startLine,
        endLine: i + 1,
        ours: oursLines.join("\n"),
        theirs: theirsLines.join("\n"),
        raw: lines.slice(startLine - 1, i + 1).join("\n"),
      });
      inConflict = false;
      inTheirs = false;
    } else if (inConflict) {
      if (inTheirs) {
        theirsLines.push(line);
      } else {
        oursLines.push(line);
      }
    }
  }

  return conflicts;
}

/**
 * Check if file has unresolved merge conflicts
 */
export function hasConflictMarkers(content: string): boolean {
  return /^<<<<<<<\s/m.test(content) && /^>>>>>>>\s/m.test(content);
}

/**
 * Parse review comments from GitHub API response
 */
export interface ReviewComment {
  id: number;
  file: string;
  line: number;
  body: string;
  author: string;
  createdAt: string;
}

export function parseReviewComments(
  comments: Array<{
    id: number;
    path: string;
    line?: number;
    original_line?: number;
    body: string;
    user?: { login: string };
    created_at: string;
  }>
): ReviewComment[] {
  return comments.map((c) => ({
    id: c.id,
    file: c.path,
    line: c.line || c.original_line || 0,
    body: c.body,
    author: c.user?.login || "unknown",
    createdAt: c.created_at,
  }));
}

/**
 * Group review comments by file
 */
export function groupCommentsByFile(comments: ReviewComment[]): Map<string, ReviewComment[]> {
  const grouped = new Map<string, ReviewComment[]>();

  for (const comment of comments) {
    const existing = grouped.get(comment.file) || [];
    existing.push(comment);
    grouped.set(comment.file, existing);
  }

  return grouped;
}

/**
 * Determine remediation type from work item payload
 */
export type RemediationType = "ci_failure" | "merge_conflict" | "review_feedback" | "manual";

export function detectRemediationType(payload: Record<string, unknown>): RemediationType {
  if (payload.conflict_type === "merge_conflict") {
    return "merge_conflict";
  }
  if (payload.feedback_type === "changes_requested") {
    return "review_feedback";
  }
  if (payload.check_suite_id || payload.workflow_run_id || payload.failing_checks) {
    return "ci_failure";
  }
  return "manual";
}
