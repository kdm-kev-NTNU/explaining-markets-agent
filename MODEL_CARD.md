<!-- em-model-card v1 disclosure=minimal -->

A hosted language model reads the competition's earnings materials and predicts where the stock's next-day abnormal return will rank across the quarter.

| Category | Classification |
| --- | --- |
| Approach | LLM / GenAI |
| Models | GPT-5.x |
| Information set | competition facts; earnings / fundamentals; estimates; prices / returns; historical company information |
| Learning / adaptation | zero-shot / prompted |
| Agent architecture | single-pass; self-consistency / committee |
| Prediction construction | direct LLM score |

## What is predicted

The abnormal (market-adjusted) stock return on the trading day after the earnings release, as a percentile between 0 and 1 across the quarter's events. A short rationale may be produced along the way. Only the percentile is submitted.

## Input context

The system reads the materials bundle delivered with the event: a pre-release research note when one is attached, pre-release option-market statistics when they are available, and a summary of the earnings call. It does not retrieve transcripts, filings, news, or the web, and it has no tools. No model is fitted on historical outcomes.

## Model & harness

A hosted general-purpose language model is prompted several times in parallel per asset with the same input and asked for the percentile directly. The answers are averaged, and pulled toward the midpoint when they disagree widely. There is no task-specific training, fine-tuning, or use of worked examples. If no call returns a usable number, a non-learned backup from the same bundle is submitted when one is available; otherwise a neutral midpoint is submitted so the event is not left blank.

## Data flow

Event notification → fetch the event materials → parallel model calls, averaged → percentile checked to lie between 0 and 1 → submitted.

## Limitations

- The same materials can produce a different percentile on another run.
- When the bundle is thin, the model has little besides the call summary and may lean on general knowledge it already has about the company.
- This description does not separate that prior from the supplied materials.
- When every model call fails, the backup is non-learned or a neutral midpoint, not an independent judgment.
- Delivery depends on a third-party model host.
