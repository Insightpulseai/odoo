/**
 * Skill implementations — starter skills for the Copilot Skills framework.
 */

export { knowledgeSearchDefinition, executeKnowledgeSearch } from './knowledge-search.js';
export { businessSummarizeDefinition, executeBusinessSummarize } from './business-summarize.js';
export { workflowExtractActionsDefinition, executeWorkflowExtractActions } from './workflow-extract-actions.js';
export { platformRouteRequestDefinition, executePlatformRouteRequest } from './platform-route-request.js';

import type { SkillDefinition } from '@ipai/builder-contract';
import { knowledgeSearchDefinition } from './knowledge-search.js';
import { businessSummarizeDefinition } from './business-summarize.js';
import { workflowExtractActionsDefinition } from './workflow-extract-actions.js';
import { platformRouteRequestDefinition } from './platform-route-request.js';

/** All starter skill definitions — register these at startup. */
export const STARTER_SKILLS: SkillDefinition[] = [
  knowledgeSearchDefinition,
  businessSummarizeDefinition,
  workflowExtractActionsDefinition,
  platformRouteRequestDefinition,
];
