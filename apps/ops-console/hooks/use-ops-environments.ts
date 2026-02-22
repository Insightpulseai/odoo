// apps/ops-console/hooks/use-ops-environments.ts
"use client";

import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect } from "react";
import { supabase } from "@/lib/supabase";

export const useOpsEnvironments = () => {
  const queryClient = useQueryClient();

  useEffect(() => {
    const channel = supabase
      .channel("ops_environments_changes")
      .on(
        "postgres_changes",
        { event: "*", schema: "ops", table: "environments" },
        () => {
          queryClient.invalidateQueries({ queryKey: ["ops", "environments"] });
        }
      )
      .subscribe();

    return () => {
      supabase.removeChannel(channel);
    };
  }, [queryClient]);

  return useQuery({
    queryKey: ["ops", "environments"],
    queryFn: async () => {
      const { data, error } = await supabase
        .from("environments")
        .select("*")
        .order("slug", { ascending: true });

      if (error) throw error;
      return data;
    },
  });
};
