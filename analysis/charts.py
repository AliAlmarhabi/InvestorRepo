"""Static report charts (matplotlib). Palette and mark specs follow the validated reference palette:
categorical blue/orange, blue<->red diverging poles, thin marks, solid hairline grid, one y-axis per chart."""
import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from .config import BENCHMARK, CHART_DIR, OIL  # noqa: E402

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
AXIS = "#c3c2b7"
BLUE = "#2a78d6"
ORANGE = "#eb6834"
RED = "#e34948"
DE_EMPH = "#c3c2b7"
DPI = 200

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica"],
    "font.size": 9,
    "axes.facecolor": SURFACE,
    "figure.facecolor": SURFACE,
    "axes.edgecolor": AXIS,
    "axes.labelcolor": INK_2,
    "axes.titlecolor": INK,
    "axes.titlesize": 11,
    "axes.titleweight": "bold",
    "axes.titlelocation": "left",
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "axes.grid": True,
    "axes.axisbelow": True,
    "grid.color": GRID,
    "grid.linewidth": 0.6,
    "grid.linestyle": "-",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "legend.frameon": False,
    "legend.labelcolor": INK_2,
})


def _save(fig, name):
    CHART_DIR.mkdir(parents=True, exist_ok=True)
    path = CHART_DIR / name
    fig.savefig(path, dpi=DPI, bbox_inches="tight", facecolor=SURFACE)
    plt.close(fig)
    return path


def _subtitle(ax, text):
    ax.text(0, 1.02, text, transform=ax.transAxes, color=INK_2, fontsize=8.5, va="bottom")


def market_vs_oil(prices: pd.DataFrame):
    idx = prices[[BENCHMARK, OIL]] / prices[[BENCHMARK, OIL]].iloc[0] * 100
    fig, ax = plt.subplots(figsize=(8, 3.8))
    ax.plot(idx.index, idx[BENCHMARK], color=BLUE, lw=2, label="Saudi equities (iShares MSCI Saudi Arabia ETF)")
    ax.plot(idx.index, idx[OIL], color=ORANGE, lw=2, label="Brent crude")
    for s, c in ((BENCHMARK, BLUE), (OIL, ORANGE)):
        ax.plot(idx.index[-1], idx[s].iloc[-1], "o", ms=6, color=c, mec=SURFACE, mew=2)
        ax.annotate(f"{idx[s].iloc[-1]:.0f}", (idx.index[-1], idx[s].iloc[-1]), xytext=(6, 0),
                    textcoords="offset points", va="center", color=INK, fontsize=9)
    events = [("2026-03-02", "US/Israel strikes\non Iran"), ("2026-07-20", "Houthi blockade\non Saudi shipping")]
    for d, label in events:
        ax.axvline(pd.Timestamp(d), color=AXIS, lw=0.8)
        ax.text(pd.Timestamp(d), ax.get_ylim()[0], " " + label, color=MUTED, fontsize=7.5, va="bottom")
    ax.axhline(100, color=AXIS, lw=0.8)
    ax.set_title("Oil rallied, Saudi stocks did not", pad=22)
    _subtitle(ax, "Total return indexed to 100 on 4 Nov 2024, weekly")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %y"))
    ax.legend(loc="upper left", fontsize=8)
    ax.set_xlim(idx.index[0], idx.index[-1] + pd.Timedelta(days=45))
    return _save(fig, "market_vs_oil.png")


def sector_returns(sector_df: pd.DataFrame):
    d = sector_df.sort_values("ret_1y")
    fig, ax = plt.subplots(figsize=(7, 4.2))
    colors = [BLUE if v >= 0 else RED for v in d["ret_1y"]]
    y = np.arange(len(d))
    ax.barh(y, d["ret_1y"] * 100, height=0.55, color=colors)
    labels = [f"{s} ({n})" for s, n in zip(d.index, d["stocks"])]
    ax.set_yticks(y, labels, color=INK_2)
    for yi, v in zip(y, d["ret_1y"] * 100):
        ax.text(v + (0.8 if v >= 0 else -0.8), yi, f"{v:+.1f}%", va="center",
                ha="left" if v >= 0 else "right", color=INK, fontsize=8)
    ax.axvline(0, color=AXIS, lw=1)
    ax.grid(axis="y", visible=False)
    lo, hi = d["ret_1y"].min() * 100, d["ret_1y"].max() * 100
    ax.set_xlim(lo - 9, max(hi, 0) + 9)
    ax.set_xlabel("1-year total return, %")
    ax.set_title("Only energy and Jarir rose over the past year", pad=22)
    _subtitle(ax, "Equal-weighted 1-year total return by sector (number of stocks covered)")
    return _save(fig, "sector_returns.png")


def composite_scores(scores: pd.DataFrame, names: pd.Series, picks):
    d = scores.sort_values("score")
    fig, ax = plt.subplots(figsize=(7, 7.2))
    y = np.arange(len(d))
    colors = [BLUE if s in picks else DE_EMPH for s in d.index]
    ax.barh(y, d["score"], height=0.6, color=colors)
    ax.set_yticks(y, [f"{names[s]}  {s.replace('.SR', '')}" for s in d.index], color=INK_2, fontsize=8)
    for yi, (s, v) in zip(y, d["score"].items()):
        if s in picks:
            ax.text(v + 0.8, yi, f"{v:.0f}", va="center", color=INK, fontsize=8, fontweight="bold")
    ax.grid(axis="y", visible=False)
    ax.set_xlim(0, 100)
    ax.set_xlabel("Composite score (0-100)")
    ax.set_title("Composite factor score, top picks in blue", pad=22)
    _subtitle(ax, "Value 25% · Quality 20% · Analyst 20% · Growth 15% · Momentum 10% · Low risk 10%")
    return _save(fig, "composite_scores.png")


def value_vs_return(pred: pd.DataFrame, names: pd.Series, picks, extra_labels):
    d = pred.copy()
    fig, ax = plt.subplots(figsize=(7.5, 4.6))
    others = d[~d.index.isin(picks)]
    top = d[d.index.isin(picks)]
    ax.scatter(others["pe_norm"], others["total_return_12m"] * 100, s=46, color=DE_EMPH,
               edgecolor=SURFACE, linewidth=2, zorder=3, label="Other stocks")
    ax.scatter(top["pe_norm"], top["total_return_12m"] * 100, s=60, color=BLUE,
               edgecolor=SURFACE, linewidth=2, zorder=4, label="Top picks")
    offsets = {"1060.SR": (6, 8), "7020.SR": (6, 6), "1010.SR": (-22, -15), "4002.SR": (6, 4),
               "4164.SR": (6, -10), "1120.SR": (-55, -22), "2222.SR": (-30, -24)}
    for s in list(picks) + list(extra_labels):
        if s not in d.index:
            continue
        dx, dy = offsets.get(s, (6, 4))
        leader = dict(arrowstyle="-", color=AXIS, lw=0.8, shrinkA=1, shrinkB=4) if abs(dx) + abs(dy) > 16 else None
        ax.annotate(names[s], (d.loc[s, "pe_norm"], d.loc[s, "total_return_12m"] * 100), xytext=(dx, dy),
                    textcoords="offset points", fontsize=8, color=INK if s in picks else INK_2,
                    arrowprops=leader)
    ax.axhline(0, color=AXIS, lw=1)
    ax.set_xscale("log")
    ticks = [6, 8, 10, 15, 20, 30, 40, 60]
    ax.set_xticks(ticks, [f"{t}x" for t in ticks])
    ax.minorticks_off()
    ax.set_xlabel("P/E on normalised EPS (log scale)")
    ax.set_ylabel("Model 12-month total return, %")
    ax.set_title("Cheap stocks carry most of the expected return", pad=22)
    _subtitle(ax, "Each dot is one stock; expected return = predicted price change + dividend yield")
    ax.legend(loc="lower left", fontsize=8)
    return _save(fig, "value_vs_return.png")


def price_forecast(symbol: str, name: str, history: pd.Series, row: pd.Series):
    """Dividend-adjusted weekly history + median path and 80% band for the next 12 months."""
    h = history.iloc[-78:]                               # last 18 months
    t0 = h.index[-1]
    p0 = float(row["price"])
    weeks = np.arange(0, 53)
    dates = [t0 + pd.Timedelta(weeks=int(w)) for w in weeks]
    tfrac = weeks / 52
    g = np.log(row["target_12m"] / p0)
    median = p0 * np.exp(g * tfrac)
    spread = 1.2816 * row["sigma"] * np.sqrt(tfrac)
    lo, hi = median * np.exp(-spread), median * np.exp(spread)

    fig, ax = plt.subplots(figsize=(7.5, 3.4))
    ax.plot(h.index, h.values, color=BLUE, lw=2, label="Weekly close (dividend-adjusted)")
    ax.fill_between(dates, lo, hi, color=BLUE, alpha=0.12, lw=0, label="80% range")
    ax.plot(dates, median, color=BLUE, lw=2, ls=(0, (4, 3)), label="Base-case path")
    ax.plot(t0, p0, "o", ms=6, color=BLUE, mec=SURFACE, mew=2, zorder=5)
    end = dates[-1]
    ax.plot(end, median[-1], "o", ms=6, color=BLUE, mec=SURFACE, mew=2, zorder=5)
    ax.annotate(f"SAR {median[-1]:.2f}", (end, median[-1]), xytext=(6, 0), textcoords="offset points",
                va="center", fontsize=8.5, color=INK, fontweight="bold")
    ax.annotate(f"{hi[-1]:.2f}", (end, hi[-1]), xytext=(6, 0), textcoords="offset points",
                va="center", fontsize=8, color=INK_2)
    ax.annotate(f"{lo[-1]:.2f}", (end, lo[-1]), xytext=(6, 0), textcoords="offset points",
                va="center", fontsize=8, color=INK_2)
    ax.annotate(f"Today {p0:.2f}", (t0, p0), xytext=(10, -16), textcoords="offset points", ha="left",
                fontsize=8, color=INK_2)
    ax.set_xlim(h.index[0], end + pd.Timedelta(days=75))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %y"))
    ax.set_ylabel("SAR")
    ax.set_title(f"{name} ({symbol.replace('.SR', '')}): 12-month price prediction", pad=22)
    _subtitle(ax, "Base case and 80% range to Nov 2027")
    ax.legend(loc="upper left", fontsize=7.5, ncol=3)
    ymin = min(h.min(), lo.min()) * 0.95
    ymax = max(h.max(), hi.max()) * 1.08
    ax.set_ylim(ymin, ymax)
    return _save(fig, f"forecast_{symbol.replace('.SR', '')}.png")
