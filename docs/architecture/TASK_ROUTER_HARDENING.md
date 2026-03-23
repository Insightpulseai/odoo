# Task Router Hardening Architecture
## Router Topology
The `StatefulTaskRouter` acts as a monolithic barrier tracking in-flight lifecycle arrays explicitly bounding lease timings.

## Queue State Machine
`queued` -> `claimed` -> `completed`
* `retry_scheduled` loop back
* `dead_lettered` terminal
* `quarantined` terminal

## At-Least-Once Delivery Doctrine
Matches only at-least-once boundaries with a duplicate suppression barrier matching on `envelope_id + type + attempt_group`.

## Retry/Dead-Letter Lifecycle
5 maximum attempts triggering sequential exponential backoff.
