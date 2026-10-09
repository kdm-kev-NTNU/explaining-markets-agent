# Approach

Short note on how this agent is scored and how the signal is built. Term definitions and primary sources: [`CONCEPTS.md`](CONCEPTS.md). Deploy steps: [`agent/README.md`](agent/README.md).

## Scoring identity

One event yields one `(event, asset)` outcome: `car1`, the next-day cumulative abnormal return. Across the quarter, `car1` is percentile-ranked to `y ∈ [0, 1]`. Earnings surprise is ranked the same way to `surprise_pct`. Fit:

```
y = α + β₁·predicted_percentile + β₂·surprise_pct
```

**ΔR² = R²(full) − R²(surprise-only).** That is the leaderboard metric: explained variation beyond the surprise benchmark.

Consequences:

1. **Constant predictions ⇒ ΔR² = 0 exactly.** A flat 0.5 baseline earns nothing. It is only a last-resort delivery so a missed event is not imputed against you on the common sample.
2. **Affine remapping is unscored.** `p → a + b·p` leaves ΔR² unchanged. Calibration and sign flips do not help; ranking does.
3. **Skipping is punished.** Prize ranking uses common-sample ΔR²; missed events are imputed with your own prediction mean. Always submit something within the window.

## Signal

The benchmark already prices the raw surprise. Restating “beat / miss” adds no ΔR². Weight what surprise does not capture:

- Guidance and outlook vs the prior trajectory
- Forward-looking call content (novel vs repeated disclosure)
- Option-market positioning — especially 25-delta skew as a directional tilt, with implied move as a confidence modulator
- Scenario placement of realized facts against the pre-release preview’s bull / base / bear grid

Caveats built into the prompt path:

- Do not double-count implied move when the earnings preview already embeds option-implied size.
- Thin materials (no preview, no option stats — common on illiquid names) need an explicit missing-data branch; otherwise the model falls back to ticker priors.
- When the LLM is unavailable, the deterministic skew fallback still varies across events. Constant 0.5 is only the final delivery path.

## Production clocks

Two independent timers:

| Clock | Budget | Starts | Miss it and… |
|---|---|---|---|
| Delivery ACK | 20 s | platform POST | retries; repeated failures disable the webhook |
| Prediction window | 5 min | your 200 ACK | prediction tagged late, dropped from scoring |

ACK immediately, then predict. Only the **first** valid prediction per event is scored. Late, early, and duplicate posts are accepted but ignored for ranking.
