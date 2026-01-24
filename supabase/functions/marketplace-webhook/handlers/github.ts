/**
 * GitHub Webhook Handler
 * Processes GitHub workflow_run events and triggers artifact syncs
 */

import { createClient, SupabaseClient } from 'https://esm.sh/@supabase/supabase-js@2';
import {
  GitHubWorkflowRunPayload,
  GitHubArtifact,
  GitHubArtifactsResponse,
  HandlerResponse,
  SyncRule,
} from '../types.ts';

const GITHUB_API_BASE = 'https://api.github.com';

/**
 * Verify GitHub webhook signature
 */
export async function verifyGitHubSignature(
  payload: string,
  signature: string,
  secret: string
): Promise<boolean> {
  if (!signature || !secret) return false;

  const encoder = new TextEncoder();
  const key = await crypto.subtle.importKey(
    'raw',
    encoder.encode(secret),
    { name: 'HMAC', hash: 'SHA-256' },
    false,
    ['sign']
  );

  const sig = await crypto.subtle.sign('HMAC', key, encoder.encode(payload));
  const hashArray = Array.from(new Uint8Array(sig));
  const expectedSignature = 'sha256=' + hashArray.map(b => b.toString(16).padStart(2, '0')).join('');

  return signature === expectedSignature;
}

/**
 * Fetch artifacts from a GitHub workflow run
 */
export async function fetchWorkflowArtifacts(
  artifactsUrl: string,
  githubToken: string
): Promise<GitHubArtifact[]> {
  const response = await fetch(artifactsUrl, {
    headers: {
      'Authorization': `Bearer ${githubToken}`,
      'Accept': 'application/vnd.github+json',
      'X-GitHub-Api-Version': '2022-11-28',
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch artifacts: ${response.status} ${response.statusText}`);
  }

  const data: GitHubArtifactsResponse = await response.json();
  return data.artifacts.filter(a => !a.expired);
}

/**
 * Download artifact content
 */
export async function downloadArtifact(
  downloadUrl: string,
  githubToken: string
): Promise<ArrayBuffer> {
  const response = await fetch(downloadUrl, {
    headers: {
      'Authorization': `Bearer ${githubToken}`,
      'Accept': 'application/vnd.github+json',
      'X-GitHub-Api-Version': '2022-11-28',
    },
    redirect: 'follow',
  });

  if (!response.ok) {
    throw new Error(`Failed to download artifact: ${response.status} ${response.statusText}`);
  }

  return await response.arrayBuffer();
}

/**
 * Get matching sync rules for GitHub artifacts
 */
async function getMatchingSyncRules(
  supabase: SupabaseClient,
  sourcePath: string,
  artifactType: string
): Promise<SyncRule[]> {
  const { data, error } = await supabase.rpc('get_matching_sync_rules', {
    p_source_provider: 'github',
    p_source_path: sourcePath,
    p_artifact_type: artifactType,
  });

  if (error) {
    console.error('Error fetching sync rules:', error);
    return [];
  }

  return data || [];
}

/**
 * Create artifact sync records for each matching rule
 */
async function createArtifactSyncs(
  supabase: SupabaseClient,
  artifact: GitHubArtifact,
  workflowRun: GitHubWorkflowRunPayload['workflow_run'],
  rules: SyncRule[]
): Promise<string[]> {
  const syncIds: string[] = [];
  const date = new Date().toISOString().split('T')[0];

  for (const rule of rules) {
    // Expand destination template
    const destinationPath = rule.destination_template
      .replace('{date}', date)
      .replace('{workflow}', workflowRun.name.replace(/[^a-zA-Z0-9-_]/g, '_'))
      .replace('{name}', artifact.name)
      .replace('{branch}', workflowRun.head_branch)
      .replace('{sha}', workflowRun.head_sha.substring(0, 7));

    // Determine artifact type from name
    const artifactType = artifact.name.endsWith('.zip')
      ? 'zip'
      : artifact.name.endsWith('.pdf')
      ? 'pdf'
      : artifact.name.endsWith('.json')
      ? 'json'
      : 'binary';

    const { data, error } = await supabase.rpc('create_artifact_sync', {
      p_source_provider: 'github',
      p_source_path: `${workflowRun.repository.full_name}/actions/runs/${workflowRun.id}/artifacts/${artifact.id}`,
      p_source_ref: workflowRun.head_sha,
      p_destination_provider: rule.destination_integration_id,
      p_destination_path: destinationPath,
      p_artifact_type: artifactType,
      p_artifact_name: artifact.name,
      p_triggered_by: 'webhook',
      p_metadata: {
        workflow_name: workflowRun.name,
        workflow_run_id: workflowRun.id,
        branch: workflowRun.head_branch,
        commit_sha: workflowRun.head_sha,
        artifact_size: artifact.size_in_bytes,
        download_url: artifact.archive_download_url,
        sync_rule_id: rule.id,
        sync_rule_name: rule.name,
      },
    });

    if (error) {
      console.error(`Error creating sync for rule ${rule.name}:`, error);
      continue;
    }

    if (data) {
      syncIds.push(data);
    }
  }

  return syncIds;
}

/**
 * Process GitHub workflow_run webhook event
 */
export async function handleWorkflowRun(
  payload: GitHubWorkflowRunPayload,
  supabase: SupabaseClient,
  githubToken: string
): Promise<HandlerResponse> {
  const { action, workflow_run } = payload;

  // Only process completed successful runs
  if (action !== 'completed' || workflow_run.conclusion !== 'success') {
    return {
      success: true,
      details: {
        message: `Skipping workflow run: action=${action}, conclusion=${workflow_run.conclusion}`,
      },
    };
  }

  try {
    // Fetch artifacts from the workflow run
    const artifacts = await fetchWorkflowArtifacts(workflow_run.artifacts_url, githubToken);

    if (artifacts.length === 0) {
      return {
        success: true,
        syncs_created: 0,
        details: {
          message: 'No artifacts found in workflow run',
          workflow_run_id: workflow_run.id,
        },
      };
    }

    let totalSyncsCreated = 0;

    // Process each artifact
    for (const artifact of artifacts) {
      const sourcePath = `artifacts/${artifact.name}`;
      const rules = await getMatchingSyncRules(supabase, sourcePath, 'zip');

      if (rules.length > 0) {
        const syncIds = await createArtifactSyncs(supabase, artifact, workflow_run, rules);
        totalSyncsCreated += syncIds.length;
      }
    }

    return {
      success: true,
      syncs_created: totalSyncsCreated,
      details: {
        workflow_run_id: workflow_run.id,
        workflow_name: workflow_run.name,
        artifacts_count: artifacts.length,
        branch: workflow_run.head_branch,
        commit_sha: workflow_run.head_sha,
      },
    };
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error processing workflow run',
      details: {
        workflow_run_id: workflow_run.id,
      },
    };
  }
}

/**
 * Main GitHub webhook handler
 */
export async function handleGitHubWebhook(
  eventType: string,
  payload: Record<string, unknown>,
  supabase: SupabaseClient,
  githubToken: string
): Promise<HandlerResponse> {
  switch (eventType) {
    case 'workflow_run':
      return handleWorkflowRun(payload as GitHubWorkflowRunPayload, supabase, githubToken);

    case 'push':
      // TODO: Handle push events for direct file syncs
      return {
        success: true,
        details: { message: 'Push event received, no action configured' },
      };

    case 'release':
      // TODO: Handle release events for release artifact syncs
      return {
        success: true,
        details: { message: 'Release event received, no action configured' },
      };

    default:
      return {
        success: true,
        details: { message: `Unhandled event type: ${eventType}` },
      };
  }
}
