# Parallel Workflow Design — Checklist

- [ ] Subtask independence verified (no hidden cross-dependencies)
- [ ] Aggregation strategy designed BEFORE implementation
- [ ] Each branch has clear input/output contract
- [ ] Failure handling policy defined (fail-fast / best-effort / retry)
- [ ] Concurrency limits set
- [ ] Sub-pattern chosen (sectioning vs. voting)
- [ ] Result ordering requirements documented
