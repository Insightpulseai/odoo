// Supabase Edge Function: GitHub App Write-Back Actions
// Contract: C-19 (docs/contracts/GITHUB_APP_CONTRACT.md)
//
// Provides write-back actions to GitHub via the App's installation token:
// - comment: Post PR/issue comments
// - check_run: Create check runs on commits
// - create_issue: Open new issues
//
// All actions obtain tokens via the github-app-token broker function.

Deno.serve(async (req) => {
  if (req.method !== "POST") {
    return new Response("Method not allowed", { status: 405 });
  }

  const { action, installation_id, owner, repo, ...params } = await req.json();

  if (!action || !installation_id || !owner || !repo) {
    return new Response(
      JSON.stringify({ error: "action, installation_id, owner, repo required" }),
      { status: 400 },
    );
  }

  // Get installation token from token broker
  const tokenResp = await fetch(
    `${Deno.env.get("SUPABASE_URL")}/functions/v1/github-app-token`,
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ installation_id }),
    },
  );

  if (!tokenResp.ok) {
    const err = await tokenResp.json();
    return new Response(JSON.stringify({ error: "Token broker failed", detail: err }), {
      status: 502,
    });
  }

  const { token } = await tokenResp.json();
  const ghHeaders = {
    Authorization: `token ${token}`,
    Accept: "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
    "Content-Type": "application/json",
  };

  let result;

  switch (action) {
    case "comment": {
      // Post PR/issue comment
      const { issue_number, body } = params;
      const resp = await fetch(
        `https://api.github.com/repos/${owner}/${repo}/issues/${issue_number}/comments`,
        { method: "POST", headers: ghHeaders, body: JSON.stringify({ body }) },
      );
      result = { status: resp.status, data: await resp.json() };
      break;
    }
    case "check_run": {
      // Create check run
      const { name, head_sha, status, conclusion, output } = params;
      const resp = await fetch(
        `https://api.github.com/repos/${owner}/${repo}/check-runs`,
        {
          method: "POST",
          headers: ghHeaders,
          body: JSON.stringify({ name, head_sha, status, conclusion, output }),
        },
      );
      result = { status: resp.status, data: await resp.json() };
      break;
    }
    case "create_issue": {
      // Open issue
      const { title, body, labels } = params;
      const resp = await fetch(
        `https://api.github.com/repos/${owner}/${repo}/issues`,
        {
          method: "POST",
          headers: ghHeaders,
          body: JSON.stringify({ title, body, labels: labels || [] }),
        },
      );
      result = { status: resp.status, data: await resp.json() };
      break;
    }
    default:
      return new Response(
        JSON.stringify({ error: `Unknown action: ${action}` }),
        { status: 400 },
      );
  }

  return new Response(JSON.stringify({ ok: result.status < 300, ...result }), {
    status: result.status < 300 ? 200 : 502,
    headers: { "Content-Type": "application/json" },
  });
});
