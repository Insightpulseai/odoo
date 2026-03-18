# SFT Alignment Design — Evals

## Eval Dimensions

| Dimension | Weight | Criteria |
|-----------|--------|----------|
| Chat template correctness | 25% | Template matches inference format, special tokens correct |
| Truncation handling | 20% | Explicit strategy, rate measured, acceptable threshold |
| Packing decision | 15% | Justified choice, boundary preservation addressed |
| Training config | 20% | Appropriate lr, epochs, evaluation frequency |
| Eval plan | 20% | Automatic metrics + judge + baseline comparison |

## Test Cases

### TC-1: Basic SFT design
- Input: "Align SmolLM2-1.7B as a chat assistant using 50K instruction pairs"
- Expected: Chat template defined, max_seq_length set, packing enabled, eval plan with judge
- Fail if: No chat template specified or truncation strategy missing

### TC-2: Long-context SFT
- Input: "SFT for document Q&A with 8K context conversations"
- Expected: Higher max_seq_length, truncation strategy addressed, packing likely disabled
- Fail if: max_seq_length too short for task or silent truncation

### TC-3: Template mismatch check
- Input: "Use ChatML template for training but deploy with Llama template"
- Expected: Warning about template mismatch between training and inference
- Fail if: Accepts mismatched templates without flagging

## Pass threshold: Template defined and matches inference, truncation explicit, eval plan present
