# AP Invoice Red Team Summary

**Status:** PASSED (All attacks blocked)

| Attack | Result | Observation |
| :--- | :--- | :--- |
| State Injection: Force approved_to_post | **FAILED (Blocked)** | Blocked at ORM layer (readonly=True). System remains in 'ingested'. |
| Direct Post Bypass: Call post on 'ingested' | **FAILED (Blocked)** | Fail-Closed gate triggered: 'AP Invoice must be in Approved to Post state'. |
| Evidence Corruption: Empty Evidence Pack | **FAILED (Blocked)** | Fail-Closed gate triggered: 'No AI evidence pack attached'. |
| Replay Attack: Duplicate Invoice Ref | **FAILED (Blocked)** | Blocked by Odoo unique constraint (ref, partner_id). Fail-closed. |
