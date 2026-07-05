# Fasal Bazaar Intelligence — Decision App

A full decision-support dashboard, not just a table: a hero header, KPI cards,
and seven sections — Overview, Ranked Opportunities, Route Map, Trends &
Forecast, Acceleration Proof, Risk Clusters, and Methodology — all styled with
a custom design system (not default Streamlit look).

## Run locally (Windows/Mac/Linux)

```bash
pip install -r requirements.txt
streamlit run app.py
```

Opens at http://localhost:8501 by default. Runs immediately on realistic demo
data — nothing else to configure to see the full UI.

## What's in each tab

- **Overview** — spotlight card for today's single best opportunity, a
  by-commodity profit bar chart, a margin distribution histogram, and a
  3-point "how this differs from a naive tool" strip.
- **Ranked Opportunities** — the full filterable table with margin-shaded
  coloring and a CSV download button.
- **Route Map** — pydeck arc map, green (buy) to amber (sell), arc thickness
  scaled to margin.
- **Trends & Forecast** — historical price + rolling-mean line chart per
  commodity, a next-day predicted-change card, and an XGBoost feature
  importance chart.
- **Acceleration Proof** — the CPU vs GPU multi-scale benchmark chart and
  table.
- **Risk Clusters** — cuML/KMeans scatter plot of markets by price level and
  volatility.
- **Methodology** — plain-language explanation of the transport-cost math,
  the persistence filter, anomaly detection, and the acceleration
  methodology, plus an honest "known simplifications" section.

## Feeding it real data

Drop these files (from the notebook) into a `data/` folder next to `app.py`.
The app auto-detects each one independently — any subset works, missing ones
just fall back to demo data for that section:

```
data/
  top_opportunities.csv              <- notebook Step 12 (required for Overview/Opportunities/Map)
  risk_clusters.csv                   <- notebook Step 12 (Risk Clusters tab)
  bench_cpu.csv                        <- notebook Step 8, CPU pass (Acceleration tab)
  bench_gpu.csv                        <- notebook Step 8, GPU pass (Acceleration tab)
  full_analyzed_data.parquet          <- notebook Step 12 (Trends & Forecast price history)
  forecast.csv                         <- optional, see below (Trends & Forecast)
  forecast_feature_importance.csv     <- optional, see below (Trends & Forecast)
```

`forecast.csv` and `forecast_feature_importance.csv` aren't exported by the
notebook by default yet — if you want real (not demo) forecast numbers, add a
short export cell after the notebook's XGBoost step:

```python
forecast_out = pd.DataFrame({
    "Commodity": [...], "Predicted_Change_Pct": [...], "Confidence": [...]
})
forecast_out.to_csv("forecast.csv", index=False)

importance_out = pd.DataFrame({
    "Feature": feature_cols, "Importance": model.feature_importances_
})
importance_out.to_csv("forecast_feature_importance.csv", index=False)
```

## Deploying to Google Cloud Run

`Dockerfile` and `.dockerignore` are already in this folder and validated (clean
pip install, confirmed CLI flags, full container-startup simulation all passed).
No local Docker install needed -- `gcloud` builds it for you via Cloud Build.

**One-time setup:**
```bash
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com
```

**Deploy** (run from inside this `streamlit_app/` folder):
```bash
gcloud run deploy fasal-bazaar-intelligence \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 1Gi \
  --port 8080
```

First run will ask permission to create an Artifact Registry repo -- accept.
Takes 2-4 minutes. Prints a live `https://fasal-bazaar-intelligence-xxxxx.run.app`
URL at the end -- that's your public, shareable demo link.

**Redeploying after changes** (new data files, code edits): just re-run the
same `gcloud run deploy` command above from this folder.

**For judging day specifically:** Cloud Run scales to zero when idle, so the
very first visit after a while can take a few seconds to "wake up." If you
want it instantly responsive right when judges click the link, temporarily add
`--min-instances 1` to the deploy command (small extra cost while it's set),
then remove it afterward with another deploy to go back to scale-to-zero.

**Cost:** Cloud Run's free tier covers this comfortably for a hackathon demo
(2 million requests/month free); well within the $300 trial credit regardless.

Other options, roughly in order of effort:

1. **Streamlit Community Cloud** (free, fastest): push this folder to a GitHub repo,
   connect it at share.streamlit.io, point it at `app.py`. Live public URL in ~2 minutes.
2. **Local + screen share for the live demo, deployed link as backup** — perfectly fine
   for a hackathon demo as long as the deployed link exists as proof it's not just running
   on your laptop.

## Notes

- The route map (pydeck ArcLayer) needs `Buy_Lat/Buy_Lon/Sell_Lat/Sell_Lon` columns in
  `top_opportunities.csv` — the v2 notebook already exports these.
- Net margin in the opportunities table already has transport cost netted out — don't
  present raw price-gap percentages next to it, that would look inconsistent on stage.
- The design system (colors, fonts, card styles) lives in the `CUSTOM_CSS` block near
  the top of `app.py` — change the `:root` CSS variables there to retheme the whole app.
- `pd.read_parquet` needs `pyarrow` (already in `requirements.txt`) — if you see a
  parquet-related import error, re-run `pip install -r requirements.txt`.
