import numpy as np
import pandas as pd

RS_PER_KM_PER_QUINTAL_DEFAULT = 0.28  # ~Rs 25-30/km for a 10-tonne truck -> Rs/km/quintal
MARGIN_PCT_DEFAULT = 3.0


def clean_pipeline(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [c.strip().replace(" ", "_") for c in df.columns]

    df["Arrival_Date"] = pd.to_datetime(df["Arrival_Date"], errors="coerce")

    df["Variety"] = df["Variety"].astype(str).str.strip().str.lower()
    df["Commodity"] = df["Commodity"].astype(str).str.strip().str.title()
    df["State"] = df["State"].astype(str).str.strip().str.title()
    df["Market"] = df["Market"].astype(str).str.strip()

    for col in ["Min_Price", "Max_Price", "Modal_Price"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["Modal_Price", "Arrival_Date"])
    df = df[df["Modal_Price"] > 0]

    for col in ["Min_Price", "Max_Price", "Modal_Price", "Lat", "Lon"]:
        if col in df.columns:
            df[col] = df[col].astype("float32")

    return df


def analyze_pipeline(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values(["Commodity", "Market", "Arrival_Date"])

    state_daily_median = (
        df.groupby(["State", "Commodity", "Arrival_Date"])["Modal_Price"]
        .transform("median")
    )
    df["State_Median_Price"] = state_daily_median
    df["Deviation_Pct"] = (df["Modal_Price"] - df["State_Median_Price"]) / df["State_Median_Price"] * 100

    grp = df.groupby(["Market", "Commodity"])["Modal_Price"]
    df["Rolling_Mean_7d"] = grp.transform(lambda s: s.rolling(7, min_periods=3).mean())
    df["Rolling_Std_7d"] = grp.transform(lambda s: s.rolling(7, min_periods=3).std())
    df["Z_Score"] = (df["Modal_Price"] - df["Rolling_Mean_7d"]) / df["Rolling_Std_7d"].replace(0, np.nan)

    return df


def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    lat1r, lon1r, lat2r, lon2r = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2r - lat1r
    dlon = lon2r - lon1r
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1r) * np.cos(lat2r) * np.sin(dlon / 2) ** 2
    return 2 * R * np.arcsin(np.sqrt(a))


def rank_opportunities_transport_aware(
    df: pd.DataFrame,
    top_n: int = 15,
    load_quintals: int = 100,
    rs_per_km_per_quintal: float = RS_PER_KM_PER_QUINTAL_DEFAULT,
    margin_pct: float = MARGIN_PCT_DEFAULT,
    as_of_date=None,
) -> pd.DataFrame:
    latest_date = as_of_date if as_of_date is not None else df["Arrival_Date"].max()
    today = df[df["Arrival_Date"] == latest_date].copy()

    recent = df[df["Arrival_Date"] >= latest_date - pd.Timedelta(days=3)]
    persistence = (
        recent.assign(flag=recent["Deviation_Pct"].abs() > 8)
        .groupby(["Market", "Commodity"])["flag"].sum().rename("Persistence_Days")
    )
    today = today.merge(persistence, on=["Market", "Commodity"], how="left")
    today["Persistence_Days"] = today["Persistence_Days"].fillna(0)

    results = []
    for commodity, grp in today.groupby("Commodity"):
        if len(grp) < 2:
            continue
        cheapest = grp.loc[grp["Modal_Price"].idxmin()]
        pricier = grp[grp["Modal_Price"] > cheapest["Modal_Price"] * 1.02]
        if pricier.empty:
            continue

        dist_km = haversine_km(cheapest["Lat"], cheapest["Lon"], pricier["Lat"].values, pricier["Lon"].values)
        transport_cost = dist_km * rs_per_km_per_quintal
        price_gap = pricier["Modal_Price"].values - cheapest["Modal_Price"]
        net_gain = price_gap - transport_cost
        net_margin_pct = net_gain / cheapest["Modal_Price"] * 100

        best_idx = np.argmax(net_gain)
        if net_margin_pct[best_idx] > margin_pct:
            sell_row = pricier.iloc[best_idx]
            results.append({
                "Commodity": commodity,
                "Buy_Market": cheapest["Market"], "Buy_State": cheapest["State"],
                "Buy_Price": round(float(cheapest["Modal_Price"]), 2),
                "Buy_Lat": float(cheapest["Lat"]), "Buy_Lon": float(cheapest["Lon"]),
                "Sell_Market": sell_row["Market"], "Sell_State": sell_row["State"],
                "Sell_Price": round(float(sell_row["Modal_Price"]), 2),
                "Sell_Lat": float(sell_row["Lat"]), "Sell_Lon": float(sell_row["Lon"]),
                "Distance_km": round(float(dist_km[best_idx]), 1),
                "Transport_Cost_Per_Quintal": round(float(transport_cost[best_idx]), 2),
                "Net_Gain_Per_Quintal": round(float(net_gain[best_idx]), 2),
                "Net_Margin_Pct": round(float(net_margin_pct[best_idx]), 2),
                "Persistence_Days": int(cheapest["Persistence_Days"]),
                "Est_Profit_Per_Truckload": round(float(net_gain[best_idx]) * load_quintals, 0),
            })

    out = pd.DataFrame(results)
    if len(out):
        out = out.sort_values("Net_Margin_Pct", ascending=False).head(top_n)
    return out
