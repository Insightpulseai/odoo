/**
 * Agent Registry - Supabase-backed agent discovery and registration
 *
 * Implements the service discovery pattern for A2A communication,
 * allowing agents to register, discover, and track other agents.
 */

import { createClient, SupabaseClient } from "@supabase/supabase-js";
import {
  AgentMetadata,
  AgentState,
  DiscoveryQuery,
  AgentStatus,
} from "./types.js";

const SUPABASE_URL = process.env.SUPABASE_URL || "";
const SUPABASE_SERVICE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY || "";

/**
 * Agent Registry client for managing agent metadata and state
 */
export class AgentRegistry {
  private supabase: SupabaseClient | null = null;
  private localCache: Map<string, AgentMetadata> = new Map();
  private cacheExpiry: number = 60000; // 1 minute
  private lastCacheUpdate: number = 0;

  constructor() {
    if (SUPABASE_URL && SUPABASE_SERVICE_KEY) {
      this.supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_KEY);
    }
  }

  /**
   * Register a new agent or update existing registration
   */
  async register(agent: AgentMetadata): Promise<AgentMetadata> {
    const now = new Date().toISOString();
    const record = {
      ...agent,
      updated_at: now,
      last_heartbeat: now,
    };

    if (this.supabase) {
      const { data, error } = await this.supabase
        .from("agent_registry")
        .upsert(record, { onConflict: "id" })
        .select()
        .single();

      if (error) {
        throw new Error(`Registration failed: ${error.message}`);
      }
      this.localCache.set(agent.id, data);
      return data;
    }

    // Fallback to local cache only
    this.localCache.set(agent.id, record);
    return record;
  }

  /**
   * Unregister an agent from the registry
   */
  async unregister(agentId: string): Promise<void> {
    if (this.supabase) {
      const { error } = await this.supabase
        .from("agent_registry")
        .delete()
        .eq("id", agentId);

      if (error) {
        throw new Error(`Unregistration failed: ${error.message}`);
      }
    }
    this.localCache.delete(agentId);
  }

  /**
   * Get agent by ID
   */
  async get(agentId: string): Promise<AgentMetadata | null> {
    // Check cache first
    if (this.localCache.has(agentId)) {
      return this.localCache.get(agentId) || null;
    }

    if (this.supabase) {
      const { data, error } = await this.supabase
        .from("agent_registry")
        .select("*")
        .eq("id", agentId)
        .single();

      if (error) {
        if (error.code === "PGRST116") return null; // Not found
        throw new Error(`Get agent failed: ${error.message}`);
      }
      this.localCache.set(agentId, data);
      return data;
    }

    return null;
  }

  /**
   * Discover agents matching query criteria
   */
  async discover(query: DiscoveryQuery): Promise<AgentMetadata[]> {
    if (this.supabase) {
      let q = this.supabase.from("agent_registry").select("*");

      // Filter by capabilities (array overlap)
      if (query.capabilities?.length) {
        q = q.overlaps("capabilities", query.capabilities);
      }

      // Filter by status
      if (query.status?.length) {
        q = q.in("status", query.status);
      }

      // Filter by tags
      if (query.tags?.length) {
        q = q.overlaps("tags", query.tags);
      }

      // Filter by tools
      if (query.tools?.length) {
        q = q.overlaps("tools", query.tools);
      }

      // Limit results
      if (query.max_results) {
        q = q.limit(query.max_results);
      }

      const { data, error } = await q;

      if (error) {
        throw new Error(`Discovery failed: ${error.message}`);
      }

      // Update cache
      for (const agent of data || []) {
        this.localCache.set(agent.id, agent);
      }

      return data || [];
    }

    // Fallback: filter local cache
    let results = Array.from(this.localCache.values());

    if (query.capabilities?.length) {
      results = results.filter((a) =>
        query.capabilities!.some((c) => a.capabilities?.includes(c))
      );
    }

    if (query.status?.length) {
      results = results.filter((a) =>
        query.status!.includes(a.status as AgentStatus)
      );
    }

    if (query.tags?.length) {
      results = results.filter((a) =>
        query.tags!.some((t) => a.tags?.includes(t))
      );
    }

    if (query.max_results) {
      results = results.slice(0, query.max_results);
    }

    return results;
  }

  /**
   * List all registered agents
   */
  async listAll(): Promise<AgentMetadata[]> {
    if (this.supabase) {
      const { data, error } = await this.supabase
        .from("agent_registry")
        .select("*")
        .order("name");

      if (error) {
        throw new Error(`List failed: ${error.message}`);
      }

      return data || [];
    }

    return Array.from(this.localCache.values());
  }

  /**
   * Update agent heartbeat (keep-alive)
   */
  async heartbeat(agentId: string): Promise<void> {
    const now = new Date().toISOString();

    if (this.supabase) {
      const { error } = await this.supabase
        .from("agent_registry")
        .update({ last_heartbeat: now, status: "active" })
        .eq("id", agentId);

      if (error) {
        throw new Error(`Heartbeat failed: ${error.message}`);
      }
    }

    const cached = this.localCache.get(agentId);
    if (cached) {
      cached.last_heartbeat = now;
    }
  }

  /**
   * Update agent status
   */
  async updateStatus(agentId: string, status: AgentStatus): Promise<void> {
    if (this.supabase) {
      const { error } = await this.supabase
        .from("agent_registry")
        .update({ status, updated_at: new Date().toISOString() })
        .eq("id", agentId);

      if (error) {
        throw new Error(`Status update failed: ${error.message}`);
      }
    }

    const cached = this.localCache.get(agentId);
    if (cached) {
      (cached as AgentMetadata & { status: AgentStatus }).status = status;
    }
  }

  /**
   * Get agent state (runtime info)
   */
  async getState(agentId: string): Promise<AgentState | null> {
    if (this.supabase) {
      const { data, error } = await this.supabase
        .from("agent_state")
        .select("*")
        .eq("agent_id", agentId)
        .single();

      if (error) {
        if (error.code === "PGRST116") return null;
        throw new Error(`Get state failed: ${error.message}`);
      }

      return data;
    }

    return null;
  }

  /**
   * Update agent state
   */
  async updateState(state: AgentState): Promise<void> {
    if (this.supabase) {
      const { error } = await this.supabase
        .from("agent_state")
        .upsert(state, { onConflict: "agent_id" });

      if (error) {
        throw new Error(`State update failed: ${error.message}`);
      }
    }
  }

  /**
   * Find agents capable of handling a specific tool
   */
  async findByTool(toolName: string): Promise<AgentMetadata[]> {
    return this.discover({ tools: [toolName] });
  }

  /**
   * Find active agents with specific capability
   */
  async findActiveByCapability(
    capability: string
  ): Promise<AgentMetadata[]> {
    return this.discover({
      capabilities: [capability as AgentMetadata["capabilities"][number]],
      status: ["active", "idle"],
    });
  }

  /**
   * Mark stale agents as offline (cleanup job)
   */
  async markStaleOffline(thresholdMs: number = 300000): Promise<number> {
    if (!this.supabase) return 0;

    const threshold = new Date(Date.now() - thresholdMs).toISOString();

    const { data, error } = await this.supabase
      .from("agent_registry")
      .update({ status: "offline" })
      .lt("last_heartbeat", threshold)
      .neq("status", "offline")
      .select("id");

    if (error) {
      throw new Error(`Stale cleanup failed: ${error.message}`);
    }

    return data?.length || 0;
  }

  /**
   * Get registry statistics
   */
  async getStats(): Promise<Record<string, number>> {
    if (this.supabase) {
      const { data, error } = await this.supabase
        .from("agent_registry")
        .select("status");

      if (error) {
        throw new Error(`Stats failed: ${error.message}`);
      }

      const stats: Record<string, number> = {
        total: data?.length || 0,
        active: 0,
        idle: 0,
        busy: 0,
        offline: 0,
        maintenance: 0,
      };

      for (const row of data || []) {
        const status = row.status as string;
        if (status in stats) {
          stats[status]++;
        }
      }

      return stats;
    }

    const agents = Array.from(this.localCache.values());
    return {
      total: agents.length,
      cached: agents.length,
    };
  }
}

// Singleton instance
export const registry = new AgentRegistry();
