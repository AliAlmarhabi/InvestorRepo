"""Return, risk and market-sensitivity metrics from weekly total-return prices."""
import numpy as np
import pandas as pd

from .config import BENCHMARK, OIL

WEEKS_PER_YEAR = 52


def _ret(prices: pd.DataFrame, weeks: int) -> pd.Series:
    return prices.iloc[-1] / prices.iloc[-1 - weeks] - 1


def compute_price_metrics(prices: pd.DataFrame) -> pd.DataFrame:
    log_ret = np.log(prices).diff().dropna()
    last_year = log_ret.iloc[-WEEKS_PER_YEAR:]

    m = pd.DataFrame(index=prices.columns)
    m["ret_3m"] = _ret(prices, 13)
    m["ret_6m"] = _ret(prices, 26)
    m["ret_1y"] = _ret(prices, 52)
    m["ret_2y"] = prices.iloc[-1] / prices.iloc[0] - 1
    m["mom_12_1"] = prices.iloc[-5] / prices.iloc[-53] - 1     # skip the latest month
    m["vol_1y"] = last_year.std() * np.sqrt(WEEKS_PER_YEAR)
    m["max_drawdown_2y"] = (prices / prices.cummax() - 1).min()

    bench = last_year[BENCHMARK]
    m["beta_1y"] = last_year.apply(lambda s: s.cov(bench) / bench.var())
    m["corr_oil_2y"] = log_ret.apply(lambda s: s.corr(log_ret[OIL]))
    return m


def sector_returns(metrics: pd.DataFrame, fundamentals: pd.DataFrame) -> pd.DataFrame:
    joined = metrics.join(fundamentals[["sector"]], how="inner")
    out = joined.groupby("sector").agg(
        stocks=("ret_1y", "size"),
        ret_1y=("ret_1y", "mean"),
        ret_6m=("ret_6m", "mean"),
        ret_3m=("ret_3m", "mean"),
    )
    return out.sort_values("ret_1y")


def correlation_matrix(prices: pd.DataFrame, symbols) -> pd.DataFrame:
    log_ret = np.log(prices[list(symbols)]).diff().dropna().iloc[-WEEKS_PER_YEAR:]
    return log_ret.corr()


def covariance_annual(prices: pd.DataFrame, symbols) -> pd.DataFrame:
    log_ret = np.log(prices[list(symbols)]).diff().dropna().iloc[-WEEKS_PER_YEAR:]
    return log_ret.cov() * WEEKS_PER_YEAR
