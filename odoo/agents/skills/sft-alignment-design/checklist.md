# SFT Alignment Design — Checklist

- [ ] Chat template selected and matches inference format
- [ ] Data formatted with correct special tokens and role markers
- [ ] Multi-turn conversations handled correctly
- [ ] max_seq_length set to match deployment context window
- [ ] Truncation strategy explicitly defined (left/right)
- [ ] Truncation rate measured and acceptable (<5%)
- [ ] Packing decision made with justification
- [ ] Packing preserves conversation boundaries (attention mask)
- [ ] Learning rate appropriate for SFT (typically 1e-5 to 5e-5)
- [ ] Evaluation strategy defined (steps or epoch)
- [ ] Validation set held out from training
- [ ] Quality assessment plan defined (automatic metrics + judge)
- [ ] Comparison to base model planned
