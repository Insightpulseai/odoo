// server/lib/idempotency.ts
// Idempotency-key builders scoped to Slack event surfaces.
//
// Strategy:
//   Events API:    "slack:event:{event_id}"
//   Interactive:   "slack:interaction:{payload.trigger_id}"
//   Slash command: "slack:command:{command}:{trigger_id}"
//
// Keys are fed into taskbus.enqueue() → ops.runs.idempotency_key.
// Duplicate Slack deliveries (Slack retries on 200 delay) produce
// the same key and are de-duped by the taskbus enqueue helper.

/** Idempotency key for an Events API event. */
export function slackEventKey(eventId: string): string {
  return `slack:event:${eventId}`
}

/** Idempotency key for an interactive payload (button click, modal submit). */
export function slackInteractionKey(triggerId: string): string {
  return `slack:interaction:${triggerId}`
}

/** Idempotency key for a slash command invocation. */
export function slackCommandKey(command: string, triggerId: string): string {
  // Normalize command — strip leading slash for consistency
  const cmd = command.startsWith('/') ? command.slice(1) : command
  return `slack:command:${cmd}:${triggerId}`
}
