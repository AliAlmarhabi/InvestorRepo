"""Paths, model parameters and documented data overrides for the Saudi market analysis."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
REPORT_DIR = ROOT / "reports"
CHART_DIR = REPORT_DIR / "charts"

AS_OF = "2026-11-05"          # last Tadawul close in the data (Thursday)
REPORT_DATE = "2026-11-07"

BENCHMARK = "KSA"             # iShares MSCI Saudi Arabia ETF (USD, riyal is pegged) - TASI proxy
OIL = "BZ=F"                  # Brent crude front-month future
NON_STOCKS = [BENCHMARK, OIL]

# Market snapshot (Yahoo Finance quotes, 5-6 Nov 2026)
TASI_LEVEL = 10095.42
KSA_ETF_PE = 13.58

# --- Factor weights for the composite score (sum to 1) ---
FACTOR_WEIGHTS = {
    "value": 0.25,      # earnings yield, dividend yield
    "quality": 0.20,    # ROE, balance sheet, cash generation
    "growth": 0.15,     # earnings growth, revenue growth, forward EPS growth
    "analyst": 0.20,    # upside to consensus target, recommendation
    "momentum": 0.10,   # 6-month total return, price vs 200-day average
    "risk": 0.10,       # low volatility, shallow drawdown
}

# --- Price-prediction model parameters ---
ANALYST_HAIRCUT = 0.25      # sell-side targets are historically optimistic: keep 75% of implied upside
ANALYST_WEIGHT = 0.5        # blend: 50% haircut analyst target, 50% relative-value fair value
PE_REVERSION = 1 / 3        # fair P/E moves one-third of the way from own P/E to the peer median in 12 months
MIN_SECTOR_PEERS = 3        # sectors with fewer listed peers use the universe median P/E as anchor
GEO_VOL_ADDON = 0.08        # extra annual volatility for war / blockade regime risk
BASE_RETURN_CAP = (-0.30, 0.40)
Z80 = 1.2816                # z-score for the 10th/90th percentile (80% interval)

# --- Data overrides, applied in data.py and documented in the report ---
# Forward EPS is used only when the implied growth vs trailing EPS sits inside this band;
# outside it, Yahoo's forward figure is usually stale or inconsistent with reported results.
FORWARD_EPS_GROWTH_BAND = (-0.15, 0.50)
# Forward EPS fields that are inconsistent with reported results even inside the band.
UNRELIABLE_FORWARD_EPS = {
    "7202.SR": "Yahoo forward EPS (13.12) implies +107% growth vs TTM 6.33; inconsistent with flat Q3 earnings.",
    "1180.SR": "Yahoo forward EPS (3.62) is below the 9M-2026 run-rate (~4.37 annualised); treated as stale.",
}
# Quarterly results published after the Yahoo snapshot was last refreshed (most recent quarter 2026-06-30).
POST_SNAPSHOT_RESULTS = {
    "4002.SR": {
        "eps_ttm": 4.19,             # TTM net income 850.4m - Q3-25 200m + Q3-26 188m, 200m shares
        "earnings_growth_q": -0.06,  # Q3-26 net profit SAR 188m, -6% y/y
        "source": "https://english.ajel.sa/business/o3x0al1qq",
    },
}
LOW_CONFIDENCE = {
    "2010.SR": "TTM profit margin is negative while TTM EPS is positive, and payout ratio is 323%: earnings are distorted by one-offs.",
    "2082.SR": "Trailing P/E of 63x and negative free cash flow; valuation rests on long-dated project pipeline.",
}

# Sector-level max picks (diversification rule)
MAX_PICKS_PER_SECTOR = 2
N_TOP_PICKS = 5
MIN_DAILY_VALUE_TRADED = 10e6   # SAR, liquidity floor for a pick
