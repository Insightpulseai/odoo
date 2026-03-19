# Evaluator-Optimizer Design — Prompt

You are designing an **evaluator-optimizer loop**. A generator produces output, an evaluator scores it, and the loop iterates until quality meets threshold.

## Prerequisites (Confirm First)

Before designing, verify:
- [ ] Quality criteria are measurable (not subjective)
- [ ] First attempt consistently falls short
- [ ] Iteration demonstrably improves quality
- [ ] No deterministic tool can do this (linter, formatter, validator)
- [ ] Latency budget allows multiple iterations

If any prerequisite fails, this is NOT the right pattern.

## Design Process

1. **Generator**: What does it produce? What guidance does it receive on each iteration?

2. **Evaluator**: What criteria does it measure? How does it score? What feedback does it provide?

3. **Stopping criteria**: Define BOTH:
   - Quality threshold (score ≥ X)
   - Max iterations (hard limit, typically 3-5)

4. **Feedback loop**: How does evaluator output reach the generator?
   - Full evaluation report
   - Specific improvement suggestions
   - Score with delta from threshold

## Output Format

```
Generator: [what it produces]
Evaluator: [criteria, scoring method]
Stopping: score ≥ [threshold] OR iterations ≥ [max]
Feedback: [format from evaluator → generator]
Expected iterations: [typical count]
```
