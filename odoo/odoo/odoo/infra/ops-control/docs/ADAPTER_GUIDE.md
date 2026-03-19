# API Adapter Implementation Guide

This guide helps you replace the stubbed adapters in `/supabase/functions/ops-executor/index.ts` with real API calls.

---

## 🔧 Vercel Adapters

### `vercel_list_deployments(project: string, limit: number)`

**Purpose:** Fetch recent deployments for a Vercel project

**API:** [Vercel REST API - List Deployments](https://vercel.com/docs/rest-api/endpoints#list-deployments)

```typescript
async function vercel_list_deployments(project: string, limit: number) {
  const token = Deno.env.get("VERCEL_TOKEN");
  
  const response = await fetch(
    `https://api.vercel.com/v6/deployments?projectId=${project}&limit=${limit}`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );

  if (!response.ok) {
    throw new Error(`Vercel API error: ${response.statusText}`);
  }

  const data = await response.json();
  
  return data.deployments.map((d: any) => ({
    id: d.uid,
    state: d.readyState,
    url: `https://${d.url}`,
    createdAt: d.createdAt,
  }));
}
```

### `vercel_get_deployment_logs(deployment_id: string, limit: number)`

**Purpose:** Fetch build and runtime logs for a deployment

**API:** [Vercel REST API - Get Deployment Events](https://vercel.com/docs/rest-api/endpoints#get-deployment-events)

```typescript
async function vercel_get_deployment_logs(deployment_id: string, limit: number) {
  const token = Deno.env.get("VERCEL_TOKEN");
  
  const response = await fetch(
    `https://api.vercel.com/v2/deployments/${deployment_id}/events?limit=${limit}`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );

  if (!response.ok) {
    throw new Error(`Vercel API error: ${response.statusText}`);
  }

  const data = await response.json();
  
  return data.map((event: any) => ({
    ts: new Date(event.created).toISOString(),
    level: event.type === "error" ? "error" : "info",
    msg: event.text,
  }));
}
```

---

## 🐙 GitHub Adapters

### `github_open_pr(args: any)`

**Purpose:** Create a branch, commit files, and open a pull request

**API:** [GitHub REST API - Git Database](https://docs.github.com/en/rest/git)

```typescript
async function github_open_pr(args: {
  repo: string;
  base: string;
  head: string;
  title: string;
  body: string;
  files: Array<{ path: string; content: string }>;
}) {
  const token = Deno.env.get("GITHUB_TOKEN");
  const [owner, repoName] = args.repo.split("/");
  const baseUrl = `https://api.github.com/repos/${owner}/${repoName}`;

  const headers = {
    Authorization: `Bearer ${token}`,
    Accept: "application/vnd.github+json",
  };

  // 1. Get the base branch ref
  const baseRefResponse = await fetch(`${baseUrl}/git/ref/heads/${args.base}`, {
    headers,
  });
  const baseRef = await baseRefResponse.json();
  const baseSha = baseRef.object.sha;

  // 2. Create a new branch
  await fetch(`${baseUrl}/git/refs`, {
    method: "POST",
    headers: { ...headers, "Content-Type": "application/json" },
    body: JSON.stringify({
      ref: `refs/heads/${args.head}`,
      sha: baseSha,
    }),
  });

  // 3. Get the base tree
  const baseTreeResponse = await fetch(`${baseUrl}/git/commits/${baseSha}`, {
    headers,
  });
  const baseCommit = await baseTreeResponse.json();
  const baseTreeSha = baseCommit.tree.sha;

  // 4. Create blobs for each file
  const tree = await Promise.all(
    args.files.map(async (file) => {
      const blobResponse = await fetch(`${baseUrl}/git/blobs`, {
        method: "POST",
        headers: { ...headers, "Content-Type": "application/json" },
        body: JSON.stringify({
          content: file.content,
          encoding: "utf-8",
        }),
      });
      const blob = await blobResponse.json();
      return {
        path: file.path,
        mode: "100644",
        type: "blob",
        sha: blob.sha,
      };
    })
  );

  // 5. Create a new tree
  const newTreeResponse = await fetch(`${baseUrl}/git/trees`, {
    method: "POST",
    headers: { ...headers, "Content-Type": "application/json" },
    body: JSON.stringify({
      base_tree: baseTreeSha,
      tree,
    }),
  });
  const newTree = await newTreeResponse.json();

  // 6. Create a commit
  const commitResponse = await fetch(`${baseUrl}/git/commits`, {
    method: "POST",
    headers: { ...headers, "Content-Type": "application/json" },
    body: JSON.stringify({
      message: args.title,
      tree: newTree.sha,
      parents: [baseSha],
    }),
  });
  const commit = await commitResponse.json();

  // 7. Update the branch ref
  await fetch(`${baseUrl}/git/refs/heads/${args.head}`, {
    method: "PATCH",
    headers: { ...headers, "Content-Type": "application/json" },
    body: JSON.stringify({
      sha: commit.sha,
    }),
  });

  // 8. Create pull request
  const prResponse = await fetch(`${baseUrl}/pulls`, {
    method: "POST",
    headers: { ...headers, "Content-Type": "application/json" },
    body: JSON.stringify({
      title: args.title,
      body: args.body,
      head: args.head,
      base: args.base,
    }),
  });
  const pr = await prResponse.json();

  return {
    url: pr.html_url,
    head: args.head,
  };
}
```

### `github_workflow_status(repo: string, branch: string)`

**Purpose:** Get the latest GitHub Actions workflow run status

**API:** [GitHub REST API - Actions](https://docs.github.com/en/rest/actions)

```typescript
async function github_workflow_status(repo: string, branch: string) {
  const token = Deno.env.get("GITHUB_TOKEN");
  const [owner, repoName] = repo.split("/");

  const response = await fetch(
    `https://api.github.com/repos/${owner}/${repoName}/actions/runs?branch=${branch}&per_page=1`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
        Accept: "application/vnd.github+json",
      },
    }
  );

  if (!response.ok) {
    throw new Error(`GitHub API error: ${response.statusText}`);
  }

  const data = await response.json();
  const latestRun = data.workflow_runs[0];

  return {
    status: latestRun?.conclusion || "in_progress",
    url: `https://github.com/${repo}/actions`,
  };
}
```

---

## 🗄️ Supabase Adapters

### `supabase_smokecheck(project_ref: string, checks: string[])`

**Purpose:** Run health checks against Supabase (HTTP health + RPC)

```typescript
async function supabase_smokecheck(project_ref: string, checks: string[]) {
  const results = [];

  for (const check of checks) {
    const start = Date.now();

    try {
      if (check === "health") {
        // Check REST API health
        const response = await fetch(
          `https://${project_ref}.supabase.co/rest/v1/`,
          {
            headers: {
              apikey: Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") || "",
            },
          }
        );
        results.push({
          check: "health",
          ok: response.ok,
          ms: Date.now() - start,
        });
      } else if (check === "rpc_ping") {
        // Call a simple RPC (you need to create this in your DB)
        const response = await fetch(
          `https://${project_ref}.supabase.co/rest/v1/rpc/ping`,
          {
            method: "POST",
            headers: {
              apikey: Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") || "",
              "Content-Type": "application/json",
            },
            body: JSON.stringify({}),
          }
        );
        results.push({
          check: "rpc_ping",
          ok: response.ok,
          ms: Date.now() - start,
        });
      } else if (check === "auth") {
        // Check auth endpoint
        const response = await fetch(
          `https://${project_ref}.supabase.co/auth/v1/health`,
          {
            headers: {
              apikey: Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") || "",
            },
          }
        );
        results.push({
          check: "auth",
          ok: response.ok,
          ms: Date.now() - start,
        });
      }
    } catch (error) {
      results.push({
        check,
        ok: false,
        ms: Date.now() - start,
        error: error.message,
      });
    }
  }

  return results;
}
```

**Note:** For `rpc_ping`, create this function in your Supabase database:

```sql
create or replace function ping()
returns text
language sql
security definer
as $$
  select 'pong';
$$;
```

---

## 🌊 DigitalOcean Adapters

### `do_droplet_health(droplets: string[], http_health_urls: string[])`

**Purpose:** Check droplet status and optional HTTP health endpoints

**API:** [DigitalOcean API - Droplets](https://docs.digitalocean.com/reference/api/api-reference/#tag/Droplets)

```typescript
async function do_droplet_health(
  droplets: string[],
  http_health_urls: string[]
) {
  const token = Deno.env.get("DIGITALOCEAN_TOKEN");

  // 1. Check droplet status via API
  const dropletResults = await Promise.all(
    droplets.map(async (name) => {
      try {
        const response = await fetch(
          `https://api.digitalocean.com/v2/droplets?name=${name}`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
              "Content-Type": "application/json",
            },
          }
        );

        if (!response.ok) {
          return { name, ok: false };
        }

        const data = await response.json();
        const droplet = data.droplets[0];

        return {
          name,
          ok: droplet?.status === "active",
          status: droplet?.status,
          ip: droplet?.networks?.v4?.[0]?.ip_address,
        };
      } catch (error) {
        return { name, ok: false, error: error.message };
      }
    })
  );

  // 2. Check HTTP health URLs
  const urlResults = await Promise.all(
    http_health_urls.map(async (url) => {
      const start = Date.now();
      try {
        const response = await fetch(url, {
          signal: AbortSignal.timeout(5000), // 5s timeout
        });
        return {
          url,
          ok: response.ok,
          status: response.status,
          ms: Date.now() - start,
        };
      } catch (error) {
        return {
          url,
          ok: false,
          ms: Date.now() - start,
          error: error.message,
        };
      }
    })
  );

  return {
    droplets: dropletResults,
    urls: urlResults,
  };
}
```

---

## 🧪 Testing Adapters

### Test each adapter individually:

```typescript
// In a separate test file or Edge Function
Deno.test("vercel_list_deployments", async () => {
  const deployments = await vercel_list_deployments("my-project", 5);
  console.log(deployments);
});

Deno.test("github_open_pr", async () => {
  const pr = await github_open_pr({
    repo: "user/repo",
    base: "main",
    head: "test-branch",
    title: "Test PR",
    body: "Testing adapter",
    files: [{ path: "TEST.md", content: "# Test\n" }],
  });
  console.log(pr);
});
```

---

## 🔐 Token Permissions

### Vercel Token:
- Needs: `deployments:read`, `logs:read`

### GitHub Token:
- Needs: `repo` scope (read + write)

### DigitalOcean Token:
- Needs: `read` scope for droplets

### Supabase Service Role:
- Full access (automatically has all permissions)

---

## 📝 Error Handling Best Practices

```typescript
async function safeApiCall<T>(
  fn: () => Promise<T>,
  fallback: T
): Promise<T> {
  try {
    return await fn();
  } catch (error) {
    console.error("API call failed:", error);
    return fallback;
  }
}

// Usage
const deployments = await safeApiCall(
  () => vercel_list_deployments("project", 5),
  [] // fallback to empty array
);
```

---

## 🎯 Next Steps

1. **Test in isolation** - Create a test Edge Function to verify each adapter
2. **Add retry logic** - Use exponential backoff for transient failures
3. **Add rate limiting** - Respect API rate limits
4. **Add caching** - Cache results for read-heavy operations
5. **Monitor usage** - Track API quota consumption

---

Happy coding! 🚀
