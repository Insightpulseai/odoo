# CLI Surface Routing Policy

## Core Principle

Every CLI operation must be routed to exactly one canonical surface. Cross-platform misuse is a routing error.

## Routing Hierarchy

1. Match task keywords to known CLI surfaces
2. If ambiguous, prefer the platform that owns the data/resource
3. If multi-surface, decompose into sequential sub-tasks
4. If deprecated tool, always REJECT

## Anti-Patterns (Always Reject)

- Using `az databricks` for workspace operations (use Databricks CLI)
- Using Odoo shell to query Databricks data directly
- Using any CLI to bypass authentication or access controls
- Using deprecated tools (odo) for any purpose

## Cross-Platform Integration

When a task genuinely spans platforms:
1. Decompose into per-surface sub-tasks
2. Define execution order (parallel or sequential)
3. Define data handoff format between sub-tasks
4. Each sub-task is routed to its canonical surface

## Escalation

If a task cannot be cleanly routed:
1. Return surface = OTHER
2. Include reasoning about why routing is ambiguous
3. Suggest which persona should make the final decision
4. Do not guess — ambiguous routing leads to misuse
