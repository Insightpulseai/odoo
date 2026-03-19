/**
 * Skills framework tests — validates registration, routing, execution, and edge cases.
 *
 * Proves:
 * 1. Skill registration and lookup works
 * 2. Skill routing resolves correctly
 * 3. Knowledge search executes through mock client
 * 4. Invalid skill slug returns null
 * 5. Deprecated skills are not routed
 * 6. Permission validation works
 * 7. executeSkill flows through the orchestrator
 */

import { describe, it } from 'node:test';
import { strict as assert } from 'node:assert';
import { randomUUID } from 'node:crypto';
import { resolve } from 'node:path';
import type {
  SkillDefinition,
  SkillInvocation,
  SkillExecutionContext,
} from '@ipai/builder-contract';
import { MockFoundryClient } from '@ipai/builder-foundry-client';
import {
  SkillRegistry,
  SkillRouter,
  Orchestrator,
  ConsoleAuditEmitter,
  knowledgeSearchDefinition,
  businessSummarizeDefinition,
  workflowExtractActionsDefinition,
  platformRouteRequestDefinition,
  STARTER_SKILLS,
  executeKnowledgeSearch,
} from '@ipai/builder-orchestrator';

const AGENTS_ROOT = resolve(__dirname, '../../../../../agents');

function makeContext(overrides: Partial<SkillExecutionContext> = {}): SkillExecutionContext {
  return {
    requestId: randomUUID(),
    userId: 'test-user',
    tenantId: 'test-tenant',
    companyId: 1,
    mode: 'PROD-ADVISORY',
    permittedTools: [],
    correlationId: randomUUID(),
    ...overrides,
  };
}

describe('SkillRegistry', () => {
  it('should register and retrieve a skill', () => {
    const registry = new SkillRegistry();
    registry.register(knowledgeSearchDefinition);

    assert.ok(registry.has('knowledge.search'));
    assert.equal(registry.get('knowledge.search')?.name, 'Knowledge Search');
    assert.equal(registry.size, 1);
  });

  it('should list all registered skills', () => {
    const registry = new SkillRegistry();
    for (const skill of STARTER_SKILLS) {
      registry.register(skill);
    }

    assert.equal(registry.list().length, 4);
  });

  it('should filter skills by type', () => {
    const registry = new SkillRegistry();
    for (const skill of STARTER_SKILLS) {
      registry.register(skill);
    }

    const retrievalSkills = registry.listByType('retrieval');
    assert.equal(retrievalSkills.length, 1);
    assert.equal(retrievalSkills[0].slug, 'knowledge.search');

    const routingSkills = registry.listByType('routing');
    assert.equal(routingSkills.length, 1);
    assert.equal(routingSkills[0].slug, 'platform.route-request');
  });

  it('should return undefined for unknown slug', () => {
    const registry = new SkillRegistry();
    assert.equal(registry.get('nonexistent.skill'), undefined);
    assert.equal(registry.has('nonexistent.skill'), false);
  });
});

describe('SkillRouter', () => {
  it('should resolve a valid skill invocation', () => {
    const registry = new SkillRegistry();
    registry.register(knowledgeSearchDefinition);
    const router = new SkillRouter(registry);

    const invocation: SkillInvocation = {
      skillSlug: 'knowledge.search',
      input: { query: 'test' },
      context: makeContext(),
    };

    const resolved = router.resolve(invocation);
    assert.ok(resolved);
    assert.equal(resolved.slug, 'knowledge.search');
  });

  it('should return null for unknown skill slug', () => {
    const registry = new SkillRegistry();
    const router = new SkillRouter(registry);

    const invocation: SkillInvocation = {
      skillSlug: 'nonexistent.skill',
      input: {},
      context: makeContext(),
    };

    const resolved = router.resolve(invocation);
    assert.equal(resolved, null);
  });

  it('should return null for deprecated skills', () => {
    const registry = new SkillRegistry();
    const deprecatedSkill: SkillDefinition = {
      ...knowledgeSearchDefinition,
      slug: 'legacy.search',
      deprecated: true,
    };
    registry.register(deprecatedSkill);
    const router = new SkillRouter(registry);

    const invocation: SkillInvocation = {
      skillSlug: 'legacy.search',
      input: { query: 'test' },
      context: makeContext(),
    };

    const resolved = router.resolve(invocation);
    assert.equal(resolved, null);
  });

  it('should validate permissions for read_only skills', () => {
    const registry = new SkillRegistry();
    registry.register(knowledgeSearchDefinition);
    const router = new SkillRouter(registry);

    // read_only skills always pass permission check, even with empty permittedTools
    const result = router.validatePermissions(knowledgeSearchDefinition, { permittedTools: [] });
    assert.equal(result, true);
  });

  it('should validate permissions for read_write skills', () => {
    const registry = new SkillRegistry();
    const readWriteSkill: SkillDefinition = {
      ...knowledgeSearchDefinition,
      slug: 'write.skill',
      capability: 'read_write',
      allowedTools: ['write_record', 'delete_record'],
    };
    registry.register(readWriteSkill);
    const router = new SkillRouter(registry);

    // Should fail without required tools
    assert.equal(
      router.validatePermissions(readWriteSkill, { permittedTools: [] }),
      false,
    );

    // Should fail with partial tools
    assert.equal(
      router.validatePermissions(readWriteSkill, { permittedTools: ['write_record'] }),
      false,
    );

    // Should pass with all required tools
    assert.equal(
      router.validatePermissions(readWriteSkill, {
        permittedTools: ['write_record', 'delete_record'],
      }),
      true,
    );
  });
});

describe('Skill Execution', () => {
  it('should execute knowledge search through mock client', async () => {
    const mockClient = new MockFoundryClient();
    const invocation: SkillInvocation = {
      skillSlug: 'knowledge.search',
      input: { query: 'What is Odoo CE?' },
      context: makeContext(),
    };

    const result = await executeKnowledgeSearch(invocation, mockClient);

    assert.equal(result.success, true);
    assert.equal(result.skillSlug, 'knowledge.search');
    assert.ok(result.output['answer'], 'Must have an answer');
    assert.ok(typeof result.latencyMs === 'number');
    assert.ok(result.latencyMs >= 0);
    assert.ok(result.tokensUsed, 'Must report token usage');
    assert.ok(result.tokensUsed!.prompt > 0);
    assert.ok(result.tokensUsed!.completion > 0);
  });

  it('should execute skill through orchestrator.executeSkill', async () => {
    const mockClient = new MockFoundryClient();
    const auditEmitter = new ConsoleAuditEmitter();

    const orchestrator = new Orchestrator({
      agentsRoot: AGENTS_ROOT,
      agentProfile: 'ipai-odoo-copilot-azure',
      foundryClient: mockClient,
      auditEmitter,
    });
    await orchestrator.initialize();

    // Register starter skills
    const registry = orchestrator.getSkillRegistry();
    for (const skill of STARTER_SKILLS) {
      registry.register(skill);
    }

    const result = await orchestrator.executeSkill({
      skillSlug: 'knowledge.search',
      input: { query: 'How does Odoo handle invoicing?' },
      context: makeContext(),
    });

    assert.equal(result.success, true);
    assert.equal(result.skillSlug, 'knowledge.search');
    assert.ok(result.output['answer']);

    // Verify audit events were emitted for skill execution
    const auditBuffer = auditEmitter.getBuffer();
    const skillEvents = auditBuffer.filter(
      e => e.dimensions && (e.dimensions as Record<string, unknown>)['skill_slug'] === 'knowledge.search'
    );
    assert.ok(skillEvents.length >= 2, 'At least 2 skill audit events (invocation + result)');
  });

  it('should return error for unregistered skill via orchestrator', async () => {
    const mockClient = new MockFoundryClient();
    const orchestrator = new Orchestrator({
      agentsRoot: AGENTS_ROOT,
      agentProfile: 'ipai-odoo-copilot-azure',
      foundryClient: mockClient,
    });
    await orchestrator.initialize();

    const result = await orchestrator.executeSkill({
      skillSlug: 'nonexistent.skill',
      input: {},
      context: makeContext(),
    });

    assert.equal(result.success, false);
    assert.ok(result.error);
    assert.equal(result.error!.code, 'SKILL_NOT_FOUND');
    assert.equal(result.error!.retryable, false);
  });

  it('should not route deprecated skill via orchestrator', async () => {
    const mockClient = new MockFoundryClient();
    const orchestrator = new Orchestrator({
      agentsRoot: AGENTS_ROOT,
      agentProfile: 'ipai-odoo-copilot-azure',
      foundryClient: mockClient,
    });
    await orchestrator.initialize();

    // Register a deprecated skill
    const registry = orchestrator.getSkillRegistry();
    registry.register({
      ...knowledgeSearchDefinition,
      slug: 'deprecated.search',
      deprecated: true,
    });

    const result = await orchestrator.executeSkill({
      skillSlug: 'deprecated.search',
      input: { query: 'test' },
      context: makeContext(),
    });

    assert.equal(result.success, false);
    assert.equal(result.error!.code, 'SKILL_NOT_FOUND');
  });
});

describe('Starter Skill Definitions', () => {
  it('should have all four starter skills with correct types', () => {
    assert.equal(STARTER_SKILLS.length, 4);

    const slugs = STARTER_SKILLS.map(s => s.slug).sort();
    assert.deepEqual(slugs, [
      'business.summarize',
      'knowledge.search',
      'platform.route-request',
      'workflow.extract-actions',
    ]);
  });

  it('should have all starter skills as read_only v0.1', () => {
    for (const skill of STARTER_SKILLS) {
      assert.equal(skill.capability, 'read_only', `${skill.slug} must be read_only`);
      assert.equal(skill.version, '0.1.0', `${skill.slug} must be v0.1.0`);
      assert.equal(skill.deprecated, false, `${skill.slug} must not be deprecated`);
    }
  });

  it('should have valid schemas on all starter skills', () => {
    for (const skill of STARTER_SKILLS) {
      assert.ok(skill.inputSchema, `${skill.slug} must have inputSchema`);
      assert.ok(skill.outputSchema, `${skill.slug} must have outputSchema`);
      assert.ok(skill.inputSchema['type'] === 'object', `${skill.slug} inputSchema must be object`);
      assert.ok(skill.outputSchema['type'] === 'object', `${skill.slug} outputSchema must be object`);
    }
  });
});
