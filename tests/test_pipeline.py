import numpy as np
import pandas as pd
import pytest

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from pipeline_core import (
    clean_pipeline,
    analyze_pipeline,
    haversine_km,
    rank_opportunities_transport_aware,
)

# clean_pipeline
def make_raw_row(**overrides):
    base = dict(
        State=" punjab ", Market=" Ludhiana Mandi ", Commodity=" wheat ",
        Variety=" Local ", Arrival_Date="2025-06-01",
        Min_Price="1900", Max_Price="2100", Modal_Price="2000",
        Lat=30.9, Lon=75.8,
    )
    base.update(overrides)
    return base


def test_clean_normalizes_whitespace_and_case():
    df = pd.DataFrame([make_raw_row()])
    out = clean_pipeline(df)
    assert out.iloc[0]["State"] == "Punjab"
    assert out.iloc[0]["Market"] == "Ludhiana Mandi"
    assert out.iloc[0]["Commodity"] == "Wheat"
    assert out.iloc[0]["Variety"] == "local"


def test_clean_drops_zero_and_negative_prices():
    df = pd.DataFrame([make_raw_row(Modal_Price="0"), make_raw_row(Modal_Price="-50"), make_raw_row()])
    out = clean_pipeline(df)
    assert len(out) == 1
    assert out.iloc[0]["Modal_Price"] == 2000


def test_clean_drops_unparseable_dates():
    df = pd.DataFrame([make_raw_row(Arrival_Date="not-a-date"), make_raw_row()])
    out = clean_pipeline(df)
    assert len(out) == 1


def test_clean_drops_non_numeric_prices():
    df = pd.DataFrame([make_raw_row(Modal_Price="N/A"), make_raw_row()])
    out = clean_pipeline(df)
    assert len(out) == 1

# analyze_pipeline
def make_series(market, commodity, state, prices, start_date="2025-01-01"):
    dates = pd.date_range(start_date, periods=len(prices), freq="D")
    return pd.DataFrame({
        "State": state, "Market": market, "Commodity": commodity,
        "Arrival_Date": dates, "Modal_Price": prices,
        "Lat": 20.0, "Lon": 78.0,
    })


def test_analyze_state_median_shared_across_markets_same_day():
    df = pd.concat([
        make_series("MarketA", "Wheat", "Punjab", [2000]),
        make_series("MarketB", "Wheat", "Punjab", [2400]),
    ])
    out = analyze_pipeline(df)
    # median of [2000, 2400] is 2200 for both rows on that single shared day
    assert out["State_Median_Price"].unique().tolist() == [2200.0]


def test_analyze_zscore_flags_injected_crash():
    stable_prices = [2000, 2005, 2010, 2015, 2020, 2025, 2030]
    prices = stable_prices + [1200]
    df = make_series("MarketA", "Wheat", "Punjab", prices)
    out = analyze_pipeline(df).sort_values("Arrival_Date")
    crash_row = out.iloc[-1]
    assert crash_row["Z_Score"] < -1.5, "z-score should strongly flag the injected crash"


def test_analyze_no_crash_gives_near_zero_zscore_trend():
    # steadily increasing prices should NOT trigger a large z-score deviation
    prices = list(range(2000, 2000 + 20, 2))
    df = make_series("MarketA", "Wheat", "Punjab", prices)
    out = analyze_pipeline(df).sort_values("Arrival_Date")
    last_z = out.iloc[-1]["Z_Score"]
    assert abs(last_z) < 2.5, "steady linear trend should not read as an anomaly"


# haversine_km
def test_haversine_zero_distance_same_point():
    assert haversine_km(20.0, 78.0, 20.0, 78.0) == pytest.approx(0.0, abs=1e-6)


def test_haversine_known_distance_delhi_mumbai():
    dist = haversine_km(28.6139, 77.2090, 19.0760, 72.8777)
    assert 1100 < dist < 1250


def test_haversine_symmetric():
    d1 = haversine_km(28.6, 77.2, 19.1, 72.9)
    d2 = haversine_km(19.1, 72.9, 28.6, 77.2)
    assert d1 == pytest.approx(d2)

# rank_opportunities_transport_aware
def make_analyzed_snapshot(rows):
    """rows: list of dicts with Commodity, Market, State, Modal_Price, Lat, Lon.
    Builds a minimal single-day 'today' snapshot plus enough history for the
    persistence lookback not to error."""
    today = pd.Timestamp("2025-06-10")
    df = pd.DataFrame(rows)
    df["Arrival_Date"] = today
    df["Deviation_Pct"] = 0.0
    return df


def test_finds_opportunity_when_gap_beats_transport_cost():
    rows = [
        dict(Commodity="Onion", Market="Cheap Mandi", State="MP", Modal_Price=1000, Lat=23.0, Lon=77.0),
        dict(Commodity="Onion", Market="Pricey Mandi", State="MP", Modal_Price=1500, Lat=24.0, Lon=77.0),
    ]
    df = make_analyzed_snapshot(rows)
    out = rank_opportunities_transport_aware(df)
    assert len(out) == 1
    assert out.iloc[0]["Buy_Market"] == "Cheap Mandi"
    assert out.iloc[0]["Sell_Market"] == "Pricey Mandi"
    assert out.iloc[0]["Net_Margin_Pct"] > 3.0


def test_rejects_opportunity_when_transport_cost_exceeds_gap():
    rows = [
        dict(Commodity="Onion", Market="Cheap Mandi", State="MP", Modal_Price=1000, Lat=10.0, Lon=77.0),
        dict(Commodity="Onion", Market="Pricey Mandi", State="MP", Modal_Price=1500, Lat=55.0, Lon=77.0),
    ]
    df = make_analyzed_snapshot(rows)
    out = rank_opportunities_transport_aware(df)
    assert len(out) == 0, "a price gap smaller than transport cost must not be flagged"


def test_respects_margin_threshold():
    rows = [
        dict(Commodity="Onion", Market="A", State="MP", Modal_Price=1000, Lat=23.0, Lon=77.0),
        dict(Commodity="Onion", Market="B", State="MP", Modal_Price=1030, Lat=23.05, Lon=77.0),
    ]
    df = make_analyzed_snapshot(rows)
    out_default_margin = rank_opportunities_transport_aware(df, margin_pct=3.0)
    out_zero_margin = rank_opportunities_transport_aware(df, margin_pct=0.0)
    assert len(out_default_margin) == 0
    assert len(out_zero_margin) == 1


def test_single_market_commodity_produces_no_opportunity():
    rows = [dict(Commodity="Wheat", Market="Only Mandi", State="UP", Modal_Price=2000, Lat=27.0, Lon=80.0)]
    df = make_analyzed_snapshot(rows)
    out = rank_opportunities_transport_aware(df)
    assert len(out) == 0


def test_top_n_limits_output():
    rows = []
    rng = np.random.default_rng(0)
    for i in range(10):
        commodity = f"Commodity_{i}"
        rows.append(dict(Commodity=commodity, Market="Cheap", State="X", Modal_Price=1000, Lat=20.0, Lon=77.0))
        rows.append(dict(Commodity=commodity, Market="Pricey", State="X", Modal_Price=2000, Lat=21.0, Lon=77.0))
    df = make_analyzed_snapshot(rows)
    out = rank_opportunities_transport_aware(df, top_n=3)
    assert len(out) == 3
    assert out["Net_Margin_Pct"].is_monotonic_decreasing


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
