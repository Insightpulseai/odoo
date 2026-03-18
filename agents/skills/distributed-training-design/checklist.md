# Distributed Training Design — Checklist

- [ ] Memory requirements estimated (model + optimizer + gradients + activations)
- [ ] Single GPU fit check performed
- [ ] Mixed precision enabled (bf16 or fp16)
- [ ] Parallelism strategy selected with justification
- [ ] Gradient checkpointing evaluated (apply if memory-bound)
- [ ] Gradient accumulation configured for effective batch size
- [ ] CPU offloading evaluated (apply only if necessary)
- [ ] Hardware allocation defined (GPU type, count, topology)
- [ ] Throughput estimated (tokens/sec or samples/sec)
- [ ] Small-scale validation test planned (100 steps)
- [ ] All GPUs verified utilized (no idle GPUs)
- [ ] OOM protection verified
