import { NextRequest, NextResponse } from 'next/server';
import { createOpenAI } from '@ai-sdk/openai';
import { generateObject } from 'ai';
import { z } from 'zod';
import { VercelBotPayloadSchema, VercelBotResponse, VercelDeployment } from '@/lib/types';
import { getSecret, logBotExecution, updateBotHeartbeat } from '@/lib/supabase';

const BOT_ID = 'vercel-bot';
const VERCEL_API_BASE = 'https://api.vercel.com';

/**
 * Vercel Bot API Route - Deployment SRE
 *
 * Queries Vercel deployments and provides AI-powered recommendations
 * for rollback, investigation, or keeping current deployment.
 *
 * POST /api/vercel-bot
 */
export async function POST(req: NextRequest) {
  const startTime = Date.now();
  let requestPayload: unknown;

  try {
    // Parse and validate request
    const json = await req.json();
    requestPayload = json;
    const payload = VercelBotPayloadSchema.parse(json);

    // Update heartbeat
    await updateBotHeartbeat(BOT_ID);

    // Get API tokens from Supabase Vault
    const vercelToken = await getSecret('VERCEL_API_TOKEN', BOT_ID, 'read');

    if (!vercelToken) {
      // Fallback to environment variable
      const envToken = process.env.VERCEL_TOKEN;
      if (!envToken) {
        throw new Error('Vercel API token not available');
      }
    }

    const token = vercelToken || process.env.VERCEL_TOKEN;

    // Query Vercel deployments
    const deploymentsResp = await fetch(
      `${VERCEL_API_BASE}/v6/deployments?projectId=${encodeURIComponent(payload.projectName)}&limit=10`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      }
    );

    if (!deploymentsResp.ok) {
      // Try with project name as filter instead of projectId
      const altResp = await fetch(
        `${VERCEL_API_BASE}/v6/deployments?limit=20`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (!altResp.ok) {
        throw new Error(`Vercel API error: ${deploymentsResp.status}`);
      }

      const altData = await altResp.json();
      const filteredDeployments = (altData.deployments || []).filter(
        (d: any) => d.name?.includes(payload.projectName)
      );

      return handleDeploymentsResponse(
        filteredDeployments,
        payload.action,
        requestPayload as object,
        startTime
      );
    }

    const deploymentData = await deploymentsResp.json();
    const deployments: VercelDeployment[] = (deploymentData.deployments || []).map((d: any) => ({
      uid: d.uid,
      name: d.name,
      url: d.url,
      state: d.state,
      created: d.created,
      ready: d.ready,
      target: d.target,
      inspectorUrl: d.inspectorUrl,
    }));

    return handleDeploymentsResponse(deployments, payload.action, requestPayload as object, startTime);
  } catch (err) {
    const latencyMs = Date.now() - startTime;
    const errorMessage = err instanceof Error ? err.message : 'Unknown error';

    console.error('Vercel Bot error:', err);

    // Log failed execution
    await logBotExecution({
      botId: BOT_ID,
      executionType: 'deployment_check',
      requestPayload: requestPayload as object,
      latencyMs,
      status: 'error',
      errorMessage,
    });

    return NextResponse.json(
      { ok: false, error: errorMessage } satisfies VercelBotResponse,
      { status: 500 }
    );
  }
}

async function handleDeploymentsResponse(
  deployments: VercelDeployment[],
  action: 'status' | 'suggest' | 'health',
  requestPayload: object,
  startTime: number
): Promise<NextResponse> {
  // For status action, just return deployments
  if (action === 'status' || action === 'health') {
    const latencyMs = Date.now() - startTime;
    const response: VercelBotResponse = { ok: true, deployments };

    await logBotExecution({
      botId: BOT_ID,
      executionType: 'deployment_status',
      requestPayload,
      responsePayload: response,
      latencyMs,
      status: 'success',
    });

    return NextResponse.json(response);
  }

  // For suggest action, use AI to analyze and recommend
  const openaiKey = await getSecret('OPENAI_API_KEY', BOT_ID, 'read');
  const apiKey = openaiKey || process.env.OPENAI_API_KEY;

  if (!apiKey) {
    throw new Error('OpenAI API key not available for suggestions');
  }

  const openai = createOpenAI({
    apiKey,
    baseURL: process.env.AI_GATEWAY_URL || undefined,
  });

  // Define the advice schema
  const adviceSchema = z.object({
    decision: z.enum(['keep_current', 'rollback', 'investigate', 'block_deploys']),
    reason: z.string(),
    candidateRollbackId: z.string().optional(),
  });

  const deploymentSummary = JSON.stringify(
    deployments.slice(0, 10).map((d) => ({
      uid: d.uid,
      name: d.name,
      state: d.state,
      created: new Date(d.created).toISOString(),
      ready: d.ready ? new Date(d.ready).toISOString() : null,
      target: d.target,
    })),
    null,
    2
  );

  const { object: advice, usage } = await generateObject({
    model: openai('gpt-4o-mini'),
    schema: adviceSchema,
    system: `You are VercelBot, a deployment SRE assistant.
Given deployment history, recommend one of:
1. keep_current - The current deployment is healthy
2. rollback - Rollback to a previous healthy deployment (specify candidateRollbackId)
3. investigate - The situation needs investigation before action
4. block_deploys - Block new deployments until issues are resolved

Consider:
- Deployment states (READY, ERROR, BUILDING, CANCELED)
- Time since last successful deployment
- Pattern of failures
- Production vs preview deployments`,
    prompt: `Analyze these recent deployments and recommend an action:

${deploymentSummary}`,
    temperature: 0.2,
  });

  const latencyMs = Date.now() - startTime;

  const response: VercelBotResponse = {
    ok: true,
    deployments,
    advice: {
      decision: advice.decision,
      reason: advice.reason,
      candidateRollbackId: advice.candidateRollbackId,
    },
  };

  await logBotExecution({
    botId: BOT_ID,
    executionType: 'deployment_suggest',
    requestPayload,
    responsePayload: response,
    aiModel: 'gpt-4o-mini',
    tokensUsed: usage?.totalTokens,
    latencyMs,
    status: 'success',
  });

  return NextResponse.json(response);
}

/**
 * GET handler for health check
 */
export async function GET() {
  await updateBotHeartbeat(BOT_ID);
  return NextResponse.json({
    ok: true,
    bot: BOT_ID,
    status: 'healthy',
    timestamp: new Date().toISOString(),
  });
}
