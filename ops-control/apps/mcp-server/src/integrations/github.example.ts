/**
 * Example: Real GitHub Integration
 * 
 * Shows how to create PRs, trigger Actions, and fetch logs.
 */

import type { RunEvent } from "@ops-control-room/core";

interface GitHubPR {
  number: number;
  html_url: string;
  state: "open" | "closed";
  title: string;
}

interface GitHubWorkflowRun {
  id: number;
  status: "queued" | "in_progress" | "completed";
  conclusion: "success" | "failure" | "cancelled" | null;
  html_url: string;
}

/**
 * Create a GitHub pull request
 */
export async function* createGitHubPR(
  owner: string,
  repo: string,
  title: string,
  body: string,
  headBranch: string,
  baseBranch: string = "main"
): AsyncGenerator<RunEvent> {
  const GITHUB_TOKEN = process.env.GITHUB_TOKEN;
  
  if (!GITHUB_TOKEN) {
    yield {
      ts: new Date().toISOString(),
      level: "error",
      source: "GitHub",
      message: "GITHUB_TOKEN not configured"
    };
    return;
  }

  yield {
    ts: new Date().toISOString(),
    level: "info",
    source: "GitHub",
    message: `Creating pull request: ${title}...`
  };

  try {
    const response = await fetch(
      `https://api.github.com/repos/${owner}/${repo}/pulls`,
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${GITHUB_TOKEN}`,
          "Content-Type": "application/json",
          Accept: "application/vnd.github.v3+json"
        },
        body: JSON.stringify({
          title,
          body,
          head: headBranch,
          base: baseBranch
        })
      }
    );

    if (!response.ok) {
      const error = await response.text();
      yield {
        ts: new Date().toISOString(),
        level: "error",
        source: "GitHub",
        message: `PR creation failed: ${error}`
      };
      return;
    }

    const pr: GitHubPR = await response.json();

    yield {
      ts: new Date().toISOString(),
      level: "success",
      source: "GitHub",
      message: `✓ PR created: #${pr.number} '${pr.title}'`,
      data: {
        pr_number: pr.number,
        pr_url: pr.html_url,
        branch: headBranch
      }
    };

  } catch (error) {
    yield {
      ts: new Date().toISOString(),
      level: "error",
      source: "GitHub",
      message: `PR creation error: ${error instanceof Error ? error.message : "Unknown error"}`,
      data: { error: String(error) }
    };
  }
}

/**
 * Trigger a GitHub Actions workflow
 */
export async function* triggerGitHubWorkflow(
  owner: string,
  repo: string,
  workflowId: string, // e.g., "deploy.yml"
  ref: string = "main",
  inputs?: Record<string, string>
): AsyncGenerator<RunEvent> {
  const GITHUB_TOKEN = process.env.GITHUB_TOKEN;
  
  if (!GITHUB_TOKEN) {
    yield {
      ts: new Date().toISOString(),
      level: "error",
      source: "GitHub",
      message: "GITHUB_TOKEN not configured"
    };
    return;
  }

  yield {
    ts: new Date().toISOString(),
    level: "info",
    source: "GitHub",
    message: `Triggering workflow: ${workflowId} on ${ref}...`
  };

  try {
    const response = await fetch(
      `https://api.github.com/repos/${owner}/${repo}/actions/workflows/${workflowId}/dispatches`,
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${GITHUB_TOKEN}`,
          "Content-Type": "application/json",
          Accept: "application/vnd.github.v3+json"
        },
        body: JSON.stringify({
          ref,
          inputs: inputs || {}
        })
      }
    );

    if (!response.ok) {
      const error = await response.text();
      yield {
        ts: new Date().toISOString(),
        level: "error",
        source: "GitHub",
        message: `Workflow trigger failed: ${error}`
      };
      return;
    }

    yield {
      ts: new Date().toISOString(),
      level: "success",
      source: "GitHub",
      message: `✓ Workflow triggered: ${workflowId}`,
      data: { workflow: workflowId, ref }
    };

    // Wait a bit for the run to start
    await new Promise(resolve => setTimeout(resolve, 2000));

    // Get the latest run
    const runsResponse = await fetch(
      `https://api.github.com/repos/${owner}/${repo}/actions/workflows/${workflowId}/runs?per_page=1`,
      {
        headers: {
          Authorization: `Bearer ${GITHUB_TOKEN}`,
          Accept: "application/vnd.github.v3+json"
        }
      }
    );

    const runsData = await runsResponse.json();
    const run: GitHubWorkflowRun | undefined = runsData.workflow_runs?.[0];

    if (run) {
      yield {
        ts: new Date().toISOString(),
        level: "info",
        source: "GitHub",
        message: `Workflow run started: ${run.html_url}`,
        data: { run_id: run.id, run_url: run.html_url }
      };

      // Poll for completion (optional)
      yield* pollWorkflowRun(owner, repo, run.id);
    }

  } catch (error) {
    yield {
      ts: new Date().toISOString(),
      level: "error",
      source: "GitHub",
      message: `Workflow trigger error: ${error instanceof Error ? error.message : "Unknown error"}`,
      data: { error: String(error) }
    };
  }
}

/**
 * Poll a workflow run until completion
 */
async function* pollWorkflowRun(
  owner: string,
  repo: string,
  runId: number
): AsyncGenerator<RunEvent> {
  const GITHUB_TOKEN = process.env.GITHUB_TOKEN!;
  let attempts = 0;
  const maxAttempts = 60; // 5 minutes max

  while (attempts < maxAttempts) {
    await new Promise(resolve => setTimeout(resolve, 5000));

    const response = await fetch(
      `https://api.github.com/repos/${owner}/${repo}/actions/runs/${runId}`,
      {
        headers: {
          Authorization: `Bearer ${GITHUB_TOKEN}`,
          Accept: "application/vnd.github.v3+json"
        }
      }
    );

    const run: GitHubWorkflowRun = await response.json();

    if (run.status === "completed") {
      if (run.conclusion === "success") {
        yield {
          ts: new Date().toISOString(),
          level: "success",
          source: "GitHub",
          message: `✓ Workflow completed successfully`,
          data: { run_id: run.id, run_url: run.html_url }
        };
      } else {
        yield {
          ts: new Date().toISOString(),
          level: "error",
          source: "GitHub",
          message: `✗ Workflow failed: ${run.conclusion}`,
          data: { run_id: run.id, run_url: run.html_url, conclusion: run.conclusion }
        };
      }
      return;
    } else {
      yield {
        ts: new Date().toISOString(),
        level: "info",
        source: "GitHub",
        message: `Workflow ${run.status}... (${attempts * 5}s elapsed)`
      };
    }

    attempts++;
  }

  yield {
    ts: new Date().toISOString(),
    level: "warn",
    source: "GitHub",
    message: "Workflow poll timeout (still running in background)"
  };
}

/**
 * Create a spec file PR (for spec generation runbook)
 */
export async function* createSpecPR(
  owner: string,
  repo: string,
  specName: string,
  files: { path: string; content: string }[]
): AsyncGenerator<RunEvent> {
  const GITHUB_TOKEN = process.env.GITHUB_TOKEN;
  
  if (!GITHUB_TOKEN) {
    yield {
      ts: new Date().toISOString(),
      level: "error",
      source: "GitHub",
      message: "GITHUB_TOKEN not configured"
    };
    return;
  }

  const branchName = `spec/${specName.toLowerCase().replace(/\s+/g, "-")}`;

  yield {
    ts: new Date().toISOString(),
    level: "info",
    source: "GitHub",
    message: `Creating spec files in branch: ${branchName}...`
  };

  try {
    // 1. Get the base branch SHA
    const baseResponse = await fetch(
      `https://api.github.com/repos/${owner}/${repo}/git/ref/heads/main`,
      {
        headers: {
          Authorization: `Bearer ${GITHUB_TOKEN}`,
          Accept: "application/vnd.github.v3+json"
        }
      }
    );
    const baseRef = await baseResponse.json();
    const baseSha = baseRef.object.sha;

    // 2. Create a new branch
    await fetch(
      `https://api.github.com/repos/${owner}/${repo}/git/refs`,
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${GITHUB_TOKEN}`,
          "Content-Type": "application/json",
          Accept: "application/vnd.github.v3+json"
        },
        body: JSON.stringify({
          ref: `refs/heads/${branchName}`,
          sha: baseSha
        })
      }
    );

    yield {
      ts: new Date().toISOString(),
      level: "success",
      source: "GitHub",
      message: `✓ Created branch: ${branchName}`
    };

    // 3. Create/update files
    for (const file of files) {
      yield {
        ts: new Date().toISOString(),
        level: "info",
        source: "GitHub",
        message: `Creating ${file.path}...`
      };

      await fetch(
        `https://api.github.com/repos/${owner}/${repo}/contents/${file.path}`,
        {
          method: "PUT",
          headers: {
            Authorization: `Bearer ${GITHUB_TOKEN}`,
            "Content-Type": "application/json",
            Accept: "application/vnd.github.v3+json"
          },
          body: JSON.stringify({
            message: `Add ${file.path}`,
            content: Buffer.from(file.content).toString("base64"),
            branch: branchName
          })
        }
      );

      yield {
        ts: new Date().toISOString(),
        level: "success",
        source: "GitHub",
        message: `✓ Created ${file.path}`
      };
    }

    // 4. Create PR
    yield* createGitHubPR(
      owner,
      repo,
      `Add spec: ${specName}`,
      `This PR adds the spec kit for ${specName}.\n\nFiles:\n${files.map(f => `- ${f.path}`).join("\n")}`,
      branchName,
      "main"
    );

  } catch (error) {
    yield {
      ts: new Date().toISOString(),
      level: "error",
      source: "GitHub",
      message: `Spec PR creation error: ${error instanceof Error ? error.message : "Unknown error"}`,
      data: { error: String(error) }
    };
  }
}

/**
 * Usage in execute.ts:
 * 
 * async function* executeSpec(plan: RunbookPlan): AsyncGenerator<RunEvent> {
 *   const repo = plan.inputs.find(i => i.key === "repo")?.value as string;
 *   const [owner, repoName] = repo.split("/");
 *   
 *   // Generate spec files (mock for now)
 *   const files = [
 *     { path: "spec/constitution.md", content: "# Constitution\n..." },
 *     { path: "spec/prd.md", content: "# PRD\n..." },
 *     { path: "spec/plan.md", content: "# Plan\n..." },
 *     { path: "spec/tasks.md", content: "# Tasks\n..." }
 *   ];
 *   
 *   yield* createSpecPR(owner, repoName, "User Dashboard", files);
 * }
 */
