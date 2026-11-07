# InvestorRepo: Saudi Stock Market (Tadawul) Analysis

A reproducible analysis of the Saudi stock market. It ranks 26 large TASI stocks, recommends the most
attractive ones with reasons, and predicts their prices over the next 3, 6 and 12 months with
uncertainty ranges.

**Read the report:** [`reports/saudi_market_report.md`](reports/saudi_market_report.md), or open
[`reports/saudi_market_report.html`](reports/saudi_market_report.html) in a browser. The HTML file is
self-contained, with charts embedded.

## Headline results (data as of 5 Nov 2026)

| # | Stock | Price (SAR) | 12-month base case | 80% range | Expected total return* |
|---|---|---:|---:|---:|---:|
| 1 | Riyad Bank (1010) | 20.22 | 23.02 | 18.67 - 28.39 | +19.1% |
| 2 | Saudi Awwal Bank, SAB (1060) | 32.06 | 36.12 | 28.41 - 45.93 | +18.9% |
| 3 | Mobily (7020) | 59.05 | 67.23 | 49.86 - 90.65 | +18.9% |
| 4 | Nahdi Medical (4164) | 93.00 | 101.44 | 73.94 - 139.18 | +14.7% |
| 5 | Mouwasat Medical (4002) | 55.15 | 65.20 | 47.79 - 88.95 | +22.1% |

\*Predicted price change plus dividend yield. TASI 12-month base case: about 10,850 (+7.5%), with an 80%
range of about 8,760 - 13,430.

**Market view:** cautiously positive and selective. Valuations are low after two losing years, but the
Iran conflict and the Red Sea blockade make the outlook unusually binary. The picks are domestic,
cash-generative, dividend-paying companies with little direct oil or shipping exposure.

> This is quantitative research for information and education, not personalised investment advice.
> Predictions are probabilistic and can be wrong; check live prices and consider a CMA-licensed adviser.

## How it works

1. **Data** (`data/raw/`): Yahoo Finance quotes and fundamentals for 26 stocks, plus two years of weekly
   dividend-adjusted prices for those stocks, the iShares MSCI Saudi Arabia ETF (KSA, a TASI proxy) and
   Brent crude. The data was pulled through Firecrawl's Yahoo Finance provider on 7 Nov 2026.
2. **Metrics** (`analysis/metrics.py`): returns, volatility, drawdown, beta, and correlation with oil.
3. **Scoring** (`analysis/scoring.py`): percentile-rank factors are combined into a 0-100 score.
   Value 25%, Quality 20%, Analyst 20%, Growth 15%, Momentum 10%, Low risk 10%. A robustness test
   redraws the weights 2,000 times.
4. **Price prediction** (`analysis/forecast.py`): the base case blends a relative-value fair value
   (P/E moving partway toward peers) with a haircut analyst consensus target. Ranges come from a
   log-normal model whose volatility includes an add-on for conflict risk.
5. **Selection**: Buy-rated stocks, at most two per sector, with a liquidity floor; the model portfolio
   is weighted by score divided by volatility.
6. **Report** (`analysis/report.py`, `analysis/narrative.py`): Markdown and HTML, with market context,
   sector views, investment theses, risks, catalysts and sources.

All parameters and data adjustments (for example, ignoring inconsistent forward EPS) are in
`analysis/config.py` and are listed in the report's methodology section.

## Run it

```bash
pip install -r requirements.txt
```

```bash
python run_analysis.py
```

Outputs are written to `reports/` (report and charts) and `data/processed/` (scores, predictions and
metrics as CSV).

## Updating the data

Replace the files in `data/raw/` with a fresh snapshot in the same format, then rerun:

- `fundamentals_<date>.csv`: one row per stock (update the file name in `analysis/data.py`)
- `weekly_part*.txt`: `SYMBOL|count|first_date|last_date|comma-separated weekly adjusted closes`

Update `AS_OF`, `TASI_LEVEL` and the narrative in `analysis/narrative.py` so the text matches the new
numbers.

## Repository layout

```
analysis/        config, data loading, metrics, scoring, forecast, charts, narrative, report builder
data/raw/        input snapshot (fundamentals CSV + weekly price series)
data/processed/  generated CSVs (clean prices, metrics, scores and predictions)
reports/         generated report (.md, .html) and charts/
run_analysis.py  entry point
```
