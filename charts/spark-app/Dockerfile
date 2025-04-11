FROM bitnami/spark:latest

USER root
RUN apt-get update && apt-get install -y python3 python3-pip && \
    pip3 install pyspark && apt-get clean
USER 1001

COPY test_spark.py /app/test_spark.py

# ✅ Add spark.jars.ivy=/tmp/.ivy2 to suppress the error
ENTRYPOINT [ "/opt/bitnami/spark/bin/spark-submit", "--conf", "spark.jars.ivy=/tmp/.ivy2", "/app/test_spark.py" ]
