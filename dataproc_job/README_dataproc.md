# Distributed batch layer — Dataproc Serverless + Spark RAPIDS

This is the "not an isolated Python script" proof point from the rubric: the same
clean + analyze logic as the notebook, but running as a distributed Spark job that
can process the full historical dataset without fitting it into a single machine's
memory, and that can be GPU-accelerated purely through submission config.

> **Naming note:** Google renamed "Dataproc Serverless" / "Google Cloud Serverless
> for Apache Spark" to **Managed Service for Apache Spark** in 2026. Same product,
> same `gcloud dataproc batches submit` commands — you may see either name in
> current docs and dashboards.

## Files

- `spark_arbitrage_job.py` — the actual ETL + analysis job (cleaning, state-median
  deviation, rolling 7-row z-score). Validated locally with PySpark against synthetic
  data including a deliberate price-crash anomaly, confirmed the z-score correctly
  flags it.
- `submit_cpu_job.sh` — baseline run, standard tier, no GPU
- `submit_gpu_job.sh` — RAPIDS-accelerated run, premium tier + L4 GPU

## One-time setup

```bash
gcloud services enable dataproc.googleapis.com compute.googleapis.com storage-api.googleapis.com bigquery.googleapis.com
gsutil mb -l us-central1 gs://your-bucket-name
```

Request GPU quota now if you haven't already (Compute Engine > Quotas > filter
`NVIDIA_L4_GPUS` in your target region) — this is the step most likely to block you
if left until the last day.

## Running the comparison

1. Land your cleaned raw Agmarknet data (CSV or Parquet) in `gs://your-bucket/raw/`
2. Edit `PROJECT_ID`, `REGION`, `BUCKET_NAME` at the top of both submit scripts
3. `bash submit_cpu_job.sh` — wait for completion, note the `BENCHMARK ... seconds=`
   line in the job logs (Cloud Console > Dataproc > Batches > your batch > logs, or
   `gcloud logging read`)
4. `bash submit_gpu_job.sh` — same input, same code, only the submission properties
   differ. Note its `BENCHMARK ... seconds=` line.
5. The two numbers, side by side, are your distributed-scale acceleration proof —
   independent of and complementary to the single-node cudf.pandas benchmark in
   the notebook. Having both is a stronger story than either alone: it shows the
   acceleration story holds at both the interactive-notebook layer and the
   production-batch layer.

## Cost awareness

GPU-accelerated batches run on the **premium pricing tier**, which costs more than
standard. With a $300 free-trial credit this is very affordable for a handful of
benchmark runs, but don't leave a large-scale job running unattended — check
current pricing before committing to a very large `SCALES` run:
https://cloud.google.com/dataproc-serverless/pricing

## Optional: write straight to BigQuery

```bash
--bq-table your-project.agmarknet.analyzed_full \
--bq-temp-bucket your-bucket-name
```
appended to either submit script's job arguments (after the existing `--output`
flag) writes the analyzed output directly into BigQuery, ready for the Looker
Studio dashboard and the Streamlit app's BigQuery-backed views.
