# Knowledge sourcing rules

## Source selection

- Start with local indexed project knowledge.
- If the answer depends on current Microsoft platform behavior and local knowledge is missing, stale, or ambiguous, use Microsoft Learn MCP.
- Prefer:
  - `microsoft-docs` for concepts, limits, setup, architecture, configuration
  - `microsoft-code-reference` for APIs, SDKs, CLI syntax, examples, and troubleshooting
- Use Microsoft Learn MCP before generic web search for Microsoft topics.
- For troubleshooting, validate the suspected root cause against official Microsoft Learn guidance when the error surface involves Azure or Microsoft platform behavior.

## Output expectations

- Name the source class used.
- Distinguish project policy from platform fact.
- If local and official Microsoft guidance disagree, treat:
  - local docs as authority for intended project design
  - Microsoft Learn MCP as authority for current external product behavior
