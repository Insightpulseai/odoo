/**
 * SkillRouter — resolves skill invocations to definitions and validates permissions.
 *
 * Enforces:
 * - Skill existence (slug must be registered)
 * - Deprecation gate (deprecated skills are not routed)
 * - Permission validation (skill's allowedTools must be in caller's permittedTools)
 */

import type { SkillInvocation, SkillDefinition } from '@ipai/builder-contract';
import type { SkillRegistry } from './skill-registry.js';

export class SkillRouter {
  constructor(private registry: SkillRegistry) {}

  /**
   * Resolve an invocation to a skill definition.
   * Returns null if the skill doesn't exist or is deprecated.
   */
  resolve(invocation: SkillInvocation): SkillDefinition | null {
    const skill = this.registry.get(invocation.skillSlug);
    if (!skill) return null;
    if (skill.deprecated) return null;
    return skill;
  }

  /**
   * Validate that the caller has permission to execute a skill.
   * read_only skills are always permitted.
   * Other capabilities require the caller's permittedTools to include all of the skill's allowedTools.
   */
  validatePermissions(skill: SkillDefinition, context: { permittedTools: string[] }): boolean {
    if (skill.capability === 'read_only') return true;
    return skill.allowedTools.every(t => context.permittedTools.includes(t));
  }
}
