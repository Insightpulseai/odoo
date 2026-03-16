/**
 * Ingest Phase Handler
 *
 * Handles data ingestion from sources (Postgres, S3, HTTP, etc.)
 * to the lakehouse bronze layer.
 *
 * @module executor/handlers/ingest
 */

import { PhaseHandler, PhaseResult, PhaseCallbacks, RunContext } from "../types.ts";

export class IngestHandler implements PhaseHandler {
  name = "ingest";

  async execute(
    ctx: RunContext,
    phaseSpec: Record<string, unknown>,
    callbacks: PhaseCallbacks
  ): Promise<PhaseResult> {
    const source = phaseSpec.source as Record<string, unknown> | undefined;
    const destination = phaseSpec.destination as Record<string, unknown> | undefined;

    if (!source) {
      return {
        success: false,
        errorCode: "MISSING_SOURCE",
        errorMessage: "Ingest phase requires a source configuration",
      };
    }

    await callbacks.emitEvent("info", "Starting data ingestion", {
      source_type: source.type,
      destination: destination,
    });

    const sourceType = source.type as string;

    try {
      switch (sourceType) {
        case "postgres": {
          return await this.ingestFromPostgres(ctx, source, destination, callbacks);
        }
        case "s3": {
          return await this.ingestFromS3(ctx, source, destination, callbacks);
        }
        case "http": {
          return await this.ingestFromHttp(ctx, source, destination, callbacks);
        }
        default: {
          return {
            success: false,
            errorCode: "UNSUPPORTED_SOURCE",
            errorMessage: `Unsupported source type: ${sourceType}`,
          };
        }
      }
    } catch (err) {
      return {
        success: false,
        errorCode: "INGEST_ERROR",
        errorMessage: err instanceof Error ? err.message : String(err),
      };
    }
  }

  private async ingestFromPostgres(
    ctx: RunContext,
    source: Record<string, unknown>,
    destination: Record<string, unknown> | undefined,
    callbacks: PhaseCallbacks
  ): Promise<PhaseResult> {
    const connectionRef = source.connection_ref as string;
    const query = source.query as string;
    const table = source.table as string;

    if (!connectionRef) {
      return {
        success: false,
        errorCode: "MISSING_CONNECTION",
        errorMessage: "Postgres source requires connection_ref",
      };
    }

    if (!query && !table) {
      return {
        success: false,
        errorCode: "MISSING_QUERY",
        errorMessage: "Postgres source requires query or table",
      };
    }

    await callbacks.emitEvent("info", "Connecting to Postgres", {
      connection_ref: connectionRef,
      table: table,
    });

    // In a real implementation, this would:
    // 1. Resolve connection_ref to actual credentials (from vault/env)
    // 2. Connect to Postgres
    // 3. Execute query or SELECT * FROM table
    // 4. Stream results to object storage in Parquet/Delta format
    // 5. Register the output artifact

    // Placeholder for MVP - simulate ingestion
    await callbacks.heartbeat();

    const outputUri = `${ctx.artifactBaseUri}/bronze/${table || "query_result"}/data.parquet`;
    const rowCount = 1000; // Simulated

    await callbacks.emitEvent("info", "Ingestion complete", {
      output_uri: outputUri,
      row_count: rowCount,
    });

    await callbacks.registerArtifact(
      "dataset",
      outputUri,
      null, // SHA256 would be computed from actual data
      null,
      {
        format: "parquet",
        row_count: rowCount,
        source_type: "postgres",
        table: table,
      }
    );

    return {
      success: true,
      artifacts: [
        {
          kind: "dataset",
          uri: outputUri,
          sha256: null,
          sizeBytes: null,
          meta: { format: "parquet", row_count: rowCount },
        },
      ],
    };
  }

  private async ingestFromS3(
    ctx: RunContext,
    source: Record<string, unknown>,
    destination: Record<string, unknown> | undefined,
    callbacks: PhaseCallbacks
  ): Promise<PhaseResult> {
    const bucket = source.bucket as string;
    const prefix = source.prefix as string;
    const pattern = source.pattern as string;

    if (!bucket) {
      return {
        success: false,
        errorCode: "MISSING_BUCKET",
        errorMessage: "S3 source requires bucket",
      };
    }

    await callbacks.emitEvent("info", "Listing S3 objects", {
      bucket,
      prefix,
      pattern,
    });

    // Placeholder for MVP
    await callbacks.heartbeat();

    const outputUri = `${ctx.artifactBaseUri}/bronze/s3_ingest/data.parquet`;

    await callbacks.emitEvent("info", "S3 ingestion complete", {
      output_uri: outputUri,
    });

    await callbacks.registerArtifact(
      "dataset",
      outputUri,
      null,
      null,
      { format: "parquet", source_type: "s3", bucket, prefix }
    );

    return {
      success: true,
      artifacts: [
        {
          kind: "dataset",
          uri: outputUri,
          sha256: null,
          sizeBytes: null,
        },
      ],
    };
  }

  private async ingestFromHttp(
    ctx: RunContext,
    source: Record<string, unknown>,
    destination: Record<string, unknown> | undefined,
    callbacks: PhaseCallbacks
  ): Promise<PhaseResult> {
    const url = source.url as string;
    const method = (source.method as string) || "GET";
    const headers = source.headers as Record<string, string> | undefined;

    if (!url) {
      return {
        success: false,
        errorCode: "MISSING_URL",
        errorMessage: "HTTP source requires url",
      };
    }

    await callbacks.emitEvent("info", "Fetching from HTTP", {
      url,
      method,
    });

    try {
      const response = await fetch(url, {
        method,
        headers,
      });

      if (!response.ok) {
        return {
          success: false,
          errorCode: "HTTP_ERROR",
          errorMessage: `HTTP ${response.status}: ${response.statusText}`,
        };
      }

      await callbacks.heartbeat();

      const contentType = response.headers.get("content-type") || "application/octet-stream";
      const outputUri = `${ctx.artifactBaseUri}/bronze/http_ingest/data`;

      // In real implementation, would stream body to object storage

      await callbacks.emitEvent("info", "HTTP ingestion complete", {
        output_uri: outputUri,
        content_type: contentType,
      });

      await callbacks.registerArtifact(
        "dataset",
        outputUri,
        null,
        null,
        { source_type: "http", url, content_type: contentType }
      );

      return {
        success: true,
        artifacts: [
          {
            kind: "dataset",
            uri: outputUri,
            sha256: null,
            sizeBytes: null,
          },
        ],
      };
    } catch (err) {
      return {
        success: false,
        errorCode: "HTTP_FETCH_ERROR",
        errorMessage: err instanceof Error ? err.message : String(err),
      };
    }
  }
}
