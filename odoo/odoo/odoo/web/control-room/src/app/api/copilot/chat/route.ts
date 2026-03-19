import { NextRequest, NextResponse } from 'next/server';
import { z } from 'zod';

// Zod schemas for request validation
const copilotMessageSchema = z.object({
  id: z.string(),
  role: z.enum(['user', 'assistant', 'system']),
  content: z.string(),
  createdAt: z.string(),
  meta: z.object({
    source: z.string().optional(),
    actionLabel: z.string().optional(),
  }).optional(),
});

const copilotProfileSchema = z.object({
  id: z.string(),
  name: z.string(),
  slug: z.string(),
  modelLabel: z.string().optional(),
  targetModel: z.string(),
});

const copilotRecordSummarySchema = z.object({
  id: z.union([z.string(), z.number()]),
  model: z.string(),
  displayName: z.string(),
  icon: z.string().optional(),
  fields: z.array(z.object({
    key: z.string(),
    label: z.string(),
    value: z.union([z.string(), z.number(), z.null()]),
  })),
});

const chatRequestSchema = z.object({
  profile: copilotProfileSchema,
  record: copilotRecordSummarySchema,
  messages: z.array(copilotMessageSchema),
  input: z.string(),
  options: z.object({
    fromActionId: z.string().optional(),
  }).optional(),
});

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const parsed = chatRequestSchema.safeParse(body);

    if (!parsed.success) {
      return NextResponse.json(
        { error: 'Invalid request', details: parsed.error.flatten() },
        { status: 400 }
      );
    }

    const { profile, record, messages, input, options } = parsed.data;

    // Build context from record fields
    const recordContext = record.fields
      .map((f) => `${f.label}: ${f.value ?? 'N/A'}`)
      .join('\n');

    // Build conversation history
    const conversationHistory = messages
      .filter((m) => m.role !== 'system')
      .map((m) => `${m.role === 'user' ? 'User' : 'Assistant'}: ${m.content}`)
      .join('\n\n');

    // Build system prompt
    const systemPrompt = `You are an AI assistant for ${profile.name}.
You are helping with a ${record.model} record: ${record.displayName}.

Current record context:
${recordContext}

Provide helpful, accurate, and concise responses. Focus on actionable insights.
When suggesting actions, be specific about what should be done and why.`;

    // TODO: Replace with actual LLM API call (Claude, GPT-4, etc.)
    // For now, return a stub response that demonstrates the system
    const reply = await generateStubResponse({
      systemPrompt,
      conversationHistory,
      input,
      profile,
      record,
      options,
    });

    return NextResponse.json({ reply });
  } catch (error) {
    console.error('Copilot chat error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

interface StubResponseParams {
  systemPrompt: string;
  conversationHistory: string;
  input: string;
  profile: z.infer<typeof copilotProfileSchema>;
  record: z.infer<typeof copilotRecordSummarySchema>;
  options?: z.infer<typeof chatRequestSchema>['options'];
}

async function generateStubResponse(params: StubResponseParams): Promise<string> {
  const { input, profile, record, options } = params;

  // Stub responses based on action type
  if (options?.fromActionId === 'summarize_record') {
    return `## Summary: ${record.displayName}

Here's an overview of this ${record.model} record:

${record.fields.map((f) => `- **${f.label}**: ${f.value ?? 'Not specified'}`).join('\n')}

### Key Observations
- Record type: ${record.model}
- Profile context: ${profile.name}

*Note: This is a stub response. Connect to your LLM API for real insights.*`;
  }

  if (options?.fromActionId === 'explain_numbers') {
    const numericFields = record.fields.filter(
      (f) => typeof f.value === 'number' || (typeof f.value === 'string' && !isNaN(parseFloat(f.value)))
    );

    return `## Numeric Analysis: ${record.displayName}

${numericFields.length > 0
  ? numericFields.map((f) => `- **${f.label}**: ${f.value}`).join('\n')
  : 'No numeric fields found in this record.'}

*Note: This is a stub response. Connect to your LLM API for real financial analysis.*`;
  }

  if (options?.fromActionId === 'draft_email') {
    return `## Draft Email

**Subject**: Update on ${record.displayName}

Dear [Stakeholder],

I wanted to provide you with a brief update regarding ${record.displayName}.

**Current Status:**
${record.fields.slice(0, 3).map((f) => `- ${f.label}: ${f.value ?? 'N/A'}`).join('\n')}

Please let me know if you have any questions or need additional information.

Best regards,
[Your Name]

*Note: This is a stub response. Connect to your LLM API for personalized drafts.*`;
  }

  if (options?.fromActionId === 'next_steps') {
    return `## Recommended Next Steps for ${record.displayName}

1. **Review current status** - Verify all fields are up to date
2. **Validate data integrity** - Cross-check with source systems
3. **Identify blockers** - Note any dependencies or issues
4. **Schedule follow-up** - Set reminder for next review
5. **Document decisions** - Record any changes made

*Note: This is a stub response. Connect to your LLM API for context-aware recommendations.*`;
  }

  // Default free-form response
  return `Thank you for your question about ${record.displayName}.

**Your query:** "${input}"

I'm currently running in stub mode. To get real AI-powered responses:

1. Configure your LLM API credentials (Claude, GPT-4, etc.)
2. Update this endpoint to call your chosen model
3. The system will use the following context:
   - Profile: ${profile.name} (${profile.slug})
   - Record: ${record.displayName}
   - Model: ${record.model}

*Replace this stub with your actual LLM integration for production use.*`;
}
