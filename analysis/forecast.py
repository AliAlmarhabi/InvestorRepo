"""12-month price predictions, ratings, top-pick selection, model portfolio and TASI outlook.

Price model (per stock):
  1. Relative-value fair value  FV = EPS_norm x P/E_fair,
     P/E_fair = PE_REVERSION x peer-median P/E + (1 - PE_REVERSION) x own P/E
     (peer = sector if it has >= MIN_SECTOR_PEERS stocks, else the whole universe).
  2. Analyst view               T_adj = P + (1 - ANALYST_HAIRCUT) x (consensus mean target - P).
  3. Base case (12-month median)  = ANALYST_WEIGHT x T_adj + (1 - ANALYST_WEIGHT) x FV, capped.
  4. Uncertainty: log-normal price with sigma = sqrt(realised vol^2 + GEO_VOL_ADDON^2);
     the 3/6/12-month medians lie on the geometric path from today's price to the base case.
"""
import math

import numpy as np
import pandas as pd

from .config import (
    ANALYST_HAIRCUT, ANALYST_WEIGHT, BASE_RETURN_CAP, GEO_VOL_ADDON, LOW_CONFIDENCE,
    MAX_PICKS_PER_SECTOR, MIN_DAILY_VALUE_TRADED, MIN_SECTOR_PEERS, N_TOP_PICKS, PE_REVERSION,
    TASI_LEVEL, Z80,
)

HORIZONS = {"3m": 0.25, "6m": 0.5, "12m": 1.0}


def _norm_cdf(x: float) -> float:
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def price_predictions(f: pd.DataFrame, m: pd.DataFrame) -> pd.DataFrame:
    d = f.join(m, how="inner")
    universe_median_pe = d["pe_norm"].median()
    sector_size = d.groupby("sector")["pe_norm"].transform("size")
    sector_median_pe = d.groupby("sector")["pe_norm"].transform("median")
    anchor_pe = np.where(sector_size >= MIN_SECTOR_PEERS, sector_median_pe, universe_median_pe)

    out = pd.DataFrame(index=d.index)
    out["price"] = d["price"]
    out["pe_norm"] = d["pe_norm"]
    out["pe_anchor"] = anchor_pe
    out["pe_fair"] = PE_REVERSION * anchor_pe + (1 - PE_REVERSION) * d["pe_norm"]
    out["fair_value"] = d["eps_norm"] * out["pe_fair"]
    out["analyst_target"] = d["target_mean"]
    out["analyst_adj"] = d["price"] + (1 - ANALYST_HAIRCUT) * (d["target_mean"] - d["price"])

    blended = ANALYST_WEIGHT * out["analyst_adj"] + (1 - ANALYST_WEIGHT) * out["fair_value"]
    blended = blended.fillna(out["fair_value"])
    lo, hi = BASE_RETURN_CAP
    out["target_12m"] = blended.clip(d["price"] * (1 + lo), d["price"] * (1 + hi))
    out["price_return_12m"] = out["target_12m"] / d["price"] - 1
    out["div_yield"] = d["div_yield"].fillna(0)
    out["total_return_12m"] = out["price_return_12m"] + out["div_yield"]

    out["sigma"] = np.sqrt(d["vol_1y"] ** 2 + GEO_VOL_ADDON ** 2)
    growth = np.log(out["target_12m"] / d["price"])
    for label, t in HORIZONS.items():
        median = d["price"] * np.exp(growth * t)
        spread = Z80 * out["sigma"] * np.sqrt(t)
        out[f"base_{label}"] = median
        out[f"low_{label}"] = median * np.exp(-spread)
        out[f"high_{label}"] = median * np.exp(spread)
    out["prob_up_12m"] = [_norm_cdf(g / s) for g, s in zip(growth, out["sigma"])]
    out["low_confidence"] = out.index.isin(list(LOW_CONFIDENCE))
    return out


def assign_ratings(pred: pd.DataFrame, scores: pd.DataFrame) -> pd.Series:
    d = pred.join(scores[["score"]])

    def rate(row):
        tr, s = row["total_return_12m"], row["score"]
        if tr < 0 or s < 35:
            return "Avoid"
        if row["low_confidence"]:
            return "Hold"
        if s >= 65 and tr >= 0.20:
            return "Strong Buy"
        if s >= 55 and tr >= 0.12:
            return "Buy"
        return "Hold"

    return d.apply(rate, axis=1)


def select_top_picks(f, scores, ratings, n=N_TOP_PICKS):
    d = f[["sector", "daily_value_traded"]].join(scores[["score"]]).join(ratings.rename("rating"))
    d = d[d["rating"].isin(["Strong Buy", "Buy"]) & (d["daily_value_traded"] >= MIN_DAILY_VALUE_TRADED)]
    picks, per_sector = [], {}
    for sym, row in d.sort_values("score", ascending=False).iterrows():
        if per_sector.get(row["sector"], 0) >= MAX_PICKS_PER_SECTOR:
            continue
        picks.append(sym)
        per_sector[row["sector"]] = per_sector.get(row["sector"], 0) + 1
        if len(picks) == n:
            break
    return picks


def model_portfolio(picks, scores, pred, cov, cap=0.30, floor=0.10):
    """Weights proportional to score / volatility, clipped to [floor, cap] and renormalised."""
    raw = scores.loc[picks, "score"] / pred.loc[picks, "sigma"]
    w = raw / raw.sum()
    for _ in range(20):
        w = w.clip(floor, cap)
        w = w / w.sum()
    exp_ret = float((w * pred.loc[picks, "total_return_12m"]).sum())
    div = float((w * pred.loc[picks, "div_yield"]).sum())
    c = cov.loc[picks, picks].values
    realised_vol = float(np.sqrt(w.values @ c @ w.values))
    vol = math.sqrt(realised_vol ** 2 + GEO_VOL_ADDON ** 2)
    return w, {"expected_total_return": exp_ret, "dividend_yield": div,
               "volatility_realised": realised_vol, "volatility": vol}


def tasi_outlook(pred: pd.DataFrame, bench_vol: float):
    """Index base case = median stock base-case price return; band from benchmark volatility."""
    base_ret = float(pred["price_return_12m"].median())
    sigma = math.sqrt(bench_vol ** 2 + GEO_VOL_ADDON ** 2)
    base = TASI_LEVEL * (1 + base_ret)
    return {
        "level": TASI_LEVEL,
        "base_return": base_ret,
        "sigma": sigma,
        "base": base,
        "bear": base * math.exp(-Z80 * sigma),
        "bull": base * math.exp(Z80 * sigma),
        "prob_up": _norm_cdf(math.log(1 + base_ret) / sigma),
    }
