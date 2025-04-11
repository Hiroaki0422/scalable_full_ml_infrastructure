from pyspark.sql import SparkSession

if __name__ == "__main__":
    spark = SparkSession.builder.appName("TestSparkJob").getOrCreate()

    # Create a simple DataFrame
    df = spark.createDataFrame([
        ("Alice", 25),
        ("Bob", 30),
        ("Carol", 35)
    ], ["name", "age"])

    df.show()

    spark.stop()
