# ETA Computation

We use an EMA per-symbol timing estimate:

```python
t_i = alpha * measured + (1 - alpha) * t_i
eta = sum(t_i_remaining) / workers
```

Used in `src/pipeline/eta.py`.
