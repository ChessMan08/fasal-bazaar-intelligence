import argparse
import time

from pyspark.sql import SparkSession, Window
import pyspark.sql.functions as F


def build_spark(app_name="fasal-bazaar-arbitrage"):
    return SparkSession.builder.appName(app_name).getOrCreate()


def load_raw(spark, input_path):
    if input_path.endswith(".csv"):
        return spark.read.option("header", True).option("inferSchema", True).csv(input_path)
    return spark.read.parquet(input_path)


def clean(df):
    for c in df.columns:
        df = df.withColumnRenamed(c, c.strip().replace(" ", "_"))

    df = df.withColumn("Arrival_Date", F.to_date("Arrival_Date"))
    df = df.withColumn("Variety", F.lower(F.trim(F.col("Variety").cast("string"))))
    df = df.withColumn("Commodity", F.initcap(F.trim(F.col("Commodity").cast("string"))))
    df = df.withColumn("State", F.initcap(F.trim(F.col("State").cast("string"))))
    df = df.withColumn("Market", F.trim(F.col("Market").cast("string")))

    for c in ["Min_Price", "Max_Price", "Modal_Price"]:
        df = df.withColumn(c, F.col(c).cast("double"))

    df = df.dropna(subset=["Modal_Price", "Arrival_Date"])
    df = df.filter(F.col("Modal_Price") > 0)
    return df


def analyze(df):
    state_win = Window.partitionBy("State", "Commodity", "Arrival_Date")
    df = df.withColumn(
        "State_Median_Price",
        F.expr("percentile_approx(Modal_Price, 0.5)").over(state_win),
    )
    df = df.withColumn(
        "Deviation_Pct",
        (F.col("Modal_Price") - F.col("State_Median_Price")) / F.col("State_Median_Price") * 100,
    )

    roll_win = (
        Window.partitionBy("Market", "Commodity")
        .orderBy("Arrival_Date")
        .rowsBetween(-6, 0)
    )
    df = df.withColumn("Rolling_Mean_7d", F.avg("Modal_Price").over(roll_win))
    df = df.withColumn("Rolling_Std_7d", F.stddev("Modal_Price").over(roll_win))
    df = df.withColumn(
        "Z_Score",
        F.when(
            F.col("Rolling_Std_7d") > 0,
            (F.col("Modal_Price") - F.col("Rolling_Mean_7d")) / F.col("Rolling_Std_7d"),
        ),
    )
    return df


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="gs:// path to raw CSV or Parquet")
    parser.add_argument("--output", required=True, help="gs:// path to write analyzed Parquet")
    parser.add_argument("--bq-table", default=None, help="PROJECT.DATASET.TABLE, optional")
    parser.add_argument("--bq-temp-bucket", default=None, help="required if --bq-table is set")
    args = parser.parse_args()

    spark = build_spark()
    spark.sparkContext.setLogLevel("WARN")

    t0 = time.time()
    df_raw = load_raw(spark, args.input)
    n_in = df_raw.count()

    df_clean = clean(df_raw)
    df_analyzed = analyze(df_clean)

    # .count() forces full execution
    # not just DAG construction time.
    n_out = df_analyzed.count()
    elapsed = time.time() - t0

    print(f"BENCHMARK rows_in={n_in} rows_out={n_out} seconds={elapsed:.2f}")

    df_analyzed.write.mode("overwrite").parquet(args.output)
    print(f"Wrote analyzed output to {args.output}")

    if args.bq_table:
        if not args.bq_temp_bucket:
            raise ValueError("--bq-temp-bucket is required when writing to BigQuery")
        df_analyzed.write.format("bigquery") \
            .option("table", args.bq_table) \
            .option("temporaryGcsBucket", args.bq_temp_bucket) \
            .mode("overwrite").save()
        print(f"Wrote analyzed output to BigQuery table {args.bq_table}")

    spark.stop()


if __name__ == "__main__":
    main()
