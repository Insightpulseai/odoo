/**
 * Query Phase Handler
 *
 * Executes SQL queries and stores results as artifacts.
 *
 * @module executor/handlers/query
 */

import { PhaseHandler, PhaseResult, PhaseCallbacks, RunContext, SqlResult } from "../types.ts";

export class QueryHandler implements PhaseHandler {
  name = "query";

  async execute(
    ctx: RunContext,
    phaseSpec: Record<string, unknown>,
    callbacks: PhaseCallbacks
  ): Promise<PhaseResult> {
    const sql = phaseSpec.sql as string;
    const sqlFile = phaseSpec.sql_file as string;
    const engine = phaseSpec.engine as string || "trino";
    const outputFormat = phaseSpec.output_format as string || "parquet";
    const limit = phaseSpec.limit as number;
    const storeSample = (phaseSpec.store_sample as boolean) ?? true;
    const sampleSize = (phaseSpec.sample_size as number) || 100;

    if (!sql && !sqlFile) {
      return {
        success: false,
        errorCode: "MISSING_SQL",
        errorMessage: "Query phase requires sql or sql_file",
      };
    }

    await callbacks.emitEvent("info", "Executing query", {
      engine,
      output_format: outputFormat,
      has_sql: !!sql,
      sql_file: sqlFile,
      limit,
    });

    try {
      await callbacks.heartbeat();

      // Execute query
      const result = await this.executeQuery(sql || "", engine, limit, callbacks);

      await callbacks.emitEvent("info", "Query executed", {
        row_count: result.rowCount,
        column_count: result.columns.length,
        execution_time_ms: result.executionTimeMs,
      });

      const artifacts: Array<{
        kind: string;
        uri: string;
        sha256: string | null;
        sizeBytes: number | null;
        meta?: Record<string, unknown>;
      }> = [];

      // Store full result
      const resultUri = `${ctx.artifactBaseUri}/query/result.${outputFormat}`;
      await callbacks.registerArtifact(
        "dataset",
        resultUri,
        null,
        null,
        {
          format: outputFormat,
          row_count: result.rowCount,
          columns: result.columns,
          execution_time_ms: result.executionTimeMs,
        }
      );
      artifacts.push({
        kind: "dataset",
        uri: resultUri,
        sha256: null,
        sizeBytes: null,
        meta: { row_count: result.rowCount },
      });

      // Store sample for preview
      if (storeSample && result.rows.length > 0) {
        const sampleRows = result.rows.slice(0, sampleSize);
        const sampleUri = `${ctx.artifactBaseUri}/query/sample.json`;

        await callbacks.registerArtifact(
          "sample",
          sampleUri,
          null,
          null,
          {
            columns: result.columns,
            rows: sampleRows,
            total_rows: result.rowCount,
            sample_size: sampleRows.length,
          }
        );
        artifacts.push({
          kind: "sample",
          uri: sampleUri,
          sha256: null,
          sizeBytes: null,
        });
      }

      // Store query text
      const queryUri = `${ctx.artifactBaseUri}/query/query.sql`;
      await callbacks.registerArtifact(
        "sql",
        queryUri,
        null,
        null,
        { sql: sql }
      );
      artifacts.push({
        kind: "sql",
        uri: queryUri,
        sha256: null,
        sizeBytes: null,
      });

      return {
        success: true,
        artifacts,
        outputManifest: {
          row_count: result.rowCount,
          columns: result.columns,
          execution_time_ms: result.executionTimeMs,
        },
      };
    } catch (err) {
      return {
        success: false,
        errorCode: "QUERY_ERROR",
        errorMessage: err instanceof Error ? err.message : String(err),
      };
    }
  }

  private async executeQuery(
    sql: string,
    engine: string,
    limit: number | undefined,
    callbacks: PhaseCallbacks
  ): Promise<SqlResult> {
    // In real implementation, would:
    // 1. Connect to appropriate engine (Trino/Spark/DuckDB)
    // 2. Execute query with timeout
    // 3. Stream results to object storage

    await callbacks.heartbeat();

    // Simulate query execution
    const startTime = Date.now();

    // Simulated result
    const columns = ["id", "name", "value", "created_at"];
    const rows: unknown[][] = [];

    const rowCount = Math.min(limit || 1000, 1000);
    for (let i = 0; i < rowCount; i++) {
      rows.push([
        i + 1,
        `item_${i + 1}`,
        Math.random() * 100,
        new Date().toISOString(),
      ]);
    }

    const executionTimeMs = Date.now() - startTime + 50; // Add simulated DB time

    return {
      columns,
      rows,
      rowCount: rows.length,
      executionTimeMs,
    };
  }
}
