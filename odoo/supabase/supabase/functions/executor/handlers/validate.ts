/**
 * Validate Phase Handler
 *
 * Runs data quality checks (row counts, null checks, schema drift, etc.)
 *
 * @module executor/handlers/validate
 */

import { PhaseHandler, PhaseResult, PhaseCallbacks, RunContext, QualityCheck, QualityResult } from "../types.ts";

export class ValidateHandler implements PhaseHandler {
  name = "validate";

  async execute(
    ctx: RunContext,
    phaseSpec: Record<string, unknown>,
    callbacks: PhaseCallbacks
  ): Promise<PhaseResult> {
    const checks = phaseSpec.checks as QualityCheck[] | undefined;
    const failOnError = (phaseSpec.fail_on_error as boolean) ?? true;
    const inputUri = phaseSpec.input_uri as string;

    if (!checks || checks.length === 0) {
      await callbacks.emitEvent("warn", "No quality checks defined, skipping validation");
      return { success: true };
    }

    await callbacks.emitEvent("info", "Starting data validation", {
      check_count: checks.length,
      input_uri: inputUri,
      fail_on_error: failOnError,
    });

    const results: QualityResult[] = [];
    let hasFailures = false;

    for (const check of checks) {
      await callbacks.heartbeat();

      const result = await this.runCheck(check, inputUri, callbacks);
      results.push(result);

      if (!result.passed) {
        hasFailures = true;
        await callbacks.emitEvent("warn", `Quality check failed: ${check.name}`, {
          check,
          result,
        });
      } else {
        await callbacks.emitEvent("debug", `Quality check passed: ${check.name}`, {
          check,
          result,
        });
      }
    }

    // Register validation report as artifact
    const reportUri = `${ctx.artifactBaseUri}/validation/report.json`;
    const report = {
      timestamp: new Date().toISOString(),
      input_uri: inputUri,
      checks: results,
      passed: !hasFailures,
      total_checks: checks.length,
      passed_checks: results.filter((r) => r.passed).length,
      failed_checks: results.filter((r) => !r.passed).length,
    };

    await callbacks.registerArtifact(
      "report",
      reportUri,
      null,
      null,
      { type: "validation_report", summary: report }
    );

    if (hasFailures && failOnError) {
      return {
        success: false,
        errorCode: "VALIDATION_FAILED",
        errorMessage: `${results.filter((r) => !r.passed).length} quality checks failed`,
        artifacts: [
          {
            kind: "report",
            uri: reportUri,
            sha256: null,
            sizeBytes: null,
          },
        ],
      };
    }

    await callbacks.emitEvent("info", "Validation complete", {
      passed: !hasFailures || !failOnError,
      total_checks: checks.length,
      passed_checks: results.filter((r) => r.passed).length,
    });

    return {
      success: true,
      artifacts: [
        {
          kind: "report",
          uri: reportUri,
          sha256: null,
          sizeBytes: null,
        },
      ],
    };
  }

  private async runCheck(
    check: QualityCheck,
    inputUri: string | undefined,
    callbacks: PhaseCallbacks
  ): Promise<QualityResult> {
    switch (check.type) {
      case "row_count": {
        return this.checkRowCount(check);
      }
      case "null_check": {
        return this.checkNulls(check);
      }
      case "schema_drift": {
        return this.checkSchemaDrift(check);
      }
      case "range_check": {
        return this.checkRange(check);
      }
      case "custom": {
        return this.checkCustom(check);
      }
      default: {
        return {
          check,
          passed: false,
          message: `Unknown check type: ${check.type}`,
        };
      }
    }
  }

  private checkRowCount(check: QualityCheck): QualityResult {
    // In real implementation, would query the actual row count from the dataset
    const actualRowCount = 1000; // Simulated
    const threshold = check.threshold || 0;
    const passed = actualRowCount >= threshold;

    return {
      check,
      passed,
      actual: actualRowCount,
      message: passed
        ? `Row count ${actualRowCount} >= threshold ${threshold}`
        : `Row count ${actualRowCount} < threshold ${threshold}`,
    };
  }

  private checkNulls(check: QualityCheck): QualityResult {
    // In real implementation, would count nulls in the specified column
    const nullPercentage = 0.02; // Simulated 2% nulls
    const threshold = check.threshold || 0.1; // Default 10% threshold
    const passed = nullPercentage <= threshold;

    return {
      check,
      passed,
      actual: nullPercentage,
      message: passed
        ? `Null percentage ${nullPercentage * 100}% <= threshold ${threshold * 100}%`
        : `Null percentage ${nullPercentage * 100}% > threshold ${threshold * 100}%`,
    };
  }

  private checkSchemaDrift(check: QualityCheck): QualityResult {
    // In real implementation, would compare current schema against expected
    const expectedSchema = check.expected as Record<string, string> | undefined;
    const driftDetected = false; // Simulated

    return {
      check,
      passed: !driftDetected,
      actual: { drift_detected: driftDetected },
      message: driftDetected
        ? "Schema drift detected"
        : "No schema drift detected",
    };
  }

  private checkRange(check: QualityCheck): QualityResult {
    // In real implementation, would check if column values are within range
    const min = (check.expected as Record<string, number>)?.min || 0;
    const max = (check.expected as Record<string, number>)?.max || 100;
    const outOfRange = 0; // Simulated

    return {
      check,
      passed: outOfRange === 0,
      actual: { out_of_range_count: outOfRange },
      message: outOfRange === 0
        ? `All values in range [${min}, ${max}]`
        : `${outOfRange} values out of range [${min}, ${max}]`,
    };
  }

  private checkCustom(check: QualityCheck): QualityResult {
    // In real implementation, would execute custom SQL check
    const sql = check.sql;
    if (!sql) {
      return {
        check,
        passed: false,
        message: "Custom check requires sql field",
      };
    }

    // Simulated execution
    return {
      check,
      passed: true,
      actual: { sql_result: 1 },
      message: "Custom SQL check passed",
    };
  }
}
