"""Qualitative content for the report: market context, sector views, investment theses and sources.

Numbers quoted here come from company results and news published up to 7 Nov 2026 (see SOURCES);
all model numbers (scores, predicted prices, ranges) are computed in code and inserted by report.py.
"""

SHORT_NAMES = {
    "2222.SR": "Aramco", "1120.SR": "Al Rajhi", "1180.SR": "SNB", "1150.SR": "Alinma",
    "1010.SR": "Riyad Bank", "1060.SR": "SAB", "1140.SR": "Albilad", "2010.SR": "SABIC",
    "1211.SR": "Ma'aden", "2020.SR": "SABIC AN", "7010.SR": "stc", "7020.SR": "Mobily",
    "5110.SR": "Saudi Energy", "2082.SR": "ACWA Power", "4013.SR": "Al Habib", "4002.SR": "Mouwasat",
    "4164.SR": "Nahdi", "2280.SR": "Almarai", "4190.SR": "Jarir", "7203.SR": "Elm",
    "7202.SR": "solutions", "8210.SR": "Bupa Arabia", "8010.SR": "Tawuniya", "1111.SR": "Tadawul Group",
    "4263.SR": "SAL", "4142.SR": "Riyadh Cables",
}

MARKET_VIEW = (
    "**Cautiously positive, and selective.** Saudi shares are cheap after two losing years: about 13.6x "
    "trailing earnings, with many large companies yielding 5-6%. A lot of bad news is already in the price. "
    "But the market is hostage to the Iran conflict and the Red Sea blockade, and either can move prices "
    "10% in a week. We favour **domestic, cash-generative, dividend-paying companies with little direct "
    "oil or shipping exposure**: value banks, telecoms and healthcare. We avoid expensive growth stories and "
    "Gulf-coast exporters whose shipments depend on the Strait of Hormuz."
)

MACRO_POINTS = [
    ("War and shipping disruption dominate 2026",
     "Brent crude jumped from about $65 to over $110 a barrel after US and Israeli strikes on Iran in early "
     "March. That followed months of disruption in the Strait of Hormuz. On 20 July the Houthis declared a "
     "maritime blockade on Saudi shipping, and Saudi crude loadings through Bab al-Mandeb fell to near zero; "
     "exports were rerouted via Suez. Brent peaked near $118 in late October, then fell about 15% in the week "
     "to 6 November, to $98.3, on hopes of a US-Iran deal. Tanker attacks have not stopped."),
    ("High oil prices did not help the stock market",
     "Over two years the KSA ETF (our TASI proxy) fell about 11% in total-return terms while Brent rose about "
     "33%. Higher prices were offset by lost export volumes, attacks on facilities and a weaker non-oil "
     "economy. The TASI closed at 10,095 on 5 November: about 10.6% lower than a year earlier and 4.6% "
     "lower than a month earlier. That follows a 12.8% fall in 2025, its worst year in almost a decade."),
    ("The economy shrinks in 2026, with a rebound expected in 2027",
     "The Ministry of Finance expects real GDP to fall 3.6% in 2026 and rebound 12.8% in 2027; the IMF says "
     "-3.3% and +7.9%. The 2026 budget deficit is estimated at SAR 245bn, against SAR 165bn planned. The "
     "2027 pre-budget statement plans spending of SAR 1.392trn and a deficit of 3.6% of GDP, funded by more "
     "borrowing. Government spending, the main driver of non-oil demand, stays under pressure."),
    ("Interest rates should fall",
     "The Saudi central bank (SAMA) repo rate is 4.25%, after three cuts in late 2025. Because the riyal is "
     "pegged to the dollar, SAMA follows the US Fed; local brokers expect further cuts. Lower rates trim "
     "banks' lending margins slightly, but they support share valuations, mortgages and consumer credit."),
    ("Q3 2026 earnings were resilient",
     "Combined Q3 bank profit rose about 4.8%: Al Rajhi +11.7% to a record SAR 7.1bn, Riyad Bank +6.6%, "
     "SNB -0.3%. Aramco's adjusted net income rose 9% to SAR 117bn, and free cash flow was SAR 105.8bn, despite "
     "attacks on its facilities. SAL +28%, Nahdi +6.6%, Mobily +1%, SAB +1%, Mouwasat -6%."),
    ("Market reforms could bring foreign money",
     "Since 1 February 2026 any foreign investor can buy Saudi shares directly; the old qualified "
     "foreign investor (QFI) regime is gone. The Capital Market Authority (CMA) is reviewing the 49% cap on "
     "foreign ownership; reports point to 75%. Morgan Stanley estimates $4.3-7.4bn of passive inflows, mostly "
     "into large banks with high free float."),
]

SECTOR_VIEWS = [
    ("Banks", "Overweight",
     "About 9x earnings, 4.5-6% yields and steady profit growth. They benefit most if the foreign-ownership "
     "cap rises. We prefer cheap Riyad Bank and SAB to Al Rajhi, which trades at 3.1x book value and is priced "
     "for growth."),
    ("Healthcare", "Overweight (selective)",
     "Demand is structural: a growing, ageing population, compulsory health insurance and privatisation. "
     "Mouwasat (13x) and Nahdi (14x) have de-rated to attractive levels; Al Habib is high quality but already "
     "priced at about 29x."),
    ("Telecom", "Overweight Mobily, Neutral stc",
     "Defensive cash flows and about 5% yields, with little link to oil. Mobily is cheaper than stc: 12.4x "
     "earnings and 7.0x EV/EBITDA, against 14.6x and 9.5x."),
    ("Energy", "Neutral",
     "Aramco has record free cash flow and a 5.2% yield, but analysts expect lower earnings next year as "
     "oil prices settle. Good for income; limited upside."),
    ("Insurance", "Neutral",
     "Premiums are growing fast, but claims inflation is hitting profits: Tawuniya H1 -16% and Q2 -31%; "
     "Bupa's latest quarter -5%."),
    ("Consumer", "Neutral",
     "Jarir has momentum (+29% over a year) but is now fairly priced; Almarai has analyst support but "
     "negative free cash flow because of heavy capex."),
    ("Technology", "Neutral",
     "Elm and solutions by stc have de-rated (down 28% and 22% over a year) on tighter government IT budgets. "
     "Wait for clarity in the 2027 budget."),
    ("Industrials", "Neutral",
     "SAL is a high-quality growth company (Q3 profit +28%) but is fairly valued; Riyadh Cables is cheap, but "
     "its forward earnings are uncertain."),
    ("Materials", "Underweight",
     "SABIC's earnings are distorted and its ROE is close to zero; Ma'aden trades at about 30x with no "
     "dividend; SABIC Agri-Nutrients' Q3 profit fell 62.5%. They would rebound if Hormuz traffic "
     "normalised."),
    ("Utilities", "Underweight",
     "ACWA Power trades at 63x trailing earnings with negative free cash flow and 92% debt/equity; Saudi "
     "Energy has a 5% ROE and large negative free cash flow."),
    ("Diversified financials", "Underweight",
     "Saudi Tadawul Group's earnings fell 42% on lower trading activity, and the stock still trades at 41x."),
]

THESES = {
    "1010.SR": {
        "headline": "The cheapest large Saudi bank, with steady growth and a 5% yield",
        "why": [
            "**Valuation:** about 7.3x normalised earnings and 1.21x book value for a 13.3% ROE. The bank "
            "median is about 9.3x.",
            "**Earnings:** Q3 2026 net profit rose 6.6% to SAR 2.87bn; 9M 2026 is up about 5% to SAR 8.13bn.",
            "**Income:** 5.2% dividend yield with a payout of only about 41%, which leaves room to raise "
            "dividends.",
            "**Low risk:** realised volatility of about 14%, the lowest of the six banks covered.",
            "**Support:** 16 analysts, average recommendation 1.75 (Buy), mean target SAR 25.3. A higher "
            "foreign-ownership cap would add buyers.",
        ],
        "risks": "Rate cuts squeezing lending margins; corporate loan losses if the downturn deepens; "
                 "competition for government deposits.",
    },
    "1060.SR": {
        "headline": "A bank priced below book value, with the highest yield among large banks",
        "why": [
            "**Valuation:** 0.97x book value and 8.2x earnings, the lowest price-to-book among the large "
            "banks covered.",
            "**Income:** about 6.2% dividend yield (SAR 2.0 a year), payout about 52%.",
            "**Earnings:** 9M 2026 net profit +3% to SAR 6.58bn; Q3 profit SAR 2.17bn (+1%), with operating "
            "income up about 5%.",
            "**Franchise:** strong corporate, trade-finance and wealth business with its HSBC affiliation.",
            "**Support:** 12 analysts, average recommendation 1.58 (Buy), mean target SAR 41.1.",
        ],
        "risks": "Lowest ROE of the picks (10.9%); earnings growth has slowed to low single digits; sensitive "
                 "to rate cuts.",
    },
    "7020.SR": {
        "headline": "A defensive telecom at a discount to stc, yielding 5%",
        "why": [
            "**Valuation:** 12.4x trailing earnings and 7.0x EV/EBITDA, against 14.6x and 9.5x for stc.",
            "**Earnings:** 9M 2026 net profit +7.7% to SAR 2.71bn; Q3 +1% to SAR 925m against a strong Q3 2025.",
            "**Returns and income:** 18% ROE and a SAR 3.0 dividend (about 5.1% yield).",
            "**Defensive:** telecom demand barely moves with oil; the stock is about 18% below its 52-week high.",
            "**Support:** 13 analysts, average recommendation 1.62 (Buy), mean target SAR 76.2.",
        ],
        "risks": "Q3 operating profit -3.3%; competition from stc and Zain; capex for 5G and data centres; "
                 "current ratio below 1.",
    },
    "4164.SR": {
        "headline": "High-return pharmacy leader with strong free cash flow",
        "why": [
            "**Quality:** 31% ROE and free cash flow of about SAR 0.93bn, a free-cash-flow yield of about 7.7%.",
            "**Recovery:** Q3 2026 net profit +6.6% to SAR 172m after an investment-heavy first half. Analysts "
            "expect 2027 EPS of about SAR 7.05 (+16%).",
            "**Income:** the latest semi-annual dividend of SAR 2.6 annualises to a 5.6% yield (3.3% trailing).",
            "**Structural growth:** non-cyclical consumer-health demand, plus growing clinics and online "
            "pharmacy.",
            "**Support:** 9 analysts, average recommendation 1.78 (Buy), mean target SAR 115.5.",
        ],
        "risks": "9M 2026 profit is still down 4.9% and 2026 guidance is only +1-2%; margin pressure from "
                 "expansion; online competition; drug-price regulation.",
    },
    "4002.SR": {
        "headline": "De-rated hospital operator: higher risk, highest upside of the picks",
        "why": [
            "**Valuation:** about 13x trailing earnings (after Q3) against about 29x for Al Habib, despite a "
            "22.6% ROE and modest debt (29% debt/equity).",
            "**Growth:** revenue still growing about 10%; 9M 2026 net profit SAR 600m (+2.7%). The Q3 dip "
            "(-6%) came from one-off collections in the comparison quarter.",
            "**Capacity:** the new Yanbu hospital should support margin recovery once it ramps up.",
            "**Entry point:** SAR 55.15, close to its 52-week low of 52.45 (high 74.25).",
            "**Support:** 13 analysts, average recommendation 2.23 (Buy), mean target SAR 79.4.",
        ],
        "risks": "Lower composite score than the other picks; HSBC downgraded it to Reduce in April 2026; "
                 "start-up costs at new hospitals; slow collections from government payers.",
    },
}

AVOID_NOTES = {
    "2082.SR": "63x trailing P/E, negative free cash flow, 92% debt/equity, down 31% over a year. The "
               "valuation rests on a long-dated project pipeline.",
    "1211.SR": "About 30x P/E, no dividend, and forward EPS below trailing. Its Gulf-coast export route "
               "depends on Hormuz.",
    "1111.SR": "Earnings -42% as trading volumes fell; still 41x trailing P/E.",
    "2010.SR": "Earnings distorted by one-offs (negative TTM margin, ROE 0.4%); the payout ratio above 300% "
               "is not sustainable.",
}

HOLD_NOTES = {
    "2222.SR": "Income holding: 5.2% yield and record free cash flow, but analysts see lower EPS in 2027 as "
               "oil prices settle.",
    "1120.SR": "Best-in-class bank (Q3 profit +11.7%) but priced at 3.1x book; the model sees limited upside.",
    "4013.SR": "Top-quality hospital group (18% revenue growth) but about 29x earnings; buy on dips.",
    "4190.SR": "Strong momentum and 67% ROE, but the price is already close to the analyst target.",
    "4263.SR": "Q3 profit +28% and 46% ROE; a great business at a fair price. Watch for pullbacks.",
}

CATALYSTS = [
    ("9 Nov 2026", "Q3 results due from Ma'aden, Saudi Energy and Jarir."),
    ("10 Nov 2026", "US October CPI and the EIA Short-Term Energy Outlook (oil price path)."),
    ("11 Nov 2026", "OPEC Monthly Oil Market Report."),
    ("16-17 Nov 2026", "Aramco Q3 dividend record/ex-date (SAR 0.3393 a share)."),
    ("29 Nov 2026", "OPEC+ ministerial meeting decides the 2027 production framework."),
    ("Mid-Dec 2026", "US Fed meeting; SAMA usually follows within hours."),
    ("Dec 2026", "Saudi 2027 budget approval; detail on spending priorities."),
    ("Ongoing", "US-Iran talks, Houthi blockade and Hormuz shipping; CMA decision on the foreign-ownership cap."),
]

SCENARIOS = [
    ("Bull", "A US-Iran deal reopens Hormuz and the Red Sea; Brent settles at $75-85 with full export "
             "volumes; SAMA cuts rates twice; the CMA lifts the foreign-ownership cap and foreign money flows "
             "into banks."),
    ("Base", "An uneasy stalemate: occasional attacks but no major escalation; Brent at $85-100; 2027 "
             "recovery broadly as the IMF expects; one or two rate cuts; earnings growth in the mid-single "
             "digits."),
    ("Bear", "Renewed US strikes on Iran (Eurasia Group puts the odds at 60%), Brent at $110-125 but Saudi "
             "volumes disrupted again; deeper spending cuts; foreign selling."),
]

SOURCES = [
    ("Trading Economics: TASI level and changes", "https://tradingeconomics.com/saudi-arabia/stock-market"),
    ("Argaam: TASI steepest annual decline in a decade (2025)", "https://www.argaam.com/en/article/articledetail/id/1869729"),
    ("SNB Capital 2026 TASI range (Argaam)", "https://www.argaam.com/en/article/articledetail/id/1872101"),
    ("Marmore: Saudi outlook 2026", "https://www.marmoremena.com/en/reports/macro-markets-gcc-saudi-arabia-outlook-january-2026/"),
    ("CNBC: Houthis declare maritime embargo on Saudi Arabia (20 Jul 2026)", "https://www.cnbc.com/2026/07/20/iran-houthi-yemen-saudi-arabia.html"),
    ("The National: Saudi shifts oil exports to Suez", "https://www.thenationalnews.com/business/energy/2026/07/26/saudi-arabia-shifts-to-suez-as-houthis-drive-bab-al-mandeb-oil-exports-to-near-zero/"),
    ("Al Jazeera: Saudi condemns Houthi blockade", "https://www.aljazeera.com/news/2026/7/21/saudi-condemns-houthi-blockade-how-will-the-rest-of-the-world-be-impacted"),
    ("FinanceFeeds: Brent $98.32 week ahead", "https://financefeeds.com/brent-crude-oil-price-98-32-saturday-week-ahead-us-iran-deal-bets-cpi-10-november-bull-105-bear-93/"),
    ("Vantage: Brent falls on midterms and Iran peace bets", "https://www.vantagemarkets.com/market-analysis/why-brent-crude-oil-price-fell-midterms-iran-peace-bets-ukousd-usousd-november-6-2026/"),
    ("EIA Short-Term Energy Outlook", "https://www.eia.gov/outlooks/steo/report/global_oil.php"),
    ("Arab News: 2027 budget deficit 3.6% of GDP", "https://www.arabnews.pk/business/saudi-arabia-projects-2027-budget-deficit-at-36-of-gdp-3002797"),
    ("Zawya: Saudi fiscal deficit estimate 2027", "https://www.zawya.com/en/economy/saudi-arabia-estimates-fiscal-deficit-of-3.6-of-gdp-in-2027-finance-ministry-says-1459338"),
    ("Trading Economics: SAMA interest rate", "https://tradingeconomics.com/saudi-arabia/interest-rate"),
    ("Zawya: SAMA expected to follow Fed cuts", "https://www.zawya.com/en/economy/gcc/saudi-central-bank-expected-to-toe-us-feds-possible-rate-cuts-of-100-bps-by-2026-end-report-x949op6l"),
    ("Arab News: Saudi banks Q3 profits", "https://www.arabnews.com/finance/saudi-banks-q3-profits-rise-53-as-6-lenders-earn-53bn-3007508"),
    ("Maaal: Al Rajhi Q3 2026 profit +11.7%", "https://maaal.com/en/news/details/al-rajhi-bank-q3-net-prof/"),
    ("Maaal: SNB Q3 2026 profit -0.29%", "https://maaal.com/en/news/details/snbs-q3-profit-falls-02/"),
    ("Argaam: Riyad Bank 9M 2026 results", "https://www.argaam.com/en/financial-reports/company-report/47/2026/72"),
    ("SAB: 9M 2026 net profit SAR 6.6bn", "https://www.sab.com/en/about-us/newsroom/news-year-2026/saudi-awwal-bank-reports-sar-6-6-billion-net-profit-for-the-first-nine-months-of-2026-up-3-year-on-year/"),
    ("Maaal: Mobily Q3 2026 profit", "https://maaal.com/en/news/details/mobily-q3-net-profit-rise/"),
    ("Decypha: Mobily 9M 2026", "https://www.decypha.com/en/news/details/Mobily-s-net-profits-cross-SAR-2-7bn-in-9M-26--revenues-up-5-/21581428?L=EN"),
    ("Decypha: Nahdi 9M 2026", "https://www.decypha.com/en/news/details/Nahdi-Medical-s-profits-near-SAR-623m-in-9M-26--revenues-jump-7-/21583197?L=EN"),
    ("Ajel: Mouwasat Q3 2026 profit -6%", "https://english.ajel.sa/business/o3x0al1qq"),
    ("MarketScreener: Mouwasat analyst actions", "https://uk.marketscreener.com/quote/stock/MOUWASAT-MEDICAL-SERVICES-10016654/"),
    ("QNA: Aramco Q3 2026 results and dividend", "https://qna.org.qa/en/News-Area/News/2026-11/3/aramco-reports-9-rise-in-q3-adjusted-net-income-declares-sar-821-billion-dividend"),
    ("MEED: Aramco Q3 profit despite attacks", "https://www.meed.com/aramco-q3-profit-rises-9-despite-attacks-on-facilities"),
    ("Maaal: SAL Q3 2026 profit +28%", "https://maaal.com/en/news/details/sal-q3-net-profit-rises-2/"),
    ("MEIR: Tawuniya H1 2026 profit -16%", "https://meinsurancereview.com/News/ViewNewsLetterArticle/id/96398/Type/MiddleEast/Saudi-Arabia-Tawuniya-1H-net-profit-falls-16-hit-by-higher-claims"),
    ("Franklin Templeton: Saudi opens markets to all foreigners", "https://www.franklinresources.com/articles/2026/etf/saudi-arabia-opens-markets-to-all-foreigners"),
    ("Enterprise AM: foreign cap hike could bring $4.3bn", "https://enterpriseam.com/ksa/2026/08/20/foreign-cap-hike-could-bring-usd-4-3-bn-to-tadawul/"),
    ("Yahoo Finance quotes and price history (via Firecrawl)", "https://finance.yahoo.com/quote/%5ETASI.SR/"),
]
