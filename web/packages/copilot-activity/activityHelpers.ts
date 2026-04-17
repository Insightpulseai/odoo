/**
 * Shared activity timeline helpers for Pulser copilot.
 *
 * Framework-agnostic — works with Owl, React, or any renderer.
 */

import type { ActivityStatus, CopilotActivity } from "./activityTypes";

/** Returns true if the activity has reached a terminal state. */
export function isTerminal(status: ActivityStatus): boolean {
    return status === "done" || status === "error" || status === "blocked";
}

/** Returns true if any activity is still in progress. */
export function hasActiveActivity(activities: CopilotActivity[]): boolean {
    return activities.some((a) => a.status === "active");
}

/** Returns the CSS class suffix for a given status. */
export function statusClass(status: ActivityStatus): string {
    return `status-${status}`;
}

/** Filter activities to only those that have started (not pending). */
export function visibleActivities(activities: CopilotActivity[]): CopilotActivity[] {
    return activities.filter((a) => a.status !== "pending");
}
