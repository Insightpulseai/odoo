import { NextResponse } from 'next/server'
import OpenAI from 'openai'
import createClient from 'openapi-fetch'

import type { paths } from '@/lib/management-api-schema'
import { listTablesSql } from '@/lib/pg-meta'
import { getOrCreateRequestId, correlationHeaders } from '@/lib/http/correlation'

// Prefer Vercel AI Gateway (100+ models, unified billing) over direct OpenAI.
// AI Gateway endpoint: https://ai-gateway.vercel.sh/v1
// Key: AI_GATEWAY_API_KEY (generate at vercel.com/[team]/~/ai-gateway/api-keys)
// Fallback: direct OpenAI via OPENAI_API_KEY
const aiGatewayKey = process.env.AI_GATEWAY_API_KEY
const openaiKey = process.env.OPENAI_API_KEY

const openai = aiGatewayKey
  ? new OpenAI({
      apiKey: aiGatewayKey,
      baseURL: 'https://ai-gateway.vercel.sh/v1',
    })
  : openaiKey
    ? new OpenAI({ apiKey: openaiKey })
    : null

// Use a model available on the gateway, or gpt-4o-mini as direct fallback.
// AI Gateway model format: "provider/model-name"
const AI_MODEL = aiGatewayKey
  ? 'anthropic/claude-haiku-4-5-20251001'
  : 'gpt-4o-mini'

const supabaseClient = createClient<paths>({
  baseUrl: 'https://api.supabase.com',
  headers: {
    Authorization: `Bearer ${process.env.SUPABASE_MANAGEMENT_API_TOKEN}`,
  },
})

async function getDbSchema(projectRef: string) {
  const token = process.env.SUPABASE_MANAGEMENT_API_TOKEN
  if (!token) {
    throw new Error('Supabase Management API token is not configured.')
  }

  const sql = listTablesSql()

  const { data, error } = await supabaseClient.POST('/v1/projects/{ref}/database/query', {
    params: { path: { ref: projectRef } },
    body: { query: sql, read_only: true },
  })

  if (error) throw error
  return data as any
}

function formatSchemaForPrompt(schema: any) {
  let schemaString = ''
  if (schema && Array.isArray(schema)) {
    schema.forEach((table: any) => {
      const columnInfo = table.columns.map((c: any) => `${c.name} (${c.data_type})`)
      schemaString += `Table "${table.name}" has columns: ${columnInfo.join(', ')}.\n`
    })
  }
  return schemaString
}

export async function POST(request: Request) {
  const rid = getOrCreateRequestId(request.headers.get('x-request-id'))
  const headers = correlationHeaders(rid)

  try {
    if (!openai) {
      return NextResponse.json(
        { message: 'AI not configured. Set AI_GATEWAY_API_KEY or OPENAI_API_KEY in .env.local.' },
        { status: 503, headers }
      )
    }

    const { prompt, projectRef } = await request.json()

    if (!prompt) {
      return NextResponse.json({ message: 'Prompt is required.' }, { status: 400, headers })
    }
    if (!projectRef) {
      return NextResponse.json({ message: 'projectRef is required.' }, { status: 400, headers })
    }

    // 1. Get database schema
    const schema = await getDbSchema(projectRef)
    const formattedSchema = formatSchemaForPrompt(schema)

    // 2. Build system prompt
    const systemPrompt = `You are an expert SQL assistant. Given the following database schema, write a SQL query that answers the user's question. Return only the SQL query, do not include any explanations or markdown.\n\nSchema:\n${formattedSchema}`

    // 3. Call AI Gateway (OpenAI-compatible chat completions)
    const completion = await openai.chat.completions.create({
      model: AI_MODEL,
      messages: [
        { role: 'system', content: systemPrompt },
        { role: 'user', content: prompt },
      ],
      temperature: 0,
    })

    const sql = completion.choices[0]?.message?.content?.trim()

    if (!sql) {
      return NextResponse.json(
        { message: 'Could not generate SQL from the prompt.' },
        { status: 500, headers }
      )
    }

    // 4. Return the generated SQL
    return NextResponse.json({ sql }, { headers })
  } catch (error: any) {
    console.error('AI SQL generation error:', error)
    const errorMessage = error.message || 'An unexpected error occurred.'
    const status = error.status || error.response?.status || 500
    return NextResponse.json({ message: errorMessage }, { status, headers })
  }
}
