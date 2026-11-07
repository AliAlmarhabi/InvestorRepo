"""Build the Saudi stock market report from the data snapshot in data/raw/.

Usage:  python run_analysis.py
Output: reports/saudi_market_report.md, reports/saudi_market_report.html, reports/charts/*.png,
        data/processed/*.csv
"""
import pandas as pd

from analysis import charts, narrative
from analysis.config import BENCHMARK, NON_STOCKS, OIL, PROCESSED_DIR, REPORT_DIR
from analysis.data import load_fundamentals, load_weekly_prices, save_processed
from analysis.forecast import assign_ratings, model_portfolio, price_predictions, select_top_picks, tasi_outlook
from analysis.metrics import compute_price_metrics, covariance_annual, sector_returns
from analysis.report import build_html, build_markdown
from analysis.scoring import compute_scores, weight_robustness


def main():
    prices, fixes = load_weekly_prices()
    fund = load_fundamentals()
    save_processed(prices)

    metrics_all = compute_price_metrics(prices)
    metrics = metrics_all.drop(index=NON_STOCKS)
    scores = compute_scores(fund, metrics)
    pred = price_predictions(fund, metrics)
    ratings = assign_ratings(pred, scores)
    picks = select_top_picks(fund, scores, ratings)
    weights, portfolio = model_portfolio(picks, scores, pred, covariance_annual(prices, picks))
    tasi = tasi_outlook(pred, metrics_all.loc[BENCHMARK, "vol_1y"])
    robust = weight_robustness(scores)
    sectors = sector_returns(metrics, fund)

    # Machine-readable outputs
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    summary = (fund[["name", "sector", "price"]]
               .join(scores.drop(columns=["analyst_upside"]))
               .join(pred.drop(columns=["price"]))
               .join(ratings.rename("rating"))
               .join(robust)
               .sort_values("score", ascending=False))
    summary.round(4).to_csv(PROCESSED_DIR / "stock_scores_and_predictions.csv")
    metrics_all.round(4).to_csv(PROCESSED_DIR / "price_metrics.csv")

    # Charts
    names = pd.Series(narrative.SHORT_NAMES)
    charts.market_vs_oil(prices)
    charts.sector_returns(sectors)
    charts.composite_scores(scores, names, picks)
    charts.value_vs_return(pred, names, picks, extra_labels=["1120.SR", "2222.SR", "2082.SR", "4013.SR", "1211.SR"])
    for sym in picks:
        charts.price_forecast(sym, names[sym], prices[sym], pred.loc[sym])

    ctx = dict(fund=fund, metrics=metrics, scores=scores, pred=pred, ratings=ratings, picks=picks,
               weights=weights, portfolio=portfolio, tasi=tasi, robust=robust, sectors=sectors,
               bench=metrics_all.loc[BENCHMARK], oil=metrics_all.loc[OIL], fixes=fixes)
    md = build_markdown(ctx)
    (REPORT_DIR / "saudi_market_report.md").write_text(md, encoding="utf-8")
    (REPORT_DIR / "saudi_market_report.html").write_text(build_html(md), encoding="utf-8")

    print("Top picks:", ", ".join(f"{narrative.SHORT_NAMES[s]} ({s})" for s in picks))
    print(f"Portfolio expected 12m total return {portfolio['expected_total_return']:.1%}, "
          f"TASI base case {tasi['base']:,.0f}")
    print("Report written to", REPORT_DIR / "saudi_market_report.md")


if __name__ == "__main__":
    main()
