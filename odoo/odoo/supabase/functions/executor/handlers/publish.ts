/**
 * Publish Phase Handler
 *
 * Publishes processed data to downstream systems (catalog, BI tools, APIs).
 *
 * @module executor/handlers/publish
 */

import { PhaseHandler, PhaseResult, PhaseCallbacks, RunContext } from "../types.ts";

export class PublishHandler implements PhaseHandler {
  name = "publish";

  async execute(
    ctx: RunContext,
    phaseSpec: Record<string, unknown>,
    callbacks: PhaseCallbacks
  ): Promise<PhaseResult> {
    const inputUri = phaseSpec.input_uri as string;
    const targets = phaseSpec.targets as PublishTarget[] | undefined;

    if (!inputUri) {
      return {
        success: false,
        errorCode: "MISSING_INPUT",
        errorMessage: "Publish phase requires input_uri",
      };
    }

    if (!targets || targets.length === 0) {
      await callbacks.emitEvent("warn", "No publish targets defined, skipping");
      return { success: true };
    }

    await callbacks.emitEvent("info", "Starting publish phase", {
      input_uri: inputUri,
      target_count: targets.length,
    });

    const results: PublishResult[] = [];

    for (const target of targets) {
      await callbacks.heartbeat();

      const result = await this.publishToTarget(ctx, inputUri, target, callbacks);
      results.push(result);

      if (!result.success) {
        await callbacks.emitEvent("error", `Failed to publish to ${target.type}`, {
          target,
          error: result.error,
        });
      } else {
        await callbacks.emitEvent("info", `Published to ${target.type}`, {
          target,
          output_ref: result.outputRef,
        });
      }
    }

    const hasFailures = results.some((r) => !r.success);
    const failOnError = (phaseSpec.fail_on_error as boolean) ?? true;

    // Register publish manifest
    const manifestUri = `${ctx.artifactBaseUri}/publish/manifest.json`;
    const manifest = {
      timestamp: new Date().toISOString(),
      input_uri: inputUri,
      targets: results,
      success: !hasFailures,
    };

    await callbacks.registerArtifact(
      "manifest",
      manifestUri,
      null,
      null,
      { type: "publish_manifest", summary: manifest }
    );

    if (hasFailures && failOnError) {
      return {
        success: false,
        errorCode: "PUBLISH_FAILED",
        errorMessage: `Failed to publish to ${results.filter((r) => !r.success).length} targets`,
      };
    }

    return {
      success: true,
      artifacts: [
        {
          kind: "manifest",
          uri: manifestUri,
          sha256: null,
          sizeBytes: null,
        },
      ],
    };
  }

  private async publishToTarget(
    ctx: RunContext,
    inputUri: string,
    target: PublishTarget,
    callbacks: PhaseCallbacks
  ): Promise<PublishResult> {
    switch (target.type) {
      case "catalog": {
        return this.publishToCatalog(ctx, inputUri, target);
      }
      case "superset": {
        return this.publishToSuperset(ctx, inputUri, target);
      }
      case "delta": {
        return this.publishToDelta(ctx, inputUri, target);
      }
      case "webhook": {
        return this.publishToWebhook(ctx, inputUri, target);
      }
      default: {
        return {
          success: false,
          target,
          error: `Unknown target type: ${target.type}`,
        };
      }
    }
  }

  private async publishToCatalog(
    ctx: RunContext,
    inputUri: string,
    target: PublishTarget
  ): Promise<PublishResult> {
    // In real implementation:
    // 1. Connect to OpenMetadata/DataHub
    // 2. Register or update table metadata
    // 3. Update lineage information

    const catalogRef = target.config?.catalog_ref as string;
    const tableName = target.config?.table_name as string;

    // Simulated
    return {
      success: true,
      target,
      outputRef: `catalog://${catalogRef}/${tableName}`,
    };
  }

  private async publishToSuperset(
    ctx: RunContext,
    inputUri: string,
    target: PublishTarget
  ): Promise<PublishResult> {
    // In real implementation:
    // 1. Connect to Superset API
    // 2. Create or update dataset
    // 3. Refresh dataset cache

    const datasetName = target.config?.dataset_name as string;
    const databaseId = target.config?.database_id as number;

    // Simulated
    return {
      success: true,
      target,
      outputRef: `superset://datasets/${databaseId}/${datasetName}`,
    };
  }

  private async publishToDelta(
    ctx: RunContext,
    inputUri: string,
    target: PublishTarget
  ): Promise<PublishResult> {
    // In real implementation:
    // 1. Read Parquet from inputUri
    // 2. Write to Delta table at target location
    // 3. Handle schema evolution

    const tablePath = target.config?.table_path as string;
    const mode = target.config?.mode as string || "append";

    // Simulated
    return {
      success: true,
      target,
      outputRef: `delta://${tablePath}`,
    };
  }

  private async publishToWebhook(
    ctx: RunContext,
    inputUri: string,
    target: PublishTarget
  ): Promise<PublishResult> {
    const url = target.config?.url as string;
    if (!url) {
      return {
        success: false,
        target,
        error: "Webhook target requires url in config",
      };
    }

    try {
      const response = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          run_id: ctx.runId,
          input_uri: inputUri,
          timestamp: new Date().toISOString(),
        }),
      });

      if (!response.ok) {
        return {
          success: false,
          target,
          error: `HTTP ${response.status}: ${response.statusText}`,
        };
      }

      return {
        success: true,
        target,
        outputRef: url,
      };
    } catch (err) {
      return {
        success: false,
        target,
        error: err instanceof Error ? err.message : String(err),
      };
    }
  }
}

interface PublishTarget {
  type: "catalog" | "superset" | "delta" | "webhook";
  config?: Record<string, unknown>;
}

interface PublishResult {
  success: boolean;
  target: PublishTarget;
  outputRef?: string;
  error?: string;
}
