#!/bin/bash
# GPU-accelerated run -- premium tier + L4 accelerator + RAPIDS shuffle manager.
# SAME spark_arbitrage_job.py as the CPU run -- zero code changes. The RAPIDS
# Accelerator is enabled purely through submission properties.
#
# Prerequisites:
#   - NVIDIA_L4_GPUS quota approved in this project/region (request this EARLY,
#     approval can take from minutes to a few business days on a new account)
#   - Premium tier is billed differently from standard -- check current pricing
#     before running at large scale: https://cloud.google.com/dataproc-serverless/pricing
#   - Region must have L4 GPU availability (us-central1 is a safe default)
set -euo pipefail

PROJECT_ID="your-gcp-project-id"       # <-- set this
REGION="us-central1"                    # <-- must support L4 GPUs
BUCKET_NAME="your-bucket-name"          # <-- set this
INPUT_PATH="gs://${BUCKET_NAME}/raw/agmarknet.parquet"   # same input as the CPU run
OUTPUT_PATH="gs://${BUCKET_NAME}/processed/analyzed_gpu"

gcloud dataproc batches submit pyspark spark_arbitrage_job.py \
  --project="${PROJECT_ID}" \
  --region="${REGION}" \
  --deps-bucket="${BUCKET_NAME}" \
  --version=1.1 \
  --batch="fasal-bazaar-gpu-$(date +%s)" \
  --properties=spark.dataproc.executor.compute.tier=premium,spark.dataproc.executor.disk.tier=premium,spark.dataproc.executor.resource.accelerator.type=l4,spark.executor.instances=5,spark.dataproc.driverEnv.LANG=C.UTF-8,spark.executorEnv.LANG=C.UTF-8,spark.shuffle.manager=com.nvidia.spark.rapids.RapidsShuffleManager,spark.rapids.sql.enabled=true \
  -- \
  --input="${INPUT_PATH}" \
  --output="${OUTPUT_PATH}"

echo ""
echo "Job submitted. Check timing via:"
echo "  gcloud dataproc batches list --project=${PROJECT_ID} --region=${REGION}"
echo "Then grep the driver log for the 'BENCHMARK rows_in=... seconds=...' line and"
echo "compare directly against the CPU run's number -- same input, same code, only"
echo "the submission properties differ. That comparison is your distributed-scale"
echo "acceleration proof, separate from and complementary to the single-node"
echo "cudf.pandas benchmark in the notebook."
