# Benchmark: Anthropic Skill Authoring Doctrine

> Source: Anthropic skill-creator blog, eval engineering posts
>
> Role: Skill design and testing benchmark for all skills in this repo
>
> This is NOT a runtime framework. It is a quality doctrine for skill authoring.

---

## Two Kinds of Skills

Every skill must be classified as one of:

| Type | Definition | Eval Strategy | Durability |
|------|-----------|---------------|------------|
| **capability_uplift** | Makes the model do something better than prompting alone | Regression testing; may become obsolete as models improve | Medium |
| **encoded_preference** | Sequences work according to team's process/doctrine | Fidelity validation; durable if process is accurate | High |

This distinction matters because:
- Capability uplift skills need periodic reassessment against improving base models
- Encoded preference skills need process accuracy validation, not capability testing

---

## Trigger Quality (First-Class Concern)

A skill must:
- **Trigger when it should** (recall) — missing valid invocations is a defect
- **NOT trigger when it shouldn't** (precision) — overfiring degrades trust

### Tuning Process

1. Analyze skill descriptions against sample prompts
2. Identify false positives (triggers on wrong prompts) and false negatives (misses valid prompts)
3. Evolve descriptions from implementation-focused ("how it works") → capability-focused ("what it provides")
4. Test trigger behavior as a first-class eval, not an afterthought

---

## Skill Description Quality

Descriptions are effectively prompt engineering for the routing layer:
- Be specific about what the skill does and when it applies
- Avoid vague descriptions that match too broadly
- Include domain terminology and boundary conditions
- Test naming schemes empirically — small changes produce measurable differences

---

## Eval Design

### Test Structure

Each eval consists of:
- **Test prompt** (plus files if needed)
- **Description of what good looks like** (success criteria)
- **Grading method** (code-based, model-based, or human)

### Eval Execution

- Use independent parallel agents in isolated contexts for uncontaminated evaluation
- Comparator agents: blind comparison judges assess outputs without knowing which version produced them
- Track: eval pass rates, execution time, token consumption, A/B comparisons

### Eval Types

| Type | When | Grader |
|------|------|--------|
| Single-turn | Simple input→output | Code-based (string match, regex, static analysis) |
| Multi-turn | Tool calls, state changes | Model-based (rubric scoring) |
| Agent evals | Mistakes compound, creative solutions | Model-based + human calibration |

### Grading Rules

- Grade outputs, not paths
- Implement partial credit for multi-component tasks
- Use pass@k when one good answer suffices; pass^k when reliability matters
- Validate LLM graders through human calibration
- Read transcripts regularly

### Eval Lifecycle

1. Capability evals: low pass rates → identify improvements
2. As evals saturate, graduate tasks to regression suites
3. Regression evals: ~100% baseline, detect backsliding
4. Refresh with harder challenges when saturated

---

## Swiss Cheese Model (Complementary Eval Methods)

No single eval method catches everything. Use all of:
- Automated evals for pre-launch CI/CD
- Production monitoring for distribution drift
- A/B testing for significant changes
- Manual transcript review for intuition
- Systematic human studies for calibration

---

## Tool Design for Skills

From Anthropic's tool-authoring guidance:
- Namespace prefixes grouped by service/resource
- Return high-signal data, strip noise
- Error messages must teach the agent what went wrong
- Tool descriptions are prompt engineering — invest heavily
- Feed eval transcripts back to Claude to analyze and refactor tools
- Use held-out test sets to prevent overfitting

---

## Sources

- [Improving skill creator](https://claude.com/blog/improving-skill-creator-test-measure-and-refine-agent-skills)
- [Demystifying evals](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
- [Writing tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents)
- [Advanced tool use](https://www.anthropic.com/engineering/advanced-tool-use)
