// apps/ops-console/hooks/use-ops-run-mutation.ts
"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { supabase } from "@/lib/supabase";
import { toast } from "sonner";

interface TriggerRunParams {
  kind: 'deploy' | 'clone' | 'backup' | 'resync' | 'test';
  env_id?: string;
  metadata?: Record<string, any>;
}

export const useOpsRunMutation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ kind, env_id, metadata }: TriggerRunParams) => {
      // 1. Create the run record
      const { data: run, error: runError } = await supabase
        .from("runs")
        .insert([
          {
            kind,
            env_id,
            status: "pending",
            metadata: {
              ...metadata,
              triggered_at: new Date().toISOString(),
              client: "OpsConsole"
            },
          },
        ])
        .select()
        .single();

      if (runError) throw runError;

      // 2. Emit initial event
      const { error: eventError } = await supabase
        .from("run_events")
        .insert([
          {
            run_id: run.id,
            level: "info",
            message: `User-initiated ${kind} run started.`,
            payload: { client: "OpsConsole" }
          },
        ]);

      if (eventError) console.error("Failed to emit initial run event", eventError);

      return run;
    },
    onSuccess: (run) => {
      toast.success(`${run.kind.toUpperCase()} run initiated (ID: ${run.id.slice(0, 8)})`);
      queryClient.invalidateQueries({ queryKey: ["ops", "runs"] });
    },
    onError: (error: any) => {
      toast.error(`Failed to initiate run: ${error.message || "Unknown error"}`);
    },
  });
};
