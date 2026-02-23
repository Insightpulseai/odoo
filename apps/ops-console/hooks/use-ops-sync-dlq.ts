// apps/ops-console/hooks/use-ops-sync-dlq.ts
"use client";

import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect } from "react";
import { supabase } from "@/lib/supabase";

export const useOpsSyncDlq = () => {
  const queryClient = useQueryClient();

  useEffect(() => {
    const channel = supabase
      .channel("ops_sync_dlq_changes")
      .on(
        "postgres_changes",
        { event: "*", schema: "ops", table: "sync_dlq" },
        () => {
          queryClient.invalidateQueries({ queryKey: ["ops", "sync-dlq"] });
        }
      )
      .subscribe();

    return () => {
      supabase.removeChannel(channel);
    };
  }, [queryClient]);

  return useQuery({
    queryKey: ["ops", "sync-dlq"],
    queryFn: async () => {
      const { data, error } = await supabase
        .from("sync_dlq")
        .select("*")
        .eq("resolved", false)
        .order("created_at", { ascending: false });

      if (error) throw error;
      return data;
    },
  });
};
