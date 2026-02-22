// apps/ops-console/hooks/use-ops-deployments.ts
"use client";

import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect } from "react";
import { supabase } from "@/lib/supabase";

export const useOpsDeployments = (limit = 10) => {
  const queryClient = useQueryClient();

  useEffect(() => {
    const channel = supabase
      .channel("ops_deployments_changes")
      .on(
        "postgres_changes",
        { event: "*", schema: "ops", table: "deployments" },
        () => {
          queryClient.invalidateQueries({ queryKey: ["ops", "deployments"] });
        }
      )
      .subscribe();

    return () => {
      supabase.removeChannel(channel);
    };
  }, [queryClient]);

  return useQuery({
    queryKey: ["ops", "deployments"],
    queryFn: async () => {
      const { data, error } = await supabase
        .from("deployments")
        .select("*")
        .order("created_at", { ascending: false })
        .limit(limit);

      if (error) throw error;
      return data;
    },
  });
};
