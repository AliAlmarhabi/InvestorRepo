"""Assemble the Markdown and self-contained HTML report from model outputs and narrative content."""
import base64
import re

import markdown
import pandas as pd

from . import narrative as N
from .config import (
    ANALYST_HAIRCUT, ANALYST_WEIGHT, AS_OF, BASE_RETURN_CAP, FACTOR_WEIGHTS, FORWARD_EPS_GROWTH_BAND,
    GEO_VOL_ADDON, KSA_ETF_PE, LOW_CONFIDENCE, MAX_PICKS_PER_SECTOR, MIN_DAILY_VALUE_TRADED, MIN_SECTOR_PEERS,
    PE_REVERSION, POST_SNAPSHOT_RESULTS, REPORT_DATE, REPORT_DIR, TASI_LEVEL, UNRELIABLE_FORWARD_EPS,
)


def pct(x, signed=True, digits=1):
    if pd.isna(x):
        return "n/a"
    return f"{x * 100:+.{digits}f}%" if signed else f"{x * 100:.{digits}f}%"


def num(x, digits=2):
    return "n/a" if pd.isna(x) else f"{x:,.{digits}f}"


def table(headers, rows, align=None):
    align = align or ["left"] + ["right"] * (len(headers) - 1)
    sep = ["---:" if a == "right" else ":---" for a in align]
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(sep) + " |"]
    lines += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(lines)


def build_markdown(ctx) -> str:
    f, m, s, p, r = ctx["fund"], ctx["metrics"], ctx["scores"], ctx["pred"], ctx["ratings"]
    picks, w, port, tasi, robust = ctx["picks"], ctx["weights"], ctx["portfolio"], ctx["tasi"], ctx["robust"]
    bench, oil = ctx["bench"], ctx["oil"]
    name = N.SHORT_NAMES
    out = []
    add = out.append

    add("# Saudi Stock Market Report: Analysis, Top Picks and 12-Month Price Predictions\n")
    as_of, rep = pd.Timestamp(AS_OF), pd.Timestamp(REPORT_DATE)
    add(f"*Data as of the Tadawul close on {as_of.day} {as_of:%B %Y} · report date "
        f"{rep.day} {rep:%B %Y} · universe: 26 large, liquid TASI stocks across 12 sectors*\n")
    add("> **Important:** this is a quantitative research report for information and education. It is not "
        "personalised investment advice. Price predictions are probabilistic estimates, not guarantees. "
        "Markets can move far outside the ranges shown, especially while the regional conflict continues. "
        "Check current prices and consider a CMA-licensed adviser before investing.\n")

    # ---------------- 1. Summary
    add("## 1. Summary\n")
    add(f"- **Market:** the TASI closed at **{TASI_LEVEL:,.0f}** on 5 Nov 2026, about 10.6% lower than a year "
        f"earlier. Over two years the KSA ETF (TASI proxy) returned **{pct(bench['ret_2y'])}** while Brent crude "
        f"rose **{pct(oil['ret_2y'])}**. The market trades at about **{KSA_ETF_PE:.1f}x** trailing earnings.")
    add(f"- **12-month TASI prediction:** base case **{tasi['base']:,.0f}** ({pct(tasi['base_return'])}), with "
        f"an 80% range of **{tasi['bear']:,.0f} - {tasi['bull']:,.0f}**; probability of being higher in 12 "
        f"months: about {tasi['prob_up'] * 100:.0f}%.")
    add(f"- **View:** {N.MARKET_VIEW}")
    add(f"- **Top 5 picks:** {', '.join(f'{name[x]} ({x[:4]})' for x in picks)}. As a model portfolio "
        f"(weights in section 6), the model expects a **{pct(port['expected_total_return'])} total return** over 12 months, "
        f"including a **{pct(port['dividend_yield'], signed=False)} dividend yield**, with estimated volatility "
        f"of {pct(port['volatility'], signed=False, digits=0)}.\n")

    rows = []
    for i, sym in enumerate(picks, 1):
        rows.append([
            i, f"**{name[sym]}** ({sym[:4]})", f.loc[sym, "sector"], num(p.loc[sym, "price"]),
            f"**{num(p.loc[sym, 'target_12m'])}**", pct(p.loc[sym, "price_return_12m"]),
            pct(p.loc[sym, "div_yield"], signed=False), f"**{pct(p.loc[sym, 'total_return_12m'])}**",
            f"{num(p.loc[sym, 'low_12m'])} - {num(p.loc[sym, 'high_12m'])}",
            f"{p.loc[sym, 'prob_up_12m'] * 100:.0f}%", r[sym],
        ])
    add(table(["#", "Stock", "Sector", "Price (SAR)", "12m target", "Price chg", "Div yield",
               "Total return", "80% range (12m)", "P(higher)", "Rating"], rows,
              ["left", "left", "left"] + ["right"] * 7 + ["left"]))
    add("\n*12m target = model base-case (median) price in Nov 2027. Total return = price change + "
        "indicated dividend yield. 80% range = 10th-90th percentile of the predicted price.*\n")

    # ---------------- 2. Market overview
    add("## 2. Market overview\n")
    add(table(["Indicator", "Latest", "Note"], [
        ["TASI", f"{TASI_LEVEL:,.0f}", "about -10.6% y/y, -4.6% over one month (Trading Economics)"],
        ["KSA ETF 1y / 2y total return", f"{pct(bench['ret_1y'])} / {pct(bench['ret_2y'])}", "USD; the riyal is pegged at 3.75"],
        ["KSA ETF volatility (1y)", pct(bench["vol_1y"], signed=False), "annualised, weekly data"],
        ["Market P/E (KSA ETF)", f"{KSA_ETF_PE:.1f}x", "trailing"],
        ["Brent crude", "$98.3", f"{pct(oil['ret_1y'])} over 1y; down about 15% in the week to 6 Nov"],
        ["SAMA repo rate", "4.25%", "follows the Fed because of the dollar peg"],
        ["Real GDP 2026 / 2027", "-3.6% / +12.8%", "Ministry of Finance (IMF: -3.3% / +7.9%)"],
        ["2027 budget deficit", "3.6% of GDP", "spending SAR 1.392trn"],
    ], ["left", "right", "left"]))
    add("\n### What is driving the market\n")
    for title, text in N.MACRO_POINTS:
        add(f"- **{title}.** {text}")
    add("\n![Saudi equities vs Brent](charts/market_vs_oil.png)\n")
    add("![Sector returns](charts/sector_returns.png)\n")
    sec = ctx["sectors"].sort_values("ret_1y", ascending=False)
    add(table(["Sector", "Stocks", "3m", "6m", "1y"], [
        [k, int(v["stocks"]), pct(v["ret_3m"]), pct(v["ret_6m"]), pct(v["ret_1y"])] for k, v in sec.iterrows()
    ]))
    add("\n*Equal-weighted total returns of the stocks covered in each sector.*\n")

    # ---------------- 3. Sector views
    add("## 3. Sector views\n")
    add(table(["Sector", "Stance", "Why"], [list(x) for x in N.SECTOR_VIEWS], ["left", "left", "left"]))
    add("")

    # ---------------- 4. Screening
    add("## 4. How the stocks were ranked\n")
    add("Each stock is ranked against the other 25 on six factors, using percentile ranks so that "
        "different units can be combined. The factors are then weighted into a 0-100 composite score:\n")
    add(table(["Factor", "Weight", "Signals"], [
        ["Value", pct(FACTOR_WEIGHTS["value"], False, 0), "earnings yield on normalised EPS, dividend yield"],
        ["Quality", pct(FACTOR_WEIGHTS["quality"], False, 0), "ROE (capped at 35%), debt/equity, positive free cash flow, payout below 100%"],
        ["Analyst", pct(FACTOR_WEIGHTS["analyst"], False, 0), "upside to the consensus mean target, average recommendation"],
        ["Growth", pct(FACTOR_WEIGHTS["growth"], False, 0), "latest-quarter earnings growth, revenue growth, forward EPS growth"],
        ["Momentum", pct(FACTOR_WEIGHTS["momentum"], False, 0), "6-month total return, price vs 200-day average"],
        ["Low risk", pct(FACTOR_WEIGHTS["risk"], False, 0), "1-year volatility, 2-year maximum drawdown"],
    ], ["left", "right", "left"]))
    add("\n![Composite scores](charts/composite_scores.png)\n")
    add("![P/E vs expected return](charts/value_vs_return.png)\n")
    add("### Full ranking\n")
    rows = []
    for sym in s.index:
        rows.append([
            f"{name[sym]} ({sym[:4]})", f.loc[sym, "sector"], num(f.loc[sym, "price"]),
            f"{p.loc[sym, 'pe_norm']:.1f}x", pct(f.loc[sym, "div_yield"], False), pct(f.loc[sym, "roe"], False, 0),
            pct(m.loc[sym, "ret_1y"]), pct(s.loc[sym, "analyst_upside"], digits=0), f"{s.loc[sym, 'score']:.0f}",
            num(p.loc[sym, "target_12m"]), pct(p.loc[sym, "total_return_12m"]), r[sym],
        ])
    add(table(["Stock", "Sector", "Price", "P/E*", "Div yld", "ROE", "1y TR", "Analyst upside", "Score",
               "12m target", "12m total return", "Rating"], rows,
              ["left", "left"] + ["right"] * 9 + ["left"]))
    add("\n*\\*P/E on normalised EPS: the average of trailing and forward EPS when the forward figure passes the "
        "consistency checks, otherwise trailing EPS. Rating rules: **Strong Buy** = score >= 65 and 12m total "
        "return >= 20%; **Buy** = score >= 55 and total return >= 12%; **Avoid** = negative expected return or "
        "score < 35; otherwise **Hold**. Low-confidence data caps a stock at Hold.*\n")
    add("**Robustness check.** The factor weights were redrawn at random 2,000 times (each weight varies by "
        "roughly ±40%). Share of draws in which each pick ranks in the top 5 by score: " +
        ", ".join(f"{name[x]} {robust[x] * 100:.0f}%" for x in picks) +
        ". Mouwasat scores lower than the others: it is the next-highest-scoring Buy once the two-per-sector "
        "cap has excluded SNB and Bank Albilad, so treat it as the higher-risk pick.\n")

    # ---------------- 5. Picks
    add("## 5. Top 5 picks: why invest, and price predictions\n")
    others = [x for x in s.index if r[x] in ("Buy", "Strong Buy") and x not in picks]
    if others:
        add("Also rated Buy but left out by the two-per-sector cap: " +
            ", ".join(f"{name[x]} ({x[:4]}, 12m target SAR {num(p.loc[x, 'target_12m'])}, total return "
                      f"{pct(p.loc[x, 'total_return_12m'])})" for x in others) +
            ". These are good alternatives or additions.\n")
    for i, sym in enumerate(picks, 1):
        t = N.THESES[sym]
        add(f"### {i}. {name[sym]} ({sym[:4]}): {t['headline']}\n")
        add(f"*{f.loc[sym, 'name']} · {f.loc[sym, 'sector']} · {f.loc[sym, 'industry']}*\n")
        add(table(["Price", "P/E", "Div yield", "ROE", "1y return", "Volatility", "Analysts", "Score", "Rating"], [[
            f"SAR {num(f.loc[sym, 'price'])}", f"{p.loc[sym, 'pe_norm']:.1f}x", pct(f.loc[sym, "div_yield"], False),
            pct(f.loc[sym, "roe"], False, 1), pct(m.loc[sym, "ret_1y"]), pct(m.loc[sym, "vol_1y"], False, 0),
            f"{int(f.loc[sym, 'analyst_count'])} (mean target {num(f.loc[sym, 'target_mean'])})",
            f"{s.loc[sym, 'score']:.0f}/100", r[sym]]], ["right"] * 8 + ["left"]))
        add("\n**Why invest**\n")
        for b in t["why"]:
            add(f"- {b}")
        add("\n**Price prediction**\n")
        add(table(["Horizon", "Base case (SAR)", "Change", "80% range (SAR)"], [
            [h, f"**{num(p.loc[sym, f'base_{k}'])}**", pct(p.loc[sym, f"base_{k}"] / p.loc[sym, "price"] - 1),
             f"{num(p.loc[sym, f'low_{k}'])} - {num(p.loc[sym, f'high_{k}'])}"]
            for h, k in (("3 months (Feb 2027)", "3m"), ("6 months (May 2027)", "6m"), ("12 months (Nov 2027)", "12m"))
        ]))
        add(f"\nBuilding blocks: relative-value fair value **SAR {num(p.loc[sym, 'fair_value'])}** "
            f"(fair P/E {p.loc[sym, 'pe_fair']:.1f}x) and haircut analyst target **SAR {num(p.loc[sym, 'analyst_adj'])}** "
            f"(raw consensus {num(p.loc[sym, 'analyst_target'])}). Expected 12-month total return "
            f"**{pct(p.loc[sym, 'total_return_12m'])}**; probability the price is higher in 12 months: about "
            f"**{p.loc[sym, 'prob_up_12m'] * 100:.0f}%**.\n")
        add(f"![{name[sym]} forecast](charts/forecast_{sym[:4]}.png)\n")
        add(f"**Risks:** {t['risks']}\n")

    # ---------------- 6. Portfolio
    add("## 6. Model portfolio\n")
    add("Weights are proportional to score divided by volatility, kept between 10% and 30%:\n")
    add(table(["Stock", "Weight", "12m target", "Expected total return", "Div yield"], [
        [f"{name[x]} ({x[:4]})", pct(w[x], False, 0), num(p.loc[x, "target_12m"]),
         pct(p.loc[x, "total_return_12m"]), pct(p.loc[x, "div_yield"], False)] for x in picks
    ] + [["**Portfolio**", "**100%**", "", f"**{pct(port['expected_total_return'])}**",
          f"**{pct(port['dividend_yield'], False)}**"]]))
    add(f"\nEstimated portfolio volatility: {pct(port['volatility'], False)} (realised "
        f"{pct(port['volatility_realised'], False)}, combined with an {pct(GEO_VOL_ADDON, False, 0)} conflict add-on). "
        "All five picks are domestic businesses whose profits depend on Saudi consumers, credit and rates. "
        "That keeps oil exposure low, but the basket is concentrated in banks and healthcare. Investors who want an oil hedge could add Aramco "
        "(Hold, 5.2% yield). Building positions in stages (for example, thirds over 2-3 months) reduces the "
        "risk of buying just before a geopolitical shock.\n")

    # ---------------- 7. Holds / avoid
    add("## 7. Quality holds and stocks to avoid\n")
    add("**Hold: good companies, limited upside at today's price**\n")
    add(table(["Stock", "12m target", "Total return", "Comment"], [
        [f"{name[x]} ({x[:4]})", num(p.loc[x, "target_12m"]), pct(p.loc[x, "total_return_12m"]), note]
        for x, note in N.HOLD_NOTES.items()
    ], ["left", "right", "right", "left"]))
    add("\n**Avoid for now**\n")
    add(table(["Stock", "Score", "12m target", "Total return", "Why"], [
        [f"{name[x]} ({x[:4]})", f"{s.loc[x, 'score']:.0f}", num(p.loc[x, "target_12m"]),
         pct(p.loc[x, "total_return_12m"]), note] for x, note in N.AVOID_NOTES.items()
    ], ["left", "right", "right", "right", "left"]))
    add("")

    # ---------------- 8. TASI
    add("## 8. TASI outlook: 12-month prediction\n")
    add(table(["Scenario", "TASI in Nov 2027", "Change", "What has to happen"], [
        ["Bull (90th pct)", f"{tasi['bull']:,.0f}", pct(tasi["bull"] / TASI_LEVEL - 1), N.SCENARIOS[0][1]],
        ["**Base (median)**", f"**{tasi['base']:,.0f}**", pct(tasi["base_return"]), N.SCENARIOS[1][1]],
        ["Bear (10th pct)", f"{tasi['bear']:,.0f}", pct(tasi["bear"] / TASI_LEVEL - 1), N.SCENARIOS[2][1]],
    ], ["left", "right", "right", "left"]))
    add(f"\nThe base case uses the median predicted price change across the 26 stocks. The range uses the "
        f"KSA ETF's realised volatility ({pct(bench['vol_1y'], False)}) plus the conflict add-on. Other "
        "forecasts: Trading Economics' model sees about 9,160 in 12 months; SNB Capital expected 10,000-11,700 "
        "for 2026. Our base case sits between the two, and the wide range reflects how binary the geopolitics "
        "are.\n")

    # ---------------- 9. Catalysts
    add("## 9. Catalysts to watch\n")
    add(table(["Date", "Event"], [list(c) for c in N.CATALYSTS], ["left", "left"]))
    add("")

    # ---------------- 10. Methodology
    lo, hi = FORWARD_EPS_GROWTH_BAND
    add("## 10. Methodology, assumptions and limitations\n")
    add("**Data.** Yahoo Finance quotes and fundamentals (snapshot of 5-6 Nov 2026) and two years of weekly "
        "dividend-adjusted prices for 26 stocks, the iShares MSCI Saudi Arabia ETF (KSA) and Brent futures, "
        "retrieved through Firecrawl. Yahoo's TASI history was unavailable, so the KSA ETF stands in for the "
        "index. News and company results come from the sources in section 11.\n")
    add("**Price model (per stock).**\n")
    add(f"1. *Relative-value fair value* = normalised EPS × fair P/E. The fair P/E moves "
        f"{PE_REVERSION:.0%} of the way from the stock's own P/E to its peer median: the sector median when the "
        f"sector has at least {MIN_SECTOR_PEERS} stocks, otherwise the median of all 26.")
    add(f"2. *Analyst view* = consensus mean target, keeping only {1 - ANALYST_HAIRCUT:.0%} of the implied "
        "upside, because sell-side targets are optimistic on average.")
    add(f"3. *Base case (12-month median)* = {ANALYST_WEIGHT:.0%} analyst view + {1 - ANALYST_WEIGHT:.0%} fair "
        f"value, capped at {pct(BASE_RETURN_CAP[0], digits=0)} / {pct(BASE_RETURN_CAP[1], digits=0)}.")
    add(f"4. *Range* = log-normal distribution, with volatility = sqrt(1-year realised volatility² + "
        f"{GEO_VOL_ADDON:.2f}²) for conflict regime risk. The 3- and 6-month figures lie on the same path, "
        "with the range scaled by sqrt(time).\n")
    add(f"**Selection rules.** Only Buy or Strong Buy ratings qualify; at most {MAX_PICKS_PER_SECTOR} per sector; "
        f"average daily traded value of at least SAR {MIN_DAILY_VALUE_TRADED / 1e6:.0f}m.\n")
    add("**Data adjustments.**\n")
    out_of_band = f.index[~f["eps_fwd_implied_growth"].between(lo, hi) & f["eps_fwd"].notna()]
    add(f"- Forward EPS is used only when it implies growth of {pct(lo, digits=0)} to {pct(hi, digits=0)} versus "
        "trailing EPS. Outside that band, Yahoo's forward figure is treated as unreliable (often stale or "
        "inconsistent with the latest results). This applies to " + ", ".join(name[x] for x in out_of_band) + ".")
    for sym, why in UNRELIABLE_FORWARD_EPS.items():
        add(f"- {name[sym]}: {why}")
    for sym, patch in POST_SNAPSHOT_RESULTS.items():
        add(f"- {name[sym]}: trailing EPS updated to {patch['eps_ttm']} and quarterly growth to "
            f"{pct(patch['earnings_growth_q'], digits=0)} for Q3 2026 results published after the snapshot "
            f"([source]({patch['source']})).")
    for sym, why in LOW_CONFIDENCE.items():
        add(f"- {name[sym]} (low-confidence data, so it cannot be rated above Hold): {why}")
    for col, date, bad, new in ctx["fixes"]:
        add(f"- {name.get(col, col)}: one-week price spike on {date} ({bad:.2f}, reversed the next week) "
            f"replaced with {new:.2f}.")
    add("\n**Limitations.** Covers 26 large caps, not the whole market. Fundamentals come from a single "
        "free data source and some fields lag the latest results. Weekly data understates intraday risk. "
        "Analyst targets and recommendations are treated as information, not truth. The log-normal range "
        "assumes no jumps; a war escalation or a peace deal could move prices beyond it. Rerun the analysis "
        "after major news or earnings.\n")

    # ---------------- 11. Sources
    add("## 11. Sources\n")
    for title, url in N.SOURCES:
        add(f"- [{title}]({url})")
    add("\n---\n*Generated by `run_analysis.py`. All tables and charts can be rebuilt from the data snapshot in "
        "`data/raw/`.*\n")
    return "\n".join(out)


CSS = """
body{font-family:system-ui,-apple-system,"Segoe UI",sans-serif;background:#f9f9f7;color:#0b0b0b;margin:0;line-height:1.55}
main{max-width:1060px;margin:0 auto;padding:32px 28px 64px;background:#fcfcfb}
h1{font-size:28px;line-height:1.25;margin-top:8px}h2{margin-top:44px;border-bottom:1px solid #e1e0d9;padding-bottom:6px}
h3{margin-top:32px}table{border-collapse:collapse;width:100%;font-size:13.5px;margin:12px 0;display:block;overflow-x:auto}
th,td{padding:6px 9px;border-bottom:1px solid #e1e0d9;vertical-align:top}th{color:#52514e;font-weight:600;text-align:left;background:#f4f3ef}
td{font-variant-numeric:tabular-nums}blockquote{margin:16px 0;padding:10px 16px;border-left:3px solid #eda100;background:#fff8e6;color:#52514e}
img{max-width:100%;height:auto;margin:12px 0}em{color:#52514e}a{color:#1c5cab}code{background:#f0efec;padding:1px 4px;border-radius:3px}
"""


def build_html(md_text: str) -> str:
    body = markdown.markdown(md_text, extensions=["tables"])

    def inline(match):
        path = REPORT_DIR / match.group(1)
        data = base64.b64encode(path.read_bytes()).decode()
        return f'src="data:image/png;base64,{data}"'

    body = re.sub(r'src="(charts/[^"]+\.png)"', inline, body)
    return (f"<!DOCTYPE html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' "
            f"content='width=device-width,initial-scale=1'><title>Saudi Stock Market Report - Nov 2026</title>"
            f"<style>{CSS}</style></head><body><main>{body}</main></body></html>")
