# Skill Trigger Tuning — Prompt

You are tuning when a skill triggers. Trigger quality has two dimensions:

- **Precision**: When the skill fires, is it relevant? (Reduce false positives)
- **Recall**: When a relevant prompt arrives, does the skill fire? (Reduce false negatives)

## Process

### 1. Baseline Test
Run the skill's current triggers against:
- Positive samples: prompts that SHOULD trigger the skill
- Negative samples: prompts that should NOT trigger the skill

### 2. Error Analysis
- **False positives**: Skill fired but shouldn't have. Why? Description too broad? Trigger too generic?
- **False negatives**: Skill didn't fire but should have. Why? Description too narrow? Missing trigger condition?

### 3. Description Refinement
Shift from implementation-focused → capability-focused:
- Bad: "This skill runs oca-port and upgrade_code commands"
- Good: "This skill migrates OCA modules between Odoo versions"

### 4. Trigger Refinement
Adjust trigger conditions:
- Add domain-specific keywords for missed cases
- Add exclusion conditions for false positive cases
- Test boundary cases

### 5. Re-Test
Run all samples again. Compare precision/recall to baseline.

## Output

```
Baseline: precision=[X]%, recall=[X]%
After tuning: precision=[X]%, recall=[X]%
Changes: [what was modified]
Remaining issues: [any unresolved edge cases]
```
