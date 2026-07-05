#!/bin/bash
# Run this first to get your CPU baseline timing, then run submit_gpu_job.sh

set -euo pipefail

PROJECT_ID="fasal-bazaar-intel"         
REGION="us-central1"
BUCKET_NAME="your-bucket-name" 
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
