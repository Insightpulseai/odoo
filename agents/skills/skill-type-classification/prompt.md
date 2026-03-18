# Skill Type Classification — Prompt

You are classifying an agent skill. Every skill must be one of two types:

## Type 1: Capability Uplift

The skill makes the model **do something better than prompting alone**.

Indicators:
- Without the skill, the model struggles or fails at the task
- The skill provides domain knowledge, specialized reasoning, or enhanced tool use
- As base models improve, this skill may become unnecessary

**Eval strategy**: Regression testing — track if the skill still provides uplift over base model.

## Type 2: Encoded Preference

The skill **sequences work according to your team's process or doctrine**.

Indicators:
- The model COULD do the task differently, but your team wants it done THIS way
- The skill encodes organizational decisions, conventions, or workflows
- Even if the model improves, the process remains the same

**Eval strategy**: Fidelity validation — verify the skill accurately follows the encoded process.

## Decision

Ask: "If I removed this skill and just prompted the base model, would it..."
- ...fail at the task? → **capability_uplift**
- ...do the task but not the way we want? → **encoded_preference**

## Output

```
Skill: [name]
Classification: [capability_uplift | encoded_preference]
Reasoning: [why this classification]
Eval strategy: [regression_testing | fidelity_validation]
Durability: [medium | high]
Reassessment trigger: [when to re-check]
```
