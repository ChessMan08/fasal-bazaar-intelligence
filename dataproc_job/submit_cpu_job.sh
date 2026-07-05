#!/bin/bash
# CPU baseline run -- standard tier, no GPU accelerator.
# Run this first to get your CPU baseline timing, then run submit_gpu_job.sh
# with the SAME input data and compare the "BENCHMARK ... seconds=" line in
# each job's logs.
set -euo pipefail

PROJECT_ID="your-gcp-project-id"       # <-- set this
REGION="us-central1"                    # <-- pick a region with L4 GPU availability for the GPU run
BUCKET_NAME="your-bucket-name"          # <-- set this (used for deps + logs)
INPUT_PATH="gs://${BUCKET_NAME}/raw/agmarknet.parquet"
OUTPUT_PATH="gs://${BUCKET_NAME}/processed/analyzed_cpu"

gcloud dataproc batches submit pyspark spark_arbitrage_job.py \
  --project="${PROJECT_ID}" \
  --region="${REGION}" \
  --deps-bucket="${BUCKET_NAME}" \
  --version=1.1 \
  --batch="fasal-bazaar-cpu-$(date +%s)" \
  -- \
  --input="${INPUT_PATH}" \
  --output="${OUTPUT_PATH}"

echo ""
echo "Job submitted. Check timing via:"
echo "  gcloud dataproc batches list --project=${PROJECT_ID} --region=${REGION}"
echo "Then grep the driver log for the 'BENCHMARK rows_in=... seconds=...' line."
