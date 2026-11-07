"""Load the raw snapshot files into clean pandas objects."""
import numpy as np
import pandas as pd

from .config import (
    FORWARD_EPS_GROWTH_BAND, POST_SNAPSHOT_RESULTS, PROCESSED_DIR, RAW_DIR, UNRELIABLE_FORWARD_EPS,
)


def _parse_weekly_files():
    series, starts = {}, set()
    for path in sorted(RAW_DIR.glob("weekly_part*.txt")):
        for line in path.read_text().strip().splitlines():
            symbol, count, start, _end, values = line.split("|")
            vals = [float(v) for v in values.split(",")]
            if len(vals) != int(count):
                raise ValueError(f"{symbol}: expected {count} values, got {len(vals)}")
            series[symbol] = vals
            starts.add(start)
    if len(starts) != 1:
        raise ValueError(f"Series start on different dates: {starts}")
    return series, starts.pop()


def fix_single_week_spikes(prices: pd.DataFrame, threshold: float = 0.25):
    """Replace one-week spikes that fully reverse (bad ticks) with the neighbours' geometric mean."""
    fixed = prices.copy()
    log = []
    for col in fixed.columns:
        p = fixed[col].to_numpy(dtype=float, copy=True)
        for t in range(1, len(p) - 1):
            up, down = p[t] / p[t - 1], p[t + 1] / p[t]
            spike = (up > 1 + threshold and down < 1 / (1 + threshold)) or (
                up < 1 / (1 + threshold) and down > 1 + threshold
            )
            if spike:
                new = float(np.sqrt(p[t - 1] * p[t + 1]))
                log.append((col, fixed.index[t].date().isoformat(), p[t], round(new, 2)))
                p[t] = new
        fixed[col] = p
    return fixed, log


def load_weekly_prices():
    """Weekly dividend-adjusted closes (total-return basis), one column per symbol.

    Yahoo appends the latest trade as an extra point after the last weekly bar;
    that point is used as the close of the final (current) week.
    """
    series, start = _parse_weekly_files()
    lengths = {len(v) for v in series.values()}
    if len(lengths) != 1:
        raise ValueError(f"Series have different lengths: {lengths}")
    n = lengths.pop() - 1
    dates = pd.date_range(start, periods=n, freq="7D")
    frame = pd.DataFrame({s: v[:-2] + [v[-1]] for s, v in series.items()}, index=dates)
    frame.index.name = "week"
    frame, fixes = fix_single_week_spikes(frame)
    return frame, fixes


def load_fundamentals():
    f = pd.read_csv(RAW_DIR / "fundamentals_2026-11-05.csv", index_col="symbol")
    for sym, patch in POST_SNAPSHOT_RESULTS.items():
        for col, val in patch.items():
            if col != "source":
                f.loc[sym, col] = val
        f.loc[sym, "pe_ttm"] = f.loc[sym, "price"] / f.loc[sym, "eps_ttm"]

    lo, hi = FORWARD_EPS_GROWTH_BAND
    implied = f["eps_fwd"] / f["eps_ttm"] - 1
    f["eps_fwd_implied_growth"] = implied
    f["eps_fwd_reliable"] = implied.between(lo, hi) & ~f.index.isin(list(UNRELIABLE_FORWARD_EPS))
    f.loc[~f["eps_fwd_reliable"], "pe_fwd"] = np.nan
    # Normalised EPS: average of trailing and forward when forward is usable, else trailing
    f["eps_norm"] = np.where(
        f["eps_fwd_reliable"] & f["eps_fwd"].notna(),
        (f["eps_ttm"] + f["eps_fwd"]) / 2,
        f["eps_ttm"],
    )
    f["pe_norm"] = f["price"] / f["eps_norm"]
    f["daily_value_traded"] = f["avg_vol_3m"] * f["price"]
    return f


def save_processed(prices: pd.DataFrame):
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    prices.round(4).to_csv(PROCESSED_DIR / "weekly_total_return_prices.csv")
