/**
 * SkillRegistry — in-memory registry of available Copilot Skills.
 *
 * Skills are registered at startup and immutable at runtime.
 * The registry is the source of truth for what skills exist.
 */

import type { SkillDefinition, SkillType } from '@ipai/builder-contract';

export class SkillRegistry {
  private skills = new Map<string, SkillDefinition>();

  /** Register a skill definition. Overwrites if slug already exists. */
  register(skill: SkillDefinition): void {
    this.skills.set(skill.slug, skill);
  }

  /** Get a skill by slug. Returns undefined if not found. */
  get(slug: string): SkillDefinition | undefined {
    return this.skills.get(slug);
  }

  /** List all registered skills. */
  list(): SkillDefinition[] {
    return Array.from(this.skills.values());
  }

  /** List skills filtered by type. */
  listByType(type: SkillType): SkillDefinition[] {
    return this.list().filter(s => s.type === type);
  }

  /** Check if a skill is registered. */
  has(slug: string): boolean {
    return this.skills.has(slug);
  }

  /** Number of registered skills. */
  get size(): number {
    return this.skills.size;
  }
}
