# Fine-Tuning Recipe Design — Checklist

- [ ] Approach selected: full fine-tuning vs LoRA vs QLoRA
- [ ] Base model identified
- [ ] Learning rate set appropriately (lower than pretraining)
- [ ] Number of epochs defined (typically 2-5)
- [ ] Batch size configured
- [ ] Warmup ratio set
- [ ] Scheduler selected
- [ ] PEFT config defined (if using LoRA/QLoRA: rank, alpha, dropout, target modules)
- [ ] Task-specific evaluation metrics defined
- [ ] General benchmark baseline recorded (catastrophic forgetting check)
- [ ] Early stopping configured with patience
- [ ] Best model selection criteria defined
- [ ] Evaluation frequency set
- [ ] Compute budget estimated
