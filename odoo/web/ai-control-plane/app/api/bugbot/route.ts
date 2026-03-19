import { NextRequest, NextResponse } from 'next/server';
import { createOpenAI } from '@ai-sdk/openai';
import { generateText } from 'ai';
import { BugBotPayloadSchema, BugBotResponse, DODropletsResponse } from '@/lib/types';
import { getSecret, logBotExecution, updateBotHeartbeat } from '@/lib/supabase';

const BOT_ID = 'bugbot';

/**
 * BugBot API Route - AI SRE & debugging assistant
 *
 * Accepts bug/build/log payloads, queries DigitalOcean for infrastructure context,
 * and uses Vercel AI Gateway + OpenAI for analysis.
 *
 * POST /api/bugbot
 */
export async function POST(req: NextRequest) {
  const startTime = Date.now();
  let requestPayload: unknown;

  try {
    // Parse and validate request
    const json = await req.json();
    requestPayload = json;
    const payload = BugBotPayloadSchema.parse(json);

    // Update heartbeat
    await updateBotHeartbeat(BOT_ID);

    // Get API tokens from Supabase Vault
    const [doToken, openaiKey] = await Promise.all([
      getSecret('DIGITALOCEAN_API_TOKEN', BOT_ID, 'read'),
      getSecret('OPENAI_API_KEY', BOT_ID, 'read'),
    ]);

    // Query DigitalOcean droplets for infrastructure context
    let dropletsSummary = 'DigitalOcean not queried';
    if (doToken) {
      try {
        const doApiBase = process.env.DIGITALOCEAN_API_BASE || 'https://api.digitalocean.com/v2';
        const resp = await fetch(`${doApiBase}/droplets`, {
          headers: {
            Authorization: `Bearer ${doToken}`,
            'Content-Type': 'application/json',
          },
        });

        if (resp.ok) {
          const data: DODropletsResponse = await resp.json();
          const dropletInfo = data.droplets.map(
            (d) => `${d.name}(${d.status}, ${d.region.slug})`
          );
          dropletsSummary = dropletInfo.length > 0
            ? `Active droplets: ${dropletInfo.join(', ')}`
            : 'No droplets found';
        } else {
          dropletsSummary = `DigitalOcean API error: ${resp.status}`;
        }
      } catch (doError) {
        dropletsSummary = `DigitalOcean fetch failed: ${(doError as Error).message}`;
      }
    }

    // Initialize OpenAI via Vercel AI Gateway (or direct if no gateway configured)
    const apiKey = openaiKey || process.env.OPENAI_API_KEY;
    if (!apiKey) {
      throw new Error('OpenAI API key not available');
    }

    const openai = createOpenAI({
      apiKey,
      // If using Vercel AI Gateway, the baseURL can be configured via env
      baseURL: process.env.AI_GATEWAY_URL || undefined,
    });

    // Analyze the bug using AI
    const systemPrompt = `You are BugBot, an AI SRE & debugging assistant for a multi-cloud stack.

Infrastructure: DigitalOcean (compute), Vercel (deployments), Supabase (database/auth), Odoo CE 18 (ERP), n8n (workflows), MCP servers (integrations).

Your job is to analyze bugs, errors, and issues and provide:
1. PROBABLE CAUSE: Root cause analysis (1-2 sentences)
2. IMPACT: Business and system impact assessment
3. RECOMMENDED ACTIONS: Concrete, actionable steps to resolve

Be concise and actionable. No fluff.`;

    const userPrompt = `
Source: ${payload.source}
Service: ${payload.service || 'unknown'}
Severity: ${payload.severity || 'unspecified'}
Tags: ${(payload.tags || []).join(', ') || 'none'}

Error Message:
${payload.message}

${payload.stack ? `Stack Trace:\n${payload.stack}` : ''}

Infrastructure Context:
${dropletsSummary}

${payload.metadata ? `Additional Metadata:\n${JSON.stringify(payload.metadata, null, 2)}` : ''}
`.trim();

    const { text: analysis, usage } = await generateText({
      model: openai('gpt-4o-mini'),
      system: systemPrompt,
      prompt: userPrompt,
      temperature: 0.2,
      maxTokens: 1500,
    });

    // Parse the analysis into structured sections
    const sections = parseAnalysis(analysis);

    const latencyMs = Date.now() - startTime;

    const response: BugBotResponse = {
      ok: true,
      bug_analysis: analysis,
      probable_cause: sections.probableCause,
      impact: sections.impact,
      recommended_actions: sections.recommendedActions,
      infra_context: dropletsSummary,
    };

    // Log successful execution
    await logBotExecution({
      botId: BOT_ID,
      executionType: 'bug_analysis',
      source: payload.source,
      requestPayload: requestPayload as object,
      responsePayload: response,
      aiModel: 'gpt-4o-mini',
      tokensUsed: usage?.totalTokens,
      latencyMs,
      status: 'success',
    });

    return NextResponse.json(response);
  } catch (err) {
    const latencyMs = Date.now() - startTime;
    const errorMessage = err instanceof Error ? err.message : 'Unknown error';

    console.error('BugBot error:', err);

    // Log failed execution
    await logBotExecution({
      botId: BOT_ID,
      executionType: 'bug_analysis',
      source: 'unknown',
      requestPayload: requestPayload as object,
      latencyMs,
      status: 'error',
      errorMessage,
    });

    return NextResponse.json(
      { ok: false, error: errorMessage } satisfies BugBotResponse,
      { status: 500 }
    );
  }
}

/**
 * Parse AI analysis into structured sections
 */
function parseAnalysis(analysis: string): {
  probableCause?: string;
  impact?: string;
  recommendedActions?: string[];
} {
  const lines = analysis.split('\n');
  let probableCause: string | undefined;
  let impact: string | undefined;
  const recommendedActions: string[] = [];

  let currentSection = '';

  for (const line of lines) {
    const trimmed = line.trim();

    if (trimmed.toLowerCase().includes('probable cause')) {
      currentSection = 'cause';
      continue;
    } else if (trimmed.toLowerCase().includes('impact')) {
      currentSection = 'impact';
      continue;
    } else if (trimmed.toLowerCase().includes('recommended') || trimmed.toLowerCase().includes('actions')) {
      currentSection = 'actions';
      continue;
    }

    if (!trimmed) continue;

    switch (currentSection) {
      case 'cause':
        probableCause = (probableCause ? probableCause + ' ' : '') + trimmed;
        break;
      case 'impact':
        impact = (impact ? impact + ' ' : '') + trimmed;
        break;
      case 'actions':
        // Parse numbered or bulleted items
        const actionMatch = trimmed.match(/^[\d\-\*\•]\s*\.?\s*(.+)/);
        if (actionMatch) {
          recommendedActions.push(actionMatch[1]);
        } else if (trimmed.length > 0) {
          recommendedActions.push(trimmed);
        }
        break;
    }
  }

  return { probableCause, impact, recommendedActions };
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
