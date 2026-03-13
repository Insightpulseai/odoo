// apps/ops-console/hooks/use-ops-run-events.ts
"use client";

import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect } from "react";
import { supabase } from "@/lib/supabase";

export const useOpsRunEvents = (runId?: string) => {
  const queryClient = useQueryClient();

  useEffect(() => {
    if (!runId) return;

    const channel = supabase
      .channel(`ops_run_events_${runId}`)
      .on(
        "postgres_changes",
        {
          event: "INSERT",
          schema: "ops",
          table: "run_events",
          filter: `run_id=eq.${runId}`
        },
        () => {
          queryClient.invalidateQueries({ queryKey: ["ops", "run-events", runId] });
        }
      )
      .subscribe();

    return () => {
      supabase.removeChannel(channel);
    };
  }, [runId, queryClient]);

  return useQuery({
    queryKey: ["ops", "run-events", runId],
    queryFn: async () => {
      if (!runId) return [];
      const { data, error } = await supabase
        .from("run_events")
        .select("*")
        .eq("run_id", runId)
        .order("created_at", { ascending: true });

      if (error) throw error;
      return data;
    },
    enabled: !!runId,
  });
};
