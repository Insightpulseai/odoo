#!/usr/bin/env node
// =============================================================================
// SYNC-GITHUB-INVENTORY.MJS - GitHub → Supabase Inventory Mirror
// =============================================================================
// Syncs GitHub organization, repositories, and rulesets to Supabase for
// the governance control plane.
//
// REQUIRED ENVIRONMENT VARIABLES:
//   GITHUB_TOKEN           - GitHub App installation token
//   SUPABASE_URL          - Supabase project URL
//   SUPABASE_SERVICE_ROLE_KEY - Supabase service role key
//
// OPTIONAL ENVIRONMENT VARIABLES:
//   GITHUB_ORG            - Organization to sync (default: Insightpulseai-net)
//   SYNC_TOPICS           - Whether to sync repo topics (default: true)
//   MAX_TOPIC_REPOS       - Max repos for topic sync (default: 200)
//   DRY_RUN               - Don't write to Supabase (default: false)
//
// USAGE:
//   export GITHUB_TOKEN=$(./scripts/github/mint-ghapp-token.sh)
//   node scripts/github/sync-github-inventory.mjs
// =============================================================================

import process from "node:process";

// Configuration
const ORG = process.env.GITHUB_ORG || "Insightpulseai-net";
const GH_TOKEN = process.env.GITHUB_TOKEN;
const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_SERVICE_ROLE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY;
const SYNC_TOPICS = process.env.SYNC_TOPICS !== "false";
const MAX_TOPIC_REPOS = parseInt(process.env.MAX_TOPIC_REPOS || "200", 10);
const DRY_RUN = process.env.DRY_RUN === "true";

// Validation
if (!GH_TOKEN) {
  console.error("ERROR: Missing GITHUB_TOKEN (installation token)");
  process.exit(1);
}
if (!SUPABASE_URL) {
  console.error("ERROR: Missing SUPABASE_URL");
  process.exit(1);
}
if (!SUPABASE_SERVICE_ROLE_KEY) {
  console.error("ERROR: Missing SUPABASE_SERVICE_ROLE_KEY");
  process.exit(1);
}

// Stats tracking
const stats = {
  org: null,
  repos: 0,
  topics_synced: 0,
  org_rulesets: 0,
  repo_rulesets: 0,
  errors: [],
};

// -----------------------------------------------------------------------------
// GitHub API Helper
// -----------------------------------------------------------------------------
async function gh(path, options = {}) {
  const url = `https://api.github.com${path}`;
  const response = await fetch(url, {
    ...options,
    headers: {
      Authorization: `Bearer ${GH_TOKEN}`,
      Accept: "application/vnd.github+json",
      "X-GitHub-Api-Version": "2022-11-28",
      ...options.headers,
    },
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(`GitHub API ${path} failed: ${response.status} ${text}`);
  }

  return response.json();
}

// Paginate through GitHub API results
async function paginate(path) {
  const results = [];
  let page = 1;

  while (true) {
    const separator = path.includes("?") ? "&" : "?";
    const data = await gh(`${path}${separator}per_page=100&page=${page}`);

    if (!Array.isArray(data) || data.length === 0) break;

    results.push(...data);
    page += 1;

    if (data.length < 100) break;
  }

  return results;
}

// -----------------------------------------------------------------------------
// Supabase API Helper
// -----------------------------------------------------------------------------
async function sb(table, rows, options = {}) {
  if (DRY_RUN) {
    console.log(`[DRY RUN] Would upsert ${rows.length} rows to ${table}`);
    return;
  }

  // Extract schema from table name (e.g., "ops.github_orgs" -> schema="ops", table="github_orgs")
  const [schema, tableName] = table.includes(".") ? table.split(".") : ["public", table];

  const url = `${SUPABASE_URL}/rest/v1/${tableName}`;
  const response = await fetch(url, {
    method: "POST",
    headers: {
      apikey: SUPABASE_SERVICE_ROLE_KEY,
      Authorization: `Bearer ${SUPABASE_SERVICE_ROLE_KEY}`,
      "Content-Type": "application/json",
      "Content-Profile": schema,  // Access non-public schemas
      "Accept-Profile": schema,
      Prefer: "resolution=merge-duplicates,return=minimal",
    },
    body: JSON.stringify(rows),
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(`Supabase upsert ${table} failed: ${response.status} ${text}`);
  }
}

async function sbDelete(table, filter) {
  if (DRY_RUN) {
    console.log(`[DRY RUN] Would delete from ${table} where ${filter}`);
    return;
  }

  // Extract schema from table name (e.g., "ops.github_rulesets" -> schema="ops", table="github_rulesets")
  const [schema, tableName] = table.includes(".") ? table.split(".") : ["public", table];

  const url = `${SUPABASE_URL}/rest/v1/${tableName}?${filter}`;
  const response = await fetch(url, {
    method: "DELETE",
    headers: {
      apikey: SUPABASE_SERVICE_ROLE_KEY,
      Authorization: `Bearer ${SUPABASE_SERVICE_ROLE_KEY}`,
      "Content-Profile": schema,
      "Accept-Profile": schema,
    },
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(`Supabase delete ${table} failed: ${response.status} ${text}`);
  }
}

async function sbRpc(fn, params) {
  if (DRY_RUN) {
    console.log(`[DRY RUN] Would call RPC ${fn} with`, params);
    return null;
  }

  // Extract schema from function name (e.g., "ops.start_run" -> schema="ops", fn="start_run")
  const [schema, funcName] = fn.includes(".") ? fn.split(".") : ["public", fn];

  const url = `${SUPABASE_URL}/rest/v1/rpc/${funcName}`;
  const response = await fetch(url, {
    method: "POST",
    headers: {
      apikey: SUPABASE_SERVICE_ROLE_KEY,
      Authorization: `Bearer ${SUPABASE_SERVICE_ROLE_KEY}`,
      "Content-Type": "application/json",
      "Content-Profile": schema,
      "Accept-Profile": schema,
      Prefer: "return=representation",
    },
    body: JSON.stringify(params),
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(`Supabase RPC ${fn} failed: ${response.status} ${text}`);
  }

  return response.json();
}

// -----------------------------------------------------------------------------
// Sync Functions
// -----------------------------------------------------------------------------

async function syncOrganization() {
  console.log(`\n📦 Syncing organization/user: ${ORG}`);

  // Try org first, fall back to user
  let entityData;
  let isOrg = true;

  try {
    entityData = await gh(`/orgs/${ORG}`);
  } catch (err) {
    if (err.message.includes("404")) {
      console.log(`  ℹ️  Not an organization, trying user endpoint...`);
      isOrg = false;
      entityData = await gh(`/users/${ORG}`);
    } else {
      throw err;
    }
  }

  await sb("ops.github_orgs", [
    {
      org_login: entityData.login,
      node_id: entityData.node_id,
      plan: entityData.plan?.name || (isOrg ? null : "user"),
      two_factor_requirement_enabled: entityData.two_factor_requirement_enabled || false,
      default_repository_permission: entityData.default_repository_permission || null,
      members_count: isOrg ? (entityData.members_count || null) : 1,
    },
  ]);

  stats.org = entityData.login;
  console.log(`  ✅ ${isOrg ? "Organization" : "User"} synced: ${entityData.login} (type: ${isOrg ? "org" : "user"})`);
}

async function syncRepositories() {
  console.log(`\n📚 Syncing repositories for ${ORG}`);

  // Try org endpoint first, fall back to user repos
  let repos;
  try {
    repos = await paginate(`/orgs/${ORG}/repos?type=all&sort=updated&direction=desc`);
  } catch (err) {
    if (err.message.includes("404")) {
      console.log(`  ℹ️  Using user repos endpoint...`);
      repos = await paginate(`/users/${ORG}/repos?type=all&sort=updated&direction=desc`);
    } else {
      throw err;
    }
  }

  const repoRows = repos.map((r) => ({
    repo_full_name: r.full_name,
    org_login: ORG,
    repo_id: r.id,
    visibility: r.visibility || (r.private ? "private" : "public"),
    is_private: !!r.private,
    default_branch: r.default_branch,
    archived: !!r.archived,
    disabled: !!r.disabled,
    has_issues: r.has_issues,
    has_projects: r.has_projects,
    has_wiki: r.has_wiki,
    allow_forking: r.allow_forking,
    web_commit_signoff_required: r.web_commit_signoff_required,
    pushed_at: r.pushed_at ? new Date(r.pushed_at).toISOString() : null,
  }));

  if (repoRows.length > 0) {
    await sb("ops.github_repos", repoRows);
  }

  stats.repos = repos.length;
  console.log(`  ✅ Synced ${repos.length} repositories`);

  // Sync topics for active repos (best-effort, capped)
  if (SYNC_TOPICS) {
    console.log(`\n🏷️  Syncing topics (max ${MAX_TOPIC_REPOS} repos)`);

    const activeRepos = repos.filter((r) => !r.archived).slice(0, MAX_TOPIC_REPOS);

    for (const repo of activeRepos) {
      try {
        const topics = await gh(`/repos/${repo.full_name}/topics`);
        await sb("ops.github_repos", [
          {
            repo_full_name: repo.full_name,
            org_login: ORG,
            topics: topics.names || [],
          },
        ]);
        stats.topics_synced += 1;
      } catch (err) {
        // Topics API may fail for some repos; non-fatal
        stats.errors.push(`topics:${repo.full_name}: ${err.message}`);
      }
    }

    console.log(`  ✅ Synced topics for ${stats.topics_synced} repositories`);
  }
}

async function syncOrgRulesets() {
  console.log(`\n📋 Syncing organization rulesets for ${ORG}`);

  let rulesets = [];
  try {
    rulesets = await gh(`/orgs/${ORG}/rulesets`);
  } catch (err) {
    // Rulesets may require elevated permissions; non-fatal
    console.log(`  ⚠️  Could not fetch org rulesets: ${err.message}`);
    stats.errors.push(`org_rulesets: ${err.message}`);
    return;
  }

  if (!Array.isArray(rulesets)) {
    console.log(`  ⚠️  Unexpected rulesets response format`);
    return;
  }

  // Clear existing org rulesets and replace
  await sbDelete(
    "ops.github_rulesets",
    `ruleset_scope=eq.org&scope_id=eq.${encodeURIComponent(ORG)}`
  );

  if (rulesets.length > 0) {
    const rows = rulesets.map((rs) => ({
      ruleset_scope: "org",
      scope_id: ORG,
      ruleset_id: rs.id,
      name: rs.name,
      enforcement: rs.enforcement,
      target: rs.target,
      bypass_actors: rs.bypass_actors || [],
      conditions: rs.conditions || {},
      rules: rs.rules || [],
      raw: rs,
    }));

    await sb("ops.github_rulesets", rows);
  }

  stats.org_rulesets = rulesets.length;
  console.log(`  ✅ Synced ${rulesets.length} organization rulesets`);
}

async function syncRepoRulesets(repoFullName) {
  try {
    const rulesets = await gh(`/repos/${repoFullName}/rulesets`);

    if (!Array.isArray(rulesets) || rulesets.length === 0) return 0;

    // Clear existing repo rulesets
    await sbDelete(
      "ops.github_rulesets",
      `ruleset_scope=eq.repo&scope_id=eq.${encodeURIComponent(repoFullName)}`
    );

    const rows = rulesets.map((rs) => ({
      ruleset_scope: "repo",
      scope_id: repoFullName,
      ruleset_id: rs.id,
      name: rs.name,
      enforcement: rs.enforcement,
      target: rs.target,
      bypass_actors: rs.bypass_actors || [],
      conditions: rs.conditions || {},
      rules: rs.rules || [],
      raw: rs,
    }));

    await sb("ops.github_rulesets", rows);
    return rulesets.length;
  } catch (err) {
    // Non-fatal; repo may not have ruleset access
    return 0;
  }
}

// -----------------------------------------------------------------------------
// Main
// -----------------------------------------------------------------------------

async function main() {
  console.log("=".repeat(60));
  console.log("GitHub → Supabase Inventory Sync");
  console.log("=".repeat(60));
  console.log(`Organization: ${ORG}`);
  console.log(`Dry run: ${DRY_RUN}`);
  console.log(`Sync topics: ${SYNC_TOPICS}`);

  const startTime = Date.now();

  try {
    // Start a governance run in Supabase
    let runId = null;
    if (!DRY_RUN) {
      try {
        runId = await sbRpc("ops.start_run", {
          p_run_type: "inventory_sync",
          p_actor: "sync-github-inventory",
          p_target_scope: "org",
          p_target_id: ORG,
        });
      } catch (err) {
        console.log(`  ⚠️  Could not start run log: ${err.message}`);
      }
    }

    // Sync in order
    await syncOrganization();
    await syncRepositories();
    await syncOrgRulesets();

    // Complete the run
    if (runId && !DRY_RUN) {
      try {
        await sbRpc("ops.complete_run", {
          p_run_id: runId,
          p_status: stats.errors.length > 0 ? "succeeded" : "succeeded",
          p_metadata: { stats },
        });
      } catch (err) {
        console.log(`  ⚠️  Could not complete run log: ${err.message}`);
      }
    }

    const duration = ((Date.now() - startTime) / 1000).toFixed(2);

    console.log("\n" + "=".repeat(60));
    console.log("SYNC COMPLETE");
    console.log("=".repeat(60));
    console.log(
      JSON.stringify(
        {
          ok: true,
          duration_seconds: parseFloat(duration),
          ...stats,
        },
        null,
        2
      )
    );

    if (stats.errors.length > 0) {
      console.log("\n⚠️  Non-fatal errors:");
      stats.errors.forEach((e) => console.log(`  - ${e}`));
    }
  } catch (err) {
    console.error("\n❌ SYNC FAILED:", err.message);
    process.exit(1);
  }
}

main();
