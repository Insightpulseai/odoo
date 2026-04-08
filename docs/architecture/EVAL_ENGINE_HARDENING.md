# Evaluation Engine Hardening Architecture
The Eval Engine treats AI judgment inherently as an untrusted bounding zone.

## Fail-Closed Semantics
The `EvalRunner` relies on a strict `Promise.race()` timeout cutoff alongside `Ajv` schema matchers bound to `ipai.eval_score.v1`. Any deviation (malformed JSON blob, confidence `< 0.8`, missing evidence arrays) structurally maps to an `ambiguous` or `fail` state explicitly. We never default to pass.
