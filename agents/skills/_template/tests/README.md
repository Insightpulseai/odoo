# Skill Tests

Place test scripts here that validate:

1. **Schema**: `skill.yaml` conforms to `agents/skills/schema/skill.schema.json`
2. **Secret deny**: No plaintext secrets in any skill file
3. **Output assertions**: Expected artifacts exist after execution
4. **Idempotency**: Running twice produces same result (if `policies.idempotent: true`)

Tests are run by: `scripts/ci/check_agent_skills.py`
