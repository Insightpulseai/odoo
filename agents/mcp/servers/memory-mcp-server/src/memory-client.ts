/**
 * Memory Client
 *
 * Supabase client for the verified memory system.
 * Handles CRUD operations for agent memories with citation verification.
 */

import { createClient, SupabaseClient } from "@supabase/supabase-js";

export interface Citation {
  path: string;
  line_start: number;
  line_end: number;
  sha?: string;
  snippet_hash?: string;
}

export interface Memory {
  id: string;
  repo: string;
  subject: string;
  fact: string;
  citations: Citation[];
  reason?: string;
  created_by?: string;
  created_at: string;
  refreshed_at: string;
  status: "active" | "superseded" | "invalid";
  verification_count: number;
  rejection_count: number;
  last_verified_at?: string;
  supersedes_id?: string;
}

export interface MemoryInput {
  repo: string;
  subject: string;
  fact: string;
  citations: Citation[];
  reason?: string;
  created_by?: string;
}

export interface MemoryStats {
  repo: string;
  status: string;
  memory_count: number;
  avg_verifications: number;
  avg_rejections: number;
  last_activity: string;
  first_memory: string;
}

export class MemoryClient {
  private supabase: SupabaseClient;

  constructor(supabaseUrl: string, supabaseKey: string) {
    this.supabase = createClient(supabaseUrl, supabaseKey);
  }

  /**
   * Store a new memory or refresh an existing one.
   * Uses the ipai.store_memory function for upsert logic.
   */
  async storeMemory(input: MemoryInput): Promise<{ id: string }> {
    const { data, error } = await this.supabase.rpc("store_memory", {
      p_repo: input.repo,
      p_subject: input.subject,
      p_fact: input.fact,
      p_citations: input.citations,
      p_reason: input.reason,
      p_created_by: input.created_by,
    });

    if (error) {
      throw new Error(`Failed to store memory: ${error.message}`);
    }

    return { id: data };
  }

  /**
   * Get recent memories for a repository.
   * Returns memories ordered by recency (most recently refreshed first).
   */
  async getRecentMemories(
    repo: string,
    limit: number = 20
  ): Promise<Memory[]> {
    const { data, error } = await this.supabase.rpc("get_recent_memories", {
      p_repo: repo,
      p_limit: limit,
    });

    if (error) {
      throw new Error(`Failed to get memories: ${error.message}`);
    }

    return data || [];
  }

  /**
   * Search memories by subject pattern.
   */
  async searchMemories(
    repo: string,
    subjectPattern?: string,
    limit: number = 20
  ): Promise<Memory[]> {
    const { data, error } = await this.supabase.rpc("search_memories", {
      p_repo: repo,
      p_subject_pattern: subjectPattern,
      p_limit: limit,
    });

    if (error) {
      throw new Error(`Failed to search memories: ${error.message}`);
    }

    return data || [];
  }

  /**
   * Mark a memory as verified after successful citation check.
   * Updates verification count and refreshes timestamp.
   */
  async verifyMemory(memoryId: string, agentId?: string): Promise<boolean> {
    const { data, error } = await this.supabase.rpc("verify_memory", {
      p_memory_id: memoryId,
      p_agent_id: agentId,
    });

    if (error) {
      throw new Error(`Failed to verify memory: ${error.message}`);
    }

    return data;
  }

  /**
   * Invalidate a memory when citations contradict.
   */
  async invalidateMemory(
    memoryId: string,
    agentId?: string,
    reason?: string
  ): Promise<boolean> {
    const { data, error } = await this.supabase.rpc("invalidate_memory", {
      p_memory_id: memoryId,
      p_agent_id: agentId,
      p_reason: reason,
    });

    if (error) {
      throw new Error(`Failed to invalidate memory: ${error.message}`);
    }

    return data;
  }

  /**
   * Replace an incorrect memory with a corrected version.
   * The old memory is marked as superseded.
   */
  async supersedeMemory(
    oldMemoryId: string,
    newMemory: MemoryInput
  ): Promise<{ id: string }> {
    const { data, error } = await this.supabase.rpc("supersede_memory", {
      p_old_memory_id: oldMemoryId,
      p_repo: newMemory.repo,
      p_subject: newMemory.subject,
      p_fact: newMemory.fact,
      p_citations: newMemory.citations,
      p_reason: newMemory.reason,
      p_created_by: newMemory.created_by,
    });

    if (error) {
      throw new Error(`Failed to supersede memory: ${error.message}`);
    }

    return { id: data };
  }

  /**
   * Get a single memory by ID.
   */
  async getMemory(memoryId: string): Promise<Memory | null> {
    const { data, error } = await this.supabase
      .schema("ipai")
      .from("agent_memory")
      .select("*")
      .eq("id", memoryId)
      .single();

    if (error) {
      if (error.code === "PGRST116") {
        return null;
      }
      throw new Error(`Failed to get memory: ${error.message}`);
    }

    return data;
  }

  /**
   * Get memory statistics for a repository.
   */
  async getStats(repo?: string): Promise<MemoryStats[]> {
    let query = this.supabase
      .schema("ipai")
      .from("agent_memory_stats")
      .select("*");

    if (repo) {
      query = query.eq("repo", repo);
    }

    const { data, error } = await query;

    if (error) {
      throw new Error(`Failed to get stats: ${error.message}`);
    }

    return data || [];
  }

  /**
   * Get memory logs for debugging/telemetry.
   */
  async getLogs(
    repo: string,
    limit: number = 50,
    eventType?: string
  ): Promise<unknown[]> {
    let query = this.supabase
      .schema("ipai")
      .from("agent_memory_log")
      .select("*")
      .eq("repo", repo)
      .order("created_at", { ascending: false })
      .limit(limit);

    if (eventType) {
      query = query.eq("event_type", eventType);
    }

    const { data, error } = await query;

    if (error) {
      throw new Error(`Failed to get logs: ${error.message}`);
    }

    return data || [];
  }
}
