import type {
  DesignBrief,
  DesignerAgentResponse,
  DesignerMode,
  ComponentTree,
  ScreenProposal,
  RefineConstraints,
  ServiceHealth,
} from '@repo/fluent-designer-contract';

export interface DesignerAgentService {
  generate(brief: DesignBrief): Promise<DesignerAgentResponse>;
  critique(tree: ComponentTree): Promise<DesignerAgentResponse>;
  refine(
    proposal: ScreenProposal,
    constraints: RefineConstraints
  ): Promise<DesignerAgentResponse>;
  handoff(proposal: ScreenProposal): Promise<DesignerAgentResponse>;
  health(): Promise<ServiceHealth>;
}
