// apps/ops-console/hooks/use-ops-sync-checkpoints.ts
"use client";

import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect } from "react";
import { supabase } from "@/lib/supabase";

export const useOpsSyncCheckpoints = () => {
  const queryClient = useQueryClient();

  useEffect(() => {
    const channel = supabase
      .channel("ops_sync_checkpoints_changes")
      .on(
        "postgres_changes",
        { event: "*", schema: "ops", table: "sync_checkpoints" },
        () => {
          queryClient.invalidateQueries({ queryKey: ["ops", "sync-checkpoints"] });
        }
      )
      .subscribe();

    return () => {
      supabase.removeChannel(channel);
    };
  }, [queryClient]);

  return useQuery({
    queryKey: ["ops", "sync-checkpoints"],
    queryFn: async () => {
      const { data, error } = await supabase
        .from("sync_checkpoints")
        .select("*")
        .order("model", { ascending: true });

      if (error) throw error;
      return data;
    },
  });
};
