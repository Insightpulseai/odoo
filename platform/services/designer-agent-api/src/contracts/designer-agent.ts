// Re-export from the shared contract package — single source of truth
export type {
  DesignerMode,
  DesignIntent,
  DesignBrief,
  ComponentRecommendation,
  SectionProposal,
  ScreenProposal,
  CritiqueItem,
  DesignCritique,
  HandoffArtifact,
  DesignerAgentResponse,
  DesignerAgentRequest,
  DesignerAgentError,
  ResponseMetadata,
} from '@repo/fluent-designer-contract';

export {
  DesignerAgentResponseSchema,
  DesignerAgentRequestSchema,
  ResponseMetadataSchema,
} from '@repo/fluent-designer-contract';
