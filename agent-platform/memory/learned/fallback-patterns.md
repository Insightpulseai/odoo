# Fallback Patterns

Use this file for successful safe recovery paths.

Examples:
- retrieval_low_confidence -> rewrite query -> rerank -> grounded low-confidence answer
- tool_timeout -> retry once -> reduce context -> reroute -> explanation-only fallback
- policy_block -> downgrade to read-only guidance -> request authorized actor
