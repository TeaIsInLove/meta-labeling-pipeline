# Meta-Labeling Pipeline

A meta-labeling and backtesting pipeline built on the methods in
López de Prado, *Advances in Financial Machine Learning* (AFML).

This project is judged on methodological honesty, not returns.

## What it does

A trivial **primary model** (moving-average crossover) decides direction and fires
events. A **secondary model** — the meta-labeler — is a binary classifier that decides
whether to act on each primary signal, and at what size. Meta-labeling estimates
P(trade profitable | primary signal fired), AFML Ch. 3 §3.6.

The primary model is deliberately dumb. Cleverness belongs in the evaluation,
not the signal.

## How it is validated

- **Sampling:** dollar bars, with the time-bar baseline retained for comparison (Ch. 2).
- **Labels:** triple-barrier — vol-scaled profit-take and stop-loss plus a time barrier,
  labelled on first touch. Barriers are sized only from information available at the
  event time (Ch. 3).
- **Sample weights:** uniqueness-based weighting for overlapping labels (Ch. 4).
- **Cross-validation:** purged K-fold with embargo. Time series are never shuffled (Ch. 7).
- **Reporting:** precision / recall / F1 on trades. Accuracy is not reported —
  meta-labels are imbalanced. Sharpe is reported alongside modelled transaction costs,
  max drawdown, the number of configurations tried, and a PBO caveat.

## What it cannot do

- It is not a trading system. No live data, no execution, no broker integration.
- Single instrument, daily-frequency free data. Nothing here generalises to
  intraday or to a cross-sectional universe without rework.
- Costs are modelled, not measured. Slippage is an assumption, not an observation.
- (Limitations are expanded as the build progresses. This section is written
  before shipping, not after criticism.)

## Status

Stage 1 of 9 — scaffold. No logic implemented yet.

## Reproducing

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```
