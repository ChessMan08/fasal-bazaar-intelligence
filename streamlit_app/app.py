import os
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import pydeck as pdk
import streamlit as st

# PAGE CONFIG
st.set_page_config(
    page_title="Fasal Bazaar Intelligence",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

# DESIGN SYSTEM - CSS
INK = "#1A2420"
MUTED = "#5C6B66"
FOREST = "#1F4E37"
FOREST_2 = "#14352A"
ACCEL = "#3F8F49"
ACCEL_LIGHT = "#E7F3E5"
AMBER = "#C97C3D"
AMBER_LIGHT = "#FBF0E4"
DANGER = "#C0463C"
DANGER_LIGHT = "#FBEAE8"
LINE = "#E4E9E5"
CARD = "#FFFFFF"
SLATE = "#3B5A72"

CUSTOM_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Fraunces:wght@600;700&display=swap');

html, body, [class*="css"], .stMarkdown, .stText {{ font-family: 'Inter', -apple-system, sans-serif; }}

.stApp {{ background: #F6F8F6; }}
#MainMenu {{visibility: hidden;}}
footer {{visibility: hidden;}}
header[data-testid="stHeader"] {{ background: transparent;}}
div[data-testid="stToolbar"] {{ display:none; }}
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
.block-container {{ padding-top: 1.6rem; padding-bottom: 3rem; max-width: 1360px; }}

/* ---------- Hero ---------- */
.hero {{
    background: linear-gradient(135deg, {FOREST} 0%, {FOREST_2} 100%);
    border-radius: 22px; padding: 2.4rem 2.8rem; margin-bottom: 1.7rem;
    color: white; position: relative; overflow: hidden;
}}
.hero::after {{
    content: ""; position: absolute; right: -70px; top: -90px; width: 320px; height: 320px;
    background: radial-gradient(circle, rgba(63,143,73,0.45), transparent 70%); border-radius: 50%;
}}
.hero-eyebrow {{ font-size: 0.76rem; letter-spacing: 0.14em; text-transform: uppercase; color: #A9D3B7; font-weight: 700; margin-bottom: 0.5rem; position:relative; }}
.hero-title {{ font-family: 'Fraunces', serif; font-size: 2.25rem; font-weight: 700; margin: 0 0 0.55rem 0; line-height: 1.15; color: white; position:relative; }}
.hero-sub {{ font-size: 1.02rem; color: #D7E6DC; max-width: 700px; line-height: 1.55; position:relative; }}
.hero-badges {{ margin-top: 1.1rem; display:flex; gap:0.5rem; flex-wrap:wrap; position:relative; }}
.hero-badge {{ background: rgba(255,255,255,0.12); border: 1px solid rgba(255,255,255,0.2); padding: 0.32rem 0.8rem; border-radius: 100px; font-size: 0.78rem; font-weight: 600; color: white; }}

/* ---------- KPI cards ---------- */
.kpi-card {{ background: {CARD}; border: 1px solid {LINE}; border-radius: 16px; padding: 1.1rem 1.25rem; box-shadow: 0 1px 3px rgba(20,30,25,0.05); height: 100%; }}
.kpi-icon {{ font-size: 1.25rem; margin-bottom: 0.45rem; }}
.kpi-label {{ font-size: 0.74rem; color: {MUTED}; font-weight: 700; text-transform: uppercase; letter-spacing: 0.04em; }}
.kpi-value {{ font-size: 1.6rem; font-weight: 800; color: {INK}; margin-top: 0.15rem; line-height:1.2; }}
.kpi-context {{ font-size: 0.8rem; margin-top: 0.35rem; font-weight: 600; color: {ACCEL}; }}

/* ---------- Section cards ----------
   Two mechanisms are used deliberately:
   1) .section-card (below) for PURE-HTML blocks built as one single, complete
      st.markdown() string (spotlight, KPI cards, route legend, differentiator
      strip) -- these never split an opening/closing tag across separate calls.
   2) Streamlit's native st.container(border=True) for anything that mixes
      styled text with a REAL widget (a chart, dataframe, selectbox...) inside
      it, styled here to look the same. Splitting a raw <div> open tag and its
      </div> close tag across separate st.markdown() calls is NOT valid --
      Streamlit renders each call as its own isolated HTML fragment, so the
      browser auto-closes the incomplete tag immediately, leaving an empty
      styled box with the real content stranded outside it. That was the
      empty-shell bug. st.container(border=True) doesn't have this problem
      because it's a real Streamlit component, not raw HTML spanning calls. */
div[data-testid="stVerticalBlockBorderWrapper"] {{
    border-radius: 16px !important; border-color: {LINE} !important; background: {CARD} !important;
}}
div[data-testid="stVerticalBlockBorderWrapper"] > div {{ border-radius: 16px !important; }}

.section-card {{ background: {CARD}; border: 1px solid {LINE}; border-radius: 16px; padding: 1.5rem 1.7rem; margin-bottom: 1.1rem; }}
.section-title {{ font-size: 1.05rem; font-weight: 800; color: {INK}; margin-bottom: 0.2rem; }}
.section-caption {{ font-size: 0.85rem; color: {MUTED}; margin-bottom: 1rem; }}

/* ---------- Spotlight callout ---------- */
.spotlight {{ background: linear-gradient(135deg, {ACCEL_LIGHT} 0%, #F3F8F2 100%); border: 1px solid #CFE6CE; border-radius: 16px; padding: 1.3rem 1.6rem; margin-bottom: 1.1rem; }}
.spotlight-tag {{ display:inline-block; background: {ACCEL}; color:white; font-size:0.7rem; font-weight:700; padding: 0.2rem 0.6rem; border-radius: 100px; letter-spacing:0.04em; text-transform:uppercase; margin-bottom:0.6rem; }}
.spotlight-route {{ font-size: 1.2rem; font-weight: 800; color: {INK}; }}
.spotlight-detail {{ font-size: 0.88rem; color: {MUTED}; margin-top: 0.3rem; line-height:1.5; }}

/* ---------- Pills / badges ---------- */
.pill {{ display:inline-block; padding: 0.15rem 0.6rem; border-radius: 100px; font-size:0.76rem; font-weight:700; }}
.pill-green {{ background: {ACCEL_LIGHT}; color: {ACCEL}; }}
.pill-amber {{ background: {AMBER_LIGHT}; color: {AMBER}; }}
.pill-slate {{ background: #E9EEF1; color: {SLATE}; }}

/* ---------- Route legend cards ---------- */
.route-card {{ border: 1px solid {LINE}; border-radius: 12px; padding: 0.7rem 0.9rem; margin-bottom: 0.55rem; background: {CARD}; }}
.route-card-top {{ display:flex; justify-content:space-between; align-items:center; }}
.route-commodity {{ font-weight: 800; font-size: 0.88rem; color: {INK}; }}
.route-path {{ font-size: 0.8rem; color: {MUTED}; margin-top: 0.25rem; }}
.dot {{ display:inline-block; width:8px; height:8px; border-radius:50%; margin-right:4px; }}
.dot-buy {{ background: {ACCEL}; }}
.dot-sell {{ background: {AMBER}; }}

/* ---------- Tabs ---------- */
.stTabs [data-baseweb="tab-list"] {{ gap: 2px; border-bottom: 1px solid {LINE}; }}
.stTabs [data-baseweb="tab"] {{ height: 44px; border-radius: 10px 10px 0 0; padding: 0 18px; font-weight: 600; color: {MUTED}; }}
.stTabs [aria-selected="true"] {{ color: {FOREST} !important; background: {ACCEL_LIGHT}; }}

/* ---------- Sidebar ---------- */
section[data-testid="stSidebar"] {{ background: #FBFCFB; border-right: 1px solid {LINE}; }}
section[data-testid="stSidebar"] .block-container {{ padding-top: 1.5rem; }}
.sidebar-brand {{ display:flex; align-items:center; gap:0.5rem; margin-bottom: 1.4rem; }}
.sidebar-brand-mark {{ width: 34px; height: 34px; border-radius: 9px; background: {FOREST}; display:flex; align-items:center; justify-content:center; font-size:1.1rem; }}
.sidebar-brand-text {{ font-weight: 800; font-size: 0.95rem; color: {INK}; line-height:1.15; }}
.sidebar-section-label {{ font-size: 0.72rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.06em; color: {MUTED}; margin: 1.1rem 0 0.5rem 0; }}

/* ---------- Dataframe ---------- */
[data-testid="stDataFrame"] {{ border-radius: 12px; overflow: hidden; border: 1px solid {LINE}; }}

/* ---------- Footer ---------- */
.app-footer {{ margin-top: 2rem; padding-top: 1.3rem; border-top: 1px solid {LINE}; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.8rem; }}
.footer-badges {{ display:flex; gap:0.4rem; flex-wrap:wrap; }}
.footer-badge {{ background: white; border:1px solid {LINE}; color: {MUTED}; font-size:0.72rem; font-weight:600; padding: 0.25rem 0.65rem; border-radius: 100px; }}
.footer-note {{ font-size: 0.78rem; color: {MUTED}; }}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def p(text, size="0.87rem", color=MUTED, weight=400, margin="0.2rem 0 0 0", line_height="1.6"):
    """Explicit-colored paragraph. Use this instead of st.markdown/st.caption for
    any body text that sits inside a custom card — see the theme-independence
    note in the CSS block above for why."""
    return f'<p style="font-size:{size}; color:{color}; font-weight:{weight}; margin:{margin}; line-height:{line_height};">{text}</p>'


def h(text, size="0.92rem", color=INK, weight=800, margin="0 0 0.3rem 0"):
    return f'<div style="font-size:{size}; color:{color}; font-weight:{weight}; margin:{margin};">{text}</div>'


PLOTLY_LAYOUT = dict(
    font=dict(family="Inter, sans-serif", color=INK, size=12),
    colorway=[ACCEL, AMBER, SLATE, "#8A8A8A", DANGER],
    plot_bgcolor="white",
    paper_bgcolor="white",

    xaxis=dict(gridcolor="#EEF1EF", zeroline=False, linecolor=LINE, automargin=True),
    yaxis=dict(gridcolor="#EEF1EF", zeroline=False, linecolor=LINE, automargin=True),
    legend=dict(bgcolor="rgba(0,0,0,0)"),
    margin=dict(t=30, b=40, l=20, r=30),
)


def style_fig(fig, height=380, **layout_overrides):
    layout = dict(PLOTLY_LAYOUT)
    layout["height"] = height

    for axis_key in ("xaxis", "yaxis"):
        if axis_key in layout_overrides:
            merged_axis = dict(layout.get(axis_key, {}))
            merged_axis.update(layout_overrides.pop(axis_key))
            layout[axis_key] = merged_axis
    layout.update(layout_overrides)
    fig.update_layout(**layout)
    return fig


def plot(fig, **kwargs):
    st.plotly_chart(fig, use_container_width=True, theme=None, **kwargs)


# HELPERS
def format_inr(n):
    try:
        n = float(n)
    except (TypeError, ValueError):
        return "\u2014"
    sign = "-" if n < 0 else ""
    n = abs(int(round(n)))
    s = str(n)
    if len(s) <= 3:
        formatted = s
    else:
        last3, rest = s[-3:], s[:-3]
        parts = []
        while len(rest) > 2:
            parts.insert(0, rest[-2:])
            rest = rest[:-2]
        if rest:
            parts.insert(0, rest)
        formatted = ",".join(parts) + "," + last3
    return f"{sign}\u20b9{formatted}"


def format_compact_inr(n):
    n = float(n)
    if abs(n) >= 1e7:
        return f"\u20b9{n/1e7:.2f} Cr"
    if abs(n) >= 1e5:
        return f"\u20b9{n/1e5:.2f} L"
    return format_inr(n)


def format_seconds(s):
    s = float(s)
    if s >= 60:
        m, sec = divmod(s, 60)
        return f"{int(m)}m {sec:.0f}s"
    return f"{s:.1f}s"


def dataframe_height(n_rows, row_px=35, header_px=38, max_px=460, min_px=110):
    return int(min(max_px, max(min_px, header_px + row_px * n_rows + 3)))


STATE_CAPITALS = {
    "Punjab": (30.73, 76.78), "Haryana": (29.06, 76.09), "Uttar Pradesh": (26.85, 80.95),
    "Madhya Pradesh": (23.26, 77.41), "Maharashtra": (19.08, 72.88), "Rajasthan": (26.91, 75.79),
    "Gujarat": (23.02, 72.57), "Bihar": (25.59, 85.14), "West Bengal": (22.57, 88.36),
    "Karnataka": (12.97, 77.59),
}
COMMODITIES = {"Wheat": 2200, "Onion": 1500, "Potato": 1200, "Rice": 2800,
               "Tomato": 1800, "Soybean": 4200, "Maize": 1900, "Mustard": 5200}


@st.cache_data
def generate_demo_opportunities(seed=7):
    rng = np.random.default_rng(seed)
    states = list(STATE_CAPITALS.keys())
    rows = []
    for c in COMMODITIES:
        buy_state, sell_state = rng.choice(states, size=2, replace=False)
        blat, blon = STATE_CAPITALS[buy_state]
        slat, slon = STATE_CAPITALS[sell_state]
        buy_price = rng.uniform(1000, 4000)
        margin_pct = rng.uniform(3, 25)
        sell_price = buy_price * (1 + margin_pct / 100 + rng.uniform(0.01, 0.05))
        dist = rng.uniform(80, 1400)
        transport = dist * 0.28
        net_gain = sell_price - buy_price - transport
        rows.append({
            "Commodity": c,
            "Buy_Market": f"{buy_state}_Market_{rng.integers(0,25)}", "Buy_State": buy_state,
            "Buy_Price": round(buy_price, 2), "Buy_Lat": blat + rng.normal(0, 0.8), "Buy_Lon": blon + rng.normal(0, 0.8),
            "Sell_Market": f"{sell_state}_Market_{rng.integers(0,25)}", "Sell_State": sell_state,
            "Sell_Price": round(sell_price, 2), "Sell_Lat": slat + rng.normal(0, 0.8), "Sell_Lon": slon + rng.normal(0, 0.8),
            "Distance_km": round(dist, 1), "Transport_Cost_Per_Quintal": round(transport, 2),
            "Net_Gain_Per_Quintal": round(net_gain, 2), "Net_Margin_Pct": round(net_gain / buy_price * 100, 2),
            "Persistence_Days": int(rng.integers(0, 4)), "Est_Profit_Per_Truckload": round(net_gain * 100, 0),
        })
    return pd.DataFrame(rows)


@st.cache_data
def generate_demo_benchmark():
    scales = [100_000, 500_000, 1_000_000, 2_000_000, 5_000_000, 10_000_000]
    cpu_clean = np.array([0.5, 2.8, 6.5, 15.0, 46.0, 115.0])
    cpu_analyze = np.array([1.3, 6.7, 14.5, 33.0, 94.0, 225.0])
    gpu_clean = np.array([0.15, 0.25, 0.40, 0.70, 1.40, 2.60])
    gpu_analyze = np.array([0.45, 0.85, 1.50, 2.70, 5.70, 10.60])
    cpu = pd.DataFrame({"n_rows": scales, "clean_seconds": cpu_clean, "analyze_seconds": cpu_analyze,
                         "seconds": cpu_clean + cpu_analyze})
    gpu = pd.DataFrame({"n_rows": scales, "clean_seconds": gpu_clean, "analyze_seconds": gpu_analyze,
                         "seconds": gpu_clean + gpu_analyze})
    return cpu, gpu


@st.cache_data
def generate_demo_dataproc_benchmark():
    return pd.DataFrame({"Stage": ["Full ETL job (clean + analyze)"], "CPU_Seconds": [612.0], "GPU_Seconds": [47.5]})


@st.cache_data
def generate_demo_clusters(seed=11):
    rng = np.random.default_rng(seed)
    n = 300
    cluster = rng.integers(0, 4, size=n)
    base_price = np.array([1500, 2800, 4200, 2000])[cluster]
    base_vol = np.array([80, 400, 150, 900])[cluster]
    return pd.DataFrame({
        "Market": [f"Market_{i}" for i in range(n)],
        "Commodity": rng.choice(list(COMMODITIES.keys())[:5], size=n),
        "mean_price": base_price + rng.normal(0, 150, n),
        "volatility": np.clip(base_vol + rng.normal(0, 60, n), 10, None),
        "mean_deviation": rng.normal(0, 6, n),
        "risk_cluster": cluster,
    })


@st.cache_data
def generate_demo_price_history(seed=21):
    rng = np.random.default_rng(seed)
    dates = pd.date_range(end=pd.Timestamp.today(), periods=90, freq="D")
    t = np.arange(len(dates))
    frames = []
    for commodity, base in COMMODITIES.items():
        for m in range(4):
            market = f"{commodity[:4]}_Market_{m}"
            walk = np.cumsum(rng.normal(0, base * 0.005, size=len(dates)))
            season = np.sin(t / len(dates) * 3 * np.pi + m) * base * 0.025
            noise = rng.normal(0, base * 0.008, size=len(dates))
            price = base + walk + season + noise
            roll_mean = pd.Series(price).rolling(7, min_periods=1).mean().values
            frames.append(pd.DataFrame({
                "Commodity": commodity, "Market": market, "Arrival_Date": dates,
                "Modal_Price": price, "Rolling_Mean_7d": roll_mean,
            }))
    return pd.concat(frames, ignore_index=True)


@st.cache_data
def generate_demo_forecast(seed=31):
    rng = np.random.default_rng(seed)
    rows = []
    for commodity in COMMODITIES:
        pred_change = rng.normal(0, 3.5)
        rows.append({"Commodity": commodity, "Predicted_Change_Pct": round(pred_change, 2),
                     "Confidence": round(rng.uniform(0.62, 0.91), 2)})
    importances = {"Rolling_Mean_7d": 0.42, "Lag_1": 0.24, "Deviation_Pct": 0.14,
                   "Z_Score": 0.11, "Lag_2": 0.06, "Modal_Price": 0.03}
    return pd.DataFrame(rows), pd.DataFrame({"Feature": list(importances.keys()), "Importance": list(importances.values())})


@st.cache_data
def load_data():
    paths = {k: os.path.join(DATA_DIR, v) for k, v in {
        "opp": "top_opportunities.csv", "cluster": "risk_clusters.csv",
        "cpu": "bench_cpu.csv", "gpu": "bench_gpu.csv",
        "history": "full_analyzed_data.parquet", "forecast": "forecast.csv",
        "importance": "forecast_feature_importance.csv", "dataproc": "dataproc_benchmark.csv",
    }.items()}

    using_demo = not os.path.exists(paths["opp"])

    opportunities = pd.read_csv(paths["opp"]) if os.path.exists(paths["opp"]) else generate_demo_opportunities()
    clusters = pd.read_csv(paths["cluster"]) if os.path.exists(paths["cluster"]) else generate_demo_clusters()

    if os.path.exists(paths["cpu"]) and os.path.exists(paths["gpu"]):
        cpu_bench, gpu_bench = pd.read_csv(paths["cpu"]), pd.read_csv(paths["gpu"])
    else:
        cpu_bench, gpu_bench = generate_demo_benchmark()

    if os.path.exists(paths["history"]):
        history = pd.read_parquet(paths["history"], columns=["Commodity", "Market", "Arrival_Date", "Modal_Price", "Rolling_Mean_7d"])
    else:
        history = generate_demo_price_history()

    if os.path.exists(paths["forecast"]) and os.path.exists(paths["importance"]):
        forecast, importance = pd.read_csv(paths["forecast"]), pd.read_csv(paths["importance"])
    else:
        forecast, importance = generate_demo_forecast()

    dataproc_bench = pd.read_csv(paths["dataproc"]) if os.path.exists(paths["dataproc"]) else generate_demo_dataproc_benchmark()

    return opportunities, clusters, cpu_bench, gpu_bench, history, forecast, importance, dataproc_bench, using_demo


(opportunities, clusters, cpu_bench, gpu_bench, price_history,
 forecast, feature_importance, dataproc_bench, using_demo) = load_data()

# SIDEBAR
with st.sidebar:
    st.markdown(
        '<div class="sidebar-brand"><div class="sidebar-brand-mark">🌾</div>'
        '<div class="sidebar-brand-text">Fasal Bazaar<br/>Intelligence</div></div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="sidebar-section-label">Filters</div>', unsafe_allow_html=True)
    all_commodities = sorted(opportunities["Commodity"].unique())
    selected_commodities = st.multiselect("Commodity", all_commodities, default=all_commodities)
    min_margin = st.slider("Minimum net margin (%)", 0.0, float(max(opportunities["Net_Margin_Pct"].max(), 5)), 3.0)
    min_persistence = st.slider("Minimum persistence (days)", 0, 3, 0)

    st.markdown('<div class="sidebar-section-label">About the ranking</div>', unsafe_allow_html=True)
    st.markdown(p(
        "Net margin already has estimated trucking cost (\u20b90.28/km/quintal) and a minimum "
        "profit margin subtracted \u2014 this is not a raw price-gap flag.",
        size="0.8rem", color=MUTED,
    ), unsafe_allow_html=True)

    if using_demo:
        st.markdown('<div class="sidebar-section-label">Data source</div>', unsafe_allow_html=True)
        st.info("Demo data. Drop real pipeline outputs into `data/` to replace it.", icon="\U0001F4C1")

filtered = opportunities[
    (opportunities["Commodity"].isin(selected_commodities))
    & (opportunities["Net_Margin_Pct"] >= min_margin)
    & (opportunities["Persistence_Days"] >= min_persistence)
].sort_values("Net_Margin_Pct", ascending=False)

# HERO HEADER
gpu_speedup = (cpu_bench["seconds"].iloc[-1] / gpu_bench["seconds"].iloc[-1]) if len(cpu_bench) and len(gpu_bench) else None
st.markdown(
    f"""
    <div class="hero">
        <div class="hero-eyebrow">GPU-Accelerated Decision Intelligence</div>
        <div class="hero-title">Fasal Bazaar Intelligence</div>
        <div class="hero-sub">Where should procurement send trucks today? Ranked, transport-cost-net
        arbitrage opportunities across India's Agmarknet mandi network \u2014 refreshed fast enough to
        act on before the opportunity closes.</div>
        <div class="hero-badges">
            <div class="hero-badge">\U0001F4E1 {len(opportunities)} commodities tracked</div>
            <div class="hero-badge">\u26A1 {gpu_speedup:.1f}x measured GPU speedup</div>
            <div class="hero-badge">\U0001F69A Transport-cost-aware ranking</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

if using_demo:
    st.info(
        "You're viewing **demo data**. Run the pipeline notebook and drop `top_opportunities.csv`, "
        "`risk_clusters.csv`, `bench_cpu.csv`, `bench_gpu.csv`, and optionally `full_analyzed_data.parquet` "
        "into `./data/` to see your real results.",
        icon="\u2139\ufe0f",
    )

# KPI ROW
k1, k2, k3, k4, k5 = st.columns(5)
kpis = [
    (k1, "\U0001F3AF", "Opportunities found", str(len(filtered)), None),
    (k2, "\U0001F4B0", "Est. profit, top routes", format_compact_inr(filtered["Est_Profit_Per_Truckload"].sum()), "per truckload, summed"),
    (k3, "\U0001F4C8", "Avg net margin", f"{filtered['Net_Margin_Pct'].mean():.1f}%" if len(filtered) else "\u2014", "after transport cost"),
    (k4, "\U0001F33E", "Commodities covered", str(filtered["Commodity"].nunique()), None),
    (k5, "\u26A1", "GPU acceleration", f"{gpu_speedup:.1f}x" if gpu_speedup else "\u2014", "at largest scale tested"),
]
for col, icon, label, value, ctx in kpis:
    with col:
        ctx_html = f'<div class="kpi-context">{ctx}</div>' if ctx else ""
        st.markdown(
            f'<div class="kpi-card"><div class="kpi-icon">{icon}</div>'
            f'<div class="kpi-label">{label}</div><div class="kpi-value">{value}</div>{ctx_html}</div>',
            unsafe_allow_html=True,
        )

st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)

# TABS
tab_overview, tab_opps, tab_map, tab_trends, tab_bench, tab_clusters, tab_method = st.tabs(
    ["\U0001F4CA Overview", "\U0001F4CB Opportunities", "\U0001F5FA\ufe0f Route Map",
     "\U0001F4C9 Trends & Forecast", "\u26A1 Acceleration Proof", "\U0001F9E9 Risk Clusters", "\U0001F4D6 Methodology"]
)

# OVERVIEW
with tab_overview:
    if len(filtered):
        top = filtered.iloc[0]
        st.markdown(
            f"""
            <div class="spotlight">
                <div class="spotlight-tag">Top opportunity today</div>
                <div class="spotlight-route">{top['Commodity']}: {top['Buy_Market']} \u2192 {top['Sell_Market']}</div>
                <div class="spotlight-detail">Buy at \u20b9{top['Buy_Price']:.0f}/quintal in {top['Buy_State']},
                sell into {top['Sell_State']} at \u20b9{top['Sell_Price']:.0f}/quintal \u2014
                {top['Distance_km']:.0f} km apart, \u20b9{top['Transport_Cost_Per_Quintal']:.0f}/quintal trucking cost netted out.
                Net margin <b>{top['Net_Margin_Pct']:.1f}%</b>, est. profit <b>{format_inr(top['Est_Profit_Per_Truckload'])}</b> per truckload.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    c1, c2 = st.columns([3, 2])
    with c1:
        with st.container(border=True):
            st.markdown(h("Opportunities by commodity") + p("Estimated profit per truckload, top routes only"), unsafe_allow_html=True)
            if len(filtered):
                by_commodity = filtered.groupby("Commodity")["Est_Profit_Per_Truckload"].sum().sort_values(ascending=True)
                fig = go.Figure(go.Bar(
                    x=by_commodity.values, y=by_commodity.index, orientation="h",
                    marker_color=ACCEL, text=[format_compact_inr(v) for v in by_commodity.values],
                    textposition="outside", cliponaxis=False,
                ))
                style_fig(fig, height=320, xaxis_title="Estimated profit (\u20b9)", yaxis_title=None,
                          xaxis=dict(range=[0, by_commodity.max() * 1.18]))
                plot(fig)
            else:
                st.markdown(p("No opportunities match the current filters."), unsafe_allow_html=True)

    with c2:
        with st.container(border=True):
            st.markdown(h("Margin distribution") + p("Net margin across all tracked routes"), unsafe_allow_html=True)
            fig = go.Figure(go.Histogram(x=opportunities["Net_Margin_Pct"], marker_color=AMBER, nbinsx=12))
            style_fig(fig, height=320, xaxis_title="Net margin (%)", yaxis_title="Routes")
            plot(fig)

    diff_items = [
        ("\U0001F69A", "Transport-cost-net", "Every gap has haversine-distance freight cost subtracted before it counts as an opportunity."),
        ("\U0001F4C5", "Persistence-filtered", "Requires the gap to hold for multiple days, filtering out one-day noise."),
        ("\u26A1", "GPU-accelerated at scale", "Same pipeline benchmarked CPU vs GPU across multiple data sizes, not one cherry-picked number."),
    ]
    diff_cells = "".join(
        f'<div>{h(f"{icon} {title}", size="0.88rem")}{p(body)}</div>' for icon, title, body in diff_items
    )
    st.markdown(
        f'<div class="section-card">{h("How this differs from a naive price-gap tool")}'
        f'<div style="display:grid; grid-template-columns:repeat(3,1fr); gap:1.4rem; margin-top:0.6rem;">'
        f'{diff_cells}</div></div>',
        unsafe_allow_html=True,
    )

# OPPORTUNITIES
with tab_opps:
    with st.container(border=True):
        st.markdown(h("Ranked procurement opportunities") +
                    p("Sorted by net margin \u2014 already accounts for trucking cost and minimum margin"),
                    unsafe_allow_html=True)
        display_cols = [
            "Commodity", "Buy_Market", "Buy_State", "Buy_Price",
            "Sell_Market", "Sell_State", "Sell_Price", "Distance_km",
            "Transport_Cost_Per_Quintal", "Net_Gain_Per_Quintal", "Net_Margin_Pct",
            "Persistence_Days", "Est_Profit_Per_Truckload",
        ]
        if len(filtered):
            styled = filtered[display_cols].style.background_gradient(
                subset=["Net_Margin_Pct"], cmap="Greens"
            ).format({
                "Buy_Price": "\u20b9{:.0f}", "Sell_Price": "\u20b9{:.0f}", "Distance_km": "{:.0f} km",
                "Transport_Cost_Per_Quintal": "\u20b9{:.0f}", "Net_Gain_Per_Quintal": "\u20b9{:.0f}",
                "Net_Margin_Pct": "{:.1f}%", "Est_Profit_Per_Truckload": "\u20b9{:,.0f}",
            })
            st.dataframe(styled, use_container_width=True, height=dataframe_height(len(filtered)))
        else:
            st.warning("No opportunities match the current filters. Try lowering the minimum margin in the sidebar.")
        st.markdown(p(
            "Buy = where to send the procurement fleet. Sell = the destination market absorbing the surplus. "
            "Persistence = how many of the last 3 days this gap held, filtering out one-day noise.",
            size="0.8rem",
        ), unsafe_allow_html=True)

    if len(filtered):
        csv = filtered[display_cols].to_csv(index=False).encode("utf-8")
        st.download_button("\u2B07\ufe0f Download filtered results as CSV", csv, "opportunities.csv", "text/csv")

# ROUTE MAP
with tab_map:
    map_col, legend_col = st.columns([5, 3])
    with map_col:
        with st.container(border=True):
            st.markdown(h("Procurement routes") + p("Green = buy market \u00b7 amber = sell destination \u00b7 arc thickness = net margin"),
                        unsafe_allow_html=True)
            if len(filtered):
                arc_data = filtered.copy()
                max_margin = max(arc_data["Net_Margin_Pct"].max(), 1)
                arc_data["width"] = 2 + (arc_data["Net_Margin_Pct"] / max_margin) * 8

                arc_layer = pdk.Layer(
                    "ArcLayer", data=arc_data,
                    get_source_position=["Buy_Lon", "Buy_Lat"], get_target_position=["Sell_Lon", "Sell_Lat"],
                    get_source_color=[63, 143, 73, 210], get_target_color=[201, 124, 61, 210],
                    get_width="width", pickable=True,
                )
                buy_points = pdk.Layer(
                    "ScatterplotLayer", data=arc_data, get_position=["Buy_Lon", "Buy_Lat"],
                    get_fill_color=[63, 143, 73, 230], get_radius=16000, get_line_color=[255, 255, 255],
                    get_line_width=400, stroked=True, pickable=True,
                )
                sell_points = pdk.Layer(
                    "ScatterplotLayer", data=arc_data, get_position=["Sell_Lon", "Sell_Lat"],
                    get_fill_color=[201, 124, 61, 230], get_radius=16000, get_line_color=[255, 255, 255],
                    get_line_width=400, stroked=True, pickable=True,
                )
                view_state = pdk.ViewState(latitude=22.5, longitude=79.0, zoom=3.9, pitch=25)
                
                st.pydeck_chart(pdk.Deck(
                    layers=[arc_layer, buy_points, sell_points], initial_view_state=view_state,
                    map_provider="carto", map_style="light",
                    tooltip={
                        "html": "<b>{Commodity}</b><br/>{Buy_Market} \u2192 {Sell_Market}<br/>Net margin: {Net_Margin_Pct}%",
                        "style": {"backgroundColor": "#1A2420", "color": "white", "fontSize": "0.8rem"},
                    },
                ), use_container_width=True)
            else:
                st.markdown(p("No opportunities match the current filters."), unsafe_allow_html=True)

    with legend_col:
        if len(filtered):
            cards = []
            for _, r in filtered.iterrows():
                pill_class = "pill-green" if r["Net_Margin_Pct"] >= 10 else "pill-amber"
                cards.append(
                    f'<div class="route-card">'
                    f'<div class="route-card-top"><div class="route-commodity">{r["Commodity"]}</div>'
                    f'<div class="pill {pill_class}">{r["Net_Margin_Pct"]:.1f}%</div></div>'
                    f'<div class="route-path"><span class="dot dot-buy"></span>{r["Buy_Market"]}'
                    f'&nbsp;\u2192&nbsp; <span class="dot dot-sell"></span>{r["Sell_Market"]}</div>'
                    f'<div class="route-path">{r["Distance_km"]:.0f} km \u00b7 est. profit '
                    f'{format_compact_inr(r["Est_Profit_Per_Truckload"])}</div></div>'
                )
            cards_html = "".join(cards)
        else:
            cards_html = p("No routes to show.")
        st.markdown(
            f'<div class="section-card" style="max-height:560px; overflow-y:auto;">'
            f'{h("Routes at a glance")}{p("Ranked by net margin")}{cards_html}</div>',
            unsafe_allow_html=True,
        )

# TRENDS & FORECAST
with tab_trends:
    c1, c2 = st.columns([2, 1])
    with c1:
        with st.container(border=True):
            st.markdown(h("Price trend") + p("Modal price vs 7-row rolling mean \u2014 pick a single market for the cleanest signal, "
                                              "or \u201cAll markets\u201d for a state-wide average with the market spread shaded"),
                        unsafe_allow_html=True)

            col_a, col_b = st.columns(2)
            with col_a:
                trend_commodities = sorted(price_history["Commodity"].unique())
                sel_commodity = st.selectbox("Commodity", trend_commodities, key="trend_commodity")
            commodity_hist = price_history[price_history["Commodity"] == sel_commodity]
            with col_b:
                market_options = ["All markets (average)"] + sorted(commodity_hist["Market"].unique())
                sel_market = st.selectbox("Market", market_options, key="trend_market")

            if sel_market == "All markets (average)":
                agg = (
                    commodity_hist.groupby("Arrival_Date")
                    .agg(Modal_Price=("Modal_Price", "mean"), Rolling_Mean_7d=("Rolling_Mean_7d", "mean"),
                         Price_Min=("Modal_Price", "min"), Price_Max=("Modal_Price", "max"))
                    .reset_index().sort_values("Arrival_Date")
                )
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=agg["Arrival_Date"], y=agg["Price_Max"], mode="lines",
                                          line=dict(width=0), showlegend=False, hoverinfo="skip"))
                fig.add_trace(go.Scatter(x=agg["Arrival_Date"], y=agg["Price_Min"], mode="lines",
                                          line=dict(width=0), fill="tonexty", fillcolor="rgba(63,143,73,0.12)",
                                          name="Market spread", hoverinfo="skip"))
                fig.add_trace(go.Scatter(x=agg["Arrival_Date"], y=agg["Modal_Price"], mode="lines",
                                          name="Average modal price", line=dict(color="#8A8A8A", width=1.8)))
                fig.add_trace(go.Scatter(x=agg["Arrival_Date"], y=agg["Rolling_Mean_7d"], mode="lines",
                                          name="7-row rolling mean", line=dict(color=ACCEL, width=2.8)))
            else:
                series = commodity_hist[commodity_hist["Market"] == sel_market].sort_values("Arrival_Date")
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=series["Arrival_Date"], y=series["Modal_Price"], mode="lines",
                                          name="Modal price", line=dict(color="#8A8A8A", width=1.6)))
                fig.add_trace(go.Scatter(x=series["Arrival_Date"], y=series["Rolling_Mean_7d"], mode="lines",
                                          name="7-row rolling mean", line=dict(color=ACCEL, width=2.8)))

            style_fig(fig, height=380, yaxis_title="\u20b9/quintal", legend=dict(orientation="h", y=1.12, bgcolor="rgba(0,0,0,0)"))
            plot(fig)

    with c2:
        with st.container(border=True):
            st.markdown(h("Next-day forecast") + p("GPU XGBoost prediction"), unsafe_allow_html=True)
            f_row = forecast[forecast["Commodity"] == sel_commodity]
            if len(f_row):
                f_row = f_row.iloc[0]
                change = f_row["Predicted_Change_Pct"]
                pill_class = "pill-green" if change >= 0 else "pill-amber"
                arrow = "\u2191" if change >= 0 else "\u2193"
                confidence_pct = f_row["Confidence"] * 100
                st.markdown(
                    f'<div style="text-align:center; padding: 0.6rem 0 1rem 0;">'
                    f'<div style="font-size:2.1rem; font-weight:800; color:{INK};">{arrow} {abs(change):.1f}%</div>'
                    f'<div class="pill {pill_class}">predicted next-day change</div>'
                    f'{p(f"Model confidence: <b>{confidence_pct:.0f}%</b>", margin="0.8rem 0 0 0")}'
                    f'</div>', unsafe_allow_html=True,
                )
            else:
                st.markdown(p("No forecast available for this commodity yet."), unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown(h("What drives the forecast") + p("XGBoost feature importance"), unsafe_allow_html=True)
            fi = feature_importance.sort_values("Importance", ascending=True)
            fig = go.Figure(go.Bar(x=fi["Importance"], y=fi["Feature"], orientation="h", marker_color=SLATE))
            style_fig(fig, height=230, xaxis_title=None, yaxis_title=None)
            plot(fig)

# ACCELERATION
with tab_bench:
    max_scale_cpu = cpu_bench["seconds"].iloc[-1]
    max_scale_gpu = gpu_bench["seconds"].iloc[-1]
    max_speedup = max_scale_cpu / max_scale_gpu
    avg_speedup = (cpu_bench["seconds"] / gpu_bench["seconds"]).mean()
    gpu_throughput = gpu_bench["n_rows"].iloc[-1] / max_scale_gpu
    cpu_throughput = cpu_bench["n_rows"].iloc[-1] / max_scale_cpu
    time_saved = max_scale_cpu - max_scale_gpu

    a1, a2, a3, a4 = st.columns(4)
    for col, icon, label, value, ctx in [
        (a1, "\U0001F680", "Max speedup", f"{max_speedup:.1f}x", f"at {cpu_bench['n_rows'].iloc[-1]:,} rows"),
        (a2, "\U0001F4CA", "Avg speedup", f"{avg_speedup:.1f}x", "across all scales tested"),
        (a3, "\u23F1\ufe0f", "Time saved", format_seconds(time_saved), "at largest scale"),
        (a4, "\U0001F4E6", "GPU throughput", f"{gpu_throughput:,.0f} rows/s", f"vs {cpu_throughput:,.0f} rows/s on CPU"),
    ]:
        with col:
            st.markdown(
                f'<div class="kpi-card"><div class="kpi-icon">{icon}</div>'
                f'<div class="kpi-label">{label}</div><div class="kpi-value">{value}</div>'
                f'<div class="kpi-context">{ctx}</div></div>', unsafe_allow_html=True,
            )
    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    r1c1, r1c2 = st.columns(2)
    with r1c1:
        with st.container(border=True):
            st.markdown(h("Runtime vs scale") + p("Same pipeline, same code \u2014 only the runtime differs"), unsafe_allow_html=True)
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=cpu_bench["n_rows"], y=cpu_bench["seconds"], mode="lines+markers",
                                      name="CPU (pandas)", line=dict(color="#8A8A8A", width=2.5)))
            fig.add_trace(go.Scatter(x=gpu_bench["n_rows"], y=gpu_bench["seconds"], mode="lines+markers",
                                      name="GPU (cudf.pandas)", line=dict(color=ACCEL, width=2.5)))
            fig.update_xaxes(type="log", title="Dataset size (rows)")
            style_fig(fig, height=340, yaxis_title="Runtime (seconds)", legend=dict(orientation="h", y=1.12, bgcolor="rgba(0,0,0,0)"))
            plot(fig)

    with r1c2:
        with st.container(border=True):
            st.markdown(h("Speedup factor by scale") + p("How much the GPU advantage grows as data size increases"), unsafe_allow_html=True)
            speedup_by_scale = cpu_bench["seconds"] / gpu_bench["seconds"]
            fig = go.Figure(go.Bar(x=cpu_bench["n_rows"].astype(str), y=speedup_by_scale, marker_color=ACCEL,
                                    text=[f"{v:.1f}x" for v in speedup_by_scale], textposition="outside", cliponaxis=False))
            style_fig(fig, height=340, xaxis_title="Dataset size (rows)", yaxis_title="Speedup (x)",
                      yaxis=dict(range=[0, speedup_by_scale.max() * 1.2]))
            plot(fig)

    r2c1, r2c2 = st.columns(2)
    with r2c1:
        with st.container(border=True):
            st.markdown(h("Stage breakdown at largest scale") + p("Where the time actually goes: cleaning vs analysis"), unsafe_allow_html=True)
            if "clean_seconds" in cpu_bench.columns and "clean_seconds" in gpu_bench.columns:
                stages = ["Clean", "Analyze"]
                cpu_vals = [cpu_bench["clean_seconds"].iloc[-1], cpu_bench["analyze_seconds"].iloc[-1]]
                gpu_vals = [gpu_bench["clean_seconds"].iloc[-1], gpu_bench["analyze_seconds"].iloc[-1]]
                fig = go.Figure()
                fig.add_trace(go.Bar(x=stages, y=cpu_vals, name="CPU", marker_color="#8A8A8A"))
                fig.add_trace(go.Bar(x=stages, y=gpu_vals, name="GPU", marker_color=ACCEL))
                style_fig(fig, height=320, yaxis_title="Seconds", barmode="group",
                          legend=dict(orientation="h", y=1.12, bgcolor="rgba(0,0,0,0)"))
                plot(fig)
            else:
                st.markdown(p("Stage-level timing not found in bench_cpu.csv / bench_gpu.csv \u2014 re-run the notebook's "
                               "Step 8 (updated to export clean_seconds/analyze_seconds) to unlock this chart."),
                            unsafe_allow_html=True)

    with r2c2:
        with st.container(border=True):
            st.markdown(h("Throughput vs scale") + p("Rows processed per second \u2014 CPU degrades, GPU stays efficient"), unsafe_allow_html=True)
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=cpu_bench["n_rows"], y=cpu_bench["n_rows"] / cpu_bench["seconds"],
                                      mode="lines+markers", name="CPU", line=dict(color="#8A8A8A", width=2.5)))
            fig.add_trace(go.Scatter(x=gpu_bench["n_rows"], y=gpu_bench["n_rows"] / gpu_bench["seconds"],
                                      mode="lines+markers", name="GPU", line=dict(color=ACCEL, width=2.5)))
            fig.update_xaxes(type="log", title="Dataset size (rows)")
            fig.update_yaxes(type="log", title="Rows / second")
            style_fig(fig, height=320, legend=dict(orientation="h", y=1.12, bgcolor="rgba(0,0,0,0)"))
            plot(fig)

    with st.container(border=True):
        st.markdown(h("Distributed batch layer \u2014 Dataproc Serverless") +
                    p("A second, independent acceleration proof: the same clean+analyze logic as a Spark job, "
                      "CPU tier vs RAPIDS-accelerated GPU tier, on the full historical dataset"),
                    unsafe_allow_html=True)
        dp = dataproc_bench.iloc[0]
        dp_speedup = dp["CPU_Seconds"] / dp["GPU_Seconds"]
        d1, d2, d3 = st.columns(3)
        with d1:
            st.markdown(f'<div class="kpi-card"><div class="kpi-icon">\U0001F40C</div><div class="kpi-label">CPU tier</div>'
                        f'<div class="kpi-value">{format_seconds(dp["CPU_Seconds"])}</div></div>', unsafe_allow_html=True)
        with d2:
            st.markdown(f'<div class="kpi-card"><div class="kpi-icon">\u26A1</div><div class="kpi-label">GPU tier (RAPIDS)</div>'
                        f'<div class="kpi-value">{format_seconds(dp["GPU_Seconds"])}</div></div>', unsafe_allow_html=True)
        with d3:
            st.markdown(f'<div class="kpi-card"><div class="kpi-icon">\U0001F680</div><div class="kpi-label">Speedup</div>'
                        f'<div class="kpi-value">{dp_speedup:.1f}x</div></div>', unsafe_allow_html=True)
        if using_demo:
            st.markdown(p("Demo numbers. Drop a real <code>dataproc_benchmark.csv</code> (columns: Stage, CPU_Seconds, "
                           "GPU_Seconds) into <code>data/</code> after running <code>dataproc_job/submit_cpu_job.sh</code> "
                           "and <code>submit_gpu_job.sh</code>.", size="0.8rem", margin="0.6rem 0 0 0"), unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown(h("Full benchmark table"), unsafe_allow_html=True)
        merged = cpu_bench.merge(gpu_bench, on="n_rows", suffixes=("_cpu", "_gpu"))
        merged["speedup"] = (merged["seconds_cpu"] / merged["seconds_gpu"]).round(1)
        show_cols = {"n_rows": "Rows", "seconds_cpu": "CPU (s)", "seconds_gpu": "GPU (s)", "speedup": "Speedup"}
        st.dataframe(merged.rename(columns=show_cols)[list(show_cols.values())],
                     use_container_width=True, height=dataframe_height(len(merged)))
        if using_demo:
            st.markdown(p("Demo numbers. Replace ./data/bench_cpu.csv and bench_gpu.csv with your real measured benchmark.",
                           size="0.8rem"), unsafe_allow_html=True)

# RISK CLUSTERS
with tab_clusters:
    with st.container(border=True):
        st.markdown(h("Commodity-market risk clusters") +
                    p("cuML / scikit-learn KMeans on price level, volatility, and mean state deviation"),
                    unsafe_allow_html=True)
        fig = go.Figure()
        palette = [ACCEL, AMBER, SLATE, DANGER]
        for i, cl in enumerate(sorted(clusters["risk_cluster"].unique())):
            sub = clusters[clusters["risk_cluster"] == cl]
            fig.add_trace(go.Scatter(
                x=sub["mean_price"], y=sub["volatility"], mode="markers", name=f"Cluster {cl}",
                marker=dict(color=palette[i % len(palette)], size=8, opacity=0.75),
                customdata=sub[["Market", "Commodity", "mean_deviation"]],
                hovertemplate="<b>%{customdata[0]}</b> (%{customdata[1]})<br>Mean price: \u20b9%{x:.0f}<br>Volatility: %{y:.0f}<br>Mean deviation: %{customdata[2]:.1f}%<extra></extra>",
            ))
        style_fig(fig, height=440, xaxis_title="Mean modal price (\u20b9/quintal)", yaxis_title="Price volatility (std dev)",
                  legend=dict(orientation="h", y=1.08, bgcolor="rgba(0,0,0,0)"))
        plot(fig)

# METHODOLOGY
with tab_method:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(
            f'<div class="section-card">{h("\U0001F69A Transport-cost-aware ranking")}'
            f'{p("A price gap only counts as a real opportunity once realistic trucking cost is "
                "subtracted from it. For each commodity and day, we find the cheapest reporting market, "
                "compute the haversine (great-circle) distance to every pricier market, and estimate "
                "freight cost at <b>\u20b90.28/km per quintal</b> (based on typical Indian medium-truck rates "
                "of roughly \u20b925\u201330/km for a ~10-tonne load). Only gaps that clear both the freight "
                "cost <b>and</b> a minimum margin (default 3%) are surfaced.")}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="section-card">{h("\U0001F4C5 Persistence filter")}'
            f'{p("A single day\'s price gap can be noise. We count how many of the last 3 days a market "
                "showed a deviation greater than 8% from its state median, and use that as a persistence "
                "score \u2014 opportunities that have held for multiple days rank higher than one-day spikes.")}</div>',
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            f'<div class="section-card">{h("\U0001F4C9 Anomaly detection")}'
            f'{p("For every (market, commodity) pair, we compute a rolling 7-row mean and standard "
                "deviation of modal price, then a z-score: <code>(price - rolling_mean) / rolling_std</code>. "
                "Large negative z-scores flag price crashes (buy signals); large positive z-scores flag "
                "spikes (sell-side signals).")}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="section-card">{h("\u26A1 Two-layer acceleration")}'
            f'{p("The same cleaning and analysis logic runs two ways: <b>cudf.pandas</b> accelerates the "
                "interactive notebook layer with zero code changes, and <b>Spark RAPIDS on Dataproc "
                "Serverless</b> accelerates the identical logic as a distributed batch job. Benchmarked at "
                "multiple data scales \u2014 not a single cherry-picked number \u2014 so the acceleration claim "
                "holds under scrutiny.")}</div>',
            unsafe_allow_html=True,
        )

    st.markdown(
        f'<div class="section-card">{h("Known simplifications")}'
        f'{p("\u2022 Haversine distance is a great-circle approximation, not real road distance \u2014 treated as "
            "a ranking signal, not a routing engine.")}'
        f'{p("\u2022 The freight rate (\u20b90.28/km/quintal) is a configurable default in <code>pipeline_core.py</code>; "
            "adjust it if you have a better real quote.")}'
        f'{p("\u2022 The state-median price is exact in the pandas pipeline but approximate "
            "(<code>percentile_approx</code>) in the distributed Spark job, which is standard practice at scale.")}</div>',
        unsafe_allow_html=True,
    )

# FOOTER
st.markdown(
    """
    <div class="app-footer">
        <div class="footer-badges">
            <div class="footer-badge">Cloud Storage</div>
            <div class="footer-badge">BigQuery</div>
            <div class="footer-badge">Dataproc Serverless</div>
            <div class="footer-badge">cudf.pandas</div>
            <div class="footer-badge">cuML</div>
            <div class="footer-badge">XGBoost (GPU)</div>
            <div class="footer-badge">Spark RAPIDS</div>
        </div>
        <div class="footer-note">Fasal Bazaar Intelligence &middot; Gen AI Academy APAC Edition</div>
    </div>
    """,
    unsafe_allow_html=True,
)
