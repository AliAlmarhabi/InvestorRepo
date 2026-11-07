"""Multi-factor composite score (0-100) for each stock in the universe.

Each raw signal is converted to a percentile rank inside the universe (0 = worst,
1 = best), signals are averaged into six factors, and factors are combined with
the weights in config.FACTOR_WEIGHTS.
"""
import numpy as np
import pandas as pd

from .config import FACTOR_WEIGHTS

FINANCIAL_SECTORS = {"Banks", "Insurance", "Diversified Financials"}


def _rank(s: pd.Series, higher_is_better: bool = True) -> pd.Series:
    """Percentile rank in [0, 1]; missing values get the neutral 0.5."""
    r = s.rank(pct=True, ascending=higher_is_better)
    r = (r - r.min()) / (r.max() - r.min())
    return r.fillna(0.5)


def compute_scores(f: pd.DataFrame, m: pd.DataFrame) -> pd.DataFrame:
    d = f.join(m, how="inner")
    is_fin = d["sector"].isin(FINANCIAL_SECTORS)

    # Value: normalised earnings yield + dividend yield
    earnings_yield = d["eps_norm"] / d["price"]
    value = (_rank(earnings_yield) + _rank(d["div_yield"])) / 2

    # Quality: ROE (capped so asset-light firms don't dominate), leverage, cash generation, payout sustainability
    roe = d["roe"].clip(upper=0.35)
    leverage = d["debt_to_equity"].where(~is_fin)          # banks/insurers: leverage is the business model
    fcf_ok = np.where(is_fin, 0.5, np.where(d["fcf"].isna(), 0.5, (d["fcf"] > 0).astype(float)))
    payout_ok = np.where(d["payout_ratio"] > 1.0, 0.0, 1.0)
    quality = (
        0.55 * _rank(roe)
        + 0.15 * _rank(leverage, higher_is_better=False)
        + 0.15 * pd.Series(fcf_ok, index=d.index)
        + 0.15 * pd.Series(payout_ok, index=d.index)
    )

    # Growth: latest-quarter earnings growth, revenue growth, forward EPS growth (winsorised)
    eps_growth_fwd = (d["eps_fwd"] / d["eps_ttm"] - 1).where(d["eps_fwd_reliable"])
    growth = (
        _rank(d["earnings_growth_q"].clip(-0.5, 0.5))
        + _rank(d["revenue_growth"].clip(-0.5, 0.5))
        + _rank(eps_growth_fwd.clip(-0.5, 0.5))
    ) / 3

    # Analyst: upside to consensus mean target and recommendation (1 = strong buy ... 5 = sell)
    upside = d["target_mean"] / d["price"] - 1
    analyst = 0.65 * _rank(upside) + 0.35 * _rank(d["rec_mean"], higher_is_better=False)

    # Momentum: 6-month total return and distance from 200-day average
    trend = d["price"] / d["ma200"] - 1
    momentum = (_rank(d["ret_6m"]) + _rank(trend)) / 2

    # Risk: low volatility and shallow drawdown score higher
    risk = (_rank(d["vol_1y"], higher_is_better=False) + _rank(d["max_drawdown_2y"])) / 2

    factors = pd.DataFrame(
        {"value": value, "quality": quality, "growth": growth,
         "analyst": analyst, "momentum": momentum, "risk": risk}
    )
    factors["score"] = 100 * sum(factors[k] * w for k, w in FACTOR_WEIGHTS.items())
    factors["analyst_upside"] = upside
    return factors.sort_values("score", ascending=False)


def weight_robustness(factors: pd.DataFrame, n_draws: int = 2000, top_n: int = 5, seed: int = 7) -> pd.Series:
    """Share of random factor weightings (Dirichlet around the base weights) that put each stock in the top N."""
    rng = np.random.default_rng(seed)
    names = list(FACTOR_WEIGHTS)
    base = np.array([FACTOR_WEIGHTS[k] for k in names])
    draws = rng.dirichlet(base * 20, size=n_draws)              # concentration 20: weights vary by roughly +/-40%
    scores = factors[names].values @ draws.T                    # stocks x draws
    ranks = (-scores).argsort(axis=0).argsort(axis=0)           # 0 = best
    return pd.Series((ranks < top_n).mean(axis=1), index=factors.index, name="top5_frequency")
