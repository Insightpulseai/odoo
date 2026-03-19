// apps/ops-console/hooks/use-ops-runs.ts
"use client";

import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect } from "react";
import { supabase } from "@/lib/supabase";

export const useOpsRuns = (limit = 10) => {
  const queryClient = useQueryClient();

  useEffect(() => {
    const channel = supabase
      .channel("ops_runs_changes")
      .on(
        "postgres_changes",
        { event: "*", schema: "ops", table: "runs" },
        () => {
          queryClient.invalidateQueries({ queryKey: ["ops", "runs"] });
        }
      )
      .subscribe();

    return () => {
      supabase.removeChannel(channel);
    };
  }, [queryClient]);

  return useQuery({
    queryKey: ["ops", "runs"],
    queryFn: async () => {
      const { data, error } = await supabase
        .from("runs")
        .select(`
          *,
          environment:environments(slug, type)
        `)
        .order("created_at", { ascending: false })
        .limit(limit);

      if (error) throw error;
      return data;
    },
  });
};
