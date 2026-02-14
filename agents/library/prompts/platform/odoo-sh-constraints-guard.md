[ROLE] Coding agent in cloud IDE/CI runner. Execute, test, deploy, validate end-to-end with no manual UI.
[GOAL] Add a CI lint step that rejects changes incompatible with Odoo.sh constraints (no apt installs, no daemon processes, etc.).
[CONSTRAINTS] No UI steps; must be deterministic; surface violations with actionable messages.
[OUTPUT FORMAT]

1. Brief execution plan (3–5 bullets)
2. Apply commands
3. Test commands
4. Deploy/migration commands
5. Validation commands
6. Rollback strategy

Guardrails to detect:

- system package installs (apt/yum/apk) in scripts or Dockerfiles
- long-lived daemons (supervisord/systemd/while-true loops)
- websocket/longpoll overload patterns
- requirements that need compilation without build deps
