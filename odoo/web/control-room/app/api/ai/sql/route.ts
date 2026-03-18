import { NextRequest, NextResponse } from 'next/server';
import { getObservabilitySchema } from '@/lib/supabase/observability';

const OPENAI_API_KEY = process.env.OPENAI_API_KEY;
const ENABLE_AI_QUERIES = process.env.NEXT_PUBLIC_ENABLE_AI_QUERIES === 'true';

/**
 * POST /api/ai/sql
 * Generate SQL from natural language prompt using AI
 */
export async function POST(request: NextRequest) {
  if (!ENABLE_AI_QUERIES) {
    return NextResponse.json(
      { error: 'AI queries are not enabled' },
      { status: 403 }
    );
  }

  if (!OPENAI_API_KEY) {
    return NextResponse.json(
      { error: 'OpenAI API key not configured' },
      { status: 500 }
    );
  }

  try {
    const body = await request.json();
    const { prompt } = body;

    if (!prompt) {
      return NextResponse.json(
        { error: 'Prompt is required' },
        { status: 400 }
      );
    }

    // Get schema for context
    const schema = await getObservabilitySchema();

    // Build system prompt
    const systemPrompt = `You are an expert SQL assistant. Given the following database schema, write a SQL query that answers the user's question.

Return ONLY the SQL query, with no explanations, markdown formatting, or additional text.

The query should be safe (SELECT only, no modifications) and optimized.

Schema:
${schema}`;

    // Call OpenAI
    const response = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${OPENAI_API_KEY}`,
      },
      body: JSON.stringify({
        model: 'gpt-4o-mini',
        messages: [
          { role: 'system', content: systemPrompt },
          { role: 'user', content: prompt },
        ],
        temperature: 0,
        max_tokens: 1000,
      }),
    });

    if (!response.ok) {
      const error = await response.text();
      console.error('OpenAI error:', error);
      throw new Error('Failed to generate SQL');
    }

    const data = await response.json();
    const sql = data.choices?.[0]?.message?.content?.trim();

    if (!sql) {
      return NextResponse.json(
        { error: 'Could not generate SQL from the prompt' },
        { status: 500 }
      );
    }

    // Basic validation - ensure it's a SELECT query
    if (!sql.toLowerCase().startsWith('select')) {
      return NextResponse.json(
        { error: 'Generated query is not a SELECT statement' },
        { status: 400 }
      );
    }

    return NextResponse.json({ sql });
  } catch (error) {
    console.error('AI SQL generation error:', error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Failed to generate SQL' },
      { status: 500 }
    );
  }
}
