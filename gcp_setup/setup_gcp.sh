#!/bin/bash
# One-time GCP project setup for the Fasal Bazaar Intelligence pipeline.
# Run this once, at the start of Week 1, right after your $300 free trial is active.
set -euo pipefail

# ---- EDIT THESE ----
PROJECT_ID="your-gcp-project-id"
REGION="us-central1"            # pick a region with L4 GPU availability
BUCKET_NAME="your-bucket-name"  # must be globally unique
BQ_DATASET="agmarknet"
# ---------------------

echo "== Setting active project =="
gcloud config set project "${PROJECT_ID}"

echo "== Enabling required APIs =="
gcloud services enable \
  dataproc.googleapis.com \
  compute.googleapis.com \
  storage-api.googleapis.com \
  storage.googleapis.com \
  bigquery.googleapis.com \
  aiplatform.googleapis.com

echo "== Creating GCS bucket with zone structure =="
if ! gsutil ls -b "gs://${BUCKET_NAME}" >/dev/null 2>&1; then
  gsutil mb -l "${REGION}" "gs://${BUCKET_NAME}"
else
  echo "Bucket gs://${BUCKET_NAME} already exists, skipping creation."
fi

# Landing zones -- creating placeholder objects so the "folders" exist and are
# visible in the console immediately.
for zone in raw processed curated; do
  echo "placeholder" | gsutil cp - "gs://${BUCKET_NAME}/${zone}/.keep"
done
echo "Created zones: gs://${BUCKET_NAME}/{raw,processed,curated}/"

echo "== Creating BigQuery dataset =="
if ! bq show "${PROJECT_ID}:${BQ_DATASET}" >/dev/null 2>&1; then
  bq mk --location="${REGION}" --dataset "${PROJECT_ID}:${BQ_DATASET}"
else
  echo "Dataset ${BQ_DATASET} already exists, skipping creation."
fi

echo "== Creating BigQuery tables (schema-on-write, first load will define types) =="
bq mk --table \
  "${PROJECT_ID}:${BQ_DATASET}.top_opportunities" \
  Commodity:STRING,Buy_Market:STRING,Buy_State:STRING,Buy_Price:FLOAT,Buy_Lat:FLOAT,Buy_Lon:FLOAT,Sell_Market:STRING,Sell_State:STRING,Sell_Price:FLOAT,Sell_Lat:FLOAT,Sell_Lon:FLOAT,Distance_km:FLOAT,Transport_Cost_Per_Quintal:FLOAT,Net_Gain_Per_Quintal:FLOAT,Net_Margin_Pct:FLOAT,Persistence_Days:INTEGER,Est_Profit_Per_Truckload:FLOAT \
  2>/dev/null || echo "top_opportunities table already exists, skipping."

bq mk --table \
  "${PROJECT_ID}:${BQ_DATASET}.risk_clusters" \
  Market:STRING,Commodity:STRING,mean_price:FLOAT,volatility:FLOAT,mean_deviation:FLOAT,risk_cluster:INTEGER \
  2>/dev/null || echo "risk_clusters table already exists, skipping."

echo ""
echo "== Done =="
echo "Bucket:  gs://${BUCKET_NAME}/{raw,processed,curated}/"
echo "Dataset: ${PROJECT_ID}:${BQ_DATASET}"
echo ""
echo "Next: upload your raw Agmarknet data to gs://${BUCKET_NAME}/raw/,"
echo "then point the notebook's RAW_CSV_PATH or the Dataproc job's --input at it."
echo ""
echo "For the Looker Studio dashboard: go to lookerstudio.google.com > Create > "
echo "Data source > BigQuery > select project '${PROJECT_ID}' > dataset '${BQ_DATASET}' > "
echo "table 'top_opportunities'. Add a table chart sorted by Net_Margin_Pct descending, "
echo "a scorecard for total Est_Profit_Per_Truckload, and a geo map using Buy_Lat/Buy_Lon. "
echo "This takes about 15-20 minutes and gives you a live, shareable GCP-native dashboard "
echo "alongside the Streamlit app."
