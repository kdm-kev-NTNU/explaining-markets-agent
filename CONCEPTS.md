# Concepts & sources

Glossary for terms used in [`README.md`](README.md) and [`APPROACH.md`](APPROACH.md). Definitions follow the competition’s public docs and scoring code; links are the primary sources.

## Primary sources

| Source | What it covers |
|---|---|
| [explainingmarkets.ai](https://explainingmarkets.ai/) | Competition home |
| [Docs](https://explainingmarkets.ai/docs) | Rules, API, materials, scoring overview |
| [Webhooks](https://explainingmarkets.ai/docs/webhooks) | Signed delivery, ACK / prediction clocks |
| [FAQ](https://explainingmarkets.ai/faq) | Knowledge cutoff, allowed data, IP |
| [Earnings previews (blog)](https://explainingmarkets.ai/blog/earnings-previews) | Q4 preview + option stats materials |
| [examples / scoring.py](https://github.com/explaining-markets/examples) | Public port of the production scorer (ΔR²) |
| [starter-modal](https://github.com/explaining-markets/starter-modal) | Reference webhook agent |

Working paper framing the benchmark: Koijen & Levy, *Assessing the Benefits of Optimized Agentic AI Systems for Asset Pricing* (University of Chicago Booth), run **in collaboration with Optiver**.

---

## Benchmark & score

**Explaining Markets**  
Live, quarterly, out-of-sample contest: agents predict how stocks move around earnings. Historical backtests suffer look-ahead bias and markets are reflexive, so the benchmark scores real-time predictions against realized outcomes.  
→ [explainingmarkets.ai](https://explainingmarkets.ai/), docs

**Look-ahead bias**  
Using information that would not have been available at decision time (e.g. training on the full history that includes the outcome). The competition’s `knowledge_cutoff` rule exists to forbid this.  
→ [FAQ](https://explainingmarkets.ai/faq)

**Knowledge cutoff**  
ISO 8601 UTC timestamp on each calendar event. The agent may not use any information from after that instant, except materials the platform delivers for the event.  
→ [FAQ](https://explainingmarkets.ai/faq), `GET /v1/events`

**`predicted_percentile`**  
Float in `[0, 1]`: where you predict this asset’s next-day abnormal return will rank **across all earnings events in the quarter** — not within the stock’s own history. `0` = most negative reaction in the quarter, `0.5` = median, `1` = most positive.  
→ Docs; starter `predict.py` docstring

**Abnormal return / `car1`**  
Next-day cumulative abnormal return: market-adjusted equity return on the earnings reaction window. One `(event, asset)` outcome.  
→ [examples scoring](https://github.com/explaining-markets/examples)

**Earnings surprise**  
How far reported results land from expectations (e.g. consensus). Ranked to `surprise_pct` the same way `car1` is ranked to `y`.  
→ Scoring docs / `scoring.py`

**R²**  
Share of variance in the outcome explained by a linear model. Here: how much of the cross-sectional rank `y` the regressors explain.

**ΔR² (delta R-squared)**  
`R²(full) − R²(surprise-only)`, where  
`y = α + β₁·predicted_percentile + β₂·surprise_pct`.  
The leaderboard metric: explained variation **beyond** the surprise benchmark. Restating the beat/miss does not help.  
→ [examples / scoring.py](https://github.com/explaining-markets/examples), Rules §5 in docs

**Own-sample vs common-sample ΔR²**  
Own-sample: score only on events you submitted. Common-sample (prize ranking): same event set for everyone; missed events are imputed with your prediction mean — skipping hurts.  
→ Docs / scoring notes in examples

**Affine remapping invariance**  
Any map `p → a + b·p` leaves ΔR² unchanged. Calibration and flipping the sign are unscored; only ranking information matters.  
→ Implied by OLS / ranking design in `scoring.py`

---

## Option surface (Optiver-linked materials)

Delivered as `option-implied-stats` when options are liquid enough; often missing. Measured **before** the release (`as_of`).  
→ [Earnings previews blog](https://explainingmarkets.ai/blog/earnings-previews), docs materials section

**Implied volatility (IV)**  
Volatility the options market prices into the contract — not historical realized vol.

**Implied earnings volatility**  
Option-implied standard deviation of the stock’s move on this earnings release.  
→ Materials: `implied_earnings_volatility`

**Implied absolute earnings move**  
Size of the move options price in; **directionless**. Often also summarized inside the earnings preview — avoid double-counting.  
→ Materials: `implied_absolute_earnings_move`

**25-delta skew**  
Call implied vol minus put implied vol at 25-delta. Negative skew ⇒ downside protection is priced richer than upside. Most directional of the three delivered stats.  
→ Materials: `skew_25_delta`

**Option surface / prior**  
The pre-release distribution implied by those stats. The agent’s edge is residual information relative to that prior and to the surprise benchmark.

---

## Event materials

**Earnings call facts** (`earnings-call-facts`)  
Post-cutoff bullet facts from the call. Always present for live scored events.  
→ Docs

**Earnings preview** (`earnings-preview`)  
Pre-cutoff research note (expectations, catalysts, scenarios) written before the release. Optional on some events; widely present in Q4.  
→ [Blog](https://explainingmarkets.ai/blog/earnings-previews)

**Information URL**  
Short-lived signed URL on the webhook payload; returns the materials JSON bundle. Select items by `id`, never by list position.

---

## Production contract

**Webhook ACK (20 s)**  
Time to verify the signature and return HTTP 200. Miss → retries; repeated failures can disable the webhook.  
→ [Webhooks docs](https://explainingmarkets.ai/docs/webhooks), [`agent/docs/advanced.md`](agent/docs/advanced.md)

**Prediction window (5 min)**  
Starts when you ACK. Submit before `prediction_deadline` or the prediction is tagged late and dropped from scoring.  
→ Same

**First prediction only**  
Only the first valid prediction per event is scored. Late / early / duplicate posts may return 201 but are ignored for ranking.  
→ Docs API section
