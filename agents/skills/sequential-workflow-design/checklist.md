# Sequential Workflow Design — Checklist

- [ ] Task confirmed as sequential (not parallel or single-call)
- [ ] Minimum number of steps identified
- [ ] Each step has clear input/output contract
- [ ] Quality gates defined between all steps
- [ ] Gate failure fallbacks specified
- [ ] No steps that could be merged without quality loss
- [ ] Total latency estimate is acceptable
- [ ] Each step is independently testable
