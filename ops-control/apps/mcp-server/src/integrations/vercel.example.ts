/**
 * Example: Real Vercel Integration
 * 
 * This shows how to replace mock execution with real Vercel API calls.
 * Uncomment and adapt this code when you're ready to wire real deployments.
 */

import type { RunEvent } from "@ops-control-room/core";

interface VercelDeployment {
  id: string;
  url: string;
  state: "BUILDING" | "READY" | "ERROR";
  readyState: "QUEUED" | "BUILDING" | "READY" | "ERROR";
}

/**
 * Real Vercel deployment executor
 */
export async function* deployToVercel(
  projectName: string,
  branch: string = "main"
): AsyncGenerator<RunEvent> {
  const VERCEL_TOKEN = process.env.VERCEL_TOKEN;
  
  if (!VERCEL_TOKEN) {
    yield {
      ts: new Date().toISOString(),
      level: "error",
      source: "Vercel",
      message: "VERCEL_TOKEN not configured"
    };
    return;
  }

  yield {
    ts: new Date().toISOString(),
    level: "info",
    source: "Vercel",
    message: `Triggering deployment for ${projectName}@${branch}...`
  };

  try {
    // 1. Trigger deployment
    const deployResponse = await fetch(
      `https://api.vercel.com/v13/deployments`,
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${VERCEL_TOKEN}`,
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          name: projectName,
          gitSource: {
            type: "github",
            ref: branch,
            repoId: process.env.GITHUB_REPO_ID // e.g., "12345678"
          }
        })
      }
    );

    if (!deployResponse.ok) {
      const error = await deployResponse.text();
      yield {
        ts: new Date().toISOString(),
        level: "error",
        source: "Vercel",
        message: `Deployment failed: ${error}`
      };
      return;
    }

    const deployment: VercelDeployment = await deployResponse.json();
    
    yield {
      ts: new Date().toISOString(),
      level: "success",
      source: "Vercel",
      message: `✓ Deployment created: ${deployment.id}`,
      data: { deployment_id: deployment.id }
    };

    // 2. Poll deployment status
    let attempts = 0;
    const maxAttempts = 60; // 5 minutes max (5s intervals)

    while (attempts < maxAttempts) {
      await new Promise(resolve => setTimeout(resolve, 5000));

      const statusResponse = await fetch(
        `https://api.vercel.com/v13/deployments/${deployment.id}`,
        {
          headers: {
            Authorization: `Bearer ${VERCEL_TOKEN}`
          }
        }
      );

      const status: VercelDeployment = await statusResponse.json();

      if (status.readyState === "BUILDING") {
        yield {
          ts: new Date().toISOString(),
          level: "info",
          source: "Vercel",
          message: `Building... (${attempts * 5}s elapsed)`
        };
      } else if (status.readyState === "READY") {
        yield {
          ts: new Date().toISOString(),
          level: "success",
          source: "Vercel",
          message: `✓ Deployment ready: https://${status.url}`,
          data: {
            url: `https://${status.url}`,
            deployment_id: status.id,
            duration: `${attempts * 5}s`
          }
        };
        return;
      } else if (status.readyState === "ERROR") {
        yield {
          ts: new Date().toISOString(),
          level: "error",
          source: "Vercel",
          message: "Deployment failed",
          data: status
        };
        return;
      }

      attempts++;
    }

    yield {
      ts: new Date().toISOString(),
      level: "error",
      source: "Vercel",
      message: "Deployment timeout (5 minutes)"
    };

  } catch (error) {
    yield {
      ts: new Date().toISOString(),
      level: "error",
      source: "Vercel",
      message: `Deployment error: ${error instanceof Error ? error.message : "Unknown error"}`,
      data: { error: String(error) }
    };
  }
}

/**
 * Get deployment logs
 */
export async function* getVercelLogs(
  deploymentId: string
): AsyncGenerator<RunEvent> {
  const VERCEL_TOKEN = process.env.VERCEL_TOKEN;
  
  if (!VERCEL_TOKEN) {
    yield {
      ts: new Date().toISOString(),
      level: "error",
      source: "Vercel",
      message: "VERCEL_TOKEN not configured"
    };
    return;
  }

  try {
    const response = await fetch(
      `https://api.vercel.com/v2/deployments/${deploymentId}/events`,
      {
        headers: {
          Authorization: `Bearer ${VERCEL_TOKEN}`
        }
      }
    );

    const logs = await response.json();

    for (const log of logs) {
      yield {
        ts: log.created,
        level: log.type === "error" ? "error" : "info",
        source: "Vercel",
        message: log.text || log.payload?.text || "Build log",
        data: log
      };
    }
  } catch (error) {
    yield {
      ts: new Date().toISOString(),
      level: "error",
      source: "Vercel",
      message: `Failed to fetch logs: ${error instanceof Error ? error.message : "Unknown error"}`
    };
  }
}

/**
 * Usage in execute.ts:
 * 
 * async function* executeDeploy(plan: RunbookPlan): AsyncGenerator<RunEvent> {
 *   const repo = plan.inputs.find(i => i.key === "repo")?.value as string;
 *   const branch = plan.inputs.find(i => i.key === "branch")?.value as string || "main";
 *   
 *   yield* deployToVercel(repo, branch);
 * }
 */
