export type DesignerMode = 'generate' | 'critique' | 'refine' | 'handoff';

export type Severity = 'info' | 'warning' | 'error';

export interface DesignIntent {
  productType: string;
  audience: string;
  platform: 'web' | 'desktop' | 'mobile';
  tone: 'microsoft-native' | 'enterprise' | 'productivity' | 'admin';
}

export interface DesignBrief {
  title: string;
  objective: string;
  constraints: string[];
  intent: DesignIntent;
  requiredRegions: string[];
}

export interface ComponentRecommendation {
  slot: string;
  fluentComponent: string;
  rationale: string;
  notes?: string[];
}

export interface SectionProposal {
  id: string;
  title: string;
  purpose: string;
  components: ComponentRecommendation[];
}

export interface ScreenProposal {
  pageType: string;
  hierarchy: string[];
  sections: SectionProposal[];
  accessibilityNotes: string[];
  tokenGuidance: string[];
}

export interface CritiqueItem {
  id: string;
  severity: Severity;
  area: 'hierarchy' | 'spacing' | 'component-choice' | 'a11y' | 'tone';
  issue: string;
  recommendation: string;
}

export interface DesignCritique {
  summary: string;
  items: CritiqueItem[];
}

export interface HandoffArtifact {
  implementationSummary: string;
  componentMap: Array<{
    region: string;
    component: string;
    reason: string;
  }>;
  acceptanceCriteria: string[];
  codingAgentPrompt: string;
}

export interface ResponseMetadata {
  provider: 'mock' | 'foundry';
  agentId?: string;
  conversationId?: string;
  responseId?: string;
  correlationId: string;
}

export interface DesignerAgentResponse {
  mode: DesignerMode;
  brief: DesignBrief;
  proposal?: ScreenProposal;
  critique?: DesignCritique;
  handoff?: HandoffArtifact;
  rationale: string[];
  warnings: string[];
  metadata?: ResponseMetadata;
}

export interface DesignerAgentRequest {
  mode: DesignerMode;
  brief: DesignBrief;
  conversationId?: string;
  correlationId?: string;
}

export interface DesignerAgentError {
  code: string;
  message: string;
  details?: Record<string, unknown>;
}

export interface ComponentTree {
  root: string;
  children: Array<{
    component: string;
    slot: string;
    children?: ComponentTree['children'];
  }>;
}

export interface RefineConstraints {
  additions: string[];
  removals: string[];
  modifications: string[];
}

export interface ServiceHealth {
  status: 'healthy' | 'degraded' | 'unavailable';
  adapter: string;
  timestamp: string;
}
