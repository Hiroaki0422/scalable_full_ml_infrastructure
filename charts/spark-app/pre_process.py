from pyspark.sql import SparkSession
from pyspark.sql.functions import col, input_file_name, to_date, coalesce
from datetime import datetime
import os
import argparse
import sys
import logging

# Constants
HISTORICAL_DATA_PATH = f"/app/data/processed/{datetime.today().strftime('%Y-%m-%d')}_historical.csv"

# Launch Spark — scalable across cores or nodes
spark = SparkSession.builder \
    .appName("Stock Sentiment Preprocessor") \
    .getOrCreate()


def process_input_data():
    # Load raw sentiment data files using distributed read
    raw_dir = "/app/data/raw/"
    files = [os.path.join(dp, f) for dp, _, filenames in os.walk(
        raw_dir) for f in filenames if '202' in f]
    files.sort()  # Ensures chronological order

    # Load and union all CSVs in Spark
    df_list = []
    for file in files:
        df = spark.read.option("header", "true").csv(file)
        df_list.append(df)

    # Combine large files using distributed union
    all_df = df_list[0]
    for df in df_list[1:]:
        # Append only new rows
        max_date = all_df.agg({"Date": "max"}).collect()[0][0]
        df = df.filter(col("Date") > max_date)
        all_df = all_df.unionByName(df)

    all_df = all_df.withColumnRenamed("Symbol", "symbol")
    return all_df.select("Date", "symbol", "sentiment").dropna()


def combine_historic_and_new_data(historic_df, new_df):
    # Distributed join by Date + symbol
    merged = historic_df.alias("A").join(
        new_df.alias("B"),
        on=["Date", "symbol"],
        how="left"
    )

    # Use coalesce for null-safe merge
    merged = merged.withColumn(
        "sentiment",
        coalesce(col("A.sentiment"), col("B.sentiment"))
    )

    return merged.select("Date", "symbol", "sentiment")


def impute_arima_locally(df):
    # Non-distributed ARIMA step: collect locally
    # This could be swapped with scalable imputation methods like KNN or mean fill
    pandas_df = df.toPandas()

    from statsmodels.tsa.arima.model import ARIMA
    series = pandas_df["sentiment"]
    model = ARIMA(series, order=(5, 1, 0))
    model_fit = model.fit()
    predictions = model_fit.predict(start=0, end=len(series)-1, typ="levels")

    pandas_df["sentiment"] = pandas_df["sentiment"].fillna(predictions)
    return spark.createDataFrame(pandas_df)


def write_output(df):
    df.write.option("header", True).csv(
        f"/app/data/curated/{datetime.today().strftime('%Y-%m-%d')}_training.csv",
        mode="overwrite"
    )


def parse_args():
    parser = argparse.ArgumentParser(
        description="Process stock sentiment data.")
    parser.add_argument('--data', type=str, help='Path to historical data')
    return parser.parse_args()


def main():
    args = parse_args()

    # Load new + historical
    new_data = process_input_data()
    historic_data = spark.read.option(
        "header", "true").csv(HISTORICAL_DATA_PATH)

    # Combine and fill
    training_dataset = combine_historic_and_new_data(historic_data, new_data)
    training_dataset = impute_arima_locally(training_dataset)

    # Output
    write_output(training_dataset)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.warning("Script interrupted by user.")
        sys.exit(1)
