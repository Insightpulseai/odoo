const GITHUB_API_BASE = 'https://api.github.com';

export async function triggerDeploy(runId: string, envId: string) {
  const token = process.env.GITHUB_TOKEN;
  
  if (!token) {
    throw new Error('GITHUB_TOKEN environment variable is required');
  }

  const response = await fetch(`${GITHUB_API_BASE}/repos/insightpulseai/odoo/dispatches`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
      'Accept': 'application/vnd.github+json',
      'X-GitHub-Api-Version': '2022-11-28'
    },
    body: JSON.stringify({
      event_type: 'deploy_environment',
      client_payload: {
        run_id: runId,
        env_id: envId,
        triggered_at: new Date().toISOString()
      }
    })
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`GitHub API error: ${response.status} ${error}`);
  }
}

export async function promoteBranch(
  sourceBranch: string,
  targetBranch: string,
  title: string,
  body: string
) {
  const token = process.env.GITHUB_TOKEN;
  
  if (!token) {
    throw new Error('GITHUB_TOKEN environment variable is required');
  }

  // Create pull request
  const response = await fetch(`${GITHUB_API_BASE}/repos/insightpulseai/odoo/pulls`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
      'Accept': 'application/vnd.github+json',
      'X-GitHub-Api-Version': '2022-11-28'
    },
    body: JSON.stringify({
      title,
      body,
      head: sourceBranch,
      base: targetBranch
    })
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Failed to create PR: ${response.status} ${error}`);
  }

  const pr = await response.json();
  
  // Auto-merge if it's dev → staging or staging → prod
  if (targetBranch === 'main' || targetBranch === 'staging') {
    await mergePullRequest(pr.number);
  }

  return pr;
}

export async function mergePullRequest(pullNumber: number) {
  const token = process.env.GITHUB_TOKEN;
  
  if (!token) {
    throw new Error('GITHUB_TOKEN environment variable is required');
  }

  const response = await fetch(
    `${GITHUB_API_BASE}/repos/insightpulseai/odoo/pulls/${pullNumber}/merge`,
    {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28'
      },
      body: JSON.stringify({
        merge_method: 'squash',
        commit_title: `Promote to production (#${pullNumber})`,
        commit_message: 'Automated promotion from control plane'
      })
    }
  );

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Failed to merge PR: ${response.status} ${error}`);
  }

  return response.json();
}
