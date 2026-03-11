[ROLE] Coding agent in cloud IDE/CI runner. Execute, test, deploy, validate end-to-end with no manual UI.
[GOAL] Audit OCA/ai (18.0) for LLM-related addons and extract best-practice patterns applicable to Odoo 19 CE + OCA + minimal IPAI glue.
[CONSTRAINTS] No UI steps; CLI only; produce a machine-readable inventory; cite file paths; avoid speculation.

[OUTPUT FORMAT]

1. 3–5 bullet execution plan
2. Commands to clone/update repo + scan
3. Inventory table (module -> purpose -> deps -> risks)
4. Recommended adoption plan (submodule layout + addons_path + config)
5. Validation commands + rollback

[STEPS]

1. Clone/update https://github.com/OCA/ai.git @ 18.0
2. Enumerate addons/ directories
3. For each addon, parse **manifest**.py (deps, external deps, installable)
4. Grep for provider keys (openai/ollama/llm/embedding/chat)
5. Flag Odoo.sh risk patterns (long-lived connections, daemons, websocket overload)
6. Output inventory as JSON + Markdown
