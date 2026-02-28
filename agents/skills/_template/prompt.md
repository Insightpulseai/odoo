# Skill: [SKILL_ID]

## Reasoning Strategy

<!-- How should the agent approach this skill? What context does it need? -->

1. **Gather context**: Read the SSOT files listed in `requires.ssot_files`
2. **Validate preconditions**: Ensure required secrets exist in the registry
3. **Execute**: Perform the skill's core action
4. **Verify**: Run all checks in `verification.checks`
5. **Produce evidence**: Write outputs to the evidence directory

## Edge Cases

<!-- What could go wrong? How should the agent handle it? -->

- If a required secret is missing: FAIL with the secret name needed
- If an SSOT file has drifted: re-read and re-validate before acting
- If verification fails: do NOT mark as complete — report the failing check

## Notes

<!-- Any additional reasoning guidance for the agent -->
