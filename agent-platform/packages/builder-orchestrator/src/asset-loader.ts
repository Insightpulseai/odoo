/**
 * AssetLoader — loads agent assets from the agents/ repository.
 *
 * Reads:
 * - System prompt from agents/foundry/ipai-odoo-copilot-azure/system-prompt.md
 * - Tool definitions from agents/foundry/ipai-odoo-copilot-azure/tool-definitions.json
 * - Tool allowlist from agents/foundry/policies/agents__policy__tool_allowlist__v1.policy.yaml
 * - Eval thresholds from agents/evals/odoo-copilot/thresholds.yaml
 */

import { readFileSync, existsSync } from 'node:fs';
import { join } from 'node:path';
import type { ToolManifest } from '@ipai/builder-contract';

/** Loaded agent assets */
export interface AgentAssets {
  systemPrompt: string;
  toolManifest: ToolManifest;
  metadata: Record<string, unknown>;
  guardrails: string;
}

/** Configuration for the asset loader */
export interface AssetLoaderConfig {
  /** Absolute path to the agents/ repository root */
  agentsRoot: string;
  /** Agent profile to load (subdirectory under foundry/) */
  agentProfile: string;
}

/**
 * Load agent assets from the agents/ repository.
 * Fails fast with clear error if required assets are missing.
 */
export class AssetLoader {
  private config: AssetLoaderConfig;

  constructor(config: AssetLoaderConfig) {
    this.config = config;
  }

  /** Load all assets for the configured agent profile */
  load(): AgentAssets {
    const profileDir = join(this.config.agentsRoot, 'foundry', this.config.agentProfile);

    if (!existsSync(profileDir)) {
      throw new Error(
        `Agent profile directory not found: ${profileDir}. ` +
        `Ensure agents/ repo is available at ${this.config.agentsRoot}`
      );
    }

    return {
      systemPrompt: this.loadSystemPrompt(profileDir),
      toolManifest: this.loadToolManifest(profileDir),
      metadata: this.loadMetadata(profileDir),
      guardrails: this.loadGuardrails(profileDir),
    };
  }

  private loadSystemPrompt(profileDir: string): string {
    const promptPath = join(profileDir, 'system-prompt.md');
    if (!existsSync(promptPath)) {
      throw new Error(`System prompt not found: ${promptPath}`);
    }

    const content = readFileSync(promptPath, 'utf-8');

    // Extract the prompt text from the markdown code block
    const match = content.match(/```text\n([\s\S]*?)```/);
    if (match && match[1]) {
      return match[1].trim();
    }

    // Fallback: use the full content
    return content;
  }

  private loadToolManifest(profileDir: string): ToolManifest {
    const toolPath = join(profileDir, 'tool-definitions.json');
    if (!existsSync(toolPath)) {
      throw new Error(`Tool definitions not found: ${toolPath}`);
    }

    const content = readFileSync(toolPath, 'utf-8');
    return JSON.parse(content) as ToolManifest;
  }

  private loadMetadata(profileDir: string): Record<string, unknown> {
    const metaPath = join(profileDir, 'metadata.yaml');
    if (!existsSync(metaPath)) {
      return {};
    }

    // Simple YAML-ish parser for key: value lines (no dependency on yaml lib)
    const content = readFileSync(metaPath, 'utf-8');
    const result: Record<string, unknown> = {};
    for (const line of content.split('\n')) {
      const match = line.match(/^(\w[\w_-]*)\s*:\s*(.+)$/);
      if (match) {
        const key = match[1];
        const raw: string = match[2].trim();
        let value: string | boolean | number = raw;
        if (raw === 'true') value = true;
        else if (raw === 'false') value = false;
        else if (/^\d+$/.test(raw)) value = parseInt(raw, 10);
        result[key] = value;
      }
    }
    return result;
  }

  private loadGuardrails(profileDir: string): string {
    const guardrailsPath = join(profileDir, 'guardrails.md');
    if (!existsSync(guardrailsPath)) {
      return '';
    }
    return readFileSync(guardrailsPath, 'utf-8');
  }
}
