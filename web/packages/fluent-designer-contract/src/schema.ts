import { z } from 'zod';

export const DesignIntentSchema = z.object({
  productType: z.string(),
  audience: z.string(),
  platform: z.enum(['web', 'desktop', 'mobile']),
  tone: z.enum(['microsoft-native', 'enterprise', 'productivity', 'admin']),
});

export const DesignBriefSchema = z.object({
  title: z.string().min(1),
  objective: z.string().min(1),
  constraints: z.array(z.string()),
  intent: DesignIntentSchema,
  requiredRegions: z.array(z.string()),
});

export const ComponentRecommendationSchema = z.object({
  slot: z.string(),
  fluentComponent: z.string(),
  rationale: z.string(),
  notes: z.array(z.string()).optional(),
});

export const SectionProposalSchema = z.object({
  id: z.string(),
  title: z.string(),
  purpose: z.string(),
  components: z.array(ComponentRecommendationSchema),
});

export const ScreenProposalSchema = z.object({
  pageType: z.string(),
  hierarchy: z.array(z.string()),
  sections: z.array(SectionProposalSchema),
  accessibilityNotes: z.array(z.string()),
  tokenGuidance: z.array(z.string()),
});

export const CritiqueItemSchema = z.object({
  id: z.string(),
  severity: z.enum(['info', 'warning', 'error']),
  area: z.enum(['hierarchy', 'spacing', 'component-choice', 'a11y', 'tone']),
  issue: z.string(),
  recommendation: z.string(),
});

export const DesignCritiqueSchema = z.object({
  summary: z.string(),
  items: z.array(CritiqueItemSchema),
});

export const HandoffArtifactSchema = z.object({
  implementationSummary: z.string(),
  componentMap: z.array(
    z.object({
      region: z.string(),
      component: z.string(),
      reason: z.string(),
    })
  ),
  acceptanceCriteria: z.array(z.string()),
  codingAgentPrompt: z.string(),
});

export const ResponseMetadataSchema = z.object({
  provider: z.enum(['mock', 'foundry']),
  agentId: z.string().optional(),
  conversationId: z.string().optional(),
  responseId: z.string().optional(),
  correlationId: z.string(),
});

export const DesignerAgentResponseSchema = z.object({
  mode: z.enum(['generate', 'critique', 'refine', 'handoff']),
  brief: DesignBriefSchema,
  proposal: ScreenProposalSchema.optional(),
  critique: DesignCritiqueSchema.optional(),
  handoff: HandoffArtifactSchema.optional(),
  rationale: z.array(z.string()),
  warnings: z.array(z.string()),
  metadata: ResponseMetadataSchema.optional(),
});

export const DesignerAgentRequestSchema = z.object({
  mode: z.enum(['generate', 'critique', 'refine', 'handoff']),
  brief: DesignBriefSchema,
  conversationId: z.string().optional(),
  correlationId: z.string().optional(),
});
